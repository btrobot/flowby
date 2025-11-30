# Grammar Proposal #002: While Loop with break/continue

> **提案编号**: #002
> **提出日期**: 2025-11-27
> **提出人**: Core Team
> **状态**: 📝 Draft
> **目标版本**: 3.0.0
> **影响级别**: MINOR (向后兼容)

---

## 📋 提案摘要

添加 `while` 循环语句及配套的 `break`/`continue` 控制流语句,支持条件驱动的迭代,并提供死循环保护机制,满足 Web 自动化中等待、重试、轮询等核心需求。

---

## 🎯 动机和背景

### 问题描述

当前 DSL 仅支持 `for` 循环(遍历已知集合),缺乏条件驱动的循环能力,导致许多 Web 自动化的核心场景无法优雅实现。

**当前做法的问题**:
```flow
# 场景1: 等待元素出现 - 无法实现
# 目标: 轮询检查元素是否存在,直到出现或超时
# 当前: ❌ 无法实现 (for 循环需要已知集合)

# 场景2: 重试机制 - 实现繁琐
let retry_count = 0
let success = False
for _ in [1, 2, 3]:  # 需要创建虚拟数组
    if success:
        # ❌ 无法 break,必须用 if 跳过剩余迭代
        pass
    else:
        try:
            click "#submit-button"
            success = True
        catch error:
            retry_count = retry_count + 1
            wait 1

# 场景3: 轮询 API 状态 - 无法实现
# 目标: 持续检查直到状态变为 "completed"
# 当前: ❌ 无法实现
```

**问题**:
1. ❌ 无法实现"等待条件满足"的循环
2. ❌ 无法实现"未知次数"的迭代
3. ❌ 缺少 `break`/`continue` 导致控制流不灵活
4. ❌ 无法优雅地实现重试、轮询等常见模式

### 为什么现有功能不够?

- ❌ `for` 循环只能遍历已知集合,不支持条件驱动
- ❌ `if` 语句只能判断一次,不能循环
- ❌ 缺少 `break`/`continue` 导致循环控制不灵活
- ❌ 无法实现"while True"的无限循环模式

### 实际需求场景

#### 场景1: 等待元素加载 (最高频)
```flow
# 等待页面加载完成
let loaded = False
let timeout = 0

while not loaded and timeout < 30:
    if element_exists("#content"):
        loaded = True
    else:
        wait 0.5
        timeout = timeout + 0.5
```

#### 场景2: 重试机制 (高频)
```flow
let retry = 0
while retry < 3:
    try:
        navigate to REGISTRATION_URL
        wait for element "#login-form"
        break  # 成功则退出
    catch error:
        retry = retry + 1
        if retry < 3:
            wait 2  # 等待后重试
```

#### 场景3: 轮询 API 状态 (高频)
```flow
let status = "pending"
while status != "completed":
    wait 2
    let response = http.get(url=STATUS_CHECK_URL)
    if response.ok:
        status = response.data.status
```

#### 场景4: 处理队列 (中频)
```flow
while items.length() > 0:
    let item = items.pop(0)
    if not validate(item):
        continue  # 跳过无效项
    process(item)
```

---

## 💡 提议的解决方案

### 语法设计

#### 基本形式 (BNF)

```bnf
while_statement ::= "while" expression ":"
                    NEWLINE
                    INDENT
                    statement+
                    DEDENT

break_statement ::= "break"

continue_statement ::= "continue"
```

#### 具体语法

```flow
# 基本 while 循环
while condition:
    statement1
    statement2

# 带 break
while condition:
    if exit_condition:
        break
    statement

# 带 continue
while condition:
    if skip_condition:
        continue
    statement

# 无限循环 + break
while True:
    statement
    if should_exit:
        break
```

### 详细说明

#### 参数说明

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| condition | expression | ✅ | 布尔表达式,每次迭代前求值 |
| body | statement+ | ✅ | 循环体,缩进块 |

#### break/continue 行为

**break 语句**:
- 立即退出最内层 while 循环
- 跳转到循环后的第一条语句
- 仅对 while 循环有效 (v3.0 暂不支持 for 循环中使用)

**continue 语句**:
- 跳过本次迭代剩余语句
- 直接进入下一次条件判断
- 仅对 while 循环有效 (v3.0 暂不支持 for 循环中使用)

### 使用示例

#### 示例 1: 基本 while 循环

```flow
/**meta
desc: 基本 while 循环示例
grammar-version: 3.0.0
*/

let count = 0
while count < 5:
    log f"Count: {count}"
    count = count + 1

# 输出: Count: 0, Count: 1, Count: 2, Count: 3, Count: 4
```

#### 示例 2: 等待元素出现 (Web 自动化核心场景)

```flow
step "等待登录表单加载":
    let loaded = False
    let elapsed = 0

    while not loaded and elapsed < 10:
        if element_exists("#login-form"):
            log "登录表单已加载"
            loaded = True
        else:
            wait 0.5
            elapsed = elapsed + 0.5

    if not loaded:
        log "超时: 登录表单未加载"
        screenshot as "timeout-login-form"
end step
```

#### 示例 3: 重试机制 + break

```flow
step "带重试的导航":
    let retry_count = 0
    let max_retries = 3
    let success = False

    while retry_count < max_retries:
        try:
            log f"尝试 {retry_count + 1}/{max_retries}"
            navigate to REGISTRATION_URL
            wait for element "#content" timeout 5
            success = True
            break  # 成功则立即退出
        catch error:
            log f"尝试失败: {error.message}"
            retry_count = retry_count + 1
            if retry_count < max_retries:
                wait 2  # 等待后重试

    assert success == True message "所有重试都失败"
end step
```

#### 示例 4: 轮询 API 状态

```flow
let job_id = "abc123"
let status = "pending"
let elapsed = 0

while status != "completed" and elapsed < 60:
    wait 2
    let response = http.get(url=f"{API_BASE}/jobs/{job_id}/status")

    if response.ok:
        status = response.data.status
        log f"当前状态: {status}"
    else:
        log f"API 请求失败: {response.error}"
        break  # API 失败则退出

    elapsed = elapsed + 2

if status == "completed":
    log "任务完成"
else:
    log "任务超时或失败"
```

#### 示例 5: 处理队列 + continue

```flow
let items = ["item1", "", "item3", None, "item5"]
let processed = 0

while items.length() > 0:
    let item = items.pop(0)

    # 跳过空项和 None
    if item == "" or item == None:
        log f"跳过无效项: {item}"
        continue

    log f"处理: {item}"
    processed = processed + 1

log f"总共处理: {processed} 个有效项"
```

#### 示例 6: 无限循环 + break (服务器模式)

```flow
# 持续监控,直到用户停止
while True:
    let event = check_event()

    if event == "stop":
        log "收到停止信号"
        break

    if event == "alert":
        log "收到警报,发送通知"
        send_notification()

    wait 5  # 每 5 秒检查一次
```

#### 示例 7: 嵌套 while 循环

```flow
let outer_count = 0
while outer_count < 3:
    log f"外层循环: {outer_count}"

    let inner_count = 0
    while inner_count < 2:
        log f"  内层循环: {inner_count}"
        inner_count = inner_count + 1

    outer_count = outer_count + 1
```

---

## 🔍 语义和行为

### 执行语义

1. **条件求值**:
   - 每次迭代**开始前**求值条件表达式
   - 如果条件为 `True`,执行循环体
   - 如果条件为 `False`,退出循环

2. **循环体执行**:
   - 按顺序执行循环体中的语句
   - 遇到 `break` 立即退出循环
   - 遇到 `continue` 跳过剩余语句,进入下一次迭代

3. **死循环保护**:
   - 设置最大迭代次数限制 (默认: 10000 次)
   - 超过限制抛出 `ExecutionError`
   - 可通过配置调整限制

### 作用域规则

- while 循环**不创建**新作用域 (与 for 循环不同)
- 循环内声明的变量在循环外可见
- 循环变量修改会影响外部作用域

**示例**:
```flow
let count = 0
while count < 5:
    count = count + 1
    let temp = count * 2

# count = 5 (循环外可访问)
# temp = 10 (循环外可访问 - 最后一次迭代的值)
```

**对比 for 循环 (每次迭代创建独立作用域)**:
```flow
for i in [1, 2, 3]:
    let temp = i * 2
# i 和 temp 在循环外不可访问 (作用域已销毁)
```

### 错误处理

| 错误情况 | 行为 | 错误类型 |
|---------|------|---------|
| 条件表达式类型错误 | 抛出 ExecutionError | RUNTIME_ERROR |
| 超过最大迭代次数 | 抛出 ExecutionError | INFINITE_LOOP_DETECTED |
| break/continue 在循环外 | 抛出 ParseError | SYNTAX_ERROR |
| 嵌套过深 (>50层) | 抛出 ExecutionError | STACK_OVERFLOW |

### break/continue 的作用范围

```flow
# ✅ 正确: break 退出最内层循环
while outer_condition:
    while inner_condition:
        if should_exit_inner:
            break  # 只退出内层循环
    # 这里仍会执行

# ❌ 错误: break 在循环外
if condition:
    break  # ParseError: break outside loop
```

---

## 📊 影响分析

### 版本影响

- [x] **MINOR** (向后兼容的新功能)
  - 新增 while/break/continue 语句
  - 不影响现有 for 循环语义
  - 现有脚本无需修改

- [ ] MAJOR (不兼容变更)
- [ ] PATCH (bug 修复)

### 兼容性

#### 向后兼容性

- ✅ **完全向后兼容**
- **原因**:
  - 新增语法,不修改现有语法
  - `while`/`break`/`continue` 不是现有关键字
  - 现有 for 循环语义不变

#### 现有功能影响

| 现有功能 | 影响 | 说明 |
|---------|------|------|
| for 循环 | 无 | v3.0 break/continue 仅支持 while,不影响 for |
| if/else | 无 | 可在 while 循环内正常使用 |
| try-catch | 无 | 可与 while 配合使用 |
| 作用域 | 扩展 | while 不创建新作用域 (与 for 不同) |
| 控制流 | 增强 | 添加 break/continue 控制流 |

### 学习曲线

- **新手**: 容易
  - while 是编程基础概念
  - 语法与 Python 几乎一致
  - 有死循环保护,不易犯错

- **现有用户**: 非常容易
  - 熟悉 for 循环的用户自然理解 while
  - break/continue 是主流语言标配
  - 学习成本 < 1 小时

### 语法复杂度

**当前状态** (v2.0.0):
```
语句类型: 25/30
表达式层次: 9/10
关键字: 80+/100
```

**添加后** (v3.0.0):
```
语句类型: 28/30  (+3: while, break, continue)
表达式层次: 9/10  (不变)
关键字: 83/100   (+3: while, break, continue)
```

**评估**: ✅ **在限制内** (28/30 = 93%, 83/100 = 83%)

---

## 🛠️ 实现方案

### AST 节点定义

```python
# src/registration_system/dsl/ast_nodes.py

@dataclass
class WhileLoop(ASTNode):
    """While 循环语句 (v3.0)"""
    condition: Expression
    statements: List[ASTNode]
    line: int = 0

    def __repr__(self):
        return f"WhileLoop(condition={self.condition}, body={len(self.statements)} statements)"


@dataclass
class BreakStatement(ASTNode):
    """Break 语句 (v3.0)"""
    line: int = 0

    def __repr__(self):
        return "Break()"


@dataclass
class ContinueStatement(ASTNode):
    """Continue 语句 (v3.0)"""
    line: int = 0

    def __repr__(self):
        return "Continue()"
```

### Lexer 变更

**新增 Token 类型**:
```python
# src/registration_system/dsl/lexer.py

class TokenType(Enum):
    # ... 现有 tokens
    WHILE = "WHILE"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"

# 关键字映射
KEYWORDS = {
    # ... 现有关键字
    "while": TokenType.WHILE,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
}
```

### Parser 变更

**新增解析方法**:
```python
# src/registration_system/dsl/parser.py

def _parse_while_loop(self) -> WhileLoop:
    """
    解析 while 循环 (v3.0)

    语法:
        while condition:
            statements
    """
    line = self._peek().line
    self._consume(TokenType.WHILE, "期望 'while'")

    # 解析条件表达式
    condition = self._parse_expression()

    self._consume(TokenType.COLON, "期望 ':'")
    self._consume(TokenType.NEWLINE, "期望换行")
    self._consume(TokenType.INDENT, "期望缩进")

    # 解析循环体
    statements = []
    while not self._check(TokenType.DEDENT) and not self._is_at_end():
        if self._check(TokenType.NEWLINE):
            self._advance()
            continue

        stmt = self._parse_statement()
        if stmt:
            statements.append(stmt)

        self._skip_newlines()

    self._consume(TokenType.DEDENT, "期望反缩进")

    return WhileLoop(
        condition=condition,
        statements=statements,
        line=line
    )


def _parse_break(self) -> BreakStatement:
    """
    解析 break 语句 (v3.0)

    语法:
        break
    """
    line = self._peek().line
    self._consume(TokenType.BREAK, "期望 'break'")

    # 验证 break 在循环内
    if not self._is_in_loop():
        raise ParseError(
            line=line,
            message="break 语句只能在循环内使用"
        )

    return BreakStatement(line=line)


def _parse_continue(self) -> ContinueStatement:
    """
    解析 continue 语句 (v3.0)

    语法:
        continue
    """
    line = self._peek().line
    self._consume(TokenType.CONTINUE, "期望 'continue'")

    # 验证 continue 在循环内
    if not self._is_in_loop():
        raise ParseError(
            line=line,
            message="continue 语句只能在循环内使用"
        )

    return ContinueStatement(line=line)


def _is_in_loop(self) -> bool:
    """检查当前是否在循环内"""
    # 实现: 通过解析器状态跟踪
    # 在 _parse_while_loop 入口设置标志,出口清除标志
    return hasattr(self, '_loop_depth') and self._loop_depth > 0
```

### Interpreter 变更

**核心执行逻辑 + 死循环保护**:
```python
# src/registration_system/dsl/interpreter.py

class WhileLoopGuard:
    """While 循环保护机制 (防止死循环)"""

    def __init__(self, max_iterations: int = 10000):
        """
        Args:
            max_iterations: 最大迭代次数 (默认 10000)
        """
        self.max_iterations = max_iterations
        self.count = 0

    def check(self, line: int):
        """检查是否超过最大迭代次数"""
        self.count += 1
        if self.count > self.max_iterations:
            raise ExecutionError(
                line=line,
                statement="while loop",
                error_type=ExecutionError.INFINITE_LOOP_DETECTED,
                message=f"While 循环超过最大迭代次数 {self.max_iterations},可能是死循环"
            )

    def reset(self):
        """重置计数器"""
        self.count = 0


# 自定义异常用于 break/continue 控制流
class BreakException(Exception):
    """Break 语句抛出的异常"""
    pass


class ContinueException(Exception):
    """Continue 语句抛出的异常"""
    pass


class Interpreter:
    # ... 现有代码

    def _execute_while_loop(self, statement: WhileLoop) -> None:
        """
        执行 while 循环 (v3.0)

        语义:
        - 不创建新作用域 (与 for 循环不同)
        - 支持 break/continue
        - 提供死循环保护
        """
        guard = WhileLoopGuard(max_iterations=10000)  # 可通过配置调整

        while True:
            # 1. 检查死循环保护
            guard.check(statement.line)

            # 2. 检查停止标志
            if self._stopped:
                break

            # 3. 求值条件
            try:
                condition = self.expression_evaluator.evaluate(statement.condition)
            except Exception as e:
                raise ExecutionError(
                    line=statement.line,
                    statement=f"while {statement.condition}",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message=f"条件求值失败: {e}"
                )

            # 4. 检查条件类型
            if not isinstance(condition, bool):
                raise ExecutionError(
                    line=statement.line,
                    statement=f"while {statement.condition}",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message=f"while 条件必须是布尔值,实际: {type(condition).__name__}"
                )

            # 5. 条件为 False 则退出
            if not condition:
                break

            # 6. 执行循环体
            try:
                for stmt in statement.statements:
                    if self._stopped:
                        break
                    self._execute_statement(stmt)

            except BreakException:
                # Break: 退出循环
                break

            except ContinueException:
                # Continue: 跳过剩余语句,进入下一次迭代
                continue


    def _execute_break(self, statement: BreakStatement) -> None:
        """执行 break 语句"""
        raise BreakException()


    def _execute_continue(self, statement: ContinueStatement) -> None:
        """执行 continue 语句"""
        raise ContinueException()


    def _execute_statement(self, statement: ASTNode) -> None:
        """
        执行单个语句

        添加 while/break/continue 支持
        """
        # ... 现有语句处理

        # while 循环
        elif isinstance(statement, WhileLoop):
            self._execute_while_loop(statement)

        # break
        elif isinstance(statement, BreakStatement):
            self._execute_break(statement)

        # continue
        elif isinstance(statement, ContinueStatement):
            self._execute_continue(statement)

        # ... 其他语句
```

### 实现难度

- [x] **中等** (3-5 天)
  - Lexer 修改简单 (+0.5 天)
  - Parser 修改中等 (+1.5 天)
    - 需要跟踪循环嵌套状态
    - break/continue 语法检查
  - Interpreter 修改中等 (+1.5 天)
    - 死循环保护机制
    - break/continue 异常控制流
  - 测试用例编写 (+1.5 天)

### 依赖项

- [x] 依赖现有的表达式求值系统 (expression_evaluator)
- [x] 依赖现有的错误处理机制 (ExecutionError)
- [x] 依赖现有的 INDENT/DEDENT token (已有)
- [ ] **不依赖** for 循环实现 (两者独立)

---

## 🧪 测试计划

### 测试用例

#### 正常情况

```python
# tests/grammar_alignment/test_09_while_loop.py

def test_while_basic(parse):
    """测试基本 while 循环"""
    code = """
let count = 0
while count < 5:
    log f"Count: {count}"
    count = count + 1
"""
    ast = parse(code)
    context = ExecutionContext('test-task')
    interpreter = Interpreter(context)
    interpreter.execute(ast)

    count = interpreter.symbol_table.get("count", 0)
    assert count == 5


def test_while_with_break(parse):
    """测试 while + break"""
    code = """
let i = 0
while i < 100:
    if i == 5:
        break
    i = i + 1
"""
    ast = parse(code)
    context = ExecutionContext('test-task')
    interpreter = Interpreter(context)
    interpreter.execute(ast)

    i = interpreter.symbol_table.get("i", 0)
    assert i == 5


def test_while_with_continue(parse):
    """测试 while + continue"""
    code = """
let i = 0
let sum = 0
while i < 10:
    i = i + 1
    if i % 2 == 0:
        continue
    sum = sum + i
"""
    ast = parse(code)
    context = ExecutionContext('test-task')
    interpreter = Interpreter(context)
    interpreter.execute(ast)

    sum_val = interpreter.symbol_table.get("sum", 0)
    assert sum_val == 25  # 1+3+5+7+9


def test_while_true_with_break(parse):
    """测试无限循环 + break"""
    code = """
let count = 0
while True:
    count = count + 1
    if count >= 10:
        break
"""
    ast = parse(code)
    context = ExecutionContext('test-task')
    interpreter = Interpreter(context)
    interpreter.execute(ast)

    count = interpreter.symbol_table.get("count", 0)
    assert count == 10
```

#### 边界情况

```python
def test_while_nested(parse):
    """测试嵌套 while 循环"""
    code = """
let outer = 0
let total = 0
while outer < 3:
    let inner = 0
    while inner < 2:
        total = total + 1
        inner = inner + 1
    outer = outer + 1
"""
    ast = parse(code)
    context = ExecutionContext('test-task')
    interpreter = Interpreter(context)
    interpreter.execute(ast)

    total = interpreter.symbol_table.get("total", 0)
    assert total == 6  # 3 * 2


def test_while_condition_false_initially(parse):
    """测试初始条件为 False"""
    code = """
let count = 0
while count > 10:
    count = count + 1
"""
    ast = parse(code)
    context = ExecutionContext('test-task')
    interpreter = Interpreter(context)
    interpreter.execute(ast)

    count = interpreter.symbol_table.get("count", 0)
    assert count == 0  # 循环体从未执行


def test_break_in_nested_loop(parse):
    """测试嵌套循环中的 break (仅退出内层)"""
    code = """
let outer_count = 0
while outer_count < 3:
    let inner_count = 0
    while inner_count < 5:
        if inner_count == 2:
            break  # 只退出内层
        inner_count = inner_count + 1
    outer_count = outer_count + 1
"""
    ast = parse(code)
    context = ExecutionContext('test-task')
    interpreter = Interpreter(context)
    interpreter.execute(ast)

    outer_count = interpreter.symbol_table.get("outer_count", 0)
    assert outer_count == 3  # 外层循环完成了所有迭代
```

#### 异常情况

```python
def test_while_infinite_loop_protection(parse):
    """测试死循环保护"""
    code = """
let i = 0
while True:
    i = i + 1
    # 没有 break,应该被死循环保护捕获
"""
    ast = parse(code)
    context = ExecutionContext('test-task')
    interpreter = Interpreter(context)

    with pytest.raises(ExecutionError, match="超过最大迭代次数"):
        interpreter.execute(ast)


def test_while_condition_not_bool(parse):
    """测试条件表达式类型错误"""
    code = """
while "not a boolean":
    log "test"
"""
    ast = parse(code)
    context = ExecutionContext('test-task')
    interpreter = Interpreter(context)

    with pytest.raises(ExecutionError, match="条件必须是布尔值"):
        interpreter.execute(ast)


def test_break_outside_loop(parse):
    """测试 break 在循环外"""
    code = """
if True:
    break
"""
    with pytest.raises(ParseError, match="break.*只能在循环内"):
        ast = parse(code)


def test_continue_outside_loop(parse):
    """测试 continue 在循环外"""
    code = """
if True:
    continue
"""
    with pytest.raises(ParseError, match="continue.*只能在循环内"):
        ast = parse(code)
```

### 测试覆盖率目标

- [ ] 行覆盖率 ≥ 95%
- [ ] 分支覆盖率 ≥ 90%
- [ ] 所有错误路径都有测试
- [ ] 所有示例代码都可运行

---

## 📚 文档变更

### 需要更新的文档

- [ ] **`grammar/MASTER.md`** - 添加 3 个新特性
  ```markdown
  | 2.6 | While Loop | `while EXPR: INDENT STMT+ DEDENT` | ❌ | v3.0 | `_parse_while_loop()` | ❌ | Condition-driven loop |
  | 2.7 | Break | `break` | ❌ | v3.0 | `_parse_break()` | ❌ | Exit loop |
  | 2.8 | Continue | `continue` | ❌ | v3.0 | `_parse_continue()` | ❌ | Skip iteration |
  ```

- [ ] **`grammar/CHANGELOG.md`** - 添加到 [3.0.0] Unreleased
  ```markdown
  ## [3.0.0] - Unreleased

  ### Added
  - **While Loop**: 条件驱动循环 (`while condition: ...`)
  - **Break Statement**: 退出循环 (`break`)
  - **Continue Statement**: 跳过当前迭代 (`continue`)
  - 死循环保护机制 (最大迭代次数限制)
  ```

- [ ] **`docs/DSL-GRAMMAR.ebnf`** - 添加 EBNF 规则
  ```ebnf
  (* While Loop *)
  while_statement = "while" , expression , ":" , NEWLINE , INDENT , statement+ , DEDENT ;
  break_statement = "break" ;
  continue_statement = "continue" ;
  ```

- [ ] **`docs/DSL-GRAMMAR-QUICK-REFERENCE.md`** - 添加快速参考
- [ ] **`docs/DSL-SYNTAX-CHEATSHEET.md`** - 添加速查表
- [ ] **`examples/flows/while_loop_examples.flow`** - 添加完整示例

### 示例文档内容

**examples/flows/while_loop_examples.flow**:
```flow
/**meta
title: While Loop Examples
desc: Demonstrating while loop, break, and continue usage
grammar-version: 3.0.0
*/

# ============================================================
# Example 1: Basic While Loop
# ============================================================
step "基本计数":
    let count = 0
    while count < 5:
        log f"Count: {count}"
        count = count + 1
end step

# ============================================================
# Example 2: Wait for Element (Web Automation)
# ============================================================
step "等待元素加载":
    let loaded = False
    let timeout = 0

    while not loaded and timeout < 10:
        if element_exists("#content"):
            log "元素已加载"
            loaded = True
        else:
            wait 0.5
            timeout = timeout + 0.5

    assert loaded == True message "元素加载超时"
end step

# ============================================================
# Example 3: Retry with Break
# ============================================================
step "重试机制":
    let retry = 0
    let success = False

    while retry < 3:
        try:
            click "#submit-button"
            success = True
            break  # 成功则退出
        catch error:
            log f"尝试失败: {error.message}"
            retry = retry + 1
            if retry < 3:
                wait 2

    assert success == True
end step

# ============================================================
# Example 4: Skip Invalid Items with Continue
# ============================================================
step "处理队列":
    let items = ["item1", "", "item3", None, "item5"]
    let processed = 0

    while items.length() > 0:
        let item = items.pop(0)

        if item == "" or item == None:
            continue  # 跳过无效项

        log f"处理: {item}"
        processed = processed + 1

    log f"处理了 {processed} 个有效项"
end step
```

---

## 🔄 替代方案

### 方案 1: 使用 for 循环模拟

**当前做法**:
```flow
# 使用 for 循环 + 条件判断模拟 while
let found = False
for _ in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    if found:
        pass  # ❌ 无法 break,只能空操作
    else:
        if condition:
            found = True
        else:
            do_something()
```

**优点**:
- 不需要新语法

**缺点**:
- ❌ 需要预先知道最大迭代次数
- ❌ 无法实现真正的"未知次数"循环
- ❌ 代码繁琐,不直观
- ❌ 性能差 (即使已 break,仍会执行空操作)

### 方案 2: 添加 do-while 循环

**语法**:
```flow
do:
    statement
while condition
```

**优点**:
- 保证至少执行一次

**缺点**:
- ❌ 使用频率低
- ❌ 增加语法复杂度
- ❌ 可以用 while True + break 替代

**决定**: 不采用,while 已足够

### 方案 3: 添加 loop/until 循环

**语法**:
```flow
loop:
    statement
    break when condition
```

**优点**:
- 更自然的"无限循环"表达

**缺点**:
- ❌ 不符合主流语言习惯
- ❌ 学习曲线更陡
- ❌ while True + break 已足够清晰

**决定**: 不采用

### 不做任何改变

**当前做法**: 仅使用 for 循环

**为什么不够**:
- ❌ 无法实现等待条件满足
- ❌ 无法实现未知次数迭代
- ❌ 无法优雅实现重试机制
- ❌ 无法实现轮询模式

---

## 💬 讨论记录

### 支持意见

**@core-team**:
- while 循环是编程基础,DSL 缺少它限制太大
- Web 自动化的核心场景(等待、重试、轮询)都需要 while
- 语法设计与 Python 一致,学习成本低
- 死循环保护机制确保安全性

### 疑虑和问题

**Q: while 循环会增加死循环风险吗?**
A:
- 实现了死循环保护 (最大迭代次数限制)
- 默认 10000 次迭代后自动终止
- 可通过配置调整限制

**Q: break/continue 是否应该同时支持 for 循环?**
A:
- v3.0 暂不支持 for 循环中使用 break/continue
- 原因: for 循环采用独立作用域,需要特殊处理
- v3.1 可考虑扩展到 for 循环

**Q: 是否需要 while...else 语法 (Python 风格)?**
A:
- 不需要,使用频率极低
- 可以用标志变量替代
- 保持语法简洁

**Q: 最大迭代次数限制如何配置?**
A:
- 通过配置文件或环境变量
- 建议: `MAX_WHILE_ITERATIONS=10000`

---

## ✅ 决策

### 核心团队评审

- [ ] 技术可行性: ✅ (待确认)
- [ ] 语法一致性: ✅ (待确认)
- [ ] 复杂度控制: ✅ (28/30, 83/100, 在限制内)
- [ ] 文档完整性: ✅ (待确认)

### 最终决定

- **状态**: 📝 Draft
- **决定日期**: 待定
- **决策者**: Core Team
- **理由**: 需要进一步讨论以下问题

### 待讨论问题

1. ✅ 最大迭代次数默认值是否合理? (建议: 10000)
2. ✅ v3.0 是否支持 for 循环中使用 break/continue?
3. ✅ 是否需要 while...else 语法?
4. ✅ 错误消息是否足够清晰?

---

## 📅 实施时间线

### Phase 1: AST 节点定义 (0.5 天)
- [ ] 定义 WhileLoop/BreakStatement/ContinueStatement
- [ ] 更新 ast_nodes.py

### Phase 2: Lexer 实现 (0.5 天)
- [ ] 添加 WHILE/BREAK/CONTINUE token
- [ ] 更新关键字映射

### Phase 3: Parser 实现 (1.5 天)
- [ ] 实现 _parse_while_loop()
- [ ] 实现 _parse_break()
- [ ] 实现 _parse_continue()
- [ ] 添加循环嵌套状态跟踪
- [ ] 语法验证 (break/continue 只能在循环内)

### Phase 4: Interpreter 实现 (1.5 天)
- [ ] 实现 _execute_while_loop()
- [ ] 实现死循环保护机制 (WhileLoopGuard)
- [ ] 实现 break/continue 控制流 (异常机制)
- [ ] 条件求值和类型检查

### Phase 5: 测试 (1.5 天)
- [ ] 单元测试 (20+ 测试用例)
- [ ] 集成测试
- [ ] 边界情况测试
- [ ] 错误处理测试

### Phase 6: 文档 (1 天)
- [ ] 更新 MASTER.md
- [ ] 更新 CHANGELOG.md
- [ ] 更新 EBNF
- [ ] 编写示例文件
- [ ] 更新快速参考和速查表

### Phase 7: 验收 (0.5 天)
- [ ] Code Review
- [ ] 运行 check_sync.py 验证
- [ ] 测试覆盖率检查
- [ ] 文档完整性检查

**总计**: 约 **7 天** (1.4 周)

---

## 📎 附录

### 参考资料

- [Python while statement](https://docs.python.org/3/reference/compound_stmts.html#the-while-statement)
- [Python break/continue](https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements)
- [JavaScript while statement](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/while)
- [Java while loop](https://docs.oracle.com/javase/tutorial/java/nutsandbolts/while.html)
- [FOR-LOOP-COMPARISON.md](../../FOR-LOOP-COMPARISON.md) - DSL for 循环分析
- [PYTHON-WHILE-SYNTAX.md](../../PYTHON-WHILE-SYNTAX.md) - Python while 语法详解

### 相关 Issue

_待创建_

### 设计决策记录

**决策 1**: while 循环不创建新作用域
- **理由**:
  - 符合 Python/JavaScript 的行为
  - 与 for 循环形成互补 (for 创建独立作用域)
  - 简化实现复杂度

**决策 2**: v3.0 仅支持 while 循环中的 break/continue
- **理由**:
  - for 循环采用独立作用域,break/continue 需要特殊处理
  - 先实现最核心的 while + break/continue
  - v3.1 再扩展到 for 循环

**决策 3**: 不实现 while...else
- **理由**:
  - 使用频率极低
  - 可以用标志变量替代
  - 保持语法简洁

**决策 4**: 死循环保护默认 10000 次迭代
- **理由**:
  - 足够大,不会误判正常循环
  - 足够小,能快速发现死循环
  - 可配置,满足不同需求

---

**提案状态**: 📝 Draft
**最后更新**: 2025-11-27
**维护者**: Core Team
**下一步**:
1. 核心团队评审和讨论
2. 确定最终设计细节
3. 批准后开始实施
