"""
交互动作模块

实现元素交互相关的操作（选择、输入、点击等）
"""

import time
import random
from typing import TYPE_CHECKING, List, Tuple, Optional

if TYPE_CHECKING:
    from ..context import ExecutionContext

from ..errors import ExecutionError


def execute_select(
    element_type: str,
    conditions: List[Tuple[str, str, str]],
    context: 'ExecutionContext',
    line: int = 0
):
    """
    选择元素

    Args:
        element_type: 元素类型（input, button, etc.）
        conditions: 属性条件列表 [(attr, operator, value), ...]
                   operator: "=", "contains", "equals", "matches"
        context: 执行上下文
        line: 行号
    """
    page = context.get_page()

    # 构建选择器
    selector = _build_selector(element_type, conditions, context)

    context.logger.info(f"选择元素: {element_type} -> {selector}")

    try:
        locator = page.locator(selector)
        count = locator.count()

        if count == 0:
            # 尝试备用定位策略
            locator = _try_alternative_locators(page, element_type, conditions, context)
            count = locator.count() if locator else 0

        if count == 0:
            # 捕获错误截图
            screenshot_path = context.screenshot_manager.capture_on_error(
                page, "element_not_found", line
            )

            # v3.0: 条件格式为 (attr, operator, value)
            conditions_str = ", ".join(f"{k} {op} {v!r}" for k, op, v in conditions)
            raise ExecutionError(
                line=line,
                statement=f"select {element_type} where {conditions_str}",
                error_type=ExecutionError.ELEMENT_NOT_FOUND,
                message=f"未找到元素: {selector}",
                screenshot_path=screenshot_path
            )

        # 设置当前元素
        context.set_current_element(locator)

        context.add_execution_record(
            record_type="select",
            content=f"select {element_type} -> {selector} (找到 {count} 个)",
            success=True
        )

        context.logger.info(f"✓ 选中元素: {selector} (找到 {count} 个)")

    except ExecutionError:
        raise
    except Exception as e:
        raise ExecutionError(
            line=line,
            statement=f"select {element_type}",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"选择元素失败: {e}"
        )


def _build_selector(
    element_type: str,
    conditions: List[Tuple[str, str, str]],
    context: 'ExecutionContext'
) -> str:
    """
    构建选择器 (支持 CSS 和 XPath)

    Args:
        element_type: 元素类型
        conditions: 属性条件列表 [(attr, operator, value), ...]
        context: 执行上下文

    Returns:
        CSS 选择器字符串或 XPath 选择器字符串
    """
    # 检查是否有 xpath 或 css 条件
    for attr, operator, value in conditions:
        if attr == 'xpath':
            # 如果指定了 xpath，直接使用 XPath 定位器
            resolved_value = context.resolve_variables(value)
            return f"xpath={resolved_value}"
        elif attr == 'css':
            # 如果指定了 css，直接使用 CSS 选择器（忽略 element_type）
            resolved_value = context.resolve_variables(value)
            return resolved_value  # 直接返回 CSS 选择器，不需要前缀

    # 元素类型映射
    type_map = {
        'input': 'input',
        'button': 'button',
        'link': 'a',
        'textarea': 'textarea',
        'div': 'div',
        'span': 'span',
        'element': '*',
    }

    base = type_map.get(element_type, element_type)

    if not conditions:
        return base

    # 构建属性选择器
    # v3.1: 条件格式为 (attr, operator, value)
    # value 可以是字符串、标识符引用或表达式对象
    selectors = []
    for attr, operator, value in conditions:
        # v3.1: 如果 value 是表达式对象，先求值
        if hasattr(value, '__class__') and hasattr(value.__class__, '__name__'):
            # 检查是否是 Expression 对象（通过类型检查）
            from ..ast_nodes import Expression
            if isinstance(value, Expression):
                # 求值表达式
                from ..executor import evaluate_expression
                resolved_value = str(evaluate_expression(value, context))
            else:
                # 字符串或其他类型，直接解析变量
                resolved_value = context.resolve_variables(value)
        else:
            # 字符串或其他类型，直接解析变量
            resolved_value = context.resolve_variables(value)

        if attr == 'text':
            # 文本匹配需要特殊处理
            # 根据 operator 选择匹配方式
            if operator == 'contains':
                selectors.append(f":has-text(\"{resolved_value}\")")
            else:  # = 或 equals
                selectors.append(f":text-is(\"{resolved_value}\")")
        elif attr == 'class':
            selectors.append(f".{resolved_value}")
        elif attr == 'id':
            selectors.append(f"#{resolved_value}")
        else:
            selectors.append(f"[{attr}=\"{resolved_value}\"]")

    return base + "".join(selectors)


def _try_alternative_locators(
    page,
    element_type: str,
    conditions: List[Tuple[str, str, str]],
    context: 'ExecutionContext'
):
    """
    尝试备用定位策略

    Args:
        page: Playwright Page 对象
        element_type: 元素类型
        conditions: 属性条件列表 [(attr, operator, value), ...]
        context: 执行上下文

    Returns:
        Locator 或 None
    """
    for attr, operator, value in conditions:
        # v3.1: 如果 value 是表达式对象，先求值
        if hasattr(value, '__class__') and hasattr(value.__class__, '__name__'):
            from ..ast_nodes import Expression
            if isinstance(value, Expression):
                from ..executor import evaluate_expression
                resolved_value = str(evaluate_expression(value, context))
            else:
                resolved_value = context.resolve_variables(value)
        else:
            resolved_value = context.resolve_variables(value)

        try:
            # 尝试 placeholder
            if attr == 'placeholder':
                locator = page.get_by_placeholder(resolved_value)
                if locator.count() > 0:
                    return locator

            # 尝试 label
            if attr == 'label':
                locator = page.get_by_label(resolved_value)
                if locator.count() > 0:
                    return locator

            # 尝试 role
            if attr == 'role':
                locator = page.get_by_role(resolved_value)
                if locator.count() > 0:
                    return locator

            # 尝试 test id
            if attr == 'testid':
                locator = page.get_by_test_id(resolved_value)
                if locator.count() > 0:
                    return locator

            # 尝试文本
            if attr == 'text':
                locator = page.get_by_text(resolved_value)
                if locator.count() > 0:
                    return locator

        except:
            continue

    return None


def execute_type(
    text: str,
    mode: Optional[str],
    context: 'ExecutionContext',
    line: int = 0
):
    """
    输入文本

    Args:
        text: 要输入的文本（可能包含变量引用）
        mode: 输入模式（slowly, fast）
        context: 执行上下文
        line: 行号
    """
    # 解析变量
    resolved_text = context.resolve_variables(text)

    context.logger.info(f"输入文本: {resolved_text[:20]}{'...' if len(resolved_text) > 20 else ''}")

    try:
        element = context.get_current_element().first

        # 确保元素可见
        if not element.is_visible():
            element.scroll_into_view_if_needed()
            time.sleep(0.3)

        # 聚焦
        element.focus()
        time.sleep(0.2)

        # 清空
        element.clear()
        time.sleep(0.1)

        # 输入
        if mode == "fast":
            # 快速填充
            element.fill(resolved_text)
        else:
            # 默认慢速输入（模拟人类）
            for char in resolved_text:
                element.type(char)
                time.sleep(random.uniform(0.05, 0.15))

        # 等待
        time.sleep(random.uniform(0.3, 0.8))

        context.add_execution_record(
            record_type="type",
            content=f"type {mode or 'slowly'} '{resolved_text[:20]}...'",
            success=True
        )

        context.logger.info(f"✓ 输入完成")

    except ExecutionError:
        raise
    except Exception as e:
        raise ExecutionError(
            line=line,
            statement=f"type {text}",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"输入失败: {e}"
        )


def execute_click(
    click_type: str,
    wait_duration: Optional[float],
    context: 'ExecutionContext',
    line: int = 0
):
    """
    点击元素

    Args:
        click_type: 点击类型（click, double_click, right_click）
        wait_duration: 点击后等待时间（秒）
        context: 执行上下文
        line: 行号
    """
    context.logger.info(f"执行: {click_type}")

    try:
        element = context.get_current_element().first

        # 确保元素可见
        if not element.is_visible():
            element.scroll_into_view_if_needed()
            time.sleep(0.5)

        # 随机延迟（模拟人类）
        time.sleep(random.uniform(0.3, 0.8))

        # 执行点击
        if click_type == "double_click":
            element.dblclick()
        elif click_type == "right_click":
            element.click(button="right")
        else:
            element.click()

        # 等待
        if wait_duration:
            time.sleep(wait_duration)
        else:
            time.sleep(random.uniform(0.3, 0.8))

        context.add_execution_record(
            record_type="click",
            content=f"{click_type}" + (f" and wait {wait_duration}s" if wait_duration else ""),
            success=True
        )

        context.logger.info(f"✓ {click_type} 完成")

    except ExecutionError:
        raise
    except Exception as e:
        # 捕获错误截图
        try:
            page = context.get_page()
            screenshot_path = context.screenshot_manager.capture_on_error(
                page, "click_failed", line
            )
        except:
            screenshot_path = None

        raise ExecutionError(
            line=line,
            statement=click_type,
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"点击失败: {e}",
            screenshot_path=screenshot_path
        )


def execute_hover(
    selector: Optional[str],
    context: 'ExecutionContext',
    line: int = 0
):
    """
    悬停在元素上

    Args:
        selector: 选择器（可选，None 表示悬停在当前元素）
        context: 执行上下文
        line: 行号
    """
    context.logger.info(f"悬停: {selector or '当前元素'}")

    try:
        if selector:
            # 悬停在指定元素
            resolved_selector = context.resolve_variables(selector)
            page = context.get_page()
            element = page.locator(resolved_selector).first
        else:
            # 悬停在当前选中元素
            element = context.get_current_element().first

        element.hover()
        time.sleep(random.uniform(0.3, 0.8))

        context.add_execution_record(
            record_type="hover",
            content=f"hover {selector or 'current'}",
            success=True
        )

        context.logger.info(f"✓ 悬停完成")

    except ExecutionError:
        raise
    except Exception as e:
        raise ExecutionError(
            line=line,
            statement=f"hover {selector or ''}",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"悬停失败: {e}"
        )


def execute_clear(context: 'ExecutionContext', line: int = 0):
    """
    清空输入框

    Args:
        context: 执行上下文
        line: 行号
    """
    context.logger.info("清空输入框")

    try:
        element = context.get_current_element().first
        element.clear()

        context.add_execution_record(
            record_type="clear",
            content="clear",
            success=True
        )

        context.logger.info("✓ 已清空")

    except ExecutionError:
        raise
    except Exception as e:
        raise ExecutionError(
            line=line,
            statement="clear",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"清空失败: {e}"
        )


def execute_press(key_name: str, context: 'ExecutionContext', line: int = 0):
    """
    按下键盘按键

    Args:
        key_name: 按键名称
        context: 执行上下文
        line: 行号
    """
    context.logger.info(f"按键: {key_name}")

    try:
        element = context.get_current_element().first
        element.press(key_name)

        context.add_execution_record(
            record_type="press",
            content=f"press {key_name}",
            success=True
        )

        context.logger.info(f"✓ 按键 {key_name} 完成")

    except ExecutionError:
        raise
    except Exception as e:
        raise ExecutionError(
            line=line,
            statement=f"press {key_name}",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"按键失败: {e}"
        )


def execute_scroll(
    target: str,
    selector: Optional[str],
    context: 'ExecutionContext',
    line: int = 0
):
    """
    滚动页面

    Args:
        target: 滚动目标（top, bottom, element）
        selector: 元素选择器（当 target 为 element 时）
        context: 执行上下文
        line: 行号
    """
    context.logger.info(f"滚动到: {target} {selector or ''}")

    try:
        page = context.get_page()

        if target == "top":
            page.evaluate("window.scrollTo(0, 0)")
        elif target == "bottom":
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        elif target == "element" and selector:
            resolved_selector = context.resolve_variables(selector)
            element = page.locator(resolved_selector).first
            element.scroll_into_view_if_needed()

        time.sleep(0.5)

        context.add_execution_record(
            record_type="scroll",
            content=f"scroll to {target} {selector or ''}",
            success=True
        )

        context.logger.info(f"✓ 滚动完成")

    except Exception as e:
        raise ExecutionError(
            line=line,
            statement=f"scroll to {target}",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"滚动失败: {e}"
        )


def execute_check(
    action: str,
    selector: str,
    context: 'ExecutionContext',
    line: int = 0
):
    """
    复选框操作

    Args:
        action: 操作类型（check, uncheck）
        selector: 选择器
        context: 执行上下文
        line: 行号
    """
    resolved_selector = context.resolve_variables(selector)
    context.logger.info(f"{action}: {resolved_selector}")

    try:
        page = context.get_page()
        element = page.locator(resolved_selector).first

        if action == "check":
            element.check()
        else:
            element.uncheck()

        context.add_execution_record(
            record_type="check",
            content=f"{action} {resolved_selector}",
            success=True
        )

        context.logger.info(f"✓ {action} 完成")

    except Exception as e:
        raise ExecutionError(
            line=line,
            statement=f"{action} {selector}",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"{action} 失败: {e}"
        )


def execute_upload(
    file_path: str,
    selector: str,
    context: 'ExecutionContext',
    line: int = 0
):
    """
    文件上传

    Args:
        file_path: 文件路径
        selector: 上传控件选择器
        context: 执行上下文
        line: 行号
    """
    resolved_path = context.resolve_variables(file_path)
    resolved_selector = context.resolve_variables(selector)

    context.logger.info(f"上传文件: {resolved_path} -> {resolved_selector}")

    try:
        page = context.get_page()
        element = page.locator(resolved_selector).first
        element.set_input_files(resolved_path)

        context.add_execution_record(
            record_type="upload",
            content=f"upload {resolved_path}",
            success=True
        )

        context.logger.info(f"✓ 上传完成")

    except Exception as e:
        raise ExecutionError(
            line=line,
            statement=f"upload file {file_path}",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"上传失败: {e}"
        )


def execute_select_option(
    option_value: str,
    selector: str,
    context: 'ExecutionContext',
    line: int = 0
):
    """
    选择下拉框选项

    Args:
        option_value: 选项值
        selector: 下拉框选择器
        context: 执行上下文
        line: 行号
    """
    resolved_value = context.resolve_variables(option_value)
    resolved_selector = context.resolve_variables(selector)

    context.logger.info(f"选择选项: {resolved_value} from {resolved_selector}")

    try:
        page = context.get_page()
        element = page.locator(resolved_selector).first
        element.select_option(resolved_value)

        context.add_execution_record(
            record_type="select_option",
            content=f"select option {resolved_value}",
            success=True
        )

        context.logger.info(f"✓ 选择完成")

    except Exception as e:
        raise ExecutionError(
            line=line,
            statement=f"select option {option_value}",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"选择选项失败: {e}"
        )
