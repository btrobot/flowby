"""
Input Statement 测试 (v5.1)

测试 input() 表达式的完整功能链：
1. Lexer: INPUT token 识别
2. Parser: input() 表达式解析
3. Evaluator: 交互/非交互模式执行
"""

import pytest
from unittest.mock import patch

from flowby.lexer import Lexer, TokenType
from flowby.parser import Parser
from flowby.ast_nodes import (
    InputExpression,
    Literal,
    LetStatement,
)
from flowby.expression_evaluator import ExpressionEvaluator
from flowby.symbol_table import SymbolTableStack, SymbolType
from flowby.system_variables import SystemVariables
from flowby.errors import ExecutionError, ParserError


# ============================================================
# 测试辅助类
# ============================================================


class MockContext:
    """模拟执行上下文"""

    def __init__(self, is_interactive=True):
        self.task_id = "test_task"
        self.is_interactive = is_interactive
        self.page = None


class MockInterpreter:
    """模拟解释器"""

    def __init__(self, is_interactive=True):
        self.context = MockContext(is_interactive)


# ============================================================
# Lexer 测试
# ============================================================


class TestInputLexer:
    """测试 Lexer 对 input 关键字的识别"""

    def test_input_token_recognition(self):
        """测试 INPUT token 识别"""
        lexer = Lexer()
        tokens = lexer.tokenize("input")

        assert len(tokens) == 2  # INPUT + EOF
        assert tokens[0].type == TokenType.INPUT
        assert tokens[0].value == "input"

    def test_input_in_expression(self):
        """测试 input 在表达式中的识别"""
        code = 'let name = input("提示: ")'
        lexer = Lexer()
        tokens = lexer.tokenize(code)

        # 验证关键 tokens
        token_types = [t.type for t in tokens]
        assert TokenType.LET in token_types
        assert TokenType.IDENTIFIER in token_types
        assert TokenType.EQUALS_SIGN in token_types
        assert TokenType.INPUT in token_types
        assert TokenType.LPAREN in token_types
        assert TokenType.STRING in token_types
        assert TokenType.RPAREN in token_types


# ============================================================
# Parser 测试
# ============================================================


class TestInputParser:
    """测试 Parser 对 input() 表达式的解析"""

    def test_parse_basic_input(self):
        """测试解析基本 input() 表达式"""
        code = 'let name = input("请输入姓名: ")'
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        assert len(ast.statements) == 1
        stmt = ast.statements[0]
        assert isinstance(stmt, LetStatement)
        assert stmt.name == "name"
        assert isinstance(stmt.value, InputExpression)

        input_expr = stmt.value
        assert isinstance(input_expr.prompt, Literal)
        assert input_expr.prompt.value == "请输入姓名: "
        assert input_expr.default_value is None
        assert input_expr.input_type == "text"

    def test_parse_input_with_default(self):
        """测试解析带默认值的 input()"""
        code = 'let email = input("邮箱: ", default="test@example.com")'
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        stmt = ast.statements[0]
        input_expr = stmt.value
        assert isinstance(input_expr, InputExpression)
        assert isinstance(input_expr.default_value, Literal)
        assert input_expr.default_value.value == "test@example.com"
        assert input_expr.input_type == "text"

    def test_parse_input_with_type(self):
        """测试解析带类型的 input()"""
        code = 'let age = input("年龄: ", type=integer)'
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        stmt = ast.statements[0]
        input_expr = stmt.value
        assert isinstance(input_expr, InputExpression)
        assert input_expr.input_type == "integer"
        assert input_expr.default_value is None

    def test_parse_input_password_type(self):
        """测试解析密码类型的 input()"""
        code = 'let pwd = input("密码: ", type=password)'
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        stmt = ast.statements[0]
        input_expr = stmt.value
        assert input_expr.input_type == "password"

    def test_parse_input_with_all_params(self):
        """测试解析包含所有参数的 input()"""
        code = 'let count = input("数量: ", default="10", type=integer)'
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        stmt = ast.statements[0]
        input_expr = stmt.value
        assert isinstance(input_expr, InputExpression)
        assert input_expr.default_value.value == "10"
        assert input_expr.input_type == "integer"

    def test_parse_input_with_colon_separator(self):
        """测试解析使用冒号分隔符的 input()"""
        code = 'let x = input("输入: ", default: "abc", type: text)'
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        stmt = ast.statements[0]
        input_expr = stmt.value
        assert input_expr.default_value.value == "abc"
        assert input_expr.input_type == "text"

    def test_parse_input_invalid_type(self):
        """测试解析无效类型应抛出错误"""
        code = 'let x = input("输入: ", type=invalid_type)'
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()

        with pytest.raises(ParserError) as exc_info:
            parser.parse(tokens)

        assert "无效的 input type" in str(exc_info.value)

    def test_parse_input_missing_prompt(self):
        """测试缺少提示参数应抛出错误"""
        code = "let x = input()"
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()

        with pytest.raises(ParserError):
            parser.parse(tokens)


# ============================================================
# Evaluator 测试
# ============================================================


class TestInputEvaluator:
    """测试 ExpressionEvaluator 对 input() 的求值"""

    def setup_method(self):
        """每个测试前的设置"""
        self.symbol_table = SymbolTableStack()
        # SystemVariables 需要 context 参数
        self.mock_context = MockContext()
        self.system_variables = SystemVariables(self.mock_context)
        self.evaluator = ExpressionEvaluator(self.symbol_table, self.system_variables)

    def test_eval_input_interactive_mode(self):
        """测试交互模式下的 input()"""
        # 准备
        self.evaluator.interpreter = MockInterpreter(is_interactive=True)
        input_expr = InputExpression(
            prompt=Literal(value="请输入: ", line=1), default_value=None, input_type="text", line=1
        )

        # Mock 用户输入
        with patch("builtins.input", return_value="测试输入"):
            result = self.evaluator.evaluate(input_expr)

        assert result == "测试输入"

    def test_eval_input_with_default_interactive(self):
        """测试交互模式下有默认值的 input()（用户输入为空）"""
        self.evaluator.interpreter = MockInterpreter(is_interactive=True)
        input_expr = InputExpression(
            prompt=Literal(value="姓名: ", line=1),
            default_value=Literal(value="张三", line=1),
            input_type="text",
            line=1,
        )

        # 用户输入空字符串
        with patch("builtins.input", return_value="  "):
            result = self.evaluator.evaluate(input_expr)

        assert result == "张三"

    def test_eval_input_integer_type(self):
        """测试整数类型转换"""
        self.evaluator.interpreter = MockInterpreter(is_interactive=True)
        input_expr = InputExpression(
            prompt=Literal(value="年龄: ", line=1), default_value=None, input_type="integer", line=1
        )

        with patch("builtins.input", return_value="25"):
            result = self.evaluator.evaluate(input_expr)

        assert result == 25
        assert isinstance(result, int)

    def test_eval_input_float_type(self):
        """测试浮点数类型转换"""
        self.evaluator.interpreter = MockInterpreter(is_interactive=True)
        input_expr = InputExpression(
            prompt=Literal(value="价格: ", line=1), default_value=None, input_type="float", line=1
        )

        with patch("builtins.input", return_value="99.99"):
            result = self.evaluator.evaluate(input_expr)

        assert result == 99.99
        assert isinstance(result, float)

    def test_eval_input_password_type(self):
        """测试密码类型（使用 getpass）"""
        self.evaluator.interpreter = MockInterpreter(is_interactive=True)
        input_expr = InputExpression(
            prompt=Literal(value="密码: ", line=1),
            default_value=None,
            input_type="password",
            line=1,
        )

        with patch("getpass.getpass", return_value="secret123"):
            result = self.evaluator.evaluate(input_expr)

        assert result == "secret123"

    def test_eval_input_invalid_integer_conversion(self):
        """测试无效整数转换应抛出错误"""
        self.evaluator.interpreter = MockInterpreter(is_interactive=True)
        input_expr = InputExpression(
            prompt=Literal(value="年龄: ", line=1), default_value=None, input_type="integer", line=1
        )

        with patch("builtins.input", return_value="not_a_number"):
            with pytest.raises(ExecutionError) as exc_info:
                self.evaluator.evaluate(input_expr)

            assert exc_info.value.error_type == ExecutionError.RUNTIME_ERROR
            assert "无法将输入" in exc_info.value.msg

    def test_eval_input_non_interactive_with_default(self):
        """测试非交互模式下有默认值（应返回默认值）"""
        self.evaluator.interpreter = MockInterpreter(is_interactive=False)
        input_expr = InputExpression(
            prompt=Literal(value="名称: ", line=1),
            default_value=Literal(value="默认名称", line=1),
            input_type="text",
            line=1,
        )

        # 非交互模式应直接返回默认值，不调用 input()
        result = self.evaluator.evaluate(input_expr)

        assert result == "默认名称"

    def test_eval_input_non_interactive_without_default(self):
        """测试非交互模式下无默认值（应抛出错误）"""
        self.evaluator.interpreter = MockInterpreter(is_interactive=False)
        input_expr = InputExpression(
            prompt=Literal(value="名称: ", line=1), default_value=None, input_type="text", line=1
        )

        with pytest.raises(ExecutionError) as exc_info:
            self.evaluator.evaluate(input_expr)

        assert exc_info.value.error_type == ExecutionError.RUNTIME_ERROR
        assert "需要交互模式" in exc_info.value.msg

    def test_eval_input_keyboard_interrupt(self):
        """测试用户中断输入（Ctrl+C）"""
        self.evaluator.interpreter = MockInterpreter(is_interactive=True)
        input_expr = InputExpression(
            prompt=Literal(value="输入: ", line=1), default_value=None, input_type="text", line=1
        )

        with patch("builtins.input", side_effect=KeyboardInterrupt()):
            with pytest.raises(ExecutionError) as exc_info:
                self.evaluator.evaluate(input_expr)

            assert "用户中断输入" in exc_info.value.msg

    def test_eval_input_prompt_from_variable(self):
        """测试提示文本可以是表达式（变量）"""
        self.evaluator.interpreter = MockInterpreter(is_interactive=True)

        # 设置变量
        from flowby.ast_nodes import Identifier

        self.symbol_table.define("prompt_text", "请输入姓名: ", SymbolType.VARIABLE, 1)

        input_expr = InputExpression(
            prompt=Identifier(name="prompt_text", line=1),
            default_value=None,
            input_type="text",
            line=1,
        )

        with patch("builtins.input", return_value="测试"):
            result = self.evaluator.evaluate(input_expr)

        assert result == "测试"


# ============================================================
# 集成测试
# ============================================================


class TestInputIntegration:
    """测试 input() 的完整集成流程"""

    def test_full_flow_parse_and_eval(self):
        """测试完整流程：解析 + 求值"""
        code = 'let username = input("用户名: ", default="admin")'

        # 解析
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        parser = Parser()
        ast = parser.parse(tokens)

        # 准备求值环境
        symbol_table = SymbolTableStack()
        mock_context = MockContext(is_interactive=True)
        system_variables = SystemVariables(mock_context)
        evaluator = ExpressionEvaluator(symbol_table, system_variables)
        evaluator.interpreter = MockInterpreter(is_interactive=True)

        # 求值
        stmt = ast.statements[0]
        with patch("builtins.input", return_value=""):  # 空输入，使用默认值
            value = evaluator.evaluate(stmt.value)

        assert value == "admin"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
