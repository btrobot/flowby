"""
符号表系统

实现变量作用域管理，支持符号表栈和符号表链。

设计原则:
    1. 符号表栈 - 管理作用域层次（Global → Step → Block）
    2. 符号链 - 支持向上查找（子作用域可访问父作用域）
    3. 符号遮蔽 - 局部变量可以遮蔽全局变量
    4. 常量保护 - 常量不可修改

参考规范: flows/SEMANTICS.md 第 1.2 节
"""

from enum import Enum
from typing import Any, Optional, Dict, List
from dataclasses import dataclass


class SymbolType(Enum):
    """
    符号类型枚举

    VARIABLE - 可变变量（let 定义）
    CONSTANT - 常量（const 定义）
    SYSTEM - 系统变量（只读，如 $context, $page）
    FUNCTION - 函数（function 定义，v4.3）
    LOOP_VARIABLE - 循环变量（for 循环，v6.3）
    PARAMETER - 函数参数（function 参数，v6.3）
    MODULE - 导入的模块别名（import alias from ..., v6.3）
    IMPORTED - 导入的成员（from ... import member, v6.3）
    """

    VARIABLE = "variable"
    CONSTANT = "constant"
    SYSTEM = "system"
    FUNCTION = "function"  # v4.3
    LOOP_VARIABLE = "loop_variable"  # v6.3
    PARAMETER = "parameter"  # v6.3
    MODULE = "module"  # v6.3
    IMPORTED = "imported"  # v6.3


@dataclass
class Symbol:
    """
    符号表项

    表示变量或常量的元信息

    Attributes:
        name: 符号名称
        value: 符号值
        symbol_type: 符号类型（VARIABLE/CONSTANT/SYSTEM）
        line_number: 定义行号（用于错误报告）
        is_used: 是否被使用（v6.3 - VR-006 未使用变量警告）
    """

    name: str
    value: Any
    symbol_type: SymbolType
    line_number: int
    is_used: bool = False  # v6.3: VR-006 未使用变量追踪

    def mark_used(self):
        """
        标记符号已使用（v6.3 - VR-006）

        用于追踪变量使用情况，避免未使用变量警告
        """
        self.is_used = True

    def is_mutable(self) -> bool:
        """
        检查符号是否可修改

        可变类型：
        - VARIABLE: let 声明的变量
        - LOOP_VARIABLE: for 循环变量（v6.3）
        - PARAMETER: 函数参数（v6.3）

        不可变类型：
        - CONSTANT: const 声明的常量
        - SYSTEM: 系统变量
        - FUNCTION: 函数定义
        - MODULE: 导入的模块别名（v6.3）
        - IMPORTED: 导入的成员（v6.3）

        Returns:
            True 如果是可变变量，False 如果是常量或系统变量
        """
        return self.symbol_type in (
            SymbolType.VARIABLE,
            SymbolType.LOOP_VARIABLE,  # v6.3: 循环变量可修改
            SymbolType.PARAMETER,  # v6.3: 函数参数可修改
        )

        return (
            f"Symbol(name={self.name!r}, "
            f"type={self.symbol_type.value}, "
            f"value={self.value!r}, "
            f"line={self.line_number})"
        )


@dataclass
class FunctionSymbol(Symbol):
    """
    函数符号表项 (v5.1 - 支持闭包, v6.0.1 - 添加源文件路径)

    扩展 Symbol 类，用于存储函数定义的元信息

    Attributes:
        name: 函数名
        value: None (函数符号不存储值)
        symbol_type: SymbolType.FUNCTION
        line_number: 函数定义行号
        params: 参数名列表
        body: 函数体 AST 节点列表
        closure_scope: 定义时的符号表引用（闭包作用域）v5.1 新增
        source_file: 函数定义所在的文件路径（v6.0.1 新增，用于错误定位）
    """

    params: list = None  # 参数名列表
    body: list = None  # 函数体 AST 节点列表
    closure_scope: Optional["SymbolTable"] = None  # v5.1: 闭包作用域
    source_file: Optional[str] = None  # v6.0.1: 函数定义所在的文件路径

    def __post_init__(self):
        """初始化后处理：确保 params 和 body 不为 None"""
        if self.params is None:
            self.params = []
        if self.body is None:
            self.body = []

    def mark_used(self):
        """
        标记符号已使用（v6.3 - VR-006）

        用于追踪变量使用情况，避免未使用变量警告
        """
        self.is_used = True

    def is_mutable(self) -> bool:
        """函数符号不可修改"""
        return False

    def __repr__(self) -> str:
        closure_info = f", closure={self.closure_scope.scope_name}" if self.closure_scope else ""
        return (
            f"FunctionSymbol(name={self.name!r}, "
            f"params={self.params}, "
            f"line={self.line_number}{closure_info})"
        )


class SymbolTable:
    """
    符号表 - 管理单个作用域的变量

    设计特点:
        - 链式结构：每个符号表可以有父符号表
        - 向上查找：如果当前作用域找不到，向父作用域查找
        - 作用域隔离：定义只在当前作用域，赋值向上查找

    Attributes:
        symbols: 当前作用域的符号字典
        parent: 父作用域符号表（None 表示全局作用域）
        scope_name: 作用域名称（用于调试）

    Examples:
        >>> global_table = SymbolTable("global")
        >>> global_table.define("MAX", 100, SymbolType.CONSTANT, line=1)
        >>>
        >>> step_table = SymbolTable("step", parent=global_table)
        >>> step_table.define("count", 0, SymbolType.VARIABLE, line=5)
        >>>
        >>> step_table.get("MAX")  # 可以访问父作用域
        100
        >>> step_table.set("count", 1, line=6)  # 修改当前作用域
    """

    def __init__(self, scope_name: str = "global", parent: Optional["SymbolTable"] = None):
        """
        初始化符号表

        Args:
            scope_name: 作用域名称（用于调试和错误报告）
            parent: 父作用域符号表（None 表示全局作用域）
        """
        self.symbols: Dict[str, Symbol] = {}
        self.parent: Optional[SymbolTable] = parent
        self.scope_name = scope_name

    def define(self, name: str, value: Any, symbol_type: SymbolType, line_number: int) -> None:
        """
        在当前作用域定义新符号

        Args:
            name: 符号名称
            value: 符号值
            symbol_type: 符号类型（VARIABLE/CONSTANT/SYSTEM）
            line_number: 定义行号

        Raises:
            RuntimeError: 如果符号已存在于当前作用域

        Examples:
            >>> table = SymbolTable("global")
            >>> table.define("username", "alice", SymbolType.VARIABLE, line=1)
            >>> table.define("MAX", 100, SymbolType.CONSTANT, line=2)
        """
        # v3.0+: 检查保留字（系统命名空间和内置命名空间）
        RESERVED_SYSTEM_NAMESPACES = {
            # v3.0 系统命名空间
            "page",
            "context",
            "browser",
            "env",
            "config",
            # v1.0 内置函数命名空间
            "Math",
            "Date",
            "JSON",
            "UUID",
            "Hash",
            "Base64",
            # v3.1 服务命名空间
            "random",
            "http",
        }
        if name in RESERVED_SYSTEM_NAMESPACES:
            raise RuntimeError(
                f"不能定义变量 '{name}'：这是保留的命名空间 (line {line_number})\n"
                f"保留字: {', '.join(sorted(RESERVED_SYSTEM_NAMESPACES))}"
            )

        if name in self.symbols:
            raise RuntimeError(
                f"符号 '{name}' 已在当前作用域 '{self.scope_name}' 中定义 "
                f"(line {self.symbols[name].line_number})"
            )

        symbol = Symbol(name=name, value=value, symbol_type=symbol_type, line_number=line_number)
        self.symbols[name] = symbol

    def set(self, name: str, value: Any, line_number: int) -> None:
        """
        设置符号值（向上查找）

        如果当前作用域有该符号，修改当前作用域
        否则向父作用域查找，直到找到或报错

        Args:
            name: 符号名称
            value: 新值
            line_number: 赋值行号

        Raises:
            RuntimeError: 如果符号未定义
            RuntimeError: 如果尝试修改常量或系统变量

        Examples:
            >>> table = SymbolTable("global")
            >>> table.define("count", 0, SymbolType.VARIABLE, line=1)
            >>> table.set("count", 10, line=2)  # ✅ 成功
            >>>
            >>> table.define("MAX", 100, SymbolType.CONSTANT, line=3)
            >>> table.set("MAX", 200, line=4)  # ❌ 错误：不能修改常量
        """
        # 向上查找符号
        symbol = self._lookup(name)

        if symbol is None:
            raise RuntimeError(f"未定义的变量: {name} (line {line_number})")

        # 检查是否可修改
        if not symbol.is_mutable():
            raise RuntimeError(
                f"不能修改 {symbol.symbol_type.value}: {name} "
                f"(定义于 line {symbol.line_number}, 修改于 line {line_number})"
            )

        # v6.3: VR-006 - 标记符号已使用（赋值也是使用）
        symbol.mark_used()

        # 修改值
        symbol.value = value

    def get(self, name: str, line_number: int) -> Any:
        """
        获取符号值（向上查找）

        Args:
            name: 符号名称
            line_number: 引用行号

        Returns:
            符号值

        Raises:
            RuntimeError: 如果符号未定义

        Examples:
            >>> global_table = SymbolTable("global")
            >>> global_table.define("MAX", 100, SymbolType.CONSTANT, line=1)
            >>>
            >>> step_table = SymbolTable("step", parent=global_table)
            >>> step_table.get("MAX", line=5)  # 可以访问父作用域
            100
        """
        symbol = self._lookup(name)

        if symbol is None:
            raise RuntimeError(f"未定义的变量: {name} (line {line_number})")

        # v6.3: VR-006 - 标记符号已使用
        symbol.mark_used()

        return symbol.value

    def exists(self, name: str) -> bool:
        """
        检查符号是否存在（向上查找）

        Args:
            name: 符号名称

        Returns:
            True 如果符号存在，False 否则

        Examples:
            >>> table = SymbolTable("global")
            >>> table.define("username", "alice", SymbolType.VARIABLE, line=1)
            >>> table.exists("username")
            True
            >>> table.exists("password")
            False
        """
        return self._lookup(name) is not None

    def exists_in_current_scope(self, name: str) -> bool:
        """
        检查符号是否存在于当前作用域（不向上查找）

        用于检查变量重复声明，不考虑父作用域的同名变量。

        Args:
            name: 符号名称

        Returns:
            True 如果符号存在于当前作用域，False 否则

        Examples:
            >>> global_table = SymbolTable("global")
            >>> global_table.define("email", "g@test.com", SymbolType.VARIABLE, line=1)
            >>>
            >>> block_table = SymbolTable("block", parent=global_table)
            >>> block_table.exists("email")  # True - 从父作用域找到
            True
            >>> block_table.exists_in_current_scope("email")  # False - 当前作用域没有
            False
            >>> block_table.define("email", "b@test.com", SymbolType.VARIABLE, line=5)
            >>> block_table.exists_in_current_scope("email")  # True - 变量遮蔽
            True
        """
        return name in self.symbols

    def _lookup(self, name: str) -> Optional[Symbol]:
        """
        向上查找符号（内部方法）

        从当前作用域开始，向父作用域递归查找

        Args:
            name: 符号名称

        Returns:
            找到的符号，如果未找到返回 None
        """
        # 当前作用域查找
        if name in self.symbols:
            return self.symbols[name]

        # 向父作用域查找
        if self.parent is not None:
            return self.parent._lookup(name)

        # 未找到
        return None

    def get_all_symbols(self) -> Dict[str, Symbol]:
        """
        获取当前作用域的所有符号（不包括父作用域）

        Returns:
            符号字典
        """
        return self.symbols.copy()

    def __repr__(self) -> str:
        parent_name = self.parent.scope_name if self.parent else None
        return (
            f"SymbolTable(scope={self.scope_name!r}, "
            f"parent={parent_name!r}, "
            f"symbols={list(self.symbols.keys())})"
        )


class SymbolTableStack:
    """
    符号表栈 - 管理作用域栈

    设计特点:
        - 栈结构：全局作用域在栈底，当前作用域在栈顶
        - 自动链接：新作用域自动链接到当前作用域作为父
        - 作用域管理：enter/exit 控制作用域生命周期

    Attributes:
        stack: 符号表栈（全局作用域在索引 0）

    Examples:
        >>> stack = SymbolTableStack()
        >>> stack.define("MAX", 100, SymbolType.CONSTANT, line=1)
        >>>
        >>> stack.enter_scope("step")
        >>> stack.define("count", 0, SymbolType.VARIABLE, line=5)
        >>> stack.get("MAX")  # 可以访问全局变量
        100
        >>>
        >>> stack.exit_scope()
        >>> # 现在 count 已销毁
    """

    def __init__(self):
        """初始化符号表栈，创建全局作用域"""
        global_table = SymbolTable("global", parent=None)
        self.stack: List[SymbolTable] = [global_table]

    def current_scope(self) -> SymbolTable:
        """
        获取当前作用域的符号表

        Returns:
            栈顶的符号表
        """
        return self.stack[-1]

    def enter_scope(self, scope_name: str) -> None:
        """
        进入新作用域

        创建新符号表，链接到当前作用域作为父

        Args:
            scope_name: 新作用域名称

        Examples:
            >>> stack = SymbolTableStack()
            >>> stack.enter_scope("step_1")
            >>> stack.enter_scope("if_block")
            >>> # 现在作用域层次: global → step_1 → if_block
        """
        parent = self.current_scope()
        new_table = SymbolTable(scope_name, parent=parent)
        self.stack.append(new_table)

    def enter_scope_with_parent(self, scope_name: str, parent: Optional["SymbolTable"]) -> None:
        """
        进入新作用域，指定父作用域（v5.1 - 支持闭包）

        用于创建函数局部作用域时指定闭包作用域作为父

        Args:
            scope_name: 新作用域名称
            parent: 父作用域（闭包作用域）

        Examples:
            >>> stack = SymbolTableStack()
            >>> closure_scope = SymbolTable("library_scope")
            >>> stack.enter_scope_with_parent("function:my_func", parent=closure_scope)
            >>> # 新作用域的 parent 是 closure_scope，而不是栈顶
        """
        new_table = SymbolTable(scope_name, parent=parent)
        self.stack.append(new_table)

    def exit_scope(self) -> None:
        """
        退出当前作用域

        弹出栈顶符号表，销毁当前作用域

        Raises:
            RuntimeError: 如果尝试退出全局作用域

        Examples:
            >>> stack = SymbolTableStack()
            >>> stack.enter_scope("step")
            >>> stack.exit_scope()  # ✅ 成功
            >>> stack.exit_scope()  # ❌ 错误：不能退出全局作用域
        """
        if len(self.stack) <= 1:
            raise RuntimeError("不能退出全局作用域")

        self.stack.pop()

    def define(self, name: str, value: Any, symbol_type: SymbolType, line_number: int) -> None:
        """在当前作用域定义符号"""
        self.current_scope().define(name, value, symbol_type, line_number)

    def set(self, name: str, value: Any, line_number: int) -> None:
        """设置符号值（向上查找）"""
        self.current_scope().set(name, value, line_number)

    def get(self, name: str, line_number: int) -> Any:
        """获取符号值（向上查找）"""
        return self.current_scope().get(name, line_number)

    def exists(self, name: str) -> bool:
        """检查符号是否存在（向上查找）"""
        return self.current_scope().exists(name)

    def exists_in_current_scope(self, name: str) -> bool:
        """
        检查符号是否存在于当前作用域（不向上查找）

        用于 VR-VAR-003 重复声明检查，只检查当前作用域，不检查父作用域。
        这允许变量遮蔽（在子作用域中声明与父作用域同名的变量）。

        Returns:
            True 如果符号存在于当前作用域，False 否则

        Examples:
            >>> stack = SymbolTableStack()
            >>> stack.define("email", "g@test.com", SymbolType.VARIABLE, line=1)
            >>>
            >>> stack.enter_scope("if_block")
            >>> stack.exists("email")  # True - 从父作用域找到
            True
            >>> stack.exists_in_current_scope("email")  # False - 当前作用域没有
            False
            >>> stack.define("email", "local@test.com", SymbolType.VARIABLE, line=10)  # 允许遮蔽
            >>> stack.exists_in_current_scope("email")  # True
            True
        """
        return self.current_scope().exists_in_current_scope(name)

    def scope_depth(self) -> int:
        """
        获取当前作用域深度

        Returns:
            作用域深度（全局作用域为 0）
        """
        return len(self.stack) - 1

    def get_all_symbols(self) -> Dict[str, Symbol]:
        """
        获取所有作用域的所有符号（v6.3 - VR-006）

        遍历整个作用域栈，收集所有符号。
        如果同名符号在多个作用域中存在，返回最内层（最近）的符号。

        Returns:
            符号字典，key 为符号名称，value 为 Symbol 对象
        """
        all_symbols: Dict[str, Symbol] = {}

        # 从底层（全局）到顶层（当前作用域）遍历
        for table in self.stack:
            # 获取当前作用域的所有符号
            for name, symbol in table.symbols.items():
                # 只记录尚未记录的符号（优先记录外层作用域）
                if name not in all_symbols:
                    all_symbols[name] = symbol

        return all_symbols

    def __repr__(self) -> str:
        scope_names = [table.scope_name for table in self.stack]
        return f"SymbolTableStack(depth={self.scope_depth()}, scopes={scope_names})"
