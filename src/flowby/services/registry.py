"""
服务注册中心
"""

import time
from typing import Dict, Any, Type, Optional

from ..config.schema import ServicesConfig, GlobalSettings
from .provider import ServiceProvider
from .errors import ServiceError


class ServiceRegistry:
    """服务注册中心"""

    def __init__(self, config: ServicesConfig):
        """
        初始化服务注册中心

        Args:
            config: 服务配置（从 ConfigLoader 加载）
        """
        self.config = config
        self.providers: Dict[str, ServiceProvider] = {}
        self._provider_classes: Dict[str, Type[ServiceProvider]] = {}

        # 注册内置提供者
        self._register_builtin_providers()

    def _register_builtin_providers(self):
        """注册内置服务提供者类"""
        from .providers import BUILTIN_PROVIDERS

        for type_name, provider_class in BUILTIN_PROVIDERS.items():
            self._provider_classes[type_name] = provider_class

    def register_provider_class(
        self,
        type_name: str,
        provider_class: Type[ServiceProvider]
    ) -> None:
        """
        注册自定义提供者类

        Args:
            type_name: 提供者类型名称
            provider_class: 提供者类
        """
        self._provider_classes[type_name] = provider_class

    def initialize(self) -> None:
        """
        根据配置初始化所有服务提供者

        Raises:
            ServiceError: 提供者初始化失败
        """
        for name, provider_config in self.config.providers.items():
            provider_type = provider_config.type

            if provider_type not in self._provider_classes:
                raise ServiceError(
                    f"未知的提供者类型: {provider_type}",
                    provider=name
                )

            provider_class = self._provider_classes[provider_type]

            try:
                # 创建提供者实例
                provider = provider_class(
                    name=name,
                    config=provider_config.config,
                    settings=self.config.settings,
                    timeout=provider_config.timeout,
                    retry_count=provider_config.retry_count,
                    retry_delay=provider_config.retry_delay
                )

                # 初始化提供者
                provider.initialize()

                self.providers[name] = provider

            except ServiceError:
                raise
            except Exception as e:
                raise ServiceError(
                    f"初始化提供者 '{name}' 失败: {e}",
                    provider=name,
                    cause=e
                )

    def get_provider(self, name: str) -> ServiceProvider:
        """
        获取服务提供者实例

        Args:
            name: 提供者名称（配置中的 key）

        Returns:
            ServiceProvider 实例

        Raises:
            ServiceError: 提供者不存在
        """
        if name not in self.providers:
            raise ServiceError(
                f"提供者 '{name}' 不存在",
                provider=name
            )

        return self.providers[name]

    def call(self, service_path: str, **kwargs) -> Any:
        """
        调用服务方法

        Args:
            service_path: 服务路径，格式为 "provider.method"
            **kwargs: 方法参数

        Returns:
            方法返回值

        Raises:
            ServiceError: 调用失败

        Example:
            registry.call("email.create")
            registry.call("email.get_code", pattern=r"\\d{6}")
        """
        # 解析路径
        parts = service_path.split(".")
        if len(parts) != 2:
            raise ServiceError(
                f"无效的服务路径: {service_path}，格式应为 'provider.method'"
            )

        provider_name, method_name = parts

        # 获取提供者
        provider = self.get_provider(provider_name)

        # 调用方法（带重试）
        return self._call_with_retry(provider, method_name, **kwargs)

    def _call_with_retry(
        self,
        provider: ServiceProvider,
        method: str,
        **kwargs
    ) -> Any:
        """
        带重试的方法调用

        Args:
            provider: 提供者实例
            method: 方法名
            **kwargs: 方法参数

        Returns:
            方法返回值
        """
        last_error = None

        for attempt in range(provider.retry_count + 1):
            try:
                return provider.call_method(method, **kwargs)

            except ServiceError as e:
                last_error = e

                # 检查是否应该重试
                if attempt < provider.retry_count and self._should_retry(e):
                    time.sleep(provider.retry_delay / 1000.0)
                    continue

                raise

        # 不应该到达这里，但以防万一
        if last_error:
            raise last_error

    def _should_retry(self, error: ServiceError) -> bool:
        """
        判断是否应该重试

        Args:
            error: 服务错误

        Returns:
            是否应该重试
        """
        # 可以根据错误类型决定是否重试
        # 目前简单处理：网络相关错误重试
        if error.cause:
            error_type = type(error.cause).__name__
            return error_type in ['TimeoutError', 'ConnectionError', 'OSError']

        return False

    def close(self) -> None:
        """关闭所有服务提供者，释放资源"""
        for name, provider in self.providers.items():
            try:
                provider.close()
            except Exception:
                # 忽略关闭错误
                pass

        self.providers.clear()

    def __repr__(self) -> str:
        return f"ServiceRegistry(providers={list(self.providers.keys())})"
