"""
Grammar Alignment Test: v3.0 内置函数（Python风格）

Features: Math, Date, JSON, Global 函数

Reference: grammar/DESIGN-V3.md, grammar/V3-EXAMPLES.dsl
"""

import pytest


class TestV3_Math_Functions:
    """Math 命名空间函数"""

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_math_abs(self, parse_v3):
        """✅ 正确：Math.abs"""
        source = "let abs_val = Math.abs(-5)"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_math_round(self, parse_v3):
        """✅ 正确：Math.round"""
        source = "let rounded = Math.round(3.7)"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_math_ceil(self, parse_v3):
        """✅ 正确：Math.ceil"""
        source = "let ceiling = Math.ceil(3.2)"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_math_floor(self, parse_v3):
        """✅ 正确：Math.floor"""
        source = "let floor = Math.floor(3.8)"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_math_max(self, parse_v3):
        """✅ 正确：Math.max"""
        source = "let max_val = Math.max(1, 5, 3)"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_math_min(self, parse_v3):
        """✅ 正确：Math.min"""
        source = "let min_val = Math.min(1, 5, 3)"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_math_random(self, parse_v3):
        """✅ 正确：Math.random（注意：不能使用 'random' 作为变量名，它是保留的命名空间）"""
        source = "let randomValue = Math.random()"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_math_pow(self, parse_v3):
        """✅ 正确：Math.pow"""
        source = "let power = Math.pow(2, 3)"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_math_sqrt(self, parse_v3):
        """✅ 正确：Math.sqrt"""
        source = "let sqrt = Math.sqrt(16)"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_math_nested(self, parse_v3):
        """✅ 正确：嵌套 Math 函数"""
        source = "let result = Math.abs(Math.min(-5, -10))"
        result = parse_v3(source)
        assert result.success == True


class TestV3_Date_Functions:
    """Date 命名空间函数"""

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_date_now(self, parse_v3):
        """✅ 正确：Date.now"""
        source = "let now = Date.now()"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_date_format(self, parse_v3):
        """✅ 正确：Date.format"""
        source = 'let formatted = Date.format("YYYY-MM-DD")'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_date_from_timestamp(self, parse_v3):
        """✅ 正确：Date.from_timestamp"""
        source = "let from_ts = Date.from_timestamp(1609459200)"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    @pytest.mark.python_aligned
    def test_date_in_log(self, parse_v3):
        """✅ 正确：在日志中使用（f-string）"""
        source = 'log f"时间戳: {Date.now()}"'
        result = parse_v3(source)
        assert result.success == True


class TestV3_JSON_Functions:
    """JSON 命名空间函数"""

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_json_stringify(self, parse_v3):
        """✅ 正确：JSON.stringify"""
        source = "let json_str = JSON.stringify({name: \"Alice\", age: 30})"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_json_parse(self, parse_v3):
        """✅ 正确：JSON.parse"""
        source = 'let json_obj = JSON.parse("{\\"key\\": \\"value\\"}")'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    @pytest.mark.python_aligned
    def test_json_with_python_values(self, parse_v3):
        """✅ 正确：JSON 处理 Python 风格值"""
        source = "let json_str = JSON.stringify({active: True, data: None})"
        result = parse_v3(source)
        assert result.success == True


class TestV3_Global_Functions:
    """全局函数（类似 Python 内置函数）"""

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_number_conversion(self, parse_v3):
        """✅ 正确：Number 转换（类似 int）"""
        source = 'let num = Number("42")'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_string_conversion(self, parse_v3):
        """✅ 正确：String 转换（类似 str）"""
        source = "let str = String(123)"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_boolean_conversion(self, parse_v3):
        """✅ 正确：Boolean 转换（类似 bool）"""
        source = "let bool = Boolean(1)"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_isnan(self, parse_v3):
        """✅ 正确：isNaN"""
        source = 'let is_nan = isNaN("abc")'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.builtin
    def test_isfinite(self, parse_v3):
        """✅ 正确：isFinite"""
        source = "let is_finite = isFinite(100)"
        result = parse_v3(source)
        assert result.success == True


class TestV3_Builtin_Integration:
    """内置函数综合测试"""

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_functions_in_workflow(self, parse_v3):
        """✅ 正确：工作流中使用内置函数（v3.0 Python 风格）"""
        source = """
step "数据处理":
    let score = Number(score_string)
    let rounded = Math.round(score)
    let now = Date.now()
    log f"分数: {rounded}, 时间: {now}"
"""
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_functions_in_conditionals(self, parse_v3):
        """✅ 正确：条件中使用函数（True/False Python 风格）"""
        source = """
if isNaN(user_input):
    log "输入不是数字"
else if isFinite(Number(user_input)):
    let num = Number(user_input)
    if num >= 0:
        log f"有效数字: {num}"
"""
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.integration
    def test_nested_function_calls(self, parse_v3):
        """✅ 正确：嵌套函数调用"""
        source = """
let result = Math.round(Math.abs(Number("-3.7")))
let json_str = JSON.stringify({value: result})
"""
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.v3_specific
    def test_functions_in_assertions(self, parse_v3):
        """✅ 正确：断言中使用函数（无 end）"""
        source = """
let result = Math.abs(-10)
assert result == 10
assert isFinite(result)
"""
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_type_conversion_workflow(self, parse_v3):
        """✅ 正确：类型转换工作流"""
        source = """
let user_age = Number(age_string)
if isFinite(user_age) and user_age >= 18:
    log f"成年用户: {user_age}岁"
else:
    log "未成年或无效输入"
"""
        result = parse_v3(source)
        assert result.success == True


"""
测试统计：
- Math Functions: 10 tests
- Date Functions: 4 tests
- JSON Functions: 3 tests
- Global Functions: 5 tests
- Integration: 5 tests
总计: 27 tests

v3.0特性验证：
✅ 所有内置函数支持
✅ Python风格：True/False/None
✅ f-string 支持
✅ 无 end 关键字
✅ 类似 Python 内置函数命名
"""
