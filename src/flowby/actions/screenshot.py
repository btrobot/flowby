"""
截图动作模块

实现截图操作
"""

import time
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..context import ExecutionContext

from ..errors import ExecutionError


def execute_screenshot(
    name: Optional[str],
    context: 'ExecutionContext',
    line: int = 0,
    fullpage: bool = False
):
    """
    截图

    Args:
        name: 截图名称（可选）
        context: 执行上下文
        line: 行号
        fullpage: 是否截取完整页面（包括滚动区域）
    """
    # 解析变量（如果名称包含变量引用）
    resolved_name = context.resolve_variables(name) if name else None

    screenshot_type = "完整页面截图" if fullpage else "截图"
    context.logger.info(f"{screenshot_type}: {resolved_name or '自动命名'}")

    try:
        page = context.get_page()

        # 使用截图管理器，传递 fullpage 参数（不传递 line）
        screenshot_path = context.screenshot_manager.capture(
            page=page,
            name=resolved_name or f"screenshot_line{line}",
            fullpage=fullpage
        )

        # 记录截图路径
        context.screenshots.append(screenshot_path)

        context.add_execution_record(
            record_type="screenshot",
            content=f"screenshot {'fullpage ' if fullpage else ''}{resolved_name or 'auto'}",
            success=True
        )

        context.logger.info(f"✓ {screenshot_type}已保存: {screenshot_path}")

        return screenshot_path

    except Exception as e:
        raise ExecutionError(
            line=line,
            statement=f"screenshot {'fullpage ' if fullpage else ''}{name or ''}",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"截图失败: {e}"
        )


def execute_screenshot_element(
    selector: str,
    name: Optional[str],
    context: 'ExecutionContext',
    line: int = 0
):
    """
    截取元素截图

    Args:
        selector: 元素选择器
        name: 截图名称（可选）
        context: 执行上下文
        line: 行号
    """
    resolved_selector = context.resolve_variables(selector)
    resolved_name = context.resolve_variables(name) if name else None

    context.logger.info(f"截取元素: {resolved_selector}")

    try:
        page = context.get_page()
        element = page.locator(resolved_selector).first

        # 确保元素可见
        element.scroll_into_view_if_needed()
        time.sleep(0.3)

        # 截取元素截图
        screenshot_path = context.screenshot_manager.capture_element(
            element=element,
            name=resolved_name,
            line=line
        )

        # 记录截图路径
        context.screenshots.append(screenshot_path)

        context.add_execution_record(
            record_type="screenshot",
            content=f"screenshot element {resolved_selector}",
            success=True
        )

        context.logger.info(f"✓ 元素截图已保存: {screenshot_path}")

        return screenshot_path

    except Exception as e:
        raise ExecutionError(
            line=line,
            statement=f"screenshot element {selector}",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"元素截图失败: {e}"
        )


def execute_screenshot_fullpage(
    name: Optional[str],
    context: 'ExecutionContext',
    line: int = 0
):
    """
    截取完整页面截图（包括滚动区域）

    Args:
        name: 截图名称（可选）
        context: 执行上下文
        line: 行号
    """
    resolved_name = context.resolve_variables(name) if name else None

    context.logger.info(f"截取完整页面: {resolved_name or '自动命名'}")

    try:
        page = context.get_page()

        # 使用截图管理器截取完整页面
        screenshot_path = context.screenshot_manager.capture_fullpage(
            page=page,
            name=resolved_name,
            line=line
        )

        # 记录截图路径
        context.screenshots.append(screenshot_path)

        context.add_execution_record(
            record_type="screenshot",
            content=f"screenshot fullpage {resolved_name or 'auto'}",
            success=True
        )

        context.logger.info(f"✓ 完整页面截图已保存: {screenshot_path}")

        return screenshot_path

    except Exception as e:
        raise ExecutionError(
            line=line,
            statement=f"screenshot fullpage {name or ''}",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"完整页面截图失败: {e}"
        )
