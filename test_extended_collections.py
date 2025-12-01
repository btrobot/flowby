#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 v6.5 扩展集合方法"""

import sys
sys.path.insert(0, 'src')

from flowby.lexer import Lexer
from flowby.parser import Parser
from flowby.interpreter import Interpreter
from flowby.context import ExecutionContext


print("\n=== 测试 v6.5 扩展集合方法 ===\n")

# ============================================================
# 1. sort() 方法
# ============================================================
print("--- 1. sort() 方法 ---")

# 默认排序
source1 = """
let numbers = [3, 1, 4, 1, 5, 9, 2, 6]
let sorted = numbers.sort()
"""
tokens = Lexer().tokenize(source1)
ast = Parser().parse(tokens)
context = ExecutionContext('test-task')
interpreter = Interpreter(context)
interpreter.execute(ast)
sorted_result = interpreter.symbol_table.get("sorted", line_number=0)
print(f"[OK] 默认排序: {sorted_result}")
assert sorted_result == [1, 1, 2, 3, 4, 5, 6, 9], f"期望 [1, 1, 2, 3, 4, 5, 6, 9]，实际 {sorted_result}"

# 自定义比较器（降序）
source2 = """
let numbers = [3, 1, 4, 1, 5]
let descending = numbers.sort((a, b) => b - a)
"""
tokens = Lexer().tokenize(source2)
ast = Parser().parse(tokens)
context = ExecutionContext('test-task')
interpreter = Interpreter(context)
interpreter.execute(ast)
descending = interpreter.symbol_table.get("descending", line_number=0)
print(f"[OK] 降序排序: {descending}")
assert descending == [5, 4, 3, 1, 1], f"期望 [5, 4, 3, 1, 1]，实际 {descending}"


# ============================================================
# 2. reverse() 方法
# ============================================================
print("\n--- 2. reverse() 方法 ---")

source3 = """
let numbers = [1, 2, 3, 4, 5]
let reversed = numbers.reverse()
"""
tokens = Lexer().tokenize(source3)
ast = Parser().parse(tokens)
context = ExecutionContext('test-task')
interpreter = Interpreter(context)
interpreter.execute(ast)
reversed_result = interpreter.symbol_table.get("reversed", line_number=0)
print(f"[OK] 反转: {reversed_result}")
assert reversed_result == [5, 4, 3, 2, 1], f"期望 [5, 4, 3, 2, 1]，实际 {reversed_result}"


# ============================================================
# 3. slice() 方法
# ============================================================
print("\n--- 3. slice() 方法 ---")

# slice(start, end)
source4 = """
let numbers = [1, 2, 3, 4, 5, 6, 7, 8]
let sliced = numbers.slice(2, 5)
"""
tokens = Lexer().tokenize(source4)
ast = Parser().parse(tokens)
context = ExecutionContext('test-task')
interpreter = Interpreter(context)
interpreter.execute(ast)
sliced_result = interpreter.symbol_table.get("sliced", line_number=0)
print(f"[OK] slice(2, 5): {sliced_result}")
assert sliced_result == [3, 4, 5], f"期望 [3, 4, 5]，实际 {sliced_result}"

# slice(start) - 到末尾
source5 = """
let numbers = [1, 2, 3, 4, 5]
let sliced = numbers.slice(3)
"""
tokens = Lexer().tokenize(source5)
ast = Parser().parse(tokens)
context = ExecutionContext('test-task')
interpreter = Interpreter(context)
interpreter.execute(ast)
sliced_result2 = interpreter.symbol_table.get("sliced", line_number=0)
print(f"[OK] slice(3): {sliced_result2}")
assert sliced_result2 == [4, 5], f"期望 [4, 5]，实际 {sliced_result2}"


# ============================================================
# 4. join() 方法
# ============================================================
print("\n--- 4. join() 方法 ---")

# 字符串列表
source6 = """
let words = ["Hello", "World", "Flowby"]
let sentence = words.join(" ")
"""
tokens = Lexer().tokenize(source6)
ast = Parser().parse(tokens)
context = ExecutionContext('test-task')
interpreter = Interpreter(context)
interpreter.execute(ast)
sentence = interpreter.symbol_table.get("sentence", line_number=0)
print(f"[OK] join(' '): {sentence}")
assert sentence == "Hello World Flowby", f"期望 'Hello World Flowby'，实际 {sentence}"

# 数字列表
source7 = """
let numbers = [1, 2, 3, 4, 5]
let joined = numbers.join(", ")
"""
tokens = Lexer().tokenize(source7)
ast = Parser().parse(tokens)
context = ExecutionContext('test-task')
interpreter = Interpreter(context)
interpreter.execute(ast)
joined = interpreter.symbol_table.get("joined", line_number=0)
print(f"[OK] join(', '): {joined}")
assert joined == "1, 2, 3, 4, 5", f"期望 '1, 2, 3, 4, 5'，实际 {joined}"


# ============================================================
# 5. unique() 方法
# ============================================================
print("\n--- 5. unique() 方法 ---")

source8 = """
let numbers = [1, 2, 2, 3, 3, 3, 4, 5, 5]
let unique = numbers.unique()
"""
tokens = Lexer().tokenize(source8)
ast = Parser().parse(tokens)
context = ExecutionContext('test-task')
interpreter = Interpreter(context)
interpreter.execute(ast)
unique_result = interpreter.symbol_table.get("unique", line_number=0)
print(f"[OK] unique(): {unique_result}")
assert unique_result == [1, 2, 3, 4, 5], f"期望 [1, 2, 3, 4, 5]，实际 {unique_result}"


# ============================================================
# 6. length() 方法
# ============================================================
print("\n--- 6. length() 方法 ---")

source9 = """
let numbers = [1, 2, 3, 4, 5]
let len = numbers.length()
"""
tokens = Lexer().tokenize(source9)
ast = Parser().parse(tokens)
context = ExecutionContext('test-task')
interpreter = Interpreter(context)
interpreter.execute(ast)
length = interpreter.symbol_table.get("len", line_number=0)
print(f"[OK] length(): {length}")
assert length == 5, f"期望 5，实际 {length}"


# ============================================================
# 7. 链式调用
# ============================================================
print("\n--- 7. 链式调用 ---")

source10 = """
let numbers = [5, 2, 8, 1, 9, 3, 7, 4, 6]
let result = numbers.filter(x => x > 3).sort().slice(0, 3)
"""
tokens = Lexer().tokenize(source10)
ast = Parser().parse(tokens)
context = ExecutionContext('test-task')
interpreter = Interpreter(context)
interpreter.execute(ast)
chained = interpreter.symbol_table.get("result", line_number=0)
print(f"[OK] 链式调用: {chained}")
assert chained == [4, 5, 6], f"期望 [4, 5, 6]，实际 {chained}"


# ============================================================
# 8. 复杂组合
# ============================================================
print("\n--- 8. 复杂组合 ---")

source11 = """
let data = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5]
let result = data.unique().reverse().slice(1, 4).join(" -> ")
"""
tokens = Lexer().tokenize(source11)
ast = Parser().parse(tokens)
context = ExecutionContext('test-task')
interpreter = Interpreter(context)
interpreter.execute(ast)
complex = interpreter.symbol_table.get("result", line_number=0)
print(f"[OK] 复杂组合: {complex}")
assert complex == "4 -> 3 -> 2", f"期望 '4 -> 3 -> 2'，实际 {complex}"


print("\n=== 所有测试通过！v6.5 扩展集合方法功能正常！ ===")
