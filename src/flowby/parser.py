"""
语法分析器 v3.0 (Parser V3 - Python风格)

将 Token 流转换为 AST (抽象语法树)

v3.0 核心变更:
    1. ✅ 使用 INDENT/DEDENT tokens（替代 END token）
    2. ✅ 支持 Python 风格缩进语义
    3. ✅ 块结构：COLON + NEWLINE + INDENT ... DEDENT
    4. ✅ 删除所有 'end step', 'end if', 'end when', 'end for' 检查

采用递归下降解析（Recursive Descent Parsing）方法，每种语法结构对应一个解析方法

示例 (v3.0):
    输入: [STEP, STRING("登录"), COLON, NEWLINE, INDENT, ..., DEDENT]
    输出: StepBlock(name="登录", ...)
"""

from typing import List, Optional
from .lexer import Token, TokenType
from .ast_nodes import *
from .errors import ParserError
from .symbol_table import SymbolTableStack, SymbolType


# v6.3: 系统变量列表（运行时隐式可用，无需声明）
SYSTEM_VARIABLES = {
    "page",  # 页面对象
    "env",  # 环境变量
    "response",  # HTTP响应对象
}


class Parser:
    """
    语法分析器

    将 Token 流转换为 AST
    """

    def __init__(self):
        """初始化解析器"""
        self.tokens: List[Token] = []
        self.current = 0
        self.symbol_table_stack = SymbolTableStack()  # 符号表栈用于语义分析
        self._loop_depth = 0  # v3.0: 跟踪循环嵌套深度 (用于 break/continue 验证)
        self.warnings: List["Warning"] = []  # v6.3: VR-006 警告收集

    def parse(self, tokens: List[Token]) -> Program:
        """
        解析 Token 流生成 AST

        Args:
            tokens: Token 列表

        Returns:
            Program 根节点

        Raises:
            ParserError: 语法错误
        """
        self.tokens = tokens
        self.current = 0

        statements = []

        # 跳过开头的换行
        self._skip_newlines()

        while not self._is_at_end():
            # 跳过空行
            if self._check(TokenType.NEWLINE):
                self._advance()
                continue

            # 解析语句
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

            # 跳过换行
            self._skip_newlines()

        # 创建 AST
        program = Program(statements=statements, line=1)

        # v6.3: VR-006 - 检查未使用变量
        self._check_unused_variables()

        return program

    def _parse_statement(self) -> Optional[ASTNode]:
        """
        解析单个语句

        Returns:
            AST 节点，如果无法解析返回 None
        """
        token = self._peek()

        # v5.0 模块系统语句
        if token.type == TokenType.LIBRARY:
            return self._parse_library_declaration()
        if token.type == TokenType.EXPORT:
            return self._parse_export_statement()
        if token.type == TokenType.IMPORT or token.type == TokenType.FROM:
            return self._parse_import_statement()

        # v2.0 变量语句
        if token.type == TokenType.LET:
            return self._parse_let_statement()
        if token.type == TokenType.CONST:
            return self._parse_const_statement()

        # v4.3 函数定义和返回
        if token.type == TokenType.FUNCTION:
            return self._parse_function_def()
        if token.type == TokenType.RETURN:
            return self._parse_return_statement()

        # v2.0 循环语句
        if token.type == TokenType.FOR:
            return self._parse_for_each_loop()

        # v3.0 while 循环语句
        if token.type == TokenType.WHILE:
            return self._parse_while_loop()
        if token.type == TokenType.BREAK:
            return self._parse_break()
        if token.type == TokenType.CONTINUE:
            return self._parse_continue()

        # v2.0 日志语句 (支持字符串插值)
        if token.type == TokenType.LOG:
            return self._parse_log_statement()

        # v2.0 提取语句 (支持新语法)
        if token.type == TokenType.EXTRACT:
            return self._parse_extract_statement()

        # 导航语句
        if token.type == TokenType.NAVIGATE:
            return self._parse_navigate()
        if token.type == TokenType.GO:
            return self._parse_go()
        if token.type == TokenType.RELOAD:
            return self._parse_reload()

        # 等待语句
        if token.type == TokenType.WAIT:
            return self._parse_wait()

        # 选择语句
        if token.type == TokenType.SELECT:
            return self._parse_select()

        # 动作语句
        if token.type == TokenType.TYPE:
            return self._parse_type()
        if token.type in (TokenType.CLICK, TokenType.DOUBLE_CLICK, TokenType.RIGHT_CLICK):
            return self._parse_click()
        if token.type == TokenType.HOVER:
            return self._parse_hover()
        if token.type == TokenType.CLEAR:
            return self._parse_clear()
        if token.type == TokenType.PRESS:
            return self._parse_press()
        if token.type == TokenType.SCROLL:
            return self._parse_scroll()
        if token.type == TokenType.CHECK or token.type == TokenType.UNCHECK:
            return self._parse_check()
        if token.type == TokenType.UPLOAD:
            return self._parse_upload()

        # 断言语句
        if token.type == TokenType.ASSERT:
            return self._parse_assert()

        # 退出语句 (v4.1)
        if token.type == TokenType.EXIT:
            return self._parse_exit()

        # 截图语句
        if token.type == TokenType.SCREENSHOT:
            return self._parse_screenshot()

        # 步骤块
        if token.type == TokenType.STEP:
            return self._parse_step()

        # 条件块
        if token.type == TokenType.IF:
            return self._parse_if()
        if token.type == TokenType.WHEN:
            return self._parse_when()

        # v3.0: 检测 double click / right click (两个词)
        if token.type == TokenType.IDENTIFIER:
            # 向前看：如果是 'double' 或 'right' 后面跟 'click'
            if token.value.lower() in ("double", "right"):
                if (
                    self.current + 1 < len(self.tokens)
                    and self.tokens[self.current + 1].type == TokenType.CLICK
                ):
                    # 先推进到第一个词，然后让 _parse_click_multiword 处理
                    return self._parse_click_multiword()

            # v4.3: 向前看: 函数调用语句 (作为独立语句)
            if (
                self.current + 1 < len(self.tokens)
                and self.tokens[self.current + 1].type == TokenType.LPAREN
            ):
                # 这是函数调用语句，将其解析为表达式然后包装成语句
                expr = self._parse_expression()
                # 创建一个表达式语句节点（或直接返回，Interpreter 会处理）
                # 这里我们创建一个简单的包装器
                from .ast_nodes import ExpressionStatement

                return ExpressionStatement(expression=expr, line=token.line)

            # v5.0: 向前看: 方法调用语句 (作为独立语句)
            if (
                self.current + 1 < len(self.tokens)
                and self.tokens[self.current + 1].type == TokenType.DOT
            ):
                # 这是方法调用语句（如 logging.log_step(...)），解析为表达式并包装
                expr = self._parse_expression()
                from .ast_nodes import ExpressionStatement

                return ExpressionStatement(expression=expr, line=token.line)

            # 向前看一个 token: 赋值语句
            if (
                self.current + 1 < len(self.tokens)
                and self.tokens[self.current + 1].type == TokenType.EQUALS_SIGN
            ):
                return self._parse_assignment()

        # v5.1: 支持关键字作为函数调用的表达式语句
        # 某些关键字（如 input）在不同上下文中有不同含义：
        # - 作为选择器: select input where...
        # - 作为函数调用: input("prompt")
        if token.type == TokenType.INPUT:
            # 向前看: 如果后面跟着 '('，则是函数调用
            if (
                self.current + 1 < len(self.tokens)
                and self.tokens[self.current + 1].type == TokenType.LPAREN
            ):
                expr = self._parse_expression()
                from .ast_nodes import ExpressionStatement

                return ExpressionStatement(expression=expr, line=token.line)

        # 未知语句
        raise ParserError(
            token.line,
            token.column,
            token.type.name,
            token.value,
            f"未知的语句开始: {token.type.name}",
        )

    # ============================================================
    # 导航语句解析
    # ============================================================

    def _parse_navigate(self) -> NavigateToStatement:
        """解析 navigate to 语句 (v3.0: 支持完整表达式和 f-string)"""
        line = self._peek().line
        self._consume(TokenType.NAVIGATE, "期望 'navigate'")
        self._consume(TokenType.TO, "期望 'to'")

        # v3.0: 支持完整表达式（包括成员访问、f-string 等）
        url = self._parse_expression()

        return NavigateToStatement(url=url, line=line)

    def _parse_go(self) -> ASTNode:
        """解析 go back / go forward 语句"""
        line = self._peek().line
        self._consume(TokenType.GO, "期望 'go'")

        if self._check(TokenType.BACK):
            self._advance()
            return GoBackStatement(line=line)
        elif self._check(TokenType.FORWARD):
            self._advance()
            return GoForwardStatement(line=line)
        else:
            raise ParserError(
                self._peek().line,
                self._peek().column,
                self._peek().type.name,
                self._peek().value,
                "期望 'back' 或 'forward'",
                "back | forward",
            )

    def _parse_reload(self) -> ReloadStatement:
        """解析 reload 语句"""
        line = self._peek().line
        self._consume(TokenType.RELOAD, "期望 'reload'")
        return ReloadStatement(line=line)

    # ============================================================
    # 等待语句解析
    # ============================================================

    def _parse_wait(self) -> ASTNode:
        """解析 wait 语句"""
        line = self._peek().line
        self._consume(TokenType.WAIT, "期望 'wait'")

        # wait for ...
        if self._check(TokenType.FOR):
            self._advance()
            return self._parse_wait_for()

        # wait until ...
        if self._check(TokenType.UNTIL):
            self._advance()
            # v2.0: 支持通用表达式（向后兼容旧式条件）
            # 尝试解析为表达式
            condition = self._parse_expression()
            return WaitUntilStatement(condition=condition, line=line)

        # wait <duration> (v6.0.2: 支持数值表达式)
        # 向后兼容：数字字面量 + 可选单位
        if self._check_any(TokenType.INTEGER, TokenType.NUMBER):
            duration_token = self._advance()
            time_value = duration_token.value

            # Check for optional time unit identifier (seconds, second, sec, s, ms, milliseconds)
            if self._check(TokenType.IDENTIFIER):
                unit = self._peek().value.lower()
                if unit in ("s", "sec", "second", "seconds", "ms", "milliseconds"):
                    time_value = time_value + unit
                    self._advance()  # consume the unit

            duration = self._parse_time_value(time_value)
            return WaitDurationStatement(duration=duration, line=line)

        # v6.0.2: 支持数值表达式 (wait delay_time s / wait (retry * 2) s)
        # 尝试解析表达式
        try:
            duration_expr = self._parse_expression()

            # 时间单位是必需的（避免歧义）
            if not self._check(TokenType.IDENTIFIER):
                raise ParserError(
                    self._peek().line,
                    self._peek().column,
                    self._peek().type.name,
                    self._peek().value,
                    "使用表达式时需要指定时间单位（s, ms 等）",
                    "s | ms | seconds | milliseconds",
                )

            unit = self._peek().value.lower()
            if unit not in ("s", "sec", "second", "seconds", "ms", "milliseconds"):
                raise ParserError(
                    self._peek().line,
                    self._peek().column,
                    self._peek().type.name,
                    self._peek().value,
                    f"无效的时间单位: {unit}",
                    "s | ms | seconds | milliseconds",
                )

            self._advance()  # consume the unit
            return WaitDurationStatement(duration=duration_expr, unit=unit, line=line)

        except ParserError:
            # 如果表达式解析失败，抛出原始错误
            raise ParserError(
                self._peek().line,
                self._peek().column,
                self._peek().type.name,
                self._peek().value,
                "期望 'for', 'until' 或时间值（数字或表达式 + 单位）",
                "for | until | <number> [unit] | <expression> <unit>",
            )

    def _parse_wait_for(self) -> ASTNode:
        """解析 wait for ... 语句"""
        line = self._previous().line

        # wait for navigation [to URL] [wait for PageState] [timeout Duration]
        if self._check(TokenType.NAVIGATION):
            self._advance()

            # 可选：to Expression (URL)
            url = None
            if self._check(TokenType.TO):
                self._advance()  # consume TO
                url = self._parse_expression()

            # 可选：wait for <page_state>
            page_state = None
            if self._check(TokenType.WAIT):
                saved_pos = self.current
                self._advance()  # consume WAIT
                if self._check(TokenType.FOR):
                    self._advance()  # consume FOR
                    # 解析页面状态
                    if self._check_any(
                        TokenType.NETWORKIDLE, TokenType.DOMCONTENTLOADED, TokenType.LOAD
                    ):
                        page_state = self._advance().value.lower()
                    else:
                        # 不是页面状态，回退
                        self.current = saved_pos
                else:
                    # 不是 "wait for"，回退
                    self.current = saved_pos

            # 可选：timeout <duration>
            timeout = None
            if self._check(TokenType.IDENTIFIER) and self._peek().value.lower() == "timeout":
                self._advance()  # consume TIMEOUT
                # 解析超时时间
                if self._check_any(TokenType.INTEGER, TokenType.NUMBER):
                    duration_token = self._advance()
                    time_value = duration_token.value

                    # Check for optional time unit identifier
                    if self._check(TokenType.IDENTIFIER):
                        unit = self._peek().value.lower()
                        if unit in ("s", "sec", "second", "seconds", "ms", "milliseconds"):
                            time_value = time_value + unit
                            self._advance()  # consume the unit

                    timeout = self._parse_time_value(time_value)
                else:
                    raise ParserError(
                        self._peek().line,
                        self._peek().column,
                        self._peek().type.name,
                        self._peek().value,
                        "期望超时时间值",
                        "<duration>",
                    )

            return WaitForNavigationStatement(
                url=url, page_state=page_state, timeout=timeout, line=line
            )

        # wait for element ...
        if self._check(TokenType.ELEMENT):
            self._advance()

            # 解析 selector (必需)
            selector = self._parse_expression()

            # 可选：to be <state>
            state = None
            if self._check(TokenType.TO):
                self._advance()  # consume TO
                # 期待 BE（作为 IDENTIFIER）
                if self._check(TokenType.IDENTIFIER) and self._peek().value.lower() == "be":
                    self._advance()  # consume BE
                    # 解析状态
                    if self._check_any(
                        TokenType.VISIBLE, TokenType.HIDDEN, TokenType.ATTACHED, TokenType.DETACHED
                    ):
                        state = self._advance().value.lower()
                    else:
                        raise ParserError(
                            self._peek().line,
                            self._peek().column,
                            self._peek().type.name,
                            self._peek().value,
                            "期望元素状态 (visible/hidden/attached/detached)",
                            "visible | hidden | attached | detached",
                        )
                else:
                    raise ParserError(
                        self._peek().line,
                        self._peek().column,
                        self._peek().type.name,
                        self._peek().value,
                        "期望 'be'",
                        "be",
                    )

            # 可选：timeout <duration>
            timeout = None
            if self._check(TokenType.IDENTIFIER) and self._peek().value.lower() == "timeout":
                self._advance()  # consume TIMEOUT
                # 解析超时时间
                if self._check_any(TokenType.INTEGER, TokenType.NUMBER):
                    duration_token = self._advance()
                    time_value = duration_token.value

                    # Check for optional time unit identifier
                    if self._check(TokenType.IDENTIFIER):
                        unit = self._peek().value.lower()
                        if unit in ("s", "sec", "second", "seconds", "ms", "milliseconds"):
                            time_value = time_value + unit
                            self._advance()  # consume the unit

                    timeout = self._parse_time_value(time_value)
                else:
                    raise ParserError(
                        self._peek().line,
                        self._peek().column,
                        self._peek().type.name,
                        self._peek().value,
                        "期望超时时间值",
                        "<duration>",
                    )

            return WaitForElementStatement(
                selector=selector, state=state, timeout=timeout, line=line
            )

        # wait for <page_state>
        if self._check_any(TokenType.NETWORKIDLE, TokenType.DOMCONTENTLOADED, TokenType.LOAD):
            state_token = self._advance()
            return WaitForStateStatement(state=state_token.value.lower(), line=line)

        # wait for <duration> (e.g., wait for 2s, wait for 500ms)
        if self._check(TokenType.NUMBER):
            duration_token = self._advance()
            time_value = duration_token.value

            # Check for optional time unit identifier (seconds, second, sec, s, ms)
            if self._check(TokenType.IDENTIFIER):
                unit = self._peek().value.lower()
                if unit in ("s", "sec", "second", "seconds", "ms", "milliseconds"):
                    time_value = time_value + unit
                    self._advance()  # consume the unit

            duration = self._parse_time_value(time_value)
            return WaitDurationStatement(duration=duration, line=line)

        raise ParserError(
            self._peek().line,
            self._peek().column,
            self._peek().type.name,
            self._peek().value,
            "期望 'navigation', 'element', 页面状态或时间值",
            "navigation | element | networkidle | domcontentloaded | load | <duration>",
        )

    # ============================================================
    # 选择语句解析
    # ============================================================

    def _parse_select(self):
        """解析 select 语句（元素选择或下拉框选项选择）"""
        line = self._peek().line
        self._consume(TokenType.SELECT, "期望 'select'")

        # 检查是否是 select option (下拉框选项选择)
        if self._check(TokenType.OPTION):
            return self._parse_select_option()

        # 否则是元素选择
        # 元素类型（支持关键字或字符串）
        # v3.0: 支持 select input 或 select "input" (向后兼容)
        if self._check(TokenType.STRING):
            # 字符串形式：select "input"
            element_type_token = self._advance()
            element_type = element_type_token.value.lower()
        else:
            # 关键字形式：select input
            element_type_token = self._consume_any(
                [
                    TokenType.INPUT,
                    TokenType.BUTTON,
                    TokenType.ELEMENT,
                    TokenType.LINK,
                    TokenType.TEXTAREA,
                    TokenType.DIV,
                    TokenType.SPAN,
                ],
                "期望元素类型",
            )
            element_type = element_type_token.value.lower()

        # where 子句
        conditions = []
        if self._check(TokenType.WHERE):
            self._advance()
            conditions = self._parse_where_clause()

        return SelectStatement(element_type=element_type, conditions=conditions, line=line)

    def _parse_select_option(self) -> SelectOptionAction:
        """解析 select option 语句（下拉框选项选择） - v2.0 支持表达式"""
        line = self._peek().line
        self._consume(TokenType.OPTION, "期望 'option'")

        # v2.0: 支持表达式
        option_value = self._parse_expression()
        self._consume(TokenType.FROM, "期望 'from'")
        selector = self._parse_expression()

        return SelectOptionAction(option_value=option_value, selector=selector, line=line)

    def _parse_where_clause(self) -> List[tuple[str, str, str]]:
        """解析 where 子句 - v3.0 支持运算符"""
        conditions = []

        # 第一个条件 - 允许关键字作为属性名
        attr = self._parse_attribute_name()

        # v3.0: 支持多种运算符
        # = | contains | equals | matches
        if self._check(TokenType.EQUALS_SIGN):
            operator = "="
            self._advance()
        elif self._check(TokenType.CONTAINS):
            operator = "contains"
            self._advance()
        elif self._check(TokenType.EQUALS):
            operator = "equals"
            self._advance()
        elif self._check(TokenType.MATCHES):
            operator = "matches"
            self._advance()
        else:
            raise ParserError(
                self._peek().line,
                self._peek().column,
                self._peek().type.name,
                self._peek().value,
                "期望运算符 (=, contains, equals, matches)",
                "= | contains | equals | matches",
            )

        # 解析值 - v3.1: 支持表达式
        # 使用 _parse_comparison 来解析非逻辑表达式（避免与 and 冲突）
        value_expr = self._parse_comparison()

        # 将表达式转换为字符串形式（用于后续求值）
        # 如果是简单的字面量，直接使用其值
        if isinstance(value_expr, Literal):
            value = value_expr.value
        elif isinstance(value_expr, Identifier):
            # 标识符引用，标记为需要求值
            value = "{" + value_expr.name + "}"
        else:
            # 复杂表达式，需要完整序列化（用于后续求值）
            # 暂时使用占位符，实际求值在运行时
            value = value_expr  # 保留表达式对象

        conditions.append((attr, operator, value))

        # 额外的条件（and 连接）
        while self._check(TokenType.AND):
            self._advance()
            attr = self._parse_attribute_name()

            # 支持多种运算符
            if self._check(TokenType.EQUALS_SIGN):
                operator = "="
                self._advance()
            elif self._check(TokenType.CONTAINS):
                operator = "contains"
                self._advance()
            elif self._check(TokenType.EQUALS):
                operator = "equals"
                self._advance()
            elif self._check(TokenType.MATCHES):
                operator = "matches"
                self._advance()
            else:
                raise ParserError(
                    self._peek().line,
                    self._peek().column,
                    self._peek().type.name,
                    self._peek().value,
                    "期望运算符 (=, contains, equals, matches)",
                    "= | contains | equals | matches",
                )

            # 解析值 - v3.1: 支持表达式
            value_expr = self._parse_comparison()

            # 将表达式转换为字符串形式（用于后续求值）
            if isinstance(value_expr, Literal):
                value = value_expr.value
            elif isinstance(value_expr, Identifier):
                value = "{" + value_expr.name + "}"
            else:
                # 复杂表达式，保留表达式对象
                value = value_expr

            conditions.append((attr, operator, value))

        return conditions

    def _parse_attribute_name(self) -> str:
        """解析属性名（允许关键字作为属性名）"""
        token = self._peek()

        # 允许 IDENTIFIER 或某些关键字作为属性名
        # 常见的属性: type, text, value, href, etc.
        if token.type == TokenType.IDENTIFIER:
            return self._advance().value
        elif token.type in (TokenType.TYPE, TokenType.TEXT, TokenType.VALUE):
            return self._advance().value.lower()
        else:
            raise ParserError(
                token.line, token.column, token.type.name, token.value, "期望属性名", "IDENTIFIER"
            )

    # ============================================================
    # 动作语句解析
    # ============================================================

    def _parse_type(self) -> TypeAction:
        """
        解析 type 语句 - v3.0 支持 into 选择器

        语法: type expression [into selector] [slowly|fast]

        示例:
            type "literal string"              # 字符串字面量
            type email                         # 变量引用
            type user.email                    # 成员访问
            type "Hello {user.name}"           # 字符串插值
            type "text" into "#selector"       # v3.0: 指定选择器
            type slowly password               # 带模式的变量引用
        """
        line = self._peek().line
        self._consume(TokenType.TYPE, "期望 'type'")

        # v3.0: 先解析文本表达式
        text_expr = self._parse_expression()

        # 可选：into Selector
        selector = None
        if self._check(TokenType.INTO):
            self._advance()  # consume INTO
            selector = self._parse_expression()

        # 可选：检查模式（slowly / fast）
        mode = None
        if self._check_any(TokenType.SLOWLY, TokenType.FAST):
            mode = self._advance().value.lower()

        return TypeAction(text=text_expr, selector=selector, mode=mode, line=line)

    def _parse_click_multiword(self) -> ClickAction:
        """解析多词 click 语句 (double click / right click, v3.2: 完全表达式支持, v3.3: f-string 支持)"""
        line = self._peek().line
        modifier = self._advance().value.lower()  # 'double' or 'right'
        self._consume(TokenType.CLICK, "期望 'click'")

        # 确定点击类型
        if modifier == "double":
            click_type = "double_click"
        elif modifier == "right":
            click_type = "right_click"
        else:
            click_type = "click"

        # v3.2: 选择器支持完整表达式（v3.3: 添加 f-string 支持）
        selector = None
        if self._check(TokenType.STRING) or self._check(TokenType.FSTRING):
            selector = self._parse_expression()
        elif self._check(TokenType.IDENTIFIER):
            # 检查是否是 "and" 关键字（避免误解析 wait duration）
            if self._peek().value.lower() != "and":
                selector = self._parse_expression()

        # 检查 "and wait <duration>"
        wait_duration = None
        if self._check(TokenType.AND):
            self._advance()
            self._consume(TokenType.WAIT, "期望 'wait'")
            duration_token = self._consume_numeric("期望时间值")
            wait_duration = self._parse_time_value(duration_token.value)

        return ClickAction(
            click_type=click_type, selector=selector, wait_duration=wait_duration, line=line
        )

    def _parse_click(self) -> ClickAction:
        """解析 click 语句 (v3.2: 完全表达式支持, v3.3: f-string 支持)"""
        line = self._peek().line
        click_token = self._advance()

        # 确定点击类型
        if click_token.type == TokenType.CLICK:
            click_type = "click"
        elif click_token.type == TokenType.DOUBLE_CLICK:
            click_type = "double_click"
        elif click_token.type == TokenType.RIGHT_CLICK:
            click_type = "right_click"
        else:
            click_type = "click"

        # v3.2: 选择器支持完整表达式（v3.3: 添加 f-string 支持）
        selector = None
        if self._check(TokenType.STRING) or self._check(TokenType.FSTRING):
            selector = self._parse_expression()
        elif self._check(TokenType.IDENTIFIER):
            # 检查是否是 "and" 关键字（避免误解析 wait duration）
            if self._peek().value.lower() != "and":
                selector = self._parse_expression()

        # 检查 "and wait <duration>"
        wait_duration = None
        if self._check(TokenType.AND):
            self._advance()
            self._consume(TokenType.WAIT, "期望 'wait'")
            duration_token = self._consume_numeric("期望时间值")
            wait_duration = self._parse_time_value(duration_token.value)

        return ClickAction(
            click_type=click_type, selector=selector, wait_duration=wait_duration, line=line
        )

    def _parse_hover(self) -> HoverAction:
        """解析 hover 语句 (v3.0: over 可选, v3.2: 完全表达式支持, v3.3: f-string 支持)"""
        line = self._peek().line
        self._consume(TokenType.HOVER, "期望 'hover'")

        selector = None

        # v3.0: over 关键字可选
        if self._check(TokenType.OVER):
            self._advance()  # 消费 over

        # v3.2: 选择器支持完整表达式（v3.3: 添加 f-string 支持）
        if (
            self._check(TokenType.STRING)
            or self._check(TokenType.FSTRING)
            or self._check(TokenType.IDENTIFIER)
        ):
            selector = self._parse_expression()

        return HoverAction(selector=selector, line=line)

    def _parse_clear(self) -> ClearAction:
        """解析 clear 语句 (v3.0: 支持可选选择器, v3.2: 完全表达式支持, v3.3: f-string 支持)"""
        line = self._peek().line
        self._consume(TokenType.CLEAR, "期望 'clear'")

        # v3.2: 选择器支持完整表达式（v3.3: 添加 f-string 支持）
        selector = None
        if (
            self._check(TokenType.STRING)
            or self._check(TokenType.FSTRING)
            or self._check(TokenType.IDENTIFIER)
        ):
            selector = self._parse_expression()

        return ClearAction(selector=selector, line=line)

    def _parse_press(self) -> PressAction:
        """解析 press 语句"""
        line = self._peek().line
        self._consume(TokenType.PRESS, "期望 'press'")
        key_token = self._consume(TokenType.IDENTIFIER, "期望按键名称")
        return PressAction(key_name=key_token.value, line=line)

    def _parse_scroll(self) -> ScrollAction:
        """解析 scroll 语句 (v3.0: 支持多种目标格式, v3.3: 完全表达式支持)"""
        line = self._peek().line
        self._consume(TokenType.SCROLL, "期望 'scroll'")
        self._consume(TokenType.TO, "期望 'to'")

        # scroll to top / bottom
        if self._check_any(TokenType.TOP, TokenType.BOTTOM):
            target_token = self._advance()
            return ScrollAction(target=target_token.value.lower(), line=line)

        # scroll to element <expr> (完整语法)
        if self._check(TokenType.ELEMENT):
            self._advance()
            # v3.3: element 后的选择器支持完整表达式
            if (
                self._check(TokenType.STRING)
                or self._check(TokenType.FSTRING)
                or self._check(TokenType.IDENTIFIER)
            ):
                selector_expr = self._parse_expression()
            else:
                raise ParserError(
                    self._peek().line,
                    self._peek().column,
                    self._peek().type.name,
                    self._peek().value,
                    "期望选择器字符串或表达式",
                    "STRING | FSTRING | IDENTIFIER",
                )
            return ScrollAction(target="element", selector=selector_expr, line=line)

        # v3.0: scroll to 500 (数字位置) - v4.0: 支持 INTEGER
        if self._check(TokenType.NUMBER) or self._check(TokenType.INTEGER):
            position = self._advance().value
            return ScrollAction(target="position", selector=position, line=line)

        # v3.3: scroll to <expr> (统一表达式支持)
        if (
            self._check(TokenType.STRING)
            or self._check(TokenType.FSTRING)
            or self._check(TokenType.IDENTIFIER)
        ):
            selector = self._parse_expression()
            return ScrollAction(target="element", selector=selector, line=line)

        raise ParserError(
            self._peek().line,
            self._peek().column,
            self._peek().type.name,
            self._peek().value,
            "期望 'top', 'bottom', 'element', 选择器字符串、数字或变量",
            "top | bottom | element | STRING | NUMBER | INTEGER | IDENTIFIER",
        )

    def _parse_check(self) -> CheckAction:
        """解析 check/uncheck 语句 (v3.2: 完全表达式支持, v3.3: f-string 支持)"""
        line = self._peek().line
        action_token = self._advance()
        action = action_token.value.lower()

        # v3.2: 选择器支持完整表达式（v3.3: 添加 f-string 支持）
        if (
            self._check(TokenType.STRING)
            or self._check(TokenType.FSTRING)
            or self._check(TokenType.IDENTIFIER)
        ):
            selector = self._parse_expression()
        else:
            raise ParserError(
                self._peek().line,
                self._peek().column,
                self._peek().type.name,
                self._peek().value,
                "期望选择器字符串或表达式",
                "STRING | FSTRING | IDENTIFIER",
            )

        return CheckAction(action=action, selector=selector, line=line)

    def _parse_upload(self) -> UploadAction:
        """解析 upload 语句 (v3.0: 支持表达式, v3.2: 完全表达式支持, v3.3: f-string 支持)"""
        line = self._peek().line
        self._consume(TokenType.UPLOAD, "期望 'upload'")
        self._consume(TokenType.FILE, "期望 'file'")

        # v3.2: 文件路径支持完整表达式（v3.3: 添加 f-string 支持）
        if (
            self._check(TokenType.STRING)
            or self._check(TokenType.FSTRING)
            or self._check(TokenType.IDENTIFIER)
        ):
            file_path = self._parse_expression()
        else:
            raise ParserError(
                self._peek().line,
                self._peek().column,
                self._peek().type.name,
                self._peek().value,
                "期望文件路径字符串或表达式",
                "STRING | FSTRING | IDENTIFIER",
            )

        self._consume(TokenType.TO, "期望 'to'")

        # v3.2: 选择器支持完整表达式（v3.3: 添加 f-string 支持）
        if (
            self._check(TokenType.STRING)
            or self._check(TokenType.FSTRING)
            or self._check(TokenType.IDENTIFIER)
        ):
            selector = self._parse_expression()
        else:
            raise ParserError(
                self._peek().line,
                self._peek().column,
                self._peek().type.name,
                self._peek().value,
                "期望选择器字符串或表达式",
                "STRING | FSTRING | IDENTIFIER",
            )

        return UploadAction(file_path=file_path, selector=selector, line=line)

    # ============================================================
    # 验证语句解析
    # ============================================================

    def _parse_assert(self) -> AssertStatement:
        """
        解析 assert 语句 - v2.0 简化语法，v4.3 增强

        语法: assert expression [, message_expression]

        示例:
            assert x > 5
            assert user.age >= 18, "User must be adult"
            assert arr.length() > 0, "Array should not be empty"
            assert status == 200 OR status == 201
            assert condition, error_msg  # v4.3: 支持变量和表达式
        """
        line = self._peek().line
        self._consume(TokenType.ASSERT, "期望 'assert'")

        # 解析条件表达式
        condition = self._parse_expression()

        # 可选的错误消息 (逗号 + 表达式) - v4.3: 支持任意表达式
        message = None
        if self._check(TokenType.COMMA):
            self._advance()  # 消费逗号
            message = self._parse_expression()  # v4.3: 解析表达式而不只是字符串字面量

        return AssertStatement(condition=condition, message=message, line=line)

    def _parse_exit(self) -> "ExitStatement":
        """
        解析 exit 语句 - v4.0

        语法: exit [code] [, "message"]

        示例:
            exit                    # 退出，code=0
            exit 1                  # 退出，code=1
            exit "Failed"           # 退出，code=1，消息
            exit 0, "Success"       # 退出，code=0，消息
        """
        line = self._peek().line
        self._consume(TokenType.EXIT, "期望 'exit'")

        code = None
        message = None

        # exit 后面可以跟：
        # 1. 什么都没有
        # 2. 数字 (code)
        # 3. 字符串 (message)
        # 4. 数字, 字符串 (code, message)

        if not self._check(TokenType.NEWLINE) and not self._is_at_end():
            # 第一个参数
            if self._check(TokenType.INTEGER):
                code = int(self._advance().value)

                # 检查是否有逗号和消息
                if self._check(TokenType.COMMA):
                    self._consume(TokenType.COMMA, "期望逗号")
                    message_token = self._consume(TokenType.STRING, "期望字符串消息")
                    message = message_token.value
            elif self._check(TokenType.STRING):
                # 只有消息，code 默认为 1
                message = self._advance().value
                code = 1

        return ExitStatement(code=code, message=message, line=line)

    # ============================================================
    # 截图语句解析
    # ============================================================

    def _parse_screenshot(self) -> ScreenshotStatement:
        """
        解析 screenshot 语句 (v3.0: 支持灵活参数顺序)

        语法:
            screenshot                              # 全屏截图，自动命名
            screenshot as "name"                    # 全屏截图，指定名称
            screenshot fullpage as "name"           # 全页面截图（滚动）
            screenshot of "#selector"               # 元素截图，自动命名
            screenshot as "name" of "#selector"     # 元素截图，指定名称
            screenshot of ".modal" as "modal-view"  # v3.0: of 在 as 之前
            screenshot of "body" fullpage as "x"    # v3.0: 灵活顺序
        """
        line = self._peek().line
        self._consume(TokenType.SCREENSHOT, "期望 'screenshot'")

        # v3.0: 支持灵活的参数顺序
        fullpage = False
        name = None
        selector = None

        # 标记已解析的参数
        seen_fullpage = False
        seen_as = False
        seen_of = False

        # 循环解析所有可选参数
        while True:
            if self._check(TokenType.FULLPAGE) and not seen_fullpage:
                self._advance()
                fullpage = True
                seen_fullpage = True
            elif self._check(TokenType.AS) and not seen_as:
                self._advance()
                name = self._parse_expression()
                seen_as = True
            elif self._check(TokenType.OF) and not seen_of:
                self._advance()
                selector = self._parse_expression()
                seen_of = True
            else:
                # 没有更多 screenshot 参数
                break

        return ScreenshotStatement(name=name, fullpage=fullpage, selector=selector, line=line)

    # ============================================================
    # 服务调用语句解析

    def _parse_number_value(self, value: str) -> float:
        """解析数字值（去除时间单位）"""
        # 移除可能的时间单位
        for suffix in ["ms", "seconds", "second", "sec", "s"]:
            if value.lower().endswith(suffix):
                value = value[: -len(suffix)]
                break

        if "." in value:
            return float(value)
        return int(value)

    # ============================================================
    # 步骤块解析
    # ============================================================

    def _parse_step(self) -> StepBlock:
        """解析 step 块 (v3.0: 支持 diagnosis 选项和空块检测)"""
        line = self._peek().line
        self._consume(TokenType.STEP, "期望 'step'")
        name_token = self._consume(TokenType.STRING, "期望步骤名称字符串")

        # 可选的 diagnosis 选项
        diagnosis = None
        if self._check(TokenType.WITH):
            self._advance()  # 消费 WITH
            self._consume(TokenType.DIAGNOSIS, "期望 'diagnosis'")
            # 解析诊断级别（接受任何 identifier 或关键字）
            level_token = self._peek()
            if level_token.type == TokenType.IDENTIFIER or level_token.type.name not in (
                "EOF",
                "NEWLINE",
                "COLON",
                "INDENT",
                "DEDENT",
            ):
                self._advance()
                diagnosis = level_token.value
            else:
                raise ParserError(
                    level_token.line,
                    level_token.column,
                    level_token.type.name,
                    level_token.value,
                    "期望诊断级别（identifier 或关键字）",
                    "IDENTIFIER",
                )

        # 可选的条件
        condition = None
        if self._check(TokenType.IF):
            self._advance()
            condition = self._parse_expression()  # 使用表达式而不是旧式条件

        # v3.0: 消费 COLON, NEWLINE
        self._consume(TokenType.COLON, "期望 ':'")
        self._consume(TokenType.NEWLINE, "期望换行")

        # v3.0: 检测空块（在尝试消费 INDENT 之前）
        if not self._check(TokenType.INDENT):
            # 空块：冒号后没有缩进的内容
            raise ParserError(
                line,
                0,
                self._peek().type.name,
                self._peek().value,
                "步骤块不能为空，必须包含至少一条语句",
                "INDENT",
            )

        # 消费 INDENT
        self._consume(TokenType.INDENT, "期望缩进")

        # 创建 step 块作用域（修复 VR-VAR-003 bug）
        # 每个 step 块有独立作用域，允许不同 step 中声明同名变量
        self.symbol_table_stack.enter_scope(f"step_{name_token.value}")

        try:
            # 解析步骤内的语句
            statements = []
            while not self._check(TokenType.DEDENT) and not self._is_at_end():
                if self._check(TokenType.NEWLINE):
                    self._advance()
                    continue

                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)

                self._skip_newlines()

            # v3.0: 消费 DEDENT
            self._consume(TokenType.DEDENT, "期望反缩进")

            # 二次检查：如果解析过程中没有产生任何语句（所有都是空行）
            if not statements:
                raise ParserError(
                    line, 0, "DEDENT", "", "步骤块不能为空，必须包含至少一条语句", "statement"
                )

            return StepBlock(
                name=name_token.value,
                condition=condition,
                diagnosis=diagnosis,
                statements=statements,
                line=line,
            )

        finally:
            # 退出 step 块作用域
            self.symbol_table_stack.exit_scope()

    # ============================================================
    # 条件块解析
    # ============================================================

    def _parse_if(self) -> IfBlock:
        """解析 if 块（支持 else-if）(v3.0: 使用 INDENT/DEDENT)"""
        line = self._peek().line
        self._consume(TokenType.IF, "期望 'if'")

        # v2.0: 解析表达式作为条件
        condition = self._parse_expression()

        # v3.0: 消费 COLON, NEWLINE, INDENT
        self._consume(TokenType.COLON, "期望 ':'")
        self._consume(TokenType.NEWLINE, "期望换行")
        self._consume(TokenType.INDENT, "期望缩进")

        # if 块中的语句
        if_statements = []
        while not self._check_any(TokenType.DEDENT, TokenType.ELSE) and not self._is_at_end():
            if self._check(TokenType.NEWLINE):
                self._advance()
                continue

            stmt = self._parse_statement()
            if stmt:
                if_statements.append(stmt)

            self._skip_newlines()

        # v3.0: 消费 if 块的 DEDENT
        self._consume(TokenType.DEDENT, "期望反缩进")

        # else-if 子句（可以有多个）
        elif_clauses = []
        while self._check(TokenType.ELSE):
            # 向前看：检查下一个 token 是否是 IF
            # 如果是 IF，则是 else-if；否则是 else
            saved_pos = self.current
            self._advance()  # 消费 ELSE

            if self._check(TokenType.IF):
                # else if 子句
                self._advance()  # 消费 IF

                # 解析 else-if 条件
                elif_condition = self._parse_expression()
                self._consume(TokenType.COLON, "期望 ':'")
                self._consume(TokenType.NEWLINE, "期望换行")
                self._consume(TokenType.INDENT, "期望缩进")

                # 解析 else-if 块中的语句
                elif_statements = []
                while (
                    not self._check_any(TokenType.DEDENT, TokenType.ELSE) and not self._is_at_end()
                ):
                    if self._check(TokenType.NEWLINE):
                        self._advance()
                        continue

                    stmt = self._parse_statement()
                    if stmt:
                        elif_statements.append(stmt)

                    self._skip_newlines()

                # v3.0: 消费 else-if 块的 DEDENT
                self._consume(TokenType.DEDENT, "期望反缩进")

                elif_clauses.append((elif_condition, elif_statements))
            else:
                # else 子句（不是 else-if）
                # 回退到 ELSE 后的位置，让下面的代码处理
                self.current = saved_pos
                break

        # else 块（可选）
        else_statements = []
        if self._check(TokenType.ELSE):
            self._advance()
            self._consume(TokenType.COLON, "期望 ':'")
            self._consume(TokenType.NEWLINE, "期望换行")
            self._consume(TokenType.INDENT, "期望缩进")

            while not self._check(TokenType.DEDENT) and not self._is_at_end():
                if self._check(TokenType.NEWLINE):
                    self._advance()
                    continue

                stmt = self._parse_statement()
                if stmt:
                    else_statements.append(stmt)

                self._skip_newlines()

            # v3.0: 消费 else 块的 DEDENT
            self._consume(TokenType.DEDENT, "期望反缩进")

        return IfBlock(
            condition=condition,
            then_statements=if_statements,
            elif_clauses=elif_clauses,
            else_statements=else_statements,
            line=line,
        )

    def _parse_when(self) -> WhenBlock:
        """解析 when 块 (v3.0: switch/match 语法)"""
        line = self._peek().line
        self._consume(TokenType.WHEN, "期望 'when'")

        # 解析要匹配的表达式（如 status）
        value_expression = self._parse_expression()

        self._consume(TokenType.COLON, "期望 ':'")
        self._consume(TokenType.NEWLINE, "期望换行")
        self._consume(TokenType.INDENT, "期望缩进")

        # 解析 case 子句
        when_clauses = []
        while not self._check(TokenType.DEDENT) and not self._is_at_end():
            if self._check(TokenType.NEWLINE):
                self._advance()
                continue

            # 检查是否是 otherwise
            if self._check(TokenType.OTHERWISE):
                break

            # 解析 case 值（v3.1: 支持 OR 模式 - 200 | 201 | 204）
            clause_line = self._peek().line
            case_values = []

            # 解析第一个值
            case_values.append(self._parse_expression())

            # 检查是否有 OR 模式（| 分隔符）
            while self._check(TokenType.PIPE):
                self._consume(TokenType.PIPE, "期望 '|'")
                case_values.append(self._parse_expression())

            self._consume(TokenType.COLON, "期望 ':'")
            self._consume(TokenType.NEWLINE, "期望换行")
            self._consume(TokenType.INDENT, "期望缩进")

            # case 子句中的语句
            statements = []
            while not self._check(TokenType.DEDENT) and not self._is_at_end():
                if self._check(TokenType.NEWLINE):
                    self._advance()
                    continue

                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)

                self._skip_newlines()

            # 消费 case 块的 DEDENT
            self._consume(TokenType.DEDENT, "期望反缩进")

            when_clauses.append(
                WhenClause(case_values=case_values, statements=statements, line=clause_line)
            )

        # otherwise 块（可选）
        otherwise_statements = []
        if self._check(TokenType.OTHERWISE):
            self._advance()
            self._consume(TokenType.COLON, "期望 ':'")
            self._consume(TokenType.NEWLINE, "期望换行")
            self._consume(TokenType.INDENT, "期望缩进")

            while not self._check(TokenType.DEDENT) and not self._is_at_end():
                if self._check(TokenType.NEWLINE):
                    self._advance()
                    continue

                stmt = self._parse_statement()
                if stmt:
                    otherwise_statements.append(stmt)

                self._skip_newlines()

            # 消费 otherwise 块的 DEDENT
            self._consume(TokenType.DEDENT, "期望反缩进")

        # 消费整个 when 块的 DEDENT
        self._consume(TokenType.DEDENT, "期望反缩进")

        return WhenBlock(
            value_expression=value_expression,
            when_clauses=when_clauses,
            otherwise_statements=otherwise_statements,
            line=line,
        )

    # ============================================================
    # v5.0 Module System 解析
    # ============================================================

    def _parse_library_declaration(self) -> LibraryDeclaration:
        """
        解析 library 声明语句 (v5.0)

        语法:
            library NAME

        示例:
            library logging
            library validation

        约束:
            - 必须在文件首行（第一条非注释语句）
            - library 名称必须与文件名匹配（运行时验证）
            - 一个文件只能有一个 library 声明
        """
        line = self._peek().line
        self._consume(TokenType.LIBRARY, "期望 'library'")

        # 解析库名称
        name_token = self._consume(TokenType.IDENTIFIER, "期望库名称（标识符）")
        library_name = name_token.value

        return LibraryDeclaration(name=library_name, line=line)

    def _parse_export_statement(self) -> ExportStatement:
        """
        解析 export 语句 (v5.0)

        语法:
            export const NAME = value
            export function NAME(...): ...

        示例:
            export const VERSION = "1.0"
            export function log_info(msg):
                log info msg

        约束:
            - 只能导出 const 或 function
            - 只能在 library 文件中使用
        """
        line = self._peek().line
        self._consume(TokenType.EXPORT, "期望 'export'")

        # 检查下一个 token，必须是 const 或 function
        next_token = self._peek()

        if next_token.type == TokenType.CONST:
            # export const ...
            target = self._parse_const_statement()
        elif next_token.type == TokenType.FUNCTION:
            # export function ...
            target = self._parse_function_def()
        else:
            raise ParserError(
                next_token.line,
                next_token.column,
                next_token.type.name,
                next_token.value,
                "export 只能用于 const 或 function",
                "const | function",
            )

        return ExportStatement(target=target, line=line)

    def _parse_import_statement(self) -> ImportStatement:
        """
        解析 import 语句 (v5.0)

        语法 1 (模块导入):
            import ALIAS from "PATH"

        语法 2 (From-Import):
            from "PATH" import NAME1, NAME2, ...

        示例:
            import logging from "libs/logging.flow"
            from "libs/validation.flow" import validate_email, validate_length

        约束:
            - 路径必须是字符串字面量
            - 路径只支持相对路径（基于当前文件目录）
            - 成员名必须是标识符
        """
        line = self._peek().line

        # 检查语法类型：import 或 from
        if self._check(TokenType.IMPORT):
            # 语法 1: import ALIAS from "PATH"
            self._consume(TokenType.IMPORT, "期望 'import'")

            # 解析模块别名
            alias_token = self._consume(TokenType.IDENTIFIER, "期望模块别名（标识符）")
            module_alias = alias_token.value

            # 期望 from
            self._consume(TokenType.FROM, "期望 'from'")

            # 解析模块路径（必须是字符串字面量）
            path_token = self._consume(TokenType.STRING, "期望模块路径字符串")
            module_path = path_token.value

            # v6.3: Register module alias in symbol table
            from .symbol_table import SymbolType

            self.symbol_table_stack.define(
                name=module_alias,
                value=None,  # Module object created at runtime
                symbol_type=SymbolType.MODULE,
                line_number=line,
            )

            return ImportStatement(
                module_path=module_path, module_alias=module_alias, members=None, line=line
            )

        elif self._check(TokenType.FROM):
            # 语法 2: from "PATH" import NAME1, NAME2, ...
            self._consume(TokenType.FROM, "期望 'from'")

            # 解析模块路径（必须是字符串字面量）
            path_token = self._consume(TokenType.STRING, "期望模块路径字符串")
            module_path = path_token.value

            # 期望 import
            self._consume(TokenType.IMPORT, "期望 'import'")

            # 解析成员列表（逗号分隔的标识符）
            members = []

            # 第一个成员
            # v5.0: 允许某些关键字作为成员名（与成员访问一致）
            if self._check(TokenType.IDENTIFIER):
                first_member = self._consume(TokenType.IDENTIFIER, "期望成员名称")
                members.append(first_member.value)
            elif self._peek().type in (
                TokenType.VALUE,
                TokenType.TEXT,
                TokenType.TYPE,
                TokenType.URL,
            ):
                first_member = self._advance()
                members.append(first_member.value)
            else:
                token = self._peek()
                raise ParserError(
                    token.line,
                    token.column,
                    token.type.name,
                    token.value,
                    "期望成员名称（标识符或关键字）",
                    "IDENTIFIER | VALUE | TEXT | TYPE | URL",
                )

            # 后续成员（可选）
            while self._check(TokenType.COMMA):
                self._consume(TokenType.COMMA, "期望 ','")
                # v5.0: 允许某些关键字作为成员名
                if self._check(TokenType.IDENTIFIER):
                    member_token = self._consume(TokenType.IDENTIFIER, "期望成员名称")
                    members.append(member_token.value)
                elif self._peek().type in (
                    TokenType.VALUE,
                    TokenType.TEXT,
                    TokenType.TYPE,
                    TokenType.URL,
                ):
                    member_token = self._advance()
                    members.append(member_token.value)
                else:
                    token = self._peek()
                    raise ParserError(
                        token.line,
                        token.column,
                        token.type.name,
                        token.value,
                        "期望成员名称（标识符或关键字）",
                        "IDENTIFIER | VALUE | TEXT | TYPE | URL",
                    )

            # v6.3: Register imported members in symbol table
            from .symbol_table import SymbolType

            for member_name in members:
                self.symbol_table_stack.define(
                    name=member_name,
                    value=None,  # Imported value bound at runtime
                    symbol_type=SymbolType.IMPORTED,
                    line_number=line,
                )

            return ImportStatement(
                module_path=module_path, module_alias=None, members=members, line=line
            )

        else:
            # 不应该到达这里（因为 _parse_statement 已经检查了 IMPORT token）
            token = self._peek()
            raise ParserError(
                token.line,
                token.column,
                token.type.name,
                token.value,
                "期望 'import' 或 'from'",
                "import | from",
            )

    # ============================================================
    # v2.0 变量语句解析
    # ============================================================

    def _parse_let_statement(self) -> LetStatement:
        """
        解析 let 语句

        v6.3: 添加 VR-003 检查
        """
        line = self._peek().line
        self._consume(TokenType.LET, "期望 'let'")
        name_token = self._consume_identifier_or_keyword("期望变量名")

        # v6.3: VR-003 检查 - 同一作用域不能重复声明
        # 只检查当前作用域，允许变量遮蔽（在子作用域声明同名变量）
        if self.symbol_table_stack.exists_in_current_scope(name_token.value):
            raise ParserError(
                line,
                0,  # 列号暂不可用
                "IDENTIFIER",
                name_token.value,
                f"变量 '{name_token.value}' 重复声明（VR-003 违规）",
                f"同一作用域内不能声明同名变量。如需在子作用域使用同名变量，请在嵌套块中声明",
            )

        self._consume(TokenType.EQUALS_SIGN, "期望 '='")
        value = self._parse_expression()

        # 将变量添加到符号表
        self.symbol_table_stack.define(
            name=name_token.value,
            value=None,  # 值在运行时计算，这里不存储
            symbol_type=SymbolType.VARIABLE,
            line_number=line,
        )

        return LetStatement(name=name_token.value, value=value, line=line)

    def _parse_const_statement(self) -> ConstStatement:
        """
        解析 const 语句

        v6.3: 添加 VR-003 检查
        """
        line = self._peek().line
        self._consume(TokenType.CONST, "期望 'const'")
        name_token = self._consume_identifier_or_keyword("期望常量名")

        # v6.3: VR-003 检查 - 同一作用域不能重复声明
        # 只检查当前作用域，允许常量遮蔽（在子作用域声明同名常量）
        if self.symbol_table_stack.exists_in_current_scope(name_token.value):
            raise ParserError(
                line,
                0,  # 列号暂不可用
                "IDENTIFIER",
                name_token.value,
                f"常量 '{name_token.value}' 重复声明（VR-003 违规）",
                f"同一作用域内不能声明同名常量。如需在子作用域使用同名常量，请在嵌套块中声明",
            )

        self._consume(TokenType.EQUALS_SIGN, "期望 '='")
        value = self._parse_expression()

        # 将常量添加到符号表
        self.symbol_table_stack.define(
            name=name_token.value, value=None, symbol_type=SymbolType.CONSTANT, line_number=line
        )

        return ConstStatement(name=name_token.value, value=value, line=line)

    def _parse_assignment(self) -> Assignment:
        """
        解析赋值语句

        v6.3: 添加 VR-002 和 VR-004 检查
        """
        line = self._peek().line
        name_token = self._consume_identifier_or_keyword("期望变量名")

        # v6.3: VR-004 检查 - 系统变量只读（优先检查）
        if name_token.value in SYSTEM_VARIABLES:
            raise ParserError(
                line,
                0,  # 列号暂不可用
                "IDENTIFIER",
                name_token.value,
                f"不能修改系统变量 '{name_token.value}'（VR-004 违规）",
                f"系统变量 (page, env, response) 是只读的",
            )

        # v6.3: VR-002 检查 - 常量不能重新赋值
        symbol = self.symbol_table_stack.current_scope()._lookup(name_token.value)  # type: ignore[attr-defined]
        if symbol and symbol.symbol_type == SymbolType.CONSTANT:
            raise ParserError(
                line,
                0,  # 列号暂不可用
                "IDENTIFIER",
                name_token.value,
                f"不能修改常量 '{name_token.value}'（VR-002 违规）",
                f"常量在定义后不可修改（定义于第 {symbol.line_number} 行）。请使用 'let' 声明可变变量",
            )

        self._consume(TokenType.EQUALS_SIGN, "期望 '='")
        value = self._parse_expression()

        return Assignment(name=name_token.value, value=value, line=line)

    # ============================================================
    # v2.0 循环语句解析
    # ============================================================

    def _parse_for_each_loop(self) -> EachLoop:
        """
        解析 for 循环语句 (v3.0+: Python 风格, v4.0: 支持多变量元组解包)

        语法:
            # 单变量循环
            for item in items:
                ...

            # 多变量循环（元组解包）
            for index, item in enumerate(items):
                ...

        特性:
        - 支持 break/continue（与 while 一致）
        - 每次迭代创建独立作用域
        - v4.0: 支持多变量解包（for a, b in ...）
        """
        line = self._peek().line
        self._consume(TokenType.FOR, "期望 'for'")

        # 解析循环变量（单变量或多变量）
        variable_names = []

        # 第一个变量名
        first_var = self._consume_identifier_or_keyword("期望循环变量名").value
        variable_names.append(first_var)

        # 检查是否有逗号（多变量）
        while self._check(TokenType.COMMA):
            self._consume(TokenType.COMMA, "期望 ','")
            var_name = self._consume_identifier_or_keyword("期望循环变量名").value
            variable_names.append(var_name)

        self._consume(TokenType.IN, "期望 'in'")
        iterable = self._parse_expression()
        self._consume(TokenType.COLON, "期望 ':'")
        self._consume(TokenType.NEWLINE, "期望换行")
        self._consume(TokenType.INDENT, "期望缩进")

        # 进入循环体（增加循环深度，与 while 一致）
        self._loop_depth += 1

        # 创建 for 循环作用域（修复 VR-VAR-003 bug）
        self.symbol_table_stack.enter_scope("for_loop")

        # v6.3: 提前注册循环变量（VR-001 所需）
        # 支持多变量解包（v4.0）
        from .symbol_table import SymbolType

        for var_name in variable_names:
            self.symbol_table_stack.define(
                name=var_name,
                value=None,  # 值在运行时绑定
                symbol_type=SymbolType.LOOP_VARIABLE,
                line_number=line,
            )

        try:
            # 解析循环体
            statements = []
            while not self._check(TokenType.DEDENT) and not self._is_at_end():
                if self._check(TokenType.NEWLINE):
                    self._advance()
                    continue

                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)

                self._skip_newlines()

            # v3.0: 消费 DEDENT
            self._consume(TokenType.DEDENT, "期望反缩进")

            return EachLoop(
                variable_names=variable_names, iterable=iterable, statements=statements, line=line
            )

        finally:
            # 退出循环作用域
            self.symbol_table_stack.exit_scope()
            # 退出循环体（恢复循环深度，与 while 一致）
            self._loop_depth -= 1

    # ============================================================
    # v3.0 While 循环语句解析
    # ============================================================

    def _parse_while_loop(self) -> WhileLoop:
        """
        解析 while 循环语句 (v3.0)

        语法:
            while condition:
                statement1
                statement2

        特性:
        - 条件驱动的循环
        - 支持 break/continue
        - 不创建新作用域
        - 提供死循环保护

        示例:
            while count < 5:
                log f"Count: {count}"
                count = count + 1

            while not loaded and timeout < 10:
                if element_exists("#content"):
                    loaded = True
                else:
                    wait 0.5
                    timeout = timeout + 0.5
        """
        line = self._peek().line
        self._consume(TokenType.WHILE, "期望 'while'")

        # 解析条件表达式
        condition = self._parse_expression()

        self._consume(TokenType.COLON, "期望 ':'")
        self._consume(TokenType.NEWLINE, "期望换行")
        self._consume(TokenType.INDENT, "期望缩进")

        # 进入循环体 (增加循环深度)
        self._loop_depth += 1

        try:
            # 解析循环体
            statements = []
            while not self._check(TokenType.DEDENT) and not self._is_at_end():
                if self._check(TokenType.NEWLINE):
                    self._advance()
                    continue

                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)

                self._skip_newlines()

            # 消费 DEDENT
            self._consume(TokenType.DEDENT, "期望反缩进")

            return WhileLoop(condition=condition, statements=statements, line=line)

        finally:
            # 退出循环体 (恢复循环深度)
            self._loop_depth -= 1

    def _parse_break(self) -> BreakStatement:
        """
        解析 break 语句 (v3.0)

        语法:
            break

        语义:
        - 立即退出最内层循环（while 或 for）
        - 只能在循环内使用

        验证:
        - 检查是否在循环内 (self._loop_depth > 0)

        示例:
            while True:
                let response = http.get(url=STATUS_URL)
                if response.ok:
                    break
                wait 2
        """
        line = self._peek().line
        self._consume(TokenType.BREAK, "期望 'break'")

        # 验证 break 在循环内
        if self._loop_depth == 0:
            raise RuntimeError(f"行 {line}: break 语句只能在循环内使用")

        return BreakStatement(line=line)

    def _parse_continue(self) -> ContinueStatement:
        """
        解析 continue 语句 (v3.0)

        语法:
            continue

        语义:
        - 跳过当前迭代的剩余语句
        - 直接进入下一次循环迭代（while 或 for）
        - 只能在循环内使用

        验证:
        - 检查是否在循环内 (self._loop_depth > 0)

        示例:
            while items.length() > 0:
                let item = items.pop(0)
                if item == "":
                    continue
                process(item)
        """
        line = self._peek().line
        self._consume(TokenType.CONTINUE, "期望 'continue'")

        # 验证 continue 在循环内
        if self._loop_depth == 0:
            raise RuntimeError(f"行 {line}: continue 语句只能在循环内使用")

        return ContinueStatement(line=line)

    # ============================================================
    # v4.3 函数定义和返回语句解析
    # ============================================================

    def _parse_function_def(self) -> FunctionDefNode:
        """
        解析函数定义语句 (v4.3)

        语法:
            function functionName(param1, param2):
                statement1
                statement2
                return expression

        特性:
        - 定义用户自定义函数
        - 函数具有独立的局部作用域
        - 参数按值传递
        - 不支持递归 (运行时检测)
        - 不支持闭包

        示例:
            function add(a, b):
                return a + b

            function isValidEmail(email):
                return email contains "@" and email contains "."

            function validateUser(email, password):
                if not isValidEmail(email):
                    return False
                if not isStrongPassword(password):
                    return False
                return True
        """
        line = self._peek().line
        self._consume(TokenType.FUNCTION, "期望 'function'")

        # 解析函数名
        if not self._check(TokenType.IDENTIFIER):
            raise ParserError(
                self._peek().line,
                self._peek().column,
                self._peek().type.name,
                self._peek().value,
                "期望函数名 (标识符)",
            )
        func_name = self._advance().value

        # 解析参数列表
        self._consume(TokenType.LPAREN, "期望 '('")

        params = []
        if not self._check(TokenType.RPAREN):
            # 解析第一个参数（允许部分保留字作为参数名）
            param_token = self._peek()
            if param_token.type == TokenType.IDENTIFIER:
                params.append(self._advance().value)
            elif param_token.type in (
                TokenType.VALUE,
                TokenType.TEXT,
                TokenType.TYPE,
                TokenType.URL,
            ):
                # 允许这些关键字作为参数名
                params.append(self._advance().value.lower())
            else:
                raise ParserError(
                    param_token.line,
                    param_token.column,
                    param_token.type.name,
                    param_token.value,
                    "期望参数名 (标识符)",
                )

            # 解析后续参数 (逗号分隔)
            while self._match(TokenType.COMMA):
                param_token = self._peek()
                if param_token.type == TokenType.IDENTIFIER:
                    params.append(self._advance().value)
                elif param_token.type in (
                    TokenType.VALUE,
                    TokenType.TEXT,
                    TokenType.TYPE,
                    TokenType.URL,
                ):
                    # 允许这些关键字作为参数名
                    params.append(self._advance().value.lower())
                else:
                    raise ParserError(
                        param_token.line,
                        param_token.column,
                        param_token.type.name,
                        param_token.value,
                        "期望参数名 (标识符)",
                    )

        self._consume(TokenType.RPAREN, "期望 ')'")
        self._consume(TokenType.COLON, "期望 ':'")
        self._consume(TokenType.NEWLINE, "期望换行")
        self._consume(TokenType.INDENT, "期望缩进")

        # v6.3: 创建函数作用域并注册参数（VR-001 所需）
        self.symbol_table_stack.enter_scope(f"function_{func_name}")

        try:
            # v6.3: 提前注册函数参数
            from .symbol_table import SymbolType

            for param in params:
                self.symbol_table_stack.define(
                    name=param,
                    value=None,  # 值在运行时传入
                    symbol_type=SymbolType.PARAMETER,
                    line_number=line,
                )

            # 解析函数体
            body = []
            while not self._check(TokenType.DEDENT) and not self._is_at_end():
                if self._check(TokenType.NEWLINE):
                    self._advance()
                    continue

                stmt = self._parse_statement()
                if stmt:
                    body.append(stmt)

                self._skip_newlines()

            # 消费 DEDENT
            self._consume(TokenType.DEDENT, "期望反缩进")

            return FunctionDefNode(name=func_name, params=params, body=body, line=line)

        finally:
            # v6.3: 退出函数作用域（确保异常安全）
            self.symbol_table_stack.exit_scope()

    def _parse_return_statement(self) -> ReturnNode:
        """
        解析 return 语句 (v4.3)

        语法:
            return expression
            return

        语义:
        - 从函数中返回值
        - 可以返回表达式结果
        - 可以无返回值 (return None)
        - 只能在函数体内使用

        示例:
            return a + b
            return True
            return

        注意:
        - 运行时会验证 return 是否在函数内使用
        """
        line = self._peek().line
        self._consume(TokenType.RETURN, "期望 'return'")

        # 检查是否有返回值表达式
        # 如果下一个 token 是换行或文件结束,则无返回值
        value = None
        if not self._check(TokenType.NEWLINE) and not self._is_at_end():
            value = self._parse_expression()

        return ReturnNode(value=value, line=line)

    # ============================================================
    # v2.0 日志和提取语句解析
    # ============================================================

    def _parse_log_statement(self) -> LogStatement:
        """
        解析 log 语句 (支持字符串插值和日志级别) - v4.3+

        语法:
            log "message"                    # 默认 info 级别
            log info "message"               # 显式级别
            log debug "message"              # 调试信息
            log success "message"            # 成功消息
            log warning "message"            # 警告消息
            log error "message"              # 错误消息
            log success f"用户 {name} 注册成功"  # 支持 f-string
        """
        line = self._peek().line
        self._consume(TokenType.LOG, "期望 'log'")

        # 检查是否有日志级别关键字 (v4.3+)
        level = "info"  # 默认级别
        valid_levels = ["debug", "info", "success", "warning", "error"]

        # 向前看一个 token，检查是否是级别关键字
        if self._check(TokenType.IDENTIFIER):
            next_token = self._peek()
            if next_token.value in valid_levels:
                level = next_token.value
                self._advance()  # 消费级别关键字

        # 解析消息 (可能是字符串插值)
        if self._match(TokenType.STRING):
            message = self._parse_string_with_interpolation()
        else:
            # 如果不是字符串,尝试解析为表达式
            message = self._parse_expression()

        return LogStatement(message=message, level=level, line=line)

    def _parse_extract_statement(self) -> ExtractStatement:
        """
        解析 extract 语句 (v3.0: 支持多种 pattern 位置, v3.3: 完全表达式支持)

        语法:
            extract text from "selector" into variable_name
            extract text from "selector" pattern "regex" into var  # v3.0
            extract attr "href" from "selector" into url
            extract pattern "regex" from "selector" into result    # v2.0
        """
        line = self._peek().line
        self._consume(TokenType.EXTRACT, "期望 'extract'")

        # 提取类型
        extract_type = None
        attribute_name = None
        pattern = None

        if self._check(TokenType.TEXT):
            self._advance()
            extract_type = "text"
        elif self._check(TokenType.VALUE):
            self._advance()
            extract_type = "value"
        elif self._check(TokenType.ATTR):
            self._advance()
            extract_type = "attr"
            attribute_name = self._consume(TokenType.STRING, "期望属性名字符串").value
        elif self._check(TokenType.PATTERN):
            self._advance()
            extract_type = "pattern"
            pattern = self._consume(TokenType.STRING, "期望正则表达式字符串").value
        else:
            # 默认为 text
            extract_type = "text"

        # from
        self._consume(TokenType.FROM, "期望 'from'")

        # v3.3: 选择器支持完整表达式
        if (
            self._check(TokenType.STRING)
            or self._check(TokenType.FSTRING)
            or self._check(TokenType.IDENTIFIER)
        ):
            selector = self._parse_expression()
        else:
            raise ParserError(
                self._peek().line,
                self._peek().column,
                self._peek().type.name,
                self._peek().value,
                "期望选择器字符串或表达式",
                "STRING | FSTRING | IDENTIFIER",
            )

        # v3.0: 可选的 pattern "regex" (在 from 之后)
        if self._check(TokenType.PATTERN):
            self._advance()
            pattern = self._consume(TokenType.STRING, "期望正则表达式字符串").value
            extract_type = "pattern"

        # into
        self._consume(TokenType.INTO, "期望 'into'")

        # 变量名 (允许某些关键字作为变量名)
        variable_name = self._parse_variable_name()

        # v6.3: VR-001 要求 - 提前注册 extract 目标变量
        from .symbol_table import SymbolType

        self.symbol_table_stack.define(
            name=variable_name,
            value=None,  # 值在运行时提取
            symbol_type=SymbolType.VARIABLE,
            line_number=line,
        )

        return ExtractStatement(
            extract_type=extract_type,
            selector=selector,
            variable_name=variable_name,
            attribute_name=attribute_name,
            pattern=pattern,
            line=line,
        )

    def _parse_variable_name(self) -> str:
        """解析变量名 (允许某些关键字作为变量名)"""
        token = self._peek()

        # 允许 IDENTIFIER 或某些关键字作为变量名
        # 常见的: url, text, value, type, link, etc.
        if token.type == TokenType.IDENTIFIER:
            return self._advance().value
        elif token.type in (
            TokenType.URL,
            TokenType.TEXT,
            TokenType.VALUE,
            TokenType.TYPE,
            TokenType.LINK,
        ):
            return self._advance().value.lower()
        else:
            raise ParserError(
                token.line, token.column, token.type.name, token.value, "期望变量名", "IDENTIFIER"
            )

    # ============================================================
    # v2.0 表达式解析 (递归下降)
    # ============================================================

    def _parse_expression(self) -> Expression:
        """解析表达式 (入口点)"""
        return self._parse_logical_or()

    def _parse_logical_or(self) -> Expression:
        """解析逻辑或表达式"""
        left = self._parse_logical_and()

        while self._match(TokenType.OR):
            line = self._previous().line
            operator = "OR"
            right = self._parse_logical_and()
            left = BinaryOp(left=left, operator=operator, right=right, line=line)

        return left

    def _parse_logical_and(self) -> Expression:
        """解析逻辑与表达式"""
        left = self._parse_logical_not()

        while self._match(TokenType.AND):
            line = self._previous().line
            operator = "AND"
            right = self._parse_logical_not()
            left = BinaryOp(left=left, operator=operator, right=right, line=line)

        return left

    def _parse_logical_not(self) -> Expression:
        """解析逻辑非表达式"""
        if self._match(TokenType.NOT):
            line = self._previous().line
            operator = "NOT"
            operand = self._parse_comparison()
            return UnaryOp(operator=operator, operand=operand, line=line)

        return self._parse_comparison()

    def _parse_comparison(self) -> Expression:
        """解析比较表达式"""
        left = self._parse_additive()

        if self._match(
            TokenType.GT,
            TokenType.LT,
            TokenType.GTE,
            TokenType.LTE,
            TokenType.EQ,
            TokenType.NEQ,
            TokenType.CONTAINS,
            TokenType.MATCHES,
            TokenType.EQUALS,
        ):
            line = self._previous().line
            token = self._previous()

            # 转换 token 类型为运算符字符串
            if token.type == TokenType.GT:
                operator = ">"
            elif token.type == TokenType.LT:
                operator = "<"
            elif token.type == TokenType.GTE:
                operator = ">="
            elif token.type == TokenType.LTE:
                operator = "<="
            elif token.type == TokenType.EQ:
                operator = "=="
            elif token.type == TokenType.NEQ:
                operator = "!="
            elif token.type == TokenType.CONTAINS:
                operator = "contains"
            elif token.type == TokenType.MATCHES:
                operator = "matches"
            elif token.type == TokenType.EQUALS:
                operator = "equals"
            else:
                operator = token.value

            right = self._parse_additive()
            return BinaryOp(left=left, operator=operator, right=right, line=line)

        return left

    def _parse_additive(self) -> Expression:
        """解析加减表达式"""
        left = self._parse_multiplicative()

        while self._match(TokenType.PLUS, TokenType.MINUS):
            line = self._previous().line
            operator = self._previous().value
            right = self._parse_multiplicative()
            left = BinaryOp(left=left, operator=operator, right=right, line=line)

        return left

    def _parse_multiplicative(self) -> Expression:
        """解析乘除模表达式"""
        left = self._parse_unary()

        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            line = self._previous().line
            operator = self._previous().value
            right = self._parse_unary()
            left = BinaryOp(left=left, operator=operator, right=right, line=line)

        return left

    def _parse_unary(self) -> Expression:
        """解析一元表达式"""
        if self._match(TokenType.PLUS, TokenType.MINUS):
            line = self._previous().line
            operator = self._previous().value
            operand = self._parse_postfix()
            return UnaryOp(operator=operator, operand=operand, line=line)

        return self._parse_postfix()

    def _parse_method_arguments(self, line: int):
        """
        解析方法调用参数列表 (v3.2: 支持位置参数和命名参数)

        语法:
            func()                              # 无参数
            func(arg1, arg2)                    # 仅位置参数
            func(name1=val1, name2=val2)        # 仅命名参数
            func(arg1, name1=val1, name2=val2)  # 混合参数（位置在前）

        支持多行格式:
            func(
                arg1,
                name1=val1,
                name2=val2
            )

        规则:
            1. 位置参数必须在命名参数之前
            2. 识别 identifier=expression 为命名参数
            3. 其他为位置参数

        Returns:
            (arguments: List[Expression], kwargs: Dict[str, Expression])

        Raises:
            ParserError: 位置参数在命名参数之后
        """
        arguments = []  # 位置参数
        kwargs = {}  # 命名参数
        seen_kwarg = False  # 是否已见过命名参数

        # 跳过开括号后的换行符和缩进（支持多行）
        self._skip_newlines_and_indents()

        if not self._check(TokenType.RPAREN):
            while True:
                # 预判是否为命名参数: identifier=expression 或 identifier: expression
                # 需要向前看两个token: IDENTIFIER/KEYWORD, EQUALS_SIGN/COLON
                is_kwarg = False

                # v3.2: 允许某些关键字作为参数名（如 url, text, value, type等）
                valid_param_name_types = (
                    TokenType.IDENTIFIER,
                    TokenType.URL,
                    TokenType.TEXT,
                    TokenType.VALUE,
                    TokenType.TYPE,
                )

                if self._peek().type in valid_param_name_types:
                    # 保存当前位置
                    saved_pos = self.current
                    identifier_token = self._advance()

                    if self._check(TokenType.EQUALS_SIGN) or self._check(TokenType.COLON):
                        # 确实是命名参数 name=value 或 name: value
                        is_kwarg = True
                        # 关键字token需要小写化
                        param_name = (
                            identifier_token.value.lower()
                            if identifier_token.type != TokenType.IDENTIFIER
                            else identifier_token.value
                        )
                        self._advance()  # 消费 '=' 或 ':'

                        # 解析值表达式
                        param_value = self._parse_expression()
                        kwargs[param_name] = param_value
                        seen_kwarg = True
                    else:
                        # 不是命名参数，回退
                        self.current = saved_pos
                        is_kwarg = False

                if not is_kwarg:
                    # 位置参数
                    if seen_kwarg:
                        raise ParserError(
                            line, 0, "PARAMETER", "", "位置参数不能出现在命名参数之后"
                        )
                    arguments.append(self._parse_expression())

                # 检查是否还有更多参数
                if not self._match(TokenType.COMMA):
                    break

                # 跳过逗号后的换行符和缩进（支持多行）
                self._skip_newlines_and_indents()

                # 允许尾随逗号：如果下一个token是右括号，则结束
                if self._check(TokenType.RPAREN):
                    break

        # 跳过右括号前的换行符和缩进（支持多行）
        self._skip_newlines_and_indents()

        return arguments, kwargs

    def _parse_postfix(self) -> Expression:
        """解析后缀表达式 (成员访问、数组访问、方法调用)"""
        expr = self._parse_primary()

        while True:
            # v4.3: 支持直接函数调用 Function(args) - 用于内置函数和用户定义函数
            if isinstance(expr, Identifier) and self._check(TokenType.LPAREN):
                line = expr.line
                self._advance()  # 消费 '('

                # v3.2: 解析参数列表（支持位置参数和命名参数）
                arguments, kwargs = self._parse_method_arguments(line)

                self._consume(TokenType.RPAREN, "期望 ')'")

                # v4.3: 创建 FunctionCall 节点（暂不支持命名参数）
                if kwargs:
                    # 如果有命名参数,仍使用 MethodCall(object=None) 兼容内置函数
                    expr = MethodCall(
                        object=None,
                        method_name=expr.name,
                        arguments=arguments,
                        kwargs=kwargs,
                        line=line,
                    )
                else:
                    # 纯位置参数,使用 FunctionCall
                    expr = FunctionCall(function_name=expr.name, arguments=arguments, line=line)
                continue

            if self._match(TokenType.DOT):
                line = self._previous().line
                # v3.0: 允许某些关键字作为属性名
                if self._check(TokenType.IDENTIFIER):
                    property_name = self._advance().value
                elif self._peek().type in (
                    TokenType.URL,
                    TokenType.TEXT,
                    TokenType.VALUE,
                    TokenType.TYPE,
                ):
                    # v5.0: 保留原始大小写以支持模块系统的大小写敏感成员访问
                    property_name = self._advance().value
                else:
                    token = self._peek()
                    raise ParserError(
                        token.line,
                        token.column,
                        token.type.name,
                        token.value,
                        "期望属性名",
                        "IDENTIFIER",
                    )

                # 检查是否是方法调用: .method(...)
                if self._check(TokenType.LPAREN):
                    # 方法调用
                    self._advance()  # 消费 '('

                    # v3.2: 解析参数列表（支持位置参数和命名参数）
                    arguments, kwargs = self._parse_method_arguments(line)

                    self._consume(TokenType.RPAREN, "期望 ')'")

                    expr = MethodCall(
                        object=expr,
                        method_name=property_name,
                        arguments=arguments,
                        kwargs=kwargs,
                        line=line,
                    )
                else:
                    # 属性访问
                    expr = MemberAccess(object=expr, property=property_name, line=line)

            elif self._match(TokenType.LBRACKET):
                line = self._previous().line
                index = self._parse_expression()
                self._consume(TokenType.RBRACKET, "期望 ']'")
                expr = ArrayAccess(array=expr, index=index, line=line)
            else:
                break

        # v6.3: VR-001 检查 - 变量使用前必须声明
        # 如果最终表达式是 Identifier（即未被转换为函数调用或成员访问的左侧）
        # 则检查该标识符是否已定义
        if isinstance(expr, Identifier):
            var_name = expr.name
            # 跳过系统变量（运行时隐式可用）
            if var_name not in SYSTEM_VARIABLES:
                # 检查符号表中是否存在该变量
                if not self.symbol_table_stack.exists(var_name):
                    raise ParserError(
                        expr.line,
                        0,  # 列号暂不可用
                        "IDENTIFIER",
                        var_name,
                        f"未定义的变量 '{var_name}'（VR-001 违规）",
                        f"在使用前先用 'let' 或 'const' 声明变量",
                    )
                else:
                    # v6.3: VR-006 - 标记符号为已使用
                    try:
                        symbol = self.symbol_table_stack.current_scope()._lookup(var_name)
                        if symbol:
                            symbol.mark_used()
                    except Exception:
                        pass

        return expr

    def _parse_primary(self) -> Expression:
        """
        解析基础表达式 (字面量、标识符、系统变量、括号、数组)

        v4.0: 支持整数（INTEGER）和浮点数（NUMBER）字面量
        """
        line = self._peek().line

        # v4.0: 整数字面量
        if self._match(TokenType.INTEGER):
            value_str = self._previous().value
            # 解析为整数
            try:
                value = int(value_str)
            except ValueError:
                value = 0
            return Literal(value=value, line=line)

        # 浮点数字面量（v4.0: 原 NUMBER，现在只处理浮点数和时间单位）
        if self._match(TokenType.NUMBER):
            value_str = self._previous().value
            # 解析为浮点数
            try:
                value = float(value_str)
            except ValueError:
                value = 0.0
            return Literal(value=value, line=line)

        # 字符串字面量 (可能包含插值)
        if self._match(TokenType.STRING):
            string_value = self._previous().value
            # 检查是否包含插值 {...}
            if "{" in string_value and "}" in string_value:
                return self._parse_string_interpolation(string_value, line)
            else:
                return Literal(value=string_value, line=line)

        # v3.0: f-string 字面量 (显式插值)
        if self._match(TokenType.FSTRING):
            fstring_value = self._previous().value
            # f-string 总是处理插值
            if "{" in fstring_value and "}" in fstring_value:
                return self._parse_string_interpolation(fstring_value, line)
            else:
                # 即使没有插值也返回字符串
                return Literal(value=fstring_value, line=line)

        # 布尔字面量
        if self._match(TokenType.TRUE):
            return Literal(value=True, line=line)

        if self._match(TokenType.FALSE):
            return Literal(value=False, line=line)

        # null 字面量
        if self._match(TokenType.NONE):
            return Literal(value=None, line=line)

        # 数组字面量 [element1, element2, ...]
        if self._match(TokenType.LBRACKET):
            return self._parse_array_literal(line)

        # 对象字面量 {key1: value1, key2: value2, ...}
        if self._match(TokenType.LBRACE):
            return self._parse_object_literal(line)

        # v5.1: input() 表达式
        if self._match(TokenType.INPUT):
            # 检查是否是 input() 函数调用
            if self._check(TokenType.LPAREN):
                return self._parse_input_expression(line)
            else:
                # 否则作为标识符处理（用于 select input 等场景）
                return Identifier(name="input", line=line)

        # 标识符 (变量引用) 或 Lambda 表达式 (x => expr)
        if self._match(TokenType.IDENTIFIER):
            name = self._previous().value
            # v6.4: 检查是否是单参数 Lambda 表达式
            if self._check(TokenType.ARROW):
                self._advance()  # 消耗 =>
                # 创建新作用域并注册参数（避免 VR-001 错误）
                self.symbol_table_stack.enter_scope(f"lambda_param_line_{line}")
                try:
                    self.symbol_table_stack.define(
                        name=name,
                        value=None,  # Parser 阶段不需要实际值
                        symbol_type=SymbolType.VARIABLE,
                        line_number=line,
                    )
                    body = self._parse_expression()
                    return LambdaExpression(parameters=[name], body=body, line=line)
                finally:
                    self.symbol_table_stack.exit_scope()
            return Identifier(name=name, line=line)

        # v3.0: 允许某些关键字作为标识符（常用属性名）
        # 如 value, text, type, url 等
        if self._peek().type in (TokenType.VALUE, TokenType.TEXT, TokenType.TYPE, TokenType.URL):
            keyword_token = self._advance()
            name = keyword_token.value
            return Identifier(name=name, line=line)

        # 括号表达式 或 多参数 Lambda (v6.4)
        if self._match(TokenType.LPAREN):
            # 向前看：检查是否是多参数 Lambda
            # 格式: (param1, param2) => expr
            saved_pos = self.current
            try:
                # 尝试解析参数列表
                params = []
                # 允许空参数列表
                if not self._check(TokenType.RPAREN):
                    # 第一个参数
                    if self._check(TokenType.IDENTIFIER):
                        params.append(self._advance().value)
                        # 后续参数
                        while self._match(TokenType.COMMA):
                            if self._check(TokenType.IDENTIFIER):
                                params.append(self._advance().value)
                            else:
                                # 不是标识符，不是 Lambda
                                raise Exception("Not a lambda")
                    else:
                        # 不是标识符，不是 Lambda
                        raise Exception("Not a lambda")

                # 检查右括号和箭头
                if self._check(TokenType.RPAREN):
                    self._advance()
                    if self._check(TokenType.ARROW):
                        # 确认是 Lambda！
                        self._advance()  # 消耗 =>
                        # 创建新作用域并注册所有参数（避免 VR-001 错误）
                        self.symbol_table_stack.enter_scope(f"lambda_params_line_{line}")
                        try:
                            for param in params:
                                self.symbol_table_stack.define(
                                    name=param,
                                    value=None,  # Parser 阶段不需要实际值
                                    symbol_type=SymbolType.VARIABLE,
                                    line_number=line,
                                )
                            body = self._parse_expression()
                            return LambdaExpression(parameters=params, body=body, line=line)
                        finally:
                            self.symbol_table_stack.exit_scope()

                # 不是 Lambda，回退
                raise Exception("Not a lambda")

            except Exception:
                # 回退到括号位置，按普通括号表达式处理
                self.current = saved_pos
                expr = self._parse_expression()
                self._consume(TokenType.RPAREN, "期望 ')'")
                return expr

        # 无法识别的表达式
        token = self._peek()
        raise ParserError(
            token.line,
            token.column,
            token.type.name,
            token.value,
            f"期望表达式，得到 {token.type.name}",
        )

    def _parse_array_literal(self, line: int) -> "ArrayLiteral":
        """
        解析数组字面量

        语法: [element1, element2, ...]

        示例:
            []                    # 空数组
            [1, 2, 3]            # 数字数组
            ["a", "b"]           # 字符串数组
            [x + 1, y * 2]       # 表达式元素
            [[1, 2], [3, 4]]     # 嵌套数组

        Args:
            line: 行号（已经消费了 '[' token）

        Returns:
            ArrayLiteral 节点
        """
        from .ast_nodes import ArrayLiteral

        elements = []

        # 跳过开头的换行符和缩进（支持多行数组）
        self._skip_newlines_and_indents()

        # 空数组: []
        if self._check(TokenType.RBRACKET):
            self._advance()  # 消费 ']'
            return ArrayLiteral(elements=[], line=line)

        # 解析第一个元素
        elements.append(self._parse_expression())

        # 解析剩余元素
        while self._match(TokenType.COMMA):
            # 跳过逗号后的换行符和缩进
            self._skip_newlines_and_indents()

            # 允许尾随逗号: [1, 2, 3,]
            if self._check(TokenType.RBRACKET):
                break

            elements.append(self._parse_expression())

        # 跳过结尾的换行符和缩进
        self._skip_newlines_and_indents()

        # 期望 ']'
        self._consume(TokenType.RBRACKET, "期望 ']' 结束数组字面量")

        return ArrayLiteral(elements=elements, line=line)

    def _parse_object_literal(self, line: int) -> "ObjectLiteral":
        """
        解析对象字面量

        语法: {key1: value1, key2: value2, ...}

        示例:
            {}                                    # 空对象
            {name: "Alice", age: 25}             # 简单对象
            {x: 10, y: 20}                       # 多个属性
            {"first-name": "Alice"}              # 字符串键
            {count: x + 1}                       # 表达式值

        Args:
            line: 行号（已经消费了 '{' token）

        Returns:
            ObjectLiteral 节点
        """
        from .ast_nodes import ObjectLiteral

        pairs = []

        # 跳过开头的换行符和缩进（支持多行对象）
        self._skip_newlines_and_indents()

        # 空对象: {}
        if self._check(TokenType.RBRACE):
            self._advance()  # 消费 '}'
            return ObjectLiteral(pairs=[], line=line)

        # 解析第一个键值对
        pairs.append(self._parse_object_pair())

        # 解析剩余键值对
        while self._match(TokenType.COMMA):
            # 跳过逗号后的换行符和缩进
            self._skip_newlines_and_indents()

            # 允许尾随逗号: {a: 1, b: 2,}
            if self._check(TokenType.RBRACE):
                break

            pairs.append(self._parse_object_pair())

        # 跳过结尾的换行符和缩进
        self._skip_newlines_and_indents()

        # 期望 '}'
        self._consume(TokenType.RBRACE, "期望 '}' 结束对象字面量")

        return ObjectLiteral(pairs=pairs, line=line)

    def _parse_object_pair(self) -> tuple[str, Expression]:
        """
        解析对象键值对

        语法: (identifier | string_literal | keyword) ":" expression

        Returns:
            (key, value_expr) 元组
        """
        # key 可以是标识符、字符串或某些关键字
        token = self._peek()

        if self._check(TokenType.IDENTIFIER):
            key = self._advance().value
        elif self._check(TokenType.STRING):
            key = self._advance().value
        # v3.0: 允许某些关键字作为对象键（常见属性名）
        elif token.type in (TokenType.VALUE, TokenType.TEXT, TokenType.TYPE, TokenType.URL):
            key = self._advance().value.lower()
        else:
            raise ParserError(
                token.line,
                token.column,
                token.type.name,
                token.value,
                "期望标识符、字符串或关键字作为对象键",
                "IDENTIFIER | STRING | keyword",
            )

        # 期望 ':'
        self._consume(TokenType.COLON, "期望 ':'")

        # 解析值表达式
        value = self._parse_expression()

        return (key, value)

    def _parse_input_expression(self, line: int) -> "InputExpression":
        """
        解析 input() 表达式 (v5.1)

        语法:
            input(PROMPT)
            input(PROMPT, default=DEFAULT_VALUE)
            input(PROMPT, type=TYPE)
            input(PROMPT, default=DEFAULT_VALUE, type=TYPE)

        示例:
            input("请输入姓名: ")
            input("请输入邮箱: ", default="test@example.com")
            input("请输入密码: ", type=password)
            input("请输入年龄: ", type=integer)

        Args:
            line: 行号（已经消费了 INPUT token）

        Returns:
            InputExpression 节点
        """
        # 消费 '('
        self._consume(TokenType.LPAREN, "期望 '(' 在 input 后")

        # 解析必需的提示文本参数
        prompt = self._parse_expression()

        # 解析可选的命名参数
        default_value = None
        input_type = "text"

        while self._match(TokenType.COMMA):
            # 跳过换行符和缩进（支持多行参数）
            self._skip_newlines_and_indents()

            # 允许尾随逗号
            if self._check(TokenType.RPAREN):
                break

            # 解析参数名
            param_token = self._peek()

            # 参数名可以是 IDENTIFIER 或保留字（如 TYPE）
            if self._check(TokenType.IDENTIFIER):
                param_name = self._advance().value
            elif self._check(TokenType.TYPE):
                # 'type' 作为参数名
                param_name = self._advance().value
            else:
                raise ParserError(
                    param_token.line,
                    param_token.column,
                    param_token.type.name,
                    param_token.value,
                    "期望参数名（identifier或type关键字）",
                    "IDENTIFIER | TYPE",
                )

            # 期望 '=' 或 ':'
            if not (self._match(TokenType.EQUALS_SIGN) or self._match(TokenType.COLON)):
                token = self._peek()
                raise ParserError(
                    token.line,
                    token.column,
                    token.type.name,
                    token.value,
                    "期望 '=' 或 ':'",
                    "EQUALS_SIGN | COLON",
                )

            # 解析参数值
            if param_name == "default":
                default_value = self._parse_expression()
            elif param_name == "type":
                # type 参数期望是标识符（text, password, integer, float）
                type_token = self._peek()

                if self._check(TokenType.IDENTIFIER):
                    input_type = self._advance().value
                elif type_token.type in (TokenType.TEXT, TokenType.INPUT):
                    # 允许关键字 text 和 input 作为类型名
                    input_type = self._advance().value
                else:
                    raise ParserError(
                        type_token.line,
                        type_token.column,
                        type_token.type.name,
                        type_token.value,
                        "type 参数期望标识符（text, password, integer, float）",
                        "IDENTIFIER",
                    )

                # 验证类型值
                valid_types = ["text", "password", "integer", "float", "input"]
                if input_type == "input":
                    input_type = "text"  # input 等价于 text
                elif input_type not in valid_types:
                    raise ParserError(
                        type_token.line,
                        type_token.column,
                        "TYPE_VALUE",
                        input_type,
                        f"无效的 input type: {input_type}。有效值：{', '.join(valid_types)}",
                    )
            else:
                # 未知参数，跳过
                raise ParserError(
                    param_token.line,
                    param_token.column,
                    "PARAMETER_NAME",
                    param_name,
                    f"未知的 input 参数: {param_name}。有效参数：default, type",
                )

        # 跳过结尾换行符和缩进
        self._skip_newlines_and_indents()

        # 消费 ')'
        self._consume(TokenType.RPAREN, "期望 ')' 结束 input 表达式")

        return InputExpression(
            prompt=prompt, default_value=default_value, input_type=input_type, line=line
        )

    def _parse_string_interpolation(self, string_value: str, line: int) -> StringInterpolation:
        """
        解析字符串插值

        将 "Hello {username}!" 解析为 StringInterpolation 节点
        """
        parts = []
        current = ""
        i = 0

        while i < len(string_value):
            if string_value[i] == "{":
                # 保存当前文本部分
                if current:
                    parts.append(current)
                    current = ""

                # 查找匹配的 }
                j = i + 1
                brace_count = 1
                while j < len(string_value) and brace_count > 0:
                    if string_value[j] == "{":
                        brace_count += 1
                    elif string_value[j] == "}":
                        brace_count -= 1
                    j += 1

                if brace_count != 0:
                    # 不匹配的花括号,当作普通文本
                    current += string_value[i]
                    i += 1
                    continue

                # 提取表达式文本
                expr_text = string_value[i + 1 : j - 1].strip()

                # 处理空表达式 - 添加空字符串字面量
                if not expr_text:
                    parts.append("")  # 空表达式被替换为空字符串
                    i = j
                    continue

                # 解析表达式 (创建临时 lexer 和 parser)
                from .lexer import Lexer

                lexer = Lexer()
                expr_tokens = lexer.tokenize(expr_text)

                # 创建临时 parser 解析表达式
                # v6.3: 共享符号表栈，避免 VR-001 误报
                temp_parser = Parser()
                temp_parser.tokens = expr_tokens
                temp_parser.current = 0
                temp_parser.symbol_table_stack = self.symbol_table_stack  # 共享符号表
                expr = temp_parser._parse_expression()

                parts.append(expr)

                i = j
            else:
                current += string_value[i]
                i += 1

        # 添加最后的文本部分
        if current:
            parts.append(current)

        return StringInterpolation(parts=parts, line=line)

    def _parse_string_with_interpolation(self) -> Expression:
        """
        解析字符串 (可能包含插值)

        在已经匹配 STRING token 后调用
        """
        line = self._previous().line
        string_value = self._previous().value

        # 检查是否包含插值
        if "{" in string_value and "}" in string_value:
            return self._parse_string_interpolation(string_value, line)
        else:
            return Literal(value=string_value, line=line)

    # ============================================================
    # 辅助方法
    # ============================================================

    def _match(self, *token_types: TokenType) -> bool:
        """
        检查当前 token 是否匹配任意一种类型，如果匹配则消费并返回 True

        这是递归下降解析中常用的辅助方法
        """
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _parse_time_value(self, value: str) -> float:
        """
        解析时间值，转换为秒

        Args:
            value: 时间值字符串（如 "3s", "500ms", "2.5s", "3sec", "2second", "5seconds", "200milliseconds"）

        Returns:
            时间值（秒）
        """
        value_lower = value.lower()

        # 毫秒 - 先检查完整单词，再检查缩写
        if value_lower.endswith("milliseconds"):
            return float(value[:-12]) / 1000.0
        elif value_lower.endswith("ms"):
            return float(value[:-2]) / 1000.0
        # 秒 - 多种格式
        elif value_lower.endswith("seconds"):
            return float(value[:-7])
        elif value_lower.endswith("second"):
            return float(value[:-6])
        elif value_lower.endswith("sec"):
            return float(value[:-3])
        elif value_lower.endswith("s"):
            return float(value[:-1])
        else:
            # 无单位，默认为秒
            return float(value)

    def _check(self, token_type: TokenType) -> bool:
        """检查当前 token 是否是指定类型"""
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _check_any(self, *token_types: TokenType) -> bool:
        """检查当前 token 是否是任意一种指定类型"""
        for token_type in token_types:
            if self._check(token_type):
                return True
        return False

    def _advance(self) -> Token:
        """消费当前 token 并前进"""
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        """检查是否到达 token 流末尾"""
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        """查看当前 token（不消费）"""
        return self.tokens[self.current]

    def _previous(self) -> Token:
        """返回上一个 token"""
        return self.tokens[self.current - 1]

    def _consume(self, token_type: TokenType, message: str) -> Token:
        """消费指定类型的 token，如果不匹配则抛出错误"""
        if self._check(token_type):
            return self._advance()

        token = self._peek()
        raise ParserError(
            token.line, token.column, token.type.name, token.value, message, token_type.name
        )

    def _consume_numeric(self, message: str) -> Token:
        """
        消费数字 token（INTEGER 或 NUMBER），如果都不匹配则抛出错误

        v4.0: 支持同时接受整数和浮点数字面量
        """
        if self._check_any(TokenType.INTEGER, TokenType.NUMBER):
            return self._advance()

        token = self._peek()
        raise ParserError(
            token.line, token.column, token.type.name, token.value, message, "INTEGER or NUMBER"
        )

    def _consume_any(self, token_types: List[TokenType], message: str) -> Token:
        """消费任意一种指定类型的 token"""
        for token_type in token_types:
            if self._check(token_type):
                return self._advance()

        token = self._peek()
        expected = " | ".join(t.name for t in token_types)
        raise ParserError(token.line, token.column, token.type.name, token.value, message, expected)

    def _skip_newlines(self):
        """跳过所有换行符"""
        while self._check(TokenType.NEWLINE):
            self._advance()

    def _skip_newlines_and_indents(self):
        """
        跳过所有换行符和缩进 tokens（用于对象/数组字面量）

        v3.0: 在解析对象和数组字面量时，需要跳过 INDENT/DEDENT tokens
        因为这些结构可以跨多行且带有缩进，但缩进对字面量语义无影响
        """
        while self._check_any(TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT):
            self._advance()

    def _consume_identifier_or_keyword(self, message: str) -> Token:
        """
        消费标识符或允许作为标识符的关键字

        v3.0: 允许 value, text, type, url 等常用词作为变量名

        Args:
            message: 错误消息

        Returns:
            Token 对象
        """
        # 允许的关键字类型（可以作为标识符使用）
        allowed_keyword_types = (TokenType.VALUE, TokenType.TEXT, TokenType.TYPE, TokenType.URL)

        if self._check(TokenType.IDENTIFIER):
            return self._advance()
        elif self._peek().type in allowed_keyword_types:
            return self._advance()
        else:
            token = self._peek()
            raise ParserError(
                token.line, token.column, token.type.name, token.value, message, "IDENTIFIER"
            )

    # ========================================================================
    # VR-006: 未使用变量警告 (v6.3+)
    # ========================================================================

    def _check_unused_variables(self):
        """
        检查未使用的变量并生成警告（VR-006）

        遍历所有作用域的符号表，对于未使用的用户定义变量生成警告。

        例外情况（不生成警告）：
        - 系统变量（page, env, response）
        - 函数定义（函数本身可以未被调用）
        - 以下划线开头的变量（约定俗成的"私有"或"忽略"变量）
        """
        from .errors import Warning

        all_symbols = self.symbol_table_stack.get_all_symbols()

        for name, symbol in all_symbols.items():
            # 跳过系统变量
            if symbol.symbol_type == SymbolType.SYSTEM:
                continue

            # 跳过函数定义（函数可以未被调用）
            if symbol.symbol_type == SymbolType.FUNCTION:
                continue

            # 跳过以下划线开头的变量（约定的"忽略"变量）
            if name.startswith("_"):
                continue

            # 检查是否未使用
            if not symbol.is_used:
                # 根据符号类型生成不同的建议
                if symbol.symbol_type == SymbolType.PARAMETER:
                    suggestion = f"如果不需要此参数，考虑使用 '_{name}' 表示忽略"
                elif symbol.symbol_type == SymbolType.IMPORTED:
                    suggestion = f"移除未使用的导入，或使用该符号"
                else:
                    suggestion = f"移除未使用的变量，或使用它"

                warning = Warning(
                    warning_code="VR-006",
                    message=f"变量 '{name}' 声明但从未使用",
                    line=symbol.line_number,
                    symbol_name=name,
                    suggestion=suggestion,
                )

                self.warnings.append(warning)

    def get_warnings(self) -> List["Warning"]:
        """
        获取所有警告（v6.3 - VR-006）

        Returns:
            警告列表
        """
        return self.warnings
