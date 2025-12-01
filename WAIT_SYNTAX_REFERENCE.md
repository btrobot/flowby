# Wait 语句完整语法参考

## 概述

Wait 语句用于控制执行流程，等待特定条件满足后再继续执行。Flowby 提供了 5 种等待模式：

1. **等待固定时间** - `wait DURATION`
2. **等待页面状态** - `wait for STATE`
3. **等待元素** - `wait for element SELECTOR`
4. **等待导航** - `wait for navigation`
5. **等待条件** - `wait until EXPRESSION`

---

## 1. 等待固定时间 (Wait Duration)

### 语法

```dsl
wait <duration>[<unit>]
wait for <duration>[<unit>]  # for 关键字可选
```

### 支持的时间单位

| 单位 | 说明 | 示例 |
|------|------|------|
| `s` | 秒（默认） | `wait 3s` |
| `ms` | 毫秒 | `wait 500ms` |
| `sec` | 秒（完整拼写） | `wait 2sec` |
| `second` | 秒（单数） | `wait 1second` |
| `seconds` | 秒（复数） | `wait 3seconds` |

### 示例

```dsl
# 基本用法
wait 2s
wait 1.5s
wait 500ms

# 可选的 for 关键字
wait for 3s
wait for 100ms

# 支持整数和浮点数 (v4.0+)
wait 0.5s    # 半秒
wait 2.5s    # 2.5秒
```

### AST 节点

```python
@dataclass
class WaitDurationStatement(ASTNode):
    duration: float  # 统一转换为秒
    line: int
```

### 执行逻辑

```python
def execute_wait_duration(duration: float, context, line):
    time.sleep(duration)
```

---

## 2. 等待页面状态 (Wait For State)

### 语法

```dsl
wait for <page_state>
```

### 支持的页面状态

| 状态 | 说明 | 触发时机 |
|------|------|----------|
| `networkidle` | 网络空闲 | 至少 500ms 内没有网络连接 |
| `load` | 页面加载完成 | `load` 事件触发 |
| `domcontentloaded` | DOM 加载完成 | `DOMContentLoaded` 事件触发 |

### 示例

```dsl
# 等待网络空闲（最常用）
wait for networkidle

# 等待页面加载完成
wait for load

# 等待 DOM 加载
wait for domcontentloaded
```

### AST 节点

```python
@dataclass
class WaitForStateStatement(ASTNode):
    state: str  # "networkidle" | "load" | "domcontentloaded"
    line: int
```

### 执行逻辑

```python
def execute_wait_for_state(state: str, context, line):
    page = context.get_page()
    page.wait_for_load_state(state=state, timeout=30000)
```

---

## 3. 等待元素 (Wait For Element)

### 语法

```dsl
wait for element <selector>
wait for element <selector> to be <state>
wait for element <selector> to be <state> timeout <duration>
```

### 支持的元素状态

| 状态 | 说明 |
|------|------|
| `visible` | 元素可见（默认检查 attached） |
| `hidden` | 元素隐藏 |
| `attached` | 元素已附加到 DOM（默认） |
| `detached` | 元素已从 DOM 移除 |

### 示例

```dsl
# 等待元素存在（默认：attached）
wait for element "#loading"

# 等待元素可见
wait for element ".modal" to be visible

# 等待元素隐藏
wait for element "#spinner" to be hidden

# 带超时的等待
wait for element "#result" to be visible timeout 10s

# v3.0+: 支持表达式
let selector = "#dynamic-content"
wait for element selector to be visible
```

### AST 节点

```python
@dataclass
class WaitForElementStatement(ASTNode):
    selector: Any              # str 或 Expression
    state: Optional[str]       # "visible" | "hidden" | "attached" | "detached"
    timeout: Optional[float]   # 超时时间（秒）
    line: int
```

### 执行逻辑

```python
def execute_wait_for_element(selector: str, state: Optional[str], context, line):
    resolved_selector = context.resolve_variables(selector)
    element_state = state or "attached"
    
    page = context.get_page()
    locator = page.locator(resolved_selector)
    locator.wait_for(state=element_state, timeout=10000)
```

---

## 4. 等待导航 (Wait For Navigation)

### 语法

```dsl
wait for navigation
wait for navigation to <url>
wait for navigation wait for <page_state>
wait for navigation to <url> wait for <page_state> timeout <duration>
```

### 示例

```dsl
# 基本用法：等待导航完成
wait for navigation

# 等待导航到特定 URL
wait for navigation to "https://success.com"

# 等待导航完成后等待页面状态
wait for navigation wait for networkidle

# 完整语法（带超时）
wait for navigation to "https://example.com" wait for load timeout 10s

# v3.0+: 支持表达式
let target_url = "https://dashboard.com"
wait for navigation to target_url
```

### AST 节点

```python
@dataclass
class WaitForNavigationStatement(ASTNode):
    url: Optional[Any]              # str 或 Expression 或 None
    page_state: Optional[str]       # "networkidle" | "load" | "domcontentloaded"
    timeout: Optional[float]        # 超时时间（秒）
    line: int
```

### 执行逻辑

```python
def execute_wait_for_navigation(context, line):
    page = context.get_page()
    page.wait_for_load_state("networkidle", timeout=30000)
```

---

## 5. 等待条件 (Wait Until)

### 语法

```dsl
wait until <expression>
```

### 支持的表达式（v2.0+）

- 比较表达式：`==`, `!=`, `>`, `<`, `>=`, `<=`
- 逻辑表达式：`and`, `or`, `not`
- 字符串操作：`contains`, `matches`
- 成员访问：`page.url`, `obj.property`
- 函数调用：`len(items) > 0`

### 示例

```dsl
# 等待变量条件
wait until page_loaded == True
wait until item_count > 0
wait until status == "ready"

# 等待系统变量
wait until page.url contains "success"

# 复杂条件
wait until len(items) > 0 and items[0].visible
wait until retry_count < 3 or success == True
```

### AST 节点

```python
@dataclass
class WaitUntilStatement(ASTNode):
    condition: Expression  # 任意表达式
    line: int
```

### 执行逻辑

```python
def execute_wait_until_expression(
    condition: Expression,
    evaluator: ExpressionEvaluator,
    context,
    line,
    timeout: float = 30.0,
    poll_interval: float = 0.5
):
    start_time = time.time()
    
    while True:
        result = evaluator.evaluate(condition)
        if to_boolean(result):
            return  # 条件满足
        
        if time.time() - start_time > timeout:
            raise ExecutionError("等待条件超时")
        
        time.sleep(poll_interval)
```

---

## 完整示例脚本

```dsl
step "等待示例":
    # 1. 等待固定时间
    log "开始加载页面..."
    wait 2s
    
    # 2. 导航并等待页面状态
    navigate to "https://example.com"
    wait for networkidle
    
    # 3. 等待加载指示器消失
    wait for element "#loading-spinner" to be hidden timeout 10s
    
    # 4. 等待内容出现
    wait for element "#main-content" to be visible
    
    # 5. 点击并等待导航
    click "#submit-button"
    wait for navigation
    
    # 6. 等待条件满足
    let retry = 0
    wait until retry >= 3 or page.url contains "success"
    
    log "所有等待完成！"
```

---

## 超时配置

### 默认超时时间

| Wait 类型 | 默认超时 | 可配置 |
|-----------|---------|--------|
| `wait for element` | 10s | ✅ `timeout N` |
| `wait for navigation` | 30s | ✅ `timeout N` |
| `wait for state` | 30s | ❌ |
| `wait until` | 30s | ❌ |
| `wait DURATION` | N/A | N/A |

### 自定义超时

```dsl
# 元素等待超时
wait for element "#slow-loading" to be visible timeout 30s

# 导航超时
wait for navigation timeout 60s
```

---

## 错误处理

### 超时错误

当等待超时时，会抛出 `ExecutionError`：

```python
ExecutionError(
    line=15,
    statement="wait for element #result",
    error_type=ExecutionError.TIMEOUT,
    message="等待元素 #result (visible) 超时: Timeout 10000ms exceeded."
)
```

### 错误时截图

`wait for element` 超时会自动捕获错误截图：

```
flowby-output/
└── screenshots/
    └── 2025-11-30/
        └── task-abc123-153045/
            └── script_153045_abc123_error_element_wait_timeout_line_15.png
```

---

## 性能考虑

### 轮询间隔

- `wait until` 轮询间隔：**500ms**
- 过于频繁的轮询会影响性能
- 建议使用 `wait for element` 而非 `wait until` 检查元素

### 最佳实践

```dsl
# ✅ 推荐：使用专用的 wait for element
wait for element "#result" to be visible

# ❌ 不推荐：使用 wait until 检查元素（效率低）
wait until element_exists("#result")

# ✅ 推荐：等待页面状态
wait for networkidle

# ❌ 不推荐：固定等待（不精确）
wait 5s
```

---

## Parser 实现细节

### 解析方法

```python
def _parse_wait(self) -> ASTNode:
    """解析 wait 语句"""
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
    
    # wait <duration>
    if self._check_any(TokenType.INTEGER, TokenType.NUMBER):
        duration_token = self._advance()
        duration = self._parse_time_value(duration_token.value)
        return WaitDurationStatement(duration=duration, line=line)
```

### 时间值解析

```python
def _parse_time_value(self, value: str) -> float:
    """解析时间值，统一转换为秒"""
    if value.endswith('ms'):
        return float(value[:-2]) / 1000.0
    elif value.endswith('s'):
        return float(value[:-1])
    else:
        return float(value)  # 默认为秒
```

---

## 版本兼容性

| 版本 | 变更 |
|------|------|
| v1.0 | 基础 wait 语法 |
| v2.0 | 支持表达式（wait until） |
| v3.0 | 选择器支持表达式（变量、成员访问、f-string） |
| v4.0 | 支持整数和浮点数时间值 |

---

## 测试覆盖

完整的测试用例位于：`tests/grammar_alignment/test_v3_04_wait.py`

包含：
- 时间单位解析测试
- 页面状态等待测试
- 元素等待测试（4 种状态）
- 导航等待测试
- 条件等待测试
- 超时测试
- 表达式支持测试

---

**最后更新**: 2025-11-30  
**对应版本**: v6.0+
