"""
模块系统 (v5.0)

提供模块加载、缓存和循环导入检测功能

核心组件:
- ModuleInfo: 模块信息数据类
- ModuleLoader: 模块加载器，负责路径解析、缓存和循环导入检测

设计原则:
- 每个模块在一次执行中只加载一次（缓存机制）
- 完全禁止循环导入（运行时检测）
- 只支持相对路径（安全考虑）
- 使用绝对路径作为缓存键（避免路径混淆）
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class ModuleInfo:
    """
    模块信息

    封装模块的元数据和导出成员

    Attributes:
        path: 模块的绝对路径
        library_name: library 声明的名称
        exports: 导出的成员字典 {成员名: 值}
        ast: 解析后的 AST (Program 节点)

    Example:
        >>> module_info = ModuleInfo(
        ...     path=Path("/path/to/logging.flow"),
        ...     library_name="logging",
        ...     exports={"log_info": function_object},
        ...     ast=program_node
        ... )
    """

    path: Path
    library_name: str
    exports: Dict[str, Any] = field(default_factory=dict)
    ast: Optional[Any] = None  # Program AST 节点

    def __repr__(self):
        export_count = len(self.exports)
        return f"ModuleInfo(library={self.library_name}, exports={export_count}, path={self.path})"


class ModuleLoader:
    """
    模块加载器

    负责模块的加载、缓存和循环导入检测

    功能:
    1. 路径解析 - 将相对路径解析为绝对路径
    2. 模块缓存 - 避免重复加载同一模块
    3. 循环导入检测 - 检测并拒绝循环依赖

    使用示例:
        >>> loader = ModuleLoader()
        >>> module_info = loader.load_module("libs/logging.flow", current_file)
        >>> logging = module_info.exports

    线程安全性:
        当前实现不是线程安全的，假设单线程执行
    """

    def __init__(self):
        """初始化模块加载器"""
        # 模块缓存：绝对路径 -> ModuleInfo
        self._cache: Dict[Path, ModuleInfo] = {}

        # 导入栈：用于循环导入检测（存储绝对路径）
        self._import_stack: List[Path] = []

    def resolve_path(self, relative_path: str, current_file: Path) -> Path:
        """
        解析相对路径为绝对路径

        路径解析规则:
        1. 相对于当前文件的目录
        2. 自动添加 .flow 扩展名（如果缺失）
        3. 规范化路径（解析 .. 和 .）
        4. 拒绝绝对路径（安全考虑）

        Args:
            relative_path: 相对路径字符串（如 "libs/logging.flow"）
            current_file: 当前文件的绝对路径

        Returns:
            解析后的绝对路径

        Raises:
            ValueError: 如果提供绝对路径

        Examples:
            >>> loader = ModuleLoader()
            >>> current = Path("/project/flows/main.flow")
            >>> resolved = loader.resolve_path("libs/logging.flow", current)
            >>> resolved
            Path('/project/flows/libs/logging.flow')
        """
        # 检查是否是绝对路径（安全限制）
        # Windows: C:/, Unix: /
        if Path(relative_path).is_absolute():
            raise ValueError(f"不支持绝对路径: {relative_path}（只允许相对路径）")

        # 检查是否包含驱动器号 (Windows)
        if len(relative_path) >= 2 and relative_path[1] == ":":
            raise ValueError(f"不支持绝对路径: {relative_path}（只允许相对路径）")

        # 检查是否以 / 开头 (Unix 绝对路径)
        if relative_path.startswith("/"):
            raise ValueError(f"不支持绝对路径: {relative_path}（只允许相对路径）")

        # 获取当前文件所在目录
        # 如果 current_file 有扩展名，认为它是文件，取其父目录
        # 否则，认为它是目录
        if current_file.suffix:
            current_dir = current_file.parent
        else:
            current_dir = current_file

        # 解析相对路径
        resolved_path = (current_dir / relative_path).resolve()

        # 如果没有扩展名，自动添加 .flow
        if not resolved_path.suffix:
            resolved_path = resolved_path.with_suffix(".flow")

        return resolved_path

    def check_circular_import(self, module_path: Path) -> bool:
        """
        检查循环导入

        通过检查导入栈来检测循环依赖

        Args:
            module_path: 模块的绝对路径

        Returns:
            True 如果检测到循环导入，False 否则

        Examples:
            >>> loader = ModuleLoader()
            >>> path_a = Path("/project/a.flow")
            >>> loader.enter_module(path_a)
            >>> loader.check_circular_import(path_a)
            True
        """
        return module_path in self._import_stack

    def enter_module(self, module_path: Path):
        """
        进入模块加载（推入导入栈）

        在开始加载模块时调用，用于循环导入检测

        Args:
            module_path: 模块的绝对路径
        """
        self._import_stack.append(module_path)

    def exit_module(self, module_path: Path):
        """
        退出模块加载（弹出导入栈）

        在完成加载模块后调用，清理导入栈

        Args:
            module_path: 模块的绝对路径
        """
        if self._import_stack and self._import_stack[-1] == module_path:
            self._import_stack.pop()

    def is_cached(self, module_path: Path) -> bool:
        """
        检查模块是否已缓存

        Args:
            module_path: 模块的绝对路径

        Returns:
            True 如果模块已缓存，False 否则
        """
        return module_path in self._cache

    def get_cached(self, module_path: Path) -> Optional[ModuleInfo]:
        """
        获取缓存的模块

        Args:
            module_path: 模块的绝对路径

        Returns:
            ModuleInfo 对象，如果未缓存则返回 None
        """
        return self._cache.get(module_path)

    def cache_module(self, module_path: Path, module_info: ModuleInfo):
        """
        缓存模块

        Args:
            module_path: 模块的绝对路径
            module_info: 模块信息对象
        """
        self._cache[module_path] = module_info

    def get_import_chain(self) -> List[str]:
        """
        获取当前导入链（用于错误报告）

        Returns:
            导入链字符串列表，格式为文件名

        Examples:
            >>> loader = ModuleLoader()
            >>> loader.enter_module(Path("/a.flow"))
            >>> loader.enter_module(Path("/b.flow"))
            >>> loader.get_import_chain()
            ['a.flow', 'b.flow']
        """
        return [path.name for path in self._import_stack]

    def validate_library_name(self, library_name: str, module_path: Path) -> bool:
        """
        验证 library 名称是否与文件名匹配

        根据设计决策，library 名称必须与文件名（不含扩展名）匹配

        Args:
            library_name: library 声明的名称
            module_path: 模块文件的绝对路径

        Returns:
            True 如果匹配，False 否则

        Examples:
            >>> loader = ModuleLoader()
            >>> path = Path("/project/libs/logging.flow")
            >>> loader.validate_library_name("logging", path)
            True
            >>> loader.validate_library_name("utils", path)
            False
        """
        file_stem = module_path.stem  # 获取文件名（不含扩展名）
        return library_name == file_stem

    def clear_cache(self):
        """
        清除所有缓存（用于测试或重置）
        """
        self._cache.clear()
        self._import_stack.clear()

    def __repr__(self):
        return f"ModuleLoader(cached={len(self._cache)}, import_depth={len(self._import_stack)})"
