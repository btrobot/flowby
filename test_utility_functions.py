#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 v6.6 实用工具函数"""

import sys

sys.path.insert(0, "src")

from flowby.lexer import Lexer
from flowby.parser import Parser
from flowby.interpreter import Interpreter
from flowby.context import ExecutionContext


print("\n=== 测试 v6.6 实用工具函数 ===\n")

# ============================================================
# 1. 字符串方法
# ============================================================
print("--- 1. 字符串方法 ---")

# capitalize()
source1 = """
let str1 = "hello world"
let capitalized = str1.capitalize()
"""
tokens = Lexer().tokenize(source1)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("capitalized", line_number=0)
print(f"[OK] capitalize(): {result}")
assert result == "Hello world", f"期望 'Hello world'，实际 {result}"

# padStart()
source2 = """
let num = "5"
let padded = num.padStart(3, "0")
"""
tokens = Lexer().tokenize(source2)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("padded", line_number=0)
print(f"[OK] padStart(): {result}")
assert result == "005", f"期望 '005'，实际 {result}"

# padEnd()
source3 = """
let num = "5"
let padded = num.padEnd(3, "0")
"""
tokens = Lexer().tokenize(source3)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("padded", line_number=0)
print(f"[OK] padEnd(): {result}")
assert result == "500", f"期望 '500'，实际 {result}"

# repeat()
source4 = """
let str2 = "ha"
let repeated = str2.repeat(3)
"""
tokens = Lexer().tokenize(source4)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("repeated", line_number=0)
print(f"[OK] repeat(): {result}")
assert result == "hahaha", f"期望 'hahaha'，实际 {result}"


# ============================================================
# 2. 数组方法
# ============================================================
print("\n--- 2. 数组方法 ---")

# flatten()
source5 = """
let nested = [[1, 2], [3, 4], [5, 6]]
let flat = nested.flatten()
"""
tokens = Lexer().tokenize(source5)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("flat", line_number=0)
print(f"[OK] flatten(): {result}")
assert result == [1, 2, 3, 4, 5, 6], f"期望 [1, 2, 3, 4, 5, 6]，实际 {result}"

# flatten(depth)
source6 = """
let deepNested = [1, [2, [3, [4]]]]
let flat2 = deepNested.flatten(2)
"""
tokens = Lexer().tokenize(source6)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("flat2", line_number=0)
print(f"[OK] flatten(2): {result}")
assert result == [1, 2, 3, [4]], f"期望 [1, 2, 3, [4]]，实际 {result}"

# chunk()
source7 = """
let numbers = [1, 2, 3, 4, 5, 6, 7]
let chunks = numbers.chunk(3)
"""
tokens = Lexer().tokenize(source7)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("chunks", line_number=0)
print(f"[OK] chunk(): {result}")
assert result == [[1, 2, 3], [4, 5, 6], [7]], f"期望 [[1, 2, 3], [4, 5, 6], [7]]，实际 {result}"


# ============================================================
# 3. 字典方法
# ============================================================
print("\n--- 3. 字典方法 ---")

# keys()
source8 = """
let dict1 = {name: "Alice", age: 30, city: "NYC"}
let keys = dict1.keys()
"""
tokens = Lexer().tokenize(source8)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("keys", line_number=0)
print(f"[OK] keys(): {result}")
assert set(result) == {"name", "age", "city"}, f"期望 ['name', 'age', 'city']，实际 {result}"

# values()
source9 = """
let dict2 = {a: 1, b: 2, c: 3}
let values = dict2.values()
"""
tokens = Lexer().tokenize(source9)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("values", line_number=0)
print(f"[OK] values(): {result}")
assert set(result) == {1, 2, 3}, f"期望 [1, 2, 3]，实际 {result}"

# entries()
source10 = """
let dict3 = {x: 10, y: 20}
let entries = dict3.entries()
"""
tokens = Lexer().tokenize(source10)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("entries", line_number=0)
print(f"[OK] entries(): {result}")
# 转换为集合比较（顺序可能不同）
result_set = {tuple(item) for item in result}
assert result_set == {("x", 10), ("y", 20)}, f"期望 [['x', 10], ['y', 20]]，实际 {result}"


# ============================================================
# 4. 实用工具函数
# ============================================================
print("\n--- 4. 实用工具函数 ---")

# zip()
source11 = """
let arr1 = [1, 2, 3]
let arr2 = ["a", "b", "c"]
let zipped = zip(arr1, arr2)
"""
tokens = Lexer().tokenize(source11)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("zipped", line_number=0)
print(f"[OK] zip(): {result}")
assert result == [
    [1, "a"],
    [2, "b"],
    [3, "c"],
], f"期望 [[1, 'a'], [2, 'b'], [3, 'c']]，实际 {result}"

# sleep() - 简单测试（不测试实际睡眠时间）
source12 = """
sleep(0.01)
let done = True
"""
tokens = Lexer().tokenize(source12)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("done", line_number=0)
print(f"[OK] sleep(): 函数执行成功")
assert result is True


# ============================================================
# 5. 链式调用
# ============================================================
print("\n--- 5. 链式调用 ---")

source13 = """
let words = ["hello", "world", "python"]
let formatted = words.map(w => w.capitalize()).join(" ")
"""
tokens = Lexer().tokenize(source13)
ast = Parser().parse(tokens)
context = ExecutionContext("test-task")
interpreter = Interpreter(context)
interpreter.execute(ast)
result = interpreter.symbol_table.get("formatted", line_number=0)
print(f"[OK] 链式调用: {result}")
assert result == "Hello World Python", f"期望 'Hello World Python'，实际 {result}"


print("\n=== 所有测试通过！v6.6 实用工具函数功能正常！ ===")
