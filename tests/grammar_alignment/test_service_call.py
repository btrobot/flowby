"""
Grammar Alignment Test: Service Call (Python-style)

Tests alignment between grammar/MASTER.md definitions and parser.py implementation.

Features tested:
- 8.1 Call Service (Python-style) - v3.1+

Reference: grammar/MASTER.md #8-Service Call
"""

import pytest
from unittest.mock import Mock, patch
from flowby.ast_nodes import (
    LetStatement,
    MethodCall,
    Program,
)
from flowby.interpreter import Interpreter
from flowby.context import ExecutionContext
from flowby.errors import ExecutionError


# ============================================================================
# Feature 8.1: Call Service (Python-style)
# ============================================================================


@pytest.mark.feature("8.1")
@pytest.mark.priority("high")
class Test8_1_PythonStyleServiceCall:
    """
    Test Python-style Service Call alignment with grammar/MASTER.md

    Grammar: SERVICE.method(args)
    Method: _eval_method_call()
    Status: ✅ v3.1+
    """

    # ========================================================================
    # Random Namespace
    # ========================================================================

    def test_random_email(self, parse):
        """Test random.email() service call"""
        ast = parse("let email = random.email()")

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert ast[0].name == "email"
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.object.name == "random"
        assert ast[0].value.method_name == "email"

    def test_random_password(self, parse):
        """Test random.password() with positional parameters"""
        ast = parse("let pwd = random.password(16, True)")

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert ast[0].name == "pwd"
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.object.name == "random"
        assert ast[0].value.method_name == "password"

    def test_random_password_named_params(self, parse):
        """Test random.password() with named parameters (v3.2+)"""
        ast = parse("let pwd = random.password(length=16, special=True)")

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.method_name == "password"

    def test_random_username(self, parse):
        """Test random.username() service call"""
        ast = parse("let user = random.username()")

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.object.name == "random"
        assert ast[0].value.method_name == "username"

    def test_random_phone(self, parse):
        """Test random.phone() with named parameter"""
        ast = parse('let phone = random.phone(locale="zh_CN")')

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.method_name == "phone"

    def test_random_number(self, parse):
        """Test random.number() with positional parameters"""
        ast = parse("let num = random.number(1, 100)")

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.object.name == "random"
        assert ast[0].value.method_name == "number"

    def test_random_uuid(self, parse):
        """Test random.uuid() service call"""
        ast = parse("let id = random.uuid()")

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.object.name == "random"
        assert ast[0].value.method_name == "uuid"

    # ========================================================================
    # HTTP Namespace
    # ========================================================================

    def test_http_get(self, parse):
        """Test http.get() service call"""
        ast = parse('let response = http.get(url="https://api.example.com")')

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert ast[0].name == "response"
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.object.name == "http"
        assert ast[0].value.method_name == "get"

    def test_http_post(self, parse):
        """Test http.post() with body parameter"""
        ast = parse('let result = http.post(url="https://api.example.com", body={name: "test"})')

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.object.name == "http"
        assert ast[0].value.method_name == "post"

    def test_http_put(self, parse):
        """Test http.put() service call"""
        ast = parse('let result = http.put(url="https://api.example.com", body={id: 1})')

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.method_name == "put"

    def test_http_delete(self, parse):
        """Test http.delete() service call"""
        ast = parse('let result = http.delete(url="https://api.example.com/users/1")')

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.method_name == "delete"

    def test_http_patch(self, parse):
        """Test http.patch() service call"""
        ast = parse(
            'let result = http.patch(url="https://api.example.com", body={status: "active"})'
        )

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.method_name == "patch"

    # ========================================================================
    # Advanced Usage
    # ========================================================================

    def test_service_call_in_expression(self, parse):
        """Test service call used in expression"""
        ast = parse("let uppercase = random.email().toUpperCase()")

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        # Should have chained method calls
        assert isinstance(ast[0].value, MethodCall)

    def test_service_call_in_object_literal(self, parse):
        """Test service call in object literal"""
        ast = parse("let user = {email: random.email(), password: random.password(16)}")

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert ast[0].name == "user"

    def test_service_call_in_array_literal(self, parse):
        """Test service call in array literal"""
        ast = parse("let emails = [random.email(), random.email(), random.email()]")

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert ast[0].name == "emails"

    def test_service_call_with_variable_url(self, parse):
        """Test service call with variable in parameter"""
        code = """let base_url = "https://api.example.com"
let response = http.get(url=base_url + "/users")"""
        ast = parse(code)

        assert len(ast) == 2
        assert isinstance(ast[1], LetStatement)
        assert isinstance(ast[1].value, MethodCall)

    def test_service_call_mixed_params(self, parse):
        """Test service call with mixed positional and named parameters (v3.2+)"""
        ast = parse("let pwd = random.password(16, special=True)")

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)

    def test_service_call_multiple_named_params(self, parse):
        """Test service call with multiple named parameters (v3.2+)"""
        ast = parse(
            'let response = http.post(url="https://api.example.com", body={data: "test"}, timeout=5000)'
        )

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.method_name == "post"

    def test_service_call_in_string_interpolation(self, parse):
        """Test service call result in string interpolation"""
        ast = parse('let message = f"Your email is {random.email()}"')

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert ast[0].name == "message"

    def test_http_get_with_headers(self, parse):
        """Test HTTP GET with headers parameter"""
        ast = parse(
            'let response = http.get(url="https://api.example.com", headers={Authorization: "Bearer token"})'
        )

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)

    def test_http_post_with_json(self, parse):
        """Test HTTP POST with json parameter"""
        ast = parse(
            'let response = http.post(url="https://api.example.com", json={email: "test@example.com"})'
        )

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.method_name == "post"

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_service_call_no_params(self, parse):
        """Test service call with no parameters"""
        ast = parse("let id = random.uuid()")

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)

    def test_service_call_only_named_params(self, parse):
        """Test service call with only named parameters"""
        ast = parse("let pwd = random.password(length=20, special=False, numeric=True)")

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)

    def test_service_call_complex_expression(self, parse):
        """Test service call with complex expression as parameter"""
        code = """let base = "https://api.example.com"
let path = "/users"
let response = http.get(url=base + path + "?page=1")"""
        ast = parse(code)

        assert len(ast) == 3
        assert isinstance(ast[2], LetStatement)
        assert isinstance(ast[2].value, MethodCall)

    def test_service_call_multiline(self, parse):
        """Test service call with multiline formatting"""
        code = """let response = http.post(
    url: "https://api.example.com",
    body: {name: "test", email: "test@example.com"}
)"""
        ast = parse(code)

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.method_name == "post"

    def test_service_call_multiline_trailing_comma(self, parse):
        """Test service call with multiline formatting and trailing comma"""
        code = """let response = http.get(
    url: "https://api.example.com",
    headers: {Authorization: "Bearer token"},
)"""
        ast = parse(code)

        assert len(ast) == 1
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[0].value, MethodCall)
        assert ast[0].value.method_name == "get"


# ============================================================================
# Feature 8.1: Execution Validation
# ============================================================================


@pytest.mark.feature("8.1")
@pytest.mark.priority("high")
class Test8_1_ExecutionValidation:
    """
    Test Python-style Service Call execution validation

    验证服务调用不仅能正确解析，还能正确执行。
    这些测试确保语法对齐测试覆盖完整的解析+执行流程。

    Coverage:
    - HttpResponse 接口验证
    - 运行时类型检查
    - 错误处理验证
    - 实际执行结果检查
    """

    @staticmethod
    def _make_program(statements):
        """辅助函数：将语句列表包装为 Program 对象"""
        if isinstance(statements, Program):
            return statements
        return Program(statements=statements, line=1)

    # ========================================================================
    # HTTP Namespace - Response Interface Validation
    # ========================================================================

    @patch("requests.get")
    def test_http_get_returns_response_object(self, mock_get, parse):
        """验证 http.get() 返回 HttpResponse 对象 (v4.0)"""
        # Mock 响应
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response

        # 解析并执行
        ast = parse('let response = http.get(url="https://api.example.com")')
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        # 验证返回 HttpResponse 对象
        response = interpreter.symbol_table.get("response", 0)
        assert hasattr(response, "ok"), "HttpResponse 必须有 .ok 属性"
        assert hasattr(response, "data"), "HttpResponse 必须有 .data 属性"
        assert hasattr(response, "status_code"), "HttpResponse 必须有 .status_code 属性"
        assert hasattr(response, "headers"), "HttpResponse 必须有 .headers 属性"

        # 验证属性值
        assert response.ok is True
        assert response.data == {"status": "ok"}
        assert response.status_code == 200

    @patch("requests.post")
    def test_http_post_with_body_parameter(self, mock_post, parse):
        """验证 http.post() 使用 body 参数（非 json）"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 201
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"id": 1}
        mock_post.return_value = mock_response

        # 使用 body 参数
        ast = parse('let result = http.post(url="https://api.example.com", body={name: "test"})')
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        # 验证 mock 调用使用了 json 参数（内部映射）
        mock_post.assert_called_once_with(
            "https://api.example.com", json={"name": "test"}, timeout=30, headers=None
        )

        # 验证返回值
        result = interpreter.symbol_table.get("result", 0)
        assert result.ok is True
        assert result.data["id"] == 1

    @patch("requests.get")
    def test_http_error_returns_failed_response(self, mock_get, parse):
        """验证 HTTP 错误抛出 ExecutionError 异常（v3.2+ 行为）"""
        import requests

        mock_get.side_effect = requests.exceptions.RequestException("Connection timeout")

        # 执行应该抛出 ExecutionError
        ast = parse('let response = http.get(url="https://invalid.com")')
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)

        # v3.2+: HTTP 网络错误抛出异常
        with pytest.raises(ExecutionError, match="(调用方法失败|Connection timeout)"):
            interpreter.execute(program)

    @patch("requests.post")
    def test_multiline_http_call_execution(self, mock_post, parse):
        """验证多行 HTTP 调用能够正确执行"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        # 多行格式
        code = """let response = http.post(
    url: "https://api.example.com",
    body: {
        name: "test",
        email: "test@example.com"
    },
    timeout: 10
)"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        # 验证参数传递正确
        mock_post.assert_called_once_with(
            "https://api.example.com",
            json={"name": "test", "email": "test@example.com"},
            timeout=10,
            headers=None,
        )

        # 验证返回值
        response = interpreter.symbol_table.get("response", 0)
        assert response.ok is True
        assert response.data["success"] is True

    # ========================================================================
    # Random Namespace - Execution Validation
    # ========================================================================

    def test_random_email_returns_valid_email(self, parse):
        """验证 random.email() 返回有效的邮箱格式"""
        ast = parse("let email = random.email()")
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        email = interpreter.symbol_table.get("email", 0)
        assert isinstance(email, str), "email() 必须返回字符串"
        assert "@" in email, "邮箱必须包含 @ 符号"
        assert "." in email, "邮箱必须包含域名后缀"

    def test_random_password_with_parameters(self, parse):
        """验证 random.password() 参数能够正确影响结果"""
        ast = parse("let pwd = random.password(20, False)")
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        pwd = interpreter.symbol_table.get("pwd", 0)
        assert isinstance(pwd, str), "password() 必须返回字符串"
        assert len(pwd) == 20, "密码长度必须符合参数指定"

        # 验证不包含特殊字符
        import string

        assert all(
            c in string.ascii_letters + string.digits for c in pwd
        ), "special=False 时密码不应包含特殊字符"

    def test_random_uuid_returns_valid_format(self, parse):
        """验证 random.uuid() 返回有效的 UUID 格式"""
        ast = parse("let id = random.uuid()")
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        uuid = interpreter.symbol_table.get("id", 0)
        assert isinstance(uuid, str), "uuid() 必须返回字符串"
        assert len(uuid) == 36, "UUID 长度必须是 36"
        assert uuid.count("-") == 4, "UUID 必须包含 4 个连字符"

    # ========================================================================
    # Integration Tests - Complex Scenarios
    # ========================================================================

    @patch("requests.post")
    def test_http_response_in_conditional(self, mock_post, parse):
        """验证 HttpResponse 对象可用于条件判断"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"created": True}
        mock_post.return_value = mock_response

        code = """
let response = http.post(url: "https://api.example.com", body: {})
let success = False
if response.ok:
    success = True
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        # 验证条件判断能够访问 .ok 属性
        success = interpreter.symbol_table.get("success", 0)
        assert success is True, "条件判断应该能够访问 response.ok"

    @patch("requests.get")
    def test_http_response_data_access(self, mock_get, parse):
        """验证 HttpResponse.data 可以访问嵌套属性"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"user": {"name": "Alice", "email": "alice@example.com"}}
        mock_get.return_value = mock_response

        code = """
let response = http.get(url: "https://api.example.com/user")
let user_email = ""
if response.ok:
    user_email = response.data.user.email
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        # 验证嵌套属性访问
        user_email = interpreter.symbol_table.get("user_email", 0)
        assert user_email == "alice@example.com", "应该能够访问嵌套的响应数据"
