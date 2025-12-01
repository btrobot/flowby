# Wait Duration 表达式扩展 - 技术分析

## 需求分析

### 当前实现

```dsl
# ✅ 当前支持：字面量
wait 2s
wait 500ms
wait 1.5seconds
```

### 期望扩展

```dsl
# 🎯 扩展目标：支持表达式
let delay = 2
wait delay s

let timeout = 500
wait timeout ms

let retry_count = 3
wait (retry_count * 2) s

function calculate_delay():
    return 1.5
wait calculate_delay() s
```

---

## 当前实现机制

### 1. Parser 阶段 (parser.py)

```python
def _parse_wait(self) -> ASTNode:
    # wait <duration>
    if self._check_any(TokenType.INTEGER, TokenType.NUMBER):
        duration_token = self._advance()  # 只接受字面量 token
        time_value = duration_token.value  # 字符串: "2", "500", "1.5"
        
        # 检查可选的单位
        if self._check(TokenType.IDENTIFIER):
            unit = self._peek().value.lower()
            if unit in ('s', 'ms', 'sec', 'second', 'seconds'):
                time_value = time_value + unit  # "2s", "500ms"
                self._advance()
        
        # 立即转换为秒（float）
        duration = self._parse_time_value(time_value)
        return WaitDurationStatement(duration=duration, line=line)
```

**关键限制**: 
- 只检查 `INTEGER` 或 `NUMBER` token
- 立即转换为 float，无法延迟求值

### 2. AST 节点 (ast_nodes.py)

```python
@dataclass
class WaitDurationStatement(ASTNode):
    duration: float  # 已经是计算好的秒数
    line: int
```

**关键限制**: 
- `duration` 是 `float` 类型，无法存储表达式

### 3. Interpreter 阶段 (interpreter.py)

```python
elif isinstance(statement, WaitDurationStatement):
    execute_wait_duration(
        duration=statement.duration,  # 直接使用 float
        context=self.context,
        line=statement.line
    )
```

**关键限制**: 
- 直接使用 `statement.duration`，无求值步骤

### 4. 执行阶段 (actions/wait.py)

```python
def execute_wait_duration(duration: float, context, line):
    time.sleep(duration)  # 直接使用 float 值
```

---

## 扩展方案设计

### 方案 A: 完全表达式化（推荐）

**目标语法**:
```dsl
wait <expression> [unit]
```

**示例**:
```dsl
wait delay s
wait (retry * 2) s
wait calculate_timeout() ms
wait base_delay + random.randint(1, 5) s
```

#### 实现步骤

##### 1. 修改 AST 节点

```python
# ast_nodes.py
@dataclass
class WaitDurationStatement(ASTNode):
    """
    等待固定时间语句 (v6.1: 支持表达式)
    
    语法: 
        wait <expression> [unit]
        
    示例:
        wait 2s                      # 字面量（向后兼容）
        wait delay s                 # 变量
        wait (retry * 2) s           # 算术表达式
        wait calculate_delay() ms    # 函数调用
    
    Attributes:
        duration_expr: 时间值表达式（可以是 Literal 或任意 Expression）
        unit: 时间单位（"s", "ms", "seconds" 等），默认为 "s"
        line: 行号
    """
    duration_expr: Expression  # 改为存储表达式
    unit: str = "s"            # 新增：时间单位
    line: int
```

##### 2. 修改 Parser

```python
# parser.py
def _parse_wait(self) -> ASTNode:
    line = self._peek().line
    self._consume(TokenType.WAIT, "期望 'wait'")
    
    # wait for ...
    if self._check(TokenType.FOR):
        self._advance()
        return self._parse_wait_for()
    
    # wait until ...
    if self._check(TokenType.UNTIL):
        self._advance()
        condition = self._parse_expression()
        return WaitUntilStatement(condition=condition, line=line)
    
    # === v6.1 新逻辑：wait <expression> [unit] ===
    # 解析时间值表达式
    duration_expr = self._parse_expression()
    
    # 检查可选的时间单位
    unit = "s"  # 默认单位
    if self._check(TokenType.IDENTIFIER):
        potential_unit = self._peek().value.lower()
        if potential_unit in ('s', 'ms', 'sec', 'second', 'seconds', 'milliseconds'):
            unit = potential_unit
            self._advance()
    
    return WaitDurationStatement(
        duration_expr=duration_expr,
        unit=unit,
        line=line
    )
```

##### 3. 修改 Interpreter

```python
# interpreter.py
elif isinstance(statement, WaitDurationStatement):
    # v6.1: 求值表达式
    duration_value = self.expression_evaluator.evaluate(statement.duration_expr)
    
    # 转换为数字
    from .expression_evaluator import to_number
    duration_number = to_number(duration_value, statement.line)
    
    # 应用单位转换
    if statement.unit == "ms" or statement.unit == "milliseconds":
        duration_seconds = duration_number / 1000.0
    else:
        # s, sec, second, seconds 都是秒
        duration_seconds = duration_number
    
    # 验证时间值合法性
    if duration_seconds < 0:
        raise ExecutionError(
            line=statement.line,
            statement="wait",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"等待时间不能为负数: {duration_seconds}s"
        )
    
    # 执行等待
    execute_wait_duration(
        duration=duration_seconds,
        context=self.context,
        line=statement.line
    )
```

##### 4. 向后兼容处理

**关键**: 字面量也是表达式！

```python
# 当前语法仍然有效
wait 2s
# Parser 解析为:
#   duration_expr = Literal(value=2, line=...)
#   unit = "s"

# Interpreter 求值:
#   evaluate(Literal(2)) → 2
#   duration_seconds = 2 / 1 = 2.0
```

**完全向后兼容！** ✅

---

### 方案 B: 保守型扩展（备选）

**仅支持简单标识符**（变量名），不支持复杂表达式。

```dsl
# ✅ 支持
wait delay s
wait timeout ms

# ❌ 不支持
wait (retry * 2) s
wait calculate_delay() s
```

**优点**: 实现简单，改动小
**缺点**: 功能受限，后续扩展需要再次修改

**不推荐**: 既然要改，不如一步到位支持完整表达式。

---

## 技术难度评估

### 难度等级：⭐⭐ (2/5) - 简单

#### 为什么难度低？

1. **表达式系统已存在** ✅
   - Flowby 已有完整的表达式求值系统
   - `_parse_expression()` 可以直接使用
   - 不需要新增语法规则

2. **类似模式已实现** ✅
   - `navigate to` 已支持表达式 URL
   - `wait for element` 已支持表达式选择器
   - 只需复用相同模式

3. **架构支持良好** ✅
   - Parser 和 Interpreter 分离
   - AST 节点可以独立修改
   - 不影响其他模块

4. **向后兼容简单** ✅
   - 字面量本身就是表达式（Literal 节点）
   - 无需特殊处理

#### 潜在难点

1. **时间单位与表达式的歧义** ⚠️
   ```dsl
   let s = 10
   wait 2 s  # s 是单位还是变量？
   ```
   
   **解决方案**: 
   - 时间单位必须紧跟表达式，中间不能有空格（Lexer 已处理）
   - 时间单位是关键字，优先级高于标识符
   - `wait 2 s` → Lexer 生成: `WAIT`, `INTEGER(2)`, `IDENTIFIER(s)`
   - Parser 检查 `IDENTIFIER` 是否为已知单位

2. **负数时间值** ⚠️
   ```dsl
   let delay = -1
   wait delay s  # 运行时错误
   ```
   
   **解决方案**: 
   - Interpreter 求值后检查值的合法性
   - 抛出清晰的错误信息

3. **非数值表达式** ⚠️
   ```dsl
   let msg = "hello"
   wait msg s  # 类型错误
   ```
   
   **解决方案**: 
   - 使用 `to_number()` 转换，失败时抛出类型错误

---

## 工作量评估

### 总工作量：⏱️ **2-3 小时**

#### 详细分解

| 任务 | 工作量 | 说明 |
|------|--------|------|
| **1. 修改 AST 节点** | 15 分钟 | 修改 `WaitDurationStatement` |
| **2. 修改 Parser** | 45 分钟 | 修改 `_parse_wait()` 逻辑 |
| **3. 修改 Interpreter** | 30 分钟 | 添加表达式求值和单位转换 |
| **4. 错误处理** | 20 分钟 | 添加负数、非数值检查 |
| **5. 测试用例** | 60 分钟 | 编写全面的测试 |
| **6. 文档更新** | 20 分钟 | 更新语法文档 |
| **7. 回归测试** | 30 分钟 | 确保向后兼容 |

### 代码改动量

| 文件 | 改动行数 | 类型 |
|------|---------|------|
| `ast_nodes.py` | +5, -2 | 修改节点定义 |
| `parser.py` | +15, -20 | 简化逻辑（表达式统一处理） |
| `interpreter.py` | +20 | 添加求值和验证 |
| `tests/` | +50 | 新增测试用例 |
| **总计** | **~90 行** | **小型改动** |

---

## 风险和边界情况

### 1. 时间单位歧义

**场景**:
```dsl
let s = 10
wait 2 s  # s 是单位还是变量？
```

**分析**:
- Lexer 生成: `WAIT`, `INTEGER(2)`, `IDENTIFIER(s)`
- Parser 看到 `IDENTIFIER(s)`，检查是否为时间单位
- `"s"` 在时间单位列表中 → 解析为单位

**结论**: 时间单位关键字会"屏蔽"同名变量（在 wait 语句后）

**影响**: ⚠️ 用户不能定义名为 `s`, `ms`, `sec` 等的变量并在 wait 后使用

**缓解措施**:
```dsl
# 问题：s 被当作单位
let s = 10
wait 2 s  # 解析为: wait 2s（字面量）

# 解决方案1：使用括号
wait 2 * s s  # 错误：第二个 s 是单位
wait (2 * s) seconds  # 正确

# 解决方案2：使用不同的单位关键字
wait 2 * s seconds
```

**是否严重**: ⚠️ 中等 - 可以文档化

### 2. 表达式求值失败

**场景**:
```dsl
let delay = "not a number"
wait delay s  # 运行时错误
```

**处理**:
```python
# Interpreter 中
try:
    duration_number = to_number(duration_value, statement.line)
except:
    raise ExecutionError(
        line=statement.line,
        statement="wait",
        error_type=ExecutionError.TYPE_ERROR,
        message=f"等待时间必须是数字，不能是 {type(duration_value).__name__}"
    )
```

### 3. 极小或极大的时间值

**场景**:
```dsl
wait 0.001 s     # 1ms，有意义
wait 86400 s     # 24小时，合理吗？
wait 999999999 s # 31年，明显错误
```

**建议**:
- 设置合理范围：0.001s ~ 3600s (1小时)
- 超出范围给出警告（不阻止执行）

```python
if duration_seconds > 3600:
    context.logger.warning(
        f"等待时间过长: {duration_seconds}s ({duration_seconds/3600:.1f}小时)，"
        f"请确认是否正确"
    )
```

### 4. 浮点精度

**场景**:
```dsl
wait 0.001 s  # 1ms
```

**Python `time.sleep()`**: 支持浮点数，精度约为 1ms（取决于系统）

**结论**: ✅ 无问题

---

## 测试策略

### 测试用例清单

```python
# tests/test_wait_duration_expression.py

# 1. 向后兼容测试
def test_wait_literal_seconds():
    """wait 2s"""
    
def test_wait_literal_milliseconds():
    """wait 500ms"""

# 2. 变量表达式
def test_wait_variable():
    """
    let delay = 3
    wait delay s
    """

# 3. 算术表达式
def test_wait_arithmetic():
    """
    let retry = 2
    wait (retry * 1.5) s
    """

# 4. 函数调用
def test_wait_function_call():
    """
    function get_delay():
        return 2
    wait get_delay() s
    """

# 5. 成员访问
def test_wait_member_access():
    """
    let config = {timeout: 3}
    wait config.timeout s
    """

# 6. 错误处理
def test_wait_negative_value():
    """
    let delay = -1
    wait delay s  # 应该抛出错误
    """

def test_wait_non_numeric():
    """
    let delay = "hello"
    wait delay s  # 应该抛出类型错误
    """

# 7. 单位转换
def test_wait_milliseconds_conversion():
    """
    let ms = 1500
    wait ms ms  # 应该等待 1.5 秒
    """

# 8. 边界情况
def test_wait_zero():
    """wait 0s"""  # 合法，立即返回

def test_wait_very_small():
    """wait 0.001s"""  # 1ms
```

---

## 实现建议

### 优先级：P1 - 高优先级

**理由**:
1. 用户需求强烈（动态等待时间是常见场景）
2. 实现难度低（2-3 小时）
3. 向后兼容（无破坏性变更）
4. 与现有设计一致（表达式系统统一）

### 实现步骤

```
Phase 1: 核心实现 (1.5 小时)
  ├─ 修改 AST 节点定义
  ├─ 修改 Parser 逻辑
  └─ 修改 Interpreter 求值

Phase 2: 错误处理 (0.5 小时)
  ├─ 添加类型检查
  ├─ 添加负数检查
  └─ 添加合理范围警告

Phase 3: 测试 (1 小时)
  ├─ 编写单元测试
  ├─ 向后兼容测试
  └─ 边界情况测试

Phase 4: 文档 (30 分钟)
  ├─ 更新语法文档
  ├─ 更新 CHANGELOG
  └─ 添加示例
```

---

## 示例对比

### Before (当前)

```dsl
# ✅ 支持
wait 2s
wait 500ms

# ❌ 不支持
let delay = 2
wait delay s  # Parser 错误：期望 INTEGER 或 NUMBER
```

### After (扩展后)

```dsl
# ✅ 全部支持
wait 2s                    # 字面量（向后兼容）
wait 500ms

let delay = 2
wait delay s               # 变量

let retry = 3
wait (retry * 2) s         # 算术表达式

function get_timeout():
    return 5
wait get_timeout() s       # 函数调用

let config = {timeout: 10}
wait config.timeout s      # 成员访问

# 实际应用
let base_delay = 1
let backoff = 2
for i in range(5):
    log f"重试 {i}"
    wait (base_delay * backoff ** i) s  # 指数退避
```

---

## 结论

### 技术可行性：✅ 高

- 架构完全支持
- 无技术障碍
- 实现路径清晰

### 实现成本：✅ 低

- 工作量：2-3 小时
- 代码改动：~90 行
- 风险：低

### 收益：✅ 高

- 用户需求强烈
- 提升语言表达能力
- 保持设计一致性

### 推荐：✅ **立即实施**

这是一个高价值、低成本的改进，强烈建议实现。

---

**分析日期**: 2025-11-30  
**分析者**: Droid & Factory Team  
**状态**: 待审批
