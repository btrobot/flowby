"""
测试服务命名空间 (v3.1+)

测试 Python-style 服务调用语法:
- random 命名空间
- http 命名空间
- 表达式中使用
- 保留字保护
- 废弃警告
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from textwrap import dedent
from registration_system.dsl.lexer import Lexer
from registration_system.dsl.parser import Parser
from registration_system.dsl.interpreter import Interpreter
from registration_system.dsl.context import ExecutionContext
from registration_system.dsl.errors import ExecutionError


def parse_script(script: str):
    """辅助函数：词法分析+语法分析"""
    lexer = Lexer()
    # 去除缩进，避免测试脚本中的Python缩进干扰DSL解析
    tokens = lexer.tokenize(dedent(script))
    parser = Parser()
    return parser.parse(tokens)


class TestRandomNamespace:
    """测试 random 命名空间"""

    def test_random_email(self):
        """测试 random.email()"""
        script = '''
        let email = random.email()
        assert email contains "@"
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证邮箱格式
        email = interpreter.symbol_table.get("email", 0)
        assert "@" in email
        assert isinstance(email, str)

    def test_random_password_default(self):
        """测试 random.password() 默认参数"""
        script = '''
        let pwd = random.password()
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证密码长度（默认 12）
        pwd = interpreter.symbol_table.get("pwd", 0)
        assert len(pwd) == 12
        assert isinstance(pwd, str)

    def test_random_password_with_length(self):
        """测试 random.password(16)"""
        script = '''
        let pwd = random.password(16)
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证密码长度
        pwd = interpreter.symbol_table.get("pwd", 0)
        assert len(pwd) == 16

    def test_random_password_no_special(self):
        """测试 random.password(special: False)"""
        script = '''
        let pwd = random.password(20, False)
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证密码不包含特殊字符
        pwd = interpreter.symbol_table.get("pwd", 0)
        import string
        assert all(c in string.ascii_letters + string.digits for c in pwd)

    def test_random_username(self):
        """测试 random.username()"""
        script = '''
        let username = random.username()
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证用户名存在
        username = interpreter.symbol_table.get("username", 0)
        assert isinstance(username, str)
        assert len(username) > 0

    def test_random_phone(self):
        """测试 random.phone()"""
        script = '''
        let phone = random.phone()
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证手机号存在
        phone = interpreter.symbol_table.get("phone", 0)
        assert isinstance(phone, str)
        assert len(phone) > 0

    def test_random_number(self):
        """测试 random.number(min, max)"""
        script = '''
        let dice = random.number(1, 6)
        assert dice >= 1
        assert dice <= 6
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证数字范围
        dice = interpreter.symbol_table.get("dice", 0)
        assert 1 <= dice <= 6

    def test_random_number_invalid_range(self):
        """测试 random.number() 无效范围"""
        script = '''
        let x = random.number(10, 5)
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)

        # 应该抛出ExecutionError（包装了ValueError）
        with pytest.raises(ExecutionError, match="min_val.*must be <= max_val"):
            interpreter.execute(ast)

    def test_random_uuid(self):
        """测试 random.uuid()"""
        script = '''
        let user_id = random.uuid()
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证 UUID 格式
        user_id = interpreter.symbol_table.get("user_id", 0)
        assert isinstance(user_id, str)
        assert len(user_id) == 36  # UUID v4 长度
        assert user_id.count('-') == 4


class TestHttpNamespace:
    """测试 http 命名空间"""

    @patch('requests.get')
    def test_http_get_json(self, mock_get):
        """测试 http.get() 返回 JSON (v4.0: HttpResponse对象)"""
        # Mock 响应
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {'name': 'Alice', 'age': 30}
        mock_get.return_value = mock_response

        script = '''
        let response = http.get("https://api.example.com/users")
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证返回值 (v4.0: HttpResponse对象)
        response = interpreter.symbol_table.get("response", 0)
        assert response.ok is True
        assert response.data == {'name': 'Alice', 'age': 30}
        assert response.status_code == 200

        # 验证 mock 调用
        mock_get.assert_called_once_with(
            "https://api.example.com/users",
            timeout=30,
            headers=None
        )

    @patch('requests.get')
    def test_http_get_with_headers(self, mock_get):
        """测试 http.get() 带请求头 (v3.2: 使用位置参数)"""
        mock_response = Mock()
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {'status': 'ok'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        script = '''
        let response = http.get("https://api.example.com/data", 30, {"Authorization": "Bearer token123"})
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证 headers 传递
        mock_get.assert_called_once_with(
            "https://api.example.com/data",
            timeout=30,
            headers={'Authorization': 'Bearer token123'}
        )

    @patch('requests.post')
    def test_http_post(self, mock_post):
        """测试 http.post() (v3.2: 使用位置参数)"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {'id': 123, 'created': True}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        script = '''
        let result = http.post("https://api.example.com/users", {name: "Bob", email: "bob@example.com"})
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证返回值 (v4.0: HttpResponse对象)
        result = interpreter.symbol_table.get("result", 0)
        assert result.ok is True
        assert result.data['id'] == 123
        assert result.data['created'] is True
        assert result.status_code == 201

        # 验证 body 传递
        mock_post.assert_called_once_with(
            "https://api.example.com/users",
            json={'name': 'Bob', 'email': 'bob@example.com'},
            timeout=30,
            headers=None
        )

    @patch('requests.put')
    def test_http_put(self, mock_put):
        """测试 http.put()"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {'updated': True}
        mock_response.raise_for_status = Mock()
        mock_put.return_value = mock_response

        script = '''
        let result = http.put("https://api.example.com/users/123", {})
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证返回值 (v4.0: HttpResponse对象)
        result = interpreter.symbol_table.get("result", 0)
        assert result.ok is True
        assert result.data['updated'] is True

    @patch('requests.delete')
    def test_http_delete(self, mock_delete):
        """测试 http.delete()"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {'deleted': True}
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response

        script = '''
        let result = http.delete("https://api.example.com/users/123")
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证返回值 (v4.0: HttpResponse对象)
        result = interpreter.symbol_table.get("result", 0)
        assert result.ok is True
        assert result.data['deleted'] is True

    @patch('requests.patch')
    def test_http_patch(self, mock_patch):
        """测试 http.patch()"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {'patched': True}
        mock_response.raise_for_status = Mock()
        mock_patch.return_value = mock_response

        script = '''
        let result = http.patch("https://api.example.com/users/123", {})
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证返回值 (v4.0: HttpResponse对象)
        result = interpreter.symbol_table.get("result", 0)
        assert result.ok is True
        assert result.data['patched'] is True

    @patch('requests.get')
    def test_http_get_error(self, mock_get):
        """测试 HTTP 请求失败 (v3.2+: 抛出异常而非返回错误对象)"""
        # Mock 抛出异常
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        script = '''
        let response = http.get("https://invalid-url.com")
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)

        # v3.2+: 网络错误抛出 ExecutionError 异常
        with pytest.raises(ExecutionError, match="(调用方法失败|Connection error)"):
            interpreter.execute(ast)


class TestServiceInExpressions:
    """测试在表达式中使用服务"""

    def test_service_in_array_literal(self):
        """测试在数组字面量中使用"""
        script = '''
        let emails = [random.email(), random.email()]
        assert emails.length() == 2
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        emails = interpreter.symbol_table.get("emails", 0)
        assert len(emails) == 2
        assert all("@" in email for email in emails)

    def test_service_in_object_literal(self):
        """测试在对象字面量中使用"""
        script = '''
        let user = {
            id: random.uuid(),
            email: random.email()
        }
        assert user.id != None
        assert user.email contains "@"
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        user = interpreter.symbol_table.get("user", 0)
        assert 'id' in user
        assert 'email' in user
        assert "@" in user['email']

    def test_service_in_string_interpolation(self):
        """测试在字符串插值中使用"""
        script = '''
        let message = f"Generated email: {random.email()}"
        assert message contains "Generated email:"
        assert message contains "@"
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        message = interpreter.symbol_table.get("message", 0)
        assert "Generated email:" in message
        assert "@" in message


class TestReservedWords:
    """测试保留字保护"""

    def test_cannot_define_random_variable(self):
        """测试不能定义 random 变量"""
        script = '''
        let random = 10
        '''

        # 应该在解析阶段抛出错误
        with pytest.raises(RuntimeError, match="不能定义变量 'random'.*保留的命名空间"):
            ast = parse_script(script)

    def test_cannot_define_http_variable(self):
        """测试不能定义 http 变量"""
        script = '''
        let http = "test"
        '''

        # 应该在解析阶段抛出错误
        with pytest.raises(RuntimeError, match="不能定义变量 'http'.*保留的命名空间"):
            ast = parse_script(script)

    def test_cannot_define_math_variable(self):
        """测试不能定义 Math 变量（已有保留字）"""
        script = '''
        let Math = 100
        '''

        # 应该在解析阶段抛出错误
        with pytest.raises(RuntimeError, match="不能定义变量 'Math'.*保留的命名空间"):
            ast = parse_script(script)


class TestDeprecationWarning:
    """测试废弃警告"""


class TestEdgeCases:
    """测试边界情况"""

    def test_password_invalid_length(self):
        """测试 password() 无效长度"""
        script = '''
        let pwd = random.password(-5)
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)

        with pytest.raises(ExecutionError, match="Password length must be positive"):
            interpreter.execute(ast)

    def test_chained_method_calls(self):
        """测试链式调用"""
        script = '''
        let uppercase_email = random.email().toUpperCase()
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证结果是大写的
        uppercase_email = interpreter.symbol_table.get("uppercase_email", 0)
        assert uppercase_email.isupper()
        assert "@" in uppercase_email.lower()

    @patch('requests.get')
    def test_http_timeout_parameter(self, mock_get):
        """测试 HTTP timeout 参数"""
        mock_response = Mock()
        mock_response.headers = {'content-type': 'text/plain'}
        mock_response.text = "OK"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        script = '''
        let response = http.get(url: "https://api.example.com", timeout: 5)
        '''
        ast = parse_script(script)

        context = ExecutionContext('test-task')
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证 timeout 传递
        mock_get.assert_called_once_with(
            "https://api.example.com",
            timeout=5,
            headers=None
        )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
