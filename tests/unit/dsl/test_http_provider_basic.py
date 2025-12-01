"""
HttpProvider 基础结构测试

测试 HttpProvider 的核心功能：
1. HttpProvider 注册到 ServiceRegistry
2. 配置加载和应用
3. 默认配置验证
4. 自定义配置验证
"""

import pytest
from flowby.config.schema import ServicesConfig, GlobalSettings, ProviderConfig
from flowby.services.registry import ServiceRegistry


class TestHttpProviderRegistration:
    """测试 HttpProvider 注册"""

    @pytest.fixture
    def basic_services_config(self):
        """提供基础服务配置"""
        return ServicesConfig(
            settings=GlobalSettings(timeout=30000, retry_count=3, retry_delay=1000),
            providers={"http": ProviderConfig(type="http", config={})},
        )

    def test_http_provider_can_be_registered(self, basic_services_config):
        """测试 HttpProvider 可以被注册"""
        # Arrange & Act
        registry = ServiceRegistry(basic_services_config)
        registry.initialize()

        # Assert
        assert "http" in registry.providers, "http 提供者应该被注册"
        assert registry.providers["http"] is not None, "http 提供者实例不应为空"

        # Cleanup
        registry.close()

    def test_registry_creation_successful(self, basic_services_config):
        """测试 ServiceRegistry 创建成功"""
        # Act
        registry = ServiceRegistry(basic_services_config)
        registry.initialize()

        # Assert
        assert registry is not None, "ServiceRegistry 应该创建成功"
        assert hasattr(registry, "providers"), "应该有 providers 属性"
        assert isinstance(registry.providers, dict), "providers 应该是字典"

        # Cleanup
        registry.close()

    def test_http_provider_instance_exists(self, basic_services_config):
        """测试 HttpProvider 实例存在"""
        # Arrange
        registry = ServiceRegistry(basic_services_config)
        registry.initialize()

        # Act
        http_provider = registry.providers.get("http")

        # Assert
        assert http_provider is not None, "HttpProvider 实例应该存在"
        assert hasattr(http_provider, "get_methods"), "应该有 get_methods 方法"

        # Cleanup
        registry.close()


class TestHttpProviderMethods:
    """测试 HttpProvider 方法"""

    @pytest.fixture
    def http_provider(self):
        """提供 HttpProvider 实例"""
        config = ServicesConfig(
            settings=GlobalSettings(timeout=30000, retry_count=3, retry_delay=1000),
            providers={"http": ProviderConfig(type="http", config={})},
        )
        registry = ServiceRegistry(config)
        registry.initialize()
        provider = registry.providers.get("http")

        yield provider

        registry.close()

    def test_get_methods_returns_list(self, http_provider):
        """测试 get_methods 返回列表"""
        # Act
        methods = http_provider.get_methods()

        # Assert
        assert isinstance(methods, list), "get_methods 应该返回列表"
        assert len(methods) > 0, "应该至少有一个方法"

    def test_http_provider_has_required_methods(self, http_provider):
        """测试 HttpProvider 包含必要的方法"""
        # Act
        methods = http_provider.get_methods()

        # Assert
        # HTTP 方法应该包括常见的方法
        common_methods = ["get", "post", "put", "delete"]
        for method in common_methods:
            assert method in methods, f"应该支持 {method} 方法"


class TestHttpProviderDefaultConfig:
    """测试 HttpProvider 默认配置"""

    @pytest.fixture
    def http_provider_with_defaults(self):
        """提供使用默认配置的 HttpProvider 实例"""
        config = ServicesConfig(
            settings=GlobalSettings(timeout=30000, retry_count=3, retry_delay=1000),
            providers={"http": ProviderConfig(type="http", config={})},
        )
        registry = ServiceRegistry(config)
        registry.initialize()
        provider = registry.providers.get("http")

        yield provider

        registry.close()

    def test_default_timeout_exists(self, http_provider_with_defaults):
        """测试默认超时配置存在"""
        # Assert
        assert hasattr(
            http_provider_with_defaults, "default_timeout"
        ), "应该有 default_timeout 属性"
        assert http_provider_with_defaults.default_timeout is not None, "default_timeout 不应为空"

    def test_verify_ssl_has_default(self, http_provider_with_defaults):
        """测试 SSL 验证有默认值"""
        # Assert
        assert hasattr(http_provider_with_defaults, "verify_ssl"), "应该有 verify_ssl 属性"
        assert isinstance(http_provider_with_defaults.verify_ssl, bool), "verify_ssl 应该是布尔值"


class TestHttpProviderCustomConfig:
    """测试 HttpProvider 自定义配置"""

    @pytest.fixture
    def custom_config(self):
        """提供自定义配置"""
        return ServicesConfig(
            settings=GlobalSettings(timeout=30000, retry_count=3, retry_delay=1000),
            providers={
                "http": ProviderConfig(
                    type="http",
                    config={
                        "default_timeout": 60,
                        "default_headers": {
                            "User-Agent": "DSL-Test/1.0",
                            "Accept": "application/json",
                        },
                        "verify_ssl": False,
                    },
                )
            },
        )

    def test_custom_timeout_applied(self, custom_config):
        """测试自定义超时配置被应用"""
        # Arrange
        registry = ServiceRegistry(custom_config)
        registry.initialize()
        http_provider = registry.providers.get("http")

        # Assert
        assert http_provider.default_timeout == 60, "自定义超时应该是 60 秒"

        # Cleanup
        registry.close()

    def test_custom_headers_applied(self, custom_config):
        """测试自定义请求头被应用"""
        # Arrange
        registry = ServiceRegistry(custom_config)
        registry.initialize()
        http_provider = registry.providers.get("http")

        # Assert
        assert hasattr(http_provider, "default_headers"), "应该有 default_headers 属性"
        assert (
            http_provider.default_headers["User-Agent"] == "DSL-Test/1.0"
        ), "User-Agent 应该是 'DSL-Test/1.0'"
        assert (
            http_provider.default_headers["Accept"] == "application/json"
        ), "Accept 应该是 'application/json'"

        # Cleanup
        registry.close()

    def test_ssl_verification_disabled(self, custom_config):
        """测试 SSL 验证被禁用"""
        # Arrange
        registry = ServiceRegistry(custom_config)
        registry.initialize()
        http_provider = registry.providers.get("http")

        # Assert
        assert http_provider.verify_ssl is False, "SSL 验证应该被禁用"

        # Cleanup
        registry.close()

    def test_all_custom_configs_applied(self, custom_config):
        """测试所有自定义配置都被应用"""
        # Arrange
        registry = ServiceRegistry(custom_config)
        registry.initialize()
        http_provider = registry.providers.get("http")

        # Assert
        assert http_provider.default_timeout == 60, "超时配置应该正确"
        assert (
            http_provider.default_headers["User-Agent"] == "DSL-Test/1.0"
        ), "User-Agent 配置应该正确"
        assert http_provider.verify_ssl is False, "SSL 验证配置应该正确"

        # Cleanup
        registry.close()


class TestServiceRegistryLifecycle:
    """测试 ServiceRegistry 生命周期"""

    def test_registry_can_be_closed(self):
        """测试 Registry 可以被关闭"""
        # Arrange
        config = ServicesConfig(
            settings=GlobalSettings(timeout=30000, retry_count=3, retry_delay=1000),
            providers={"http": ProviderConfig(type="http", config={})},
        )
        registry = ServiceRegistry(config)
        registry.initialize()

        # Act & Assert
        # 应该可以调用 close 而不抛出异常
        registry.close()

    def test_registry_initialize_and_close_cycle(self):
        """测试 Registry 初始化和关闭循环"""
        # Arrange
        config = ServicesConfig(
            settings=GlobalSettings(timeout=30000, retry_count=3, retry_delay=1000),
            providers={"http": ProviderConfig(type="http", config={})},
        )

        # Act
        registry = ServiceRegistry(config)
        registry.initialize()

        # Assert
        assert "http" in registry.providers, "初始化后应该有 http 提供者"

        # Act - Close
        registry.close()

        # Assert - 关闭后应该能正常完成（不抛异常）


class TestHttpProviderConfiguration:
    """测试 HttpProvider 配置验证"""

    def test_empty_config_works(self):
        """测试空配置可以工作"""
        # Arrange
        config = ServicesConfig(
            settings=GlobalSettings(timeout=30000, retry_count=3, retry_delay=1000),
            providers={"http": ProviderConfig(type="http", config={})},
        )

        # Act
        registry = ServiceRegistry(config)
        registry.initialize()
        http_provider = registry.providers.get("http")

        # Assert
        assert http_provider is not None, "空配置应该能创建 HttpProvider"

        # Cleanup
        registry.close()

    def test_partial_config_works(self):
        """测试部分配置可以工作"""
        # Arrange
        config = ServicesConfig(
            settings=GlobalSettings(timeout=30000, retry_count=3, retry_delay=1000),
            providers={
                "http": ProviderConfig(
                    type="http",
                    config={
                        "default_timeout": 45
                        # 只配置超时，其他使用默认值
                    },
                )
            },
        )

        # Act
        registry = ServiceRegistry(config)
        registry.initialize()
        http_provider = registry.providers.get("http")

        # Assert
        assert http_provider is not None, "部分配置应该能创建 HttpProvider"
        assert http_provider.default_timeout == 45, "应该使用自定义超时"

        # Cleanup
        registry.close()
