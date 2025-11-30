# Grammar Alignment Tests

> **目的**: 系统化验证 grammar/MASTER.md 定义的语法与 parser.py 实际实现的一致性

**创建日期**: 2025-11-26
**状态**: Active

---

## 📖 什么是对齐测试？

对齐测试是专门为验证语法文档（grammar/MASTER.md）和实际解析器实现（parser.py）一致性而设计的测试套件。

### 与常规测试的区别

| 维度 | 常规测试 | 对齐测试 |
|------|---------|---------|
| **目标** | 验证功能正确性 | 验证文档-代码一致性 |
| **组织** | 按模块/功能分组 | 按 grammar/MASTER.md 特性ID分组 |
| **覆盖** | 核心功能和边界情况 | 文档中描述的所有细节 |
| **可追溯性** | 与需求关联 | 与 MASTER.md 特性ID 1:1映射 |
| **维护** | 随功能变化 | 随语法版本变化 |

**重要**: 对齐测试不是替代现有测试，而是补充，确保文档化的语法与实现完全一致。

---

## 🗂️ 测试文件组织

### 按特性类别组织

```
tests/grammar_alignment/
├── README.md                      # 本文档
├── conftest.py                    # 共享 fixtures
│
├── test_01_variables.py           # 1.x 变量与赋值 (3个特性)
│   ├─ 1.1 Let Declaration
│   ├─ 1.2 Const Declaration
│   └─ 1.3 Assignment
│
├── test_02_control_flow.py        # 2.x 控制流 (4个特性)
│   ├─ 2.1 Step Block
│   ├─ 2.2 If-Else
│   ├─ 2.3 When-Otherwise
│   └─ 2.4 For-Each Loop
│
├── test_03_navigation.py          # 3.x 导航 (3个特性)
├── test_04_wait.py                # 4.x 等待 (3个特性)
├── test_05_selection.py           # 5.x 选择 (2个特性)
├── test_06_actions.py             # 6.x 动作 (10个特性)
├── test_07_assertions.py          # 7.x 断言 (4个特性)
├── test_08_service_call.py        # 8.x 服务调用 (1个特性)
├── test_09_extraction.py          # 9.x 数据提取 (1个特性)
├── test_10_utilities.py           # 10.x 工具 (2个特性)
│
├── test_expressions.py            # 表达式系统 (9级优先级)
├── test_data_types.py             # 数据类型 (7种)
├── test_system_variables.py       # 系统变量 (5个命名空间)
├── test_builtin_functions.py      # 内置函数 (19个)
└── test_validation_rules.py       # 验证规则 (4条 VR-VAR-*)
```

### 特性ID映射

每个测试类对应 grammar/MASTER.md 中的一个特性：

```python
# Feature 1.1: Let Declaration
class Test1_1_LetDeclaration:
    """Test Let Declaration alignment with grammar/MASTER.md"""
    pass

# Feature 6.10: Hover Action
class Test6_10_HoverAction:
    """Test Hover Action alignment with grammar/MASTER.md"""
    pass
```

---

## ✅ 测试编写规范

### 1. 文件头注释

每个测试文件必须包含：

```python
"""
Grammar Alignment Test: [Category Name]

Tests alignment between grammar/MASTER.md definitions and parser.py implementation.

Features tested:
- [Feature ID] [Feature Name] (v[Version])
- ...

Reference: grammar/MASTER.md #[Section]
"""
```

### 2. 测试类命名

**格式**: `Test{FeatureID}_{FeatureName}`

**规则**:
- 特性ID中的 `.` 替换为 `_`
- 特性名用 PascalCase
- 多词特性名连写

**示例**:
```python
class Test1_1_LetDeclaration:      # Feature 1.1
class Test2_2_IfElse:              # Feature 2.2
class Test6_10_HoverAction:        # Feature 6.10
```

### 3. 测试方法命名

**必需的测试方法**:

```python
def test_basic_syntax(self):
    """Test basic syntax as documented in MASTER.md"""
    # 验证最简单的合法用法
    pass

def test_all_options(self):
    """Test all documented options and modifiers"""
    # 验证所有参数、选项、修饰符
    pass

def test_edge_cases(self):
    """Test edge cases and boundary conditions"""
    # 空值、极值、特殊字符等
    pass

def test_error_cases(self):
    """Test error handling and error messages"""
    # 语法错误、语义错误
    pass

def test_examples_from_docs(self):
    """Test all examples from grammar documentation"""
    # MASTER.md 中的所有示例必须能运行
    pass
```

**可选的测试方法**:
- `test_with_{modifier}()` - 测试特定修饰符
- `test_nested()` - 测试嵌套情况
- `test_scope_behavior()` - 测试作用域行为
- `test_version_specific()` - 测试版本特定行为

### 4. 断言内容

**完整的断言应包括**:

```python
def test_basic_syntax(self):
    """Test basic let declaration"""
    source = 'let x = 10'

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    # 1. 验证 AST 结构
    assert len(ast) == 1
    assert isinstance(ast[0], LetStatement)

    # 2. 验证属性值
    assert ast[0].variable == 'x'

    # 3. 验证初始值
    assert isinstance(ast[0].value, Number)
    assert ast[0].value.value == 10

    # 4. 验证行号信息（如果需要）
    assert ast[0].line == 1
```

### 5. 测试数据组织

**使用参数化测试**:

```python
import pytest

class Test1_1_LetDeclaration:

    @pytest.mark.parametrize("source, var_name, expected_value", [
        ('let x = 10', 'x', 10),
        ('let name = "Alice"', 'name', "Alice"),
        ('let flag = true', 'flag', True),
    ])
    def test_various_types(self, source, var_name, expected_value):
        """Test let declaration with various data types"""
        # ... test implementation
        pass
```

---

## 🔍 发现不一致时的处理

### 情况1: 文档描述有误

**示例**: MASTER.md 说支持某个选项，但实际不支持

**处理步骤**:
1. 标记测试为预期失败:
   ```python
   @pytest.mark.xfail(reason="Doc error: option not implemented, see issue #123")
   def test_undocumented_option(self):
       pass
   ```

2. 创建 Issue 记录问题
3. 决定: 更新文档 或 实现功能
4. 修复后移除 `xfail` 标记

### 情况2: 实现有 Bug

**示例**: 边界情况处理错误

**处理步骤**:
1. 编写失败的测试（TDD）
2. 修复 parser.py 的 bug
3. 验证测试通过
4. 在 grammar/CHANGELOG.md 记录修复

### 情况3: 行为未定义

**示例**: MASTER.md 没有说明某个边界情况

**处理步骤**:
1. 记录当前实现行为
2. 讨论是否合理（Issue）
3. 更新 MASTER.md 明确定义
4. 编写测试固化行为

### 情况4: 版本差异

**示例**: v1.0 和 v2.0 行为不同

**处理步骤**:
1. 分别编写测试并标记版本:
   ```python
   @pytest.mark.version("1.0")
   def test_v1_behavior(self):
       pass

   @pytest.mark.version("2.0")
   def test_v2_behavior(self):
       pass
   ```

2. 在 CHANGELOG.md 中明确记录
3. 考虑兼容性测试

---

## 🚀 运行测试

### 运行所有对齐测试

```bash
# 运行整个对齐测试套件
pytest tests/grammar_alignment/ -v

# 显示详细输出
pytest tests/grammar_alignment/ -vv

# 运行并显示覆盖率
pytest tests/grammar_alignment/ --cov=registration_system.dsl --cov-report=html
```

### 运行特定类别

```bash
# 只测试变量相关
pytest tests/grammar_alignment/test_01_variables.py -v

# 只测试控制流
pytest tests/grammar_alignment/test_02_control_flow.py -v
```

### 运行特定特性

```bash
# 只测试 Feature 1.1
pytest tests/grammar_alignment/test_01_variables.py::Test1_1_LetDeclaration -v
```

### 查看失败的测试

```bash
# 只运行上次失败的测试
pytest tests/grammar_alignment/ --lf

# 先运行失败的，再运行成功的
pytest tests/grammar_alignment/ --ff
```

---

## 📊 进度追踪

### 对齐完成度

使用以下命令查看覆盖率：

```bash
python grammar/tools/check_test_coverage.py
```

**当前进度**: 见 `grammar/ALIGNMENT-STRATEGY.md` 中的进度跟踪矩阵

### 报告

每周更新 `grammar/ALIGNMENT-STRATEGY.md` 中的进度矩阵。

---

## 🎯 质量标准

### 一个特性对齐完成的标准

- [x] 基本语法测试 ✅
- [x] 所有选项和修饰符测试 ✅
- [x] 边界情况测试 ✅
- [x] 错误处理测试 ✅
- [x] 文档示例测试 ✅
- [x] 所有测试通过 ✅
- [x] 代码覆盖率 ≥ 90%

### 整体完成标准

- 所有 49 个特性对齐完成
- 对齐测试覆盖率 = 100%
- 所有测试通过
- 无未解决的不一致问题

---

## 📚 参考资料

### 核心文档
- [grammar/MASTER.md](../../grammar/MASTER.md) - 语法定义（单一真理源）
- [grammar/ALIGNMENT-STRATEGY.md](../../grammar/ALIGNMENT-STRATEGY.md) - 对齐策略
- [grammar/GOVERNANCE.md](../../grammar/GOVERNANCE.md) - 变更流程

### 实现代码
- `src/registration_system/dsl/lexer.py` - 词法分析器
- `src/registration_system/dsl/parser.py` - 语法分析器
- `src/registration_system/dsl/ast_nodes.py` - AST 节点定义

### 现有测试
- `tests/` - 现有的功能测试套件

---

## ❓ FAQ

**Q: 对齐测试和现有测试有什么区别？**
A: 现有测试关注功能正确性，对齐测试关注文档-代码一致性。对齐测试严格按照 MASTER.md 的特性ID组织，具有明确的可追溯性。

**Q: 会不会重复现有测试？**
A: 会有部分重复，但这是必要的。对齐测试的组织方式和目的不同，确保每个文档化的特性都被系统验证。

**Q: 如何知道该写哪些测试？**
A: 打开 grammar/MASTER.md，找到对应的特性ID，测试该特性的：
1. 语法示例
2. 所有参数和选项
3. 说明中提到的行为
4. 可能的边界情况

**Q: 测试失败了怎么办？**
A: 按照"发现不一致时的处理"部分的流程处理，判断是文档错误、实现bug、还是行为未定义。

**Q: 对齐测试需要mock吗？**
A: 通常不需要。对齐测试主要验证 Lexer 和 Parser 层，这些是纯函数式的，不依赖外部服务。

---

**创建日期**: 2025-11-26
**维护者**: Registration System Core Team
**状态**: 🚧 In Progress

**下一步**: 开始阶段1 - 高优先级特性对齐（变量、控制流、表达式、数据类型）
