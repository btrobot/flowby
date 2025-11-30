"""
Retry Handler - v4.2 Phase 4

错误重试策略实现。

功能:
- 指数退避（Exponential Backoff）
- 固定延迟（Fixed Delay）
- 线性退避（Linear Backoff）
- 抖动（Jitter）
- 可配置的重试条件
- 幂等性检查
"""

import time
import random
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod


class RetryStrategy(ABC):
    """重试策略基类"""

    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """
        计算第 n 次重试的延迟时间

        Args:
            attempt: 重试次数（从 1 开始）

        Returns:
            延迟时间（秒）
        """
        pass


class ExponentialBackoff(RetryStrategy):
    """指数退避策略"""

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        multiplier: float = 2.0,
        jitter: bool = False,
        jitter_factor: float = 0.3
    ):
        """
        初始化指数退避策略

        Args:
            base_delay: 基础延迟（秒）
            max_delay: 最大延迟（秒）
            multiplier: 倍增系数
            jitter: 是否启用抖动
            jitter_factor: 抖动因子（±百分比）
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier
        self.jitter = jitter
        self.jitter_factor = jitter_factor

    def get_delay(self, attempt: int) -> float:
        """计算指数退避延迟"""
        # 指数计算：base_delay * (multiplier ^ (attempt - 1))
        delay = self.base_delay * (self.multiplier ** (attempt - 1))

        # 限制最大延迟
        delay = min(delay, self.max_delay)

        # 添加抖动
        if self.jitter:
            jitter_range = delay * self.jitter_factor
            delay += random.uniform(-jitter_range, jitter_range)
            # 确保延迟为正数
            delay = max(0.1, delay)

        return delay


class FixedDelay(RetryStrategy):
    """固定延迟策略"""

    def __init__(self, delay: float = 2.0):
        """
        初始化固定延迟策略

        Args:
            delay: 固定延迟时间（秒）
        """
        self.delay = delay

    def get_delay(self, attempt: int) -> float:
        """返回固定延迟"""
        return self.delay


class LinearBackoff(RetryStrategy):
    """线性退避策略"""

    def __init__(
        self,
        base_delay: float = 1.0,
        increment: float = 1.0,
        max_delay: float = 60.0
    ):
        """
        初始化线性退避策略

        Args:
            base_delay: 基础延迟（秒）
            increment: 每次增加的延迟（秒）
            max_delay: 最大延迟（秒）
        """
        self.base_delay = base_delay
        self.increment = increment
        self.max_delay = max_delay

    def get_delay(self, attempt: int) -> float:
        """计算线性退避延迟"""
        delay = self.base_delay + (attempt - 1) * self.increment
        return min(delay, self.max_delay)


class RetryHandler:
    """
    重试处理器

    负责执行带重试的操作，支持多种重试策略。
    """

    # 幂等的 HTTP 方法
    IDEMPOTENT_METHODS = {"GET", "HEAD", "OPTIONS", "PUT", "DELETE"}

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化重试处理器

        Args:
            config: 重试配置

        配置示例:
            {
                "max_retries": 3,
                "strategy": "exponential",  # 或 "fixed", "linear"
                "base_delay": 1.0,
                "max_delay": 60.0,
                "multiplier": 2.0,
                "jitter": True,
                "jitter_factor": 0.3,
                "retry_on_status": [429, 503, 504],
                "retry_on_exceptions": ["ConnectionError", "Timeout"],
                "only_idempotent": True,
                "idempotent_methods": ["GET", "HEAD", "PUT", "DELETE"]
            }
        """
        self.config = config or {}
        self.max_retries = self.config.get('max_retries', 0)
        self.retry_on_status = set(self.config.get('retry_on_status', [429, 503, 504]))
        self.retry_on_exceptions = set(self.config.get('retry_on_exceptions', [
            'ConnectionError', 'Timeout', 'ReadTimeout'
        ]))
        self.only_idempotent = self.config.get('only_idempotent', True)
        self.idempotent_methods = set(self.config.get(
            'idempotent_methods',
            self.IDEMPOTENT_METHODS
        ))

        # 创建重试策略
        self.strategy = self._create_strategy()

        # 统计信息
        self.total_retries = 0
        self.successful_retries = 0
        self.failed_retries = 0

    def _create_strategy(self) -> RetryStrategy:
        """创建重试策略"""
        strategy_type = self.config.get('strategy', 'exponential')

        if strategy_type == 'exponential':
            return ExponentialBackoff(
                base_delay=self.config.get('base_delay', 1.0),
                max_delay=self.config.get('max_delay', 60.0),
                multiplier=self.config.get('multiplier', 2.0),
                jitter=self.config.get('jitter', False),
                jitter_factor=self.config.get('jitter_factor', 0.3)
            )
        elif strategy_type == 'fixed':
            return FixedDelay(
                delay=self.config.get('delay', 2.0)
            )
        elif strategy_type == 'linear':
            return LinearBackoff(
                base_delay=self.config.get('base_delay', 1.0),
                increment=self.config.get('increment', 1.0),
                max_delay=self.config.get('max_delay', 60.0)
            )
        else:
            raise ValueError(f"不支持的重试策略: {strategy_type}")

    def should_retry(
        self,
        exception: Optional[Exception] = None,
        response: Optional[Any] = None,
        method: str = "GET"
    ) -> bool:
        """
        判断是否应该重试

        Args:
            exception: 发生的异常
            response: HTTP 响应对象（如果有）
            method: HTTP 方法

        Returns:
            是否应该重试
        """
        # 检查幂等性
        if self.only_idempotent and method.upper() not in self.idempotent_methods:
            return False

        # 检查异常类型
        if exception:
            exception_name = type(exception).__name__
            if exception_name in self.retry_on_exceptions:
                return True

        # 检查 HTTP 状态码
        if response and hasattr(response, 'status_code'):
            if response.status_code in self.retry_on_status:
                return True

        return False

    def execute(
        self,
        operation_name: str,
        func: Callable,
        method: str = "GET",
        logger: Optional[Any] = None
    ) -> Any:
        """
        执行带重试的操作

        Args:
            operation_name: 操作名称（用于日志）
            func: 要执行的函数
            method: HTTP 方法（用于幂等性检查）
            logger: 日志记录器

        Returns:
            函数执行结果

        Raises:
            最后一次失败的异常
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                # 执行操作
                result = func()

                # 第一次成功，直接返回
                if attempt == 0:
                    return result

                # 重试成功
                self.successful_retries += 1
                if logger:
                    logger.info(
                        f"[RETRY] Attempt {attempt + 1}/{self.max_retries + 1} "
                        f"succeeded for {operation_name}"
                    )
                return result

            except Exception as e:
                last_exception = e

                # 检查是否应该重试
                if attempt < self.max_retries:
                    # 判断是否可重试
                    response = getattr(e, 'response', None)
                    if not self.should_retry(e, response, method):
                        # 不可重试的错误，直接抛出
                        raise

                    # 计算延迟
                    delay = self.strategy.get_delay(attempt + 1)

                    # 记录日志
                    self.total_retries += 1
                    if logger:
                        error_msg = str(e)
                        if response and hasattr(response, 'status_code'):
                            error_msg = f"{response.status_code} {error_msg}"

                        logger.warning(
                            f"[RETRY] Attempt {attempt + 1}/{self.max_retries + 1} "
                            f"failed for {operation_name}: {error_msg}"
                        )
                        logger.info(
                            f"[RETRY] Waiting {delay:.2f}s before retry "
                            f"({self.config.get('strategy', 'exponential')} backoff)"
                        )

                    # 等待后重试
                    time.sleep(delay)
                else:
                    # 达到最大重试次数
                    self.failed_retries += 1
                    if logger:
                        logger.error(
                            f"[RETRY] All {self.max_retries + 1} attempts failed "
                            f"for {operation_name}"
                        )
                    raise

        # 理论上不会到达这里
        if last_exception:
            raise last_exception

    def get_metrics(self) -> Dict[str, Any]:
        """获取重试统计指标"""
        return {
            "total_retries": self.total_retries,
            "successful_retries": self.successful_retries,
            "failed_retries": self.failed_retries,
        }

    def reset_metrics(self):
        """重置统计指标"""
        self.total_retries = 0
        self.successful_retries = 0
        self.failed_retries = 0
