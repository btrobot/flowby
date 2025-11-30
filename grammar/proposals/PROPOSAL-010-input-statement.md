# PROPOSAL-010: Input Statement (控制台交互输入)

**提案编号**: PROPOSAL-010
**提案标题**: Input Statement - 控制台交互输入语句
**提案类型**: 新增语法特性
**目标版本**: v5.1
**提案状态**: 📝 Draft
**提交日期**: 2025-11-29
**提案人**: System Analysis

---

## 📋 提案概述

### 问题陈述

当前 DSL 是完全自动化执行的脚本语言，**不支持运行时用户交互**。这导致以下场景无法实现：

1. **调试场景**: 无法在关键点暂停并让用户决定下一步
2. **半自动化流程**: 某些步骤需要人工确认或输入
3. **动态参数**: 运行时才能确定的参数（如验证码、动态密码）
4. **交互式配置**: 根据用户选择执行不同分支
5. **测试数据输入**: 手动输入测试数据而非硬编码

### 解决方案

引入 **`input` 语句**，允许脚本在运行时从控制台读取用户输入，实现交互式控制流。

---

## 🎯 使用场景分析

### 场景 1: 调试与人工干预

```dsl
# 自动化流程中需要人工确认
step "用户注册":
    navigate to "https://example.com/register"
    type text user.email into "#email"

    # 💡 等待人工确认邮箱是否正确
    let confirmed = input("请确认邮箱是否正确 (y/n): ")

    if confirmed == "y":
        click "#submit"
    else:
        log error "用户取消注册"
        exit
```

**价值**:
- ✅ 在关键步骤前暂停，让人工检查状态
- ✅ 避免错误数据提交到生产环境
- ✅ 调试时可以手动介入

### 场景 2: 动态参数输入

```dsl
# 运行时输入敏感信息（不硬编码）
step "登录":
    navigate to "https://example.com/login"

    # 💡 从控制台安全输入密码
    let username = input("请输入用户名: ")
    let password = input("请输入密码: ", type=password)  # 密码不回显

    type text username into "#username"
    type text password into "#password"
    click "#login"
```

**价值**:
- ✅ 避免密码硬编码在脚本中
- ✅ 支持多用户测试（每次运行输入不同账号）
- ✅ 提高安全性

### 场景 3: 交互式分支选择

```dsl
# 用户选择执行路径
step "选择测试环境":
    log info "请选择测试环境:"
    log info "  1. 开发环境 (dev)"
    log info "  2. 测试环境 (staging)"
    log info "  3. 生产环境 (prod)"

    let choice = input("请输入选项 (1-3): ")

    if choice == "1":
        let base_url = "https://dev.example.com"
    elif choice == "2":
        let base_url = "https://staging.example.com"
    else:
        let base_url = "https://example.com"

    navigate to base_url
```

**价值**:
- ✅ 一个脚本支持多环境
- ✅ 减少重复代码
- ✅ 交互式配置

### 场景 4: 人工验证码输入

```dsl
# 真实场景：需要人工识别验证码
step "处理验证码":
    navigate to "https://example.com/verify"
    screenshot as "captcha"

    # 💡 人工查看截图并输入验证码
    log info "请查看截图 screenshots/captcha.png"
    let captcha = input("请输入验证码: ")

    type text captcha into "#captcha"
    click "#verify"
```

**价值**:
- ✅ 处理复杂验证码（OCR 无法识别）
- ✅ 结合自动化和人工
- ✅ 实用性强

### 场景 5: 测试数据批量输入

```dsl
# 循环输入测试用户
step "批量创建用户":
    let continue_input = True

    while continue_input:
        let name = input("请输入用户名 (输入 'done' 结束): ")

        if name == "done":
            let continue_input = False
        else:
            let email = input("请输入邮箱: ")

            # 创建用户
            navigate to "https://example.com/users/new"
            type text name into "#name"
            type text email into "#email"
            click "#submit"

            log success "用户 {name} 创建成功"
```

**价值**:
- ✅ 灵活的测试数据输入
- ✅ 无需预先准备数据文件
- ✅ 适合临时测试

---

## 💡 语法设计方案

### 方案 A: 基础输入（推荐）

**语法**:
```dsl
let VAR = input(PROMPT)
let VAR = input(PROMPT, default=DEFAULT_VALUE)
let VAR = input(PROMPT, type=TYPE)
```

**示例**:
```dsl
# 基本输入
let name = input("请输入姓名: ")

# 带默认值
let email = input("请输入邮箱: ", default="test@example.com")

# 指定类型（密码不回显）
let password = input("请输入密码: ", type=password)

# 整数类型（自动验证和转换）
let age = input("请输入年龄: ", type=integer)
```

**参数说明**:
- `PROMPT`: 提示文本（必填）
- `default`: 默认值（可选，按 Enter 使用默认值）
- `type`: 输入类型（可选，支持 `text`, `password`, `integer`, `float`）

**优点**:
- ✅ 语法简洁，符合 Python/JavaScript 习惯
- ✅ 类型安全（支持类型验证）
- ✅ 支持默认值（提高易用性）

**缺点**:
- ❌ 功能相对基础
- ❌ 不支持高级验证（如正则）

### 方案 B: 增强验证（未来扩展）

**语法**:
```dsl
let VAR = input(PROMPT, validate=VALIDATION_FUNC)
let VAR = input(PROMPT, pattern=REGEX)
let VAR = input(PROMPT, choices=[OPTION1, OPTION2, ...])
```

**示例**:
```dsl
# 正则验证
let email = input("请输入邮箱: ", pattern="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")

# 选项验证
let env = input("选择环境: ", choices=["dev", "staging", "prod"])

# 自定义验证（需要函数支持）
let age = input("请输入年龄: ", validate=validate_age)
```

**优点**:
- ✅ 功能强大，支持复杂验证
- ✅ 提高输入质量

**缺点**:
- ❌ 实现复杂度高
- ❌ 需要错误处理机制

### 方案 C: 确认型输入（特化）

**语法**:
```dsl
let BOOL_VAR = confirm(PROMPT)
let CHOICE_VAR = select(PROMPT, options=[...])
```

**示例**:
```dsl
# 确认型（返回 True/False）
let confirmed = confirm("是否继续执行？")

# 选择型（从列表中选择）
let env = select("选择环境: ", options=["dev", "staging", "prod"])
```

**优点**:
- ✅ 语义清晰，专用场景更直观
- ✅ 减少输入错误

**缺点**:
- ❌ 新增多个关键字
- ❌ 增加学习成本

---

## 🏗️ 技术实现分析

### 实现层级

#### 1. 词法分析器 (Lexer)

```python
# 新增 token
class TokenType(Enum):
    INPUT = "INPUT"  # 新增

# lexer.py
def _read_identifier(self):
    if identifier == "input":
        return Token(TokenType.INPUT, "input", ...)
```

#### 2. 语法分析器 (Parser)

```python
# 新增 AST 节点
@dataclass
class InputExpression(Expression):
    """
    Input 表达式 (v5.1)

    从控制台读取用户输入

    语法: input(PROMPT, default=..., type=...)
    """
    prompt: Expression  # 提示文本
    default_value: Optional[Expression] = None
    input_type: str = "text"  # text | password | integer | float
    line: int = 0

# parser.py
def _parse_primary(self):
    if self._match(TokenType.INPUT):
        return self._parse_input_expression()

def _parse_input_expression(self):
    # input(PROMPT, default=..., type=...)
    self._consume(TokenType.LPAREN, "期望 '('")

    # 解析提示文本
    prompt = self._parse_expression()

    # 解析可选参数
    default_value = None
    input_type = "text"

    while self._match(TokenType.COMMA):
        param_name = self._consume(TokenType.IDENTIFIER)
        self._consume(TokenType.EQUALS_SIGN)

        if param_name.value == "default":
            default_value = self._parse_expression()
        elif param_name.value == "type":
            input_type = self._parse_expression().value

    self._consume(TokenType.RPAREN, "期望 ')'")

    return InputExpression(
        prompt=prompt,
        default_value=default_value,
        input_type=input_type,
        line=self.current_line
    )
```

#### 3. 表达式求值器 (Expression Evaluator)

```python
# expression_evaluator.py
def _eval(self, expr):
    if isinstance(expr, InputExpression):
        return self._eval_input(expr)

def _eval_input(self, expr: InputExpression):
    """
    执行 input 表达式，从控制台读取用户输入

    Args:
        expr: InputExpression 节点

    Returns:
        用户输入的值（根据 type 转换类型）
    """
    # 1. 求值提示文本
    prompt = self._eval(expr.prompt)

    # 2. 求值默认值
    default = None
    if expr.default_value:
        default = self._eval(expr.default_value)

    # 3. 检查是否在交互模式
    if not self.interpreter.context.is_interactive:
        # 非交互模式：使用默认值或抛出错误
        if default is not None:
            return default
        else:
            raise ExecutionError(
                line=expr.line,
                statement="input(...)",
                error_type=ExecutionError.RUNTIME_ERROR,
                message="input() 需要交互模式，但当前在自动模式。请提供 default 参数"
            )

    # 4. 从控制台读取输入
    import sys

    # 显示提示（支持默认值提示）
    if default is not None:
        full_prompt = f"{prompt} [默认: {default}] "
    else:
        full_prompt = str(prompt)

    # 读取输入
    if expr.input_type == "password":
        import getpass
        user_input = getpass.getpass(full_prompt)
    else:
        user_input = input(full_prompt)

    # 5. 处理空输入（使用默认值）
    if user_input == "" and default is not None:
        user_input = str(default)

    # 6. 类型转换
    try:
        if expr.input_type == "integer":
            return int(user_input)
        elif expr.input_type == "float":
            return float(user_input)
        else:
            return user_input
    except ValueError as e:
        raise ExecutionError(
            line=expr.line,
            statement=f"input(..., type={expr.input_type})",
            error_type=ExecutionError.TYPE_ERROR,
            message=f"无法将输入 '{user_input}' 转换为 {expr.input_type}: {e}"
        )
```

#### 4. 执行上下文 (Context)

```python
# context.py
class ExecutionContext:
    def __init__(
        self,
        task_id: str,
        ...
        interactive_mode: bool = True  # 新增：是否交互模式
    ):
        self.is_interactive = interactive_mode
        ...

# 提供方法切换模式
def set_interactive_mode(self, enabled: bool):
    """设置交互模式"""
    self.is_interactive = enabled
```

#### 5. CLI 接口

```python
# cli.py
@click.command()
@click.argument('script_path')
@click.option('--non-interactive', is_flag=True, help='非交互模式（CI/CD）')
def run(script_path, non_interactive):
    """运行 DSL 脚本"""

    context = ExecutionContext(
        task_id=str(uuid.uuid4()),
        script_name=Path(script_path).stem,
        interactive_mode=not non_interactive  # 默认交互模式
    )

    interpreter = Interpreter(context)
    interpreter.execute(ast)
```

---

## 🧪 测试策略

### 单元测试

```python
# tests/unit/test_input_expression.py

def test_input_basic(mock_input):
    """测试基本输入"""
    mock_input.return_value = "John"

    script = '''
    let name = input("请输入姓名: ")
    log info name
    '''

    result = execute_script(script, interactive=True)
    assert result.variables["name"] == "John"

def test_input_with_default(mock_input):
    """测试默认值"""
    mock_input.return_value = ""  # 空输入

    script = '''
    let email = input("请输入邮箱: ", default="test@example.com")
    '''

    result = execute_script(script, interactive=True)
    assert result.variables["email"] == "test@example.com"

def test_input_integer_type(mock_input):
    """测试整数类型转换"""
    mock_input.return_value = "25"

    script = '''
    let age = input("请输入年龄: ", type=integer)
    '''

    result = execute_script(script, interactive=True)
    assert result.variables["age"] == 25
    assert isinstance(result.variables["age"], int)

def test_input_non_interactive_with_default():
    """测试非交互模式使用默认值"""
    script = '''
    let env = input("选择环境: ", default="dev")
    '''

    # 非交互模式
    result = execute_script(script, interactive=False)
    assert result.variables["env"] == "dev"

def test_input_non_interactive_no_default():
    """测试非交互模式无默认值抛出错误"""
    script = '''
    let name = input("请输入姓名: ")
    '''

    with pytest.raises(ExecutionError) as exc:
        execute_script(script, interactive=False)

    assert "需要交互模式" in str(exc.value)
```

### 集成测试

```python
# tests/integration/test_input_integration.py

def test_input_in_flow(mock_input):
    """测试在完整流程中的输入"""
    mock_input.side_effect = ["staging", "yes"]

    script = '''
    step "环境选择":
        let env = input("选择环境 (dev/staging/prod): ")
        log info "选择的环境: {env}"

        if env == "staging":
            let base_url = "https://staging.example.com"
        else:
            let base_url = "https://example.com"

        let confirmed = input("确认继续？(yes/no): ")

        if confirmed == "yes":
            log success "继续执行"
        else:
            log error "用户取消"
    '''

    result = execute_script(script, interactive=True)
    assert result.variables["env"] == "staging"
    assert result.variables["confirmed"] == "yes"
```

---

## ⚖️ 优缺点分析

### 优点

#### 1. 极大提升灵活性
- ✅ 支持半自动化流程（自动+人工）
- ✅ 调试时可以暂停并手动介入
- ✅ 动态参数无需硬编码

#### 2. 实用场景丰富
- ✅ 人工验证码识别
- ✅ 敏感信息安全输入（密码）
- ✅ 多环境配置选择
- ✅ 测试数据灵活输入

#### 3. 实现相对简单
- ✅ Python 原生 `input()` 函数
- ✅ 不需要复杂的 UI 框架
- ✅ 与现有架构兼容

#### 4. 向后兼容
- ✅ 不影响现有脚本
- ✅ 可选功能（默认值支持非交互）

### 缺点

#### 1. CI/CD 环境挑战
- ❌ 自动化 CI/CD 无法使用交互输入
- ⚠️ 需要明确区分交互/非交互模式
- ⚠️ 需要提供默认值或环境变量替代

**解决方案**:
```dsl
# 方案 1: 提供默认值
let env = input("选择环境: ", default="dev")

# 方案 2: 从环境变量读取
let env = env("TEST_ENV") or input("选择环境: ", default="dev")
```

#### 2. 测试复杂度增加
- ❌ 需要 mock 用户输入
- ⚠️ 集成测试需要额外设置

**解决方案**: 使用 `unittest.mock` 的 `patch` 功能

#### 3. 超时问题
- ❌ 用户长时间不输入会阻塞
- ⚠️ 需要超时机制

**解决方案**: 添加 `timeout` 参数
```dsl
let name = input("请输入姓名: ", timeout=30)  # 30秒超时
```

#### 4. 多线程/并发冲突
- ❌ 多个脚本并发运行时输入混乱
- ⚠️ 控制台输入是全局的

**解决方案**:
- 交互模式下禁止并发执行
- 或使用任务 ID 前缀区分输入

---

## 🔄 替代方案

### 替代方案 1: 环境变量

**实现**: 通过环境变量传递参数
```dsl
# 不使用 input，而是读取环境变量
let username = env("TEST_USERNAME") or "default_user"
let password = env("TEST_PASSWORD")
```

**优点**:
- ✅ CI/CD 友好
- ✅ 不需要交互

**缺点**:
- ❌ 不支持动态选择
- ❌ 需要预先设置环境变量

### 替代方案 2: 配置文件

**实现**: 从配置文件读取参数
```dsl
# 从 config.json 读取
let config = load_json("config.json")
let username = config.username
```

**优点**:
- ✅ 支持复杂配置
- ✅ CI/CD 友好

**缺点**:
- ❌ 不支持动态输入
- ❌ 需要维护配置文件

### 替代方案 3: 命令行参数

**实现**: CLI 传递参数
```bash
regflow run script.flow --username=admin --password=secret
```

**优点**:
- ✅ CI/CD 友好
- ✅ 灵活

**缺点**:
- ❌ 不支持运行时动态决策
- ❌ 密码明文显示在命令行（安全隐患）

---

## 📊 对比总结

| 方案 | 交互性 | CI/CD | 动态决策 | 安全性 | 实现难度 |
|------|--------|-------|----------|--------|----------|
| **input 语句** | ✅ | ⚠️ (需默认值) | ✅ | ✅ | 中 |
| 环境变量 | ❌ | ✅ | ❌ | ✅ | 低 |
| 配置文件 | ❌ | ✅ | ❌ | ✅ | 低 |
| 命令行参数 | ❌ | ✅ | ❌ | ❌ | 低 |

**结论**: `input` 语句提供了**其他方案无法替代的交互性和动态决策能力**，值得实现。

---

## 🎯 实施建议

### 阶段 1: MVP (v5.1)

**目标**: 实现基础 input 功能

**范围**:
```dsl
# 基础输入
let name = input("提示文本: ")

# 带默认值
let email = input("提示文本: ", default="默认值")

# 密码输入（不回显）
let password = input("密码: ", type=password)
```

**工作量**: 2-3 天

**测试覆盖**:
- ✅ 单元测试（词法、语法、求值）
- ✅ 集成测试（交互模式、非交互模式）
- ✅ 示例脚本

### 阶段 2: 增强 (v5.2)

**目标**: 增加类型验证和超时

**范围**:
```dsl
# 整数类型
let age = input("年龄: ", type=integer)

# 浮点数类型
let price = input("价格: ", type=float)

# 超时机制
let name = input("姓名: ", timeout=30)
```

**工作量**: 1-2 天

### 阶段 3: 高级 (v6.0)

**目标**: 选择型输入和验证

**范围**:
```dsl
# 确认型
let confirmed = confirm("是否继续？")

# 选择型
let env = select("选择环境: ", options=["dev", "staging", "prod"])

# 正则验证
let email = input("邮箱: ", pattern="^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$")
```

**工作量**: 3-4 天

---

## 📝 文档更新计划

### MASTER.md

新增章节: **14. Input & Interaction (v5.1)**

```markdown
## 14. Input & Interaction (v5.1) - 1 feature

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 14.1 | Input Statement | `input(PROMPT, default=..., type=...)` | ✅ | v5.1 | `_parse_input_expression()` | ✅ | 控制台交互输入 |
```

### CHANGELOG.md

新增版本: **v5.1.0 - Input Statement**

```markdown
## [5.1.0] - 2025-12-XX

### ✨ 新增功能

#### 14.1 Input Statement (v5.1)

**语法**:
- `let VAR = input(PROMPT)`
- `let VAR = input(PROMPT, default=DEFAULT)`
- `let VAR = input(PROMPT, type=TYPE)`

**核心特性**:
- ✅ 从控制台读取用户输入
- ✅ 支持默认值（非交互模式友好）
- ✅ 支持类型转换（text, password, integer, float）
- ✅ 密码输入不回显

**使用示例**:
\`\`\`dsl
# 基本输入
let name = input("请输入姓名: ")

# 密码输入
let password = input("请输入密码: ", type=password)

# 带默认值（CI/CD 友好）
let env = input("选择环境: ", default="dev")
\`\`\`
```

---

## ✅ 检查清单

### 设计阶段
- [x] 需求分析完成
- [x] 使用场景明确
- [x] 语法设计完成
- [x] 技术方案评估
- [x] 替代方案对比

### 实现阶段（待执行）
- [ ] Lexer 新增 INPUT token
- [ ] Parser 新增 InputExpression AST 节点
- [ ] Expression Evaluator 实现 _eval_input()
- [ ] Context 新增 interactive_mode 字段
- [ ] CLI 新增 --non-interactive 选项

### 测试阶段（待执行）
- [ ] 单元测试: Lexer
- [ ] 单元测试: Parser
- [ ] 单元测试: Expression Evaluator
- [ ] 集成测试: 交互模式
- [ ] 集成测试: 非交互模式
- [ ] 示例脚本

### 文档阶段（待执行）
- [ ] MASTER.md 更新
- [ ] CHANGELOG.md 新增 v5.1
- [ ] 用户指南更新
- [ ] API 文档更新

---

## 🤔 待讨论问题

### 1. 非交互模式策略

**问题**: CI/CD 环境如何处理 input 语句？

**选项**:
- A. 强制要求所有 input 提供 default（推荐）
- B. 允许从环境变量读取（`env("INPUT_NAME")`）
- C. 抛出错误并跳过

**建议**: **选项 A + B 组合**
```dsl
# 最佳实践
let username = env("TEST_USERNAME") or input("用户名: ", default="admin")
```

### 2. 超时策略

**问题**: 用户长时间不输入如何处理？

**选项**:
- A. 无限等待（默认）
- B. 固定超时（如 60 秒）
- C. 可配置超时 `timeout=30`

**建议**: **选项 C**
```dsl
let name = input("姓名: ", timeout=30, default="未输入")
```

### 3. 验证重试

**问题**: 输入验证失败是否允许重试？

**选项**:
- A. 直接抛出错误（推荐 MVP）
- B. 循环重试直到成功（未来扩展）

**建议**: MVP 使用选项 A，未来扩展选项 B

---

## 📚 参考资料

- Python `input()` 文档: https://docs.python.org/3/library/functions.html#input
- Python `getpass()` 文档: https://docs.python.org/3/library/getpass.html
- Inquirer.py (交互式 CLI): https://github.com/magmax/python-inquirer

---

## 📅 提案时间线

- **2025-11-29**: 提案创建
- **待定**: 团队评审
- **待定**: 实现开始
- **待定**: 发布 v5.1

---

## 👤 提案人声明

本提案基于实际使用场景分析，认为 **input 语句对提升 DSL 实用性有重大价值**。

**核心价值**:
1. ✅ 支持半自动化流程（自动化 + 人工确认）
2. ✅ 调试友好（关键点暂停检查）
3. ✅ 安全性提升（密码不硬编码）
4. ✅ 灵活性增强（动态决策）

**建议**: **批准并在 v5.1 实现 MVP**

---

**提案状态**: 📝 Draft → 等待评审
