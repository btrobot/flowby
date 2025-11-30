"""
DSL (Domain-Specific Language) 解释器包

该包实现了一个用于浏览器自动化和注册流程的领域特定语言解释器。

主要组件:
    - lexer: 词法分析器（Tokenization）
    - parser: 语法分析器（AST 生成）
    - interpreter: 解释器（AST 执行）
    - context: 执行上下文（状态隔离）
    - actions: 动作实现（具体操作）
    - runner: CLI 运行器

设计原则:
    1. 实例隔离 - 每个工作流执行创建独立的解释器实例
    2. 无全局状态 - 所有状态存储在 ExecutionContext
    3. 并发安全 - 支持多个解释器实例并发执行
"""

# 只导入已实现的模块
from .lexer import Lexer, Token, TokenType
from .parser import Parser
from .interpreter import Interpreter, interpret
from .context import ExecutionContext, ExecutionStatus
from .ast_nodes import ASTNode, Program
from .errors import DSLError, LexerError, ParserError, ExecutionError
from .runner import DSLRunner

__version__ = "1.0.0"

__all__ = [
    "Lexer",
    "Token",
    "TokenType",
    "Parser",
    "Interpreter",
    "interpret",
    "ExecutionContext",
    "ExecutionStatus",
    "ASTNode",
    "Program",
    "DSLError",
    "LexerError",
    "ParserError",
    "ExecutionError",
    "DSLRunner",
]
