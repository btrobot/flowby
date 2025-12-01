"""
测试前向引用行为
"""

from src.flowby.lexer import Lexer
from src.flowby.parser import Parser
from src.flowby.interpreter import Interpreter
from src.flowby.context import ExecutionContext


def test_variable_forward_reference():
    """测试变量前向引用是否被禁止"""
    source = """
log x
let x = 10
"""
    try:
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        print("[FAIL] Parser 没有检测到变量前向引用")
    except Exception as e:
        print(f"[PASS] Parser 检测到变量前向引用: {e}")


def test_function_forward_reference():
    """测试函数前向引用是否被允许"""
    source = """
let result = add(1, 2)

function add(a, b):
    return a + b
"""
    try:
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        context = ExecutionContext(task_id="test-forward-ref", script_name="test")
        interpreter = Interpreter(context)
        interpreter.execute(ast)
        print(f"[PASS] 函数前向引用允许: result = {context.variables.get('result')}")
    except Exception as e:
        print(f"[FAIL] 函数前向引用被禁止: {e}")


def test_function_backward_reference():
    """测试函数后向引用（正常情况）"""
    source = """
function add(a, b):
    return a + b

let result = add(1, 2)
"""
    try:
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        context = ExecutionContext(task_id="test-backward-ref", script_name="test")
        interpreter = Interpreter(context)
        interpreter.execute(ast)
        print(f"[PASS] 函数后向引用成功: result = {context.variables.get('result')}")
    except Exception as e:
        print(f"[FAIL] 函数后向引用失败: {e}")


def test_function_mutual_recursion():
    """测试相互递归函数（前向引用场景）"""
    source = """
function isEven(n):
    if n == 0:
        return True
    return isOdd(n - 1)

function isOdd(n):
    if n == 0:
        return False
    return isEven(n - 1)

let result = isEven(4)
"""
    try:
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        context = ExecutionContext(task_id="test-mutual-recursion", script_name="test")
        interpreter = Interpreter(context)
        interpreter.execute(ast)
        print(f"[PASS] 相互递归成功: result = {context.variables.get('result')}")
    except Exception as e:
        print(f"[FAIL] 相互递归失败: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("测试 Flowby DSL 的前向引用行为")
    print("=" * 60)

    print("\n1. 测试变量前向引用:")
    test_variable_forward_reference()

    print("\n2. 测试函数前向引用:")
    test_function_forward_reference()

    print("\n3. 测试函数后向引用:")
    test_function_backward_reference()

    print("\n4. 测试相互递归函数:")
    test_function_mutual_recursion()

    print("\n" + "=" * 60)
