"""
VR-001 变量未定义检查测试

测试 Parser 阶段的变量未定义检查（VR-001 规则）

测试策略：
1. 基本检查：未声明变量直接使用
2. 循环变量：for 循环变量可在循环内使用
3. 函数参数：函数参数可在函数内使用
4. 导入符号：import 的模块和成员可使用
5. 系统变量：page, env, response 无需声明
6. 作用域：变量在定义的作用域及子作用域内可见
"""

import pytest
from flowby.lexer import Lexer
from flowby.parser import Parser
from flowby.errors import ParserError


class TestVR001BasicChecks:
    """基本的 VR-001 变量未定义检查"""

    def test_undefined_variable_in_expression(self):
        """测试：表达式中使用未定义变量应报错"""
        source = """
let result = undefined_var + 10
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "未定义的变量" in str(exc_info.value)
        assert "undefined_var" in str(exc_info.value)
        assert "VR-001" in str(exc_info.value)

    def test_undefined_variable_in_assignment(self):
        """测试：赋值右侧使用未定义变量应报错"""
        source = """
let x = 10
let y = x + undefined_var
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "未定义的变量" in str(exc_info.value)
        assert "undefined_var" in str(exc_info.value)

    def test_undefined_variable_in_condition(self):
        """测试：条件表达式中使用未定义变量应报错"""
        source = """
if undefined_var == 10:
    log "test"
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "未定义的变量" in str(exc_info.value)
        assert "undefined_var" in str(exc_info.value)

    def test_defined_variable_can_be_used(self):
        """测试：已声明的变量可以正常使用"""
        source = """
let x = 10
let y = x + 5
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_const_variable_can_be_used(self):
        """测试：const 声明的变量可以正常使用"""
        source = """
const MAX = 100
let value = MAX - 10
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None


class TestVR001LoopVariables:
    """测试循环变量的 VR-001 检查"""

    def test_loop_variable_can_be_used_in_loop(self):
        """测试：循环变量可以在循环体内使用"""
        source = """
const items = [1, 2, 3]
for item in items:
    log item
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_loop_variable_in_expression(self):
        """测试：循环变量可以在表达式中使用"""
        source = """
const items = [1, 2, 3]
for item in items:
    let doubled = item * 2
    log doubled
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_multiple_loop_variables(self):
        """测试：多个循环变量都可以使用"""
        source = """
const pairs = [[1, 2], [3, 4]]
for a, b in pairs:
    let sum = a + b
    log sum
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None


class TestVR001FunctionParameters:
    """测试函数参数的 VR-001 检查"""

    def test_function_parameter_can_be_used(self):
        """测试：函数参数可以在函数体内使用"""
        source = """
function double(x):
    return x * 2

let result = double(10)
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_multiple_function_parameters(self):
        """测试：多个函数参数都可以使用"""
        source = """
function add(a, b):
    return a + b

let sum = add(1, 2)
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_parameter_in_complex_expression(self):
        """测试：参数可以在复杂表达式中使用"""
        source = """
function calculate(x, y, z):
    let temp = x * 2
    let result = temp + y - z
    return result

let value = calculate(10, 5, 3)
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None


class TestVR001ImportSymbols:
    """测试导入符号的 VR-001 检查"""

    def test_module_alias_can_be_used(self):
        """测试：import 的模块别名可以使用"""
        source = """
import utils from "lib/utils"
let result = utils.greet("Alice")
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_imported_member_can_be_used(self):
        """测试：from...import 的成员可以使用"""
        source = """
from "lib/utils" import greet
let message = greet("Bob")
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_multiple_imported_members(self):
        """测试：多个导入成员都可以使用"""
        source = """
from "lib/validation" import validate_email, validate_length
let email_ok = validate_email("test@example.com")
let length_ok = validate_length("password", 8)
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None


class TestVR001SystemVariables:
    """测试系统变量的 VR-001 检查"""

    def test_page_variable_no_declaration_needed(self):
        """测试：page 系统变量无需声明即可使用"""
        source = """
let url = page.url
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_env_variable_no_declaration_needed(self):
        """测试：env 系统变量无需声明即可使用"""
        source = """
let token = env.API_TOKEN
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_response_variable_no_declaration_needed(self):
        """测试：response 系统变量无需声明即可使用"""
        source = """
let status = response.status_code
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None


class TestVR001Scope:
    """测试变量作用域的 VR-001 检查"""

    def test_variable_visible_in_same_scope(self):
        """测试：变量在同一作用域内可见"""
        source = """
let x = 10
let y = x + 5
let z = y * 2
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_global_variable_visible_in_function(self):
        """测试：全局变量在函数内可见"""
        source = """
const MAX = 100

function check_limit(value):
    return value < MAX

let ok = check_limit(50)
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_global_variable_visible_in_loop(self):
        """测试：全局变量在循环内可见"""
        source = """
const multiplier = 10
const items = [1, 2, 3]

for item in items:
    let result = item * multiplier
    log result
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None


class TestVR001FunctionCalls:
    """测试函数调用的 VR-001 检查"""

    def test_defined_function_can_be_called(self):
        """测试：已定义的函数可以调用"""
        source = """
function greet():
    return "Hello"

let message = greet()
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_builtin_function_can_be_called(self):
        """测试：内置函数可以直接调用（无需声明）"""
        source = """
let items = [1, 2, 3]
let count = len(items)
let text_type = type("hello")
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None


class TestVR001ComplexScenarios:
    """测试复杂场景的 VR-001 检查"""

    def test_chained_variable_dependencies(self):
        """测试：变量依赖链"""
        source = """
let a = 10
let b = a * 2
let c = b + 5
let d = c - a
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_undefined_in_middle_of_chain(self):
        """测试：依赖链中间出现未定义变量"""
        source = """
let a = 10
let b = a * 2
let c = b + undefined_var
let d = c - a
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "未定义的变量" in str(exc_info.value)
        assert "undefined_var" in str(exc_info.value)

    def test_forward_reference_error(self):
        """测试：前向引用应报错"""
        source = """
let x = y + 10
let y = 5
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "未定义的变量" in str(exc_info.value)
        assert "y" in str(exc_info.value)
