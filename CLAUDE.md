# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 项目概述

**Flowby** 是一个 Python 风格的 Web 自动化 DSL（领域特定语言），基于 Playwright 实现浏览器控制。

- **当前版本**: v0.1.0 (语法版本 v5.1)
- **Python**: 3.8 - 3.12
- **核心特性**: 声明式语法、OpenAPI 集成、模块系统、交互式输入

---

## 开发命令

### 环境设置

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 安装 Playwright 浏览器
playwright install chromium
```

### 测试

```bash
# 运行全部测试（推荐）
pytest

# 运行特定测试文件
pytest tests/grammar_alignment/test_v3_01_variables.py

# 运行单个测试
pytest tests/grammar_alignment/test_v3_01_variables.py::test_let_declaration_basic -v

# 带覆盖率
pytest --cov=flowby --cov-report=html

# 查看覆盖率报告
# htmlcov/index.html
```

### 代码检查

```bash
# 格式化代码
black src/

# 代码检查
flake8 src/

# 类型检查
mypy src/
```

### 运行脚本

```bash
# 方式一：使用命令行工具
flowby examples/hello.flow

# 方式二：使用 Python 模块
python -m flowby examples/hello.flow

# 方式三：编程方式
python
>>> from flowby import Lexer, Parser, Interpreter, ExecutionContext
>>> # ... 执行代码
```

---

## 核心架构

### 三阶段解释器模型

```
.flow 源文件
    ↓
[Lexer] 词法分析 (lexer.py)
    ↓ Token 流
[Parser] 语法分析 + 语义检查 (parser.py)
    ↓ AST + 符号表
[Interpreter] 解释执行 (interpreter.py)
    ↓
    ├─ ExpressionEvaluator (表达式求值)
    ├─ ExecutionContext (执行状态)
    ├─ Actions (浏览器操作)
    └─ PlaywrightWrapper (浏览器控制)
```

### 关键设计模式

- **Lexer**: 缩进栈算法（Python 风格缩进 → INDENT/DEDENT tokens）
- **Parser**: 递归下降解析（每种语法对应一个 `_parse_*()` 方法）
- **Interpreter**: 访问者模式（每种节点对应一个 `visit_*()` 方法）
- **SymbolTable**: 作用域栈（支持嵌套作用域）
- **ExpressionEvaluator**: 短路求值（优化 and/or 逻辑运算）

### 关键模块速查

| 模块 | 职责 | 行数 | 关键函数/类 |
|------|------|------|-------------|
| `lexer.py` | 词法分析 | 1200 | `Lexer.tokenize()`, `TokenType` |
| `parser.py` | 语法分析 | 3000 | `Parser.parse()`, `_parse_*()` 方法 |
| `interpreter.py` | 解释执行 | 1500 | `Interpreter.run()`, `visit_*()` 方法 |
| `ast_nodes.py` | AST 节点定义 | 800 | 40+ `*Node` 类 |
| `expression_evaluator.py` | 表达式求值 | 800 | `ExpressionEvaluator.evaluate()` |
| `context.py` | 执行上下文 | 600 | `ExecutionContext` |
| `symbol_table.py` | 符号表 | 400 | `SymbolTableStack` |
| `actions/` | 浏览器动作 | 500 | `execute_*()` 函数 |

---

## v3.0 语法革命性变更

**v3.0 是最重大的语法变革**，采用 Python 风格缩进：

### 核心变化

```python
# ✅ v3.0+ 正确语法（Python 风格）
if user == "admin":
    log "Admin user"
else:
    log "Regular user"

# ❌ v2.0 旧语法（已废弃）
if user == "admin":
    log "Admin user"
end if
```

### 关键语法规则

1. **移除所有 `end` 关键字**: `end if`, `end step`, `end for`, `end while` 等全部移除
2. **采用 4 空格缩进**: 每级缩进必须是 4 空格（或 1 Tab = 4 空格）
3. **布尔值**: `True` / `False` (首字母大写)
4. **空值**: `None` (而非 `null`)
5. **字符串插值**: `f"Hello, {name}!"` (Python f-string 语法)

### 修改现有代码时注意

- **所有控制流块**: `if`, `else`, `for`, `while`, `step`, `when`, `otherwise`, `function`
- **必须使用冒号 + 换行 + 缩进块**
- **不要添加 `end` 关键字**

---

## 实例隔离原则

**CRITICAL**: 项目采用严格的实例隔离架构，确保多任务并发安全。

### 设计原则

1. **无全局状态**: 禁止使用全局变量存储执行状态
2. **每任务独立上下文**: 每个脚本执行创建独立的 `ExecutionContext` 实例
3. **组件独立**: 每个上下文有独立的 `ScreenshotManager`, `DiagnosisManager` 等

### 代码示例

```python
# ✅ 正确：实例隔离
def run_script(script_path: str):
    context = ExecutionContext(
        task_id=generate_uuid(),
        script_name=script_path.stem
    )
    interpreter = Interpreter()
    interpreter.run(ast, context)

# ❌ 错误：全局状态
GLOBAL_VARIABLES = {}  # 不要这样做
GLOBAL_PAGE = None     # 会导致并发问题
```

---

## 测试策略

### 测试分类

1. **语法对齐测试** (`tests/grammar_alignment/`)
   - 验证所有 MASTER.md 中定义的语法特性
   - 1082 个测试用例，全部通过
   - 按语法版本组织: `test_v3_*.py`, `test_v4_*.py`, `test_v5_*.py`

2. **单元测试** (`tests/unit/dsl/`)
   - 测试单个组件功能
   - 覆盖 Lexer, Parser, ExpressionEvaluator, Actions 等

3. **集成测试** (`examples/`)
   - 端到端测试真实场景
   - Web 自动化示例、API 集成示例

### pytest Markers

项目注册了以下测试标记（见 `pyproject.toml`）:

- `@pytest.mark.builtin`: 内置函数/命名空间测试
- `@pytest.mark.error`: 错误处理测试
- `@pytest.mark.execution`: 执行流程测试
- `@pytest.mark.expressions`: 表达式求值测试
- `@pytest.mark.feature`: 特定 DSL 功能测试
- `@pytest.mark.integration`: 集成测试
- `@pytest.mark.v3_specific`: v3.0 语法专用测试
- `@pytest.mark.v31`: v3.1 功能测试
- `@pytest.mark.v40`: v4.0 功能测试

**使用标记时请使用已注册的标记**，避免 pytest 警告。

---

## 添加新特性的标准流程

### 1. 定义语法（如果是新语法）

更新 `grammar/MASTER.md`，遵循现有格式。

### 2. 词法分析

```python
# lexer.py

# 添加 Token 类型
class TokenType(Enum):
    # ... 现有 tokens
    NEW_KEYWORD = auto()

# 添加关键字映射
KEYWORDS = {
    # ... 现有关键字
    "newkeyword": TokenType.NEW_KEYWORD,
}
```

### 3. 定义 AST 节点

```python
# ast_nodes.py

@dataclass
class NewFeatureNode(ASTNode):
    """新特性的 AST 节点"""
    param1: Expression
    param2: List[ASTNode]
    line: int
```

### 4. 语法解析

```python
# parser.py

def _parse_new_feature(self) -> NewFeatureNode:
    """解析新特性语法"""
    self.expect(TokenType.NEW_KEYWORD)
    param1 = self._parse_expression()
    self.expect(TokenType.COLON)
    self.expect(TokenType.NEWLINE)
    self.expect(TokenType.INDENT)
    param2 = self._parse_block()
    self.expect(TokenType.DEDENT)

    return NewFeatureNode(param1, param2, line)

# 在 _parse_statement() 中添加分支
def _parse_statement(self) -> ASTNode:
    if self.match(TokenType.NEW_KEYWORD):
        return self._parse_new_feature()
    # ... 现有分支
```

### 5. 解释执行

```python
# interpreter.py

def visit_NewFeatureNode(self, node: NewFeatureNode):
    """执行新特性节点"""
    value = self.evaluator.evaluate(node.param1)

    # 执行逻辑
    for stmt in node.param2:
        self.visit(stmt)
```

### 6. 添加测试

```python
# tests/grammar_alignment/test_v5_new_feature.py

import pytest
from flowby.lexer import Lexer
from flowby.parser import Parser
from flowby.interpreter import Interpreter
from flowby.context import ExecutionContext

@pytest.mark.v5_specific
@pytest.mark.feature
def test_new_feature_basic():
    """测试新特性的基本功能"""
    source = """
newkeyword condition:
    log "Hello"
    """

    tokens = Lexer().tokenize(source)
    ast = Parser().parse(tokens)
    context = ExecutionContext()
    interpreter = Interpreter()
    interpreter.run(ast, context)

    # 断言预期行为
    assert ...
```

### 7. 更新文档

- `CHANGELOG.md`: 添加变更记录
- `grammar/MASTER.md`: 更新语法规范
- `README.md`: 更新特性列表（如果需要）

---

## 符号表与作用域

### 作用域规则

- **全局作用域**: 顶层定义的变量
- **函数作用域**: 函数内部定义的变量
- **循环作用域**: for/while 循环变量（循环内可见）
- **闭包**: 函数捕获外层作用域变量

### 符号表操作

```python
# 进入新作用域（函数、循环）
context.symbol_table.push_scope()

# 定义变量
context.symbol_table.define(name, symbol)

# 查找变量（向上查找）
symbol = context.symbol_table.lookup(name)

# 退出作用域
context.symbol_table.pop_scope()
```

### 语义检查规则

Parser 在解析时进行以下检查（通过 SymbolTable）：

- **VR-001**: 变量使用前必须声明
- **VR-002**: 常量不能重新赋值
- **VR-003**: 同一作用域不能重复声明
- **VR-004**: 系统变量（page, env）只读

---

## 模块系统（v5.0）

### 两阶段执行

1. **Library Definition Phase**: 解析 library 文件，收集 export 符号
2. **Main Execution Phase**: 处理 import 语句，执行主程序

### 库文件示例

```python
# lib/utils.flow
library utils

function greet(name):
    return f"Hello, {name}!"

export greet
```

### 主文件示例

```python
# main.flow
import {greet} from "utils"

let message = greet("Alice")
log message
```

### 库查找路径（优先级）

1. 当前脚本目录
2. 当前脚本目录/lib/
3. 项目根目录/lib/
4. 用户主目录/.flowby/lib/
5. 系统库目录

---

## 表达式求值

### 运算符优先级（从高到低）

1. `()`, `[]`, `.` - 括号、数组访问、成员访问
2. `not`, `-` (一元) - 逻辑非、负号
3. `*`, `/`, `%` - 乘除模
4. `+`, `-` - 加减
5. `<`, `<=`, `>`, `>=` - 比较
6. `==`, `!=` - 相等性
7. `and` - 逻辑与（短路）
8. `or` - 逻辑或（短路）

### 短路求值

- `and`: 左侧为 False 时不求值右侧
- `or`: 左侧为 True 时不求值右侧

### 类型转换（Truthy/Falsy）

**Falsy 值**: `None`, `False`, `0`, `""`, `[]`, `{}`
**Truthy 值**: 其他所有值

---

## OpenAPI 资源系统

### 声明式资源定义

```python
# DSL 语法
resource petstore:
    spec: "https://petstore3.swagger.io/api/v3/openapi.json"
    auth: {type: "bearer", token: env.API_TOKEN}
    resilience:
        retry: {max_retries: 3, strategy: "exponential"}

# 使用
let pet = petstore.getPetById(petId=123)
log pet.name
```

### 实现流程

1. Parser 解析 `resource` 声明为 `ResourceStatement` 节点
2. Interpreter 执行时加载 OpenAPI spec
3. 自动生成 API 客户端（基于 spec）
4. 注册到 `context.resources`
5. 方法调用通过 `ExpressionEvaluator._eval_method_call()` 执行

---

## 诊断系统

### 分级诊断

- **minimal**: 仅错误（生产环境）
- **basic**: 错误 + 关键操作（默认，日常开发）
- **detailed**: 全量日志 + 性能指标（调试复杂问题）

### 启用详细诊断

```python
step "关键步骤" with diagnosis detailed:
    # 会记录详细的执行日志、性能指标、DOM 快照
    navigate to "https://example.com"
    click "#submit"
```

### 诊断输出位置

```
flowby-output/
├── diagnosis/
│   └── task-{uuid}.json
└── screenshots/
    └── task-{uuid}/
```

---

## 常见问题排查

### 缩进错误

```
错误: LexerError: 缩进量不是 4 的倍数
原因: 使用了 2 空格或 Tab 混用
解决: 统一使用 4 空格缩进
```

### 变量未定义

```
错误: ParserError: 未定义变量 'x'
原因: 变量使用前未声明
解决: 先 let x = ... 再使用
定位: symbol_table.py (VR-001 规则)
```

### 常量重赋值

```
错误: ExecutionError: 不能修改常量 'MAX'
原因: 尝试修改 const 声明的变量
解决: 使用 let 声明可变变量
定位: symbol_table.py (VR-002 规则)
```

### 页面未初始化

```
错误: ExecutionError: 页面未初始化
原因: 直接执行浏览器操作，但未先 navigate
解决: 先 navigate to URL，再执行操作
定位: actions/*.py
```

---

## 关键参考文档

### 单一事实来源

- **`grammar/MASTER.md`**: 完整语法规范（54 个特性）
- **`ARCHITECTURE.md`**: 完整架构文档（2155 行）
- **`QUICK_REFERENCE.md`**: 快速参考手册

### 变更历史

- **`CHANGELOG.md`**: 所有版本变更记录
- **`grammar/CHANGELOG.md`**: 语法变更历史

### 开发指南

- **`CONTRIBUTING.md`**: 贡献指南
- **`pyproject.toml`**: 项目配置（依赖、工具配置）

---

## 代码风格

### Python 规范

- 遵循 PEP 8
- 使用 black 格式化 (line-length=100)
- 使用 flake8 检查
- 使用 type hints（Python 3.8 兼容）

### 命名约定

- **类**: `PascalCase` (例如: `LexerToken`, `ASTNode`)
- **函数/方法**: `snake_case` (例如: `parse_statement`, `get_next_token`)
- **常量**: `UPPER_SNAKE_CASE` (例如: `MAX_DEPTH`, `DEFAULT_TIMEOUT`)
- **私有成员**: `_private_method`

### Docstring 格式

```python
def parse_if_statement(self) -> IfBlock:
    """解析 if 语句。

    语法规则:
        if_statement ::= IF expression COLON NEWLINE
                         INDENT block DEDENT
                         [ELSE COLON NEWLINE INDENT block DEDENT]

    Returns:
        IfBlock: if 语句的 AST 节点

    Raises:
        ParserError: 语法错误时抛出
    """
    ...
```

---

## 性能考虑

### 执行时间分布

```
典型脚本（100 行）执行耗时:
├─ 词法分析:    ~10ms  (1%)
├─ 语法分析:    ~20ms  (2%)
├─ 解释执行:    ~10ms  (1%)
└─ 浏览器操作: ~960ms (96%)  ← 主要瓶颈
```

### 优化建议

- **主要瓶颈在浏览器操作**，DSL 解释开销可忽略
- 优化重点：减少不必要的浏览器等待、并行执行独立任务
- 不要过度优化 Lexer/Parser，可读性优先

---

## 调试技巧

### 查看 Token 流

```python
from flowby import Lexer

tokens = Lexer().tokenize("let x = 10")
for t in tokens:
    print(f"{t.type.name:15} {t.value}")
```

### 查看 AST

```python
from flowby import Lexer, Parser

source = "if True: log 'Hello'"
tokens = Lexer().tokenize(source)
ast = Parser().parse(tokens)

import pprint
pprint.pprint(ast.__dict__)
```

### 启用详细日志

```dsl
step "调试步骤" with diagnosis detailed:
    # 详细诊断报告: flowby-output/diagnosis/task-{uuid}.json
    let x = 10
    log x
```

### 使用 pytest 调试

```bash
# 运行单个测试并显示打印
pytest tests/test_file.py::test_function -v -s

# 失败时进入调试器
pytest tests/test_file.py --pdb
```

---

## 特殊注意事项

### 1. v3.0 语法迁移

**所有修改必须遵循 v3.0 语法**：

- 使用缩进块，不使用 `end` 关键字
- 布尔值: `True`/`False`（不是 `true`/`false`）
- 空值: `None`（不是 `null`）

### 2. 实例隔离

**禁止使用全局状态**：

- 所有执行状态必须在 `ExecutionContext` 中
- 不要使用全局变量存储变量、页面对象等
- 确保多任务并发安全

### 3. 符号表一致性

**Parser 和 Interpreter 共享 SymbolTable**：

- Parser 阶段：语义检查（VR 规则验证）
- Interpreter 阶段：变量查找和作用域管理
- 确保两者使用同一个 `SymbolTableStack` 实例

### 4. 错误处理

**使用明确的错误类型**：

- `LexerError`: 词法错误（非法字符、缩进错误等）
- `ParserError`: 语法错误（语法不匹配、语义违规等）
- `ExecutionError`: 运行时错误（变量未定义、类型错误等）

### 5. 测试覆盖

**新特性必须包含测试**：

- 至少包含基本功能测试
- 包含边界情况测试
- 包含错误处理测试
- 使用合适的 pytest marker

---

## 快速定位代码位置

### 修改词法分析

→ `src/flowby/lexer.py`

### 修改语法解析

→ `src/flowby/parser.py` (添加 `_parse_*()` 方法)

### 修改执行逻辑

→ `src/flowby/interpreter.py` (添加 `visit_*()` 方法)

### 添加内置函数

→ `src/flowby/builtin_functions.py` (添加到 `BUILTIN_FUNCTIONS` 字典)

### 添加命名空间

→ `src/flowby/builtin_namespaces.py` (如 `random.*`, `http.*`)

### 添加浏览器动作

→ `src/flowby/actions/*.py` (navigation, interaction, assertion, wait, screenshot)

### 修改系统变量

→ `src/flowby/system_variables.py` (`page`, `env`, `response`)

---

**版本**: v1.0
**生成时间**: 2025-11-30
**维护**: 与代码库同步更新
