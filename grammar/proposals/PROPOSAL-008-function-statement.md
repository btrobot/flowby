# Grammar Proposal #008: Function Statement

> **提案编号**: #008
> **提出日期**: 2025-11-29
> **提出人**: Flowby Core Team
> **状态**: ✅ Approved (直接实施)
> **目标版本**: 4.3.0
> **影响级别**: MINOR

---

## 📋 提案摘要

添加用户自定义函数（function statement），支持基本的函数定义和调用，用于提升代码可读性和复用性。**不支持递归和闭包**，保持最简化实现。

---

## 🎯 动机和背景

### 问题描述

当前 DSL 脚本中存在以下可读性和复用性问题：

**示例场景 1: 重复的验证逻辑**:
```flow
# 站点 A
step "Validate Site A":
    if not (email contains "@" and email contains "."):
        log "Invalid email"
        workflow_aborted = True

# 站点 B（重复代码）
step "Validate Site B":
    if not (email contains "@" and email contains "."):
        log "Invalid email"
        workflow_aborted = True

# 站点 C（重复代码）
step "Validate Site C":
    if not (email contains "@" and email contains "."):
        log "Invalid email"
        workflow_aborted = True
```

**问题**:
1. 验证逻辑重复 3 次
2. 修改验证规则需要改 3 处
3. 代码意图不明确（`email contains "@"` 不如 `isValidEmail(email)` 语义化）

**示例场景 2: 复杂逻辑封装**:
```flow
step "Check password strength":
    # 10+ 行密码强度验证逻辑混杂在业务流程中
    let has_uppercase = False
    let has_lowercase = False
    let has_digit = False

    for char in password:
        if char >= "A" and char <= "Z":
            has_uppercase = True
        # ... 更多逻辑

    let password_strong = has_uppercase and has_lowercase and has_digit

    if not password_strong:
        log "Weak password"
```

**问题**:
1. 复杂逻辑混在 step 中，降低可读性
2. step 应专注于业务流程，而非实现细节

### 为什么现有功能不够？

| 现有方案 | 局限性 |
|---------|--------|
| **Step 分组** | 只能分组语句，不能接受参数和返回值 |
| **内置函数** | 需要修改 Python 代码，不够灵活 |
| **Resource 扩展** | 适合 API 调用，不适合纯逻辑封装 |
| **重复代码** | 无法消除，维护成本高 |

---

## 💡 提议的解决方案

### 语法设计

#### 基本形式

```bnf
function_def ::= "function" IDENTIFIER "(" parameter_list? ")" ":" NEWLINE
                 INDENT statement+ DEDENT

parameter_list ::= IDENTIFIER ("," IDENTIFIER)*

return_statement ::= "return" expression?
```

#### 具体语法

```flow
# 函数定义
function functionName(param1, param2):
    # function body
    let local_var = param1 + param2
    return local_var

# 函数调用（与内置函数语法一致）
let result = functionName(10, 20)
```

### 详细说明

#### 参数说明

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| functionName | IDENTIFIER | ✅ | 函数名（遵循标识符命名规则） |
| param1, param2, ... | IDENTIFIER | ❌ | 参数列表（0 个或多个） |
| body | statements | ✅ | 函数体（至少 1 条语句） |

#### 特性约束

**支持**:
- ✅ 局部变量（函数内部作用域）
- ✅ 参数传递（按值传递）
- ✅ 返回值（`return expr` 或 `return`）
- ✅ 调用其他函数（包括内置函数和自定义函数）
- ✅ 访问全局常量（const）

**不支持** (明确限制):
- ❌ 递归调用（运行时检测并拒绝）
- ❌ 闭包（无法访问外部函数的局部变量）
- ❌ 嵌套定义（函数只能在顶层定义）
- ❌ 默认参数
- ❌ 可变参数
- ❌ 高阶函数（函数不能作为参数或返回值）

### 使用示例

#### 示例 1: 语义化命名

```flow
/**meta
desc: 使用函数提升代码可读性
*/

# 定义验证函数
function isValidEmail(email):
    return email contains "@" and email contains "."

function isValidPassword(password):
    let length = len(password)
    return length >= 8 and length <= 32

# 使用（语义清晰）
step "Validate input":
    if not isValidEmail(user_email):
        log "Invalid email format"
        workflow_aborted = True

    if not isValidPassword(user_password):
        log "Invalid password length"
        workflow_aborted = True
```

**预期输出**:
```
[INFO] [OK] 定义函数: function isValidEmail(email)
[INFO] [OK] 定义函数: function isValidPassword(password)
[INFO] Validate input
[INFO] Invalid email format (如果邮箱无效)
```

#### 示例 2: 复杂逻辑封装

```flow
# 封装密码强度检查
function isStrongPassword(password):
    if len(password) < 8:
        return False

    let has_uppercase = False
    let has_lowercase = False
    let has_digit = False

    for char in password:
        if char >= "A" and char <= "Z":
            has_uppercase = True
        if char >= "a" and char <= "z":
            has_lowercase = True
        if char >= "0" and char <= "9":
            has_digit = True

    return has_uppercase and has_lowercase and has_digit

# step 专注业务流程
step "Check password":
    if not isStrongPassword(user_password):
        log "Weak password"
        workflow_aborted = True
```

#### 示例 3: 重复代码消除

```flow
# 定义通用的日志函数
function logSuccess(operation, data):
    log "✓ {operation} 成功"
    log "  数据: {data}"

function logFailure(operation, reason):
    log "✗ {operation} 失败"
    log "  原因: {reason}"

# 复用
step "Create account":
    let response = api.createAccount(...)
    if response:
        logSuccess("账号创建", response.email)
    else:
        logFailure("账号创建", "API 返回空")
```

---

## 🔍 语义和行为

### 执行语义

1. **定义阶段**（解析时）:
   - Parser 解析函数定义，创建 `FunctionDefNode`
   - Interpreter 将函数注册到符号表（全局作用域）

2. **调用阶段**（运行时）:
   - 查找函数符号
   - 检查参数数量匹配
   - **检测递归调用**（查找调用栈）
   - 创建新的函数作用域
   - 绑定参数到局部变量
   - 执行函数体
   - 遇到 `return` 或函数结束时返回值
   - 恢复调用前的作用域

3. **清理阶段**:
   - 函数返回后，局部变量自动销毁
   - 调用栈弹出当前函数

### 作用域规则

**函数作用域**:
```
全局作用域
   ├─ 常量 (const)
   ├─ 全局变量 (let)
   └─ 函数定义
        └─ 函数作用域（独立）
             ├─ 参数
             ├─ 局部变量
             └─ 可访问：全局常量、其他函数
             ❌ 不可访问：全局变量（避免副作用）
```

**变量查找顺序**:
1. 局部变量（参数 + let）
2. 全局常量（const）
3. 内置函数
4. 其他自定义函数
5. ❌ 不查找全局变量

### 错误处理

| 错误情况 | 行为 | 示例 |
|---------|------|------|
| 函数重定义 | 编译错误 | `function foo(): ... function foo(): ...` |
| 未定义函数 | 运行时错误 | `bar()` 但 `bar` 未定义 |
| 参数数量不匹配 | 运行时错误 | `foo(1)` 但 `function foo(a, b)` |
| 递归调用 | 运行时错误 | `function foo(): foo()` |
| 嵌套定义 | 语法错误 | `function outer(): function inner(): ...` |

---

## 📊 影响分析

### 版本影响

- [x] **MINOR** (向后兼容的新功能)
  - 新增功能
  - 不影响现有代码
  - 现有脚本无需修改

### 兼容性

#### 向后兼容性

- ✅ 与现有语法完全兼容
- ✅ `function` 是新增关键字，不会与现有代码冲突
- ✅ 现有脚本无需任何修改

#### 现有功能影响

| 现有功能 | 影响 | 说明 |
|---------|------|------|
| Step 语句 | 无 | 函数可在 step 中调用 |
| 内置函数 | 无 | 语法一致，透明集成 |
| 变量作用域 | 扩展 | 新增函数作用域 |
| 符号表 | 扩展 | 新增函数符号类型 |

### 学习曲线

- **新手**: 容易
  - 类似 Python/JavaScript 的函数语法
  - 比内置函数更灵活

- **现有用户**: 容易
  - 已熟悉内置函数调用 `len()`, `log()`
  - 自定义函数调用语法完全一致

### 语法复杂度

**当前状态** (v4.2):
```
语句类型: 25/30
表达式层次: 9/10
关键字: 80+/100
```

**添加后** (v4.3):
```
语句类型: 27/30  (增加 2 个: function, return)
表达式层次: 9/10  (无变化)
关键字: 82/100   (增加 2 个: function, return)
```

**评估**: ✅ 在限制内（距离上限还有空间）

---

## 🛠️ 实现方案

### Parser 变更

**需要添加的方法**:
```python
def _parse_function_def(self) -> FunctionDefNode:
    """
    解析函数定义

    语法:
        function functionName(param1, param2):
            body
    """
    self.expect(Token.FUNCTION)
    name = self.expect(Token.IDENTIFIER)

    self.expect(Token.LPAREN)
    params = self._parse_parameter_list()
    self.expect(Token.RPAREN)

    self.expect(Token.COLON)
    self.expect(Token.INDENT)
    body = self._parse_block()
    self.expect(Token.DEDENT)

    return FunctionDefNode(name, params, body)

def _parse_parameter_list(self) -> List[str]:
    """解析参数列表"""
    params = []
    if self.current_token.type == Token.IDENTIFIER:
        params.append(self.current_token.value)
        self.advance()
        while self.current_token.type == Token.COMMA:
            self.advance()
            params.append(self.expect(Token.IDENTIFIER))
    return params

def _parse_return_statement(self) -> ReturnNode:
    """解析 return 语句"""
    self.expect(Token.RETURN)
    value = None
    if self.current_token.type not in [Token.NEWLINE, Token.DEDENT]:
        value = self._parse_expression()
    return ReturnNode(value)
```

**AST 节点**:
```python
@dataclass
class FunctionDefNode(ASTNode):
    name: str
    params: List[str]
    body: List[ASTNode]

@dataclass
class ReturnNode(ASTNode):
    value: Optional[Expression]
```

### Interpreter 变更

```python
def _execute_function_def(self, node: FunctionDefNode):
    """注册函数到符号表"""
    function = FunctionSymbol(node.name, node.params, node.body)
    self.symbol_table.define_function(node.name, function)
    self.logger.info(f"[OK] 定义函数: function {node.name}({', '.join(node.params)})")

def _execute_function_call(self, node: FunctionCallNode) -> Any:
    """执行函数调用"""
    # 1. 查找函数
    function = self.symbol_table.get_function(node.function_name)
    if not function:
        raise ExecutionError(...)

    # 2. 检查参数数量
    if len(node.args) != len(function.params):
        raise ExecutionError(...)

    # 3. 检测递归
    if node.function_name in self.call_stack:
        raise ExecutionError(error_type="RECURSION_NOT_SUPPORTED", ...)

    # 4. 计算参数
    arg_values = [self._evaluate_expression(arg) for arg in node.args]

    # 5. 创建函数作用域
    self.call_stack.append(node.function_name)
    self.symbol_table.push_scope()

    # 6. 绑定参数
    for param, value in zip(function.params, arg_values):
        self.symbol_table.define(param, value, SymbolType.VARIABLE)

    # 7. 执行函数体
    return_value = None
    try:
        for stmt in function.body:
            if isinstance(stmt, ReturnNode):
                return_value = self._execute_return(stmt)
                break
            self._execute_statement(stmt)
    finally:
        self.call_stack.pop()
        self.symbol_table.pop_scope()

    return return_value
```

### Lexer 变更

**新增 Token**:
```python
Token.FUNCTION = 'FUNCTION'
Token.RETURN = 'RETURN'

# 在 keywords 字典中添加
keywords = {
    # ... 现有关键字
    'function': Token.FUNCTION,
    'return': Token.RETURN,
}
```

### 实现难度

- [x] **中等** (3-5 天)
  - Parser 修改（2 个新方法）
  - Interpreter 修改（函数调用、作用域管理）
  - 符号表扩展（函数符号）
  - 涉及中等复杂度的作用域管理

### 依赖项

- [x] 无依赖（基于现有的 Parser/Interpreter 架构）

---

## 🧪 测试计划

### 测试用例

#### 正常情况

```python
def test_function_basic():
    """测试基本函数定义和调用"""
    source = """
    function add(a, b):
        return a + b

    let result = add(10, 20)
    assert result == 30
    """

def test_function_local_variables():
    """测试局部变量"""
    source = """
    let x = 100

    function test():
        let x = 200
        return x

    let result = test()
    assert result == 200
    assert x == 100
    """

def test_function_call_builtin():
    """测试调用内置函数"""
    source = """
    function greet(name):
        log "Hello, {name}"

    greet("Alice")
    """

def test_function_call_other_function():
    """测试调用其他自定义函数"""
    source = """
    function helper():
        return 42

    function main():
        return helper()

    let result = main()
    assert result == 42
    """
```

#### 边界情况

```python
def test_function_no_params():
    """测试无参数函数"""
    source = """
    function getValue():
        return 42

    let result = getValue()
    assert result == 42
    """

def test_function_no_return():
    """测试无返回值函数"""
    source = """
    function doSomething():
        let x = 10

    let result = doSomething()
    assert result == None
    """

def test_function_many_params():
    """测试多参数函数"""
    source = """
    function sum5(a, b, c, d, e):
        return a + b + c + d + e

    let result = sum5(1, 2, 3, 4, 5)
    assert result == 15
    """
```

#### 异常情况

```python
def test_function_recursion_rejected():
    """测试递归调用被拒绝"""
    source = """
    function factorial(n):
        if n <= 1:
            return 1
        return n * factorial(n - 1)

    factorial(5)
    """
    # 期望: ExecutionError(RECURSION_NOT_SUPPORTED)

def test_function_redefinition():
    """测试函数重定义"""
    source = """
    function foo():
        return 1

    function foo():
        return 2
    """
    # 期望: ExecutionError(FUNCTION_REDEFINITION)

def test_function_wrong_arg_count():
    """测试参数数量错误"""
    source = """
    function add(a, b):
        return a + b

    add(10)
    """
    # 期望: ExecutionError(ARGUMENT_MISMATCH)

def test_function_undefined():
    """测试调用未定义函数"""
    source = """
    foo()
    """
    # 期望: ExecutionError(UNDEFINED_FUNCTION)
```

### 测试覆盖率目标

- [x] 行覆盖率 ≥ 90%
- [x] 分支覆盖率 ≥ 80%
- [x] 所有错误路径都有测试

---

## 📚 文档变更

### 需要更新的文档

- [x] `MASTER.md` - 添加新特性（2 个语句）
- [x] `CHANGELOG.md` - 添加 v4.3.0 变更记录
- [x] `DSL-GRAMMAR.ebnf` - 添加 function 和 return 的 EBNF 规则
- [x] 添加示例到 `examples/flows/`

### 文档示例

**在 MASTER.md 中的条目**:

```markdown
## 9. Functions (3 features)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 9.1 | Function Definition | `function name(params):` | ✅ | v4.3 | `_parse_function_def()` | ✅ | No recursion, no closure |
| 9.2 | Function Call | `name(args)` | ✅ | v4.3 | `_parse_function_call()` | ✅ | Same as built-in |
| 9.3 | Return Statement | `return expr` | ✅ | v4.3 | `_parse_return_statement()` | ✅ | Single return value |
```

---

## 🔄 替代方案

### 方案 1: 扩展内置函数库

**做法**:
```python
# builtin_functions.py
def builtin_is_valid_email(email: str) -> bool:
    return '@' in email and '.' in email
```

**优点**:
- 实现简单（每个函数 ~10 行）
- 无需语法变更

**缺点**:
- 不够灵活（需要修改 Python 代码）
- 无法满足用户特定需求
- 需要预先定义所有常用函数

### 方案 2: 仅支持内联函数（lambda）

**语法**:
```flow
let add = (a, b) => a + b
let result = add(10, 20)
```

**优点**:
- 语法简洁

**缺点**:
- 增加语法复杂度（新增箭头语法）
- 不适合多行函数体
- 学习成本高（函数式编程概念）

### 方案 3: 使用宏/模板系统

**语法**:
```flow
macro validate_email(email):
    if not (email contains "@"):
        log "Invalid"
```

**优点**:
- 编译期展开，零运行时开销

**缺点**:
- 实现复杂
- 无法动态调用
- 调试困难

### 不做任何改变

**当前做法**:
```flow
# 重复代码或 step 分组
step "Validate":
    if not (email contains "@"):
        log "Invalid"
```

**为什么不够**:
- 代码重复
- 可读性差（`email contains "@"` vs `isValidEmail(email)`）
- 难以维护

---

## 💬 讨论记录

### 设计决策

**决策 1**: 不支持递归
- **理由**:
  - DSL 脚本中几乎不存在递归算法需求
  - 可用 while 循环替代
  - 避免栈溢出风险

**决策 2**: 不支持闭包
- **理由**:
  - 闭包增加实现复杂度（捕获变量、内存管理）
  - DSL 场景不需要高级函数式编程特性
  - 保持简洁性

**决策 3**: 函数调用语法与内置函数一致
- **理由**:
  - 用户已熟悉 `len()`, `log()` 语法
  - 语法统一，学习成本低

---

## ✅ 决策

### 核心团队评审

- [x] 技术可行性: ✅
- [x] 语法一致性: ✅
- [x] 复杂度控制: ✅
- [x] 文档完整性: ✅

### 最终决定

- **状态**: ✅ Approved
- **决定日期**: 2025-11-29
- **决策者**: Core Team
- **理由**:
  - 显著提升代码可读性和可维护性
  - 实现成本可控（~1030 行，1.5-2 周）
  - 符合 DSL 设计理念（低代码、声明式）
  - 向后兼容，不影响现有代码

### 如果批准

**目标版本**: 4.3.0
**预计发布**: 2025-12-13
**负责人**: Core Team

---

## 📅 实施时间线

### Phase 1: 设计阶段 (完成)
- [x] 提案编写
- [x] 分析文档创建
- [x] 核心团队评审

### Phase 2: 实施阶段 (预计 5 天)
- [ ] Lexer 添加 token (0.5 天)
- [ ] Parser 实现 (1.5 天)
- [ ] Interpreter 实现 (2 天)
- [ ] 符号表扩展 (0.5 天)
- [ ] 单元测试 (0.5 天)

### Phase 3: 文档阶段 (预计 1 天)
- [ ] 更新 MASTER.md
- [ ] 更新 CHANGELOG.md
- [ ] 更新 EBNF
- [ ] 编写示例脚本

### Phase 4: 验收阶段 (预计 1 天)
- [ ] Code Review
- [ ] check_sync.py 验证
- [ ] 集成测试
- [ ] 归档提案

**总计**: 约 7 天（1.5 周）

---

## 📎 附录

### 参考资料

- [MINIMAL_FUNCTION_ANALYSIS.md](../../docs/MINIMAL_FUNCTION_ANALYSIS.md) - 最简化函数分析
- [FUNCTION_NECESSITY_ANALYSIS.md](../../docs/FUNCTION_NECESSITY_ANALYSIS.md) - 必要性分析

### 相关 Issue

- 分支: feature/function-implementation

---

**提案状态**: ✅ Approved
**最后更新**: 2025-11-29
**维护者**: Flowby Core Team
