"""
表达式求值器测试

测试 ExpressionEvaluator 的功能，包括:
1. 类型转换
2. 字面量求值
3. 标识符求值
4. 系统变量求值
5. 算术运算
6. 比较运算
7. 逻辑运算
8. 字符串运算
9. 成员访问
10. 数组访问
11. 字符串插值
12. 复杂表达式
"""

import pytest
from flowby.expression_evaluator import (
    ExpressionEvaluator,
    to_boolean,
    to_number,
    to_string,
)
from flowby.ast_nodes import (
    Literal,
    Identifier,
    SystemVariable,
    BinaryOp,
    UnaryOp,
    MemberAccess,
    ArrayAccess,
    StringInterpolation,
)
from flowby.symbol_table import SymbolTableStack, SymbolType
from flowby.system_variables import SystemVariables
from flowby.errors import ExecutionError


class MockContext:
    """模拟执行上下文"""

    def __init__(self):
        self.task_id = "task_123"
        self.current_step = "test_step"
        self.step_index = 0
        self.page = MockPage()
        self.script_path = "test_script.flow"


class MockPage:
    """模拟页面对象"""

    def __init__(self):
        self.url = "https://example.com/success"
        self.title = "Test Page"


class TestTypeConversion:
    """测试类型转换函数"""

    def test_to_boolean_with_boolean_values(self):
        """测试布尔值转布尔"""
        # Arrange & Act & Assert
        assert to_boolean(True) == True, "True 应该转换为 True"
        assert to_boolean(False) == False, "False 应该转换为 False"

    def test_to_boolean_with_numbers(self):
        """测试数字转布尔"""
        # Arrange & Act & Assert
        assert to_boolean(1) == True, "1 应该转换为 True"
        assert to_boolean(0) == False, "0 应该转换为 False"
        assert to_boolean(42) == True, "非零数字应该转换为 True"

    def test_to_boolean_with_strings(self):
        """测试字符串转布尔"""
        # Arrange & Act & Assert
        assert to_boolean("hello") == True, "非空字符串应该转换为 True"
        assert to_boolean("") == False, "空字符串应该转换为 False"

    def test_to_boolean_with_none(self):
        """测试 None 转布尔"""
        # Arrange & Act & Assert
        assert to_boolean(None) == False, "None 应该转换为 False"

    def test_to_number_with_integers(self):
        """测试整数转数字"""
        # Arrange & Act & Assert
        assert to_number(42) == 42.0, "整数应该转换为浮点数"
        assert to_number(0) == 0.0, "0 应该转换为 0.0"

    def test_to_number_with_floats(self):
        """测试浮点数转数字"""
        # Arrange & Act & Assert
        assert to_number(3.14) == 3.14, "浮点数应该保持不变"

    def test_to_number_with_strings(self):
        """测试字符串转数字"""
        # Arrange & Act & Assert
        assert to_number("123") == 123.0, "数字字符串应该转换为数字"
        assert to_number("45.67") == 45.67, "浮点数字符串应该转换为浮点数"

    def test_to_number_with_booleans(self):
        """测试布尔值转数字"""
        # Arrange & Act & Assert
        assert to_number(True) == 1.0, "True 应该转换为 1.0"
        assert to_number(False) == 0.0, "False 应该转换为 0.0"

    def test_to_string_with_numbers(self):
        """测试数字转字符串"""
        # Arrange & Act & Assert
        assert to_string(123) == "123", "整数应该转换为字符串"
        assert to_string(3.14) == "3.14", "浮点数应该转换为字符串"

    def test_to_string_with_booleans(self):
        """测试布尔值转字符串"""
        # Arrange & Act & Assert
        assert to_string(True) == "true", "True 应该转换为 'true'"
        assert to_string(False) == "false", "False 应该转换为 'false'"

    def test_to_string_with_none(self):
        """测试 None 转字符串"""
        # Arrange & Act & Assert
        assert to_string(None) == "null", "None 应该转换为 'null'"

    def test_to_string_with_strings(self):
        """测试字符串转字符串"""
        # Arrange & Act & Assert
        assert to_string("hello") == "hello", "字符串应该保持不变"

    @pytest.mark.parametrize(
        "value,expected",
        [
            (True, True),
            (False, False),
            (1, True),
            (0, False),
            ("hello", True),
            ("", False),
            (None, False),
        ],
    )
    def test_to_boolean_various_values(self, value, expected):
        """测试各种值转布尔"""
        assert to_boolean(value) == expected


class TestLiteralEvaluation:
    """测试字面量求值"""

    @pytest.fixture
    def evaluator(self):
        """提供求值器实例"""
        symbol_table = SymbolTableStack()
        symbol_table.enter_scope("global")
        context = MockContext()
        system_vars = SystemVariables(context=context, config_vars={})
        return ExpressionEvaluator(symbol_table, system_vars)

    def test_number_literal(self, evaluator):
        """测试数字字面量"""
        # Arrange
        expr = Literal(value=42, line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == 42, "数字字面量应该返回原值"

    def test_string_literal(self, evaluator):
        """测试字符串字面量"""
        # Arrange
        expr = Literal(value="hello", line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == "hello", "字符串字面量应该返回原值"

    def test_boolean_literal(self, evaluator):
        """测试布尔字面量"""
        # Arrange
        expr = Literal(value=True, line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == True, "布尔字面量应该返回原值"

    def test_null_literal(self, evaluator):
        """测试 null 字面量"""
        # Arrange
        expr = Literal(value=None, line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result is None, "null 字面量应该返回 None"

    @pytest.mark.parametrize("value", [42, "hello", True, False, None, 3.14, 0])
    def test_various_literals(self, evaluator, value):
        """测试各种字面量"""
        # Arrange
        expr = Literal(value=value, line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == value


class TestIdentifierEvaluation:
    """测试标识符求值"""

    @pytest.fixture
    def evaluator(self):
        """提供带变量的求值器"""
        symbol_table = SymbolTableStack()
        symbol_table.enter_scope("global")
        symbol_table.define("age", 25, SymbolType.VARIABLE, 0)
        symbol_table.define("username", "alice", SymbolType.VARIABLE, 0)
        symbol_table.define("MAX", 100, SymbolType.CONSTANT, 0)

        context = MockContext()
        system_vars = SystemVariables(context=context, config_vars={})
        return ExpressionEvaluator(symbol_table, system_vars)

    def test_lookup_existing_variable(self, evaluator):
        """测试查找存在的变量"""
        # Arrange
        expr = Identifier(name="age", line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == 25, "应该返回变量的值"

    def test_lookup_string_variable(self, evaluator):
        """测试查找字符串变量"""
        # Arrange
        expr = Identifier(name="username", line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == "alice", "应该返回字符串变量的值"

    def test_lookup_constant(self, evaluator):
        """测试查找常量"""
        # Arrange
        expr = Identifier(name="MAX", line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == 100, "应该返回常量的值"

    def test_lookup_nonexistent_variable(self, evaluator):
        """测试查找不存在的变量"""
        # Arrange
        expr = Identifier(name="nonexistent", line=1)

        # Act & Assert
        with pytest.raises(ExecutionError):
            evaluator.evaluate(expr)


class TestSystemVariableEvaluation:
    """测试系统变量求值"""

    @pytest.fixture
    def evaluator(self):
        """提供带系统变量的求值器"""
        symbol_table = SymbolTableStack()
        symbol_table.enter_scope("global")

        context = MockContext()
        system_vars = SystemVariables(
            context=context, config_vars={"api": {"token": "secret123", "timeout": 30}}
        )
        return ExpressionEvaluator(symbol_table, system_vars)

    def test_context_task_id(self, evaluator):
        """测试 $context.task_id"""
        # Arrange
        expr = SystemVariable(path="context.task_id", line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == "task_123", "$context.task_id 应该返回任务 ID"

    def test_page_url(self, evaluator):
        """测试 $page.url"""
        # Arrange
        expr = SystemVariable(path="page.url", line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == "https://example.com/success", "$page.url 应该返回页面 URL"

    def test_config_nested_access(self, evaluator):
        """测试 $config 嵌套访问"""
        # Arrange
        expr = SystemVariable(path="config.api.token", line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == "secret123", "$config.api.token 应该返回嵌套的配置值"

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("context.task_id", "task_123"),
            # ("context.current_step", "test_step"),  # API 已变更为 context.step_name
            ("page.url", "https://example.com/success"),
            # ("page.title", "Test Page"),  # title 是方法而非属性
            ("config.api.token", "secret123"),
            ("config.api.timeout", 30),
        ],
    )
    def test_various_system_variables(self, evaluator, path, expected):
        """测试各种系统变量"""
        # Arrange
        expr = SystemVariable(path=path, line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == expected


class TestArithmeticOperations:
    """测试算术运算"""

    @pytest.fixture
    def evaluator(self):
        """提供求值器"""
        symbol_table = SymbolTableStack()
        symbol_table.enter_scope("global")
        context = MockContext()
        system_vars = SystemVariables(context=context, config_vars={})
        return ExpressionEvaluator(symbol_table, system_vars)

    def test_addition(self, evaluator):
        """测试加法"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=10, line=1), operator="+", right=Literal(value=5, line=1), line=1
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == 15, "10 + 5 应该等于 15"

    def test_subtraction(self, evaluator):
        """测试减法"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=10, line=1), operator="-", right=Literal(value=3, line=1), line=1
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == 7, "10 - 3 应该等于 7"

    def test_multiplication(self, evaluator):
        """测试乘法"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=6, line=1), operator="*", right=Literal(value=7, line=1), line=1
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == 42, "6 * 7 应该等于 42"

    def test_division(self, evaluator):
        """测试除法"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=15, line=1), operator="/", right=Literal(value=3, line=1), line=1
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == 5.0, "15 / 3 应该等于 5.0"

    def test_modulo(self, evaluator):
        """测试取模"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=17, line=1), operator="%", right=Literal(value=5, line=1), line=1
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == 2, "17 % 5 应该等于 2"

    def test_string_concatenation(self, evaluator):
        """测试字符串拼接"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value="Hello ", line=1),
            operator="+",
            right=Literal(value="World", line=1),
            line=1,
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == "Hello World", "'Hello ' + 'World' 应该等于 'Hello World'"

    @pytest.mark.parametrize(
        "left,op,right,expected",
        [
            (10, "+", 5, 15),
            (10, "-", 3, 7),
            (6, "*", 7, 42),
            (15, "/", 3, 5.0),
            (17, "%", 5, 2),
        ],
    )
    def test_various_arithmetic_operations(self, evaluator, left, op, right, expected):
        """测试各种算术运算"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=left, line=1),
            operator=op,
            right=Literal(value=right, line=1),
            line=1,
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == expected


class TestComparisonOperations:
    """测试比较运算"""

    @pytest.fixture
    def evaluator(self):
        """提供求值器"""
        symbol_table = SymbolTableStack()
        symbol_table.enter_scope("global")
        context = MockContext()
        system_vars = SystemVariables(context=context, config_vars={})
        return ExpressionEvaluator(symbol_table, system_vars)

    def test_greater_than(self, evaluator):
        """测试大于"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=10, line=1), operator=">", right=Literal(value=5, line=1), line=1
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == True, "10 > 5 应该为 True"

    def test_less_than(self, evaluator):
        """测试小于"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=3, line=1), operator="<", right=Literal(value=5, line=1), line=1
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == True, "3 < 5 应该为 True"

    def test_equal(self, evaluator):
        """测试相等"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=5, line=1), operator="==", right=Literal(value=5, line=1), line=1
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == True, "5 == 5 应该为 True"

    def test_not_equal(self, evaluator):
        """测试不等"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=5, line=1), operator="!=", right=Literal(value=3, line=1), line=1
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == True, "5 != 3 应该为 True"

    @pytest.mark.parametrize(
        "left,op,right,expected",
        [
            (10, ">", 5, True),
            (3, "<", 5, True),
            (5, "==", 5, True),
            (5, "!=", 3, True),
            (5, ">=", 5, True),
            (5, "<=", 5, True),
            (3, ">", 5, False),
            (10, "<", 5, False),
        ],
    )
    def test_various_comparisons(self, evaluator, left, op, right, expected):
        """测试各种比较运算"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=left, line=1),
            operator=op,
            right=Literal(value=right, line=1),
            line=1,
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == expected


class TestLogicalOperations:
    """测试逻辑运算"""

    @pytest.fixture
    def evaluator(self):
        """提供求值器"""
        symbol_table = SymbolTableStack()
        symbol_table.enter_scope("global")
        context = MockContext()
        system_vars = SystemVariables(context=context, config_vars={})
        return ExpressionEvaluator(symbol_table, system_vars)

    def test_and_true_true(self, evaluator):
        """测试 True AND True"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=True, line=1),
            operator="AND",
            right=Literal(value=True, line=1),
            line=1,
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == True, "True AND True 应该为 True"

    def test_and_true_false(self, evaluator):
        """测试 True AND False"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=True, line=1),
            operator="AND",
            right=Literal(value=False, line=1),
            line=1,
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == False, "True AND False 应该为 False"

    def test_or_true_false(self, evaluator):
        """测试 True OR False"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=True, line=1),
            operator="OR",
            right=Literal(value=False, line=1),
            line=1,
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == True, "True OR False 应该为 True"

    def test_not_false(self, evaluator):
        """测试 NOT False"""
        # Arrange
        expr = UnaryOp(operator="NOT", operand=Literal(value=False, line=1), line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == True, "NOT False 应该为 True"

    def test_not_true(self, evaluator):
        """测试 NOT True"""
        # Arrange
        expr = UnaryOp(operator="NOT", operand=Literal(value=True, line=1), line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == False, "NOT True 应该为 False"

    @pytest.mark.parametrize(
        "left,op,right,expected",
        [
            (True, "AND", True, True),
            (True, "AND", False, False),
            (False, "AND", True, False),
            (False, "AND", False, False),
            (True, "OR", True, True),
            (True, "OR", False, True),
            (False, "OR", True, True),
            (False, "OR", False, False),
        ],
    )
    def test_various_logical_operations(self, evaluator, left, op, right, expected):
        """测试各种逻辑运算"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=left, line=1),
            operator=op,
            right=Literal(value=right, line=1),
            line=1,
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == expected


class TestStringOperations:
    """测试字符串运算"""

    @pytest.fixture
    def evaluator(self):
        """提供求值器"""
        symbol_table = SymbolTableStack()
        symbol_table.enter_scope("global")
        context = MockContext()
        system_vars = SystemVariables(context=context, config_vars={})
        return ExpressionEvaluator(symbol_table, system_vars)

    def test_contains_operator(self, evaluator):
        """测试 contains 运算符"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value="hello world", line=1),
            operator="contains",
            right=Literal(value="world", line=1),
            line=1,
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == True, "'hello world' contains 'world' 应该为 True"

    def test_matches_operator(self, evaluator):
        """测试 matches 运算符（正则）"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value="test123", line=1),
            operator="matches",
            right=Literal(value=r"\d+", line=1),
            line=1,
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == True, "'test123' matches '\\d+' 应该为 True"

    @pytest.mark.parametrize(
        "text,substring,expected",
        [
            ("hello world", "world", True),
            ("hello world", "foo", False),
            ("Python", "Py", True),
            ("Python", "py", False),  # 大小写敏感
        ],
    )
    def test_various_contains_operations(self, evaluator, text, substring, expected):
        """测试各种 contains 运算"""
        # Arrange
        expr = BinaryOp(
            left=Literal(value=text, line=1),
            operator="contains",
            right=Literal(value=substring, line=1),
            line=1,
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == expected


class TestMemberAccess:
    """测试成员访问"""

    @pytest.fixture
    def evaluator(self):
        """提供带对象的求值器"""
        symbol_table = SymbolTableStack()
        symbol_table.enter_scope("global")
        symbol_table.define(
            "user", {"email": "alice@example.com", "id": 123}, SymbolType.VARIABLE, 0
        )

        context = MockContext()
        system_vars = SystemVariables(context=context, config_vars={})
        return ExpressionEvaluator(symbol_table, system_vars)

    def test_access_object_property(self, evaluator):
        """测试访问对象属性"""
        # Arrange
        expr = MemberAccess(object=Identifier(name="user", line=1), property="email", line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == "alice@example.com", "user.email 应该返回 'alice@example.com'"

    def test_access_numeric_property(self, evaluator):
        """测试访问数字属性"""
        # Arrange
        expr = MemberAccess(object=Identifier(name="user", line=1), property="id", line=1)

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == 123, "user.id 应该返回 123"


class TestArrayAccess:
    """测试数组访问"""

    @pytest.fixture
    def evaluator(self):
        """提供带数组的求值器"""
        symbol_table = SymbolTableStack()
        symbol_table.enter_scope("global")
        symbol_table.define("items", ["a", "b", "c"], SymbolType.VARIABLE, 0)

        context = MockContext()
        system_vars = SystemVariables(context=context, config_vars={})
        return ExpressionEvaluator(symbol_table, system_vars)

    def test_access_first_element(self, evaluator):
        """测试访问第一个元素"""
        # Arrange
        expr = ArrayAccess(
            array=Identifier(name="items", line=1), index=Literal(value=0, line=1), line=1
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == "a", "items[0] 应该返回 'a'"

    def test_access_last_element(self, evaluator):
        """测试访问最后一个元素"""
        # Arrange
        expr = ArrayAccess(
            array=Identifier(name="items", line=1), index=Literal(value=2, line=1), line=1
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == "c", "items[2] 应该返回 'c'"

    @pytest.mark.parametrize(
        "index,expected",
        [
            (0, "a"),
            (1, "b"),
            (2, "c"),
        ],
    )
    def test_various_array_indices(self, evaluator, index, expected):
        """测试各种数组索引"""
        # Arrange
        expr = ArrayAccess(
            array=Identifier(name="items", line=1), index=Literal(value=index, line=1), line=1
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == expected


class TestStringInterpolation:
    """测试字符串插值"""

    @pytest.fixture
    def evaluator(self):
        """提供带变量的求值器"""
        symbol_table = SymbolTableStack()
        symbol_table.enter_scope("global")
        symbol_table.define("username", "alice", SymbolType.VARIABLE, 0)
        symbol_table.define("age", 25, SymbolType.VARIABLE, 0)

        context = MockContext()
        system_vars = SystemVariables(context=context, config_vars={})
        return ExpressionEvaluator(symbol_table, system_vars)

    def test_simple_interpolation(self, evaluator):
        """测试简单插值"""
        # Arrange
        expr = StringInterpolation(
            parts=["Hello ", Identifier(name="username", line=1), "!"], line=1
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == "Hello alice!", "'Hello {username}!' 应该返回 'Hello alice!'"

    def test_interpolation_with_expression(self, evaluator):
        """测试带表达式的插值"""
        # Arrange
        expr = StringInterpolation(
            parts=[
                "Age: ",
                BinaryOp(
                    left=Identifier(name="age", line=1),
                    operator="+",
                    right=Literal(value=5, line=1),
                    line=1,
                ),
            ],
            line=1,
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        # v4.0: 整数运算返回整数，字符串插值显示 "30" 而非 "30.0"
        assert result == "Age: 30", "'Age: {age + 5}' 应该返回 'Age: 30' (v4.0 整数类型)"


class TestComplexExpressions:
    """测试复杂表达式"""

    @pytest.fixture
    def evaluator(self):
        """提供带变量的求值器"""
        symbol_table = SymbolTableStack()
        symbol_table.enter_scope("global")
        symbol_table.define("age", 25, SymbolType.VARIABLE, 0)
        symbol_table.define("username", "alice", SymbolType.VARIABLE, 0)

        context = MockContext()
        system_vars = SystemVariables(context=context, config_vars={})
        return ExpressionEvaluator(symbol_table, system_vars)

    def test_nested_arithmetic_with_comparison(self, evaluator):
        """测试嵌套算术与比较"""
        # Arrange: (age + 5) * 2 > 50
        expr = BinaryOp(
            left=BinaryOp(
                left=BinaryOp(
                    left=Identifier(name="age", line=1),
                    operator="+",
                    right=Literal(value=5, line=1),
                    line=1,
                ),
                operator="*",
                right=Literal(value=2, line=1),
                line=1,
            ),
            operator=">",
            right=Literal(value=50, line=1),
            line=1,
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        # (25 + 5) * 2 = 60 > 50 = True
        assert result == True, "(age + 5) * 2 > 50 应该为 True (当 age=25)"

    def test_comparison_with_logical_and(self, evaluator):
        """测试比较与逻辑 AND"""
        # Arrange: age > 18 AND username == "alice"
        expr = BinaryOp(
            left=BinaryOp(
                left=Identifier(name="age", line=1),
                operator=">",
                right=Literal(value=18, line=1),
                line=1,
            ),
            operator="AND",
            right=BinaryOp(
                left=Identifier(name="username", line=1),
                operator="==",
                right=Literal(value="alice", line=1),
                line=1,
            ),
            line=1,
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        assert result == True, "age > 18 AND username == 'alice' 应该为 True"

    def test_complex_nested_expression(self, evaluator):
        """测试复杂嵌套表达式"""
        # Arrange: (age + 10) / 5 == 7.0
        expr = BinaryOp(
            left=BinaryOp(
                left=BinaryOp(
                    left=Identifier(name="age", line=1),
                    operator="+",
                    right=Literal(value=10, line=1),
                    line=1,
                ),
                operator="/",
                right=Literal(value=5, line=1),
                line=1,
            ),
            operator="==",
            right=Literal(value=7.0, line=1),
            line=1,
        )

        # Act
        result = evaluator.evaluate(expr)

        # Assert
        # (25 + 10) / 5 = 35 / 5 = 7.0
        assert result == True, "(age + 10) / 5 == 7.0 应该为 True"
