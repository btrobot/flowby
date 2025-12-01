"""
断言动作模块

实现各种断言操作（assertion operations）
"""

import re
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..context import ExecutionContext
    from ..ast_nodes import Condition

from ..errors import ExecutionError
from ..diagnosis import DiagnosisLevel


def _capture_diagnosis(
    context: "ExecutionContext",
    error: Exception,
    error_type: str,
    line: int,
    statement: str,
    selector: str = "",
    diagnosis_level: Optional[str] = None,
) -> str:
    """
    捕获诊断信息

    Args:
        context: 执行上下文
        error: 异常对象
        error_type: 错误类型
        line: 行号
        statement: 语句内容
        selector: 选择器
        diagnosis_level: 诊断级别（如果为 None 使用默认配置）

    Returns:
        诊断目录路径
    """
    page = context.get_page()

    # 确定诊断级别
    level = None
    if diagnosis_level:
        level = DiagnosisLevel.from_string(diagnosis_level)

    return context.diagnosis_manager.capture_diagnosis(
        page=page,
        context=context,
        error=error,
        error_type=error_type,
        level=level,
        statement=statement,
        line=line,
        selector=selector,
        listeners=context.diagnosis_listeners,
    )


def execute_assert_url(
    operator: str,
    expected: str,
    context: "ExecutionContext",
    line: int = 0,
    diagnosis_level: Optional[str] = None,
):
    """
    断言 URL

    Args:
        operator: 操作符（contains, equals, matches）
        expected: 期望值
        context: 执行上下文
        line: 行号
        diagnosis_level: 诊断级别
    """
    # 解析变量
    resolved_expected = context.resolve_variables(expected)

    page = context.get_page()
    current_url = page.url

    context.logger.info(f"断言 URL {operator} {resolved_expected!r}")

    result = False
    if operator == "contains":
        result = resolved_expected in current_url
    elif operator == "equals":
        result = current_url == resolved_expected
    elif operator == "matches":
        result = re.search(resolved_expected, current_url) is not None

    if not result:
        error = Exception(
            f"URL 断言失败: 当前 URL '{current_url}' 不 {operator} '{resolved_expected}'"
        )
        statement = f"assert url {operator} {expected}"

        # 捕获诊断信息
        diagnosis_path = _capture_diagnosis(
            context=context,
            error=error,
            error_type="ASSERTION_FAILED",
            line=line,
            statement=statement,
            diagnosis_level=diagnosis_level,
        )

        raise ExecutionError(
            line=line,
            statement=statement,
            error_type=ExecutionError.ASSERTION_FAILED,
            message=str(error),
            screenshot_path=diagnosis_path,
        )

    context.add_execution_record(
        record_type="assert", content=f"assert url {operator} {resolved_expected}", success=True
    )

    context.logger.info(f"✓ URL 断言通过")


def execute_assert_element(
    state: str,
    selector: str,
    context: "ExecutionContext",
    line: int = 0,
    diagnosis_level: Optional[str] = None,
):
    """
    断言元素状态

    Args:
        state: 状态（exists, visible, hidden）
        selector: 选择器
        context: 执行上下文
        line: 行号
        diagnosis_level: 诊断级别
    """
    # 解析变量
    resolved_selector = context.resolve_variables(selector)

    page = context.get_page()
    locator = page.locator(resolved_selector)

    context.logger.info(f"断言元素 {state}: {resolved_selector}")

    try:
        if state == "exists":
            count = locator.count()
            if count == 0:
                raise Exception(f"元素不存在: {resolved_selector}")

        elif state == "visible":
            element = locator.first
            if not element.is_visible():
                raise Exception(f"元素不可见: {resolved_selector}")

        elif state == "hidden":
            element = locator.first
            if element.is_visible():
                raise Exception(f"元素应该隐藏但实际可见: {resolved_selector}")

        context.add_execution_record(
            record_type="assert",
            content=f"assert element {state} {resolved_selector}",
            success=True,
        )

        context.logger.info(f"✓ 元素断言通过")

    except Exception as e:
        statement = f"assert element {state} {selector}"

        # 捕获诊断信息
        diagnosis_path = _capture_diagnosis(
            context=context,
            error=e,
            error_type="ELEMENT_NOT_FOUND" if state == "exists" else "ASSERTION_FAILED",
            line=line,
            statement=statement,
            selector=resolved_selector,
            diagnosis_level=diagnosis_level,
        )

        raise ExecutionError(
            line=line,
            statement=statement,
            error_type=ExecutionError.ASSERTION_FAILED,
            message=str(e),
            screenshot_path=diagnosis_path,
        )


def execute_assert_text(
    operator: str,
    expected: str,
    selector: str,
    context: "ExecutionContext",
    line: int = 0,
    diagnosis_level: Optional[str] = None,
):
    """
    断言文本内容

    Args:
        operator: 操作符（contains, equals）
        expected: 期望值
        selector: 选择器（可选）
        context: 执行上下文
        line: 行号
        diagnosis_level: 诊断级别
    """
    # 解析变量
    resolved_expected = context.resolve_variables(expected)
    resolved_selector = context.resolve_variables(selector) if selector else None

    page = context.get_page()

    context.logger.info(f"断言文本 {operator} {resolved_expected!r}")

    try:
        if resolved_selector:
            element = page.locator(resolved_selector).first
            actual_text = element.text_content() or ""
        else:
            actual_text = page.text_content("body") or ""

        result = False
        if operator == "contains":
            result = resolved_expected in actual_text
        elif operator == "equals":
            result = actual_text.strip() == resolved_expected

        if not result:
            raise Exception(f"文本断言失败: 实际文本不 {operator} '{resolved_expected}'")

        context.add_execution_record(
            record_type="assert",
            content=f"assert text {operator} {resolved_expected}",
            success=True,
        )

        context.logger.info(f"✓ 文本断言通过")

    except Exception as e:
        statement = f"assert text {operator} {expected}"

        # 捕获诊断信息
        diagnosis_path = _capture_diagnosis(
            context=context,
            error=e,
            error_type="ASSERTION_FAILED",
            line=line,
            statement=statement,
            selector=resolved_selector or "",
            diagnosis_level=diagnosis_level,
        )

        raise ExecutionError(
            line=line,
            statement=statement,
            error_type=ExecutionError.ASSERTION_FAILED,
            message=str(e),
            screenshot_path=diagnosis_path,
        )


def execute_assert_value(
    operator: str,
    expected: str,
    selector: str,
    context: "ExecutionContext",
    line: int = 0,
    diagnosis_level: Optional[str] = None,
):
    """
    断言输入框的值

    Args:
        operator: 操作符（contains, equals）
        expected: 期望值
        selector: 选择器
        context: 执行上下文
        line: 行号
        diagnosis_level: 诊断级别
    """
    # 解析变量
    resolved_expected = context.resolve_variables(expected)
    resolved_selector = context.resolve_variables(selector)

    page = context.get_page()

    context.logger.info(f"断言值 {operator} {resolved_expected!r} in {resolved_selector}")

    try:
        element = page.locator(resolved_selector).first
        actual_value = element.input_value()

        result = False
        if operator == "contains":
            result = resolved_expected in actual_value
        elif operator == "equals":
            result = actual_value == resolved_expected

        if not result:
            raise Exception(
                f"值断言失败: 实际值 '{actual_value}' 不 {operator} '{resolved_expected}'"
            )

        context.add_execution_record(
            record_type="assert",
            content=f"assert value {operator} {resolved_expected}",
            success=True,
        )

        context.logger.info(f"✓ 值断言通过")

    except Exception as e:
        statement = f"assert value {operator} {expected}"

        # 捕获诊断信息
        diagnosis_path = _capture_diagnosis(
            context=context,
            error=e,
            error_type="ASSERTION_FAILED",
            line=line,
            statement=statement,
            selector=resolved_selector,
            diagnosis_level=diagnosis_level,
        )

        raise ExecutionError(
            line=line,
            statement=statement,
            error_type=ExecutionError.ASSERTION_FAILED,
            message=str(e),
            screenshot_path=diagnosis_path,
        )


def _check_condition(condition: "Condition", context: "ExecutionContext") -> bool:
    """
    检查条件是否满足（用于 wait until 和条件语句）

    Args:
        condition: 条件表达式
        context: 执行上下文

    Returns:
        条件是否满足
    """
    page = context.get_page()

    # URL 条件
    if condition.condition_type == "url":
        current_url = page.url
        resolved_value = context.resolve_variables(condition.value) if condition.value else ""

        if condition.operator == "contains":
            return resolved_value in current_url
        elif condition.operator == "equals":
            return current_url == resolved_value
        elif condition.operator == "matches":
            return re.search(resolved_value, current_url) is not None

    # 元素条件
    if condition.condition_type == "element":
        resolved_selector = (
            context.resolve_variables(condition.selector) if condition.selector else ""
        )
        locator = page.locator(resolved_selector)

        if condition.operator == "exists":
            return locator.count() > 0
        elif condition.operator == "visible":
            try:
                return locator.first.is_visible()
            except Exception:
                return False
        elif condition.operator == "hidden":
            try:
                return not locator.first.is_visible()
            except Exception:
                return True

    # 文本条件
    if condition.condition_type == "text":
        resolved_value = context.resolve_variables(condition.value) if condition.value else ""

        if condition.selector:
            resolved_selector = context.resolve_variables(condition.selector)
            try:
                element = page.locator(resolved_selector).first
                actual_text = element.text_content() or ""
            except Exception:
                actual_text = ""
        else:
            actual_text = page.text_content("body") or ""

        if condition.operator == "contains":
            return resolved_value in actual_text
        elif condition.operator == "equals":
            return actual_text.strip() == resolved_value

    return False
