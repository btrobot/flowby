# Flowby 快速参考手册

> 新会话必读 - 5 分钟快速定位关键信息

---

## 🎯 项目定位

**Flowby** = Python 风格的 Web 自动化 DSL
- 基于 Playwright 的浏览器控制
- 声明式语法，类似 Python
- OpenAPI 集成 + 模块系统

---

## 📊 当前状态

```
版本:         v0.1.0
语法版本:     v5.1
测试状态:     1082 passed, 0 failed
Python:       3.8 - 3.12
GitHub:       https://github.com/btrobot/flowby
```

---

## 🗂️ 关键文件定位

### **核心代码** (`src/flowby/`)

```
执行链路:
cli.py → runner.py → interpreter.py → actions/

关键模块:
├─ lexer.py              (词法分析，1200 行)
├─ parser.py             (语法分析，3000 行)
├─ interpreter.py        (解释执行，1500 行)
├─ expression_evaluator.py  (表达式求值，800 行)
├─ context.py            (执行上下文，600 行)
├─ symbol_table.py       (符号表，400 行)
└─ actions/              (浏览器动作，500 行)
```

### **语法文档** (`grammar/`)

```
单一事实来源:
└─ MASTER.md            (完整语法规范，54 个特性)

参考文档:
├─ DSL-SYNTAX-CHEATSHEET.md
├─ MIGRATION-GUIDE-v3.1.md
└─ CHANGELOG.md
```

### **测试代码** (`tests/`)

```
语法对齐测试:  tests/grammar_alignment/
单元测试:      tests/unit/dsl/
集成测试:      examples/
```

---

## 🔧 三大核心组件

### **1. Lexer (词法分析器)**

**作用**: 文本 → Token 流

**核心算法**: 缩进栈（Python 风格）

```python
# 输入
step "测试":
    log "Hello"

# 输出 Tokens
[STEP, STRING, COLON, NEWLINE,
 INDENT, LOG, STRING, NEWLINE, DEDENT]
```

**关键代码**: `src/flowby/lexer.py:tokenize()`

### **2. Parser (语法分析器)**

**作用**: Token 流 → AST

**核心算法**: 递归下降解析

```python
# Token 流
[IF, TRUE, COLON, NEWLINE, INDENT, ...]

# AST
IfBlock(
    condition=Literal(True),
    then_block=[...]
)
```

**关键代码**: `src/flowby/parser.py:parse()`

### **3. Interpreter (解释器)**

**作用**: AST → 执行

**核心模式**: 访问者模式

```python
def visit_IfBlock(self, node: IfBlock):
    if self.evaluate(node.condition):
        self.visit_block(node.then_block)
```

**关键代码**: `src/flowby/interpreter.py:run()`

---

## 🌟 核心特性速查

### **v3.0 革命性变更**

```dsl
# ✅ v3.0 (Python 风格)
if condition:
    log "Yes"

# ❌ v2.0 (已废弃)
if condition:
    log "Yes"
end if
```

**关键变化**:
- ❌ 移除所有 `end` 关键字
- ✅ 采用缩进块（4 空格）
- ✅ `True`/`False`/`None`（首字母大写）

### **v5.1 最新特性**

```dsl
# Input Expression
let name = input("Enter name: ")

# Function Closures
function makeCounter():
    let count = 0
    function increment():
        count = count + 1
        return count
    return increment
```

### **语法特性清单**（54 个）

| 类别 | 特性数 | 关键语法 |
|------|--------|----------|
| **变量** | 3 | `let`, `const`, `=` |
| **控制流** | 7 | `if`, `when`, `for`, `while`, `break`, `continue`, `step` |
| **数据类型** | 8 | Number, String, Boolean, None, List, Dict, f-string |
| **浏览器** | 15 | `navigate`, `click`, `type`, `wait`, `assert`, `screenshot` |
| **高级** | 21 | `resource`, `function`, `library`, `import`, `input()` |

---

## 🐛 常见问题快速定位

### **问题 1: 缩进错误**

```
错误: LexerError: 缩进量不是 4 的倍数
定位: src/flowby/lexer.py (缩进栈算法)
解决: 确保使用 4 空格缩进
```

### **问题 2: 变量未定义**

```
错误: ParserError: 未定义变量 'x'
定位: src/flowby/parser.py + symbol_table.py
解决: 先 let x = ... 再使用
```

### **问题 3: 执行错误**

```
错误: ExecutionError: ...
定位: src/flowby/interpreter.py (visit 方法)
     src/flowby/actions/ (动作执行)
调试: 启用 diagnosis detailed
```

### **问题 4: 表达式错误**

```
错误: ExpressionError: ...
定位: src/flowby/expression_evaluator.py
检查: 运算符优先级、类型转换
```

---

## 🔍 代码定位技巧

### **查找特性实现**

```bash
# 1. 查找关键字处理
rg "class TokenType" src/flowby/lexer.py

# 2. 查找 AST 节点
rg "class.*Node" src/flowby/ast_nodes.py

# 3. 查找解析方法
rg "_parse_" src/flowby/parser.py

# 4. 查找执行方法
rg "visit_" src/flowby/interpreter.py
```

### **追踪执行路径**

```
用户脚本 (.flow)
    ↓
Lexer.tokenize()           (lexer.py:100)
    ↓
Parser.parse()             (parser.py:93)
    ↓
Interpreter.run()          (interpreter.py:150)
    ↓
Interpreter.visit()        (interpreter.py:200)
    ↓
actions.execute_*()        (actions/*.py)
```

### **查找测试用例**

```bash
# 1. 按特性查找
find tests/ -name "*variable*.py"

# 2. 按语法版本查找
find tests/ -name "*v3*.py"

# 3. 查看测试覆盖
pytest tests/grammar_alignment/ -v --collect-only
```

---

## 📐 架构速览

### **执行流程**

```
.flow 文件
    ↓
[Lexer] 词法分析
    ↓ [Tokens]
[Parser] 语法分析 + 语义检查
    ↓ [AST + SymbolTable]
[Interpreter] 解释执行
    ↓
    ├─ ExpressionEvaluator (求值)
    ├─ ExecutionContext (状态)
    ├─ PlaywrightWrapper (浏览器)
    └─ Actions (动作)
        ↓
    [输出] 日志/截图/报告
```

### **关键设计模式**

| 模式 | 位置 | 用途 |
|------|------|------|
| **访问者模式** | `interpreter.py` | 遍历 AST 节点 |
| **策略模式** | `actions/` | 不同动作实现 |
| **工厂模式** | `builtin_namespaces.py` | 命名空间创建 |
| **单例模式** | `Settings` | 全局配置 |

### **数据流**

```
用户变量: ExecutionContext.variables (Dict)
系统变量: SystemVariables (page, env, response)
符号表:   SymbolTableStack (作用域栈)
浏览器:   PlaywrightWrapper.page (Playwright Page)
```

---

## 🧪 测试快速指南

### **运行测试**

```bash
# 全部测试
pytest tests/ -v

# 语法对齐测试
pytest tests/grammar_alignment/ -v

# 单个特性测试
pytest tests/grammar_alignment/test_v3_01_variables.py -v

# 带覆盖率
pytest tests/ --cov=flowby --cov-report=html
```

### **测试结构**

```python
def test_feature():
    # 1. 准备源码
    source = """
    let x = 10
    log x
    """

    # 2. 词法分析
    tokens = Lexer().tokenize(source)

    # 3. 语法分析
    ast = Parser().parse(tokens)

    # 4. 执行
    context = ExecutionContext()
    interpreter = Interpreter()
    interpreter.run(ast, context)

    # 5. 断言
    assert context.variables['x'] == 10
```

---

## 🛠️ 调试技巧

### **查看 Token 流**

```python
from flowby import Lexer

tokens = Lexer().tokenize("let x = 10")
for t in tokens:
    print(f"{t.type.name:15} {t.value}")
```

### **查看 AST**

```python
from flowby import Lexer, Parser

source = "if True: log 'Hello'"
tokens = Lexer().tokenize(source)
ast = Parser().parse(tokens)

# 打印 AST 结构
import pprint
pprint.pprint(ast.__dict__)
```

### **查看符号表**

```python
parser = Parser()
ast = parser.parse(tokens)

# 获取符号表
symbol_table = parser.get_symbol_table_dict()
print(symbol_table)
```

### **启用诊断**

```dsl
step "调试" with diagnosis detailed:
    # 详细日志会保存到 flowby-output/diagnosis/
    let x = 10
    log x
```

---

## 📚 文档索引

| 文档 | 用途 | 路径 |
|------|------|------|
| **ARCHITECTURE.md** | 完整架构文档 | `./ARCHITECTURE.md` |
| **QUICK_REFERENCE.md** | 快速参考（本文档） | `./QUICK_REFERENCE.md` |
| **MASTER.md** | 语法规范 | `./grammar/MASTER.md` |
| **README.md** | 项目介绍 | `./README.md` |
| **CHANGELOG.md** | 变更日志 | `./CHANGELOG.md` |
| **CONTRIBUTING.md** | 贡献指南 | `./CONTRIBUTING.md` |

---

## 🎓 学习路径

### **第一次接触 Flowby**

1. 阅读 `README.md` (5 分钟) - 了解项目
2. 阅读本文档 (5 分钟) - 快速定位
3. 查看 `examples/` (10 分钟) - 实际示例
4. 运行测试 (2 分钟) - 验证环境

### **深入理解架构**

1. 阅读 `ARCHITECTURE.md` (30 分钟) - 完整架构
2. 阅读 `grammar/MASTER.md` (20 分钟) - 语法规范
3. 调试示例脚本 (30 分钟) - 追踪执行
4. 阅读核心代码 (2 小时) - lexer/parser/interpreter

### **贡献代码**

1. 查看 `CONTRIBUTING.md` - 贡献指南
2. 查看 `.github/ISSUE_TEMPLATE/` - Issue 模板
3. 运行 `pytest tests/` - 确保测试通过
4. 遵循代码风格 (black, flake8)

---

## 🚀 开发工作流

### **添加新特性**

```bash
# 1. 创建分支
git checkout -b feature/new-feature

# 2. 修改代码
# - lexer.py (添加 TokenType)
# - parser.py (添加解析方法)
# - interpreter.py (添加执行方法)
# - ast_nodes.py (添加 AST 节点)

# 3. 添加测试
# - tests/grammar_alignment/test_v3_*.py

# 4. 更新文档
# - grammar/MASTER.md
# - CHANGELOG.md

# 5. 运行测试
pytest tests/ -v

# 6. 代码检查
black src/
flake8 src/

# 7. 提交
git add .
git commit -m "feat: add new feature"

# 8. 推送
git push origin feature/new-feature
```

### **修复 Bug**

```bash
# 1. 定位问题
# - 查看错误信息
# - 追踪执行路径
# - 添加断点调试

# 2. 编写失败测试
# - 先写测试复现 bug

# 3. 修复代码
# - 修改相关模块

# 4. 验证测试通过
pytest tests/path/to/test.py -v

# 5. 提交
git commit -m "fix: resolve issue #123"
```

---

## 🔗 快速链接

| 资源 | 链接 |
|------|------|
| **GitHub 仓库** | https://github.com/btrobot/flowby |
| **Issues** | https://github.com/btrobot/flowby/issues |
| **Playwright 文档** | https://playwright.dev/python/ |
| **Python PEP 8** | https://peps.python.org/pep-0008/ |

---

## 💡 关键概念记忆卡片

### **缩进栈**
```
作用: 将 Python 风格缩进转为 INDENT/DEDENT tokens
位置: lexer.py
算法: 栈结构，缩进增加 push，减少 pop
```

### **递归下降解析**
```
作用: 将 Token 流转为 AST
位置: parser.py
特点: 每种语法对应一个解析方法
```

### **访问者模式**
```
作用: 遍历 AST 并执行
位置: interpreter.py
方法: visit_IfBlock, visit_LetStatement 等
```

### **实例隔离**
```
作用: 支持并发执行多个脚本
原则: 无全局状态，每任务独立 ExecutionContext
关键: 线程安全
```

### **短路求值**
```
作用: 优化逻辑运算符求值
位置: expression_evaluator.py
示例: a and b → 若 a 为 False，不求值 b
```

---

## ⚡ 性能要点

```
典型脚本执行时间分布:
├─ 词法分析:   ~10ms  (1%)
├─ 语法分析:   ~20ms  (2%)
├─ 解释执行:   ~10ms  (1%)
└─ 浏览器操作: ~960ms (96%)  ← 主要瓶颈

优化方向:
1. 浏览器操作 (Playwright 优化)
2. 减少不必要的等待
3. 并行执行独立任务
```

---

## 📝 代码风格

```python
# 遵循 PEP 8
# 使用 black 格式化
# 使用 flake8 检查

# 示例
def parse_statement(self) -> ASTNode:
    """
    解析语句

    Returns:
        ASTNode: 解析后的 AST 节点

    Raises:
        ParserError: 语法错误
    """
    if self.match(TokenType.LET):
        return self._parse_let_statement()
    elif self.match(TokenType.IF):
        return self._parse_if()
    # ...
```

---

**📌 提示**: 将本文档添加到书签，新会话时快速查阅！

**版本**: v1.0
**生成时间**: 2025-11-30
**维护**: 与 ARCHITECTURE.md 同步更新
