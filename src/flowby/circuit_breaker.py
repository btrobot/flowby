"""
Circuit Breaker - v4.2 Phase 4

断路器模式实现。

功能:
- 三状态机制（CLOSED、OPEN、HALF_OPEN）
- 失败率阈值检测
- 自动恢复机制
- 降级处理（Fallback）
- 状态转换监控
"""

import time
from enum import Enum
from typing import Dict, Any, Optional, Callable
from collections import deque
from threading import Lock


class CircuitBreakerState(Enum):
    """断路器状态"""
    CLOSED = "CLOSED"      # 正常状态，请求正常通过
    OPEN = "OPEN"          # 断开状态，请求直接失败
    HALF_OPEN = "HALF_OPEN"  # 半开状态，允许少量探测请求


class CircuitBreakerError(Exception):
    """断路器开启时的异常"""
    def __init__(self, message: str, fallback_result: Any = None):
        super().__init__(message)
        self.fallback_result = fallback_result


class CircuitBreaker:
    """
    断路器

    实现三状态机制，当失败率超过阈值时自动打开，
    经过恢复时间后进入半开状态进行探测。
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化断路器

        Args:
            config: 断路器配置

        配置示例:
            {
                "failure_threshold": 5,        # 失败次数阈值
                "success_threshold": 2,        # 半开状态下成功次数阈值
                "recovery_timeout": 60,        # 恢复超时（秒）
                "window_size": 100,            # 滑动窗口大小
                "failure_rate_threshold": 0.5, # 失败率阈值（0.0-1.0）
                "fallback": None               # 降级函数
            }
        """
        self.config = config or {}

        # 阈值配置
        self.failure_threshold = self.config.get('failure_threshold', 5)
        self.success_threshold = self.config.get('success_threshold', 2)
        self.recovery_timeout = self.config.get('recovery_timeout', 60)
        self.window_size = self.config.get('window_size', 100)
        self.failure_rate_threshold = self.config.get('failure_rate_threshold', 0.5)
        self.fallback = self.config.get('fallback')

        # 状态
        self.state = CircuitBreakerState.CLOSED
        self.last_failure_time = None
        self.opened_at = None

        # 统计（滑动窗口）
        self.call_history = deque(maxlen=self.window_size)
        self.consecutive_failures = 0
        self.consecutive_successes = 0

        # 总体统计
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.state_transitions = 0

        # 线程安全
        self._lock = Lock()

    def execute(
        self,
        operation_name: str,
        func: Callable,
        logger: Optional[Any] = None
    ) -> Any:
        """
        执行操作（带断路器保护）

        Args:
            operation_name: 操作名称（用于日志）
            func: 要执行的函数
            logger: 日志记录器

        Returns:
            函数执行结果，或降级函数结果

        Raises:
            CircuitBreakerError: 断路器打开且无降级函数时
        """
        with self._lock:
            # 检查是否需要从 OPEN 状态恢复到 HALF_OPEN
            self._check_recovery()

            # 如果断路器打开，直接拒绝请求
            if self.state == CircuitBreakerState.OPEN:
                if logger:
                    logger.warning(
                        f"[CIRCUIT_BREAKER] {operation_name} rejected: "
                        f"Circuit is OPEN (failure rate too high)"
                    )

                # 尝试降级处理
                if self.fallback:
                    if logger:
                        logger.info(f"[CIRCUIT_BREAKER] Using fallback for {operation_name}")
                    return self._execute_fallback()

                raise CircuitBreakerError(
                    f"断路器已打开，操作被拒绝: {operation_name}。"
                    f"将在 {self.recovery_timeout} 秒后尝试恢复。"
                )

            # CLOSED 或 HALF_OPEN 状态：允许请求通过
            try:
                result = func()
                self._on_success(operation_name, logger)
                return result

            except Exception as e:
                self._on_failure(operation_name, e, logger)
                raise

    def _on_success(self, operation_name: str, logger: Optional[Any]) -> None:
        """
        记录成功调用

        Args:
            operation_name: 操作名称
            logger: 日志记录器
        """
        self.total_calls += 1
        self.total_successes += 1
        self.call_history.append(True)
        self.consecutive_failures = 0
        self.consecutive_successes += 1

        # 如果在 HALF_OPEN 状态，检查是否可以关闭断路器
        if self.state == CircuitBreakerState.HALF_OPEN:
            if self.consecutive_successes >= self.success_threshold:
                self._transition_to_closed(operation_name, logger)

    def _on_failure(
        self,
        operation_name: str,
        exception: Exception,
        logger: Optional[Any]
    ) -> None:
        """
        记录失败调用

        Args:
            operation_name: 操作名称
            exception: 异常对象
            logger: 日志记录器
        """
        self.total_calls += 1
        self.total_failures += 1
        self.call_history.append(False)
        self.consecutive_successes = 0
        self.consecutive_failures += 1
        self.last_failure_time = time.time()

        # 检查是否需要打开断路器
        if self.state == CircuitBreakerState.CLOSED:
            self._check_failure_threshold(operation_name, logger)
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # 半开状态下任何失败都会重新打开断路器
            self._transition_to_open(operation_name, logger)

    def _check_failure_threshold(
        self,
        operation_name: str,
        logger: Optional[Any]
    ) -> None:
        """
        检查失败阈值，决定是否打开断路器

        Args:
            operation_name: 操作名称
            logger: 日志记录器
        """
        # 方式1：连续失败次数
        if self.consecutive_failures >= self.failure_threshold:
            self._transition_to_open(operation_name, logger)
            return

        # 方式2：滑动窗口失败率
        if len(self.call_history) >= self.window_size:
            failure_count = sum(1 for call in self.call_history if not call)
            failure_rate = failure_count / len(self.call_history)

            if failure_rate >= self.failure_rate_threshold:
                if logger:
                    logger.warning(
                        f"[CIRCUIT_BREAKER] Failure rate {failure_rate:.2%} "
                        f"exceeds threshold {self.failure_rate_threshold:.2%}"
                    )
                self._transition_to_open(operation_name, logger)

    def _check_recovery(self) -> None:
        """检查是否可以从 OPEN 状态恢复到 HALF_OPEN"""
        if self.state == CircuitBreakerState.OPEN:
            if self.opened_at:
                elapsed = time.time() - self.opened_at
                if elapsed >= self.recovery_timeout:
                    self._transition_to_half_open()

    def _transition_to_open(
        self,
        operation_name: str,
        logger: Optional[Any]
    ) -> None:
        """
        转换到 OPEN 状态

        Args:
            operation_name: 操作名称
            logger: 日志记录器
        """
        self.state = CircuitBreakerState.OPEN
        self.opened_at = time.time()
        self.state_transitions += 1

        if logger:
            logger.error(
                f"[CIRCUIT_BREAKER] {operation_name} → OPEN "
                f"(consecutive failures: {self.consecutive_failures}, "
                f"failure rate: {self._get_failure_rate():.2%})"
            )

    def _transition_to_half_open(self) -> None:
        """转换到 HALF_OPEN 状态"""
        self.state = CircuitBreakerState.HALF_OPEN
        self.consecutive_successes = 0
        self.consecutive_failures = 0
        self.state_transitions += 1

    def _transition_to_closed(
        self,
        operation_name: str,
        logger: Optional[Any]
    ) -> None:
        """
        转换到 CLOSED 状态

        Args:
            operation_name: 操作名称
            logger: 日志记录器
        """
        self.state = CircuitBreakerState.CLOSED
        self.opened_at = None
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.state_transitions += 1

        if logger:
            logger.info(
                f"[CIRCUIT_BREAKER] {operation_name} → CLOSED "
                f"(recovered after {self.success_threshold} successful calls)"
            )

    def _execute_fallback(self) -> Any:
        """
        执行降级函数

        Returns:
            降级函数的结果
        """
        if callable(self.fallback):
            return self.fallback()
        else:
            return self.fallback

    def _get_failure_rate(self) -> float:
        """
        计算当前失败率

        Returns:
            失败率（0.0-1.0）
        """
        if not self.call_history:
            return 0.0

        failure_count = sum(1 for call in self.call_history if not call)
        return failure_count / len(self.call_history)

    def get_metrics(self) -> Dict[str, Any]:
        """获取断路器统计指标"""
        return {
            "state": self.state.value,
            "total_calls": self.total_calls,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "success_rate": (
                self.total_successes / self.total_calls
                if self.total_calls > 0 else 0.0
            ),
            "failure_rate": self._get_failure_rate(),
            "consecutive_failures": self.consecutive_failures,
            "consecutive_successes": self.consecutive_successes,
            "state_transitions": self.state_transitions,
            "opened_at": self.opened_at,
        }

    def reset(self):
        """重置断路器状态"""
        with self._lock:
            self.state = CircuitBreakerState.CLOSED
            self.last_failure_time = None
            self.opened_at = None
            self.call_history.clear()
            self.consecutive_failures = 0
            self.consecutive_successes = 0
            # 重置统计指标
            self.total_calls = 0
            self.total_failures = 0
            self.total_successes = 0

    def force_open(self):
        """强制打开断路器（用于测试或维护）"""
        with self._lock:
            self.state = CircuitBreakerState.OPEN
            self.opened_at = time.time()

    def force_close(self):
        """强制关闭断路器（用于测试或维护）"""
        with self._lock:
            self.state = CircuitBreakerState.CLOSED
            self.opened_at = None
            self.consecutive_failures = 0

    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"<CircuitBreaker state={self.state.value} "
            f"failures={self.consecutive_failures}/{self.failure_threshold}>"
        )
