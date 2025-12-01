"""
Flowby DSL 国际化消息字典

支持中英文错误消息和用户界面文本
"""

import os
from typing import Dict, Any


# 当前语言（默认中文）
_current_language = os.environ.get("FLOWBY_LANG", "zh").lower()


def set_language(lang: str):
    """设置当前语言"""
    global _current_language
    if lang.lower() not in ("zh", "en"):
        raise ValueError(f"Unsupported language: {lang}. Supported: zh, en")
    _current_language = lang.lower()


def get_current_language() -> str:
    """获取当前语言"""
    return _current_language


def get_message(key: str, **kwargs) -> str:
    """
    获取国际化消息

    Args:
        key: 消息键（例如 'lexer.illegal_character'）
        **kwargs: 格式化参数

    Returns:
        格式化后的消息文本
    """
    message_template = MESSAGES.get(key, {}).get(_current_language)

    if message_template is None:
        # 回退到中文
        message_template = MESSAGES.get(key, {}).get("zh")

    if message_template is None:
        # 如果消息不存在，返回键本身
        return f"[Missing message: {key}]"

    # 格式化消息
    try:
        return message_template.format(**kwargs)
    except KeyError as e:
        return f"[Format error in {key}: missing {e}]"


# ============================================================
# 消息字典
# ============================================================

MESSAGES: Dict[str, Dict[str, str]] = {
    # ========================================
    # Lexer 错误消息
    # ========================================
    "lexer.illegal_character": {"zh": "非法字符: '{char}'", "en": "Illegal character: '{char}'"},
    "lexer.unterminated_string": {"zh": "未闭合的字符串", "en": "Unterminated string"},
    "lexer.unterminated_fstring": {"zh": "未闭合的 f-string", "en": "Unterminated f-string"},
    "lexer.unterminated_multiline_string": {
        "zh": "未闭合的多行字符串（从第 {start_line} 行开始）",
        "en": "Unterminated multi-line string (started at line {start_line})",
    },
    "lexer.unterminated_comment": {
        "zh": "未闭合的多行注释（从第 {start_line} 行开始）",
        "en": "Unterminated multi-line comment (started at line {start_line})",
    },
    "lexer.invalid_indent_not_multiple": {
        "zh": "缩进量不是 4 的倍数，当前为 {indent} 个空格",
        "en": "Indentation is not a multiple of 4, got {indent} spaces",
    },
    "lexer.invalid_indent_inconsistent": {
        "zh": "缩进不一致：期望 {expected} 个空格，实际 {actual} 个空格",
        "en": "Inconsistent indentation: expected {expected} spaces, got {actual}",
    },
    "lexer.invalid_dedent": {
        "zh": "反缩进到无效的缩进级别",
        "en": "Dedent to invalid indentation level",
    },
    "lexer.false_keyword": {
        "zh": "v3.0 使用 Python 风格布尔值，应该使用 'False' 而不是 'false'",
        "en": "v3.0 uses Python-style booleans, use 'False' instead of 'false'",
    },
    "lexer.true_keyword": {
        "zh": "v3.0 使用 Python 风格布尔值，应该使用 'True' 而不是 'true'",
        "en": "v3.0 uses Python-style booleans, use 'True' instead of 'true'",
    },
    "lexer.null_keyword": {
        "zh": "v3.0 使用 Python 风格空值，应该使用 'None' 而不是 'null'",
        "en": "v3.0 uses Python-style null, use 'None' instead of 'null'",
    },
    "lexer.hint_replace": {"zh": "将 '{old}' 改为 '{new}'", "en": "Replace '{old}' with '{new}'"},
    # ========================================
    # Parser 错误消息
    # ========================================
    "parser.unexpected_token": {"zh": "意外的 token 类型", "en": "Unexpected token type"},
    "parser.expected_token": {
        "zh": "期望 {expected}，实际得到 {actual}",
        "en": "Expected {expected}, got {actual}",
    },
    "parser.undefined_variable": {
        "zh": "未定义的变量 '{name}'（VR-001 违规）",
        "en": "Undefined variable '{name}' (VR-001 violation)",
    },
    "parser.undefined_variable_hint": {
        "zh": "在使用前先用 'let' 或 'const' 声明变量",
        "en": "Declare variable with 'let' or 'const' before use",
    },
    "parser.const_reassignment": {
        "zh": "不能修改常量 '{name}'（第 {def_line} 行定义，VR-002 违规）",
        "en": "Cannot reassign constant '{name}' (defined at line {def_line}, VR-002 violation)",
    },
    "parser.const_reassignment_hint": {
        "zh": "如果需要修改，请使用 'let' 声明",
        "en": "Use 'let' declaration if you need to modify the value",
    },
    "parser.duplicate_declaration": {
        "zh": "变量 '{name}' 已在第 {first_line} 行声明（VR-003 违规）",
        "en": "Variable '{name}' already declared at line {first_line} (VR-003 violation)",
    },
    "parser.duplicate_declaration_hint": {
        "zh": "同一作用域中不能重复声明变量",
        "en": "Cannot redeclare variable in the same scope",
    },
    "parser.system_variable_readonly": {
        "zh": "系统变量 '{name}' 是只读的（VR-004 违规）",
        "en": "System variable '{name}' is read-only (VR-004 violation)",
    },
    "parser.system_variable_readonly_hint": {
        "zh": "系统变量包括: page, env, response, context",
        "en": "System variables: page, env, response, context",
    },
    "parser.empty_step": {
        "zh": "步骤块不能为空，必须包含至少一条语句",
        "en": "Step block cannot be empty, must contain at least one statement",
    },
    "parser.return_outside_function": {
        "zh": "return 语句只能在函数内使用",
        "en": "return statement can only be used inside a function",
    },
    # ========================================
    # Execution 错误消息
    # ========================================
    "exec.runtime_error": {"zh": "运行时错误", "en": "Runtime error"},
    "exec.page_not_initialized": {
        "zh": "页面未初始化，请先使用 navigate 打开页面",
        "en": "Page not initialized, use navigate to open a page first",
    },
    "exec.element_not_found": {
        "zh": "找不到元素: {selector}",
        "en": "Element not found: {selector}",
    },
    "exec.timeout": {"zh": "操作超时（{timeout}秒）", "en": "Operation timeout ({timeout}s)"},
    "exec.assertion_failed": {"zh": "断言失败: {condition}", "en": "Assertion failed: {condition}"},
    "exec.type_error": {
        "zh": "类型错误: 期望 {expected}，得到 {actual}",
        "en": "Type error: expected {expected}, got {actual}",
    },
    "exec.division_by_zero": {"zh": "除数不能为零", "en": "Division by zero"},
    "exec.index_out_of_range": {"zh": "索引超出范围: {index}", "en": "Index out of range: {index}"},
    "exec.undefined_function": {"zh": "未定义的函数: {name}", "en": "Undefined function: {name}"},
    "exec.wrong_argument_count": {
        "zh": "函数 {name} 期望 {expected} 个参数，实际传入 {actual} 个",
        "en": "Function {name} expects {expected} arguments, got {actual}",
    },
    # ========================================
    # Warning 消息
    # ========================================
    "warning.unused_variable": {
        "zh": "变量 '{name}' 声明但从未使用",
        "en": "Variable '{name}' is declared but never used",
    },
    "warning.unused_variable_hint_param": {
        "zh": "如果这是有意的，可以用下划线前缀命名: _{name}",
        "en": "If intentional, prefix with underscore: _{name}",
    },
    "warning.unused_variable_hint_import": {
        "zh": "如果不需要，请移除此导入",
        "en": "Remove this import if not needed",
    },
    "warning.unused_variable_hint_regular": {
        "zh": "如果不需要，请移除此变量声明",
        "en": "Remove this variable declaration if not needed",
    },
    # ========================================
    # 通用消息
    # ========================================
    "common.at_line": {"zh": "在第 {line} 行", "en": "at line {line}"},
    "common.at_position": {
        "zh": "在第 {line} 行第 {column} 列",
        "en": "at line {line}, column {column}",
    },
    "common.help": {"zh": "提示", "en": "help"},
    "common.file": {"zh": "文件", "en": "file"},
    "common.expected": {"zh": "期望", "en": "expected"},
    "common.actual": {"zh": "实际", "en": "actual"},
}
