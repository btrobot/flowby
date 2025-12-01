"""
HttpProvider 单元测试
使用 pytest 和 responses 库进行测试
"""

import pytest
import responses
from requests.exceptions import Timeout, ConnectionError
from flowby.config.schema import ServicesConfig, GlobalSettings, ProviderConfig
from flowby.services.registry import ServiceRegistry


@pytest.fixture
def registry():
    """创建测试用的 ServiceRegistry"""
    services_config = ServicesConfig(
        settings=GlobalSettings(timeout=30000, retry_count=3, retry_delay=1000),
        providers={
            "http": ProviderConfig(
                type="http",
                config={
                    "default_timeout": 30,
                    "default_headers": {"User-Agent": "DSL-Test/1.0", "Accept": "application/json"},
                    "verify_ssl": True,
                },
            )
        },
    )
    registry = ServiceRegistry(services_config)
    registry.initialize()
    yield registry
    registry.close()


@pytest.fixture
def http_provider(registry):
    """获取 HttpProvider 实例"""
    return registry.providers["http"]


class TestHttpProviderBasics:
    """测试 HttpProvider 基础功能"""

    def test_provider_registration(self, registry):
        """测试提供者注册"""
        assert "http" in registry.providers
        provider = registry.providers["http"]
        assert provider.name == "http"
        assert provider.default_timeout == 30
        assert provider.verify_ssl is True

    def test_get_methods(self, http_provider):
        """测试 get_methods 返回所有支持的方法"""
        methods = http_provider.get_methods()
        assert "get" in methods
        assert "post" in methods
        assert "put" in methods
        assert "delete" in methods
        assert "patch" in methods
        assert "request" in methods

    def test_session_initialization(self, http_provider):
        """测试 Session 已正确初始化"""
        assert http_provider.session is not None
        assert "User-Agent" in http_provider.session.headers
        assert http_provider.session.headers["User-Agent"] == "DSL-Test/1.0"


class TestGetMethod:
    """测试 GET 方法"""

    @responses.activate
    def test_basic_get(self, registry):
        """测试基本 GET 请求"""
        responses.add(
            responses.GET,
            "https://api.example.com/users",
            json={"users": ["alice", "bob"]},
            status=200,
        )
        response = registry.call("http.get", url="https://api.example.com/users")
        assert response["status_code"] == 200
        assert response["ok"] is True
        assert response["data"] == {"users": ["alice", "bob"]}
        assert response["error"] is None

    @responses.activate
    def test_get_with_params(self, registry):
        """测试带查询参数的 GET 请求"""
        responses.add(
            responses.GET, "https://api.example.com/search", json={"results": []}, status=200
        )
        response = registry.call(
            "http.get", url="https://api.example.com/search", params={"q": "test", "limit": 10}
        )
        assert response["status_code"] == 200
        assert len(responses.calls) == 1
        assert "q=test" in responses.calls[0].request.url
        assert "limit=10" in responses.calls[0].request.url

    @responses.activate
    def test_get_with_custom_headers(self, registry):
        """测试自定义请求头"""
        responses.add(
            responses.GET, "https://api.example.com/protected", json={"data": "secret"}, status=200
        )
        response = registry.call(
            "http.get",
            url="https://api.example.com/protected",
            headers={"Authorization": "Bearer token123"},
        )
        assert response["status_code"] == 200
        assert len(responses.calls) == 1
        assert responses.calls[0].request.headers["Authorization"] == "Bearer token123"
        # 默认请求头也应该存在
        assert responses.calls[0].request.headers["User-Agent"] == "DSL-Test/1.0"


class TestPostMethod:
    """测试 POST 方法"""

    @responses.activate
    def test_post_json(self, registry):
        """测试 POST JSON 数据"""
        responses.add(
            responses.POST,
            "https://api.example.com/users",
            json={"id": 123, "name": "John"},
            status=201,
        )
        test_data = {"name": "John", "email": "john@example.com"}
        response = registry.call("http.post", url="https://api.example.com/users", json=test_data)
        assert response["status_code"] == 201
        assert response["ok"] is True
        assert len(responses.calls) == 1
        assert responses.calls[0].request.headers["Content-Type"] == "application/json"

    @responses.activate
    def test_post_form_data(self, registry):
        """测试 POST Form 数据"""
        responses.add(
            responses.POST, "https://api.example.com/login", json={"token": "abc123"}, status=200
        )
        response = registry.call(
            "http.post",
            url="https://api.example.com/login",
            data={"username": "user", "password": "pass"},
        )
        assert response["status_code"] == 200
        assert len(responses.calls) == 1
        assert (
            "application/x-www-form-urlencoded"
            in responses.calls[0].request.headers["Content-Type"]
        )


class TestOtherMethods:
    """测试其他 HTTP 方法"""

    @responses.activate
    def test_put_method(self, registry):
        """测试 PUT 请求"""
        responses.add(
            responses.PUT,
            "https://api.example.com/users/123",
            json={"id": 123, "updated": True},
            status=200,
        )
        response = registry.call(
            "http.put", url="https://api.example.com/users/123", json={"name": "Updated Name"}
        )
        assert response["status_code"] == 200
        assert response["ok"] is True

    @responses.activate
    def test_delete_method(self, registry):
        """测试 DELETE 请求"""
        responses.add(responses.DELETE, "https://api.example.com/users/123", status=204)
        response = registry.call("http.delete", url="https://api.example.com/users/123")
        assert response["status_code"] == 204
        assert response["ok"] is True

    @responses.activate
    def test_patch_method(self, registry):
        """测试 PATCH 请求"""
        responses.add(
            responses.PATCH,
            "https://api.example.com/users/123",
            json={"id": 123, "patched": True},
            status=200,
        )
        response = registry.call(
            "http.patch", url="https://api.example.com/users/123", json={"field": "value"}
        )
        assert response["status_code"] == 200
        assert response["ok"] is True

    @responses.activate
    def test_request_method_get(self, registry):
        """测试通用 request() 方法 - GET"""
        responses.add(
            responses.GET, "https://api.example.com/data", json={"data": "value"}, status=200
        )
        response = registry.call(
            "http.request", http_method="GET", url="https://api.example.com/data"
        )
        assert response["status_code"] == 200
        assert response["ok"] is True

    @responses.activate
    def test_request_method_post(self, registry):
        """测试通用 request() 方法 - POST"""
        responses.add(
            responses.POST, "https://api.example.com/data", json={"created": True}, status=201
        )
        response = registry.call(
            "http.request",
            http_method="POST",
            url="https://api.example.com/data",
            json={"key": "value"},
        )
        assert response["status_code"] == 201
        assert response["ok"] is True


class TestResponseParsing:
    """测试响应解析"""

    @responses.activate
    def test_json_response_parsing(self, registry):
        """测试 JSON 响应自动解析"""
        responses.add(
            responses.GET,
            "https://api.example.com/json",
            json={"key": "value", "number": 123},
            status=200,
        )
        response = registry.call("http.get", url="https://api.example.com/json")
        assert response["data"] is not None
        assert isinstance(response["data"], dict)
        assert response["data"]["key"] == "value"
        assert response["data"]["number"] == 123

    @responses.activate
    def test_non_json_response(self, registry):
        """测试非 JSON 响应"""
        responses.add(
            responses.GET,
            "https://api.example.com/text",
            body="Plain text response",
            status=200,
            content_type="text/plain",
        )
        response = registry.call("http.get", url="https://api.example.com/text")
        assert response["status_code"] == 200
        assert response["data"] is None
        assert response["text"] == "Plain text response"

    @responses.activate
    def test_empty_response(self, registry):
        """测试空响应"""
        responses.add(responses.DELETE, "https://api.example.com/resource", status=204)
        response = registry.call("http.delete", url="https://api.example.com/resource")
        assert response["status_code"] == 204
        assert response["ok"] is True
        assert response["data"] is None
        assert response["text"] == ""


class TestErrorHandling:
    """测试错误处理"""

    @responses.activate
    def test_http_404_error(self, registry):
        """测试 404 错误"""
        responses.add(
            responses.GET,
            "https://api.example.com/notfound",
            json={"error": "Not Found"},
            status=404,
        )
        response = registry.call("http.get", url="https://api.example.com/notfound")
        assert response["status_code"] == 404
        assert response["ok"] is False
        assert response["error"] is not None
        assert "HTTP 404" in response["error"]

    @responses.activate
    def test_http_500_error(self, registry):
        """测试 500 服务器错误"""
        responses.add(
            responses.GET,
            "https://api.example.com/error",
            json={"error": "Internal Server Error"},
            status=500,
        )
        response = registry.call("http.get", url="https://api.example.com/error")
        assert response["status_code"] == 500
        assert response["ok"] is False
        assert response["error"] is not None

    @responses.activate
    def test_connection_error(self, registry):
        """测试连接错误"""
        responses.add(
            responses.GET,
            "https://api.example.com/data",
            body=ConnectionError("Connection refused"),
        )
        response = registry.call("http.get", url="https://api.example.com/data")
        assert response["status_code"] == 0
        assert response["ok"] is False
        assert response["error"] is not None
        assert "无法连接到服务器" in response["error"]

    @responses.activate
    def test_timeout_error(self, registry):
        """测试超时错误"""
        responses.add(
            responses.GET, "https://api.example.com/slow", body=Timeout("Request timed out")
        )
        response = registry.call("http.get", url="https://api.example.com/slow")
        assert response["status_code"] == 0
        assert response["ok"] is False
        assert response["error"] is not None
        assert "请求超时" in response["error"]


class TestConfiguration:
    """测试配置功能"""

    def test_custom_timeout(self):
        """测试自定义超时配置"""
        services_config = ServicesConfig(
            settings=GlobalSettings(),
            providers={"http": ProviderConfig(type="http", config={"default_timeout": 60})},
        )
        registry = ServiceRegistry(services_config)
        registry.initialize()
        provider = registry.providers["http"]
        assert provider.default_timeout == 60
        registry.close()

    def test_custom_headers(self):
        """测试自定义默认请求头"""
        services_config = ServicesConfig(
            settings=GlobalSettings(),
            providers={
                "http": ProviderConfig(
                    type="http",
                    config={
                        "default_headers": {"X-Custom": "value", "User-Agent": "Custom-Agent/2.0"}
                    },
                )
            },
        )
        registry = ServiceRegistry(services_config)
        registry.initialize()
        provider = registry.providers["http"]
        assert provider.default_headers["X-Custom"] == "value"
        assert provider.default_headers["User-Agent"] == "Custom-Agent/2.0"
        registry.close()

    def test_ssl_verification_disabled(self):
        """测试禁用 SSL 验证"""
        services_config = ServicesConfig(
            settings=GlobalSettings(),
            providers={"http": ProviderConfig(type="http", config={"verify_ssl": False})},
        )
        registry = ServiceRegistry(services_config)
        registry.initialize()
        provider = registry.providers["http"]
        assert provider.verify_ssl is False
        registry.close()


class TestHeaderMerging:
    """测试请求头合并"""

    @responses.activate
    def test_headers_merge(self, registry):
        """测试请求头合并（自定义优先级高于默认）"""
        responses.add(responses.GET, "https://api.example.com/test", json={"ok": True}, status=200)
        response = registry.call(
            "http.get",
            url="https://api.example.com/test",
            headers={"User-Agent": "Override-Agent", "X-Custom": "test"},
        )
        assert response["status_code"] == 200
        assert len(responses.calls) == 1
        # 自定义请求头应该覆盖默认值
        assert responses.calls[0].request.headers["User-Agent"] == "Override-Agent"
        assert responses.calls[0].request.headers["X-Custom"] == "test"
        # 默认请求头中的其他字段应该保留
        assert responses.calls[0].request.headers["Accept"] == "application/json"


class TestAdvancedParameters:
    """测试高级参数"""

    @responses.activate
    def test_allow_redirects_parameter(self, registry):
        """测试 allow_redirects 参数"""
        # 这个测试仅验证参数可以传递，实际重定向行为由 requests 库处理
        responses.add(
            responses.GET, "https://api.example.com/redirect", json={"redirected": True}, status=200
        )
        response = registry.call(
            "http.get", url="https://api.example.com/redirect", allow_redirects=False
        )
        assert response["status_code"] == 200

    @responses.activate
    def test_custom_timeout_parameter(self, registry):
        """测试方法级别的超时参数"""
        responses.add(
            responses.GET, "https://api.example.com/data", json={"data": "value"}, status=200
        )
        # 超时参数应该可以在方法调用时指定
        response = registry.call("http.get", url="https://api.example.com/data", timeout=10)
        assert response["status_code"] == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
