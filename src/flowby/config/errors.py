"""
配置错误定义
"""

from typing import Optional


class ConfigError(Exception):
    """配置加载错误"""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        line: Optional[int] = None,
        column: Optional[int] = None,
        suggestion: Optional[str] = None,
    ):
        """
        初始化配置错误

        Args:
            message: 错误消息
            file_path: 配置文件路径
            line: 错误行号
            column: 错误列号
            suggestion: 修复建议
        """
        self.message = message
        self.file_path = file_path
        self.line = line
        self.column = column
        self.suggestion = suggestion

        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """格式化错误消息"""
        parts = [f"ConfigError: {self.message}"]

        if self.file_path:
            parts.append(f"\n文件: {self.file_path}")

        if self.line is not None:
            location = f"第 {self.line} 行"
            if self.column is not None:
                location += f", 第 {self.column} 列"
            parts.append(f"位置: {location}")

        if self.suggestion:
            parts.append(f"\n建议:\n{self.suggestion}")

        return "\n".join(parts)
