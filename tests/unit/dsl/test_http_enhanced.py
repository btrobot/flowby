"""
HTTP命名空间完善测试 (v3.2+)

测试覆盖:
1. 所有HTTP方法 (GET/POST/PUT/DELETE/PATCH)
2. 错误场景 (超时、网络错误、HTTP状态码)
3. Headers传递
4. Body序列化
5. 响应格式 (JSON/Text)
6. v3.2 命名参数语法
7. 自定义timeout参数
"""

import pytest
from unittest.mock import Mock, patch
from textwrap import dedent
import requests

from flowby.lexer import Lexer
from flowby.parser import Parser
from flowby.context import ExecutionContext
from flowby.interpreter import Interpreter
from flowby.errors import ExecutionError


def parse_script(script: str):
    """辅助函数：词法分析+语法分析"""
    lexer = Lexer()
    tokens = lexer.tokenize(dedent(script))
    parser = Parser()
    return parser.parse(tokens)


class TestHttpGetMethod:
    """测试 HTTP GET 方法"""

    @patch("requests.get")
    def test_get_json_response(self, mock_get):
        """测试 GET 请求返回 JSON"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"id": 1, "name": "Alice"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        script = """
        let response = http.get("https://api.example.com/users/1")
        assert response.id == 1
        assert response.name == "Alice"
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        mock_get.assert_called_once_with(
            "https://api.example.com/users/1", timeout=30, headers=None
        )

    @patch("requests.get")
    def test_get_text_response(self, mock_get):
        """测试 GET 请求返回纯文本"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "Hello, World!"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        script = """
        let response = http.get("https://example.com/hello.txt")
        assert response == "Hello, World!"
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

    @patch("requests.get")
    def test_get_html_response(self, mock_get):
        """测试 GET 请求返回 HTML"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "text/html"}
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        script = """
        let response = http.get("https://example.com")
        assert response contains "<html>"
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

    @patch("requests.get")
    def test_get_with_custom_timeout(self, mock_get):
        """测试 GET 请求自定义超时时间"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": "ok"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        script = """
        let response = http.get("https://api.example.com/slow", 60)
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证 timeout 参数
        mock_get.assert_called_once_with("https://api.example.com/slow", timeout=60, headers=None)

    @patch("requests.get")
    def test_get_with_headers(self, mock_get):
        """测试 GET 请求带请求头"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"authorized": True}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        script = """
        let auth_headers = {"Authorization": "Bearer token123", "User-Agent": "DSL/3.2"}
        let response = http.get("https://api.example.com/protected", 30, auth_headers)
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证 headers 传递
        mock_get.assert_called_once_with(
            "https://api.example.com/protected",
            timeout=30,
            headers={"Authorization": "Bearer token123", "User-Agent": "DSL/3.2"},
        )

    @patch("requests.get")
    def test_get_with_named_params(self, mock_get):
        """测试 GET 请求使用 v3.2 命名参数"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"status": "ok"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        script = """
        let response = http.get(url="https://api.example.com/data", timeout=10, headers={"X-Custom": "value"})
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        mock_get.assert_called_once_with(
            "https://api.example.com/data", timeout=10, headers={"X-Custom": "value"}
        )


class TestHttpPostMethod:
    """测试 HTTP POST 方法"""

    @patch("requests.post")
    def test_post_with_json_body(self, mock_post):
        """测试 POST 请求带 JSON body"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"id": 42, "created": True}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        script = """
        let user = {name: "Bob", email: "bob@example.com", age: 30}
        let response = http.post("https://api.example.com/users", user)
        assert response.id == 42
        assert response.created is True
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证 body 序列化
        mock_post.assert_called_once_with(
            "https://api.example.com/users",
            json={"name": "Bob", "email": "bob@example.com", "age": 30},
            timeout=30,
            headers=None,
        )

    @patch("requests.post")
    def test_post_with_nested_body(self, mock_post):
        """测试 POST 请求带嵌套对象 body"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        script = """
        let body = {
            user: {
                name: "Alice",
                profile: {
                    age: 25,
                    city: "Shanghai"
                }
            },
            tags: ["admin", "vip"]
        }
        let response = http.post("https://api.example.com/complex", body)
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证嵌套对象序列化
        expected_body = {
            "user": {"name": "Alice", "profile": {"age": 25, "city": "Shanghai"}},
            "tags": ["admin", "vip"],
        }
        mock_post.assert_called_once_with(
            "https://api.example.com/complex", json=expected_body, timeout=30, headers=None
        )

    @patch("requests.post")
    def test_post_with_headers(self, mock_post):
        """测试 POST 请求带请求头"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"id": 1}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        script = """
        let body = {title: "Test Post"}
        let headers = {"Content-Type": "application/json", "Authorization": "Bearer xyz"}
        let response = http.post("https://api.example.com/posts", body, 30, headers)
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        mock_post.assert_called_once_with(
            "https://api.example.com/posts",
            json={"title": "Test Post"},
            timeout=30,
            headers={"Content-Type": "application/json", "Authorization": "Bearer xyz"},
        )

    @patch("requests.post")
    def test_post_with_named_params(self, mock_post):
        """测试 POST 请求使用 v3.2 命名参数"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"created": True}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        script = """
        let response = http.post(url="https://api.example.com/items", body={name: "Item1", price: 99}, timeout=15, headers={"X-API-Key": "secret"})
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        mock_post.assert_called_once_with(
            "https://api.example.com/items",
            json={"name": "Item1", "price": 99},
            timeout=15,
            headers={"X-API-Key": "secret"},
        )


class TestHttpPutMethod:
    """测试 HTTP PUT 方法"""

    @patch("requests.put")
    def test_put_with_body(self, mock_put):
        """测试 PUT 请求带 body"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"updated": True}
        mock_response.raise_for_status = Mock()
        mock_put.return_value = mock_response

        script = """
        let updated_data = {name: "Alice Updated", status: "active"}
        let response = http.put("https://api.example.com/users/1", updated_data)
        assert response.updated is True
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        mock_put.assert_called_once_with(
            "https://api.example.com/users/1",
            json={"name": "Alice Updated", "status": "active"},
            timeout=30,
            headers=None,
        )

    @patch("requests.put")
    def test_put_with_named_params(self, mock_put):
        """测试 PUT 请求使用 v3.2 命名参数"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = Mock()
        mock_put.return_value = mock_response

        script = """
        let response = http.put(url="https://api.example.com/items/123", body={price: 199}, timeout=20)
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        mock_put.assert_called_once()


class TestHttpDeleteMethod:
    """测试 HTTP DELETE 方法"""

    @patch("requests.delete")
    def test_delete_basic(self, mock_delete):
        """测试 DELETE 请求"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"deleted": True}
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response

        script = """
        let response = http.delete("https://api.example.com/users/999")
        assert response.deleted is True
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        mock_delete.assert_called_once_with(
            "https://api.example.com/users/999", timeout=30, headers=None
        )

    @patch("requests.delete")
    def test_delete_with_headers(self, mock_delete):
        """测试 DELETE 请求带请求头"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response

        script = """
        let response = http.delete(url="https://api.example.com/resources/123", headers={"Authorization": "Bearer token"})
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        mock_delete.assert_called_once()


class TestHttpPatchMethod:
    """测试 HTTP PATCH 方法"""

    @patch("requests.patch")
    def test_patch_with_partial_update(self, mock_patch):
        """测试 PATCH 请求部分更新"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"patched": True}
        mock_response.raise_for_status = Mock()
        mock_patch.return_value = mock_response

        script = """
        let partial_update = {status: "inactive"}
        let response = http.patch("https://api.example.com/users/5", partial_update)
        assert response.patched is True
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        mock_patch.assert_called_once_with(
            "https://api.example.com/users/5", json={"status": "inactive"}, timeout=30, headers=None
        )


class TestHttpErrorHandling:
    """测试 HTTP 错误处理"""

    @patch("requests.get")
    def test_timeout_error(self, mock_get):
        """测试超时错误"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        script = """
        let response = http.get("https://slow-api.example.com/data")
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)

        with pytest.raises(ExecutionError, match="(调用方法失败|Request timed out)"):
            interpreter.execute(ast)

    @patch("requests.get")
    def test_connection_error(self, mock_get):
        """测试网络连接错误"""
        mock_get.side_effect = requests.exceptions.ConnectionError("Failed to connect")

        script = """
        let response = http.get("https://unreachable.example.com")
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)

        with pytest.raises(ExecutionError, match="(调用方法失败|Failed to connect)"):
            interpreter.execute(ast)

    @patch("requests.get")
    def test_http_404_error(self, mock_get):
        """测试 HTTP 404 错误"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        script = """
        let response = http.get("https://api.example.com/notfound")
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)

        with pytest.raises(ExecutionError, match="(调用方法失败|404)"):
            interpreter.execute(ast)

    @patch("requests.get")
    def test_http_500_error(self, mock_get):
        """测试 HTTP 500 服务器错误"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "500 Internal Server Error"
        )
        mock_get.return_value = mock_response

        script = """
        let response = http.get("https://api.example.com/broken")
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)

        with pytest.raises(ExecutionError, match="(调用方法失败|500)"):
            interpreter.execute(ast)

    @patch("requests.post")
    def test_post_timeout_error(self, mock_post):
        """测试 POST 超时错误"""
        mock_post.side_effect = requests.exceptions.Timeout("POST timeout")

        script = """
        let response = http.post("https://api.example.com/slow", {data: "test"})
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)

        with pytest.raises(ExecutionError, match="(调用方法失败|timeout)"):
            interpreter.execute(ast)

    @patch("requests.get")
    def test_invalid_json_response(self, mock_get):
        """测试无效 JSON 响应"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        script = """
        let response = http.get("https://api.example.com/bad-json")
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)

        # 应该捕获并包装为 ExecutionError
        with pytest.raises(ExecutionError, match="(调用方法失败|Invalid JSON)"):
            interpreter.execute(ast)


class TestHttpMixedParameterSyntax:
    """测试 v3.2 混合参数语法"""

    @patch("requests.get")
    def test_mixed_positional_and_named(self, mock_get):
        """测试混合使用位置参数和命名参数"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"data": "ok"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        script = """
        let response = http.get("https://api.example.com/mixed", timeout=15, headers={"X-Test": "value"})
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        mock_get.assert_called_once_with(
            "https://api.example.com/mixed", timeout=15, headers={"X-Test": "value"}
        )

    @patch("requests.post")
    def test_post_mixed_params(self, mock_post):
        """测试 POST 请求混合参数"""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"id": 1}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        script = """
        let response = http.post("https://api.example.com/items", {name: "Item"}, timeout=20)
        """
        ast = parse_script(script)

        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        mock_post.assert_called_once_with(
            "https://api.example.com/items", json={"name": "Item"}, timeout=20, headers=None
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
