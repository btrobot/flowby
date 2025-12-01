"""
服务提供者基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from ..config.schema import GlobalSettings
from .errors import ServiceError


class ServiceProvider(ABC):
    """服务提供者基类"""

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        settings: GlobalSettings,
        timeout: Optional[int] = None,
        retry_count: Optional[int] = None,
        retry_delay: Optional[int] = None,
    ):
        """
        初始化提供者

        Args:
            name: 提供者名称
            config: 提供者配置
            settings: 全局设置
            timeout: 覆盖超时
            retry_count: 覆盖重试次数
            retry_delay: 覆盖重试间隔
        """
        self.name = name
        self.config = config
        self.settings = settings

        # 使用覆盖值或全局设置
        self.timeout = timeout if timeout is not None else settings.timeout
        self.retry_count = retry_count if retry_count is not None else settings.retry_count
        self.retry_delay = retry_delay if retry_delay is not None else settings.retry_delay

    @abstractmethod
    def initialize(self) -> None:
        """
        初始化提供者（建立连接等）

        Raises:
            ServiceError: 初始化失败
        """

    @abstractmethod
    def get_methods(self) -> List[str]:
        """
        获取提供者支持的方法列表

        Returns:
            方法名列表
        """

    def call_method(self, method: str, **kwargs) -> Any:
        """
        调用提供者方法

        Args:
            method: 方法名
            **kwargs: 方法参数

        Returns:
            方法返回值

        Raises:
            ServiceError: 方法不存在或调用失败
        """
        if method not in self.get_methods():
            raise ServiceError(f"方法 '{method}' 不存在", provider=self.name, method=method)

        if not hasattr(self, method):
            raise ServiceError(f"方法 '{method}' 未实现", provider=self.name, method=method)

        method_func = getattr(self, method)

        try:
            return method_func(**kwargs)
        except ServiceError:
            raise
        except Exception as e:
            raise ServiceError(f"方法调用失败: {e}", provider=self.name, method=method, cause=e)

    def close(self) -> None:
        """关闭提供者，释放资源"""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
