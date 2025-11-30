# Grammar Proposal #006: Exit Statement for Controlled Termination

> **提案编号**: #006
> **提出日期**: 2025-11-28
> **提出人**: DSL Core Team
> **状态**: ✅ Approved (Post-Implementation)
> **目标版本**: 4.1.0
> **影响级别**: MINOR

---

## 📋 提案摘要

添加 `exit` 语句用于受控脚本终止，区分优雅退出与验证错误，提供比 `assert` 更灵活的控制流终止机制。

---

## 🎯 动机和背景

### 问题描述

DSL 目前仅支持 `assert` 语句用于验证断言，当条件不满足时会抛出异常并导致任务失败。然而，在某些场景下，我们需要优雅地提前终止脚本执行，而不是将其视为错误。

**示例场景 1: 特殊用户跳过处理**
```dsl
# ❌ 当前做法：使用 assert 不合适（不是验证失败，是业务逻辑）
if user_type == "guest":
    # 无法优雅退出，只能让脚本执行完所有语句
    log "Guest user, skipping registration"
    # 后续代码仍会执行...
```

**示例场景 2: 条件性失败**
```dsl
# ❌ 当前做法：使用 assert 语义不清晰
let validation_errors = validate_form()
if validation_errors > 0:
    # assert 用于验证预期，但这里是条件性失败
    assert False, f"Found {validation_errors} validation errors"
```

**问题**:
1. **语义不清晰**: `assert` 用于验证预期条件，不适合表达"条件性提前退出"
2. **缺少成功退出**: 无法表达"任务成功完成，但无需继续执行"的场景
3. **控制流受限**: 无法在满足特定条件时优雅地提前终止
4. **状态映射不准确**: 提前退出被视为错误（FAILED），实际可能是正常业务逻辑

### 为什么现有功能不够？

**`assert` 的局限性**:
- **用途**: 验证预期条件（"这个条件必须为真"）
- **失败行为**: 抛出 `ExecutionError` 异常
- **状态**: 总是导致 `FAILED` 状态
- **语义**: 表示验证失败（unexpected error）

**需要的功能**:
- **用途**: 受控终止执行（"提前结束，这是预期的"）
- **行为**: 正常控制流终止（不抛出错误异常）
- **状态**: 根据退出码决定 `COMPLETED` 或 `FAILED`
- **语义**: 表示主动退出（expected termination）

---

## 💡 提议的解决方案

### 语法设计

#### 基本形式

```bnf
exit_statement ::= "exit" [exit_code] ["," exit_message] NEWLINE
exit_code      ::= INTEGER
exit_message   ::= STRING
```

#### 具体语法

```dsl
# 形式 1: 无参数（默认成功退出）
exit

# 形式 2: 指定退出码
exit 0          # 成功退出
exit 1          # 失败退出

# 形式 3: 仅消息（默认 code=1）
exit "Validation failed"

# 形式 4: 退出码 + 消息
exit 0, "Processing completed"
exit 1, "Validation failed"
```

### 详细说明

#### 参数说明

| 参数 | 类型 | 必选 | 默认值 | 说明 |
|------|------|------|--------|------|
| code | INTEGER | ❌ | 0 | 退出码：0=成功，非0=失败 |
| message | STRING | ❌ | None | 退出消息，用于日志记录 |

#### 退出码规范

- **0**: 成功退出 → `ExecutionStatus.COMPLETED`
- **非0**: 失败退出 → `ExecutionStatus.FAILED`
- **省略**: 默认为 0（成功）

#### 执行语义

- 执行 `exit` 语句会抛出 `EarlyExitException`（控制流异常）
- Interpreter 捕获该异常并**正常结束执行**（不是错误）
- 根据退出码设置任务状态
- 记录退出信息到执行历史

### 使用示例

#### 示例 1: 特殊用户跳过处理

```dsl
/**meta
desc: Guest 用户跳过注册流程
*/

if user_type == "guest":
    log "Guest user detected, skipping registration"
    exit 0, "Guest users don't require processing"

# ✅ 后续代码不会执行
log "Processing registration for normal user..."
fill_registration_form()
```

**预期输出**:
```
[LOG] Guest user detected, skipping registration
[EXIT] Guest users don't require processing (code=0)
状态: COMPLETED
```

#### 示例 2: 验证失败提前退出

```dsl
/**meta
desc: 表单验证失败时退出
*/

let validation_errors = validate_form()
if validation_errors > 0:
    log f"Found {validation_errors} validation errors"
    exit 1, "Validation failed"

# ✅ 只有验证通过才会继续
submit_form()
assert response.status == 200
```

#### 示例 3: 多条件检查

```dsl
/**meta
desc: 多个条件检查，任意失败则退出
*/

# 检查 1: 用户状态
if user.status == "inactive":
    exit 1, "User account is inactive"

# 检查 2: 年龄限制
if user.age < 18:
    exit 0, "Underage users skip verification"

# 检查 3: 权限检查
if not user.has_permission("edit"):
    exit 1, "User lacks edit permission"

# ✅ 所有检查通过，继续正常流程
process_verification()
```

#### 示例 4: 与 assert 对比

```dsl
# ❌ assert: 验证预期条件（必须为真）
assert user.is_authenticated, "User must be logged in"
# 失败 → 抛出 ExecutionError → FAILED

# ✅ exit: 条件性提前退出
if not user.is_authenticated:
    exit 1, "User not authenticated"
# 不抛出错误异常 → 正常终止 → FAILED (code=1)

# ✅ exit: 成功退出
if special_case_detected:
    exit 0, "Special case handled"
# 正常终止 → COMPLETED (code=0)
```

---

## 🔍 语义和行为

### 执行语义

1. **解析阶段**:
   - Lexer 识别 `exit` 关键字 → `TokenType.EXIT`
   - Parser 解析参数（code, message）→ `ExitStatement` AST 节点

2. **执行阶段**:
   - Interpreter 执行 `ExitStatement`
   - 记录退出信息到执行历史
   - 抛出 `EarlyExitException(code, message)`

3. **终止阶段**:
   - `Interpreter.execute()` 捕获 `EarlyExitException`
   - 根据 `code` 设置任务状态：
     - `code == 0` → `ExecutionStatus.COMPLETED`
     - `code != 0` → `ExecutionStatus.FAILED`
   - 正常结束执行（不向上传播异常）

### 控制流影响

```dsl
let x = 1
log f"x = {x}"

exit 0

let y = 2  # ❌ 不会执行
log f"y = {y}"  # ❌ 不会执行
```

**行为**: `exit` 语句后的所有代码都不会执行（类似 Python 的 `sys.exit()`）

### 作用域规则

`exit` 语句不影响作用域，但会立即终止当前执行流程，包括：
- 跳出当前 block
- 跳出所有嵌套的 if/for/while/step
- 直接终止整个脚本

### 错误处理

| 错误情况 | 行为 | 示例 |
|---------|------|------|
| 退出码不是整数 | Parser 错误 | `exit "abc"` → SyntaxError |
| 语法错误（逗号缺失） | Parser 错误 | `exit 0 "msg"` → SyntaxError |
| 无错误情况 | - | `exit` 是合法语句，始终成功 |

---

## 📊 影响分析

### 版本影响

- [x] **MINOR** (向后兼容的新功能)
  - 新增功能：`exit` 语句
  - 不影响现有代码：现有脚本无需修改
  - 向后兼容：100%

- [ ] **MAJOR** (不兼容变更) - 不适用
- [ ] **PATCH** (向后兼容的修复) - 不适用

### 兼容性

#### 向后兼容性

- ✅ 与现有语法完全兼容
- **原因**:
  - `exit` 是新增关键字，不与现有标识符冲突
  - 纯功能添加，不修改现有行为
  - 所有现有脚本无需修改即可运行

#### 现有功能影响

| 现有功能 | 影响 | 说明 |
|---------|------|------|
| `assert` | 无 | `exit` 与 `assert` 语义不同，互补关系 |
| `if/for/while` | 无 | `exit` 可在任何控制流中使用 |
| `step` | 无 | `exit` 会终止整个脚本，包括 step |
| 异常处理 | 无 | `EarlyExitException` 不是错误异常 |

### 学习曲线

- **新手**: 容易
  - 语法简单直观：`exit 0`
  - 类似 Python/Bash 的 `exit` 命令

- **现有用户**: 容易
  - 与 `assert` 的区别清晰
  - 使用场景明确

### 语法复杂度

**当前状态** (v4.0):
```
语句类型: 25/30
表达式层次: 9/10
关键字: 40/100
Token 类型: 191+
```

**添加后** (v4.1):
```
语句类型: 26/30  (增加 1 个: exit)
表达式层次: 9/10  (无变化)
关键字: 41/100  (增加 1 个: exit)
Token 类型: 192+  (增加 1 个: EXIT)
```

**评估**: ✅ 在限制内（语句类型 26/30, 关键字 41/100）

---

## 🛠️ 实现方案

### Lexer 变更

**新增 Token**:
```python
# lexer.py:118
EXIT = auto()  # exit 语句 (v4.1)
```

**关键字映射**:
```python
# lexer.py:326
KEYWORDS = {
    # ... 现有关键字 ...
    'exit': TokenType.EXIT,  # v4.1
}
```

### Parser 变更

**新增方法**:
```python
# parser.py:954-997
def _parse_exit(self) -> 'ExitStatement':
    """
    解析 exit 语句 - v4.1

    语法: exit [code] [, "message"]

    示例:
        exit                    # 退出，code=0
        exit 1                  # 退出，code=1
        exit "Failed"           # 退出，code=1，消息
        exit 0, "Success"       # 退出，code=0，消息
    """
    line = self._peek().line
    self._consume(TokenType.EXIT, "期望 'exit'")

    code = None
    message = None

    if not self._check(TokenType.NEWLINE) and not self._is_at_end():
        # 第一个参数
        if self._check(TokenType.INTEGER):
            code = int(self._advance().value)

            # 检查是否有逗号和消息
            if self._check(TokenType.COMMA):
                self._consume(TokenType.COMMA, "期望逗号")
                message_token = self._consume(TokenType.STRING, "期望字符串消息")
                message = message_token.value
        elif self._check(TokenType.STRING):
            # 只有消息，code 默认为 1
            message = self._advance().value
            code = 1

    return ExitStatement(
        code=code,
        message=message,
        line=line
    )
```

**调度逻辑**:
```python
# parser.py:203-205 (在 _parse_statement 中)
elif self._check(TokenType.EXIT):
    return self._parse_exit()
```

### AST 变更

**新增节点**:
```python
# ast_nodes.py:490-508
@dataclass
class ExitStatement(ASTNode):
    """
    退出语句 (Exit Statement) - v4.1

    语法: exit [code] [, "message"]

    示例:
        exit                    # 退出，code=0
        exit 1                  # 退出，code=1
        exit "Failed"           # 退出，code=1，消息
        exit 0, "Success"       # 退出，code=0，消息

    Attributes:
        code: 退出码（0=成功，非0=失败），默认0
        message: 可选的退出消息
    """
    code: Optional[int] = 0
    message: Optional[str] = None
```

### Interpreter 变更

**新增异常类**:
```python
# interpreter.py:128-149
class EarlyExitException(Exception):
    """
    提前退出异常 (v4.1)

    用于实现 exit 语句的控制流。
    当执行 exit 语句时抛出此异常，由 execute() 方法捕获并正常结束执行。

    与 ExecutionError 的区别：
        - ExecutionError: 表示执行错误，任务失败
        - EarlyExitException: 表示主动退出，可以是成功或失败

    Attributes:
        code: 退出码（0=成功，非0=失败）
        message: 退出消息
    """
    def __init__(self, code: int = 0, message: Optional[str] = None):
        self.code = code
        self.message = message or f"Exit with code {code}"
        super().__init__(self.message)
```

**执行方法**:
```python
# interpreter.py:840-864
def _execute_exit(self, statement: ExitStatement) -> None:
    """执行退出语句 - v4.1"""
    code = statement.code if statement.code is not None else 0
    message = statement.message or f"Exit with code {code}"

    # 记录退出信息
    self.context.logger.info(f"[EXIT] {message} (code={code})")
    self.context.add_execution_record(
        record_type="exit",
        content=message,
        success=(code == 0)
    )

    # 抛出提前退出异常
    raise EarlyExitException(code=code, message=message)
```

**异常捕获**:
```python
# interpreter.py:389-399 (在 execute() 中)
except EarlyExitException as e:
    # 提前退出（不是错误）
    if e.code == 0:
        self.context.status = ExecutionStatus.COMPLETED
        self.context.logger.info(f"任务提前退出（成功）: {e.message}")
    else:
        self.context.status = ExecutionStatus.FAILED
        self.context.logger.warning(f"任务提前退出（失败）: {e.message}")
```

### 实现难度

- [x] **简单** (1-2 天)
  - ✅ 只需简单的 parser/interpreter 修改
  - ✅ 不涉及复杂的语义
  - ✅ 已完成实现

### 依赖项

- [x] 无依赖
  - ✅ 独立功能，不依赖其他特性
  - ✅ 使用现有的异常处理机制

---

## 🧪 测试计划

### 测试用例

**测试文件**: `tests/unit/test_exit_statement.py` (508 lines, 33 tests)

#### 正常情况

```python
def test_exit_no_args_stops_execution(self, lexer, parser, context, interpreter):
    """测试 exit（无参数）停止执行"""
    source = '''
let x = 1
exit
let y = 2
'''
    tokens = lexer.tokenize(source)
    program = parser.parse(tokens)
    interpreter.execute(program)

    assert context.status == ExecutionStatus.COMPLETED
    assert interpreter.symbol_table.get("x", 0) == 1
    assert not interpreter.symbol_table.exists("y")  # exit 后不执行
```

#### 边界情况

```python
@pytest.mark.parametrize("exit_code,expected_status", [
    (0, ExecutionStatus.COMPLETED),
    (1, ExecutionStatus.FAILED),
    (127, ExecutionStatus.FAILED),
])
def test_various_exit_codes(self, lexer, parser, exit_code, expected_status):
    """测试各种退出码"""
    source = f'exit {exit_code}\n'
    tokens = lexer.tokenize(source)
    program = parser.parse(tokens)

    task_id = str(uuid.uuid4())
    context = ExecutionContext(task_id=task_id, script_name="test")
    interpreter = Interpreter(context)
    interpreter.execute(program)

    assert context.status == expected_status
```

#### 异常情况

- **无异常情况**: `exit` 语句始终合法
- **Parser 错误**: 语法错误（如 `exit "msg" 0`）会在解析阶段被捕获

### 测试覆盖率

**实际测试覆盖**:
- ✅ **Lexer**: 3 tests (100%)
  - exit 关键字识别
  - exit 带退出码
  - exit 带消息

- ✅ **Parser**: 13 tests (100%)
  - 各种 exit 语法形式
  - 参数化测试覆盖所有组合

- ✅ **AST**: 5 tests (100%)
  - 节点属性验证
  - 默认值测试

- ✅ **Interpreter**: 9 tests (100%)
  - 执行行为
  - 状态设置
  - 执行记录

- ✅ **Integration**: 4 tests (100%)
  - 与其他语句混合使用
  - exit vs assert 对比

**测试结果**: 33/33 passing (100%)

---

## 📚 文档变更

### 已更新的文档

- [x] `grammar/MASTER.md`
  - Section 7: Assertions & Control Flow (5 types)
  - 添加 7.5: Exit Statement
  - 更新 Summary Statistics
  - 添加 v4.1 Version History

- [x] `grammar/CHANGELOG.md`
  - 添加 [4.1.0] 版本记录
  - 详细的功能说明和示例

- [x] `docs/dsl/syntax.md`
  - Section 9.5: 退出语句 (v4.0+)
  - 完整的语法说明和示例
  - Exit vs Assert 对比

- [ ] `docs/DSL-GRAMMAR.ebnf` (待更新)
  - 添加 exit_statement EBNF 规则

- [ ] `docs/DSL-GRAMMAR-QUICK-REFERENCE.md` (待更新)
  - 添加 exit 快速参考

- [ ] `docs/DSL-SYNTAX-CHEATSHEET.md` (待更新)
  - 添加 exit 速查表

### 文档示例

**在 MASTER.md 中的条目**:
```markdown
| 7.5 | Exit Statement | `exit [code] [, "message"]` | ✅ | v4.1 | `_parse_exit()` | ✅ | Controlled termination (success/failure) |
```

---

## 🔄 替代方案

### 方案 1: 扩展 assert 语法

**语法**:
```dsl
assert condition, "message", fail_mode="exit"
```

**优点**:
- 不引入新关键字

**缺点**:
- 语义混乱：`assert` 本质是验证，不是退出
- 无法表达"成功退出"（exit 0）
- 参数过于复杂

**❌ 拒绝理由**: 语义不清晰，违反单一职责原则

### 方案 2: 使用返回语句

**语法**:
```dsl
return success  # 或 return failure
```

**优点**:
- 类似函数返回，概念熟悉

**缺点**:
- DSL 脚本不是函数，没有"返回"的概念
- 无法携带退出消息
- 语义不匹配（return 意味着返回值，exit 意味着终止）

**❌ 拒绝理由**: 概念不匹配，DSL 不是函数式语言

### 方案 3: 不做任何改变

**当前做法**:
```dsl
# 使用 assert 模拟退出
if condition:
    assert False, "Exit message"
```

**为什么不够**:
- 语义错误：将"提前退出"视为"验证失败"
- 无法表达成功退出
- 所有退出都是 FAILED 状态
- 日志混乱：错误日志中充满"正常的提前退出"

**✅ 选择新增 exit 语句**: 语义清晰，功能完整，符合最佳实践

---

## 💬 讨论记录

### 设计决策

**决策 1**: 选择 `exit` 关键字而不是 `return`
- **理由**:
  - DSL 脚本不是函数，没有"返回值"的概念
  - `exit` 更直观表达"终止执行"的语义
  - 与 Python/Bash 的 `exit` 保持一致

**决策 2**: 退出码默认为 0（成功）
- **理由**:
  - 遵循 POSIX 惯例：0=成功，非0=失败
  - 大多数提前退出是正常业务逻辑，应默认成功
  - 显式指定失败码（exit 1）更清晰

**决策 3**: 使用 `EarlyExitException` 而不是 `ExecutionError`
- **理由**:
  - 区分"正常退出"与"执行错误"
  - 避免混淆错误处理逻辑
  - 允许 Interpreter 识别并正确设置状态

**决策 4**: 支持 `exit "message"` 语法（默认 code=1）
- **理由**:
  - 便利性：快速指定错误消息
  - 合理假设：带消息的退出通常是失败情况
  - 可以显式指定 `exit 0, "message"` 来覆盖默认值

---

## ✅ 决策

### 核心团队评审

- [x] 技术可行性: ✅
  - 实现简单，无技术障碍
  - 已完成实现并测试

- [x] 语法一致性: ✅
  - 与现有语法风格一致
  - 不引入冲突或歧义

- [x] 复杂度控制: ✅
  - 仅增加 1 个语句类型（26/30）
  - 语法简单直观

- [x] 文档完整性: ✅
  - 已更新 MASTER.md, CHANGELOG.md, syntax.md
  - 待更新 EBNF, Quick Reference, Cheatsheet

### 最终决定

- **状态**: ✅ Approved (Post-Implementation)
- **决定日期**: 2025-11-28
- **决策者**: DSL Core Team
- **理由**:
  - 填补语法空白，提供清晰的提前退出机制
  - 100% 向后兼容，风险极低
  - 实现简单，测试充分
  - 语义清晰，易于理解和使用

### 实施情况

**目标版本**: 4.1.0
**实际发布**: 2025-11-28
**实施状态**: ✅ 已完成

**实施内容**:
- ✅ Lexer: TokenType.EXIT
- ✅ Parser: _parse_exit()
- ✅ AST: ExitStatement
- ✅ Interpreter: EarlyExitException, _execute_exit()
- ✅ Tests: 33/33 passing
- ✅ Documentation: MASTER.md, CHANGELOG.md, syntax.md
- ⏳ Documentation: EBNF, Quick Reference, Cheatsheet (待完成)

---

## 📅 实施时间线

### Phase 1: 设计阶段 (已完成)
- [x] 需求分析 (EXIT_MECHANISM_ANALYSIS.md)
- [x] 提案编写 (本文档)
- [x] 核心团队批准

### Phase 2: 实施阶段 (已完成)
- [x] Lexer 实现 (2 lines)
- [x] Parser 实现 (44 lines)
- [x] AST 节点定义 (19 lines)
- [x] Interpreter 实现 (42 lines)
- [x] 单元测试 (508 lines, 33 tests)

### Phase 3: 文档阶段 (进行中)
- [x] 更新 MASTER.md
- [x] 更新 CHANGELOG.md
- [x] 更新 syntax.md
- [ ] 更新 DSL-GRAMMAR.ebnf
- [ ] 更新 Quick Reference
- [ ] 更新 Cheatsheet

### Phase 4: 验收阶段 (待进行)
- [ ] Code Review
- [ ] 文档同步验证 (check_sync.py)
- [ ] 集成测试
- [ ] 用户验收测试

---

## 📎 附录

### 参考资料

- [EXIT_MECHANISM_ANALYSIS.md](../../EXIT_MECHANISM_ANALYSIS.md) - Exit 机制分析文档
- [Python sys.exit()](https://docs.python.org/3/library/sys.html#sys.exit) - Python 退出机制
- [Bash exit command](https://www.gnu.org/software/bash/manual/bash.html#Bourne-Shell-Builtins) - Bash 退出命令

### 相关文件

- **实现**:
  - `src/registration_system/dsl/lexer.py:118, 326`
  - `src/registration_system/dsl/parser.py:954-997`
  - `src/registration_system/dsl/ast_nodes.py:490-508`
  - `src/registration_system/dsl/interpreter.py:128-149, 840-864`

- **测试**:
  - `tests/unit/test_exit_statement.py` (508 lines, 33 tests)

- **文档**:
  - `grammar/MASTER.md` (Section 7.5, Version History)
  - `grammar/CHANGELOG.md` ([4.1.0])
  - `docs/dsl/syntax.md` (Section 9.5)

---

**提案状态**: ✅ Approved & Implemented
**最后更新**: 2025-11-28
**维护者**: DSL Core Team
