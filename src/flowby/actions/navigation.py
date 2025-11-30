"""
导航动作模块

实现页面导航相关的操作
"""

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..context import ExecutionContext

from ..errors import ExecutionError


def execute_navigate_to(url: str, context: 'ExecutionContext', line: int = 0):
    """
    导航到指定 URL

    Args:
        url: 目标 URL（可能包含变量引用）
        context: 执行上下文
        line: 行号（用于错误报告）
    """
    # 解析变量
    resolved_url = context.resolve_variables(url)

    context.logger.info(f"导航到: {resolved_url}")

    try:
        page = context.get_page()

        # 导航
        page.goto(
            resolved_url,
            wait_until="networkidle",
            timeout=30000
        )

        # 清空当前元素上下文
        context.clear_current_element()

        # 记录执行
        context.add_execution_record(
            record_type="navigate",
            content=f"navigate to {resolved_url}",
            success=True
        )

        context.logger.info(f"✓ 导航成功: {resolved_url}")

    except Exception as e:
        error_msg = str(e)

        # 捕获错误截图
        try:
            page = context.get_page()
            screenshot_path = context.screenshot_manager.capture_on_error(
                page, "navigation_failed", line
            )
        except:
            screenshot_path = None

        raise ExecutionError(
            line=line,
            statement=f"navigate to {resolved_url}",
            error_type=ExecutionError.NAVIGATION_FAILED,
            message=f"导航失败: {error_msg}",
            screenshot_path=screenshot_path
        )


def execute_go_back(context: 'ExecutionContext', line: int = 0):
    """
    返回上一页

    Args:
        context: 执行上下文
        line: 行号
    """
    context.logger.info("返回上一页")

    try:
        page = context.get_page()
        page.go_back(wait_until="networkidle", timeout=30000)

        # 清空当前元素上下文
        context.clear_current_element()

        context.add_execution_record(
            record_type="navigate",
            content="go back",
            success=True
        )

        context.logger.info("✓ 已返回上一页")

    except Exception as e:
        raise ExecutionError(
            line=line,
            statement="go back",
            error_type=ExecutionError.NAVIGATION_FAILED,
            message=f"返回上一页失败: {e}"
        )


def execute_go_forward(context: 'ExecutionContext', line: int = 0):
    """
    前进到下一页

    Args:
        context: 执行上下文
        line: 行号
    """
    context.logger.info("前进到下一页")

    try:
        page = context.get_page()
        page.go_forward(wait_until="networkidle", timeout=30000)

        # 清空当前元素上下文
        context.clear_current_element()

        context.add_execution_record(
            record_type="navigate",
            content="go forward",
            success=True
        )

        context.logger.info("✓ 已前进到下一页")

    except Exception as e:
        raise ExecutionError(
            line=line,
            statement="go forward",
            error_type=ExecutionError.NAVIGATION_FAILED,
            message=f"前进到下一页失败: {e}"
        )


def execute_reload(context: 'ExecutionContext', line: int = 0):
    """
    刷新当前页面

    Args:
        context: 执行上下文
        line: 行号
    """
    context.logger.info("刷新页面")

    try:
        page = context.get_page()
        page.reload(wait_until="networkidle", timeout=30000)

        # 清空当前元素上下文
        context.clear_current_element()

        context.add_execution_record(
            record_type="navigate",
            content="reload",
            success=True
        )

        context.logger.info("✓ 页面已刷新")

    except Exception as e:
        raise ExecutionError(
            line=line,
            statement="reload",
            error_type=ExecutionError.NAVIGATION_FAILED,
            message=f"刷新页面失败: {e}"
        )
