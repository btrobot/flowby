"""
VR-003 语义检查测试

VR-003: 同一作用域不能重复声明

测试策略：
1. 基本检查：同一作用域重复声明 let/const
2. 作用域遮蔽：子作用域可以声明同名变量（允许）
3. 混合声明：let 和 const 不能同名
4. 函数作用域：函数内部的重复声明
5. 循环作用域：循环内部的重复声明
6. 错误消息质量
"""

import pytest
from flowby.lexer import Lexer
from flowby.parser import Parser
from flowby.errors import ParserError


class TestVR003BasicDuplicateDeclaration:
    """VR-003 基本的重复声明检查"""

    def test_duplicate_let_in_same_scope(self):
        """测试：同一作用域重复声明 let 变量应报错"""
        source = """
let x = 10
let x = 20
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "重复声明" in str(exc_info.value)
        assert "x" in str(exc_info.value)
        assert "VR-003" in str(exc_info.value)

    def test_duplicate_const_in_same_scope(self):
        """测试：同一作用域重复声明 const 常量应报错"""
        source = """
const MAX = 100
const MAX = 200
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "重复声明" in str(exc_info.value)
        assert "MAX" in str(exc_info.value)
        assert "VR-003" in str(exc_info.value)

    def test_let_and_const_same_name(self):
        """测试：同一作用域 let 和 const 不能同名"""
        source1 = """
let x = 10
const x = 20
"""
        source2 = """
const x = 10
let x = 20
"""
        for source in [source1, source2]:
            tokens = Lexer().tokenize(source)
            with pytest.raises(ParserError) as exc_info:
                Parser().parse(tokens)

            assert "重复声明" in str(exc_info.value)
            assert "x" in str(exc_info.value)

    def test_multiple_declarations_in_sequence(self):
        """测试：连续多次声明同名变量"""
        source = """
let count = 0
let count = 1
let count = 2
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        # 应该在第二次声明时就报错
        assert "重复声明" in str(exc_info.value)


class TestVR003ScopeShadowing:
    """测试作用域遮蔽（允许）"""

    def test_variable_shadowing_in_function(self):
        """测试：函数内部可以声明与全局同名的变量（遮蔽）"""
        source = """
let x = 10

function test():
    let x = 20
    return x

let result = test()
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_const_shadowing_in_function(self):
        """测试：函数内部可以声明与全局同名的常量"""
        source = """
const MAX = 100

function test():
    const MAX = 200
    return MAX

let result = test()
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_variable_shadowing_in_loop(self):
        """测试：循环内部可以声明与外部同名的变量"""
        source = """
let total = 0
const items = [1, 2, 3]

for item in items:
    let total = item * 2
    log total
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_nested_function_shadowing(self):
        """测试：嵌套函数中的变量遮蔽"""
        source = """
let value = 10

function outer():
    let value = 20

    function inner():
        let value = 30
        return value

    return inner()

let result = outer()
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None


class TestVR003FunctionScope:
    """测试函数作用域中的重复声明"""

    def test_duplicate_let_in_function(self):
        """测试：函数内部重复声明 let 应报错"""
        source = """
function test():
    let x = 10
    let x = 20
    return x
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "重复声明" in str(exc_info.value)
        assert "x" in str(exc_info.value)

    def test_duplicate_const_in_function(self):
        """测试：函数内部重复声明 const 应报错"""
        source = """
function test():
    const MAX = 100
    const MAX = 200
    return MAX
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "重复声明" in str(exc_info.value)
        assert "MAX" in str(exc_info.value)

    def test_parameter_and_local_variable_conflict(self):
        """测试：参数名和局部变量冲突"""
        source = """
function test(x):
    let x = 20
    return x
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        # 参数 x 已经在符号表中，不能再声明同名的 let
        assert "重复声明" in str(exc_info.value)


class TestVR003LoopScope:
    """测试循环作用域中的重复声明"""

    def test_duplicate_let_in_loop(self):
        """测试：循环内部重复声明 let 应报错"""
        source = """
const items = [1, 2, 3]
for item in items:
    let result = item * 2
    let result = item * 3
    log result
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "重复声明" in str(exc_info.value)
        assert "result" in str(exc_info.value)

    def test_duplicate_const_in_loop(self):
        """测试：循环内部重复声明 const 应报错"""
        source = """
const items = [1, 2, 3]
for item in items:
    const MULTIPLIER = 2
    const MULTIPLIER = 3
    log item * MULTIPLIER
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "重复声明" in str(exc_info.value)
        assert "MULTIPLIER" in str(exc_info.value)


class TestVR003AllowedCases:
    """测试允许的声明模式"""

    def test_different_names_in_same_scope(self):
        """测试：不同名称的变量可以正常声明"""
        source = """
let x = 10
let y = 20
let z = 30
const MAX = 100
const MIN = 0
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_same_name_in_different_functions(self):
        """测试：不同函数中可以有同名变量"""
        source = """
function func1():
    let value = 10
    return value

function func2():
    let value = 20
    return value

let result1 = func1()
let result2 = func2()
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_reassignment_is_allowed(self):
        """测试：重新赋值不是重复声明（允许）"""
        source = """
let counter = 0
counter = 1
counter = 2
counter = counter + 1
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None


class TestVR003ErrorMessages:
    """测试 VR-003 错误消息质量"""

    def test_error_message_includes_rule_id(self):
        """测试：错误消息包含 VR-003 规则ID"""
        source = """
let x = 10
let x = 20
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "VR-003" in str(exc_info.value)

    def test_error_message_includes_variable_name(self):
        """测试：错误消息包含变量名"""
        source = """
const MY_CONSTANT = 42
const MY_CONSTANT = 100
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        assert "MY_CONSTANT" in str(exc_info.value)

    def test_error_message_provides_help(self):
        """测试：错误消息提供修复建议"""
        source = """
let value = 10
let value = 20
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        error_msg = str(exc_info.value)
        # 应该提到作用域或嵌套块
        assert "作用域" in error_msg or "嵌套" in error_msg or "scope" in error_msg.lower()


class TestVR003ComplexScenarios:
    """测试复杂场景"""

    def test_multiple_scopes_no_conflict(self):
        """测试：多层作用域嵌套不冲突"""
        source = """
let x = 1

function level1():
    let x = 2

    function level2():
        let x = 3

        function level3():
            let x = 4
            return x

        return level3()

    return level2()

let result = level1()
"""
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        assert ast is not None

    def test_duplicate_in_middle_of_scope(self):
        """测试：作用域中间出现重复声明"""
        source = """
let a = 1
let b = 2
let c = 3
let b = 4
let d = 5
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        # 应该在第二次声明 b 时报错
        assert "b" in str(exc_info.value)
        assert "重复声明" in str(exc_info.value)

    def test_import_and_declaration_conflict(self):
        """测试：导入的符号和声明冲突"""
        source = """
from "lib/utils" import greet
let greet = "invalid"
"""
        tokens = Lexer().tokenize(source)
        with pytest.raises(ParserError) as exc_info:
            Parser().parse(tokens)

        # greet 已经由 import 注册，不能再声明
        assert "重复声明" in str(exc_info.value)
