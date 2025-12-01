"""
v4.3 函数定义和调用测试

测试用户自定义函数功能，包括:
1. 基础函数定义和调用
2. 参数传递（按值传递）
3. 返回值
4. 局部作用域和变量
5. 访问全局常量
6. 调用其他函数（内置和自定义）
7. 递归检测
8. 错误处理
"""

import pytest
import uuid
from flowby.lexer import Lexer
from flowby.parser import Parser
from flowby.interpreter import Interpreter, ReturnException
from flowby.context import ExecutionContext
from flowby.errors import ExecutionError
from flowby.symbol_table import SymbolType


def create_context():
    """创建测试执行上下文"""
    task_id = str(uuid.uuid4())
    return ExecutionContext(task_id=task_id)


class TestBasicFunctionDefinition:
    """测试基础函数定义"""

    def test_simple_function_definition(self):
        """测试简单函数定义（无参数，无返回值）"""
        # Arrange
        code = """
function greet():
    log "Hello, World!"
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert - 函数应该被注册到符号表
        symbol = interpreter.symbol_table.current_scope().symbols["greet"]
        assert symbol.symbol_type == SymbolType.FUNCTION
        # 值本身就是 FunctionSymbol
        func_symbol = symbol.value
        assert func_symbol.name == "greet"
        assert len(func_symbol.params) == 0

    def test_function_with_parameters(self):
        """测试带参数的函数定义"""
        # Arrange
        code = """
function add(a, b):
    log a + b
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        symbol = interpreter.symbol_table.current_scope().symbols["add"]
        assert symbol.symbol_type == SymbolType.FUNCTION
        func_symbol = symbol.value
        assert len(func_symbol.params) == 2
        assert func_symbol.params == ["a", "b"]

    def test_function_redefinition_error(self):
        """测试函数重定义应该失败"""
        # Arrange
        code = """
function test():
    log "First"

function test():
    log "Second"
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act & Assert
        with pytest.raises(ExecutionError) as exc_info:
            interpreter.execute(program)

        assert "已定义" in str(exc_info.value)


class TestFunctionCall:
    """测试函数调用"""

    def test_simple_function_call(self):
        """测试简单函数调用（无参数）"""
        # Arrange
        code = """
let result = 0

function increment():
    result = result + 1

increment()
increment()
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("result", 0) == 2

    def test_function_call_with_arguments(self):
        """测试带参数的函数调用"""
        # Arrange
        code = """
let sum = 0

function add(a, b):
    sum = a + b

add(10, 20)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("sum", 0) == 30

    def test_function_call_with_expression_arguments(self):
        """测试使用表达式作为参数"""
        # Arrange
        code = """
let result = 0

function multiply(x, y):
    result = x * y

let a = 5
let b = 6
multiply(a + 1, b - 1)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("result", 0) == 30  # (5+1) * (6-1) = 6 * 5 = 30


class TestReturnStatement:
    """测试 return 语句"""

    def test_return_value(self):
        """测试函数返回值"""
        # Arrange
        code = """
function add(a, b):
    return a + b

let result = add(10, 20)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("result", 0) == 30

    def test_return_without_value(self):
        """测试无返回值的 return 语句"""
        # Arrange
        code = """
function doSomething():
    log "Doing something"
    return

let result = doSomething()
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("result", 0) is None

    def test_early_return(self):
        """测试提前 return"""
        # Arrange
        code = """
let executed = False

function checkValue(x):
    if x < 0:
        return False

    executed = True
    return True

let result1 = checkValue(-5)
let result2 = checkValue(5)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("result1", 0) is False
        assert interpreter.symbol_table.get("result2", 0) is True
        assert interpreter.symbol_table.get("executed", 0) is True

    def test_return_outside_function_error(self):
        """测试在函数外使用 return 应该失败"""
        # Arrange
        code = """
let x = 5
return x
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act & Assert
        with pytest.raises(ExecutionError) as exc_info:
            interpreter.execute(program)

        assert "只能在函数内使用" in str(exc_info.value)


class TestLocalScope:
    """测试函数局部作用域"""

    def test_local_variables(self):
        """测试局部变量不影响全局作用域"""
        # Arrange
        code = """
let x = 10

function changeX():
    let x = 20
    log x

changeX()
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("x", 0) == 10  # 全局变量未改变

    def test_parameter_isolation(self):
        """测试参数按值传递（值拷贝，不影响外部变量）"""
        # Arrange
        code = """
let num = 5

function double(n):
    n = n * 2
    return n

let result = double(num)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("num", 0) == 5  # 原变量未改变
        assert interpreter.symbol_table.get("result", 0) == 10

    def test_access_global_const(self):
        """测试函数可以访问全局常量"""
        # Arrange
        code = """
const MAX_VALUE = 100

function checkLimit(value):
    return value <= MAX_VALUE

let ok1 = checkLimit(50)
let ok2 = checkLimit(150)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("ok1", 0) is True
        assert interpreter.symbol_table.get("ok2", 0) is False


class TestNestedFunctionCalls:
    """测试嵌套函数调用"""

    def test_call_builtin_function_from_user_function(self):
        """测试在用户函数中调用内置函数"""
        # Arrange
        code = """
function getLength(text):
    return len(text)

let result = getLength("Hello")
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("result", 0) == 5

    def test_call_user_function_from_user_function(self):
        """测试在用户函数中调用另一个用户函数"""
        # Arrange
        code = """
function add(a, b):
    return a + b

function addThree(x, y, z):
    return add(add(x, y), z)

let result = addThree(1, 2, 3)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("result", 0) == 6

    def test_complex_function_composition(self):
        """测试复杂函数组合"""
        # Arrange
        code = """
function isValidEmail(email):
    return email contains "@" and email contains "."

function isStrongPassword(password):
    return len(password) >= 8

function validateUser(email, password):
    if not isValidEmail(email):
        return False
    if not isStrongPassword(password):
        return False
    return True

let valid1 = validateUser("test@example.com", "password123")
let valid2 = validateUser("invalid", "short")
let valid3 = validateUser("test@example.com", "short")
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("valid1", 0) is True
        assert interpreter.symbol_table.get("valid2", 0) is False
        assert interpreter.symbol_table.get("valid3", 0) is False


class TestRecursionDetection:
    """测试递归检测"""

    def test_direct_recursion_error(self):
        """测试直接递归应该失败"""
        # Arrange
        code = """
function factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

let result = factorial(5)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act & Assert
        with pytest.raises(ExecutionError) as exc_info:
            interpreter.execute(program)

        assert "不支持递归" in str(exc_info.value)

    def test_indirect_recursion_error(self):
        """测试间接递归应该失败"""
        # Arrange
        code = """
function funcA(n):
    if n <= 0:
        return 0
    return funcB(n - 1)

function funcB(n):
    if n <= 0:
        return 0
    return funcA(n - 1)

let result = funcA(5)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act & Assert
        with pytest.raises(ExecutionError) as exc_info:
            interpreter.execute(program)

        assert "不支持递归" in str(exc_info.value)


class TestErrorHandling:
    """测试错误处理"""

    def test_undefined_function_error(self):
        """测试调用未定义的函数应该失败"""
        # Arrange
        code = """
let result = unknownFunction(10)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act & Assert
        with pytest.raises(ExecutionError) as exc_info:
            interpreter.execute(program)

        assert "未定义的函数" in str(exc_info.value)

    def test_wrong_argument_count_error(self):
        """测试参数数量不匹配应该失败"""
        # Arrange
        code = """
function add(a, b):
    return a + b

let result = add(10)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act & Assert
        with pytest.raises(ExecutionError) as exc_info:
            interpreter.execute(program)

        assert "需要 2 个参数" in str(exc_info.value)
        assert "提供了 1 个" in str(exc_info.value)

    def test_calling_non_function_error(self):
        """测试调用非函数类型应该失败"""
        # Arrange
        code = """
let x = 10
let result = x(5)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act & Assert
        with pytest.raises(ExecutionError) as exc_info:
            interpreter.execute(program)

        assert "不是函数" in str(exc_info.value)


class TestComplexScenarios:
    """测试复杂场景"""

    def test_function_with_loop(self):
        """测试函数内包含循环"""
        # Arrange
        code = """
function sumArray(arr):
    let total = 0
    for item in arr:
        total = total + item
    return total

let numbers = [1, 2, 3, 4, 5]
let result = sumArray(numbers)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("result", 0) == 15

    def test_function_with_conditional(self):
        """测试函数内包含条件语句"""
        # Arrange
        code = """
function max(a, b):
    if a > b:
        return a
    else:
        return b

let result1 = max(10, 20)
let result2 = max(30, 15)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("result1", 0) == 20
        assert interpreter.symbol_table.get("result2", 0) == 30

    def test_multiple_functions(self):
        """测试定义和使用多个函数"""
        # Arrange
        code = """
function double(x):
    return x * 2

function triple(x):
    return x * 3

function addDoubleAndTriple(n):
    return double(n) + triple(n)

let result = addDoubleAndTriple(5)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        # double(5) = 10, triple(5) = 15, sum = 25
        assert interpreter.symbol_table.get("result", 0) == 25

    def test_function_returning_boolean_expression(self):
        """测试函数返回布尔表达式"""
        # Arrange
        code = """
function inRange(value, min, max):
    return value >= min and value <= max

let ok1 = inRange(50, 0, 100)
let ok2 = inRange(150, 0, 100)
let ok3 = inRange(-10, 0, 100)
"""
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        program = parser.parse(tokens)

        context = create_context()
        interpreter = Interpreter(context)

        # Act
        interpreter.execute(program)

        # Assert
        assert interpreter.symbol_table.get("ok1", 0) is True
        assert interpreter.symbol_table.get("ok2", 0) is False
        assert interpreter.symbol_table.get("ok3", 0) is False
