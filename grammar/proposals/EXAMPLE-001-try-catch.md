# Grammar Proposal #001: Exception Handling (try-catch)

> **提案编号**: #001
> **提出日期**: 2025-11-25
> **提出人**: Core Team
> **状态**: 💭 Under Discussion
> **目标版本**: 2.1.0
> **影响级别**: MINOR (向后兼容)

---

## 📋 提案摘要

添加 `try-catch` 异常处理语句，允许捕获和处理执行过程中的错误，提高脚本的健壮性。

---

## 🎯 动机和背景

### 问题描述

当前 DSL 在遇到错误时会直接终止整个流程，无法优雅地处理错误情况。

**当前做法的问题**:
```flow
# 场景：尝试点击一个可能不存在的元素
step "尝试关闭弹窗":
    click ".modal-close"  # 如果元素不存在，整个流程终止
end step

step "继续后续流程":
    log "这一步可能永远执行不到"
end step
```

**问题**:
1. 无法捕获和处理运行时错误
2. 无法实现"如果失败则尝试备用方案"的逻辑
3. 无法记录错误并继续执行
4. 难以实现健壮的自动化测试

### 为什么现有功能不够？

- ❌ `if` 语句只能检查条件，不能捕获运行时错误
- ❌ `when` 语句只能做模式匹配，不能处理异常
- ❌ `assert` 失败会直接终止，无法恢复

### 实际需求场景

1. **优雅降级**: 如果主要操作失败，尝试备用方案
2. **错误记录**: 捕获错误并记录详细信息
3. **部分失败容忍**: 某些步骤失败不影响整体流程
4. **清理资源**: 无论成功失败都执行清理操作

---

## 💡 提议的解决方案

### 语法设计

#### 基本形式

```bnf
try_catch ::= "try" ":"
              statement*
              "catch" identifier ":"
              statement*
              [ "finally" ":" statement* ]
              "end" "try"
```

#### 具体语法

```flow
try:
    # 可能失败的操作
    ...
catch error:
    # 错误处理
    ...
[finally:
    # 无论成功失败都执行
    ...]
end try
```

### 详细说明

#### 参数说明

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| try block | statement* | ✅ | 要执行的语句，可能抛出错误 |
| catch variable | identifier | ✅ | 错误对象的变量名 |
| catch block | statement* | ✅ | 错误处理逻辑 |
| finally block | statement* | ❌ | 清理代码（可选） |

#### Error 对象属性

捕获的 `error` 对象包含：
- `error.message` - 错误消息
- `error.type` - 错误类型
- `error.line` - 错误行号
- `error.statement` - 错误语句

### 使用示例

#### 示例 1: 基本错误捕获

```flow
/**meta
desc: 基本的 try-catch 用法
grammar-version: 2.1.0
*/

const BASE_URL = "https://example.com"

step "尝试导航":
    try:
        navigate to BASE_URL + "/login"
        wait for element "#login-form"
    catch error:
        log "导航失败: {error.message}"
        screenshot as "navigation-error"
        # 尝试备用 URL
        navigate to BASE_URL + "/auth"
    end try
end step
```

**预期行为**:
- 如果导航成功，正常执行
- 如果导航失败，记录错误并尝试备用URL
- 流程不会终止

#### 示例 2: 优雅降级

```flow
step "尝试关闭弹窗":
    try:
        click ".modal-close"
        wait for element ".modal" to be hidden
        log "弹窗已关闭"
    catch error:
        log "没有弹窗或关闭失败，继续执行"
    end try
end step

step "继续主流程":
    # 无论弹窗是否存在，这里都会执行
    log "主流程继续..."
end step
```

#### 示例 3: 带 finally 的资源清理

```flow
let file_uploaded = false

try:
    upload file "test.pdf" to "#file-input"
    file_uploaded = true
    click "#submit"
    wait for navigation
catch error:
    log "上传失败: {error.message}"
    screenshot as "upload-error"
finally:
    # 无论成功失败都执行清理
    if file_uploaded:
        log "文件已上传，清理临时文件"
    end if
    log "清理完成"
end try
```

#### 示例 4: 嵌套 try-catch

```flow
try:
    step "外层操作":
        navigate to "https://example.com"

        try:
            # 内层可能失败的操作
            click ".popup-close"
        catch inner_error:
            log "关闭弹窗失败（可忽略）"
        end try

        click "#login-button"
    end step
catch outer_error:
    log "严重错误: {outer_error.message}"
    # 外层错误处理
end try
```

#### 示例 5: 重试逻辑

```flow
let max_retries = 3
let attempt = 0
let success = false

for attempt in [1, 2, 3]:
    try:
        log "尝试 #{attempt}"
        navigate to "https://example.com"
        wait for element "#content" timeout 5000
        success = true
        # 成功后跳出循环
        # （注：需要添加 break 语句，或使用条件）
    catch error:
        log "尝试 #{attempt} 失败: {error.message}"
        if attempt < max_retries:
            wait 2 seconds  # 等待后重试
        end if
    end try
end for

if not success:
    log "所有尝试都失败"
end if
```

---

## 🔍 语义和行为

### 执行语义

1. **try 块执行**:
   - 按顺序执行 try 块中的语句
   - 如果所有语句成功，跳过 catch 块
   - 如果任何语句失败，停止 try 块执行，进入 catch 块

2. **catch 块执行**:
   - 创建包含错误信息的 error 对象
   - 将 error 对象绑定到指定的变量名
   - 执行 catch 块中的语句
   - catch 块内的错误会向上传播（除非嵌套 try-catch）

3. **finally 块执行**:
   - 无论 try/catch 如何，finally 总是执行
   - 即使 catch 块也失败，finally 仍会执行
   - 用于资源清理、日志记录等

### 作用域规则

- `error` 对象只在 catch 块内可见
- catch 块可以访问 try 块外的变量
- try 块内声明的变量在 catch/finally 块中可见

### 错误处理

| 错误情况 | 行为 |
|---------|------|
| try 块无错误 | 跳过 catch，执行 finally（如有） |
| try 块有错误 | 执行 catch，然后执行 finally（如有） |
| catch 块有错误 | 向上传播，但 finally 仍执行 |
| finally 块有错误 | 向上传播 |

---

## 📊 影响分析

### 版本影响

- [x] **MINOR** (向后兼容的新功能)
  - 新增 try-catch-finally 语句
  - 不影响现有代码

- [ ] MAJOR (不兼容变更)
- [ ] PATCH (bug 修复)

### 兼容性

#### 向后兼容性

- ✅ 完全向后兼容
- **原因**: 这是新增语法，不修改现有语法

#### 现有功能影响

| 现有功能 | 影响 | 说明 |
|---------|------|------|
| 所有现有语句 | 无 | 可以在 try 块中使用 |
| 错误处理 | 增强 | 提供结构化错误处理 |
| 作用域 | 扩展 | 添加 catch 作用域 |

### 学习曲线

- **新手**: 中等
  - 需要理解异常处理概念
  - 但语法简单直观

- **现有用户**: 容易
  - 熟悉其他语言的开发者很容易理解
  - 类似 Python/JavaScript 的 try-catch

### 语法复杂度

**当前状态** (v2.0.0):
```
语句类型: 25/30
表达式层次: 9/10
关键字: 80+/100
```

**添加后** (v2.1.0):
```
语句类型: 26/30  (+1: try-catch)
表达式层次: 9/10  (不变)
关键字: 85/100   (+5: try, catch, finally, end)
```

**评估**: ✅ 在限制内（26/30 = 87%）

---

## 🛠️ 实现方案

### Parser 变更

**需要添加的方法**:
```python
def _parse_try_catch(self) -> TryCatchBlock:
    """
    解析 try-catch 语句

    语法:
        try:
            statements
        catch error:
            statements
        [finally:
            statements]
        end try
    """
    line = self.previous().line

    # 解析 try 块
    self.consume(TokenType.TRY, "Expected 'try'")
    self.consume(TokenType.COLON, "Expected ':' after 'try'")

    # 进入新作用域
    self.symbol_table_stack.enter_scope()
    try_body = self._parse_statement_list_until([TokenType.CATCH])
    self.symbol_table_stack.exit_scope()

    # 解析 catch 块
    self.consume(TokenType.CATCH, "Expected 'catch'")
    error_var = self.consume(TokenType.IDENTIFIER, "Expected error variable name")
    self.consume(TokenType.COLON, "Expected ':' after catch variable")

    # 进入 catch 作用域，添加 error 变量
    self.symbol_table_stack.enter_scope()
    self.symbol_table_stack.define(error_var.value, SymbolType.VARIABLE, line)

    catch_body = self._parse_statement_list_until([TokenType.FINALLY, TokenType.END])

    # 解析可选的 finally 块
    finally_body = None
    if self.match(TokenType.FINALLY):
        self.consume(TokenType.COLON, "Expected ':' after 'finally'")
        finally_body = self._parse_statement_list_until([TokenType.END])

    self.symbol_table_stack.exit_scope()

    self.consume(TokenType.END, "Expected 'end'")
    self.consume(TokenType.TRY, "Expected 'try' after 'end'")

    return TryCatchBlock(
        try_body=try_body,
        catch_variable=error_var.value,
        catch_body=catch_body,
        finally_body=finally_body,
        line=line
    )
```

**AST 节点**:
```python
@dataclass
class TryCatchBlock(ASTNode):
    """Try-Catch 语句"""
    try_body: List[ASTNode]
    catch_variable: str
    catch_body: List[ASTNode]
    finally_body: Optional[List[ASTNode]] = None
    line: int = 0

    def __repr__(self):
        return f"TryCatch(var={self.catch_variable}, try={len(self.try_body)}, catch={len(self.catch_body)})"
```

### Interpreter 变更

```python
def visit_try_catch_block(self, node: TryCatchBlock):
    """执行 try-catch 块"""
    error_occurred = None

    # 执行 try 块
    try:
        for stmt in node.try_body:
            stmt.accept(self)
    except Exception as e:
        # 捕获错误
        error_occurred = e

        # 创建 error 对象
        error_obj = {
            "message": str(e),
            "type": type(e).__name__,
            "line": node.line,
            "statement": str(node)
        }

        # 进入 catch 作用域
        self.symbol_table.enter_scope()
        self.symbol_table.define(node.catch_variable, error_obj)

        # 执行 catch 块
        try:
            for stmt in node.catch_body:
                stmt.accept(self)
        finally:
            self.symbol_table.exit_scope()

    # 执行 finally 块（无论如何都执行）
    if node.finally_body:
        for stmt in node.finally_body:
            stmt.accept(self)
```

### Lexer 变更

**新增 Token**:
- `TokenType.TRY`
- `TokenType.CATCH`
- `TokenType.FINALLY`

**关键字映射**:
```python
KEYWORDS = {
    # ...
    "try": TokenType.TRY,
    "catch": TokenType.CATCH,
    "finally": TokenType.FINALLY,
}
```

### 实现难度

- [x] **中等** (3-5 天)
  - 需要 lexer + parser + interpreter 修改
  - 涉及作用域和错误传播
  - 需要完善的测试

### 依赖项

- [ ] 无特殊依赖
- [x] 依赖现有的作用域系统
- [x] 依赖现有的错误处理机制

---

## 🧪 测试计划

### 测试用例

#### 正常情况

```python
def test_try_catch_basic():
    """测试基本 try-catch"""
    source = """
    let result = "none"

    try:
        result = "success"
    catch error:
        result = "failed"
    end try

    log result
    """
    # 断言: result == "success"

def test_try_catch_with_error():
    """测试捕获错误"""
    source = """
    let error_msg = ""

    try:
        click "#nonexistent"  # 会失败
    catch error:
        error_msg = error.message
        log "Caught: {error_msg}"
    end try
    """
    # 断言: error_msg 包含错误信息

def test_try_catch_finally():
    """测试 finally 块"""
    source = """
    let cleanup_done = false

    try:
        log "try"
    catch error:
        log "catch"
    finally:
        cleanup_done = true
        log "finally"
    end try
    """
    # 断言: cleanup_done == true
```

#### 边界情况

```python
def test_nested_try_catch():
    """测试嵌套 try-catch"""
    source = """
    try:
        try:
            click "#inner"
        catch inner_error:
            log "Inner error"
        end try
    catch outer_error:
        log "Outer error"
    end try
    """

def test_try_catch_in_loop():
    """测试循环中的 try-catch"""
    source = """
    for i in [1, 2, 3]:
        try:
            log "Attempt {i}"
        catch error:
            log "Failed {i}"
        end try
    end for
    """
```

#### 异常情况

```python
def test_try_catch_syntax_errors():
    """测试语法错误"""
    # 缺少 catch
    # 缺少 end try
    # catch 变量名错误
    # finally 位置错误
```

### 测试覆盖率目标

- [ ] 行覆盖率 ≥ 90%
- [ ] 分支覆盖率 ≥ 80%
- [ ] 错误路径测试 100%

---

## 📚 文档变更

### 需要更新的文档

- [ ] `GRAMMAR-MASTER.md` - 添加 Feature 2.5
  ```markdown
  | 2.5 | Try-Catch | `try: ... catch VAR: ... [finally: ...] end try` | ✅ | v2.1 | `_parse_try_catch()` | ✅ | Exception handling |
  ```

- [ ] `GRAMMAR-CHANGELOG.md` - 添加到 [2.1.0] Unreleased
- [ ] `DSL-GRAMMAR.ebnf` - 添加 EBNF 规则
- [ ] `DSL-GRAMMAR-QUICK-REFERENCE.md` - 添加示例
- [ ] `DSL-SYNTAX-CHEATSHEET.md` - 添加速查
- [ ] `02-MODULE-DETAILS.md` - 添加 parser 方法说明
- [ ] `04-API-REFERENCE.md` - 添加使用指南
- [ ] 添加示例到 `examples/flows/try_catch_example.flow`

---

## 🔄 替代方案

### 方案 1: 基于返回码的错误处理

**语法**:
```flow
let result = call "risky.operation"

if result.success:
    log "OK"
else:
    log "Failed: {result.error}"
end if
```

**优点**:
- 不需要新语法
- 明确的错误检查

**缺点**:
- 只适用于服务调用
- 不能捕获语句执行错误
- 代码冗长

### 方案 2: 全局错误处理器

**语法**:
```flow
on error:
    log "Error occurred: {$error.message}"
    screenshot as "error"
end on error

# 后续所有错误都会被捕获
navigate to "..."
click "..."
```

**优点**:
- 集中式错误处理
- 代码简洁

**缺点**:
- 不够灵活
- 无法针对不同错误做不同处理
- 难以实现重试逻辑

### 不做任何改变

**当前做法**:
```flow
# 使用 assert 检查
assert "#element" exists
click "#element"
```

**为什么不够**:
- assert 失败会终止，无法恢复
- 无法实现优雅降级
- 无法记录错误详情继续执行

---

## 💬 讨论记录

### 支持意见

**@core-team**:
- 异常处理是现代语言的标配
- 提高脚本健壮性
- 语法设计清晰，类似主流语言

**需要考虑的问题**:
- finally 块是否必要？（可选）
- error 对象应该包含哪些信息？
- 嵌套 try-catch 的行为？

### 疑虑和问题

**Q: 是否会让语法过于复杂？**
A: try-catch 是标准的异常处理模式，用户应该熟悉。复杂度增加可控（+1 语句类型，+3-4 关键字）。

**Q: 是否有性能影响？**
A: 只在需要时使用，不影响不使用的脚本。实现上使用 Python 的 try-except，性能开销很小。

**Q: 如何与 assert 语句配合？**
A: assert 仍然用于"必须满足"的条件，try-catch 用于"可能失败"的操作。两者互补。

---

## ✅ 决策

### 核心团队评审

- [ ] 技术可行性: ✅ (待确认)
- [ ] 语法一致性: ✅ (待确认)
- [ ] 复杂度控制: ✅ (26/30, 在限制内)
- [ ] 文档完整性: ✅ (待确认)

### 最终决定

- **状态**: 💭 Under Discussion
- **决定日期**: 待定
- **决策者**: Core Team
- **理由**: 需要进一步讨论 finally 的必要性和 error 对象的详细设计

### 待讨论问题

1. finally 块是否作为可选？还是强制要求？
2. error 对象应该包含哪些属性？
3. 是否支持多个 catch 块（不同错误类型）？
4. 嵌套 try-catch 的语义是否清晰？

---

## 📅 实施时间线

_如果批准，预计时间线_

### Phase 1: 设计阶段 (1 天)
- [ ] 讨论并确定最终设计
- [ ] 确定 error 对象结构
- [ ] 更新提案文档

### Phase 2: 实施阶段 (3-4 天)
- [ ] Lexer 添加新 Token (0.5 天)
- [ ] Parser 实现 `_parse_try_catch()` (1 天)
- [ ] Interpreter 实现错误捕获逻辑 (1 天)
- [ ] 单元测试 (1-1.5 天)

### Phase 3: 文档阶段 (1-2 天)
- [ ] 更新所有语法文档
- [ ] 编写使用指南和示例
- [ ] 更新 CHANGELOG

### Phase 4: 验收阶段 (1 天)
- [ ] Code Review
- [ ] 集成测试
- [ ] 用户验收测试

**总计**: 约 6-8 天

---

## 📎 附录

### 参考资料

- Python try-except: https://docs.python.org/3/tutorial/errors.html
- JavaScript try-catch: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/try...catch
- Java exception handling: https://docs.oracle.com/javase/tutorial/essential/exceptions/

### 相关 Issue

_待创建_

---

**提案状态**: 💭 Under Discussion
**最后更新**: 2025-11-25
**维护者**: Core Team
**下一步**: 等待核心团队讨论和决策
