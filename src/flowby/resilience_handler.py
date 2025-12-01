"""
Resilience Handler - v4.2 Phase 4

弹性处理器，整合重试和断路器功能。

功能:
- 统一的弹性配置接口
- 断路器 + 重试的组合策略
- 统一的指标收集
- 灵活的降级策略
"""

from typing import Dict, Any, Optional, Callable
from .retry_handler import RetryHandler
from .circuit_breaker import CircuitBreaker


class ResilienceHandler:
    """
    弹性处理器

    整合重试和断路器功能，提供统一的弹性处理接口。
    执行流程：断路器检查 → 重试机制 → 操作执行
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化弹性处理器

        Args:
            config: 弹性配置

        配置示例:
            {
                # 重试配置
                "retry": {
                    "max_retries": 3,
                    "strategy": "exponential",
                    "base_delay": 1.0,
                    "max_delay": 60.0,
                    "multiplier": 2.0,
                    "jitter": True,
                    "retry_on_status": [429, 503, 504],
                    "retry_on_exceptions": ["ConnectionError", "Timeout"],
                    "only_idempotent": True
                },

                # 断路器配置
                "circuit_breaker": {
                    "failure_threshold": 5,
                    "success_threshold": 2,
                    "recovery_timeout": 60,
                    "window_size": 100,
                    "failure_rate_threshold": 0.5,
                    "fallback": None
                },

                # 全局配置
                "enabled": True,           # 是否启用弹性处理
                "retry_enabled": True,     # 是否启用重试
                "circuit_breaker_enabled": True  # 是否启用断路器
            }
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.retry_enabled = self.config.get("retry_enabled", True)
        self.circuit_breaker_enabled = self.config.get("circuit_breaker_enabled", True)

        # 创建重试处理器
        retry_config = self.config.get("retry", {})
        self.retry_handler = RetryHandler(retry_config) if self.retry_enabled else None

        # 创建断路器
        circuit_config = self.config.get("circuit_breaker", {})
        self.circuit_breaker = (
            CircuitBreaker(circuit_config) if self.circuit_breaker_enabled else None
        )

    def execute(
        self, operation_name: str, func: Callable, method: str = "GET", logger: Optional[Any] = None
    ) -> Any:
        """
        执行带弹性保护的操作

        Args:
            operation_name: 操作名称（用于日志）
            func: 要执行的函数
            method: HTTP 方法（用于重试的幂等性检查）
            logger: 日志记录器

        Returns:
            函数执行结果

        Raises:
            CircuitBreakerError: 断路器打开且无降级函数时
            Exception: 函数执行失败且重试耗尽时
        """
        # 如果未启用弹性处理，直接执行
        if not self.enabled:
            return func()

        # 场景1：仅启用断路器
        if self.circuit_breaker_enabled and not self.retry_enabled:
            return self.circuit_breaker.execute(operation_name, func, logger)

        # 场景2：仅启用重试
        if self.retry_enabled and not self.circuit_breaker_enabled:
            return self.retry_handler.execute(operation_name, func, method, logger)

        # 场景3：同时启用断路器和重试（推荐配置）
        if self.circuit_breaker_enabled and self.retry_enabled:
            # 先通过断路器检查，再使用重试机制
            def retry_wrapper():
                """包装函数，用于重试"""
                return func()

            return self.circuit_breaker.execute(
                operation_name,
                lambda: self.retry_handler.execute(operation_name, retry_wrapper, method, logger),
                logger,
            )

        # 默认：直接执行
        return func()

    def get_metrics(self) -> Dict[str, Any]:
        """
        获取弹性处理器统计指标

        Returns:
            包含重试和断路器指标的字典
        """
        metrics = {
            "enabled": self.enabled,
            "retry_enabled": self.retry_enabled,
            "circuit_breaker_enabled": self.circuit_breaker_enabled,
        }

        # 添加重试指标
        if self.retry_handler:
            metrics["retry"] = self.retry_handler.get_metrics()

        # 添加断路器指标
        if self.circuit_breaker:
            metrics["circuit_breaker"] = self.circuit_breaker.get_metrics()

        return metrics

    def reset_metrics(self):
        """重置所有统计指标"""
        if self.retry_handler:
            self.retry_handler.reset_metrics()

        if self.circuit_breaker:
            self.circuit_breaker.reset()

    def reset_circuit_breaker(self):
        """重置断路器状态"""
        if self.circuit_breaker:
            self.circuit_breaker.reset()

    def force_circuit_open(self):
        """强制打开断路器（用于测试或维护）"""
        if self.circuit_breaker:
            self.circuit_breaker.force_open()

    def force_circuit_close(self):
        """强制关闭断路器（用于测试或维护）"""
        if self.circuit_breaker:
            self.circuit_breaker.force_close()

    def __repr__(self) -> str:
        """字符串表示"""
        status = []
        if self.retry_enabled:
            status.append("retry")
        if self.circuit_breaker_enabled:
            status.append("circuit_breaker")

        return f"<ResilienceHandler enabled={self.enabled} features=[{', '.join(status)}]>"


def create_resilience_handler(
    config: Optional[Dict[str, Any]] = None,
) -> Optional[ResilienceHandler]:
    """
    创建弹性处理器（工厂函数）

    Args:
        config: 弹性配置

    Returns:
        ResilienceHandler 实例，如果配置为空则返回 None
    """
    if not config:
        return None

    # 检查是否启用了任何弹性功能
    enabled = config.get("enabled", True)
    retry_enabled = config.get("retry_enabled", True)
    circuit_breaker_enabled = config.get("circuit_breaker_enabled", True)

    if not enabled or (not retry_enabled and not circuit_breaker_enabled):
        return None

    return ResilienceHandler(config)
