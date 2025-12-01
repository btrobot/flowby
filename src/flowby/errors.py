"""
DSL 异常定义

定义了 DSL 解释器中使用的所有异常类型，提供清晰的错误信息和定位。

异常层次:
    DSLError (基类)
    ├── LexerError (词法分析错误)
    ├── ParserError (语法分析错误)
    └── ExecutionError (执行时错误)
"""

from typing import Optional, List
from dataclasses import dataclass

try:
    from colorama import Fore, Style, init

    # 初始化 colorama（Windows 支持）
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    # 如果 colorama 未安装，使用空字符串
    class Fore:
        RED = ""
        GREEN = ""
        YELLOW = ""
        CYAN = ""

    class Style:
        RESET_ALL = ""

    COLORS_AVAILABLE = False


class DSLError(Exception):
    """
    DSL 基础异常类（增强版）

    所有 DSL 相关异常的基类，提供增强的错误消息格式

    Attributes:
        line: 错误发生的行号
        column: 错误发生的列号
        error_type: 错误类型描述
        message: 错误消息
        file_path: 错误发生的文件路径（可选）
        source_lines: 源代码行列表
        expected: 期望的内容
        actual: 实际的内容
        suggestion: 修复建议
    """

    def __init__(
        self,
        line: int,
        column: int,
        error_type: str,
        message: str,
        file_path: Optional[str] = None,
        source_lines: Optional[List[str]] = None,
        expected: Optional[str] = None,
        actual: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        self.line = line
        self.column = column
        self.error_type = error_type
        self.msg = message  # 使用 msg 避免与 Exception.message 冲突
        self.file_path = file_path  # v6.0.1: 文件路径（用于模块导入错误定位）
        self.source_lines = source_lines or []
        self.expected = expected
        self.actual = actual
        self.suggestion = suggestion

        super().__init__(self._format_error())

    def _format_error(self) -> str:
        """格式化错误消息（增强版）"""
        lines = []

        # 错误标题
        title = f"{Fore.RED}[{self.error_type}]{Style.RESET_ALL} "

        # v6.0.1: 如果有文件路径，显示文件名
        if self.file_path:
            from pathlib import Path

            file_name = Path(self.file_path).name
            title += f"文件 {Fore.CYAN}{file_name}{Style.RESET_ALL}, "

        title += f"第 {Fore.YELLOW}{self.line}{Style.RESET_ALL} 行"
        if self.column > 0:
            title += f"，第 {Fore.YELLOW}{self.column}{Style.RESET_ALL} 列"
        title += f": {Fore.RED}{self.msg}{Style.RESET_ALL}"
        lines.append(title)
        lines.append("")

        # 代码上下文
        if self.source_lines:
            lines.extend(self._format_code_context())
            lines.append("")

        # 期望 vs 实际
        if self.expected or self.actual:
            if self.expected:
                lines.append(f"{Fore.GREEN}期望:{Style.RESET_ALL} {self.expected}")
            if self.actual:
                lines.append(f"{Fore.RED}实际:{Style.RESET_ALL} {self.actual}")
            lines.append("")

        # 修复建议
        if self.suggestion:
            lines.append(f"{Fore.CYAN}💡 提示:{Style.RESET_ALL} {self.suggestion}")
            lines.append("")

        return "\n".join(lines)

    def _format_code_context(self) -> List[str]:
        """格式化代码上下文"""
        lines = []
        context_range = 2  # 前后显示行数

        start_line = max(1, self.line - context_range)
        end_line = min(len(self.source_lines), self.line + context_range)

        for i in range(start_line, end_line + 1):
            line_num = i
            line_content = self.source_lines[i - 1] if i <= len(self.source_lines) else ""

            # 行号前缀
            if line_num == self.line:
                prefix = f"{Fore.RED}>{Style.RESET_ALL} {line_num:3d} | "
            else:
                prefix = f"  {line_num:3d} | "

            lines.append(prefix + line_content)

            # 错误位置指示
            if line_num == self.line and self.column > 0:
                indicator = " " * (len(prefix) + self.column - 1)
                indicator += f"{Fore.RED}^^^^^{Style.RESET_ALL}"
                lines.append(indicator)

        return lines


class LexerError(DSLError):
    """
    词法分析错误（增强版）

    在将源代码转换为 Token 流时发生的错误

    Attributes:
        line: 错误发生的行号（从 1 开始）
        column: 错误发生的列号（从 1 开始）
        message: 错误消息
        file_path: 错误发生的文件路径（可选，v6.0.1）
        source_line: 错误所在的源代码行（用于单行显示，向后兼容）
        source_lines: 完整源代码行列表（用于上下文显示）
        suggestion: 修复建议
    """

    def __init__(
        self,
        line: int,
        column: int,
        message: str,
        file_path: Optional[str] = None,
        source_line: Optional[str] = None,
        source_lines: Optional[List[str]] = None,
        suggestion: Optional[str] = None,
    ):
        # 如果只提供了 source_line，转换为 source_lines
        if source_line and not source_lines:
            source_lines = [source_line]

        super().__init__(
            line=line,
            column=column,
            error_type="词法错误",
            message=message,
            file_path=file_path,  # v6.0.1
            source_lines=source_lines,
            suggestion=suggestion,
        )

        # 保留向后兼容性
        self.source_line = source_line


class ParserError(DSLError):
    """
    语法分析错误（增强版）

    在将 Token 流转换为 AST 时发生的错误

    Attributes:
        line: 错误发生的行号
        column: 错误发生的列号
        token_type: 当前 Token 的类型
        token_value: 当前 Token 的值
        message: 错误消息
        file_path: 错误发生的文件路径（可选，v6.0.1）
        expected: 期望的 Token 类型（可选）
        source_lines: 完整源代码行列表
        suggestion: 修复建议
    """

    def __init__(
        self,
        line: int,
        column: int,
        token_type: str,
        token_value: str,
        message: str,
        file_path: Optional[str] = None,
        expected: Optional[str] = None,
        source_lines: Optional[List[str]] = None,
        suggestion: Optional[str] = None,
    ):
        self.token_type = token_type
        self.token_value = token_value

        # 构建实际值描述
        actual = f"{token_type}"
        if token_value:
            actual += f" ('{token_value}')"

        super().__init__(
            line=line,
            column=column,
            error_type="语法错误",
            message=message,
            file_path=file_path,  # v6.0.1
            source_lines=source_lines,
            expected=expected,
            actual=actual,
            suggestion=suggestion,
        )


class ExecutionError(DSLError):
    """
    执行时错误（增强版）

    在解释执行 AST 时发生的错误

    Attributes:
        line: 错误发生的行号
        statement: 错误发生时的语句描述
        error_type: 错误类型（ELEMENT_NOT_FOUND, TIMEOUT, etc.）
        message: 错误消息
        file_path: 错误发生的文件路径（可选，v6.0.1）
        screenshot_path: 错误时的截图路径（可选）
        source_lines: 完整源代码行列表
        suggestion: 修复建议
    """

    # 错误类型常量
    ELEMENT_NOT_FOUND = "元素未找到"
    TIMEOUT = "超时"
    NAVIGATION_FAILED = "导航失败"
    ASSERTION_FAILED = "断言失败"
    VERIFICATION_FAILED = "断言失败"  # 向后兼容别名
    INVALID_STATE = "无效状态"
    RUNTIME_ERROR = "运行时错误"
    VARIABLE_NOT_FOUND = "变量未找到"
    SERVICE_ERROR = "服务调用错误"
    INFINITE_LOOP_DETECTED = "死循环检测"  # v3.0: while 循环保护

    def __init__(
        self,
        line: int,
        statement: str,
        error_type: str,
        message: str,
        file_path: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        source_lines: Optional[List[str]] = None,
        suggestion: Optional[str] = None,
    ):
        self.statement = statement
        self.screenshot_path = screenshot_path

        # 添加截图路径到消息
        full_message = message
        if screenshot_path:
            full_message += f"\n{Fore.CYAN}📸 错误截图:{Style.RESET_ALL} {screenshot_path}"

        super().__init__(
            line=line,
            column=0,  # 执行错误通常不需要列号
            error_type=error_type,
            message=full_message,
            file_path=file_path,  # v6.0.1
            source_lines=source_lines,
            suggestion=suggestion,
        )


class ValidationError(Exception):
    """
    验证错误

    在验证 AST 或配置时发生的错误

    Attributes:
        message: 错误消息
        context: 额外的上下文信息（可选）
    """

    def __init__(self, message: str, context: Optional[str] = None):
        self.message = message
        self.context = context
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """格式化错误消息"""
        msg = f"{Fore.RED}[验证错误]{Style.RESET_ALL} {self.message}"

        if self.context:
            msg += f"\n{Fore.YELLOW}上下文:{Style.RESET_ALL} {self.context}"

        return msg


class ResourceError(Exception):
    """
    资源错误

    在分配或管理资源时发生的错误（浏览器、数据等）

    Attributes:
        resource_type: 资源类型（browser, user_data, etc.）
        message: 错误消息
    """

    def __init__(self, resource_type: str, message: str):
        self.resource_type = resource_type
        self.message = message
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """格式化错误消息"""
        return f"{Fore.RED}[资源错误]{Style.RESET_ALL} {self.resource_type}: {self.message}"


# 便捷函数


def format_error_with_context(error: Exception, flow_content: str) -> str:
    """
    格式化错误消息，包含源代码上下文

    Args:
        error: DSL 错误对象（DSLError 或其他异常）
        flow_content: .flow 文件的完整内容

    Returns:
        格式化后的错误消息，包含源代码上下文

    Note:
        此函数主要用于向后兼容。新的 DSLError 类已经内置了更好的格式化。
    """
    # 如果是新的 DSLError，已经包含了格式化，直接返回
    if isinstance(error, DSLError):
        return str(error)

    # 对于其他异常类型，尝试提取行号
    lines = flow_content.split("\n")

    if isinstance(error, (LexerError, ParserError, ExecutionError)):
        line_no = error.line
    else:
        # 无法提取行号，直接返回错误消息
        return str(error)

    # 构建上下文（旧格式，向后兼容）
    context_lines = []

    # 显示前 2 行
    for i in range(max(1, line_no - 2), line_no):
        if i <= len(lines):
            context_lines.append(f"{i:4d} | {lines[i - 1]}")

    # 显示错误行（高亮）
    if line_no <= len(lines):
        context_lines.append(f"{line_no:4d} > {lines[line_no - 1]}")

    # 显示后 2 行
    for i in range(line_no + 1, min(len(lines) + 1, line_no + 3)):
        if i <= len(lines):
            context_lines.append(f"{i:4d} | {lines[i - 1]}")

    # 组合错误消息
    result = str(error)
    result += "\n\n源代码上下文:\n"
    result += "\n".join(context_lines)

    return result


class ReturnException(Exception):
    """
    Return 异常 (v4.3+)

    用于实现 return 语句的控制流

    Attributes:
        value: 返回值
    """

    def __init__(self, value=None):
        self.value = value
        super().__init__(f"return {value}")


# ============================================================================
# VR-006: 警告系统 (v6.3+)
# ============================================================================


@dataclass
class Warning:
    """
    DSL 警告（非阻塞，v6.3+）

    用于收集代码质量警告，不会中断执行。
    主要用于 VR-006（未使用变量）等代码质量检查。

    Attributes:
        warning_code: 警告代码（如 "VR-006"）
        message: 警告消息
        line: 警告发生的行号
        symbol_name: 相关符号名称（可选）
        file_path: 警告发生的文件路径（可选）
        suggestion: 修复建议（可选）

    Example:
        >>> w = Warning(
        ...     warning_code="VR-006",
        ...     message="变量 'unused_var' 声明但从未使用",
        ...     line=10,
        ...     symbol_name="unused_var",
        ...     suggestion="移除此变量或使用它"
        ... )
        >>> print(w.format())
    """

    warning_code: str
    message: str
    line: int
    symbol_name: Optional[str] = None
    file_path: Optional[str] = None
    suggestion: Optional[str] = None

    def format(self) -> str:
        """
        格式化警告消息（彩色输出）

        Returns:
            格式化的警告字符串
        """
        parts = []

        # 文件路径和行号
        location = ""
        if self.file_path:
            location = f"{self.file_path}:"
        location += f"{self.line}"

        # 警告标题（黄色）
        title = f"{Fore.YELLOW}[Warning {self.warning_code}]{Style.RESET_ALL}"
        parts.append(f"{title} {self.message}")
        parts.append(f"  at {location}")

        # 建议（青色）
        if self.suggestion:
            parts.append(f"  {Fore.CYAN}help:{Style.RESET_ALL} {self.suggestion}")

        return "\n".join(parts)

    def __str__(self) -> str:
        """字符串表示"""
        return self.format()
