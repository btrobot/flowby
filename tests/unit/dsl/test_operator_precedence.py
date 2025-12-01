"""
运算符优先级测试

测试 DSL 表达式解析中的运算符优先级是否正确。

优先级（从高到低）：
1. 括号 ()
2. 成员访问和数组访问 . []
3. 一元运算 + - NOT
4. 乘除 * / %
5. 加减 + -
6. 比较 > < >= <= == != contains matches equals
7. 逻辑与 AND
8. 逻辑或 OR
"""

import pytest
from flowby.lexer import Lexer
from flowby.parser import Parser
from flowby.ast_nodes import (
    BinaryOp,
    UnaryOp,
    Identifier,
    Literal,
    LetStatement,
)


class TestArithmeticPrecedence:
    """测试算术运算符优先级"""

    @pytest.fixture
    def lexer(self):
        return Lexer()

    @pytest.fixture
    def parser(self):
        return Parser()

    def test_multiplication_before_addition(self, lexer, parser):
        """测试乘法优先于加法: a + b * c -> a + (b * c)"""
        # Arrange
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet result = a + b * c"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert - get the last statement (result = a + b * c)
        let_stmt = program.statements[-1]
        assert isinstance(let_stmt, LetStatement)

        # result = BinaryOp(a, '+', BinaryOp(b, '*', c))
        expr = let_stmt.value
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "+"
        assert isinstance(expr.left, Identifier)
        assert expr.left.name == "a"

        # 右侧应该是 b * c
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.operator == "*"
        assert isinstance(expr.right.left, Identifier)
        assert expr.right.left.name == "b"
        assert isinstance(expr.right.right, Identifier)
        assert expr.right.right.name == "c"

    def test_division_before_subtraction(self, lexer, parser):
        """测试除法优先于减法: a - b / c -> a - (b / c)"""
        # Arrange
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet result = a - b / c"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(a, '-', BinaryOp(b, '/', c))
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "-"
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.operator == "/"

    def test_modulo_before_addition(self, lexer, parser):
        """测试取模优先于加法: a + b % c -> a + (b % c)"""
        # Arrange
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet result = a + b % c"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(a, '+', BinaryOp(b, '%', c))
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "+"
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.operator == "%"

    def test_left_associativity_addition(self, lexer, parser):
        """测试加法左结合: a + b + c -> (a + b) + c"""
        # Arrange
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet result = a + b + c"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(BinaryOp(a, '+', b), '+', c)
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "+"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == "+"
        assert isinstance(expr.right, Identifier)
        assert expr.right.name == "c"

    def test_left_associativity_multiplication(self, lexer, parser):
        """测试乘法左结合: a * b * c -> (a * b) * c"""
        # Arrange
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet result = a * b * c"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(BinaryOp(a, '*', b), '*', c)
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "*"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == "*"

    def test_mixed_operators(self, lexer, parser):
        """测试混合运算: a + b * c - d / e -> (a + (b * c)) - (d / e)"""
        # Arrange
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet d = 4\nlet e = 5\nlet result = a + b * c - d / e"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # 最外层应该是减法: (a + b * c) - (d / e)
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "-"

        # 左侧: a + (b * c)
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == "+"
        assert isinstance(expr.left.right, BinaryOp)
        assert expr.left.right.operator == "*"

        # 右侧: d / e
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.operator == "/"


class TestLogicalPrecedence:
    """测试逻辑运算符优先级"""

    @pytest.fixture
    def lexer(self):
        return Lexer()

    @pytest.fixture
    def parser(self):
        return Parser()

    def test_and_before_or(self, lexer, parser):
        """测试 AND 优先于 OR: a AND b OR c -> (a AND b) OR c"""
        # Arrange
        source = "let a = True\nlet b = True\nlet c = True\nlet result = a and b or c"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(BinaryOp(a, 'AND', b), 'OR', c)
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "OR"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == "AND"
        assert isinstance(expr.left.left, Identifier)
        assert expr.left.left.name == "a"
        assert isinstance(expr.left.right, Identifier)
        assert expr.left.right.name == "b"
        assert isinstance(expr.right, Identifier)
        assert expr.right.name == "c"

    def test_and_left_associative(self, lexer, parser):
        """测试 AND 左结合: a AND b AND c -> (a AND b) AND c"""
        # Arrange
        source = "let a = True\nlet b = True\nlet c = True\nlet result = a and b and c"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(BinaryOp(a, 'AND', b), 'AND', c)
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "AND"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == "AND"

    def test_or_left_associative(self, lexer, parser):
        """测试 OR 左结合: a OR b OR c -> (a OR b) OR c"""
        # Arrange
        source = "let a = True\nlet b = True\nlet c = True\nlet result = a or b or c"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(BinaryOp(a, 'OR', b), 'OR', c)
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "OR"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == "OR"

    def test_complex_logical_expression(self, lexer, parser):
        """测试复杂逻辑表达式: a OR b AND c OR d -> (a OR (b AND c)) OR d"""
        # Arrange
        source = "let a = True\nlet b = True\nlet c = True\nlet d = True\nlet result = a or b and c or d"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # 最外层: (a OR (b AND c)) OR d
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "OR"

        # 左侧: a OR (b AND c)
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == "OR"

        # 左侧的右侧: b AND c
        assert isinstance(expr.left.right, BinaryOp)
        assert expr.left.right.operator == "AND"


class TestUnaryPrecedence:
    """测试一元运算符优先级"""

    @pytest.fixture
    def lexer(self):
        return Lexer()

    @pytest.fixture
    def parser(self):
        return Parser()

    def test_not_before_and(self, lexer, parser):
        """测试 NOT 优先于 AND: NOT a AND b -> (NOT a) AND b"""
        # Arrange
        source = "let a = True\nlet b = True\nlet result = not a and b"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(UnaryOp('NOT', a), 'AND', b)
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "AND"
        assert isinstance(expr.left, UnaryOp)
        assert expr.left.operator == "NOT"
        assert isinstance(expr.left.operand, Identifier)
        assert expr.left.operand.name == "a"
        assert isinstance(expr.right, Identifier)
        assert expr.right.name == "b"

    def test_not_before_or(self, lexer, parser):
        """测试 NOT 优先于 OR: NOT a OR b -> (NOT a) OR b"""
        # Arrange
        source = "let a = True\nlet b = True\nlet result = not a or b"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(UnaryOp('NOT', a), 'OR', b)
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "OR"
        assert isinstance(expr.left, UnaryOp)
        assert expr.left.operator == "NOT"

    def test_unary_minus(self, lexer, parser):
        """测试一元负号: -a + b -> (-a) + b"""
        # Arrange
        source = "let a = 1\nlet b = 2\nlet result = -a + b"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(UnaryOp('-', a), '+', b)
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "+"
        assert isinstance(expr.left, UnaryOp)
        assert expr.left.operator == "-"


class TestComparisonPrecedence:
    """测试比较运算符优先级"""

    @pytest.fixture
    def lexer(self):
        return Lexer()

    @pytest.fixture
    def parser(self):
        return Parser()

    def test_arithmetic_before_comparison(self, lexer, parser):
        """测试算术优先于比较: a + b > c - d -> (a + b) > (c - d)"""
        # Arrange
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet d = 4\nlet result = a + b > c - d"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(BinaryOp(a, '+', b), '>', BinaryOp(c, '-', d))
        assert isinstance(expr, BinaryOp)
        assert expr.operator == ">"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == "+"
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.operator == "-"

    def test_comparison_before_logical(self, lexer, parser):
        """测试比较优先于逻辑: a > b AND c < d -> (a > b) AND (c < d)"""
        # Arrange
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet d = 4\nlet result = a > b and c < d"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(BinaryOp(a, '>', b), 'AND', BinaryOp(c, '<', d))
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "AND"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == ">"
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.operator == "<"

    def test_equality_before_logical(self, lexer, parser):
        """测试相等优先于逻辑: a == b OR c != d -> (a == b) OR (c != d)"""
        # Arrange
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet d = 4\nlet result = a == b or c != d"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(BinaryOp(a, '==', b), 'OR', BinaryOp(c, '!=', d))
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "OR"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == "=="
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.operator == "!="


class TestParenthesesPrecedence:
    """测试括号改变优先级"""

    @pytest.fixture
    def lexer(self):
        return Lexer()

    @pytest.fixture
    def parser(self):
        return Parser()

    def test_parentheses_override_multiplication(self, lexer, parser):
        """测试括号优先于乘法: (a + b) * c -> (a + b) * c"""
        # Arrange
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet result = (a + b) * c"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(BinaryOp(a, '+', b), '*', c)
        # 加法在左侧，乘法在外层
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "*"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == "+"
        assert isinstance(expr.right, Identifier)
        assert expr.right.name == "c"

    def test_parentheses_override_and(self, lexer, parser):
        """测试括号优先于 AND: a AND (b OR c) -> a AND (b OR c)"""
        # Arrange
        source = "let a = True\nlet b = True\nlet c = True\nlet result = a and (b or c)"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(a, 'AND', BinaryOp(b, 'OR', c))
        # OR 在右侧，AND 在外层
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "AND"
        assert isinstance(expr.left, Identifier)
        assert expr.left.name == "a"
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.operator == "OR"

    def test_nested_parentheses(self, lexer, parser):
        """测试嵌套括号: (a + (b * c)) - d"""
        # Arrange
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet d = 4\nlet result = (a + (b * c)) - d"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # result = BinaryOp(BinaryOp(a, '+', BinaryOp(b, '*', c)), '-', d)
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "-"
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.operator == "+"
        assert isinstance(expr.left.right, BinaryOp)
        assert expr.left.right.operator == "*"


class TestComplexPrecedence:
    """测试复杂混合优先级场景"""

    @pytest.fixture
    def lexer(self):
        return Lexer()

    @pytest.fixture
    def parser(self):
        return Parser()

    def test_full_precedence_chain(self, lexer, parser):
        """测试完整优先级链: a OR b AND c > d + e * f"""
        # Arrange
        source = "let a = True\nlet b = True\nlet c = 1\nlet d = 2\nlet e = 3\nlet f = 4\nlet result = a or b and c > d + e * f"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # 最外层: OR
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "OR"

        # OR 的右侧: b AND (c > (d + (e * f)))
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.operator == "AND"

        # AND 的右侧: c > (d + (e * f))
        assert isinstance(expr.right.right, BinaryOp)
        assert expr.right.right.operator == ">"

        # 比较的右侧: d + (e * f)
        assert isinstance(expr.right.right.right, BinaryOp)
        assert expr.right.right.right.operator == "+"

        # 加法的右侧: e * f
        assert isinstance(expr.right.right.right.right, BinaryOp)
        assert expr.right.right.right.right.operator == "*"

    def test_unary_with_comparison_and_logical(self, lexer, parser):
        """测试一元、比较和逻辑混合: NOT a > b AND c < d -> (NOT (a > b)) AND (c < d)"""
        # Arrange
        source = "let a = 1\nlet b = 2\nlet c = 3\nlet d = 4\nlet result = not a > b and c < d"

        # Act
        tokens = lexer.tokenize(source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        # 最外层: AND
        assert isinstance(expr, BinaryOp)
        assert expr.operator == "AND"

        # 左侧: NOT (a > b) - NOT 作用于整个比较表达式
        assert isinstance(expr.left, UnaryOp)
        assert expr.left.operator == "NOT"
        assert isinstance(expr.left.operand, BinaryOp)
        assert expr.left.operand.operator == ">"

    @pytest.mark.parametrize(
        "source,expected_outer_op,expected_description",
        [
            ("a + b * c", "+", "乘法优先于加法"),
            ("a and b or c", "OR", "and 优先于 or"),
            ("not a and b", "AND", "not 优先于 and"),
            ("a > b and c", "AND", "比较优先于逻辑"),
            ("(a + b) * c", "*", "括号改变优先级"),
        ],
    )
    def test_precedence_examples(
        self, lexer, parser, source, expected_outer_op, expected_description
    ):
        """参数化测试各种优先级场景"""
        # Arrange - add variable declarations
        full_source = f"let a = 1\nlet b = 2\nlet c = 3\nlet result = {source}"

        # Act
        tokens = lexer.tokenize(full_source)
        program = parser.parse(tokens)

        # Assert
        let_stmt = program.statements[-1]
        expr = let_stmt.value

        assert isinstance(expr, BinaryOp) or isinstance(
            expr, UnaryOp
        ), f"{expected_description}: 应该是运算符节点"

        if isinstance(expr, BinaryOp):
            assert (
                expr.operator == expected_outer_op
            ), f"{expected_description}: 最外层运算符应该是 {expected_outer_op}"
