"""
服务错误定义
"""

from typing import Optional


class ServiceError(Exception):
    """服务调用错误"""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        method: Optional[str] = None,
        cause: Optional[Exception] = None
    ):
        """
        初始化服务错误

        Args:
            message: 错误消息
            provider: 提供者名称
            method: 方法名称
            cause: 原始异常
        """
        self.message = message
        self.provider = provider
        self.method = method
        self.cause = cause

        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """格式化错误消息"""
        parts = [f"ServiceError: {self.message}"]

        if self.provider:
            parts.append(f"提供者: {self.provider}")

        if self.method:
            parts.append(f"方法: {self.method}")

        if self.cause:
            parts.append(f"原因: {self.cause}")

        return "\n".join(parts)
