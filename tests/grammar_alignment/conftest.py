"""
DSL v3.0 测试 Fixtures

专注于外部语法特性验证：
- 代码能否被正确解析
- 错误提示是否清晰
- Python 对齐度验证
"""

import pytest


# ============================================================================
# v3.0 实现状态
# ============================================================================
# PHASE 2 (Lexer V3): ✅ 已实现
# PHASE 3 (Parser V3): ✅ 已实现


@pytest.fixture
def parse():
    """
    通用语法解析器（返回 AST 语句列表）

    用法:
        def test_variable(parse):
            ast = parse("let x = 10")
            assert len(ast) == 1
            assert isinstance(ast[0], LetStatement)
    """
    from flowby.lexer import Lexer
    from flowby.parser import Parser

    def _parse(code: str):
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)
        return program.statements

    return _parse


@pytest.fixture
def parse_v3():
    """
    v3.0 语法解析器（完整 Lexer + Parser 流程）

    用法:
        def test_variable(parse_v3):
            # 验证代码能被完整解析
            result = parse_v3("let x = 10")
            assert result.success is True
            assert result.ast is not None

            # 验证错误提示
            result = parse_v3("let x = ")
            assert result.success is False
            assert "error" in result.error.lower()
    """
    from flowby.lexer import Lexer
    from flowby.parser import Parser

    class ParseResult:
        """完整的解析结果（Lexer + Parser）"""

        def __init__(self, success: bool, tokens=None, ast=None, error=None):
            self.success = success
            self.tokens = tokens
            self.ast = ast
            self.error = error

    def _parse(code: str) -> ParseResult:
        try:
            # Step 1: 词法分析
            lexer = Lexer()
            tokens = lexer.tokenize(code)

            # Step 2: 语法分析
            parser = Parser()
            ast = parser.parse(tokens)

            return ParseResult(success=True, tokens=tokens, ast=ast)
        except Exception as e:
            return ParseResult(success=False, error=str(e))

    return _parse


@pytest.fixture
def can_parse_v3():
    """
    快速检查代码是否能被解析（完整 Lexer + Parser 流程）

    用法:
        def test_syntax(can_parse_v3):
            # 验证合法语法
            assert can_parse_v3('let x = 10') is True

            # 验证非法语法
            assert can_parse_v3('let x = ') is False
    """
    from flowby.lexer import Lexer
    from flowby.parser import Parser

    def _can_parse(code: str) -> bool:
        try:
            # Step 1: 词法分析
            lexer = Lexer()
            tokens = lexer.tokenize(code)

            # Step 2: 语法分析
            parser = Parser()
            parser.parse(tokens)

            return True
        except Exception:
            return False

    return _can_parse


# ============================================================================
# Python 对齐验证工具
# ============================================================================


def check_python_alignment(source_code: str):
    """
    检查代码的 Python 对齐度

    验证点：
    1. 使用 True/False（不是 true/false）
    2. 使用 None（不是 null）
    3. 无 $ 前缀（page.url 不是 $page.url）
    4. f-string 显式（f"text {x}" 不是 "text {x}"）
    5. 无 end 关键字（纯缩进）
    6. 三引号块注释（\"\"\" \"\"\" 不是 /* */）

    返回:
        dict: {
            'aligned': bool,  # 是否对齐
            'issues': list    # 问题列表
        }
    """
    issues = []

    # 1. 检查布尔值（不区分大小写的检查）
    lower_code = source_code.lower()
    if "true" in lower_code and "True" not in source_code:
        issues.append("应使用 'True' 而非 'true'（Python 风格）")
    if "false" in lower_code and "False" not in source_code:
        issues.append("应使用 'False' 而非 'false'（Python 风格）")

    # 2. 检查 None
    if "null" in source_code:
        issues.append("应使用 'None' 而非 'null'（Python 风格）")

    # 3. 检查 $ 前缀
    if (
        "$page" in source_code
        or "$env" in source_code
        or "$browser" in source_code
        or "$context" in source_code
        or "$config" in source_code
    ):
        issues.append("系统变量不应使用 $ 前缀（应为 page.url 而非 $page.url）")

    # 4. 检查 f-string（如果有插值）
    # 简单启发式：如果有 {var} 模式但无 f" 前缀
    import re

    if re.search(r'\"[^"]*\{[^}]+\}[^"]*\"', source_code):
        if not re.search(r"f\"", source_code):
            issues.append('字符串插值应使用 f-string（f"text {x}"）')

    # 5. 检查 end 关键字
    if re.search(r"\bend\s+(if|step|when|for)\b", source_code):
        issues.append("v3.0 不使用 'end' 关键字，应使用纯缩进")

    # 6. 检查块注释
    if "/*" in source_code or "*/" in source_code:
        issues.append('应使用三引号块注释 """ """ 而非 /* */')

    return {"aligned": len(issues) == 0, "issues": issues}


@pytest.fixture
def assert_python_aligned():
    """
    断言代码符合 Python 对齐规范

    用法:
        def test_alignment(assert_python_aligned):
            # 应通过
            assert_python_aligned('let x = True')

            # 应失败
            assert_python_aligned('let x = true')  # 报错：应使用 True
    """

    def _assert(source_code: str):
        result = check_python_alignment(source_code)
        if not result["aligned"]:
            issues_str = "\n  - ".join(result["issues"])
            pytest.fail(f"Python 对齐问题:\n  - {issues_str}")

    return _assert


# ============================================================================
# 缩进验证工具
# ============================================================================


def check_indentation(source_code: str):
    """
    检查缩进一致性

    验证点：
    1. 缩进使用 4 空格
    2. 不混合空格和 Tab
    3. 同级语句缩进相同

    返回:
        dict: {
            'valid': bool,
            'errors': list
        }
    """
    errors = []
    lines = source_code.split("\n")

    for i, line in enumerate(lines, 1):
        if not line.strip():  # 跳过空行
            continue

        # 检查混合空格和 Tab
        if (
            " " in line[: len(line) - len(line.lstrip())]
            and "\t" in line[: len(line) - len(line.lstrip())]
        ):
            errors.append(f"第 {i} 行：混合使用空格和 Tab")

        # 检查缩进是否为 4 的倍数
        indent = len(line) - len(line.lstrip())
        if indent % 4 != 0 and line.lstrip():  # 非空行
            errors.append(f"第 {i} 行：缩进 {indent} 不是 4 的倍数")

    return {"valid": len(errors) == 0, "errors": errors}


@pytest.fixture
def assert_valid_indentation():
    """
        断言缩进有效

        用法:
            def test_indent(assert_valid_indentation):
                source = '''
    step "test":
        let x = 1
    '''
                assert_valid_indentation(source)
    """

    def _assert(source_code: str):
        result = check_indentation(source_code)
        if not result["valid"]:
            errors_str = "\n  - ".join(result["errors"])
            pytest.fail(f"缩进错误:\n  - {errors_str}")

    return _assert


# ============================================================================
# 测试标记
# ============================================================================


def pytest_configure(config):
    """配置 v3.0 测试标记"""
    config.addinivalue_line("markers", "v3: DSL v3.0 语法测试")
    config.addinivalue_line("markers", "python_aligned: Python 对齐验证测试")
    config.addinivalue_line("markers", "indentation: 缩进机制测试")
    config.addinivalue_line("markers", "syntax: 外部语法特性测试")
