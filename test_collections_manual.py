#!/usr/bin/env python
"""
手动测试 Lambda 和集合操作功能
"""

from src.flowby.lexer import Lexer
from src.flowby.parser import Parser
from src.flowby.interpreter import Interpreter
from src.flowby.context import ExecutionContext


def test_lambda_single_param():
    """测试单参数 Lambda"""
    print("\n=== 测试单参数 Lambda ===")
    source = """
let double = x => x * 2
let result = double(5)
"""
    tokens = Lexer().tokenize(source)
    ast = Parser().parse(tokens)
    context = ExecutionContext('test-task')
    interpreter = Interpreter(context)
    interpreter.execute(ast)

    result = context.symbol_table.get("result", line_number=0)
    print(f"✅ result = {result}, 期望 = 10")
    assert result == 10


def test_filter_basic():
    """测试 filter 方法"""
    print("\n=== 测试 filter 方法 ===")
    source = """
let numbers = [1, 2, 3, 4, 5, 6]
let evens = numbers.filter(x => x % 2 == 0)
"""
    tokens = Lexer().tokenize(source)
    ast = Parser().parse(tokens)
    context = ExecutionContext('test-task')
    interpreter = Interpreter(context)
    interpreter.execute(ast)

    evens = context.symbol_table.get("evens", line_number=0)
    print(f"✅ evens = {evens}, 期望 = [2, 4, 6]")
    assert evens == [2, 4, 6]


def test_map_basic():
    """测试 map 方法"""
    print("\n=== 测试 map 方法 ===")
    source = """
let numbers = [1, 2, 3, 4]
let doubled = numbers.map(x => x * 2)
"""
    tokens = Lexer().tokenize(source)
    ast = Parser().parse(tokens)
    context = ExecutionContext('test-task')
    interpreter = Interpreter(context)
    interpreter.execute(ast)

    doubled = context.symbol_table.get("doubled", line_number=0)
    print(f"✅ doubled = {doubled}, 期望 = [2, 4, 6, 8]")
    assert doubled == [2, 4, 6, 8]


def test_reduce_sum():
    """测试 reduce 求和"""
    print("\n=== 测试 reduce 求和 ===")
    source = """
let numbers = [1, 2, 3, 4, 5]
let sum = numbers.reduce((acc, x) => acc + x, 0)
"""
    tokens = Lexer().tokenize(source)
    ast = Parser().parse(tokens)
    context = ExecutionContext('test-task')
    interpreter = Interpreter(context)
    interpreter.execute(ast)

    sum_result = context.symbol_table.get("sum", line_number=0)
    print(f"✅ sum = {sum_result}, 期望 = 15")
    assert sum_result == 15


def test_chained_operations():
    """测试链式调用"""
    print("\n=== 测试链式调用 ===")
    source = """
let numbers = [1, 2, 3, 4, 5, 6]
let result = numbers.filter(x => x % 2 == 0).map(x => x * 2)
"""
    tokens = Lexer().tokenize(source)
    ast = Parser().parse(tokens)
    context = ExecutionContext('test-task')
    interpreter = Interpreter(context)
    interpreter.execute(ast)

    result = context.symbol_table.get("result", line_number=0)
    print(f"✅ result = {result}, 期望 = [4, 8, 12]")
    assert result == [4, 8, 12]


if __name__ == "__main__":
    try:
        test_lambda_single_param()
        test_filter_basic()
        test_map_basic()
        test_reduce_sum()
        test_chained_operations()
        print("\n🎉 所有测试通过！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
