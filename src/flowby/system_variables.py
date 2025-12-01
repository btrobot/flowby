"""
系统变量提供者

提供运行时系统变量，如 $context, $page, $element, $env, $config

设计原则:
    1. 只读 - 系统变量不能被用户修改
    2. 动态 - 系统变量值动态获取（如 $page.url）
    3. 命名空间 - 使用 $ 前缀区分系统变量和用户变量

支持的系统变量:
    - $context.*  - 执行上下文（task_id, step_name, step_index 等）
    - $page.*     - 页面状态（url, title, origin, pathname, width, height）
    - $browser.*  - 浏览器信息（name, version, userAgent）
    - $element.*  - 当前元素（text, value, visible, enabled, attr.*）
    - $data.*     - 运行时数据存储（用户自定义数据）
    - $env.*      - 环境变量（从 os.environ 读取）
    - $config.*   - 配置变量（从 variables.yaml 读取）

参考规范: flows/SEMANTICS.md 第 2.4 节
"""

import os
from typing import Any, Optional, Dict
from playwright.sync_api import Page, Locator


class SystemVariables:
    """
    系统变量提供者

    提供运行时系统变量的访问接口

    Attributes:
        context: 执行上下文引用（用于访问 task_id, step_name 等）
        config_vars: 配置变量字典（从 variables.yaml 加载）
        data_store: 运行时数据存储（用于 $data.* 变量）

    Examples:
        >>> sys_vars = SystemVariables(context, config_vars={"base_url": "https://example.com"})
        >>> sys_vars.get("context.task_id")
        "12345678-1234-1234-1234-123456789012"
        >>> sys_vars.get("page.url")
        "https://example.com/login"
        >>> sys_vars.get("config.base_url")
        "https://example.com"
    """

    def __init__(self, context: Any, config_vars: Optional[Dict[str, Any]] = None):
        """
        初始化系统变量提供者

        Args:
            context: 执行上下文（ExecutionContext 实例）
            config_vars: 配置变量字典（可选）
        """
        self.context = context
        self.config_vars = config_vars or {}
        self.data_store: Dict[str, Any] = {}  # 运行时数据存储

    def get(self, path: str, line_number: int = 0) -> Any:
        """
        获取系统变量值

        Args:
            path: 系统变量路径（不含 $ 前缀），如 "context.task_id", "page.url"
            line_number: 引用行号（用于错误报告）

        Returns:
            系统变量值

        Raises:
            RuntimeError: 如果命名空间或属性不存在

        Examples:
            >>> sys_vars.get("context.task_id")
            "12345678-1234-1234-1234-123456789012"
            >>> sys_vars.get("page.url")
            "https://example.com/login"
            >>> sys_vars.get("env.API_TOKEN")
            "secret_token_12345"
        """
        parts = path.split(".", 1)  # 最多分割一次
        namespace = parts[0]

        if len(parts) == 1:
            # 只有命名空间，如 "$context"
            raise RuntimeError(
                f"系统变量需要指定属性: ${path} (line {line_number})\n"
                f"例如: $context.task_id, $page.url"
            )

        property_path = parts[1]  # 剩余部分，如 "task_id" 或 "attr.id"

        # 路由到对应的命名空间处理器
        if namespace == "context":
            return self._get_context_var(property_path, line_number)
        elif namespace == "page":
            return self._get_page_var(property_path, line_number)
        elif namespace == "browser":
            return self._get_browser_var(property_path, line_number)
        elif namespace == "element":
            return self._get_element_var(property_path, line_number)
        elif namespace == "data":
            return self._get_data_var(property_path, line_number)
        elif namespace == "env":
            return self._get_env_var(property_path, line_number)
        elif namespace == "config":
            return self._get_config_var(property_path, line_number)
        else:
            raise RuntimeError(
                f"未知的系统变量命名空间: ${namespace} (line {line_number})\n"
                f"支持的命名空间: $context, $page, $browser, $element, $data, $env, $config"
            )

    def _get_context_var(self, property_name: str, line_number: int) -> Any:
        """
        获取上下文变量 ($context.*)

        支持的属性:
            - task_id: 任务 ID
            - execution_id: 执行 ID（同 task_id）
            - step_name: 当前步骤名称
            - step_index: 当前步骤索引
            - line_number: 当前行号
            - total_steps: 总步骤数（未实现）
            - completed_steps: 已完成步骤数（未实现）
            - failed_steps: 失败步骤数（未实现）

        Args:
            property_name: 属性名称
            line_number: 引用行号

        Returns:
            属性值

        Raises:
            RuntimeError: 如果属性不存在
        """
        if property_name == "task_id":
            return self.context.task_id
        elif property_name == "execution_id":
            return self.context.task_id  # 同 task_id
        elif property_name == "step_name":
            return self.context.current_step or ""
        elif property_name == "step_index":
            # TODO: 实现步骤索引跟踪
            return 0
        elif property_name == "line_number":
            return line_number
        else:
            raise RuntimeError(
                f"未知的上下文属性: $context.{property_name} (line {line_number})\n"
                f"支持的属性: task_id, execution_id, step_name, step_index, line_number"
            )

    def _get_page_var(self, property_name: str, line_number: int) -> Any:
        """
        获取页面状态变量 ($page.*)

        支持的属性:
            - url: 当前 URL
            - title: 页面标题
            - origin: 协议+域名（如 "https://example.com"）
            - pathname: 路径（如 "/login"）
            - width: 视口宽度
            - height: 视口高度

        Args:
            property_name: 属性名称
            line_number: 引用行号

        Returns:
            属性值

        Raises:
            RuntimeError: 如果页面未初始化或属性不存在
        """
        page = self._get_page(line_number)

        if property_name == "url":
            return page.url
        elif property_name == "title":
            return page.title()
        elif property_name == "origin":
            # 提取协议+域名
            url = page.url
            if "://" in url:
                protocol_and_rest = url.split("://", 1)
                protocol = protocol_and_rest[0]
                rest = protocol_and_rest[1]
                domain = rest.split("/", 1)[0]
                return f"{protocol}://{domain}"
            return ""
        elif property_name == "pathname":
            # 提取路径
            url = page.url
            if "://" in url:
                rest = url.split("://", 1)[1]
                if "/" in rest:
                    return "/" + rest.split("/", 1)[1]
            return "/"
        elif property_name == "width":
            # 视口宽度
            size = page.viewport_size
            return size["width"] if size else 0
        elif property_name == "height":
            # 视口高度
            size = page.viewport_size
            return size["height"] if size else 0
        else:
            raise RuntimeError(
                f"未知的页面属性: $page.{property_name} (line {line_number})\n"
                f"支持的属性: url, title, origin, pathname, width, height"
            )

    def _get_browser_var(self, property_name: str, line_number: int) -> Any:
        """
        获取浏览器信息变量 ($browser.*)

        支持的属性:
            - name: 浏览器名称（chromium, firefox, webkit）
            - version: 浏览器版本
            - userAgent: User-Agent 字符串

        Args:
            property_name: 属性名称
            line_number: 引用行号

        Returns:
            属性值

        Raises:
            RuntimeError: 如果页面未初始化或属性不存在
        """
        page = self._get_page(line_number)

        if property_name == "name":
            # 从 context 获取浏览器名称
            browser_name = getattr(self.context, "browser_name", "chromium")
            return browser_name
        elif property_name == "version":
            # 通过 JavaScript 获取浏览器版本
            return page.evaluate("navigator.appVersion")
        elif property_name == "userAgent":
            # 通过 JavaScript 获取 User-Agent
            return page.evaluate("navigator.userAgent")
        else:
            raise RuntimeError(
                f"未知的浏览器属性: $browser.{property_name} (line {line_number})\n"
                f"支持的属性: name, version, userAgent"
            )

    def _get_data_var(self, var_path: str, line_number: int) -> Any:
        """
        获取数据存储变量 ($data.*)

        从运行时数据存储中读取变量
        支持嵌套路径，如 "user.name"

        Args:
            var_path: 数据变量路径（如 "myKey" 或 "user.name"）
            line_number: 引用行号

        Returns:
            数据变量值

        Raises:
            RuntimeError: 如果数据变量不存在

        Examples:
            >>> sys_vars.set_data("myKey", "myValue")
            >>> sys_vars._get_data_var("myKey", 0)
            "myValue"
        """
        # 嵌套路径访问
        parts = var_path.split(".")
        current = self.data_store

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise RuntimeError(
                    f"数据存储中不存在键: $data.{var_path} (line {line_number})\n"
                    f"请先使用 set_data() 方法设置该变量"
                )

        return current

    def _get_element_var(self, property_path: str, line_number: int) -> Any:
        """
        获取元素变量 ($element.*)

        支持的属性:
            - text: 元素文本内容
            - value: 输入框值
            - visible: 是否可见
            - enabled: 是否启用
            - attr.<name>: HTML 属性值（如 attr.id, attr.class）

        Args:
            property_path: 属性路径（可能包含子路径，如 "attr.id"）
            line_number: 引用行号

        Returns:
            属性值

        Raises:
            RuntimeError: 如果没有选中元素或属性不存在
        """
        element = self._get_current_element(line_number)

        # 处理 attr.* 子路径
        if property_path.startswith("attr."):
            attr_name = property_path[5:]  # 去掉 "attr." 前缀
            return element.get_attribute(attr_name) or ""

        # 处理普通属性
        if property_path == "text":
            return element.inner_text()
        elif property_path == "value":
            return element.input_value()
        elif property_path == "visible":
            return element.is_visible()
        elif property_path == "enabled":
            return element.is_enabled()
        else:
            raise RuntimeError(
                f"未知的元素属性: $element.{property_path} (line {line_number})\n"
                f"支持的属性: text, value, visible, enabled, attr.<name>"
            )

    def _get_env_var(self, var_name: str, line_number: int) -> str:
        """
        获取环境变量 ($env.*)

        从 os.environ 读取环境变量

        Args:
            var_name: 环境变量名称
            line_number: 引用行号

        Returns:
            环境变量值

        Raises:
            RuntimeError: 如果环境变量不存在

        Examples:
            >>> os.environ["API_TOKEN"] = "secret_123"
            >>> sys_vars._get_env_var("API_TOKEN", 0)
            "secret_123"
        """
        if var_name in os.environ:
            return os.environ[var_name]
        else:
            raise RuntimeError(
                f"环境变量不存在: $env.{var_name} (line {line_number})\n"
                f"请设置环境变量或检查变量名是否正确"
            )

    def _get_config_var(self, var_path: str, line_number: int) -> Any:
        """
        获取配置变量 ($config.*)

        从配置文件（variables.yaml）读取变量
        支持嵌套路径，如 "api.token"

        Args:
            var_path: 配置变量路径（如 "base_url" 或 "api.token"）
            line_number: 引用行号

        Returns:
            配置变量值

        Raises:
            RuntimeError: 如果配置变量不存在

        Examples:
            >>> config_vars = {"base_url": "https://example.com", "api": {"token": "secret"}}
            >>> sys_vars = SystemVariables(context, config_vars)
            >>> sys_vars._get_config_var("base_url", 0)
            "https://example.com"
            >>> sys_vars._get_config_var("api.token", 0)
            "secret"
        """
        # 嵌套路径访问
        parts = var_path.split(".")
        current = self.config_vars

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise RuntimeError(
                    f"配置变量不存在: $config.{var_path} (line {line_number})\n"
                    f"请检查 variables.yaml 中是否定义了该变量"
                )

        return current

    def set_data(self, key: str, value: Any) -> None:
        """
        设置数据存储变量 (用于 $data.*)

        支持嵌套路径，如 "user.name"

        Args:
            key: 数据变量路径（如 "myKey" 或 "user.name"）
            value: 要设置的值

        Examples:
            >>> sys_vars.set_data("myKey", "myValue")
            >>> sys_vars.set_data("user.name", "Alice")
        """
        parts = key.split(".")

        if len(parts) == 1:
            # 简单键
            self.data_store[key] = value
        else:
            # 嵌套键 - 创建嵌套字典
            current = self.data_store
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value

    def _get_page(self, line_number: int) -> Page:
        """
        获取页面对象（内部方法）

        Args:
            line_number: 引用行号

        Returns:
            Playwright Page 对象

        Raises:
            RuntimeError: 如果页面未初始化
        """
        if self.context.page is None:
            raise RuntimeError(
                f"无法访问 $page.*: 页面未初始化 (line {line_number})\n"
                f"请先执行 navigate 语句打开页面"
            )
        return self.context.page

    def _get_current_element(self, line_number: int) -> Locator:
        """
        获取当前元素（内部方法）

        Args:
            line_number: 引用行号

        Returns:
            Playwright Locator 对象

        Raises:
            RuntimeError: 如果没有选中元素
        """
        if self.context.current_element is None:
            raise RuntimeError(
                f"无法访问 $element.*: 没有选中元素 (line {line_number})\n"
                f"请先执行 select 语句选择元素"
            )
        return self.context.current_element

    def __repr__(self) -> str:
        return (
            f"SystemVariables("
            f"task_id={self.context.task_id[:8]}..., "
            f"config_vars={list(self.config_vars.keys())}"
            f")"
        )
