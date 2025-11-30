"""
等待动作模块

实现各种等待操作
"""

import time
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..context import ExecutionContext
    from ..ast_nodes import Condition, Expression
    from ..expression_evaluator import ExpressionEvaluator

from ..errors import ExecutionError


def execute_wait_duration(duration: float, context: 'ExecutionContext', line: int = 0):
    """
    等待固定时间

    Args:
        duration: 等待时间（秒）
        context: 执行上下文
        line: 行号
    """
    context.logger.info(f"等待 {duration} 秒")

    time.sleep(duration)

    context.add_execution_record(
        record_type="wait",
        content=f"wait {duration}s",
        duration=duration,
        success=True
    )


def execute_wait_for_state(state: str, context: 'ExecutionContext', line: int = 0):
    """
    等待页面状态

    Args:
        state: 页面状态（networkidle, domcontentloaded, load）
        context: 执行上下文
        line: 行号
    """
    context.logger.info(f"等待页面状态: {state}")

    try:
        page = context.get_page()
        page.wait_for_load_state(state=state, timeout=30000)

        context.add_execution_record(
            record_type="wait",
            content=f"wait for {state}",
            success=True
        )

        context.logger.info(f"✓ 页面状态达到: {state}")

    except Exception as e:
        raise ExecutionError(
            line=line,
            statement=f"wait for {state}",
            error_type=ExecutionError.TIMEOUT,
            message=f"等待页面状态 {state} 超时: {e}"
        )


def execute_wait_for_element(
    selector: str,
    state: Optional[str],
    context: 'ExecutionContext',
    line: int = 0
):
    """
    等待元素出现或达到指定状态

    Args:
        selector: CSS/XPath 选择器
        state: 元素状态（visible, hidden, attached, detached）
        context: 执行上下文
        line: 行号
    """
    # 解析变量
    resolved_selector = context.resolve_variables(selector)
    element_state = state or "attached"

    context.logger.info(f"等待元素 {element_state}: {resolved_selector}")

    try:
        page = context.get_page()
        locator = page.locator(resolved_selector)
        locator.wait_for(state=element_state, timeout=10000)

        context.add_execution_record(
            record_type="wait",
            content=f"wait for element {element_state} {resolved_selector}",
            success=True
        )

        context.logger.info(f"✓ 元素已 {element_state}: {resolved_selector}")

    except Exception as e:
        # 捕获错误截图
        try:
            page = context.get_page()
            screenshot_path = context.screenshot_manager.capture_on_error(
                page, "element_wait_timeout", line
            )
        except:
            screenshot_path = None

        raise ExecutionError(
            line=line,
            statement=f"wait for element {element_state} {resolved_selector}",
            error_type=ExecutionError.TIMEOUT,
            message=f"等待元素 {resolved_selector} ({element_state}) 超时: {e}",
            screenshot_path=screenshot_path
        )


def execute_wait_for_navigation(context: 'ExecutionContext', line: int = 0):
    """
    等待导航完成

    Args:
        context: 执行上下文
        line: 行号
    """
    context.logger.info("等待导航完成")

    try:
        page = context.get_page()
        page.wait_for_load_state("networkidle", timeout=30000)

        context.add_execution_record(
            record_type="wait",
            content="wait for navigation",
            success=True
        )

        context.logger.info("✓ 导航已完成")

    except Exception as e:
        raise ExecutionError(
            line=line,
            statement="wait for navigation",
            error_type=ExecutionError.TIMEOUT,
            message=f"等待导航超时: {e}"
        )


def execute_wait_until(
    condition: 'Condition',
    context: 'ExecutionContext',
    line: int = 0
):
    """
    等待条件满足

    Args:
        condition: 条件表达式
        context: 执行上下文
        line: 行号
    """
    from .assertion import _check_condition

    context.logger.info(f"等待条件: {condition.condition_type} {condition.operator}")

    start_time = time.time()
    timeout = 30.0
    poll_interval = 0.5

    while time.time() - start_time < timeout:
        try:
            if _check_condition(condition, context):
                context.add_execution_record(
                    record_type="wait",
                    content=f"wait until {condition.condition_type} {condition.operator}",
                    duration=time.time() - start_time,
                    success=True
                )
                context.logger.info(f"✓ 条件满足")
                return
        except:
            pass

        time.sleep(poll_interval)

    # 超时
    raise ExecutionError(
        line=line,
        statement=f"wait until {condition.condition_type} {condition.operator}",
        error_type=ExecutionError.TIMEOUT,
        message=f"等待条件超时（{timeout}秒）"
    )


def execute_wait_until_expression(
    condition: 'Expression',
    evaluator: 'ExpressionEvaluator',
    context: 'ExecutionContext',
    line: int = 0,
    timeout: float = 30.0,
    poll_interval: float = 0.5
):
    """
    等待直到条件表达式为真 (v2.0)

    Args:
        condition: 条件表达式
        evaluator: 表达式求值器
        context: 执行上下文
        line: 行号
        timeout: 超时时间（秒）
        poll_interval: 轮询间隔（秒）

    Raises:
        ExecutionError: 超时或条件评估失败
    """
    context.logger.info(f"等待条件表达式满足")

    start_time = time.time()

    while True:
        try:
            # 评估条件表达式
            result = evaluator.evaluate(condition)

            # 转换为布尔值
            from ..expression_evaluator import to_boolean
            if to_boolean(result):
                elapsed = time.time() - start_time
                context.add_execution_record(
                    record_type="wait",
                    content=f"wait until expression",
                    duration=elapsed,
                    success=True
                )
                context.logger.info(f"✓ 条件满足 (耗时 {elapsed:.1f}s)")
                return
        except Exception as e:
            context.logger.debug(f"条件评估失败: {e}")

        # 检查超时
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise ExecutionError(
                line=line,
                statement="wait until",
                error_type=ExecutionError.TIMEOUT,
                message=f"等待条件超时 ({timeout}s)"
            )

        # 等待轮询间隔
        time.sleep(poll_interval)
