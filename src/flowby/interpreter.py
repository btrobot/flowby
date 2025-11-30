"""
DSL 解释器

遍历 AST 并执行相应动作
"""

from typing import TYPE_CHECKING, Optional, Any, Dict
from pathlib import Path

if TYPE_CHECKING:
    from .context import ExecutionContext

from .ast_nodes import (
    Program,
    NavigateToStatement,
    GoBackStatement,
    GoForwardStatement,
    ReloadStatement,
    WaitDurationStatement,
    WaitForStateStatement,
    WaitForElementStatement,
    WaitForNavigationStatement,
    WaitUntilStatement,
    SelectStatement,
    TypeAction,
    ClickAction,
    HoverAction,
    ClearAction,
    PressAction,
    ScrollAction,
    CheckAction,
    UploadAction,
    SelectOptionAction,
    AssertStatement,
    ScreenshotStatement,
    StepBlock,
    IfBlock,
    WhenBlock,
    SetVariableStatement,
    ExtractStatement,
    LogStatement,
    ASTNode,
    # v2.0 新增节点
    LetStatement,
    ConstStatement,
    Assignment,
    EachLoop,
    Expression,
    # v3.0 While 循环节点
    WhileLoop,
    BreakStatement,
    ContinueStatement,
    # v4.1 Exit 语句
    ExitStatement,
    # v4.2 Resource 语句
    ResourceStatement,
    # v4.3 函数定义
    FunctionDefNode,
    ReturnNode,
    ExpressionStatement,
    # v5.0 Module System
    LibraryDeclaration,
    ExportStatement,
    ImportStatement,
)

from .actions import (
    # 导航
    execute_navigate_to,
    execute_go_back,
    execute_go_forward,
    execute_reload,
    # 等待
    execute_wait_duration,
    execute_wait_for_state,
    execute_wait_for_element,
    execute_wait_for_navigation,
    execute_wait_until,
    # 交互
    execute_select,
    execute_type,
    execute_click,
    execute_hover,
    execute_clear,
    execute_press,
    execute_scroll,
    execute_check,
    execute_upload,
    execute_select_option,
    # 断言
    execute_assert_url,
    execute_assert_element,
    execute_assert_text,
    execute_assert_value,
    # 截图
    execute_screenshot,
)

from .actions.assertion import _check_condition
from .errors import ExecutionError, ReturnException
from .context import ExecutionStatus

# v2.0 新增导入
from .symbol_table import SymbolTableStack, SymbolType, FunctionSymbol
from .system_variables import SystemVariables
from .expression_evaluator import ExpressionEvaluator
# v5.0 新增导入
from .module_system import ModuleLoader, ModuleInfo


# ============================================================
# v3.0 While 循环控制流
# ============================================================

class BreakException(Exception):
    """
    Break 语句异常 (v3.0)

    用于实现 break 语句的控制流。
    当执行 break 语句时抛出此异常，由最内层循环捕获。

    用法:
        在 _execute_break() 中抛出，在 _execute_while_loop() 中捕获。
    """
    pass


class ContinueException(Exception):
    """
    Continue 语句异常 (v3.0)

    用于实现 continue 语句的控制流。
    当执行 continue 语句时抛出此异常,由最内层循环捕获。

    用法:
        在 _execute_continue() 中抛出，在 _execute_while_loop() 中捕获。
    """
    pass


class EarlyExitException(Exception):
    """
    提前退出异常 (v4.0)

    用于实现 exit 语句的控制流。
    当执行 exit 语句时抛出此异常，由 execute() 方法捕获并正常结束执行。

    与 ExecutionError 的区别：
        - ExecutionError: 表示执行错误，任务失败
        - EarlyExitException: 表示主动退出，可以是成功或失败

    Attributes:
        code: 退出码（0=成功，非0=失败）
        message: 退出消息

    用法:
        在 _execute_exit() 中抛出，在 execute() 中捕获。
    """
    def __init__(self, code: int = 0, message: Optional[str] = None):
        self.code = code
        self.message = message or f"Exit with code {code}"
        super().__init__(self.message)


class WhileLoopGuard:
    """
    While 循环保护机制 (v3.0)

    防止死循环的保护类，限制循环的最大迭代次数。

    特性:
    - 跟踪当前循环的迭代次数
    - 超过最大次数时抛出 ExecutionError
    - 可配置最大迭代次数（默认 10000）

    示例:
        guard = WhileLoopGuard(max_iterations=5000)
        while condition:
            guard.check(line=10)  # 每次迭代检查
            # ... 循环体

    Attributes:
        max_iterations: 最大允许的迭代次数
        count: 当前已执行的迭代次数
    """

    def __init__(self, max_iterations: int = 10000):
        """
        初始化循环保护器

        Args:
            max_iterations: 最大迭代次数（默认 10000）
                          可通过环境变量或配置覆盖
        """
        self.max_iterations = max_iterations
        self.count = 0

    def check(self, line: int):
        """
        检查是否超过最大迭代次数

        Args:
            line: 循环语句的行号（用于错误报告）

        Raises:
            ExecutionError: 超过最大迭代次数时抛出
        """
        self.count += 1
        if self.count > self.max_iterations:
            raise ExecutionError(
                line=line,
                statement="while loop",
                error_type=ExecutionError.INFINITE_LOOP_DETECTED,
                message=(
                    f"While 循环超过最大迭代次数 {self.max_iterations}，"
                    f"可能是死循环。\n"
                    f"提示：检查循环条件是否能够变为 False，"
                    f"或在循环内添加 break 语句。"
                )
            )

    def reset(self):
        """重置迭代计数器"""
        self.count = 0


class Interpreter:
    """DSL 解释器"""

    def __init__(self, context: 'ExecutionContext', introspection_callback: Optional[Dict[str, Any]] = None):
        """
        初始化解释器

        Args:
            context: 执行上下文（包含变量、page、日志等）
            introspection_callback: 自省回调字典，用于记录运行时信息
        """
        self.context = context
        self._stopped = False

        # v2.0 新增：符号表栈
        self.symbol_table = SymbolTableStack()

        # v2.0 新增：系统变量提供者
        self.system_variables = SystemVariables(
            context=context,
            config_vars=getattr(context, 'config_vars', {})
        )

        # v2.0 新增：表达式求值器
        self.expression_evaluator = ExpressionEvaluator(
            self.symbol_table,
            self.system_variables
        )
        # v4.3: 设置延迟绑定,让 evaluator 可以调用函数
        self.expression_evaluator.interpreter = self

        # v2.0 新增：自省回调（用于测试框架）
        self._introspection_callback = introspection_callback or {}
        self._scope_history = self._introspection_callback.get('scope_history', [])
        self._assertions = self._introspection_callback.get('assertions', [])
        self._current_line = 0

        # v4.3 新增：函数调用栈和 return 控制
        self._call_stack = []  # 函数调用栈（用于递归检测）
        self._return_value = None  # return 语句的返回值
        self._return_flag = False  # 是否执行了 return 语句

        # v5.0 新增：模块系统
        self.module_loader = ModuleLoader()  # 模块加载器
        self.is_library_file = False  # 是否是库文件
        self.library_exports = {}  # 库的导出成员（如果是库文件）
        self.library_name = None  # 库名称（如果是库文件）

    def _record_scope_change(self, action: str, scope_type: str, scope_name: str, line: int):
        """
        记录作用域变化（用于自省）

        Args:
            action: 'enter' 或 'exit'
            scope_type: 作用域类型（'step', 'if', 'elif', 'else', 'each', 'block'）
            scope_name: 作用域名称
            line: 行号
        """
        import time

        record = {
            'timestamp': time.time(),
            'action': action,
            'scope_type': scope_type,
            'scope_name': scope_name,
            'line': line,
            'current_depth': self.symbol_table.scope_depth()
        }

        self._scope_history.append(record)

        # 如果配置了回调，也存储到回调字典中
        if 'scope_history' in self._introspection_callback:
            self._introspection_callback['scope_history'].append(record)

    def _record_assertion(self, condition: str, passed: bool, line: int, message: Optional[str] = None):
        """
        记录断言信息（用于自省）

        Args:
            condition: 条件表达式字符串
            passed: 是否通过
            line: 行号
            message: 断言消息（可选）
        """
        import time

        record = {
            'timestamp': time.time(),
            'line': line,
            'condition': condition,
            'passed': passed,
            'message': message,
            'scope_depth': self.symbol_table.scope_depth(),
            'current_scope': self.symbol_table.current_scope().scope_name if self.symbol_table.current_scope() else 'global'
        }

        self._assertions.append(record)

        # 如果配置了回调，也存储到回调字典中
        if 'assertions' in self._introspection_callback:
            self._introspection_callback['assertions'].append(record)

    def _record_scope_change(self, action: str, scope_type: str, scope_name: str, line: int):
        """
        记录作用域变化（用于自省）

        Args:
            action: 'enter' 或 'exit'
            scope_type: 作用域类型（'step', 'if', 'elif', 'else', 'each', 'block'）
            scope_name: 作用域名称
            line: 行号
        """
        import time

        record = {
            'timestamp': time.time(),
            'action': action,
            'scope_type': scope_type,
            'scope_name': scope_name,
            'line': line,
            'current_depth': self.symbol_table.scope_depth()
        }

        self._scope_history.append(record)

        # 如果配置了回调，也存储到回调字典中
        if 'scope_history' in self._introspection_callback:
            self._introspection_callback['scope_history'].append(record)

    def _record_assertion(self, condition: str, passed: bool, line: int, message: Optional[str] = None):
        """
        记录断言信息（用于自省）

        Args:
            condition: 条件表达式字符串
            passed: 是否通过
            line: 行号
            message: 断言消息（可选）
        """
        import time

        record = {
            'timestamp': time.time(),
            'line': line,
            'condition': condition,
            'passed': passed,
            'message': message,
            'scope_depth': self.symbol_table.scope_depth(),
            'current_scope': self.symbol_table.current_scope().scope_name if self.symbol_table.current_scope() else 'global'
        }

        self._assertions.append(record)

        # 如果配置了回调，也存储到回调字典中
        if 'assertions' in self._introspection_callback:
            self._introspection_callback['assertions'].append(record)

    def execute(self, program: Program) -> None:
        """
        执行 AST 程序

        Args:
            program: AST 根节点
        """
        self.context.logger.info(f"开始执行 DSL 脚本 ({len(program.statements)} 条语句)")

        # 设置状态为 RUNNING
        self.context.status = ExecutionStatus.RUNNING

        # v2.0: 使用 SymbolTableStack 初始化时创建的全局作用域
        # 不再调用 enter_scope("global")，避免双重创建

        try:
            for statement in program.statements:
                if self._stopped:
                    self.context.logger.info("执行已停止")
                    self.context.status = ExecutionStatus.CANCELLED
                    break

                self._execute_statement(statement)

            # 如果没有被取消，标记为完成
            if self.context.status == ExecutionStatus.RUNNING:
                self.context.status = ExecutionStatus.COMPLETED

            self.context.logger.info("DSL 脚本执行完成")

        except EarlyExitException as e:
            # 提前退出（不是错误）
            if e.code == 0:
                # 成功退出
                self.context.status = ExecutionStatus.COMPLETED
                self.context.logger.info(f"任务提前退出（成功）: {e.message}")
            else:
                # 失败退出
                self.context.status = ExecutionStatus.FAILED
                self.context.logger.warning(f"任务提前退出（失败）: {e.message}")
            # 不再向上抛出，任务正常结束

        except ExecutionError:
            self.context.status = ExecutionStatus.FAILED
            raise
        except Exception as e:
            self.context.status = ExecutionStatus.FAILED
            raise ExecutionError(
                line=0,
                statement="program",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"执行失败: {e}"
            )
        # 注意: 不要在 finally 中退出全局作用域
        # 因为测试可能需要在执行后访问全局变量

    def stop(self) -> None:
        """停止执行"""
        self._stopped = True
        self.context.logger.info("收到停止信号")

    def _resolve_string_with_variables(self, text: str) -> str:
        """
        解析字符串中的变量引用和表达式 (v2.0)

        支持格式:
        - {variable_name} - 变量引用，从符号表查找
        - {$page.url} - 系统变量引用
        - {x + 3} - 表达式求值
        - 普通字符串 - 直接返回

        Args:
            text: 包含变量引用或表达式的字符串

        Returns:
            解析后的字符串

        Raises:
            RuntimeError: 如果变量未定义或表达式求值失败
        """
        import re

        # 匹配 {任意内容}，允许嵌套大括号
        pattern = r'\{([^}]+)\}'

        def replacer(match):
            expr_text = match.group(1).strip()

            # 处理空表达式
            if not expr_text:
                # 空表达式返回空字符串
                return ""

            # 尝试解析并求值表达式
            try:
                # 简单变量引用（优化路径）
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', expr_text):
                    value = self.symbol_table.get(expr_text, line_number=0)
                    return str(value)

                # 系统变量引用（如 $page.url）
                elif expr_text.startswith('$'):
                    value = self.system_vars.get_system_variable(expr_text)
                    return str(value)

                # 表达式（如 x + 3, user.age >= 18）
                else:
                    # 使用 ExpressionEvaluator 解析和求值表达式
                    # 这需要重新词法分析和解析表达式字符串
                    from .lexer import Lexer
                    from .parser import Parser

                    # 创建临时 lexer 和 parser 解析表达式
                    temp_lexer = Lexer()
                    tokens = temp_lexer.tokenize(expr_text)

                    temp_parser = Parser()
                    # 解析为表达式节点
                    expr_node = temp_parser._parse_expression()

                    # 使用表达式求值器求值
                    value = self.expr_evaluator.evaluate(expr_node)
                    return str(value)

            except Exception as e:
                raise RuntimeError(
                    f"字符串插值失败 '{{{expr_text}}}': {e}"
                )

        # 替换所有变量引用和表达式
        resolved = re.sub(pattern, replacer, text)

        return resolved

    def _execute_statement(self, statement: ASTNode) -> None:
        """
        执行单个语句

        Args:
            statement: AST 语句节点
        """
        # v5.0 模块系统语句
        if isinstance(statement, LibraryDeclaration):
            self._execute_library_declaration(statement)
            return

        elif isinstance(statement, ExportStatement):
            self._execute_export_statement(statement)
            return

        elif isinstance(statement, ImportStatement):
            self._execute_import_statement(statement)
            return

        # 导航语句
        if isinstance(statement, NavigateToStatement):
            # v3.0: URL 是表达式，需要先求值
            # 支持：字符串字面量、变量引用、f-string等
            url_value = self.expression_evaluator.evaluate(statement.url)
            resolved_url = str(url_value)  # 确保是字符串类型

            execute_navigate_to(
                url=resolved_url,
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, GoBackStatement):
            execute_go_back(
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, GoForwardStatement):
            execute_go_forward(
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, ReloadStatement):
            execute_reload(
                context=self.context,
                line=statement.line
            )

        # 等待语句
        elif isinstance(statement, WaitDurationStatement):
            execute_wait_duration(
                duration=statement.duration,
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, WaitForStateStatement):
            execute_wait_for_state(
                state=statement.state,
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, WaitForElementStatement):
            # v2.0: selector 可能是表达式，需要求值
            from .expression_evaluator import to_string

            # 如果是 Expression，求值并转换为字符串
            if isinstance(statement.selector, Expression):
                selector_value = self.expression_evaluator.evaluate(statement.selector)
                resolved_selector = to_string(selector_value)
            else:
                # 向后兼容：如果是字符串字面量，直接使用
                resolved_selector = statement.selector

            execute_wait_for_element(
                selector=resolved_selector,
                state=statement.state,
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, WaitForNavigationStatement):
            execute_wait_for_navigation(
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, WaitUntilStatement):
            # v2.0: 支持表达式条件或旧式条件
            if isinstance(statement.condition, Expression):
                # 新式表达式条件
                from .actions.wait import execute_wait_until_expression
                execute_wait_until_expression(
                    condition=statement.condition,
                    evaluator=self.expression_evaluator,
                    context=self.context,
                    line=statement.line
                )
            else:
                # 旧式条件（向后兼容）
                execute_wait_until(
                    condition=statement.condition,
                    context=self.context,
                    line=statement.line
                )

        # 选择语句
        elif isinstance(statement, SelectStatement):
            # v3.0: 解析条件中的变量引用（支持 operator）
            # conditions 格式：[(attr, operator, value), ...]
            resolved_conditions = [
                (attr, operator, self._resolve_string_with_variables(value))
                for attr, operator, value in statement.conditions
            ]
            execute_select(
                element_type=statement.element_type,
                conditions=resolved_conditions,
                context=self.context,
                line=statement.line
            )

        # 交互动作
        elif isinstance(statement, TypeAction):
            # v2.0: text 现在是表达式,需要求值后转为字符串
            from .expression_evaluator import to_string

            # 求值表达式
            text_value = self.expression_evaluator.evaluate(statement.text)
            # 转换为字符串
            resolved_text = to_string(text_value)

            execute_type(
                text=resolved_text,
                mode=statement.mode,
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, ClickAction):
            execute_click(
                click_type=statement.click_type,
                wait_duration=statement.wait_duration,
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, HoverAction):
            execute_hover(
                selector=statement.selector,
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, ClearAction):
            execute_clear(
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, PressAction):
            execute_press(
                key_name=statement.key_name,
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, ScrollAction):
            execute_scroll(
                target=statement.target,
                selector=statement.selector,
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, CheckAction):
            execute_check(
                action=statement.action,
                selector=statement.selector,
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, UploadAction):
            execute_upload(
                file_path=statement.file_path,
                selector=statement.selector,
                context=self.context,
                line=statement.line
            )

        elif isinstance(statement, SelectOptionAction):
            # v2.0: option_value 和 selector 可能是表达式，需要求值
            from .expression_evaluator import to_string

            # 求值 option_value
            if isinstance(statement.option_value, Expression):
                option_value_result = self.expression_evaluator.evaluate(statement.option_value)
                resolved_option_value = to_string(option_value_result)
            else:
                resolved_option_value = statement.option_value

            # 求值 selector
            if isinstance(statement.selector, Expression):
                selector_result = self.expression_evaluator.evaluate(statement.selector)
                resolved_selector = to_string(selector_result)
            else:
                resolved_selector = statement.selector

            execute_select_option(
                option_value=resolved_option_value,
                selector=resolved_selector,
                context=self.context,
                line=statement.line
            )

        # 断言语句
        elif isinstance(statement, AssertStatement):
            self._execute_assert(statement)

        # 退出语句 (v4.1)
        elif isinstance(statement, ExitStatement):
            self._execute_exit(statement)

        # 资源定义 (v4.2)
        elif isinstance(statement, ResourceStatement):
            self._execute_resource(statement)

        # 截图语句
        elif isinstance(statement, ScreenshotStatement):
            # v2.0: name 和 selector 可能是表达式，需要求值
            from .expression_evaluator import to_string

            # 求值 name（如果存在）
            resolved_name = None
            if statement.name is not None:
                if isinstance(statement.name, Expression):
                    name_result = self.expression_evaluator.evaluate(statement.name)
                    resolved_name = to_string(name_result)
                else:
                    resolved_name = statement.name

            # 求值 selector（如果存在）
            resolved_selector = None
            if statement.selector is not None:
                if isinstance(statement.selector, Expression):
                    selector_result = self.expression_evaluator.evaluate(statement.selector)
                    resolved_selector = to_string(selector_result)
                else:
                    resolved_selector = statement.selector

            # v2.0: 支持元素截图（screenshot of "selector"）
            if resolved_selector:
                # 元素截图
                from .actions.screenshot import execute_screenshot_element
                execute_screenshot_element(
                    selector=resolved_selector,
                    name=resolved_name,
                    context=self.context,
                    line=statement.line
                )
            else:
                # 全屏或全页面截图
                execute_screenshot(
                    name=resolved_name,
                    fullpage=statement.fullpage,
                    context=self.context,
                    line=statement.line
                )

        # Step 块
        elif isinstance(statement, StepBlock):
            self._execute_step(statement)

        # If 块
        elif isinstance(statement, IfBlock):
            self._execute_if(statement)

        # When 块
        elif isinstance(statement, WhenBlock):
            self._execute_when(statement)

        # 变量设置
        elif isinstance(statement, SetVariableStatement):
            self._execute_set_variable(statement)

        # 数据提取
        elif isinstance(statement, ExtractStatement):
            self._execute_extract(statement)


        # 日志
        elif isinstance(statement, LogStatement):
            self._execute_log(statement)

        # v2.0 新增: 变量定义和赋值
        elif isinstance(statement, LetStatement):
            self._execute_let_statement(statement)

        elif isinstance(statement, ConstStatement):
            self._execute_const_statement(statement)

        elif isinstance(statement, Assignment):
            self._execute_assignment(statement)

        # v2.0 新增: 循环语句
        elif isinstance(statement, EachLoop):
            self._execute_each_loop(statement)

        # v3.0 While 循环语句
        elif isinstance(statement, WhileLoop):
            self._execute_while_loop(statement)

        elif isinstance(statement, BreakStatement):
            self._execute_break(statement)

        elif isinstance(statement, ContinueStatement):
            self._execute_continue(statement)

        # v4.3 函数定义和返回
        elif isinstance(statement, FunctionDefNode):
            self._execute_function_def(statement)

        elif isinstance(statement, ReturnNode):
            self._execute_return(statement)

        # v4.3 表达式语句（独立的函数调用等）
        elif isinstance(statement, ExpressionStatement):
            # 直接求值表达式（副作用会执行）
            self.expression_evaluator.evaluate(statement.expression)

        else:
            raise ExecutionError(
                line=getattr(statement, 'line', 0),
                statement=str(type(statement).__name__),
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"未知的语句类型: {type(statement).__name__}"
            )

    def _execute_assert(self, statement: AssertStatement) -> None:
        """
        执行断言语句 - v2.0 简化语法，v4.3 增强

        语法: assert expression [, message_expression]

        示例:
            assert x > 5
            assert user.age >= 18, "User must be adult"
            assert arr.length() > 0, "Array should not be empty"
            assert condition, error_msg  # v4.3: 支持变量和表达式
        """
        # 求值条件表达式
        result = self.expression_evaluator.evaluate(statement.condition)

        # 转换为布尔值
        from .expression_evaluator import to_boolean
        passed = to_boolean(result)

        # v4.3: 求值错误消息表达式
        error_message_str = None
        if statement.message:
            # 如果 message 是表达式，求值得到字符串
            if isinstance(statement.message, str):
                # 兼容：已经是字符串（来自旧版本或字符串字面量）
                error_message_str = statement.message
            else:
                # v4.3: 对表达式求值
                msg_value = self.expression_evaluator.evaluate(statement.message)
                error_message_str = str(msg_value) if msg_value is not None else ""

        # v2.0: 记录断言信息（用于自省）
        condition_str = str(statement.condition) if hasattr(statement.condition, '__str__') else "unknown"
        self._record_assertion(
            condition=condition_str,
            passed=passed,
            line=statement.line,
            message=error_message_str
        )

        # 如果断言失败，抛出错误
        if not passed:
            # 构建错误消息
            if error_message_str:
                error_message = error_message_str
            else:
                # 没有提供消息，生成默认消息
                error_message = f"断言失败: {condition_str}"

            # 记录断言失败
            self.context.add_execution_record(
                record_type="assertion_failed",
                content=error_message
            )

            # 抛出执行错误
            raise ExecutionError(
                line=statement.line,
                statement=f"assert",
                error_type=ExecutionError.ASSERTION_FAILED,
                message=error_message
            )

    def _execute_exit(self, statement: ExitStatement) -> None:
        """
        执行退出语句 - v4.0

        语法: exit [code] [, "message"]

        示例:
            exit                    # 退出，code=0
            exit 1                  # 退出，code=1
            exit "Failed"           # 退出，code=1，消息
            exit 0, "Success"       # 退出，code=0，消息
        """
        code = statement.code if statement.code is not None else 0
        message = statement.message or f"Exit with code {code}"

        # 记录退出信息
        self.context.logger.info(f"[EXIT] {message} (code={code})")
        self.context.add_execution_record(
            record_type="exit",
            content=message,
            success=(code == 0)
        )

        # 抛出提前退出异常
        raise EarlyExitException(code=code, message=message)

    def _execute_resource(self, statement: ResourceStatement) -> None:
        """
        执行 resource 语句 - v4.2

        加载 OpenAPI 规范文件并创建资源命名空间

        语法:
            resource <name> from <spec_file>
            或
            resource <name>:
                spec: <file>
                base_url: <url>
                auth: <expr>
                timeout: <int>
                headers: <dict>
            end resource

        示例:
            resource user_api from "openapi/user-service.yml"

            resource user_api:
                spec: "openapi/user-service.yml"
                base_url: "https://api.example.com"
                auth: bearer(token)
                timeout: 60
            end resource
        """
        from .openapi_loader import OpenAPISpec
        from .resource_namespace import ResourceNamespace

        # 1. 加载 OpenAPI 规范（v4.2.1: 支持智能路径查找）
        try:
            # 传递脚本路径以支持智能路径查找
            spec = OpenAPISpec(
                spec_file=statement.spec_file,
                script_path=self.context.script_path
            )
        except FileNotFoundError as e:
            raise ExecutionError(
                line=statement.line,
                statement=f"resource {statement.name} from \"{statement.spec_file}\"",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"OpenAPI 文件不存在: {statement.spec_file}"
            )
        except ValueError as e:
            raise ExecutionError(
                line=statement.line,
                statement=f"resource {statement.name} from \"{statement.spec_file}\"",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"OpenAPI 文件解析失败: {str(e)}"
            )
        except Exception as e:
            raise ExecutionError(
                line=statement.line,
                statement=f"resource {statement.name} from \"{statement.spec_file}\"",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"加载 OpenAPI 文件失败: {str(e)}"
            )

        # 2. 求值配置表达式
        base_url = None
        if statement.base_url:
            base_url_result = self.expression_evaluator.evaluate(statement.base_url)
            if not isinstance(base_url_result, str):
                raise ExecutionError(
                    line=statement.line,
                    statement=f"resource {statement.name}",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message=f"base_url 必须是字符串，得到: {type(base_url_result).__name__}"
                )
            base_url = base_url_result

        auth = None
        if statement.auth:
            auth = self.expression_evaluator.evaluate(statement.auth)
            if not isinstance(auth, dict):
                raise ExecutionError(
                    line=statement.line,
                    statement=f"resource {statement.name}",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message=f"auth 必须是字典，得到: {type(auth).__name__}"
                )

        headers = None
        if statement.headers:
            headers = self.expression_evaluator.evaluate(statement.headers)
            if not isinstance(headers, dict):
                raise ExecutionError(
                    line=statement.line,
                    statement=f"resource {statement.name}",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message=f"headers 必须是字典，得到: {type(headers).__name__}"
                )

        # 3. 创建资源命名空间
        try:
            resource_ns = ResourceNamespace(
                name=statement.name,
                spec=spec,
                base_url=base_url,
                auth=auth,
                timeout=statement.timeout,
                headers=headers,
                context=self.context
            )
        except Exception as e:
            raise ExecutionError(
                f"第 {statement.line} 行: 创建资源命名空间失败\n{str(e)}",
                statement.line
            )

        # 4. 注册到符号表（resource 定义为常量）
        from .symbol_table import SymbolType
        self.symbol_table.define(
            name=statement.name,
            value=resource_ns,
            symbol_type=SymbolType.CONSTANT,  # resource 定义为常量
            line_number=statement.line
        )

        # 5. 记录日志
        self.context.logger.info(
            f"[RESOURCE] 已加载资源 '{statement.name}' "
            f"({len(spec.operations)} 个操作): {statement.spec_file}"
        )

    def _execute_step(self, statement: StepBlock) -> None:
        """执行 Step 块"""
        import time

        step_name = statement.name
        self.context.current_step = step_name
        self.context.logger.info(f">>> 开始步骤: {step_name}")

        # v2.0: 进入步骤作用域
        self.symbol_table.enter_scope(f"step_{step_name}")

        # 记录作用域进入
        self._record_scope_change('enter', 'step', f"step_{step_name}", statement.line)

        # 记录步骤开始
        start_time = time.time()
        self.context.add_execution_record(
            record_type="step_start",
            content=step_name
        )

        success = True
        try:
            for stmt in statement.statements:
                if self._stopped:
                    success = False
                    break
                self._execute_statement(stmt)

            self.context.logger.info(f"<<< 步骤完成: {step_name}")

        except ExecutionError as e:
            success = False
            self.context.logger.error(f"<<< 步骤失败: {step_name}")
            raise

        finally:
            # 记录步骤结束（包含耗时和成功状态）
            end_time = time.time()
            duration = end_time - start_time

            self.context.add_execution_record(
                record_type="step_end",
                content=step_name,
                duration=duration,
                success=success
            )

            self.context.current_step = None

            # v2.0: 退出步骤作用域
            self.symbol_table.exit_scope()

            # 记录作用域退出
            self._record_scope_change('exit', 'step', f"step_{step_name}", statement.line)

    def _execute_if(self, statement: IfBlock) -> None:
        """
        执行 If 块（支持 else-if）

        v2.0 语义规范：每个分支创建独立作用域
        - if 分支有独立作用域
        - 每个 else-if 分支有独立作用域
        - else 分支有独立作用域
        """
        # v2.0: 求值 if 条件（不创建整体作用域）
        if isinstance(statement.condition, Expression):
            # 新的表达式求值
            condition_result = self.expression_evaluator.evaluate(statement.condition)
            from .expression_evaluator import to_boolean
            condition_met = to_boolean(condition_result)
        else:
            # 旧的条件检查 (向后兼容)
            condition_met = _check_condition(statement.condition, self.context)

        if condition_met:
            # 为 if 分支创建独立作用域
            self.symbol_table.enter_scope(f"if_then_line_{statement.line}")
            try:
                self.context.logger.info(f"If 条件满足，执行 then 分支")
                for stmt in statement.then_statements:
                    if self._stopped:
                        break
                    self._execute_statement(stmt)
            finally:
                self.symbol_table.exit_scope()
        else:
            # 评估 else-if 子句
            executed = False
            for index, (elif_condition, elif_statements) in enumerate(statement.elif_clauses):
                # 评估 else-if 条件
                if isinstance(elif_condition, Expression):
                    elif_result = self.expression_evaluator.evaluate(elif_condition)
                    from .expression_evaluator import to_boolean
                    elif_met = to_boolean(elif_result)
                else:
                    elif_met = _check_condition(elif_condition, self.context)

                if elif_met:
                    # 为每个 else-if 分支创建独立作用域
                    self.symbol_table.enter_scope(f"elif_{index}_line_{statement.line}")
                    try:
                        self.context.logger.info(f"Else-if 条件满足，执行 else-if 分支")
                        for stmt in elif_statements:
                            if self._stopped:
                                break
                            self._execute_statement(stmt)
                    finally:
                        self.symbol_table.exit_scope()
                    executed = True
                    break

            # 如果没有 else-if 执行，执行 else
            if not executed and statement.else_statements:
                # 为 else 分支创建独立作用域
                self.symbol_table.enter_scope(f"else_line_{statement.line}")
                try:
                    self.context.logger.info(f"所有条件不满足，执行 else 分支")
                    for stmt in statement.else_statements:
                        if self._stopped:
                            break
                        self._execute_statement(stmt)
                finally:
                    self.symbol_table.exit_scope()

    def _execute_when(self, statement: WhenBlock) -> None:
        """
        执行 When 块（v3.1: 支持 OR 模式）

        when value_expression:
            case_value1 | case_value2 | case_value3:
                ...
            otherwise:
                ...
        """
        # 求值要匹配的表达式
        match_value = self.evaluator.evaluate(statement.value_expression)

        # 遍历所有 when 子句
        for clause in statement.when_clauses:
            # 检查是否匹配任一 case 值（OR 模式）
            matched = False
            for case_value_expr in clause.case_values:
                case_value = self.evaluator.evaluate(case_value_expr)
                if match_value == case_value:
                    matched = True
                    break

            if matched:
                self.context.logger.info(f"When 条件匹配: {match_value}")
                # 执行匹配分支的语句
                for stmt in clause.statements:
                    if self._stopped:
                        break
                    self._execute_statement(stmt)
                return  # 只执行第一个匹配的分支

        # 没有匹配的 case，执行 otherwise 分支
        if statement.otherwise_statements:
            self.context.logger.info("执行 otherwise 分支")
            for stmt in statement.otherwise_statements:
                if self._stopped:
                    break
                self._execute_statement(stmt)
        else:
            self.context.logger.info("没有 When 条件匹配，且无 otherwise 分支")

    def _execute_set_variable(self, statement: SetVariableStatement) -> None:
        """执行变量设置"""
        # 解析值中的变量引用
        resolved_value = self.context.resolve_variables(statement.value)

        # 设置变量
        self.context.set_variable(statement.name, resolved_value)

        self.context.add_execution_record(
            record_type="set",
            content=f"set {statement.name} = {resolved_value}",
            success=True
        )

        self.context.logger.info(f"✓ 设置变量: {statement.name} = {resolved_value}")

    def _execute_extract(self, statement: ExtractStatement) -> None:
        """执行数据提取"""
        page = self.context.get_page()

        try:
            resolved_selector = self.context.resolve_variables(statement.selector)
            element = page.locator(resolved_selector).first

            # 根据提取类型获取值
            if statement.extract_type == "text":
                value = element.text_content() or ""
            elif statement.extract_type == "value":
                value = element.input_value()
            elif statement.extract_type == "attribute":
                value = element.get_attribute(statement.attribute_name) or ""
            elif statement.extract_type == "href":
                value = element.get_attribute("href") or ""
            else:
                value = element.text_content() or ""

            # 存储到变量
            self.context.set_variable(statement.variable_name, value)

            self.context.add_execution_record(
                record_type="extract",
                content=f"extract {statement.extract_type} from {resolved_selector} -> {statement.variable_name}",
                success=True
            )

            self.context.logger.info(
                f"✓ 提取数据: {statement.variable_name} = {value[:50]}{'...' if len(value) > 50 else ''}"
            )

        except Exception as e:
            raise ExecutionError(
                line=statement.line,
                statement=f"extract {statement.extract_type}",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"提取数据失败: {e}"
            )

    def _execute_log(self, statement: LogStatement) -> None:
        """
        执行日志输出 - v4.3+ 支持日志级别

        支持的级别：
        - debug: 调试信息（灰色 🔍）
        - info: 普通信息（默认）
        - success: 成功消息（绿色 ✓）
        - warning: 警告消息（黄色 ⚠）
        - error: 错误消息（红色 ✗）
        """
        # 日志级别图标映射 (v4.3+)
        LOG_ICONS = {
            'debug': '🔍',
            'info': '',
            'success': '✓',
            'warning': '⚠',
            'error': '✗'
        }

        # v2.0: 支持 Expression 或旧的字符串
        if isinstance(statement.message, Expression):
            # 新的表达式求值
            message_value = self.expression_evaluator.evaluate(statement.message)
            resolved_message = str(message_value)
        else:
            # 旧的变量解析 (向后兼容)
            resolved_message = self.context.resolve_variables(statement.message)

        # v4.3+: 添加级别图标前缀
        icon = LOG_ICONS.get(statement.level, '')
        formatted_message = f"{icon} {resolved_message}" if icon else resolved_message

        # 根据级别输出日志
        level_map = {
            'debug': self.context.logger.debug,
            'info': self.context.logger.info,
            'success': self.context.logger.info,  # success 使用 info 级别但带 ✓ 图标
            'warning': self.context.logger.warning,
            'error': self.context.logger.error
        }

        log_func = level_map.get(statement.level, self.context.logger.info)
        log_func(f"[LOG] {formatted_message}")

        self.context.add_execution_record(
            record_type=f"log_{statement.level}",
            content=f"log {statement.level} {resolved_message}",
            success=True
        )


    # ============================================================
    # v2.0 新增执行方法
    # ============================================================

    def _execute_let_statement(self, statement: LetStatement) -> None:
        """执行 let 语句"""
        # 求值表达式
        value = self.expression_evaluator.evaluate(statement.value)

        # 定义变量
        self.symbol_table.define(
            name=statement.name,
            value=value,
            symbol_type=SymbolType.VARIABLE,
            line_number=statement.line
        )

        self.context.logger.info(f"[OK] 定义变量: let {statement.name} = {value}")

    def _execute_const_statement(self, statement: ConstStatement) -> None:
        """执行 const 语句"""
        # 求值表达式
        value = self.expression_evaluator.evaluate(statement.value)

        # 定义常量
        self.symbol_table.define(
            name=statement.name,
            value=value,
            symbol_type=SymbolType.CONSTANT,
            line_number=statement.line
        )

        self.context.logger.info(f"[OK] 定义常量: const {statement.name} = {value}")

    def _execute_assignment(self, statement: Assignment) -> None:
        """执行赋值语句"""
        # 求值表达式
        value = self.expression_evaluator.evaluate(statement.value)

        # 更新变量
        self.symbol_table.set(
            name=statement.name,
            value=value,
            line_number=statement.line
        )

        self.context.logger.info(f"[OK] 赋值: {statement.name} = {value}")

    def _execute_each_loop(self, statement: EachLoop) -> None:
        """
        执行 for 循环

        语义规范：每次迭代创建独立作用域
        - 每次迭代都创建新作用域
        - 循环变量在每次迭代的作用域中定义
        - 迭代结束后销毁作用域
        - v3.0+: 支持 break/continue（与 while 一致）
        - v4.0: 支持多变量元组解包（for a, b in ...）
        """
        # 求值可迭代对象
        iterable = self.expression_evaluator.evaluate(statement.iterable)

        # 确保是可迭代对象
        if not isinstance(iterable, (list, tuple, str)):
            raise ExecutionError(
                line=statement.line,
                statement=f"for {', '.join(statement.variable_names)} in ...",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"无法迭代类型 {type(iterable).__name__}"
            )

        # 获取变量数量
        var_count = len(statement.variable_names)
        is_multi_var = var_count > 1

        self.context.logger.info(
            f"开始 for 循环: {', '.join(statement.variable_names)} in {type(iterable).__name__} (长度 {len(iterable)})"
        )

        # 不为整个循环创建作用域，为每次迭代创建作用域
        for index, item in enumerate(iterable):
            if self._stopped:
                break

            # 为每次迭代创建独立作用域
            self.symbol_table.enter_scope(f"for_iter_{index}_line_{statement.line}")

            # 跟踪作用域是否已退出（与 while 一致）
            scope_exited = False

            try:
                # v4.0: 支持多变量元组解包
                if is_multi_var:
                    # 多变量：解包 item
                    if not isinstance(item, (list, tuple)):
                        raise ExecutionError(
                            line=statement.line,
                            statement=f"for {', '.join(statement.variable_names)} in ...",
                            error_type=ExecutionError.RUNTIME_ERROR,
                            message=f"无法解包类型 {type(item).__name__}（期望 list 或 tuple）"
                        )

                    if len(item) != var_count:
                        raise ExecutionError(
                            line=statement.line,
                            statement=f"for {', '.join(statement.variable_names)} in ...",
                            error_type=ExecutionError.RUNTIME_ERROR,
                            message=f"解包值数量不匹配：需要 {var_count} 个值，得到 {len(item)} 个"
                        )

                    # 为每个变量定义值
                    for var_name, value in zip(statement.variable_names, item):
                        self.symbol_table.define(
                            name=var_name,
                            value=value,
                            symbol_type=SymbolType.VARIABLE,
                            line_number=statement.line
                        )

                    self.context.logger.debug(
                        f"  循环迭代 {index + 1}/{len(iterable)}: "
                        f"{', '.join(f'{name}={value}' for name, value in zip(statement.variable_names, item))}"
                    )
                else:
                    # 单变量：直接赋值
                    self.symbol_table.define(
                        name=statement.variable_names[0],
                        value=item,
                        symbol_type=SymbolType.VARIABLE,
                        line_number=statement.line
                    )

                    self.context.logger.debug(
                        f"  循环迭代 {index + 1}/{len(iterable)}: {statement.variable_names[0]} = {item}"
                    )

                # 执行循环体
                for stmt in statement.statements:
                    if self._stopped:
                        break
                    self._execute_statement(stmt)

            except BreakException:
                # Break: 先退出作用域，再退出循环（与 while 一致）
                self.symbol_table.exit_scope()
                scope_exited = True
                self.context.logger.debug(f"  遇到 break，退出循环（已迭代 {index + 1} 次）")
                break

            except ContinueException:
                # Continue: 跳过剩余语句，作用域在 finally 中清理（与 while 一致）
                self.context.logger.debug(f"  遇到 continue，跳过剩余语句")
                pass

            finally:
                # 每次迭代后销毁作用域（如果尚未退出）
                if not scope_exited:
                    self.symbol_table.exit_scope()

        self.context.logger.info(f"完成 for 循环")

    # ============================================================
    # v3.0 While 循环执行
    # ============================================================

    def _execute_while_loop(self, statement: WhileLoop) -> None:
        """
        执行 while 循环 (v3.0)

        v3.0 语义规范：每次迭代创建独立作用域（与 for/each 一致）
        - 条件驱动循环，每次迭代前求值条件
        - 每次迭代创建新作用域，迭代结束后销毁
        - 循环内可以使用 let 声明变量（每次迭代独立）
        - 支持 break/continue 控制流
        - 提供死循环保护机制

        示例:
            let count = 0
            while count < 5:
                let temp = count * 2  # ✅ 每次迭代创建新 temp
                log f"Count: {count}, Temp: {temp}"
                count = count + 1

        Args:
            statement: WhileLoop AST 节点
        """
        guard = WhileLoopGuard(max_iterations=10000)  # 可通过配置调整

        self.context.logger.info(f"开始 while 循环（行 {statement.line}）")

        iteration_count = 0
        while True:
            # 1. 检查死循环保护
            guard.check(statement.line)

            # 2. 检查停止标志
            if self._stopped:
                break

            # 3. 求值条件（在作用域外求值，确保可以访问外部变量）
            try:
                condition = self.expression_evaluator.evaluate(statement.condition)
            except Exception as e:
                raise ExecutionError(
                    line=statement.line,
                    statement=f"while {statement.condition}",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message=f"条件求值失败: {e}"
                )

            # 4. 验证条件类型
            if not isinstance(condition, bool):
                raise ExecutionError(
                    line=statement.line,
                    statement=f"while {statement.condition}",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message=f"while 条件必须是布尔值，实际类型: {type(condition).__name__}"
                )

            # 5. 条件为 False 则退出循环
            if not condition:
                self.context.logger.debug(f"  while 条件为 False，退出循环（共迭代 {iteration_count} 次）")
                break

            iteration_count += 1
            self.context.logger.debug(f"  while 迭代 #{iteration_count}: 条件为 True")

            # 6. 为每次迭代创建独立作用域（与 for/each 一致）
            self.symbol_table.enter_scope(f"while_iter_{iteration_count}_line_{statement.line}")

            # 7. 执行循环体
            scope_exited = False  # 跟踪作用域是否已退出
            try:
                for stmt in statement.statements:
                    if self._stopped:
                        break
                    self._execute_statement(stmt)

            except BreakException:
                # Break: 先退出作用域，再退出循环
                self.symbol_table.exit_scope()
                scope_exited = True
                self.context.logger.debug(f"  遇到 break，退出循环（共迭代 {iteration_count} 次）")
                break

            except ContinueException:
                # Continue: 跳过剩余语句，作用域在 finally 中清理
                self.context.logger.debug(f"  遇到 continue，跳过剩余语句")
                pass

            finally:
                # 8. 每次迭代后销毁作用域（如果尚未退出）
                if not scope_exited:
                    self.symbol_table.exit_scope()

        self.context.logger.info(f"完成 while 循环（共迭代 {iteration_count} 次）")


    def _execute_break(self, statement: BreakStatement) -> None:
        """
        执行 break 语句 (v3.0)

        抛出 BreakException，由最内层循环捕获。

        Args:
            statement: BreakStatement AST 节点
        """
        self.context.logger.debug(f"执行 break（行 {statement.line}）")
        raise BreakException()


    def _execute_continue(self, statement: ContinueStatement) -> None:
        """
        执行 continue 语句 (v3.0)

        抛出 ContinueException，由最内层循环捕获。

        Args:
            statement: ContinueStatement AST 节点
        """
        self.context.logger.debug(f"执行 continue（行 {statement.line}）")
        raise ContinueException()

    # ============================================================
    # v4.3 函数定义和返回语句执行
    # ============================================================

    def _execute_function_def(self, statement: FunctionDefNode) -> None:
        """
        执行函数定义语句 (v5.1 - 支持闭包)

        将函数注册到符号表中，以便后续调用

        Args:
            statement: FunctionDefNode AST 节点

        示例:
            function add(a, b):
                return a + b

        实现:
        - 创建 FunctionSymbol 并注册到当前作用域
        - 存储函数名、参数列表和函数体 AST
        - v5.1: 保存定义时的符号表引用（闭包）
        - 函数体在调用时才执行（延迟执行）
        """
        from .symbol_table import FunctionSymbol, SymbolType

        func_name = statement.name
        params = statement.params
        body = statement.body

        # 检查函数名是否已存在
        if self.symbol_table.exists_in_current_scope(func_name):
            raise ExecutionError(
                line=statement.line,
                statement=f"function {func_name}",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"函数 '{func_name}' 已定义"
            )

        # 创建函数符号（v5.1: 保存定义时的符号表作为闭包作用域）
        func_symbol = FunctionSymbol(
            name=func_name,
            value=None,  # 函数符号不存储值
            symbol_type=SymbolType.FUNCTION,
            line_number=statement.line,
            params=params,
            body=body,
            closure_scope=self.symbol_table.current_scope()  # v5.1: 闭包作用域
        )

        # 注册到符号表
        self.symbol_table.define(
            name=func_name,
            value=func_symbol,  # 存储整个 FunctionSymbol 对象
            symbol_type=SymbolType.FUNCTION,
            line_number=statement.line
        )

        self.context.logger.debug(
            f"定义函数 '{func_name}' (参数: {params}, "
            f"闭包作用域: {func_symbol.closure_scope.scope_name if func_symbol.closure_scope else 'None'}, "
            f"行 {statement.line})"
        )

    def _execute_return(self, statement: ReturnNode) -> None:
        """
        执行 return 语句 (v4.3)

        从函数中返回值，通过抛出 ReturnException 实现控制流

        Args:
            statement: ReturnNode AST 节点

        示例:
            return a + b
            return True
            return

        验证:
        - 检查是否在函数内使用 (self._call_stack 非空)

        实现:
        - 设置返回值标志和返回值
        - 抛出 ReturnException 异常退出函数
        """
        # 验证 return 在函数内
        if not self._call_stack:
            raise ExecutionError(
                line=statement.line,
                statement="return",
                error_type=ExecutionError.RUNTIME_ERROR,
                message="return 语句只能在函数内使用"
            )

        # 求值返回表达式
        return_value = None
        if statement.value is not None:
            return_value = self.expression_evaluator.evaluate(statement.value)

        # 设置返回值和标志
        self._return_value = return_value
        self._return_flag = True

        self.context.logger.debug(
            f"执行 return（值: {return_value}, 行 {statement.line}）"
        )

        # 抛出 ReturnException 退出函数
        raise ReturnException(return_value)

    def call_function(self, func_name: str, args: list, line: int) -> Any:
        """
        调用用户定义的函数 (v5.1 - 支持闭包)

        Args:
            func_name: 函数名
            args: 实参列表（已求值）
            line: 调用行号

        Returns:
            函数返回值

        抛出:
            ExecutionError: 函数未定义、参数数量不匹配、递归调用等错误

        实现流程:
        1. 从符号表获取函数符号
        2. 检测递归调用（通过调用栈）
        3. v5.1: 如果有闭包，切换到闭包作用域
        4. 创建函数局部作用域（父作用域是闭包作用域）
        5. 绑定参数
        6. 执行函数体
        7. 捕获 ReturnException 获取返回值
        8. 清理作用域和调用栈
        9. v5.1: 恢复符号表
        """
        from .symbol_table import FunctionSymbol, SymbolType

        # 1. 获取函数符号
        try:
            # 先检查符号是否存在
            if not self.symbol_table.exists(func_name):
                raise KeyError(f"函数 '{func_name}' 未定义")

            # 获取符号（这会返回 Symbol 对象）
            # 使用当前作用域查找（会向上查找父作用域）
            current_table = self.symbol_table.current_scope()
            symbol = None
            while current_table and symbol is None:
                if func_name in current_table.symbols:
                    symbol = current_table.symbols[func_name]
                    break
                current_table = current_table.parent

            if symbol is None:
                raise KeyError(f"函数 '{func_name}' 未定义")

        except KeyError:
            raise ExecutionError(
                line=line,
                statement=f"{func_name}(...)",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"未定义的函数: '{func_name}'"
            )

        # 验证是函数类型并获取 FunctionSymbol
        if symbol.symbol_type != SymbolType.FUNCTION:
            raise ExecutionError(
                line=line,
                statement=f"{func_name}(...)",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"'{func_name}' 不是函数"
            )

        func_symbol: FunctionSymbol = symbol.value

        # 2. 检测递归调用
        if func_name in self._call_stack:
            raise ExecutionError(
                line=line,
                statement=f"{func_name}(...)",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"不支持递归调用: 函数 '{func_name}' 正在执行中"
            )

        # 3. 验证参数数量
        if len(args) != len(func_symbol.params):
            raise ExecutionError(
                line=line,
                statement=f"{func_name}(...)",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"函数 '{func_name}' 需要 {len(func_symbol.params)} 个参数，但提供了 {len(args)} 个"
            )

        # 4. 进入函数调用栈
        self._call_stack.append(func_name)

        try:
            # 5. v5.1: 创建函数局部作用域
            if func_symbol.closure_scope:
                # 使用闭包作用域作为父作用域
                self.symbol_table.enter_scope_with_parent(
                    f"function:{func_name}",
                    parent=func_symbol.closure_scope
                )
                self._record_scope_change('enter', 'function', func_name, line)
            else:
                # 后向兼容：没有闭包的函数使用当前作用域作为父
                self.symbol_table.enter_scope(f"function:{func_name}")
                self._record_scope_change('enter', 'function', func_name, line)

            try:
                # 6. 绑定参数到局部作用域
                for param_name, arg_value in zip(func_symbol.params, args):
                    self.symbol_table.define(
                        name=param_name,
                        value=arg_value,
                        symbol_type=SymbolType.VARIABLE,
                        line_number=line
                    )

                self.context.logger.debug(
                    f"调用函数 '{func_name}' (参数: {dict(zip(func_symbol.params, args))}, "
                    f"闭包: {func_symbol.closure_scope.scope_name if func_symbol.closure_scope else 'None'}, "
                    f"行 {line})"
                )

                # 7. 执行函数体
                self._return_value = None
                self._return_flag = False

                for stmt in func_symbol.body:
                    if self._stopped or self._return_flag:
                        break
                    self._execute_statement(stmt)

                # 8. 返回值（如果没有 return 语句，返回 None）
                return_value = self._return_value

                self.context.logger.debug(
                    f"函数 '{func_name}' 返回: {return_value}"
                )

                return return_value

            except ReturnException as e:
                # 捕获 return 语句抛出的异常
                return e.value

            finally:
                # 9. 清理作用域
                self.symbol_table.exit_scope()
                self._record_scope_change('exit', 'function', func_name, line)

                # 重置 return 标志
                self._return_flag = False
                self._return_value = None

        finally:
            # 10. 退出函数调用栈
            self._call_stack.pop()

    # ============================================================
    # v5.0 Module System 执行
    # ============================================================

    def _execute_library_declaration(self, statement: LibraryDeclaration) -> None:
        """
        执行 library 声明语句 (v5.0)

        标记当前文件为库文件，开启独立作用域模式

        语法:
            library NAME

        行为:
            1. 标记文件为库文件（self.is_library_file = True）
            2. 设置库名称（self.library_name = NAME）
            3. 验证库名称与文件名匹配（基于 context.script_path）

        限制:
            - 必须在文件首行（第一条可执行语句）
            - 一个文件只能有一个 library 声明
        """
        # 验证是否已声明过library
        if self.is_library_file:
            raise ExecutionError(
                line=statement.line,
                statement=f"library {statement.name}",
                error_type=ExecutionError.RUNTIME_ERROR,
                message="一个文件只能有一个 library 声明"
            )

        # 标记为库文件
        self.is_library_file = True
        self.library_name = statement.name

        # 验证库名称与文件名匹配
        if hasattr(self.context, 'script_path') and self.context.script_path:
            from pathlib import Path
            script_path = Path(self.context.script_path)

            if not self.module_loader.validate_library_name(statement.name, script_path):
                raise ExecutionError(
                    line=statement.line,
                    statement=f"library {statement.name}",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message=f"library 名称必须与文件名匹配: 期望 '{script_path.stem}'，得到 '{statement.name}'"
                )

        self.context.logger.debug(f"Library '{statement.name}' 声明成功（行 {statement.line}）")

    def _execute_export_statement(self, statement: ExportStatement) -> None:
        """
        执行 export 语句 (v5.0)

        将 const 或 function 添加到导出列表

        语法:
            export const NAME = value
            export function NAME(...): ...

        行为:
            1. 执行被导出的语句（const 或 function）
            2. 将成员添加到 self.library_exports
            3. 验证仅在库文件中使用

        限制:
            - 只能在 library 文件中使用
            - 只能导出 const 或 function
        """
        # 验证在库文件中使用
        if not self.is_library_file:
            raise ExecutionError(
                line=statement.line,
                statement="export ...",
                error_type=ExecutionError.RUNTIME_ERROR,
                message="export 语句只能在 library 文件中使用（需要先声明 library）"
            )

        # 执行被导出的语句
        self._execute_statement(statement.target)

        # 提取导出的名称和值
        if isinstance(statement.target, ConstStatement):
            export_name = statement.target.name
            export_value = self.symbol_table.get(export_name, statement.target.line)
        elif isinstance(statement.target, FunctionDefNode):
            export_name = statement.target.name
            export_value = self.symbol_table.get(export_name, statement.target.line)
        else:
            raise ExecutionError(
                line=statement.line,
                statement="export ...",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"export 只能用于 const 或 function，得到: {type(statement.target).__name__}"
            )

        # 添加到导出列表
        self.library_exports[export_name] = export_value

        self.context.logger.debug(
            f"导出成员 '{export_name}' 从 library '{self.library_name}'（行 {statement.line}）"
        )

    def _execute_import_statement(self, statement: ImportStatement) -> None:
        """
        执行 import 语句 (v5.0)

        从其他库导入导出的成员

        语法 1 (模块导入):
            import ALIAS from "PATH"
            -> 将整个模块作为命名空间对象导入

        语法 2 (From-Import):
            from "PATH" import NAME1, NAME2, ...
            -> 导入特定成员到当前作用域

        行为:
            1. 解析模块路径（相对于当前文件）
            2. 加载模块（使用 ModuleLoader）
            3. 检测循环导入
            4. 将导入的成员添加到符号表

        限制:
            - 只支持相对路径
            - 完全禁止循环导入
        """
        from pathlib import Path

        # 获取当前文件路径
        current_file = Path(self.context.script_path) if (hasattr(self.context, 'script_path') and self.context.script_path) else Path.cwd()

        # 解析模块路径
        try:
            resolved_path = self.module_loader.resolve_path(statement.module_path, current_file)
        except ValueError as e:
            raise ExecutionError(
                line=statement.line,
                statement=f"import ... from \"{statement.module_path}\"",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=str(e)
            )

        # 检查循环导入
        if self.module_loader.check_circular_import(resolved_path):
            import_chain = self.module_loader.get_import_chain()
            chain_str = " -> ".join(import_chain + [resolved_path.name])
            raise ExecutionError(
                line=statement.line,
                statement=f"import ... from \"{statement.module_path}\"",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"检测到循环导入: {chain_str}"
            )

        # 加载模块（如果未缓存）
        module_info = self._load_module(resolved_path)

        # 语法 1: import ALIAS from "PATH" - 模块导入
        if statement.module_alias:
            # 创建模块命名空间对象
            # 使用简单类来存储导出的成员
            class ModuleNamespace:
                pass

            module_namespace = ModuleNamespace()
            # 将导出的成员设置为命名空间的属性
            for member_name, member_value in module_info.exports.items():
                setattr(module_namespace, member_name, member_value)

            # 将模块添加到符号表
            self.symbol_table.define(
                name=statement.module_alias,
                value=module_namespace,
                symbol_type=SymbolType.VARIABLE,
                line_number=statement.line
            )

            self.context.logger.debug(
                f"导入模块 '{statement.module_alias}' 从 {statement.module_path}（行 {statement.line}）"
            )

        # 语法 2: from "PATH" import NAME1, NAME2, ... - 成员导入
        elif statement.members:
            for member_name in statement.members:
                # 验证成员是否存在
                if member_name not in module_info.exports:
                    available = ", ".join(module_info.exports.keys())
                    raise ExecutionError(
                        line=statement.line,
                        statement=f"from \"{statement.module_path}\" import {member_name}",
                        error_type=ExecutionError.RUNTIME_ERROR,
                        message=f"模块 '{module_info.library_name}' 没有导出成员 '{member_name}'。可用成员: {available}"
                    )

                # 获取导出成员的值
                member_value = module_info.exports[member_name]

                # v5.0: 根据成员类型确定 symbol_type
                if isinstance(member_value, FunctionSymbol):
                    member_symbol_type = SymbolType.FUNCTION
                else:
                    member_symbol_type = SymbolType.VARIABLE

                # 将成员添加到当前作用域
                self.symbol_table.define(
                    name=member_name,
                    value=member_value,
                    symbol_type=member_symbol_type,
                    line_number=statement.line
                )

            members_str = ", ".join(statement.members)
            self.context.logger.debug(
                f"导入成员 [{members_str}] 从 {statement.module_path}（行 {statement.line}）"
            )

    def _load_module(self, module_path: Path) -> ModuleInfo:
        """
        加载模块（内部辅助方法）

        处理模块的实际加载逻辑：
        1. 检查缓存
        2. 读取文件
        3. 词法分析和语法分析
        4. 执行模块（使用新的 Interpreter 实例）
        5. 提取导出成员
        6. 缓存结果

        Args:
            module_path: 模块的绝对路径

        Returns:
            ModuleInfo 对象

        Raises:
            ExecutionError: 文件不存在、解析错误、执行错误等
        """
        # 1. 检查缓存
        if self.module_loader.is_cached(module_path):
            return self.module_loader.get_cached(module_path)

        # 2. 进入模块加载（用于循环导入检测）
        self.module_loader.enter_module(module_path)

        try:
            # 3. 读取文件
            if not module_path.exists():
                raise ExecutionError(
                    line=0,
                    statement=f"import from \"{module_path}\"",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message=f"模块文件不存在: {module_path}"
                )

            with open(module_path, 'r', encoding='utf-8') as f:
                module_source = f.read()

            # 4. 词法分析
            from .lexer import Lexer
            lexer = Lexer()
            tokens = lexer.tokenize(module_source)

            # 5. 语法分析
            from .parser import Parser
            parser = Parser()
            ast = parser.parse(tokens)

            # 6. 执行模块（创建独立的 Interpreter 实例）
            # 使用与主 Interpreter 相同的 context，但独立的符号表
            module_context = self.context  # 共享执行上下文

            # 创建新的 Interpreter 实例来执行模块
            module_interpreter = Interpreter(module_context)

            # v5.0: 共享 module_loader 以正确检测循环导入
            module_interpreter.module_loader = self.module_loader

            # 设置脚本路径为模块路径（用于相对导入）
            original_script_path = module_context.script_path
            module_context.script_path = str(module_path)

            try:
                # 执行模块
                module_interpreter.execute(ast)

                # 7. 验证是否是库文件
                if not module_interpreter.is_library_file:
                    raise ExecutionError(
                        line=0,
                        statement=f"import from \"{module_path}\"",
                        error_type=ExecutionError.RUNTIME_ERROR,
                        message=f"导入的文件必须是 library 文件（需要 library 声明）: {module_path.name}"
                    )

                # 8. 提取导出成员
                library_name = module_interpreter.library_name
                exports = module_interpreter.library_exports.copy()

                # 9. 创建 ModuleInfo
                module_info = ModuleInfo(
                    path=module_path,
                    library_name=library_name,
                    exports=exports,
                    ast=ast
                )

                # 10. 缓存模块
                self.module_loader.cache_module(module_path, module_info)

                self.context.logger.info(
                    f"成功加载模块 '{library_name}' (导出 {len(exports)} 个成员)"
                )

                return module_info

            finally:
                # 恢复原始脚本路径
                module_context.script_path = original_script_path

        except Exception as e:
            # 如果是 ExecutionError，直接重新抛出
            if isinstance(e, ExecutionError):
                raise
            # 其他异常包装为 ExecutionError
            raise ExecutionError(
                line=0,
                statement=f"import from \"{module_path}\"",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"加载模块失败: {str(e)}"
            )

        finally:
            # 11. 退出模块加载
            self.module_loader.exit_module(module_path)


# ============================================================
# v4.3 Return 异常
# ============================================================



def interpret(program: Program, context: 'ExecutionContext') -> None:
    """
    便捷函数：执行 DSL 程序

    Args:
        program: AST 程序
        context: 执行上下文
    """
    interpreter = Interpreter(context)
    interpreter.execute(program)
