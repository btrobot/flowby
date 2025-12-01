"""
系统命名空间代理

v3.0 变更：移除 $ 前缀，系统变量作为内置全局对象访问

设计：
    - v2.0: $page.url  → 词法分析识别 SystemVariable
    - v3.0: page.url   → 运行时识别为系统命名空间代理
"""

from typing import Any, TYPE_CHECKING

# 类型检查时导入（避免循环导入）
if TYPE_CHECKING:
    from .system_variables import SystemVariables


class SystemNamespaceProxy:
    """
    通用系统命名空间代理

    用于将 page.url, context.task_id 等访问转发到 SystemVariables

    工作原理:
        page.url → SystemNamespaceProxy("page", sys_vars).__getattr__("url")
                 → sys_vars.get("page.url", 0)

    Examples:
        >>> sys_vars = SystemVariables(context)
        >>> page = SystemNamespaceProxy("page", sys_vars)
        >>> url = page.url  # 实际调用 sys_vars.get("page.url", 0)
    """

    def __init__(self, namespace: str, sys_vars: "SystemVariables"):
        """
        初始化系统命名空间代理

        Args:
            namespace: 命名空间名称 (page, context, browser, env, config)
            sys_vars: SystemVariables 实例
        """
        # 使用 object.__setattr__ 避免触发 __setattr__
        object.__setattr__(self, "_namespace", namespace)
        object.__setattr__(self, "_sys_vars", sys_vars)

    def __getattr__(self, attr: str) -> Any:
        """
        动态属性访问

        Args:
            attr: 属性名称 (如 "url", "title", "task_id")

        Returns:
            SystemVariables.get() 返回的值

        Raises:
            RuntimeError: 如果系统变量不存在
        """
        # 防止访问内部属性
        if attr.startswith("_"):
            raise AttributeError(f"'{self._namespace}' object has no attribute '{attr}'")

        # 构造完整路径并查询
        path = f"{self._namespace}.{attr}"
        return self._sys_vars.get(path, line_number=0)

    def __setattr__(self, attr: str, value: Any) -> None:
        """
        禁止修改系统变量

        Raises:
            RuntimeError: 系统变量只读
        """
        raise RuntimeError(f"不能修改系统变量: {self._namespace}.{attr} 是只读的")

    def __repr__(self) -> str:
        """调试信息"""
        return f"<SystemNamespace: {self._namespace}>"


# 系统命名空间列表（保留字）
SYSTEM_NAMESPACES = {
    "page",  # 页面状态 (url, title, origin, pathname, width, height)
    "context",  # 执行上下文 (task_id, step_name, step_index)
    "browser",  # 浏览器信息 (name, version, userAgent)
    "env",  # 环境变量 (env.API_KEY)
    "config",  # 配置变量 (config.base_url)
}
