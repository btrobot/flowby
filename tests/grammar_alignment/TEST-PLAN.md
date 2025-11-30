# DSL v3.0 Grammar Alignment Test Plan

> **基于目录**: `tests/grammar_alignment/`
> **参考文档**: `grammar/DESIGN-V3.md`, `grammar/V3-EBNF.md`, `grammar/V3-EXAMPLES.dsl`
> **目标**: 验证 v3.0 Python化语法的实现与设计文档一致性
> **创建日期**: 2025-11-26
> **状态**: Planning Phase

---

## 🎯 核心策略

### 1. 在现有 grammar_alignment 框架下进行

**重要原则**:
- ✅ 专注于 `grammar_alignment` 目录
- ✅ 使用现有的 `conftest.py` 测试基础设施
- ❌ **不干扰** `tests/dsl/` 下的 v2 测试
- ✅ 为 v3.0 创建独立的测试文件（避免混淆）

### 2. v3.0 测试文件命名规范

**格式**: `test_v3_{category}.py`

```
tests/grammar_alignment/
├── README.md                        # 现有框架文档
├── conftest.py                      # 现有共享 fixtures
│
├── # v2.0 测试（保持不变）
├── test_01_variables.py
├── test_02_control_flow.py
├── ...
│
└── # v3.0 测试（新增）
    ├── conftest_v3.py               # v3 专用 fixtures
    ├── test_v3_00_indentation.py    # ⭐ v3 核心：缩进机制 (150 tests)
    ├── test_v3_01_variables.py      # 变量（Python风格）
    ├── test_v3_02_control_flow.py   # 控制流（无end关键字）
    ├── test_v3_03_navigation.py     # 导航
    ├── test_v3_04_wait.py           # 等待
    ├── test_v3_05_selection.py      # 选择
    ├── test_v3_06_actions.py        # 动作
    ├── test_v3_07_assertions.py     # 断言
    ├── test_v3_08_service_call.py   # 服务调用
    ├── test_v3_09_extraction.py     # 数据提取
    ├── test_v3_10_utilities.py      # 工具
    ├── test_v3_data_types.py        # 数据类型（Python对齐）
    ├── test_v3_expressions.py       # 表达式
    ├── test_v3_system_variables.py  # 系统变量（无$前缀）
    ├── test_v3_builtin_functions.py # 内置函数
    └── test_v3_python_alignment.py  # ⭐ Python对齐验证 (50 tests)
```

---

## 📊 测试数量规划

### v3.0 新增测试清单

| 分类 | v2 测试数 | v3 新增 | v3 总计 | 说明 |
|------|----------|---------|---------|------|
| **0. 缩进机制** | 0 | **150** | 150 | ⭐ v3 核心特性 |
| 1. 变量与赋值 | 53 | 10 | 63 | Python风格验证 |
| 2. 控制流 | 33 | 20 | 53 | 删除end关键字 |
| 3. 导航 | 32 | 5 | 37 | 基本不变 |
| 4. 等待 | 34 | 5 | 39 | 基本不变 |
| 5. 选择 | 27 | 3 | 30 | 基本不变 |
| 6. 动作 | 44 | 5 | 49 | 基本不变 |
| 7. 断言 | 33 | 5 | 38 | 基本不变 |
| 8. 服务调用 | 25 | 3 | 28 | 基本不变 |
| 9. 数据提取 | 24 | 3 | 27 | 基本不变 |
| 10. 工具 | 32 | 10 | 42 | f-string验证 |
| 表达式 | 75 | 10 | 85 | 基本不变 |
| **数据类型** | 65 | **30** | 95 | ⭐ Python对齐 |
| **系统变量** | 38 | **20** | 58 | ⭐ 删除$前缀 |
| 内置函数 | 39 | 5 | 44 | 基本不变 |
| **Python对齐** | 0 | **50** | 50 | ⭐ v3 专属验证 |
| **总计** | **554** | **334** | **888** | |

**v3.0 测试总量**: 888 个测试（而非之前计划的704个）

---

## 🔧 v3.0 测试基础设施

### conftest_v3.py 设计

创建 v3 专用的 fixtures，避免干扰现有 v2 测试：

```python
"""
v3.0 专用测试 fixtures

提供 v3.0 语法解析的测试工具：
- LexerV3 和 ParserV3 的 fixtures
- Python对齐验证工具
- 缩进测试工具
"""

import pytest
from registration_system.dsl.lexer_v3 import LexerV3
from registration_system.dsl.parser_v3 import ParserV3


@pytest.fixture
def parse_v3():
    """
    v3.0 语法解析器 fixture

    用法:
        def test_let_statement(parse_v3):
            ast = parse_v3("let x = 10")
            assert len(ast) == 1
    """
    def _parse(source: str):
        lexer = LexerV3()
        tokens = lexer.tokenize(source)
        parser = ParserV3()
        program = parser.parse(tokens)
        return program.statements
    return _parse


@pytest.fixture
def lexer_v3():
    """v3.0 词法分析器 fixture"""
    def _lexer(source: str):
        return LexerV3(source)
    return _lexer


@pytest.fixture
def parser_v3():
    """v3.0 语法分析器 fixture"""
    def _parser(tokens):
        p = ParserV3()
        return p.parse(tokens)
    return _parser


def assert_indentation_error(source: str, error_contains: str = None):
    """
    断言缩进错误

    Args:
        source: 源代码
        error_contains: 错误信息应包含的字符串
    """
    lexer = LexerV3()
    with pytest.raises(IndentationError) as exc_info:
        lexer.tokenize(source)

    if error_contains:
        assert error_contains in str(exc_info.value)


def assert_python_aligned(source_dsl: str, source_python: str):
    """
    验证 DSL 代码的 Python 对齐度

    检查：
    1. True/False 而非 true/false
    2. None 而非 null
    3. 无 $ 前缀
    4. f-string 显式插值
    """
    # 验证布尔值
    assert 'true' not in source_dsl.lower() or 'True' in source_dsl, \
        "Should use 'True' not 'true'"
    assert 'false' not in source_dsl.lower() or 'False' in source_dsl, \
        "Should use 'False' not 'false'"

    # 验证None
    assert 'null' not in source_dsl, "Should use 'None' not 'null'"

    # 验证无$前缀
    assert '$page' not in source_dsl, "Should use 'page.url' not '$page.url'"
    assert '$env' not in source_dsl, "Should use 'env.API_KEY' not '$env.API_KEY'"

    # 验证f-string
    if '{' in source_dsl and '}' in source_dsl:
        # 如果有插值，应该有 f 前缀
        assert 'f"' in source_dsl or "f'" in source_dsl, \
            "Interpolation requires f-string prefix"


# Pytest markers for v3.0
def pytest_configure(config):
    """为 v3.0 测试配置 markers"""
    config.addinivalue_line(
        "markers", "v3: v3.0 grammar tests"
    )
    config.addinivalue_line(
        "markers", "python_aligned: Python alignment validation tests"
    )
    config.addinivalue_line(
        "markers", "indentation: Indentation mechanism tests"
    )
```

---

## 🔥 核心测试类别详解

### 1. ⭐ 缩进机制测试 (test_v3_00_indentation.py)

**新增 150 个测试** - v3.0 最核心的变更

#### 1.1 基础缩进测试 (30个)

```python
class TestV3_Indentation_Basic:
    """基础缩进解析测试"""

    def test_single_level_indent(self, parse_v3):
        """测试单层缩进"""
        source = """
step "test":
    let x = 1
"""
        ast = parse_v3(source)
        # 验证 step 块正确解析

    def test_multi_level_indent(self, parse_v3):
        """测试多层缩进"""
        source = """
step "outer":
    if x > 0:
        let y = 1
"""
        ast = parse_v3(source)

    def test_dedent_to_same_level(self, parse_v3):
        """测试回退到同级缩进"""
        source = """
step "one":
    let x = 1
step "two":
    let y = 2
"""
        ast = parse_v3(source)
```

#### 1.2 缩进边界测试 (40个)

```python
class TestV3_Indentation_Boundaries:
    """缩进边界条件测试"""

    def test_4_space_standard(self, parse_v3):
        """测试标准 4 空格缩进"""
        source = 'step "test":\n    let x = 1'  # 正好4空格
        ast = parse_v3(source)

    def test_inconsistent_indent_error(self, lexer_v3):
        """测试不一致缩进报错"""
        source = """
step "test":
    let x = 1
  let y = 2
"""  # 第二个 let 只有2空格
        with pytest.raises(IndentationError):
            lexer_v3(source).tokenize()

    def test_indent_jump_error(self, lexer_v3):
        """测试缩进跳跃报错"""
        source = """
step "test":
        let x = 1
"""  # 直接跳到8空格
        with pytest.raises(IndentationError):
            lexer_v3(source).tokenize()
```

#### 1.3 Tab 处理测试 (20个)

```python
class TestV3_Indentation_Tabs:
    """Tab 缩进测试"""

    def test_pure_tabs(self, parse_v3):
        """测试纯 Tab 缩进（转为8空格）"""
        source = 'step "test":\n\tlet x = 1'  # 1个Tab
        ast = parse_v3(source)

    def test_mixed_spaces_tabs_error(self, lexer_v3):
        """测试混合空格Tab报错"""
        source = 'step "test":\n  \tlet x = 1'  # 2空格+1Tab
        with pytest.raises(IndentationError):
            lexer_v3(source).tokenize()
```

#### 1.4 空行与注释处理 (30个)

```python
class TestV3_Indentation_Whitespace:
    """空行和注释与缩进交互测试"""

    def test_empty_lines_in_block(self, parse_v3):
        """测试块内空行"""
        source = """
step "test":
    let x = 1

    let y = 2
"""
        ast = parse_v3(source)

    def test_comments_dont_affect_indent(self, parse_v3):
        """测试注释不影响缩进"""
        source = """
step "test":
# 这是注释
    let x = 1
"""
        ast = parse_v3(source)
```

#### 1.5 错误恢复测试 (30个)

```python
class TestV3_Indentation_Errors:
    """缩进错误消息测试"""

    def test_indentation_error_message_format(self, lexer_v3):
        """测试 IndentationError 消息格式"""
        source = """
step "test":
  let x = 1
"""
        with pytest.raises(IndentationError) as exc_info:
            lexer_v3(source).tokenize()

        # 验证错误消息包含：
        # - 行号
        # - 期望的缩进量
        # - 实际的缩进量
        assert 'line 2' in str(exc_info.value).lower()
        assert 'expected 4' in str(exc_info.value).lower()
```

---

### 2. ⭐ Python 对齐验证测试 (test_v3_python_alignment.py)

**新增 50 个测试** - 验证 v3.0 的 Python 化程度

```python
class TestV3_PythonAlignment_Booleans:
    """布尔字面量 Python 对齐测试"""

    def test_true_capitalized(self, parse_v3):
        """测试 True（首字母大写）"""
        source = "let active = True"
        ast = parse_v3(source)
        assert ast[0].value.value == True

    def test_lowercase_true_error(self, parse_v3):
        """测试 true（小写）报错"""
        source = "let active = true"
        with pytest.raises(SyntaxError):
            parse_v3(source)


class TestV3_PythonAlignment_None:
    """None 字面量 Python 对齐测试"""

    def test_none_capitalized(self, parse_v3):
        """测试 None（首字母大写）"""
        source = "let data = None"
        ast = parse_v3(source)

    def test_null_keyword_error(self, parse_v3):
        """测试 null 关键字报错"""
        source = "let data = null"
        with pytest.raises(SyntaxError):
            parse_v3(source)


class TestV3_PythonAlignment_SystemVariables:
    """系统变量无$前缀 Python 对齐测试"""

    def test_page_url_no_dollar(self, parse_v3):
        """测试 page.url（无$前缀）"""
        source = 'assert page.url == "https://example.com"'
        ast = parse_v3(source)
        # 验证解析为 MemberAccess(Identifier("page"), "url")

    def test_dollar_prefix_error(self, parse_v3):
        """测试 $page.url 报错"""
        source = 'assert $page.url == "test"'
        with pytest.raises(SyntaxError):
            parse_v3(source)


class TestV3_PythonAlignment_FString:
    """f-string Python 对齐测试"""

    def test_fstring_interpolation(self, parse_v3):
        """测试 f-string 插值"""
        source = 'log f"Count: {count}"'
        ast = parse_v3(source)
        # 验证解析为 FStringLiteral

    def test_plain_string_no_interpolation(self, parse_v3):
        """测试普通字符串不插值"""
        source = 'log "Count: {count}"'
        ast = parse_v3(source)
        # 验证解析为 StringLiteral，{count} 是字面量

    def test_auto_interpolation_error(self, parse_v3):
        """测试自动插值已禁用"""
        source = 'log "Count: {count}"'
        ast = parse_v3(source)
        # 验证 {count} 是普通字符串一部分，不是插值


class TestV3_PythonAlignment_BlockComments:
    """块注释 Python 对齐测试"""

    def test_triple_quote_block_comment(self, parse_v3):
        """测试三引号块注释"""
        source = '''
"""
这是块注释
跨越多行
"""
let x = 1
'''
        ast = parse_v3(source)

    def test_c_style_comment_error(self, lexer_v3):
        """测试 C 风格注释报错"""
        source = "/* comment */ let x = 1"
        with pytest.raises(SyntaxError):
            lexer_v3(source).tokenize()


class TestV3_PythonAlignment_Comprehensive:
    """综合 Python 对齐测试"""

    @pytest.mark.parametrize("source,python_equiv", [
        (
            'let active = True',
            'active = True'
        ),
        (
            'let data = None',
            'data = None'
        ),
        (
            'log f"User: {user.name}"',
            'print(f"User: {user.name}")'
        ),
        (
            'assert page.url == "test"',
            'assert page.url == "test"'
        ),
    ])
    def test_python_similarity(self, parse_v3, source, python_equiv):
        """测试 DSL 与 Python 相似度"""
        # 验证 DSL 代码能被解析
        ast = parse_v3(source)
        # 验证语法结构与 Python 等价
```

---

### 3. 控制流测试 (test_v3_02_control_flow.py)

**重点**: 验证删除 `end` 关键字后的行为

```python
class TestV3_2_1_StepBlock:
    """Step 块测试（无 end step）"""

    def test_step_with_indent_only(self, parse_v3):
        """测试只用缩进的 step 块"""
        source = """
step "test":
    let x = 1
    let y = 2
"""
        ast = parse_v3(source)
        # 验证块结束由 DEDENT 决定

    def test_nested_step_blocks(self, parse_v3):
        """测试嵌套 step 块"""
        source = """
step "outer":
    step "inner":
        let x = 1
    let y = 2
"""
        ast = parse_v3(source)


class TestV3_2_2_IfElse:
    """If-Else 块测试（无 end if）"""

    def test_if_without_end(self, parse_v3):
        """测试无 end if 的 if 语句"""
        source = """
if x > 0:
    let y = 1
"""
        ast = parse_v3(source)

    def test_end_if_keyword_error(self, parse_v3):
        """测试 end if 关键字报错"""
        source = """
if x > 0:
    let y = 1
end if
"""
        with pytest.raises(SyntaxError):
            parse_v3(source)
```

---

## 📅 测试实施时间表

### Phase 1: 核心机制测试 (Week 1-2)

**优先级**: ⭐⭐⭐⭐⭐

| 测试文件 | 测试数 | 工作量 | 负责人 |
|---------|-------|--------|--------|
| conftest_v3.py | - | 1天 | - |
| test_v3_00_indentation.py | 150 | 3天 | - |
| test_v3_python_alignment.py | 50 | 2天 | - |

### Phase 2: 控制流与数据类型 (Week 3-4)

**优先级**: ⭐⭐⭐⭐

| 测试文件 | 测试数 | 工作量 |
|---------|-------|--------|
| test_v3_01_variables.py | 63 | 1天 |
| test_v3_02_control_flow.py | 53 | 2天 |
| test_v3_data_types.py | 95 | 2天 |
| test_v3_system_variables.py | 58 | 1.5天 |

### Phase 3: 语句与表达式 (Week 5-6)

**优先级**: ⭐⭐⭐

| 测试文件 | 测试数 | 工作量 |
|---------|-------|--------|
| test_v3_03_navigation.py | 37 | 1天 |
| test_v3_04_wait.py | 39 | 1天 |
| test_v3_05_selection.py | 30 | 1天 |
| test_v3_06_actions.py | 49 | 1.5天 |
| test_v3_07_assertions.py | 38 | 1天 |
| test_v3_expressions.py | 85 | 1.5天 |

### Phase 4: 其他特性 (Week 7-8)

**优先级**: ⭐⭐

| 测试文件 | 测试数 | 工作量 |
|---------|-------|--------|
| test_v3_08_service_call.py | 28 | 0.5天 |
| test_v3_09_extraction.py | 27 | 0.5天 |
| test_v3_10_utilities.py | 42 | 1天 |
| test_v3_builtin_functions.py | 44 | 1天 |

**总工作量**: 约 20 工作日

---

## 🎯 成功标准

### 单个测试文件完成标准

- [ ] 所有 v3.0 特性都有对应测试
- [ ] 所有测试通过
- [ ] Python 对齐验证通过
- [ ] 缩进机制测试通过
- [ ] 代码覆盖率 ≥ 90%

### 整体完成标准

- [ ] 888 个 v3.0 测试全部编写完成
- [ ] 所有测试通过（100%）
- [ ] conftest_v3.py 提供完整的测试工具
- [ ] 6 个 Python 对齐关键点全部验证
- [ ] 缩进机制 150 个边界情况全覆盖

---

## 📝 下一步行动

### 立即执行（本周）

1. ✅ 创建 `V3-TEST-PLAN.md`（本文档）
2. ⏭️ 创建 `conftest_v3.py` - v3.0 测试基础设施
3. ⏭️ 创建 `test_v3_00_indentation.py` - 缩进机制测试框架
4. ⏭️ 编写前 30 个缩进基础测试

### 本周目标

- 完成 v3.0 测试基础设施（conftest_v3.py）
- 完成缩进机制测试框架（150 个测试的结构）
- 完成前 50 个核心测试（缩进基础 + Python 对齐）

---

**创建日期**: 2025-11-26
**维护者**: DSL v3.0 Core Team
**参考**: `grammar/V3-REFACTOR-PLAN.md`, `grammar/DESIGN-V3.md`
