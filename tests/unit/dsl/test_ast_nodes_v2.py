"""
AST Nodes v2.0 测试

验证所有 v2.0 新添加的 AST 节点定义正确，包括：
1. 变量语句节点 (LetStatement, ConstStatement, Assignment)
2. 表达式节点 (Expression, BinaryOp, UnaryOp, Literal, Identifier)
3. 系统变量 (SystemVariable)
4. 访问节点 (MemberAccess, ArrayAccess)
5. 字符串插值 (StringInterpolation)
6. 循环节点 (EachLoop)
7. 更新的节点 (IfBlock, LogStatement)
"""

import pytest
from registration_system.dsl.ast_nodes import (
    # v2.0 变量语句
    LetStatement,
    ConstStatement,
    Assignment,
    # v2.0 表达式节点
    Expression,
    BinaryOp,
    UnaryOp,
    Literal,
    Identifier,
    SystemVariable,
    MemberAccess,
    ArrayAccess,
    StringInterpolation,
    # v2.0 循环
    EachLoop,
    # 更新的节点
    IfBlock,
    LogStatement,
    ExtractStatement,
)


class TestVariableStatements:
    """测试变量定义语句节点"""

    def test_let_statement_creation(self):
        """测试 LetStatement 创建"""
        # Arrange & Act
        let_stmt = LetStatement(name="age", value=Literal(value=25, line=1), line=1)

        # Assert
        assert let_stmt.name == "age", "变量名应该是 age"
        assert isinstance(let_stmt.value, Literal), "值应该是 Literal 节点"
        assert let_stmt.line == 1, "行号应该是 1"

    def test_let_statement_with_expression(self):
        """测试 LetStatement 使用表达式"""
        # Arrange & Act
        let_stmt = LetStatement(
            name="result",
            value=BinaryOp(
                left=Literal(value=10, line=1),
                operator="+",
                right=Literal(value=20, line=1),
                line=1,
            ),
            line=1,
        )

        # Assert
        assert let_stmt.name == "result"
        assert isinstance(let_stmt.value, BinaryOp), "值应该是 BinaryOp 表达式"

    def test_const_statement_creation(self):
        """测试 ConstStatement 创建"""
        # Arrange & Act
        const_stmt = ConstStatement(name="MAX", value=Literal(value=100, line=2), line=2)

        # Assert
        assert const_stmt.name == "MAX", "常量名应该是 MAX"
        assert isinstance(const_stmt.value, Literal), "值应该是 Literal 节点"
        assert const_stmt.line == 2, "行号应该是 2"

    def test_assignment_statement_creation(self):
        """测试 Assignment 创建"""
        # Arrange & Act
        assign = Assignment(
            name="counter",
            value=BinaryOp(
                left=Identifier(name="counter", line=3),
                operator="+",
                right=Literal(value=1, line=3),
                line=3,
            ),
            line=3,
        )

        # Assert
        assert assign.name == "counter", "变量名应该是 counter"
        assert isinstance(assign.value, BinaryOp), "值应该是 BinaryOp 表达式"
        assert assign.line == 3, "行号应该是 3"

    def test_assignment_with_identifier(self):
        """测试 Assignment 使用标识符"""
        # Arrange & Act
        assign = Assignment(name="x", value=Identifier(name="y", line=1), line=1)

        # Assert
        assert assign.name == "x"
        assert isinstance(assign.value, Identifier)
        assert assign.value.name == "y"


class TestLiteralNode:
    """测试字面量节点"""

    @pytest.mark.parametrize(
        "value,expected_type",
        [
            ("hello", str),
            (42, int),
            (3.14, float),
            (True, bool),
            (None, type(None)),
        ],
    )
    def test_literal_with_various_types(self, value, expected_type):
        """测试各种类型的字面量"""
        # Arrange & Act
        lit = Literal(value=value, line=1)

        # Assert
        assert lit.value == value, f"值应该是 {value}"
        assert isinstance(lit.value, expected_type), f"类型应该是 {expected_type}"
        assert lit.line == 1, "行号应该是 1"

    def test_string_literal(self):
        """测试字符串字面量"""
        # Arrange & Act
        lit = Literal(value="hello world", line=1)

        # Assert
        assert lit.value == "hello world"
        assert isinstance(lit.value, str)

    def test_numeric_literal(self):
        """测试数字字面量"""
        # Arrange & Act
        lit = Literal(value=42, line=1)

        # Assert
        assert lit.value == 42
        assert isinstance(lit.value, int)


class TestIdentifierNode:
    """测试标识符节点"""

    def test_identifier_creation(self):
        """测试 Identifier 创建"""
        # Arrange & Act
        ident = Identifier(name="username", line=1)

        # Assert
        assert ident.name == "username", "标识符名称应该是 username"
        assert ident.line == 1, "行号应该是 1"

    @pytest.mark.parametrize(
        "name",
        [
            "x",
            "counter",
            "user_name",
            "MAX_VALUE",
            "age123",
        ],
    )
    def test_identifier_with_various_names(self, name):
        """测试各种标识符名称"""
        # Arrange & Act
        ident = Identifier(name=name, line=1)

        # Assert
        assert ident.name == name, f"标识符应该是 {name}"


class TestSystemVariableNode:
    """测试系统变量节点"""

    @pytest.mark.parametrize(
        "path,description",
        [
            ("context.task_id", "任务ID"),
            ("page.url", "页面URL"),
            ("page.title", "页面标题"),
            ("element.text", "元素文本"),
            ("browser.name", "浏览器名称"),
        ],
    )
    def test_system_variable_paths(self, path, description):
        """测试各种系统变量路径"""
        # Arrange & Act
        sys_var = SystemVariable(path=path, line=1)

        # Assert
        assert sys_var.path == path, f"路径应该是 {path} ({description})"
        assert sys_var.line == 1

    def test_system_variable_creation(self):
        """测试 SystemVariable 创建"""
        # Arrange & Act
        sys_var = SystemVariable(path="context.task_id", line=1)

        # Assert
        assert sys_var.path == "context.task_id"
        assert sys_var.line == 1


class TestBinaryOpNode:
    """测试二元运算符节点"""

    @pytest.mark.parametrize(
        "operator,description",
        [
            ("+", "加法"),
            ("-", "减法"),
            ("*", "乘法"),
            ("/", "除法"),
            ("%", "取模"),
            (">", "大于"),
            ("<", "小于"),
            (">=", "大于等于"),
            ("<=", "小于等于"),
            ("==", "等于"),
            ("!=", "不等于"),
            ("AND", "逻辑与"),
            ("OR", "逻辑或"),
            ("contains", "包含"),
        ],
    )
    def test_binary_operators(self, operator, description):
        """测试各种二元运算符"""
        # Arrange & Act
        bin_op = BinaryOp(
            left=Identifier(name="a", line=1),
            operator=operator,
            right=Identifier(name="b", line=1),
            line=1,
        )

        # Assert
        assert bin_op.operator == operator, f"运算符应该是 {operator} ({description})"
        assert isinstance(bin_op.left, Identifier)
        assert isinstance(bin_op.right, Identifier)

    def test_binary_op_comparison(self):
        """测试比较运算"""
        # Arrange & Act
        bin_op = BinaryOp(
            left=Identifier(name="age", line=1),
            operator=">",
            right=Literal(value=18, line=1),
            line=1,
        )

        # Assert
        assert bin_op.operator == ">"
        assert isinstance(bin_op.left, Identifier)
        assert isinstance(bin_op.right, Literal)
        assert bin_op.left.name == "age"
        assert bin_op.right.value == 18

    def test_binary_op_arithmetic(self):
        """测试算术运算"""
        # Arrange & Act
        bin_op = BinaryOp(
            left=Literal(value=10, line=1), operator="+", right=Literal(value=20, line=1), line=1
        )

        # Assert
        assert bin_op.operator == "+"
        assert bin_op.left.value == 10
        assert bin_op.right.value == 20


class TestUnaryOpNode:
    """测试一元运算符节点"""

    @pytest.mark.parametrize(
        "operator",
        [
            "NOT",
            "-",
            "+",
        ],
    )
    def test_unary_operators(self, operator):
        """测试各种一元运算符"""
        # Arrange & Act
        unary = UnaryOp(operator=operator, operand=Identifier(name="flag", line=1), line=1)

        # Assert
        assert unary.operator == operator, f"运算符应该是 {operator}"
        assert isinstance(unary.operand, Identifier)

    def test_unary_not_operator(self):
        """测试 NOT 运算符"""
        # Arrange & Act
        unary = UnaryOp(operator="NOT", operand=Identifier(name="flag", line=1), line=1)

        # Assert
        assert unary.operator == "NOT"
        assert unary.operand.name == "flag"

    def test_unary_negation(self):
        """测试负号运算符"""
        # Arrange & Act
        unary = UnaryOp(operator="-", operand=Literal(value=42, line=1), line=1)

        # Assert
        assert unary.operator == "-"
        assert isinstance(unary.operand, Literal)
        assert unary.operand.value == 42


class TestMemberAccessNode:
    """测试成员访问节点"""

    def test_member_access_creation(self):
        """测试 MemberAccess 创建"""
        # Arrange & Act
        member = MemberAccess(object=Identifier(name="user", line=1), property="email", line=1)

        # Assert
        assert member.property == "email", "属性名应该是 email"
        assert isinstance(member.object, Identifier), "对象应该是 Identifier"
        assert member.object.name == "user"

    @pytest.mark.parametrize(
        "object_name,property",
        [
            ("user", "email"),
            ("user", "name"),
            ("config", "timeout"),
            ("page", "url"),
        ],
    )
    def test_various_member_accesses(self, object_name, property):
        """测试各种成员访问"""
        # Arrange & Act
        member = MemberAccess(
            object=Identifier(name=object_name, line=1), property=property, line=1
        )

        # Assert
        assert member.object.name == object_name
        assert member.property == property


class TestArrayAccessNode:
    """测试数组访问节点"""

    def test_array_access_with_literal_index(self):
        """测试使用字面量索引的数组访问"""
        # Arrange & Act
        array = ArrayAccess(
            array=Identifier(name="items", line=1), index=Literal(value=0, line=1), line=1
        )

        # Assert
        assert isinstance(array.array, Identifier), "数组应该是 Identifier"
        assert isinstance(array.index, Literal), "索引应该是 Literal"
        assert array.array.name == "items"
        assert array.index.value == 0

    def test_array_access_with_identifier_index(self):
        """测试使用标识符索引的数组访问"""
        # Arrange & Act
        array = ArrayAccess(
            array=Identifier(name="items", line=1), index=Identifier(name="i", line=1), line=1
        )

        # Assert
        assert isinstance(array.index, Identifier)
        assert array.index.name == "i"


class TestStringInterpolationNode:
    """测试字符串插值节点"""

    def test_simple_interpolation(self):
        """测试简单插值"""
        # Arrange & Act
        interp = StringInterpolation(
            parts=["Hello ", Identifier(name="username", line=1), "!"], line=1
        )

        # Assert
        assert len(interp.parts) == 3, "应该有 3 个部分"
        assert interp.parts[0] == "Hello ", "第一部分应该是字符串"
        assert isinstance(interp.parts[1], Identifier), "第二部分应该是 Identifier"
        assert interp.parts[2] == "!", "第三部分应该是字符串"

    def test_multiple_variable_interpolation(self):
        """测试多个变量插值"""
        # Arrange & Act
        interp = StringInterpolation(
            parts=[
                "User: ",
                Identifier(name="username", line=1),
                ", Age: ",
                Identifier(name="age", line=1),
            ],
            line=1,
        )

        # Assert
        assert len(interp.parts) == 4, "应该有 4 个部分"
        assert isinstance(interp.parts[1], Identifier)
        assert isinstance(interp.parts[3], Identifier)
        assert interp.parts[1].name == "username"
        assert interp.parts[3].name == "age"

    def test_interpolation_with_expression(self):
        """测试包含表达式的插值"""
        # Arrange & Act
        interp = StringInterpolation(
            parts=[
                "Result: ",
                BinaryOp(
                    left=Identifier(name="a", line=1),
                    operator="+",
                    right=Identifier(name="b", line=1),
                    line=1,
                ),
            ],
            line=1,
        )

        # Assert
        assert len(interp.parts) == 2
        assert isinstance(interp.parts[1], BinaryOp)


class TestEachLoopNode:
    """测试 EachLoop 循环节点"""

    def test_each_loop_creation(self):
        """测试 EachLoop 创建"""
        # Arrange & Act
        each_loop = EachLoop(
            variable_names=["item"],  # v4.0: 使用 variable_names（列表）
            iterable=Identifier(name="items", line=1),
            statements=[
                LogStatement(
                    message=StringInterpolation(
                        parts=["Item: ", Identifier(name="item", line=2)], line=2
                    ),
                    level="info",
                    line=2,
                )
            ],
            line=1,
        )

        # Assert
        assert each_loop.variable_name == "item", "循环变量应该是 item（向后兼容属性）"
        assert each_loop.variable_names == ["item"], "variable_names 应该是 ['item']"
        assert isinstance(each_loop.iterable, Identifier), "可迭代对象应该是 Identifier"
        assert len(each_loop.statements) == 1, "应该有 1 条语句"
        assert isinstance(each_loop.statements[0], LogStatement)

    def test_each_loop_with_multiple_statements(self):
        """测试包含多条语句的 EachLoop"""
        # Arrange & Act
        each_loop = EachLoop(
            variable_names=["num"],  # v4.0: 使用 variable_names（列表）
            iterable=Identifier(name="numbers", line=1),
            statements=[
                Assignment(
                    name="total",
                    value=BinaryOp(
                        left=Identifier(name="total", line=2),
                        operator="+",
                        right=Identifier(name="num", line=2),
                        line=2,
                    ),
                    line=2,
                ),
                LogStatement(message="Processing", level="debug", line=3),
            ],
            line=1,
        )

        # Assert
        assert each_loop.variable_name == "num", "循环变量应该是 num（向后兼容属性）"
        assert each_loop.variable_names == ["num"], "variable_names 应该是 ['num']"
        assert len(each_loop.statements) == 2, "应该有 2 条语句"
        assert isinstance(each_loop.statements[0], Assignment)
        assert isinstance(each_loop.statements[1], LogStatement)


class TestUpdatedIfBlock:
    """测试更新的 IfBlock 节点"""

    def test_if_block_with_expression_condition(self):
        """测试使用表达式作为条件的 IfBlock"""
        # Arrange & Act
        if_block = IfBlock(
            condition=BinaryOp(
                left=Identifier(name="age", line=1),
                operator=">",
                right=Literal(value=18, line=1),
                line=1,
            ),
            then_statements=[LogStatement(message="成年人", level="info", line=2)],
            else_statements=[],
            line=1,
        )

        # Assert
        assert isinstance(if_block.condition, BinaryOp), "条件应该是 BinaryOp 表达式"
        assert if_block.condition.operator == ">"
        assert len(if_block.then_statements) == 1
        assert len(if_block.else_statements) == 0

    def test_if_else_block_with_expressions(self):
        """测试包含 else 的 IfBlock"""
        # Arrange & Act
        if_block = IfBlock(
            condition=BinaryOp(
                left=Identifier(name="score", line=1),
                operator=">=",
                right=Literal(value=60, line=1),
                line=1,
            ),
            then_statements=[
                Assignment(name="result", value=Literal(value="pass", line=2), line=2)
            ],
            else_statements=[
                Assignment(name="result", value=Literal(value="fail", line=3), line=3)
            ],
            line=1,
        )

        # Assert
        assert len(if_block.then_statements) == 1
        assert len(if_block.else_statements) == 1
        assert isinstance(if_block.then_statements[0], Assignment)
        assert isinstance(if_block.else_statements[0], Assignment)


class TestUpdatedLogStatement:
    """测试更新的 LogStatement 节点"""

    def test_log_statement_with_string_interpolation(self):
        """测试使用字符串插值的 LogStatement"""
        # Arrange & Act
        log_stmt = LogStatement(
            message=StringInterpolation(parts=["Age: ", Identifier(name="age", line=1)], line=1),
            level="info",
            line=1,
        )

        # Assert
        assert isinstance(
            log_stmt.message, StringInterpolation
        ), "消息应该是 StringInterpolation 节点"
        assert log_stmt.level == "info"

    def test_log_statement_with_plain_string(self):
        """测试使用普通字符串的 LogStatement"""
        # Arrange & Act
        log_stmt = LogStatement(message="Simple message", level="debug", line=1)

        # Assert
        assert log_stmt.message == "Simple message"
        assert log_stmt.level == "debug"


class TestComplexExpressions:
    """测试复杂表达式组合"""

    def test_nested_binary_expression(self):
        """测试嵌套二元表达式 (a + b) * c > 100"""
        # Arrange & Act
        expr = BinaryOp(
            left=BinaryOp(
                left=BinaryOp(
                    left=Identifier(name="a", line=1),
                    operator="+",
                    right=Identifier(name="b", line=1),
                    line=1,
                ),
                operator="*",
                right=Identifier(name="c", line=1),
                line=1,
            ),
            operator=">",
            right=Literal(value=100, line=1),
            line=1,
        )

        # Assert
        assert isinstance(expr.left, BinaryOp), "左侧应该是 BinaryOp"
        assert isinstance(expr.left.left, BinaryOp), "左侧的左侧应该是 BinaryOp"
        assert expr.operator == ">"
        assert expr.left.operator == "*"
        assert expr.left.left.operator == "+"

    def test_system_variable_in_expression(self):
        """测试表达式中的系统变量 $page.url contains "success" """
        # Arrange & Act
        expr = BinaryOp(
            left=SystemVariable(path="page.url", line=1),
            operator="contains",
            right=Literal(value="success", line=1),
            line=1,
        )

        # Assert
        assert isinstance(expr.left, SystemVariable), "左侧应该是 SystemVariable"
        assert expr.left.path == "page.url"
        assert expr.operator == "contains"
        assert expr.right.value == "success"

    def test_member_access_in_expression(self):
        """测试表达式中的成员访问 user.age > 18"""
        # Arrange & Act
        expr = BinaryOp(
            left=MemberAccess(object=Identifier(name="user", line=1), property="age", line=1),
            operator=">",
            right=Literal(value=18, line=1),
            line=1,
        )

        # Assert
        assert isinstance(expr.left, MemberAccess)
        assert expr.left.property == "age"
        assert expr.operator == ">"

    def test_array_access_in_expression(self):
        """测试表达式中的数组访问 items[0] == "first" """
        # Arrange & Act
        expr = BinaryOp(
            left=ArrayAccess(
                array=Identifier(name="items", line=1), index=Literal(value=0, line=1), line=1
            ),
            operator="==",
            right=Literal(value="first", line=1),
            line=1,
        )

        # Assert
        assert isinstance(expr.left, ArrayAccess)
        assert expr.operator == "=="
        assert expr.right.value == "first"


class TestNodeLineNumbers:
    """测试所有节点的行号属性"""

    def test_all_nodes_have_line_numbers(self):
        """测试所有节点都有行号"""
        # Arrange & Act
        nodes = [
            LetStatement(name="x", value=Literal(value=1, line=5), line=5),
            ConstStatement(name="MAX", value=Literal(value=100, line=10), line=10),
            Assignment(name="y", value=Identifier(name="x", line=15), line=15),
            Literal(value="test", line=20),
            Identifier(name="var", line=25),
            SystemVariable(path="context.id", line=30),
            BinaryOp(
                left=Identifier(name="a", line=35),
                operator="+",
                right=Identifier(name="b", line=35),
                line=35,
            ),
            UnaryOp(operator="NOT", operand=Identifier(name="flag", line=40), line=40),
        ]

        # Assert
        expected_lines = [5, 10, 15, 20, 25, 30, 35, 40]
        for i, node in enumerate(nodes):
            assert (
                node.line == expected_lines[i]
            ), f"节点 {type(node).__name__} 的行号应该是 {expected_lines[i]}"
