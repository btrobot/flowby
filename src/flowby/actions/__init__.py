"""
动作模块包

实现 DSL 语句的具体操作

模块:
    - navigation: 页面导航操作
    - interaction: 元素交互操作
    - assertion: 断言操作（assertion operations）
    - screenshot: 截图操作
"""

from .navigation import (
    execute_navigate_to,
    execute_go_back,
    execute_go_forward,
    execute_reload,
)

from .interaction import (
    execute_select,
    execute_type,
    execute_click,
    execute_hover,
    execute_clear,
    execute_press,
    execute_scroll,
    execute_check,
    execute_upload,
    execute_select_option,
)

from .assertion import (
    execute_assert_url,
    execute_assert_element,
    execute_assert_text,
    execute_assert_value,
)

from .screenshot import execute_screenshot

from .wait import (
    execute_wait_duration,
    execute_wait_for_state,
    execute_wait_for_element,
    execute_wait_for_navigation,
    execute_wait_until,
)

__all__ = [
    # 导航
    "execute_navigate_to",
    "execute_go_back",
    "execute_go_forward",
    "execute_reload",
    # 等待
    "execute_wait_duration",
    "execute_wait_for_state",
    "execute_wait_for_element",
    "execute_wait_for_navigation",
    "execute_wait_until",
    # 交互
    "execute_select",
    "execute_type",
    "execute_click",
    "execute_hover",
    "execute_clear",
    "execute_press",
    "execute_scroll",
    "execute_check",
    "execute_upload",
    "execute_select_option",
    # 断言（assertion）
    "execute_assert_url",
    "execute_assert_element",
    "execute_assert_text",
    "execute_assert_value",
    # 截图
    "execute_screenshot",
]
