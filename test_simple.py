#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简单验证 Lambda 和集合操作"""

import sys

sys.path.insert(0, "src")

from flowby.lexer import Lexer
from flowby.parser import Parser
from flowby.interpreter import Interpreter
from flowby.context import ExecutionContext


print("\n=== 测试 1: 单参数 Lambda ===")
source1 = """
let double = x => x * 2
let result = double(5)
"""
tokens = Lexer().tokenize(source1)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("result", line_number=0)
print(f"[OK] result = {result} (期望 10)")
assert result == 10, f"期望 10，实际 {result}"


print("\n=== 测试 2: filter 方法 ===")
source2 = """
let numbers = [1, 2, 3, 4, 5, 6]
let evens = numbers.filter(x => x % 2 == 0)
"""
tokens = Lexer().tokenize(source2)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
evens = interpreter.symbol_table.get("evens", line_number=0)
print(f"[OK] evens = {evens} (期望 [2, 4, 6])")
assert evens == [2, 4, 6], f"期望 [2, 4, 6]，实际 {evens}"


print("\n=== 测试 3: map 方法 ===")
source3 = """
let numbers = [1, 2, 3, 4]
let doubled = numbers.map(x => x * 2)
"""
tokens = Lexer().tokenize(source3)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
doubled = interpreter.symbol_table.get("doubled", line_number=0)
print(f"[OK] doubled = {doubled} (期望 [2, 4, 6, 8])")
assert doubled == [2, 4, 6, 8], f"期望 [2, 4, 6, 8]，实际 {doubled}"


print("\n=== 测试 4: reduce 方法 ===")
source4 = """
let numbers = [1, 2, 3, 4, 5]
let sum = numbers.reduce((acc, x) => acc + x, 0)
"""
tokens = Lexer().tokenize(source4)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
sum_result = interpreter.symbol_table.get("sum", line_number=0)
print(f"[OK] sum = {sum_result} (期望 15)")
assert sum_result == 15, f"期望 15，实际 {sum_result}"


print("\n=== 测试 5: 链式调用 ===")
source5 = """
let numbers = [1, 2, 3, 4, 5, 6]
let result = numbers.filter(x => x % 2 == 0).map(x => x * 2)
"""
tokens = Lexer().tokenize(source5)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("result", line_number=0)
print(f"[OK] result = {result} (期望 [4, 8, 12])")
assert result == [4, 8, 12], f"期望 [4, 8, 12]，实际 {result}"


print("\n=== 所有测试通过！集合操作和 Lambda 表达式功能正常工作！ ===")
