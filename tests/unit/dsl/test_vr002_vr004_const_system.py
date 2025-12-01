"""
VR-002 和 VR-004 语义检查测试

VR-002: 常量不能重新赋值
VR-004: 系统变量只读

测试策略：
1. VR-002 基本检查：const 声明的变量不能修改
2. VR-002 作用域检查：不同作用域的常量
3. VR-004 系统变量检查：page, env, response 不能修改
4. VR-004 成员访问：系统变量成员可以访问（不算修改）
5. 允许的操作：let 变量可以修改
"""

import pytest
from flowby.lexer import Lexer
from flowby.parser import Parser
from flowby.errors import ParserError


class TestVR002ConstReassignment:
    """VR-002: 常量不能重新赋值"""

    def test_const_cannot_be_reassigned(self):
        """测试：修改 const 变量应报错"""
        source = """
const MAX = 100
MAX = 200
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "不能修改常量" in str(exc_info.value)
        assert "MAX" in str(exc_info.value)
        assert "VR-002" in str(exc_info.value)

    def test_const_reassignment_in_expression(self):
        """测试：在表达式中修改常量应报错"""
        source = """
const PI = 3.14
PI = PI * 2
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "不能修改常量" in str(exc_info.value)
        assert "PI" in str(exc_info.value)

    def test_const_can_be_used_in_expression(self):
        """测试：常量可以在表达式中使用（读取）"""
        source = """
const MAX = 100
let value = MAX + 50
let doubled = MAX * 2
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_let_variable_can_be_reassigned(self):
        """测试：let 变量可以正常重新赋值"""
        source = """
let counter = 0
counter = counter + 1
counter = 10
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_const_in_different_scopes(self):
        """测试：不同作用域的同名常量"""
        source = """
const MAX = 100

function test():
    const MAX = 200
    return MAX

let result = test()
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_const_in_loop_scope(self):
        """测试：循环内部的常量"""
        source = """
const items = [1, 2, 3]

for item in items:
    const squared = item * item
    log squared
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_multiple_const_declarations(self):
        """测试：多个常量声明"""
        source = """
const MAX = 100
const MIN = 0
const PI = 3.14

let range = MAX - MIN
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_const_error_shows_definition_line(self):
        """测试：错误消息应包含常量定义行号"""
        source = """
const MAX = 100
let x = 10
MAX = 200
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        error_msg = str(exc_info.value)
        assert "定义于" in error_msg
        # 错误消息应该指出 MAX 定义在第 2 行


class TestVR004SystemVariableReadonly:
    """VR-004: 系统变量只读"""

    def test_page_cannot_be_reassigned(self):
        """测试：不能修改 page 系统变量"""
        source = """
page = "invalid"
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "不能修改系统变量" in str(exc_info.value)
        assert "page" in str(exc_info.value)
        assert "VR-004" in str(exc_info.value)

    def test_env_cannot_be_reassigned(self):
        """测试：不能修改 env 系统变量"""
        source = """
env = "invalid"
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "不能修改系统变量" in str(exc_info.value)
        assert "env" in str(exc_info.value)
        assert "VR-004" in str(exc_info.value)

    def test_response_cannot_be_reassigned(self):
        """测试：不能修改 response 系统变量"""
        source = """
response = "invalid"
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "不能修改系统变量" in str(exc_info.value)
        assert "response" in str(exc_info.value)
        assert "VR-004" in str(exc_info.value)

    def test_page_member_access_allowed(self):
        """测试：可以访问 page 的成员（不是修改 page 本身）"""
        source = """
let url = page.url
let title = page.title
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_env_member_access_allowed(self):
        """测试：可以访问 env 的成员"""
        source = """
let token = env.API_TOKEN
let base_url = env.BASE_URL
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_response_member_access_allowed(self):
        """测试：可以访问 response 的成员"""
        source = """
let status = response.status_code
let data = response.data
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None


class TestVR002VR004Combined:
    """VR-002 和 VR-004 组合测试"""

    def test_const_and_system_variable_together(self):
        """测试：常量和系统变量混合使用"""
        source = """
const MAX_RETRIES = 3
let url = page.url
let retries = 0

if retries < MAX_RETRIES:
    log "Retrying..."
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_cannot_modify_const_or_system_variable(self):
        """测试：既不能修改常量，也不能修改系统变量"""
        source1 = """
const MAX = 100
MAX = 200
"""
        source2 = """
page = "invalid"
"""

        for source in [source1, source2]:
            tokens = Lexer().tokenize(source)
            with pytest.raises(ParserError):
                Parser().parse(tokens)

    def test_let_variables_not_affected(self):
        """测试：let 变量不受 VR-002/VR-004 影响"""
        source = """
const MAX = 100
let counter = 0
let url = page.url

counter = counter + 1
counter = 10
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_function_parameters_not_affected(self):
        """测试：函数参数可以修改（不受常量规则影响）"""
        source = """
function increment(x):
    x = x + 1
    return x

let result = increment(10)
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_loop_variables_not_affected(self):
        """测试：循环变量可以修改"""
        source = """
const items = [1, 2, 3]

for item in items:
    item = item * 2
    log item
"""
        tokens = Lexer().tokenize(source)
        # 注意：这个测试可能会失败，因为修改循环变量通常不推荐
        # 但从语法角度，循环变量是可修改的
        ast = Parser().parse(tokens)
        assert ast is not None


class TestVR002ErrorMessages:
    """测试 VR-002 错误消息质量"""

    def test_error_message_includes_rule_id(self):
        """测试：错误消息包含 VR-002 规则ID"""
        source = """
const VALUE = 42
VALUE = 100
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "VR-002" in str(exc_info.value)

    def test_error_message_includes_variable_name(self):
        """测试：错误消息包含变量名"""
        source = """
const MAGIC_NUMBER = 42
MAGIC_NUMBER = 100
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "MAGIC_NUMBER" in str(exc_info.value)

    def test_error_message_provides_help(self):
        """测试：错误消息提供修复建议"""
        source = """
const MAX = 100
MAX = 200
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        error_msg = str(exc_info.value)
        assert "let" in error_msg.lower() or "不可修改" in error_msg


class TestVR004ErrorMessages:
    """测试 VR-004 错误消息质量"""

    def test_error_message_includes_rule_id(self):
        """测试：错误消息包含 VR-004 规则ID"""
        source = """
page = "invalid"
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "VR-004" in str(exc_info.value)

    def test_error_message_mentions_readonly(self):
        """测试：错误消息提到只读"""
        source = """
env = "invalid"
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        error_msg = str(exc_info.value)
        assert "只读" in error_msg or "readonly" in error_msg.lower()

    def test_error_message_lists_system_variables(self):
        """测试：错误消息列出系统变量"""
        source = """
response = "invalid"
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        error_msg = str(exc_info.value)
        # 应该提到 page, env, response
        assert "page" in error_msg or "env" in error_msg or "response" in error_msg
