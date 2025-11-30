"""
表达式求值器 (Expression Evaluator) v2.0

负责对表达式 AST 节点进行求值，返回计算结果。

主要功能:
1. 类型转换（弱类型系统）
2. 运算符求值（算术、比较、逻辑）
3. 短路求值（AND, OR）
4. 变量查找（用户变量 + 系统变量）
5. 成员访问和数组访问

参考: flows/SEMANTICS.md 第 3 节 - 类型系统
"""

from typing import Any, Dict, Optional
from .ast_nodes import (
    Expression,
    BinaryOp,
    UnaryOp,
    Literal,
    Identifier,
    SystemVariable,
    MemberAccess,
    ArrayAccess,
    MethodCall,
    FunctionCall,  # v4.3
    ArrayLiteral,
    ObjectLiteral,
    StringInterpolation,
    InputExpression,  # v5.1
)
from .symbol_table import SymbolTableStack, FunctionSymbol
from .system_variables import SystemVariables
from .errors import ExecutionError
from .builtin_functions import (
    BUILTIN_NAMESPACES,
    BUILTIN_FUNCTIONS,
)


class ExpressionEvaluator:
    """
    表达式求值器

    负责对表达式 AST 进行求值
    """

    def __init__(
        self,
        symbol_table: SymbolTableStack,
        system_variables: SystemVariables
    ):
        """
        初始化求值器

        Args:
            symbol_table: 符号表栈（用于查找用户变量）
            system_variables: 系统变量提供者
        """
        self.symbol_table = symbol_table
        self.system_variables = system_variables
        self.interpreter = None  # v4.3: 延迟绑定,由 Interpreter 设置

    def evaluate(self, expr: Expression) -> Any:
        """
        对表达式进行求值

        Args:
            expr: 表达式节点

        Returns:
            求值结果

        Raises:
            ExecutionError: 求值错误
        """
        if isinstance(expr, Literal):
            return self._eval_literal(expr)

        elif isinstance(expr, Identifier):
            return self._eval_identifier(expr)

        elif isinstance(expr, SystemVariable):
            return self._eval_system_variable(expr)

        elif isinstance(expr, BinaryOp):
            return self._eval_binary_op(expr)

        elif isinstance(expr, UnaryOp):
            return self._eval_unary_op(expr)

        elif isinstance(expr, MemberAccess):
            return self._eval_member_access(expr)

        elif isinstance(expr, ArrayAccess):
            return self._eval_array_access(expr)

        elif isinstance(expr, MethodCall):
            return self._eval_method_call(expr)

        elif isinstance(expr, FunctionCall):
            return self._eval_function_call(expr)

        elif isinstance(expr, ArrayLiteral):
            return self._eval_array_literal(expr)

        elif isinstance(expr, ObjectLiteral):
            return self._eval_object_literal(expr)

        elif isinstance(expr, StringInterpolation):
            return self._eval_string_interpolation(expr)

        elif isinstance(expr, InputExpression):
            return self._eval_input(expr)

        else:
            raise ExecutionError(
                line=expr.line if hasattr(expr, 'line') else 0,
                statement=f"表达式求值",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"未知的表达式类型: {type(expr).__name__}"
            )

    # ============================================================
    # 基本表达式求值
    # ============================================================

    def _eval_literal(self, expr: Literal) -> Any:
        """求值字面量"""
        return expr.value

    def _eval_identifier(self, expr: Identifier) -> Any:
        """求值标识符（查找变量、内置函数和命名空间）"""
        # 首先检查内置命名空间 (Math, Date, JSON, UUID, Hash, Base64)
        if expr.name in BUILTIN_NAMESPACES:
            return BUILTIN_NAMESPACES[expr.name]

        # 然后检查全局内置函数 (Number, String, Boolean, isNaN, isFinite)
        if expr.name in BUILTIN_FUNCTIONS:
            return BUILTIN_FUNCTIONS[expr.name]

        # v3.0: 检查系统命名空间 (page, context, browser, env, config)
        from .system_namespaces import SYSTEM_NAMESPACES, SystemNamespaceProxy
        if expr.name in SYSTEM_NAMESPACES:
            return SystemNamespaceProxy(expr.name, self.system_variables)

        # 最后查找用户定义的变量
        try:
            return self.symbol_table.get(expr.name, expr.line)
        except Exception as e:
            raise ExecutionError(
                line=expr.line,
                statement=f"变量引用: {expr.name}",
                error_type=ExecutionError.VARIABLE_NOT_FOUND,
                message=f"变量 '{expr.name}' 未定义"
            )

    def _eval_system_variable(self, expr: SystemVariable) -> Any:
        """求值系统变量"""
        return self.system_variables.get(expr.path, expr.line)

    def _eval_member_access(self, expr: MemberAccess) -> Any:
        """求值成员访问 object.property"""
        obj = self.evaluate(expr.object)

        if obj is None:
            raise ExecutionError(
                line=expr.line,
                statement=f"成员访问: .{expr.property}",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"无法访问 null 对象的属性 '{expr.property}'"
            )

        if isinstance(obj, dict):
            if expr.property not in obj:
                raise ExecutionError(
                    line=expr.line,
                    statement=f"成员访问: .{expr.property}",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message=f"对象没有属性 '{expr.property}'"
                )
            return obj[expr.property]

        elif hasattr(obj, expr.property):
            return getattr(obj, expr.property)

        else:
            raise ExecutionError(
                line=expr.line,
                statement=f"成员访问: .{expr.property}",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"对象 {type(obj).__name__} 没有属性 '{expr.property}'"
            )

    def _eval_array_access(self, expr: ArrayAccess) -> Any:
        """求值数组访问 array[index]"""
        array = self.evaluate(expr.array)
        index = self.evaluate(expr.index)

        if array is None:
            raise ExecutionError(
                line=expr.line,
                statement=f"数组访问",
                error_type=ExecutionError.RUNTIME_ERROR,
                message="无法对 null 值进行数组访问"
            )

        # 索引必须是整数
        try:
            index_int = int(index)
        except (ValueError, TypeError):
            raise ExecutionError(
                line=expr.line,
                statement=f"数组访问",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"数组索引必须是整数，不能是 {type(index).__name__}"
            )

        # 检查索引范围
        if not isinstance(array, (list, tuple, str)):
            raise ExecutionError(
                line=expr.line,
                statement=f"数组访问",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"只能对数组/字符串进行索引访问，不能对 {type(array).__name__}"
            )

        if index_int < 0 or index_int >= len(array):
            raise ExecutionError(
                line=expr.line,
                statement=f"数组访问",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"数组索引越界: {index_int} (数组长度: {len(array)})"
            )

        return array[index_int]

    def _eval_method_call(self, expr: MethodCall) -> Any:
        """
        求值方法调用 object.method(args, kwargs) 或直接函数调用 func(args, kwargs)

        v3.2: 支持命名参数

        Args:
            expr: MethodCall 节点

        Returns:
            方法调用结果

        Raises:
            ExecutionError: 方法不存在或调用失败
        """
        # 处理直接函数调用 (object 为 None)
        if expr.object is None:
            # 查找全局内置函数
            if expr.method_name in BUILTIN_FUNCTIONS:
                func = BUILTIN_FUNCTIONS[expr.method_name]
                args = [self.evaluate(arg) for arg in expr.arguments]
                # v3.2: 求值命名参数
                kwargs = {key: self.evaluate(value) for key, value in expr.kwargs.items()}
                try:
                    # v6.0: 特殊处理 Resource() 函数，需要注入 context
                    if expr.method_name == 'Resource':
                        # Resource(spec_file, **kwargs) 需要 context 参数
                        # 从 system_variables 获取 context 并注入
                        context = self.system_variables.context
                        return func(*args, context=context, **kwargs)
                    else:
                        # 普通内置函数
                        return func(*args, **kwargs)
                except Exception as e:
                    raise ExecutionError(
                        line=expr.line,
                        statement=f"函数调用 {expr.method_name}",
                        error_type=ExecutionError.RUNTIME_ERROR,
                        message=f"调用内置函数失败: {e}"
                    )
            else:
                raise ExecutionError(
                    line=expr.line,
                    statement=f"函数调用 {expr.method_name}",
                    error_type=ExecutionError.VARIABLE_NOT_FOUND,
                    message=f"未定义的函数: {expr.method_name}"
                )

        # 求值对象
        obj = self.evaluate(expr.object)

        if obj is None:
            raise ExecutionError(
                line=expr.line,
                statement=f"方法调用 {expr.method_name}",
                error_type=ExecutionError.RUNTIME_ERROR,
                message="无法对 null 值调用方法"
            )

        # 求值位置参数
        args = [self.evaluate(arg) for arg in expr.arguments]

        # v3.2: 求值命名参数
        kwargs = {key: self.evaluate(value) for key, value in expr.kwargs.items()}

        # 尝试调用原生方法
        if hasattr(obj, expr.method_name):
            method = getattr(obj, expr.method_name)

            # v5.0: 检查是否是 FunctionSymbol（来自模块导入）
            if isinstance(method, FunctionSymbol):
                # 直接执行导入的函数（不在当前符号表中，无法使用 call_function）
                from .symbol_table import SymbolType
                from .errors import ReturnException

                func_symbol = method
                func_name = func_symbol.name

                # 1. 验证参数数量
                if len(args) != len(func_symbol.params):
                    raise ExecutionError(
                        line=expr.line,
                        statement=f"{func_name}(...)",
                        error_type=ExecutionError.RUNTIME_ERROR,
                        message=f"函数 '{func_name}' 需要 {len(func_symbol.params)} 个参数，但提供了 {len(args)} 个"
                    )

                # 2. 检测递归调用
                if func_name in self.interpreter._call_stack:
                    raise ExecutionError(
                        line=expr.line,
                        statement=f"{func_name}(...)",
                        error_type=ExecutionError.RUNTIME_ERROR,
                        message=f"不支持递归调用: 函数 '{func_name}' 正在执行中"
                    )

                # 3. 进入函数调用栈
                self.interpreter._call_stack.append(func_name)

                try:
                    # 4. v5.1: 创建函数局部作用域（支持闭包）
                    if func_symbol.closure_scope:
                        # 使用闭包作用域作为父作用域
                        self.interpreter.symbol_table.enter_scope_with_parent(
                            f"function:{func_name}",
                            parent=func_symbol.closure_scope
                        )
                    else:
                        # 后向兼容：没有闭包的函数使用当前作用域作为父
                        self.interpreter.symbol_table.enter_scope(f"function:{func_name}")

                    try:
                        # 5. 绑定参数到局部作用域
                        for param_name, arg_value in zip(func_symbol.params, args):
                            self.interpreter.symbol_table.define(
                                name=param_name,
                                value=arg_value,
                                symbol_type=SymbolType.VARIABLE,
                                line_number=expr.line
                            )

                        # 6. 执行函数体
                        self.interpreter._return_value = None
                        self.interpreter._return_flag = False

                        for stmt in func_symbol.body:
                            if self.interpreter._stopped or self.interpreter._return_flag:
                                break
                            self.interpreter._execute_statement(stmt)

                        # 7. 返回值（如果没有 return 语句，返回 None）
                        return self.interpreter._return_value

                    except ReturnException as e:
                        # 捕获 return 语句抛出的异常
                        return e.value

                    finally:
                        # 8. 清理作用域
                        self.interpreter.symbol_table.exit_scope()

                        # 重置 return 标志
                        self.interpreter._return_flag = False
                        self.interpreter._return_value = None

                finally:
                    # 9. 退出函数调用栈
                    self.interpreter._call_stack.pop()


            if callable(method):
                try:
                    return method(*args, **kwargs)
                except Exception as e:
                    raise ExecutionError(
                        line=expr.line,
                        statement=f"方法调用 {expr.method_name}",
                        error_type=ExecutionError.RUNTIME_ERROR,
                        message=f"调用方法失败: {e}"
                    )

        # 方法不存在
        obj_type = type(obj).__name__
        raise ExecutionError(
            line=expr.line,
            statement=f"方法调用 {expr.method_name}",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"对象类型 {obj_type} 没有方法 '{expr.method_name}'"
        )

    def _eval_function_call(self, expr: FunctionCall) -> Any:
        """
        求值函数调用 (v4.3)

        调用用户定义的函数或内置函数

        Args:
            expr: FunctionCall 节点

        Returns:
            函数返回值

        Raises:
            ExecutionError: 函数不存在或调用失败
        """
        func_name = expr.function_name

        # 1. 首先检查是否是内置函数
        if func_name in BUILTIN_FUNCTIONS:
            func = BUILTIN_FUNCTIONS[func_name]
            args = [self.evaluate(arg) for arg in expr.arguments]
            try:
                # v6.0: 特殊处理 Resource() 函数，需要注入 context
                if func_name == 'Resource':
                    # Resource(spec_file, **kwargs) 需要 context 参数
                    # 从 system_variables 获取 context 并作为关键字参数传递
                    context = self.system_variables.context
                    return func(*args, context=context)
                else:
                    # 普通内置函数
                    return func(*args)
            except Exception as e:
                raise ExecutionError(
                    line=expr.line,
                    statement=f"函数调用 {func_name}",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message=f"调用内置函数失败: {e}"
                )

        # 2. 然后检查是否是用户定义的函数
        if self.interpreter is None:
            raise ExecutionError(
                line=expr.line,
                statement=f"函数调用 {func_name}",
                error_type=ExecutionError.RUNTIME_ERROR,
                message="表达式求值器未正确初始化（缺少 interpreter 引用）"
            )

        # 求值参数
        args = [self.evaluate(arg) for arg in expr.arguments]

        # 调用用户定义的函数
        try:
            return self.interpreter.call_function(func_name, args, expr.line)
        except ExecutionError:
            # 重新抛出 ExecutionError
            raise
        except Exception as e:
            raise ExecutionError(
                line=expr.line,
                statement=f"函数调用 {func_name}",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"调用函数失败: {e}"
            )

    def _eval_array_literal(self, expr: ArrayLiteral) -> list:
        """
        求值数组字面量 [element1, element2, ...]

        Args:
            expr: ArrayLiteral 节点

        Returns:
            包含求值后元素的 Python list

        示例:
            [] -> []
            [1, 2, 3] -> [1, 2, 3]
            [x + 1, y * 2] -> [计算后的值1, 计算后的值2]
            [[1, 2], [3, 4]] -> [[1, 2], [3, 4]]
        """
        # 对每个元素表达式求值
        result = []
        for element_expr in expr.elements:
            element_value = self.evaluate(element_expr)
            result.append(element_value)

        return result

    def _eval_object_literal(self, expr: ObjectLiteral) -> dict:
        """
        求值对象字面量 {key1: value1, key2: value2, ...}

        Args:
            expr: ObjectLiteral 节点

        Returns:
            包含求值后键值对的 Python dict

        示例:
            {} -> {}
            {name: "Alice", age: 25} -> {"name": "Alice", "age": 25}
            {x: a + 1, y: b * 2} -> {"x": 计算后的值1, "y": 计算后的值2}
            {user: {name: "Bob"}} -> {"user": {"name": "Bob"}}
        """
        # 对每个键值对求值
        result = {}
        for key, value_expr in expr.pairs:
            value = self.evaluate(value_expr)
            result[key] = value

        return result

    def _eval_string_interpolation(self, expr: StringInterpolation) -> str:
        """求值字符串插值"""
        result = ""

        for part in expr.parts:
            if isinstance(part, str):
                result += part
            else:
                # 是表达式，求值后转为字符串
                value = self.evaluate(part)
                result += to_string(value)

        return result

    def _eval_input(self, expr: 'InputExpression') -> Any:
        """
        执行 input 表达式，从控制台读取用户输入 (v5.1)

        Args:
            expr: InputExpression 节点

        Returns:
            用户输入的值（根据 type 转换类型）

        Raises:
            ExecutionError: 输入错误、类型转换错误
        """
        # 1. 求值提示文本
        prompt_value = self.evaluate(expr.prompt)
        prompt = to_string(prompt_value)

        # 2. 求值默认值
        default = None
        if expr.default_value:
            default = self.evaluate(expr.default_value)

        # 3. 检查是否在交互模式（非交互模式下必须有默认值）
        # v5.1: 暂时假设总是交互模式，后续通过 context.is_interactive 判断
        is_interactive = True
        if self.interpreter and hasattr(self.interpreter, 'context'):
            is_interactive = getattr(self.interpreter.context, 'is_interactive', True)

        if not is_interactive:
            if default is not None:
                return default
            else:
                raise ExecutionError(
                    line=expr.line,
                    statement="input(...)",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message="input() 需要交互模式，但当前在自动模式。请提供 default 参数"
                )

        # 4. 构建完整提示文本
        if default is not None:
            full_prompt = f"{prompt} [默认: {default}] "
        else:
            full_prompt = prompt

        # 5. 从控制台读取输入（密码模式使用 getpass）
        try:
            if expr.input_type == "password":
                import getpass
                user_input = getpass.getpass(full_prompt)
            else:
                user_input = input(full_prompt)
        except (KeyboardInterrupt, EOFError) as e:
            # 用户中断输入
            raise ExecutionError(
                line=expr.line,
                statement="input(...)",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"用户中断输入: {type(e).__name__}"
            )

        # 6. 处理空输入（使用默认值）
        if user_input.strip() == "" and default is not None:
            return default

        # 7. 类型转换
        try:
            if expr.input_type == "integer":
                return int(user_input)
            elif expr.input_type == "float":
                return float(user_input)
            else:
                # text 或 password 类型直接返回字符串
                return user_input
        except ValueError as e:
            raise ExecutionError(
                line=expr.line,
                statement=f"input(..., type={expr.input_type})",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"无法将输入 '{user_input}' 转换为 {expr.input_type}: {e}"
            )

    # ============================================================
    # 二元运算求值
    # ============================================================

    def _eval_binary_op(self, expr: BinaryOp) -> Any:
        """
        求值二元运算（v4.0: 支持整数类型和类型提升）

        类型提升规则（Python风格）:
            - int OP int → int (除法 / 例外，总是返回float)
            - int OP float → float
            - float OP int → float
            - float OP float → float
        """
        operator = expr.operator

        # 短路求值：AND
        if operator == "AND":
            left = self.evaluate(expr.left)
            if not to_boolean(left):
                return False
            right = self.evaluate(expr.right)
            return to_boolean(right)

        # 短路求值：OR
        elif operator == "OR":
            left = self.evaluate(expr.left)
            if to_boolean(left):
                return True
            right = self.evaluate(expr.right)
            return to_boolean(right)

        # 其他运算符：先求值两边
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        # v4.0: 算术运算符（类型感知）
        if operator == "+":
            # 字符串拼接
            if isinstance(left, str) or isinstance(right, str):
                return to_string(left) + to_string(right)
            # 列表连接
            elif isinstance(left, list) and isinstance(right, list):
                return left + right
            # 数值相加
            else:
                # v4.0: 类型提升逻辑
                return self._arithmetic_add(left, right, expr.line)

        elif operator == "-":
            return self._arithmetic_subtract(left, right, expr.line)

        elif operator == "*":
            return self._arithmetic_multiply(left, right, expr.line)

        elif operator == "/":
            # v4.0: 除法总是返回 float（Python 3 风格）
            right_num = to_number(right, expr.line)
            if right_num == 0:
                raise ExecutionError(
                    line=expr.line,
                    statement=f"除法运算",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message="除数不能为零"
                )
            return to_number(left, expr.line) / right_num

        elif operator == "//":
            # v4.0: 整除运算符（返回整数）
            right_num = to_number(right, expr.line)
            if right_num == 0:
                raise ExecutionError(
                    line=expr.line,
                    statement=f"整除运算",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message="整除运算的除数不能为零"
                )
            return int(to_number(left, expr.line) // right_num)

        elif operator == "%":
            # v4.0: 模运算（类型保持）
            return self._arithmetic_modulo(left, right, expr.line)

        elif operator == "**":
            # v4.0: 幂运算（类型提升）
            return self._arithmetic_power(left, right, expr.line)

        # 比较运算符
        elif operator == ">":
            return to_number(left, expr.line) > to_number(right, expr.line)

        elif operator == "<":
            return to_number(left, expr.line) < to_number(right, expr.line)

        elif operator == ">=":
            return to_number(left, expr.line) >= to_number(right, expr.line)

        elif operator == "<=":
            return to_number(left, expr.line) <= to_number(right, expr.line)

        elif operator == "==" or operator == "equals":
            return left == right

        elif operator == "!=" or operator == "NEQ":
            return left != right

        # 字符串运算符
        elif operator == "contains":
            # 检查 left 是否包含 right（如: text contains "success"）
            return to_string(right) in to_string(left)

        elif operator == "matches":
            # 正则匹配
            import re
            try:
                pattern = to_string(right)
                text = to_string(left)
                return bool(re.search(pattern, text))
            except re.error as e:
                raise ExecutionError(
                    line=expr.line,
                    statement=f"正则匹配",
                    error_type=ExecutionError.RUNTIME_ERROR,
                    message=f"正则表达式错误: {e}"
                )

        else:
            raise ExecutionError(
                line=expr.line,
                statement=f"二元运算",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"未知的二元运算符: {operator}"
            )

    # ============================================================
    # 一元运算求值
    # ============================================================

    def _eval_unary_op(self, expr: UnaryOp) -> Any:
        """求值一元运算（v4.0: 保持类型）"""
        operand = self.evaluate(expr.operand)
        operator = expr.operator

        if operator == "+":
            # v4.0: 保持原类型（int或float）
            if isinstance(operand, (int, float)) and not isinstance(operand, bool):
                return operand
            return +to_number(operand, expr.line)

        elif operator == "-":
            # v4.0: 保持原类型（int或float）
            if isinstance(operand, int) and not isinstance(operand, bool):
                return -operand  # int → int
            if isinstance(operand, float):
                return -operand  # float → float
            return -to_number(operand, expr.line)

        elif operator == "NOT":
            return not to_boolean(operand)

        else:
            raise ExecutionError(
                line=expr.line,
                statement=f"一元运算",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"未知的一元运算符: {operator}"
            )

    # ============================================================
    # v4.0: 类型感知的算术运算辅助方法
    # ============================================================

    def _arithmetic_add(self, left: Any, right: Any, line: int) -> Any:
        """
        加法运算（类型提升）

        规则:
            - int + int → int
            - int + float → float
            - float + int → float
            - float + float → float
        """
        # 检查是否都是数值类型
        left_is_int = isinstance(left, int) and not isinstance(left, bool)
        left_is_float = isinstance(left, float)
        right_is_int = isinstance(right, int) and not isinstance(right, bool)
        right_is_float = isinstance(right, float)

        if left_is_int and right_is_int:
            return left + right  # int + int → int
        elif (left_is_int or left_is_float) and (right_is_int or right_is_float):
            # 至少有一个是float，提升为float
            return float(left) + float(right)
        else:
            # 回退到通用转换
            return to_number(left, line) + to_number(right, line)

    def _arithmetic_subtract(self, left: Any, right: Any, line: int) -> Any:
        """减法运算（类型提升）"""
        left_is_int = isinstance(left, int) and not isinstance(left, bool)
        left_is_float = isinstance(left, float)
        right_is_int = isinstance(right, int) and not isinstance(right, bool)
        right_is_float = isinstance(right, float)

        if left_is_int and right_is_int:
            return left - right  # int - int → int
        elif (left_is_int or left_is_float) and (right_is_int or right_is_float):
            return float(left) - float(right)
        else:
            return to_number(left, line) - to_number(right, line)

    def _arithmetic_multiply(self, left: Any, right: Any, line: int) -> Any:
        """乘法运算（类型提升）"""
        left_is_int = isinstance(left, int) and not isinstance(left, bool)
        left_is_float = isinstance(left, float)
        right_is_int = isinstance(right, int) and not isinstance(right, bool)
        right_is_float = isinstance(right, float)

        if left_is_int and right_is_int:
            return left * right  # int * int → int
        elif (left_is_int or left_is_float) and (right_is_int or right_is_float):
            return float(left) * float(right)
        else:
            return to_number(left, line) * to_number(right, line)

    def _arithmetic_modulo(self, left: Any, right: Any, line: int) -> Any:
        """
        模运算（类型保持）

        规则:
            - int % int → int
            - int % float → int
            - float % int → int
            - float % float → int
        """
        right_num = to_number(right, line)
        if right_num == 0:
            raise ExecutionError(
                line=line,
                statement=f"模运算",
                error_type=ExecutionError.RUNTIME_ERROR,
                message="模运算的除数不能为零"
            )

        left_num = to_number(left, line)
        # 模运算总是返回整数
        return int(left_num % right_num)

    def _arithmetic_power(self, left: Any, right: Any, line: int) -> Any:
        """
        幂运算（类型提升）

        规则:
            - int ** int → int (如果指数非负)
            - int ** int → float (如果指数为负)
            - int ** float → float
            - float ** int → float
            - float ** float → float
        """
        left_is_int = isinstance(left, int) and not isinstance(left, bool)
        left_is_float = isinstance(left, float)
        right_is_int = isinstance(right, int) and not isinstance(right, bool)
        right_is_float = isinstance(right, float)

        if left_is_int and right_is_int:
            if right >= 0:
                return left ** right  # int ** int (非负) → int
            else:
                return float(left) ** float(right)  # int ** int (负数) → float
        elif (left_is_int or left_is_float) and (right_is_int or right_is_float):
            return float(left) ** float(right)
        else:
            return to_number(left, line) ** to_number(right, line)


# ============================================================
# 类型转换函数（弱类型系统）
# ============================================================

def to_boolean(value: Any) -> bool:
    """
    转换为布尔值

    规则:
        null/None  -> False
        false      -> False
        0          -> False
        ""         -> False
        其他       -> True
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return len(value) > 0
    return True  # 其他对象认为是 true


def to_number(value: Any, line: int = 0) -> float:
    """
    转换为数字

    Args:
        value: 要转换的值
        line: 行号（用于错误报告）

    Returns:
        浮点数

    Raises:
        ExecutionError: 无法转换为数字
    """
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, bool):
        return 1.0 if value else 0.0

    if isinstance(value, str):
        # 尝试解析数字
        try:
            return float(value)
        except ValueError:
            raise ExecutionError(
                line=line,
                statement=f"类型转换",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"无法将字符串 '{value}' 转换为数字"
            )

    if value is None:
        raise ExecutionError(
            line=line,
            statement=f"类型转换",
            error_type=ExecutionError.RUNTIME_ERROR,
            message="无法将 null 转换为数字"
        )

    raise ExecutionError(
        line=line,
        statement=f"类型转换",
        error_type=ExecutionError.RUNTIME_ERROR,
        message=f"无法将类型 {type(value).__name__} 转换为数字"
    )


def to_string(value: Any) -> str:
    """
    转换为字符串（v4.0: 智能处理整数）

    规则:
        null/None  -> "null"
        true       -> "true"
        false      -> "false"
        整数       -> 不带小数点 ("5")
        浮点数     -> 带小数点 ("5.0", "3.14")
        其他       -> str(value)
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    # v4.0: 区分整数和浮点数
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)  # 整数：无小数点
    if isinstance(value, float):
        # 浮点数：保留小数点
        # 如果是整数值的浮点数（如 5.0），保留 .0
        if value == int(value):
            return f"{int(value)}.0"
        else:
            return str(value)
    return str(value)
