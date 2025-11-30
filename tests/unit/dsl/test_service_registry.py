"""
Service Registry 单元测试

测试 ServiceRegistry 核心功能，包括：
1. 提供者注册和初始化
2. 服务调用 (call 方法)
3. 配置继承和覆盖
4. 错误处理
5. 资源管理
"""
import pytest
from typing import List, Any
from registration_system.dsl.config.schema import (
    ServicesConfig,
    GlobalSettings,
    ProviderConfig
)
from registration_system.dsl.services import (
    ServiceRegistry,
    ServiceProvider,
    ServiceError
)


class MockProvider(ServiceProvider):
    """测试用 Mock 提供者"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialized = False
        self.closed = False
        self.call_history = []

    def initialize(self):
        """初始化提供者"""
        self.initialized = True

    def get_methods(self) -> List[str]:
        """返回支持的方法列表"""
        return ['echo', 'add', 'fail', 'get_config']

    def echo(self, message: str) -> str:
        """回显消息"""
        self.call_history.append(('echo', {'message': message}))
        return message

    def add(self, a: int, b: int) -> int:
        """加法运算"""
        self.call_history.append(('add', {'a': a, 'b': b}))
        return a + b

    def fail(self) -> None:
        """故意失败的方法"""
        self.call_history.append(('fail', {}))
        raise ValueError("Intentional failure")

    def get_config(self, key: str) -> Any:
        """获取配置值"""
        self.call_history.append(('get_config', {'key': key}))
        return self.config.get(key)

    def close(self):
        """关闭提供者"""
        self.closed = True


class FailingProvider(ServiceProvider):
    """初始化失败的提供者"""

    def initialize(self):
        """初始化时故意失败"""
        raise RuntimeError("Init failed")

    def get_methods(self) -> List[str]:
        """返回空方法列表"""
        return []


class TestProviderRegistration:
    """测试提供者注册"""

    @pytest.fixture
    def config(self):
        """提供基础配置"""
        settings = GlobalSettings(timeout=5000, retry_count=2, retry_delay=100)
        return ServicesConfig(settings=settings, providers={})

    def test_register_provider_class(self, config):
        """测试注册提供者类"""
        # Arrange
        registry = ServiceRegistry(config)

        # Act
        registry.register_provider_class('mock', MockProvider)

        # Assert
        assert 'mock' in registry._provider_classes, \
            "提供者类应该被注册"

    def test_register_multiple_provider_classes(self, config):
        """测试注册多个提供者类"""
        # Arrange
        registry = ServiceRegistry(config)
        initial_count = len(registry._provider_classes)

        # Act
        registry.register_provider_class('mock', MockProvider)
        registry.register_provider_class('failing', FailingProvider)

        # Assert
        assert 'mock' in registry._provider_classes
        assert 'failing' in registry._provider_classes
        assert len(registry._provider_classes) == initial_count + 2, \
            "应该在初始提供者基础上增加 2 个新提供者"

    @pytest.mark.parametrize("provider_type,provider_class", [
        ("mock", MockProvider),
        ("failing", FailingProvider),
    ])
    def test_register_various_provider_types(
        self,
        config,
        provider_type,
        provider_class
    ):
        """测试注册各种提供者类型"""
        # Arrange
        registry = ServiceRegistry(config)

        # Act
        registry.register_provider_class(provider_type, provider_class)

        # Assert
        assert provider_type in registry._provider_classes


class TestProviderInitialization:
    """测试提供者初始化"""

    def _create_config(self, providers_data: dict = None) -> ServicesConfig:
        """创建测试配置"""
        settings = GlobalSettings(timeout=5000, retry_count=2, retry_delay=100)
        providers = {}

        if providers_data:
            for name, data in providers_data.items():
                providers[name] = ProviderConfig(
                    type=data.get('type', 'mock'),
                    config=data.get('config', {}),
                    timeout=data.get('timeout'),
                    retry_count=data.get('retry_count'),
                    retry_delay=data.get('retry_delay')
                )

        return ServicesConfig(settings=settings, providers=providers)

    def test_initialize_single_provider(self):
        """测试初始化单个提供者"""
        # Arrange
        config = self._create_config({
            'test': {'type': 'mock', 'config': {'key': 'value'}}
        })
        registry = ServiceRegistry(config)
        registry.register_provider_class('mock', MockProvider)

        # Act
        registry.initialize()

        # Assert
        assert 'test' in registry.providers, "提供者应该被初始化"
        assert registry.providers['test'].initialized, "提供者应该处于已初始化状态"

    def test_initialize_multiple_providers(self):
        """测试初始化多个提供者"""
        # Arrange
        config = self._create_config({
            'provider1': {'type': 'mock', 'config': {}},
            'provider2': {'type': 'mock', 'config': {}}
        })
        registry = ServiceRegistry(config)
        registry.register_provider_class('mock', MockProvider)

        # Act
        registry.initialize()

        # Assert
        assert len(registry.providers) == 2, "应该初始化 2 个提供者"
        assert 'provider1' in registry.providers
        assert 'provider2' in registry.providers

    def test_initialized_provider_has_correct_config(self):
        """测试初始化的提供者有正确的配置"""
        # Arrange
        config = self._create_config({
            'test': {'type': 'mock', 'config': {'api_key': 'secret123'}}
        })
        registry = ServiceRegistry(config)
        registry.register_provider_class('mock', MockProvider)

        # Act
        registry.initialize()

        # Assert
        provider = registry.providers['test']
        assert provider.config.get('api_key') == 'secret123', \
            "提供者应该有正确的配置"

    @pytest.mark.parametrize("num_providers", [1, 2, 3, 5])
    def test_initialize_various_numbers_of_providers(self, num_providers):
        """测试初始化不同数量的提供者"""
        # Arrange
        providers_data = {
            f'provider{i}': {'type': 'mock', 'config': {}}
            for i in range(num_providers)
        }
        config = self._create_config(providers_data)
        registry = ServiceRegistry(config)
        registry.register_provider_class('mock', MockProvider)

        # Act
        registry.initialize()

        # Assert
        assert len(registry.providers) == num_providers


class TestProviderRetrieval:
    """测试提供者获取"""

    def _create_registry_with_provider(self, provider_name='test'):
        """创建带有提供者的 registry"""
        settings = GlobalSettings()
        providers = {
            provider_name: ProviderConfig(type='mock', config={})
        }
        config = ServicesConfig(settings=settings, providers=providers)
        registry = ServiceRegistry(config)
        registry.register_provider_class('mock', MockProvider)
        registry.initialize()
        return registry

    def test_get_existing_provider(self):
        """测试获取存在的提供者"""
        # Arrange
        registry = self._create_registry_with_provider('test')

        # Act
        provider = registry.get_provider('test')

        # Assert
        assert provider is not None, "应该返回提供者"
        assert isinstance(provider, MockProvider), "应该是 MockProvider 实例"

    def test_get_provider_not_found(self):
        """测试获取不存在的提供者"""
        # Arrange
        registry = self._create_registry_with_provider('test')

        # Act & Assert
        with pytest.raises(ServiceError) as exc_info:
            registry.get_provider('nonexistent')

        assert "不存在" in str(exc_info.value), "错误消息应该包含'不存在'"

    @pytest.mark.parametrize("provider_name", [
        "test",
        "email",
        "sms",
        "random",
    ])
    def test_get_various_providers(self, provider_name):
        """测试获取各种提供者"""
        # Arrange
        registry = self._create_registry_with_provider(provider_name)

        # Act
        provider = registry.get_provider(provider_name)

        # Assert
        assert provider is not None
        assert isinstance(provider, MockProvider)


class TestServiceCalling:
    """测试服务调用"""

    @pytest.fixture
    def registry(self):
        """提供已初始化的 registry"""
        settings = GlobalSettings()
        providers = {
            'test': ProviderConfig(type='mock', config={'api_key': 'secret'})
        }
        config = ServicesConfig(settings=settings, providers=providers)
        registry = ServiceRegistry(config)
        registry.register_provider_class('mock', MockProvider)
        registry.initialize()
        return registry

    def test_call_simple_method(self, registry):
        """测试调用简单方法"""
        # Arrange & Act
        result = registry.call("test.echo", message="hello")

        # Assert
        assert result == "hello", "echo 方法应该返回原消息"

    def test_call_with_multiple_parameters(self, registry):
        """测试带多个参数的调用"""
        # Arrange & Act
        result = registry.call("test.add", a=3, b=5)

        # Assert
        assert result == 8, "add 方法应该返回 3 + 5 = 8"

    def test_call_uses_provider_config(self, registry):
        """测试调用使用提供者配置"""
        # Arrange & Act
        result = registry.call("test.get_config", key="api_key")

        # Assert
        assert result == "secret", "应该返回配置中的值"

    def test_call_history_is_recorded(self, registry):
        """测试调用历史被记录"""
        # Arrange & Act
        registry.call("test.echo", message="hello")
        registry.call("test.add", a=1, b=2)

        # Assert
        provider = registry.get_provider('test')
        assert len(provider.call_history) == 2, "应该记录 2 次调用"
        assert provider.call_history[0] == ('echo', {'message': 'hello'})
        assert provider.call_history[1] == ('add', {'a': 1, 'b': 2})

    @pytest.mark.parametrize("method,params,expected", [
        ("echo", {"message": "test"}, "test"),
        ("echo", {"message": "hello world"}, "hello world"),
        ("add", {"a": 10, "b": 20}, 30),
        ("add", {"a": 100, "b": 200}, 300),
    ])
    def test_various_method_calls(self, registry, method, params, expected):
        """测试各种方法调用"""
        # Act
        result = registry.call(f"test.{method}", **params)

        # Assert
        assert result == expected


class TestServiceCallingErrors:
    """测试服务调用错误处理"""

    @pytest.fixture
    def registry(self):
        """提供已初始化的 registry"""
        settings = GlobalSettings()
        providers = {
            'test': ProviderConfig(type='mock', config={})
        }
        config = ServicesConfig(settings=settings, providers=providers)
        registry = ServiceRegistry(config)
        registry.register_provider_class('mock', MockProvider)
        registry.initialize()
        return registry

    def test_call_with_invalid_path(self, registry):
        """测试无效的服务路径"""
        # Act & Assert
        with pytest.raises(ServiceError) as exc_info:
            registry.call("invalid_path")

        assert "无效的服务路径" in str(exc_info.value)

    def test_call_nonexistent_method(self, registry):
        """测试调用不存在的方法"""
        # Act & Assert
        with pytest.raises(ServiceError) as exc_info:
            registry.call("test.nonexistent")

        assert "不存在" in str(exc_info.value)

    def test_call_method_that_raises_error(self, registry):
        """测试方法抛出错误"""
        # Act & Assert
        with pytest.raises(ServiceError) as exc_info:
            registry.call("test.fail")

        error_message = str(exc_info.value)
        assert "调用失败" in error_message or "Intentional failure" in error_message

    @pytest.mark.parametrize("invalid_path", [
        "no_dot",
        "too.many.dots",
        "..empty",
        "nonexistent.method",
    ])
    def test_various_invalid_paths(self, registry, invalid_path):
        """测试各种无效路径"""
        # Act & Assert
        with pytest.raises(ServiceError):
            registry.call(invalid_path)


class TestConfigurationInheritance:
    """测试配置继承和覆盖"""

    def _create_config(self, providers_data: dict = None) -> ServicesConfig:
        """创建测试配置"""
        settings = GlobalSettings(timeout=5000, retry_count=2, retry_delay=100)
        providers = {}

        if providers_data:
            for name, data in providers_data.items():
                providers[name] = ProviderConfig(
                    type=data.get('type', 'mock'),
                    config=data.get('config', {}),
                    timeout=data.get('timeout'),
                    retry_count=data.get('retry_count'),
                    retry_delay=data.get('retry_delay')
                )

        return ServicesConfig(settings=settings, providers=providers)

    def test_provider_inherits_global_settings(self):
        """测试提供者继承全局设置"""
        # Arrange
        config = self._create_config({
            'test': {'type': 'mock', 'config': {}}
        })
        registry = ServiceRegistry(config)
        registry.register_provider_class('mock', MockProvider)

        # Act
        registry.initialize()

        # Assert
        provider = registry.get_provider('test')
        assert provider.timeout == 5000, "应该继承全局 timeout"
        assert provider.retry_count == 2, "应该继承全局 retry_count"
        assert provider.retry_delay == 100, "应该继承全局 retry_delay"

    def test_provider_overrides_timeout(self):
        """测试提供者覆盖 timeout"""
        # Arrange
        config = self._create_config({
            'test': {
                'type': 'mock',
                'config': {},
                'timeout': 10000
            }
        })
        registry = ServiceRegistry(config)
        registry.register_provider_class('mock', MockProvider)

        # Act
        registry.initialize()

        # Assert
        provider = registry.get_provider('test')
        assert provider.timeout == 10000, "应该使用覆盖的 timeout"
        assert provider.retry_count == 2, "未覆盖的应该使用全局值"

    def test_provider_overrides_retry_count(self):
        """测试提供者覆盖 retry_count"""
        # Arrange
        config = self._create_config({
            'test': {
                'type': 'mock',
                'config': {},
                'retry_count': 5
            }
        })
        registry = ServiceRegistry(config)
        registry.register_provider_class('mock', MockProvider)

        # Act
        registry.initialize()

        # Assert
        provider = registry.get_provider('test')
        assert provider.retry_count == 5, "应该使用覆盖的 retry_count"
        assert provider.timeout == 5000, "未覆盖的应该使用全局值"

    def test_provider_overrides_all_settings(self):
        """测试提供者覆盖所有设置"""
        # Arrange
        config = self._create_config({
            'test': {
                'type': 'mock',
                'config': {},
                'timeout': 10000,
                'retry_count': 5,
                'retry_delay': 200
            }
        })
        registry = ServiceRegistry(config)
        registry.register_provider_class('mock', MockProvider)

        # Act
        registry.initialize()

        # Assert
        provider = registry.get_provider('test')
        assert provider.timeout == 10000
        assert provider.retry_count == 5
        assert provider.retry_delay == 200


class TestErrorHandling:
    """测试错误处理"""

    def _create_config(self, providers_data: dict) -> ServicesConfig:
        """创建测试配置"""
        settings = GlobalSettings()
        providers = {}

        for name, data in providers_data.items():
            providers[name] = ProviderConfig(
                type=data.get('type', 'mock'),
                config=data.get('config', {})
            )

        return ServicesConfig(settings=settings, providers=providers)

    def test_unknown_provider_type(self):
        """测试未知的提供者类型"""
        # Arrange
        config = self._create_config({
            'test': {'type': 'unknown', 'config': {}}
        })
        registry = ServiceRegistry(config)

        # Act & Assert
        with pytest.raises(ServiceError) as exc_info:
            registry.initialize()

        assert "未知的提供者类型" in str(exc_info.value)

    def test_provider_initialization_failure(self):
        """测试提供者初始化失败"""
        # Arrange
        config = self._create_config({
            'test': {'type': 'failing', 'config': {}}
        })
        registry = ServiceRegistry(config)
        registry.register_provider_class('failing', FailingProvider)

        # Act & Assert
        with pytest.raises(ServiceError) as exc_info:
            registry.initialize()

        error_message = str(exc_info.value)
        assert "初始化" in error_message or "Init failed" in error_message


class TestResourceManagement:
    """测试资源管理"""

    def _create_config(self, providers_data: dict) -> ServicesConfig:
        """创建测试配置"""
        settings = GlobalSettings()
        providers = {}

        for name, data in providers_data.items():
            providers[name] = ProviderConfig(
                type=data.get('type', 'mock'),
                config=data.get('config', {})
            )

        return ServicesConfig(settings=settings, providers=providers)

    def test_close_single_provider(self):
        """测试关闭单个提供者"""
        # Arrange
        config = self._create_config({
            'test': {'type': 'mock', 'config': {}}
        })
        registry = ServiceRegistry(config)
        registry.register_provider_class('mock', MockProvider)
        registry.initialize()
        provider = registry.providers['test']

        # Act
        registry.close()

        # Assert
        assert provider.closed, "提供者应该被关闭"
        assert len(registry.providers) == 0, "提供者列表应该为空"

    def test_close_multiple_providers(self):
        """测试关闭多个提供者"""
        # Arrange
        config = self._create_config({
            'test1': {'type': 'mock', 'config': {}},
            'test2': {'type': 'mock', 'config': {}}
        })
        registry = ServiceRegistry(config)
        registry.register_provider_class('mock', MockProvider)
        registry.initialize()
        provider1 = registry.providers['test1']
        provider2 = registry.providers['test2']

        # Act
        registry.close()

        # Assert
        assert provider1.closed, "提供者 1 应该被关闭"
        assert provider2.closed, "提供者 2 应该被关闭"
        assert len(registry.providers) == 0, "提供者列表应该为空"

    @pytest.mark.parametrize("num_providers", [1, 2, 3, 5])
    def test_close_various_numbers_of_providers(self, num_providers):
        """测试关闭不同数量的提供者"""
        # Arrange
        providers_data = {
            f'provider{i}': {'type': 'mock', 'config': {}}
            for i in range(num_providers)
        }
        config = self._create_config(providers_data)
        registry = ServiceRegistry(config)
        registry.register_provider_class('mock', MockProvider)
        registry.initialize()

        # 保存所有提供者引用
        providers = [registry.providers[f'provider{i}'] for i in range(num_providers)]

        # Act
        registry.close()

        # Assert
        for provider in providers:
            assert provider.closed, "每个提供者都应该被关闭"
        assert len(registry.providers) == 0


class TestServiceError:
    """测试 ServiceError 异常"""

    def test_basic_error_message(self):
        """测试基本错误消息"""
        # Arrange & Act
        error = ServiceError("测试错误")

        # Assert
        assert "测试错误" in str(error), "错误消息应该包含原始文本"

    def test_error_with_provider_name(self):
        """测试带提供者名称的错误"""
        # Arrange & Act
        error = ServiceError("测试错误", provider="email")

        # Assert
        message = str(error)
        assert "测试错误" in message
        assert "email" in message, "错误消息应该包含提供者名称"

    def test_error_with_method_name(self):
        """测试带方法名称的错误"""
        # Arrange & Act
        error = ServiceError("测试错误", provider="email", method="get_code")

        # Assert
        message = str(error)
        assert "email" in message, "应该包含提供者名称"
        assert "get_code" in message, "应该包含方法名称"

    def test_error_with_cause(self):
        """测试带原因的错误"""
        # Arrange
        cause = ValueError("原始错误")

        # Act
        error = ServiceError("测试错误", cause=cause)

        # Assert
        message = str(error)
        assert "原始错误" in message, "错误消息应该包含原始错误信息"

    @pytest.mark.parametrize("message,provider,method", [
        ("连接失败", "email", "send"),
        ("超时", "sms", "get_code"),
        ("认证失败", "random", "password"),
    ])
    def test_various_error_combinations(self, message, provider, method):
        """测试各种错误组合"""
        # Act
        error = ServiceError(message, provider=provider, method=method)

        # Assert
        error_str = str(error)
        assert message in error_str
        assert provider in error_str
        assert method in error_str
