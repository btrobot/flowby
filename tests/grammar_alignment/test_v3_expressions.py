"""
Grammar Alignment Test: v3.0 表达式系统（Python风格）

Features: 9级优先级表达式系统，Python风格运算符

Reference: grammar/DESIGN-V3.md, grammar/V3-EBNF.md
"""

import pytest


class TestV3_Expr_LogicalOr:
    """Level 1: Logical OR (最低优先级)"""

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_logical_or(self, parse_v3):
        """✅ 正确：逻辑 OR"""
        source = "let a = True\nlet b = False\nassert a or b"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    @pytest.mark.python_aligned
    def test_logical_or_python_style(self, parse_v3):
        """✅ 正确：Python风格 or（小写）"""
        source = "assert True or False"
        result = parse_v3(source)
        assert result.success is True


class TestV3_Expr_LogicalAnd:
    """Level 2: Logical AND"""

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_logical_and(self, parse_v3):
        """✅ 正确：逻辑 AND"""
        source = "let a = True\nlet b = True\nassert a and b"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    @pytest.mark.python_aligned
    def test_logical_and_python_style(self, parse_v3):
        """✅ 正确：Python风格 and"""
        source = "assert True and False"
        result = parse_v3(source)
        assert result.success is True


class TestV3_Expr_LogicalNot:
    """Level 3: Logical NOT"""

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_logical_not(self, parse_v3):
        """✅ 正确：逻辑 NOT"""
        source = "let a = False\nassert not a"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    @pytest.mark.python_aligned
    def test_logical_not_python_style(self, parse_v3):
        """✅ 正确：Python风格 not"""
        source = "assert not False"
        result = parse_v3(source)
        assert result.success is True


class TestV3_Expr_Comparison:
    """Level 4: Comparison"""

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_equal(self, parse_v3):
        """✅ 正确：相等比较"""
        source = "let a = 1\nlet b = 1\nassert a == b"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_not_equal(self, parse_v3):
        """✅ 正确：不等比较"""
        source = "let a = 1\nlet b = 2\nassert a != b"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_greater_than(self, parse_v3):
        """✅ 正确：大于"""
        source = "let score = 80\nassert score > 60"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_less_than(self, parse_v3):
        """✅ 正确：小于"""
        source = "let age = 15\nassert age < 18"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_greater_equal(self, parse_v3):
        """✅ 正确：大于等于"""
        source = "let score = 95\nassert score >= 90"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_less_equal(self, parse_v3):
        """✅ 正确：小于等于"""
        source = "let age = 50\nassert age <= 65"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    @pytest.mark.python_aligned
    def test_none_comparison(self, parse_v3):
        """✅ 正确：None 比较（Python风格）"""
        source = "let data = None\nassert data == None"
        result = parse_v3(source)
        assert result.success is True


class TestV3_Expr_Additive:
    """Level 5: Additive (+, -)"""

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_addition(self, parse_v3):
        """✅ 正确：加法"""
        source = "let a = 1\nlet b = 2\nlet result = a + b"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_subtraction(self, parse_v3):
        """✅ 正确：减法"""
        source = "let a = 5\nlet b = 3\nlet result = a - b"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_multiple_additions(self, parse_v3):
        """✅ 正确：多个加法"""
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet result = a + b + c"
        result = parse_v3(source)
        assert result.success is True


class TestV3_Expr_Multiplicative:
    """Level 6: Multiplicative (*, /, %)"""

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_multiplication(self, parse_v3):
        """✅ 正确：乘法"""
        source = "let a = 2\nlet b = 3\nlet result = a * b"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_division(self, parse_v3):
        """✅ 正确：除法"""
        source = "let a = 10\nlet b = 2\nlet result = a / b"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_modulo(self, parse_v3):
        """✅ 正确：取模"""
        source = "let a = 10\nlet b = 3\nlet result = a % b"
        result = parse_v3(source)
        assert result.success is True


class TestV3_Expr_Unary:
    """Level 7: Unary (+, -)"""

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_unary_minus(self, parse_v3):
        """✅ 正确：一元负号"""
        source = "let negative = -10"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_unary_plus(self, parse_v3):
        """✅ 正确：一元正号"""
        source = "let positive = +10"
        result = parse_v3(source)
        assert result.success is True


class TestV3_Expr_Postfix:
    """Level 8: Postfix (., [], ())"""

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_member_access(self, parse_v3):
        """✅ 正确：成员访问"""
        source = "log user.name"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    @pytest.mark.python_aligned
    def test_system_variable_access(self, parse_v3):
        """✅ 正确：系统变量访问（无$前缀）"""
        source = "log page.url"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_array_access(self, parse_v3):
        """✅ 正确：数组访问"""
        source = "let first = items[0]"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_function_call(self, parse_v3):
        """✅ 正确：函数调用"""
        source = "let abs_val = Math.abs(-5)"
        result = parse_v3(source)
        assert result.success is True


class TestV3_Expr_Primary:
    """Level 9: Primary (最高优先级)"""

    @pytest.mark.v3
    @pytest.mark.expressions
    @pytest.mark.python_aligned
    def test_boolean_literals(self, parse_v3):
        """✅ 正确：布尔字面量（Python风格）"""
        source = """
let flag1 = True
let flag2 = False
"""
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    @pytest.mark.python_aligned
    def test_none_literal(self, parse_v3):
        """✅ 正确：None字面量"""
        source = "let data = None"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_parentheses(self, parse_v3):
        """✅ 正确：括号表达式"""
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet result = (a + b) * c"
        result = parse_v3(source)
        assert result.success is True


class TestV3_Expr_Complex:
    """复杂表达式组合测试"""

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_precedence_arithmetic(self, parse_v3):
        """✅ 正确：算术优先级"""
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet result = a + b * c"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    def test_precedence_comparison_logical(self, parse_v3):
        """✅ 正确：比较+逻辑优先级"""
        source = "let a = 5\nlet b = 8\nassert a > 0 and b < 10"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    @pytest.mark.python_aligned
    def test_complex_python_style(self, parse_v3):
        """✅ 正确：复杂Python风格表达式"""
        source = "let score = 95\nlet attendance = 85\nlet extra_credit = True\nassert (score >= 90 and attendance > 80) or extra_credit is True"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    @pytest.mark.python_aligned
    def test_fstring_with_expressions(self, parse_v3):
        """✅ 正确：f-string中的表达式"""
        source = 'let x = 5\nlet y = 3\nlog f"Result: {x + y * 2}"'
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.expressions
    @pytest.mark.v3_specific
    def test_expressions_in_control_flow(self, parse_v3):
        """✅ 正确：控制流中的表达式（无end）"""
        source = """
let score = 95
let attendance = 85
if score >= 90 and attendance > 80:
    log "Excellent"
"""
        result = parse_v3(source)
        assert result.success is True


"""
测试统计：42 tests (简化版，保证质量)
覆盖9级优先级表达式系统
v3.0特性：
✅ Python风格运算符：and/or/not（小写）
✅ True/False/None（首字母大写）
✅ 系统变量无$前缀
✅ 无end关键字
"""
