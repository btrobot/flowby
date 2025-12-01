"""
Grammar Alignment Test: While Loop (v3.0)

Tests alignment between grammar/MASTER.md definitions and parser.py implementation.

Features tested:
- 9.1 While Loop - v3.0
- 9.2 Break Statement - v3.0
- 9.3 Continue Statement - v3.0

Reference: grammar/MASTER.md #9-While Loop
"""

import pytest
from unittest.mock import Mock, patch
from registration_system.dsl.ast_nodes import (
    WhileLoop,
    BreakStatement,
    ContinueStatement,
    LetStatement,
    Assignment,
    LogStatement,
    IfBlock,
    Program,
)
from registration_system.dsl.interpreter import Interpreter
from registration_system.dsl.context import ExecutionContext
from registration_system.dsl.errors import ExecutionError


# ============================================================================
# Feature 9.1: While Loop
# ============================================================================


@pytest.mark.feature("9.1")
@pytest.mark.priority("high")
class Test9_1_WhileLoopParsing:
    """
    Test While Loop parsing alignment with grammar/MASTER.md

    Grammar: while EXPR: INDENT STMT+ DEDENT
    Method: _parse_while_loop()
    Status: ✅ v3.0
    """

    def test_while_basic(self, parse):
        """Test basic while loop parsing"""
        code = """
let count = 0
while count < 5:
    log "test"
    count = count + 1
"""
        ast = parse(code)

        assert len(ast) == 2
        assert isinstance(ast[0], LetStatement)
        assert isinstance(ast[1], WhileLoop)
        assert ast[1].condition is not None
        assert len(ast[1].statements) == 2

    def test_while_true(self, parse):
        """Test while True loop"""
        code = """
while True:
    log "infinite"
    break
"""
        ast = parse(code)

        assert len(ast) == 1
        assert isinstance(ast[0], WhileLoop)

    def test_while_complex_condition(self, parse):
        """Test while with complex condition"""
        code = """
let loaded = False
let timeout = 0
while not loaded and timeout < 10:
    log "waiting"
"""
        ast = parse(code)

        assert len(ast) == 3
        assert isinstance(ast[2], WhileLoop)

    def test_while_nested(self, parse):
        """Test nested while loops"""
        code = """
let outer = 0
while outer < 3:
    let inner = 0
    while inner < 2:
        log "nested"
        inner = inner + 1
    outer = outer + 1
"""
        ast = parse(code)

        assert len(ast) == 2
        outer_loop = ast[1]
        assert isinstance(outer_loop, WhileLoop)
        # 循环体应该包含 inner 声明和内层循环
        assert len(outer_loop.statements) >= 2

    def test_while_empty_body(self, parse):
        """Test while with empty body (should still parse)"""
        code = """
while True:
    pass
"""
        # pass 不是 DSL 语句，这应该失败或者只有 while 没有 body
        # 实际上应该至少有一条语句
        with pytest.raises(Exception):  # 应该报错
            ast = parse(code)


# ============================================================================
# Feature 9.2: Break Statement
# ============================================================================


@pytest.mark.feature("9.2")
@pytest.mark.priority("high")
class Test9_2_BreakStatement:
    """
    Test Break Statement parsing

    Grammar: break
    Method: _parse_break()
    Status: ✅ v3.0
    """

    def test_break_in_while(self, parse):
        """Test break inside while loop"""
        code = """
while True:
    log "test"
    break
"""
        ast = parse(code)

        assert len(ast) == 1
        assert isinstance(ast[0], WhileLoop)
        assert any(isinstance(stmt, BreakStatement) for stmt in ast[0].statements)

    def test_break_with_condition(self, parse):
        """Test break with if condition"""
        code = """
let i = 0
while i < 100:
    if i == 5:
        break
    i = i + 1
"""
        ast = parse(code)

        assert len(ast) == 2
        while_loop = ast[1]
        assert isinstance(while_loop, WhileLoop)

    def test_break_outside_loop_error(self, parse):
        """Test break outside loop raises error"""
        code = """
if True:
    break
"""
        with pytest.raises(RuntimeError, match="break.*只能在循环内使用"):
            ast = parse(code)

    def test_break_at_top_level_error(self, parse):
        """Test break at top level raises error"""
        code = """
let x = 10
break
"""
        with pytest.raises(RuntimeError, match="break.*只能在循环内使用"):
            ast = parse(code)


# ============================================================================
# Feature 9.3: Continue Statement
# ============================================================================


@pytest.mark.feature("9.3")
@pytest.mark.priority("high")
class Test9_3_ContinueStatement:
    """
    Test Continue Statement parsing

    Grammar: continue
    Method: _parse_continue()
    Status: ✅ v3.0
    """

    def test_continue_in_while(self, parse):
        """Test continue inside while loop"""
        code = """
let i = 0
while i < 10:
    i = i + 1
    if i % 2 == 0:
        continue
    log f"odd: {i}"
"""
        ast = parse(code)

        assert len(ast) == 2
        while_loop = ast[1]
        assert isinstance(while_loop, WhileLoop)

    def test_continue_outside_loop_error(self, parse):
        """Test continue outside loop raises error"""
        code = """
if True:
    continue
"""
        with pytest.raises(RuntimeError, match="continue.*只能在循环内使用"):
            ast = parse(code)

    def test_continue_at_top_level_error(self, parse):
        """Test continue at top level raises error"""
        code = """
continue
"""
        with pytest.raises(RuntimeError, match="continue.*只能在循环内使用"):
            ast = parse(code)


# ============================================================================
# Feature 9: Execution Validation
# ============================================================================


@pytest.mark.feature("9")
@pytest.mark.priority("high")
class Test9_ExecutionValidation:
    """
    Test While Loop execution validation

    验证 while 循环不仅能正确解析，还能正确执行。
    这些测试确保语法对齐测试覆盖完整的解析+执行流程。

    Coverage:
    - 基本 while 循环执行
    - Break/Continue 控制流
    - 死循环保护
    - 条件类型检查
    - 嵌套循环
    - 作用域验证
    """

    @staticmethod
    def _make_program(statements):
        """辅助函数：将语句列表包装为 Program 对象"""
        if isinstance(statements, Program):
            return statements
        return Program(statements=statements, line=1)

    # ========================================================================
    # 基本功能测试
    # ========================================================================

    def test_while_basic_execution(self, parse):
        """测试基本 while 循环执行"""
        code = """
let count = 0
while count < 5:
    count = count + 1
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        count = interpreter.symbol_table.get("count", 0)
        assert count == 5, "循环应该执行 5 次"

    def test_while_condition_false_initially(self, parse):
        """测试初始条件为 False 的情况"""
        code = """
let count = 10
while count < 5:
    count = count + 1
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        count = interpreter.symbol_table.get("count", 0)
        assert count == 10, "循环体不应该执行"

    def test_while_true_with_break(self, parse):
        """测试 while True + break"""
        code = """
let count = 0
while True:
    count = count + 1
    if count >= 10:
        break
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        count = interpreter.symbol_table.get("count", 0)
        assert count == 10, "应该在 count=10 时 break"

    def test_while_with_continue(self, parse):
        """测试 while + continue"""
        code = """
let i = 0
let sum = 0
while i < 10:
    i = i + 1
    if i % 2 == 0:
        continue
    sum = sum + i
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        sum_val = interpreter.symbol_table.get("sum", 0)
        assert sum_val == 25, "奇数之和 1+3+5+7+9 = 25"

    # ========================================================================
    # Break/Continue 测试
    # ========================================================================

    def test_break_exits_loop(self, parse):
        """测试 break 立即退出循环"""
        code = """
let i = 0
while i < 100:
    if i == 5:
        break
    i = i + 1
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        i = interpreter.symbol_table.get("i", 0)
        assert i == 5, "应该在 i=5 时 break"

    def test_continue_skips_iteration(self, parse):
        """测试 continue 跳过当前迭代"""
        code = """
let i = 0
let processed = 0
while i < 10:
    i = i + 1
    if i == 5:
        continue
    processed = processed + 1
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        processed = interpreter.symbol_table.get("processed", 0)
        assert processed == 9, "应该跳过 i=5，处理 9 次"

    def test_break_in_nested_loop(self, parse):
        """测试嵌套循环中的 break (只退出内层)"""
        code = """
let outer_count = 0
let inner_breaks = 0
let inner_count = 0
while outer_count < 3:
    inner_count = 0
    while inner_count < 5:
        if inner_count == 2:
            inner_breaks = inner_breaks + 1
            break
        inner_count = inner_count + 1
    outer_count = outer_count + 1
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        outer_count = interpreter.symbol_table.get("outer_count", 0)
        inner_breaks = interpreter.symbol_table.get("inner_breaks", 0)
        assert outer_count == 3, "外层循环应该完成所有迭代"
        assert inner_breaks == 3, "内层循环应该 break 3 次"

    # ========================================================================
    # 作用域测试
    # ========================================================================

    def test_while_creates_scope_per_iteration(self, parse):
        """测试 while 循环每次迭代创建新作用域（与 for 一致）"""
        code = """
let count = 0
while count < 3:
    let temp = count * 2
    count = count + 1
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        # temp 应该在循环外不可访问（作用域已销毁）
        assert not interpreter.symbol_table.exists("temp"), "temp 应该在循环外不可见"

    def test_while_let_in_loop_body(self, parse):
        """测试 while 循环内可以使用 let（每次迭代独立）"""
        code = """
let count = 0
let sum = 0
while count < 3:
    let temp = count * 2
    sum = sum + temp
    count = count + 1
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        sum_val = interpreter.symbol_table.get("sum", 0)
        assert sum_val == 6, "应该是 0+2+4 = 6"

        # temp 应该在循环外不可见
        assert not interpreter.symbol_table.exists("temp"), "temp 应该在循环外不可见"

    def test_while_variable_modification(self, parse):
        """测试循环内变量修改影响外部"""
        code = """
let x = 0
let y = 10
while x < 5:
    x = x + 1
    y = y - 1
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        x = interpreter.symbol_table.get("x", 0)
        y = interpreter.symbol_table.get("y", 0)
        assert x == 5
        assert y == 5

    # ========================================================================
    # 嵌套循环测试
    # ========================================================================

    def test_nested_while_loops(self, parse):
        """测试嵌套 while 循环"""
        code = """
let outer = 0
let total = 0
let inner = 0
while outer < 3:
    inner = 0
    while inner < 2:
        total = total + 1
        inner = inner + 1
    outer = outer + 1
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        total = interpreter.symbol_table.get("total", 0)
        assert total == 6, "3 * 2 = 6"

    # ========================================================================
    # 错误处理测试
    # ========================================================================

    def test_while_condition_type_error(self, parse):
        """测试条件类型错误"""
        code = """
while "not a boolean":
    log "test"
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)

        with pytest.raises(ExecutionError, match="条件必须是布尔值"):
            interpreter.execute(program)

    def test_while_condition_number_error(self, parse):
        """测试条件为数字时报错"""
        code = """
let x = 5
while x:
    log "test"
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)

        with pytest.raises(ExecutionError, match="条件必须是布尔值"):
            interpreter.execute(program)

    def test_infinite_loop_protection(self, parse):
        """测试死循环保护"""
        code = """
let i = 0
while True:
    i = i + 1
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)

        with pytest.raises(ExecutionError, match="超过最大迭代次数"):
            interpreter.execute(program)

    def test_infinite_loop_no_break(self, parse):
        """测试没有 break 的无限循环被保护"""
        code = """
while True:
    log "infinite"
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)

        with pytest.raises(ExecutionError, match="超过最大迭代次数"):
            interpreter.execute(program)

    # ========================================================================
    # 复杂场景测试
    # ========================================================================

    def test_while_with_if_else(self, parse):
        """测试 while 循环内使用 if-else"""
        code = """
let i = 0
let even_count = 0
let odd_count = 0
while i < 10:
    if i % 2 == 0:
        even_count = even_count + 1
    else:
        odd_count = odd_count + 1
    i = i + 1
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        even_count = interpreter.symbol_table.get("even_count", 0)
        odd_count = interpreter.symbol_table.get("odd_count", 0)
        assert even_count == 5
        assert odd_count == 5

    def test_while_condition_evaluation_each_iteration(self, parse):
        """测试条件在每次迭代前求值"""
        code = """
let remaining = 5
let count = 0
while remaining > 0:
    remaining = remaining - 1
    count = count + 1
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        count = interpreter.symbol_table.get("count", 0)
        remaining = interpreter.symbol_table.get("remaining", 0)
        assert count == 5, "应该处理所有 5 次迭代"
        assert remaining == 0, "remaining 应该减为 0"

    def test_multiple_breaks_in_sequence(self, parse):
        """测试多个 break 条件（只执行第一个）"""
        code = """
let i = 0
let reason = ""
while i < 100:
    if i == 3:
        reason = "hit 3"
        break
    if i == 5:
        reason = "hit 5"
        break
    i = i + 1
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        i = interpreter.symbol_table.get("i", 0)
        reason = interpreter.symbol_table.get("reason", 0)
        assert i == 3, "应该在 i=3 时 break"
        assert reason == "hit 3"

    def test_break_and_continue_in_same_loop(self, parse):
        """测试同一循环中使用 break 和 continue"""
        code = """
let i = 0
let processed = 0
while i < 100:
    i = i + 1
    if i > 10:
        break
    if i % 2 == 0:
        continue
    processed = processed + 1
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        i = interpreter.symbol_table.get("i", 0)
        processed = interpreter.symbol_table.get("processed", 0)
        assert i == 11, "应该在 i=11 时 break"
        assert processed == 5, "应该处理 1,3,5,7,9 共 5 个奇数"


# ============================================================================
# 运行测试
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
