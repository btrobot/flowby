"""
Flowby DSL 国际化（i18n）系统

提供多语言错误消息和用户界面文本支持
"""

from .messages import get_message, set_language, get_current_language

__all__ = ["get_message", "set_language", "get_current_language"]
