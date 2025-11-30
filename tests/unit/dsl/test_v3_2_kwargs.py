"""
v3.2 命名参数测试

测试 Python-style 命名参数语法
"""

import pytest
from textwrap import dedent
from registration_system.dsl.lexer import Lexer
from registration_system.dsl.parser import Parser
from registration_system.dsl.context import ExecutionContext
from registration_system.dsl.interpreter import Interpreter
from registration_system.dsl.errors import ExecutionError


def parse_script(script: str):
    """Helper function: Lexer + Parser"""
    lexer = Lexer()
    tokens = lexer.tokenize(dedent(script))
    parser = Parser()
    return parser.parse(tokens)


class TestNamedParameters:
    """测试命名参数功能"""

    def test_random_password_with_named_params(self):
        """测试使用命名参数调用 random.password"""
        script = '''
        let pwd = random.password(length=16, special=True)
        assert pwd.length() == 16
        '''
        ast = parse_script(script)
        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        pwd = interpreter.symbol_table.get("pwd", 0)
        assert len(pwd) == 16

    def test_random_password_mixed_params(self):
        """测试混合参数（位置+命名）"""
        script = '''
        let pwd = random.password(16, special=True)
        assert pwd.length() == 16
        '''
        ast = parse_script(script)
        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        pwd = interpreter.symbol_table.get("pwd", 0)
        assert len(pwd) == 16

    def test_random_number_with_named_params(self):
        """测试 random.number 使用命名参数"""
        script = '''
        let num = random.number(min_val=1, max_val=10)
        assert num >= 1
        assert num <= 10
        '''
        ast = parse_script(script)
        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        num = interpreter.symbol_table.get("num", 0)
        assert 1 <= num <= 10

    def test_random_phone_with_named_param(self):
        """测试 random.phone 使用命名参数"""
        script = '''
        let phone = random.phone(locale="zh_CN")
        assert phone != None
        '''
        ast = parse_script(script)
        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        phone = interpreter.symbol_table.get("phone", 0)
        assert phone is not None

    def test_backward_compatible_positional_params(self):
        """测试向后兼容：仍然支持位置参数"""
        script = '''
        let pwd = random.password(12, False)
        assert pwd.length() == 12
        '''
        ast = parse_script(script)
        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        pwd = interpreter.symbol_table.get("pwd", 0)
        assert len(pwd) == 12

    def test_named_params_in_array_literal(self):
        """测试在数组字面量中使用命名参数"""
        script = '''
        let passwords = [
            random.password(length=8, special=False),
            random.password(length=12, special=True),
            random.password(length=16, special=True)
        ]
        assert passwords.length() == 3
        assert passwords[0].length() == 8
        assert passwords[1].length() == 12
        assert passwords[2].length() == 16
        '''
        ast = parse_script(script)
        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        passwords = interpreter.symbol_table.get("passwords", 0)
        assert len(passwords) == 3
        assert len(passwords[0]) == 8
        assert len(passwords[1]) == 12
        assert len(passwords[2]) == 16

    def test_named_params_in_object_literal(self):
        """测试在对象字面量中使用命名参数"""
        script = '''
        let user = {
            email: random.email(),
            password: random.password(length=16, special=True),
            username: random.username()
        }
        assert user.email != None
        assert user.password.length() == 16
        assert user.username != None
        '''
        ast = parse_script(script)
        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        user = interpreter.symbol_table.get("user", 0)
        assert user["email"] is not None
        assert len(user["password"]) == 16
        assert user["username"] is not None

    def test_named_params_in_string_interpolation(self):
        """测试在字符串插值中使用命名参数"""
        script = '''
        let message = f"Generated password: {random.password(length=10, special=False)}"
        log message
        '''
        ast = parse_script(script)
        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        message = interpreter.symbol_table.get("message", 0)
        assert "Generated password:" in message
        # 提取密码部分（最后10个字符应该是密码）
        assert len(message) > 20  # "Generated password: " + 10个字符

    def test_positional_after_named_raises_error(self):
        """测试位置参数在命名参数之后应该报错"""
        script = '''
        let pwd = random.password(special=True, 16)
        '''
        with pytest.raises(Exception) as exc_info:
            ast = parse_script(script)

        # 应该包含错误信息
        assert "位置参数" in str(exc_info.value) or "PARAMETER" in str(exc_info.value)

    def test_named_params_with_expressions(self):
        """测试命名参数使用表达式作为值"""
        script = '''
        let base_length = 10
        let pwd = random.password(length=base_length + 6, special=True)
        assert pwd.length() == 16
        '''
        ast = parse_script(script)
        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        pwd = interpreter.symbol_table.get("pwd", 0)
        assert len(pwd) == 16


class TestBuiltinFunctionsWithKwargs:
    """测试内置函数的命名参数支持"""

    def test_builtin_functions_still_work(self):
        """测试内置函数仍然正常工作（向后兼容）"""
        script = '''
        let num = Number("42")
        assert num == 42
        '''
        ast = parse_script(script)
        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        num = interpreter.symbol_table.get("num", 0)
        assert num == 42


class TestMethodChaining:
    """测试链式调用与命名参数"""

    def test_chained_method_with_kwargs(self):
        """测试命名参数调用后的链式调用"""
        script = '''
        let email = random.email()
        let upper_email = email.toUpperCase()
        assert upper_email contains "@"
        '''
        ast = parse_script(script)
        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        upper_email = interpreter.symbol_table.get("upper_email", 0)
        assert "@" in upper_email
        assert upper_email.isupper()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
