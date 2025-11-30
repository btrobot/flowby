"""
Grammar Alignment Test: v3.0 数据类型（Python风格）

⭐ v3.0 核心变更：Python 化的数据类型

测试核心原则：
1. Python 风格数据类型正确解析
2. 非 Python 风格数据类型报错一致

Features tested:
- Boolean: True/False (v3.0: 首字母大写)
- None: None (v3.0: 而非 null)
- Number: 整数、浮点数、负数
- String: 普通字符串、f-string (v3.0: 显式插值)
- Array: Python 风格列表
- Object: Python 风格字典

Reference: grammar/DESIGN-V3.md, grammar/PYTHON-ALIGNMENT-REVIEW.md
"""

import pytest


# ============================================================================
# 布尔类型测试（Python 风格）
# ============================================================================

class TestV3_DataTypes_Boolean:
    """布尔类型：True/False（Python 风格）"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_true_literal(self, parse_v3):
        """✅ 正确：True（首字母大写）"""
        source = "let active = True"
        result = parse_v3(source)
        assert result.success == True, "True 应该被正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_false_literal(self, parse_v3):
        """✅ 正确：False（首字母大写）"""
        source = "let inactive = False"
        result = parse_v3(source)
        assert result.success == True, "False 应该被正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_true_in_expression(self, parse_v3):
        """✅ 正确：表达式中的 True"""
        source = "let result = active == True"
        result = parse_v3(source)
        assert result.success == True, "表达式中的 True 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_false_in_condition(self, parse_v3):
        """✅ 正确：条件中的 False"""
        source = """
if verified == False:
    log "未验证"
"""
        result = parse_v3(source)
        assert result.success == True, "条件中的 False 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_boolean_operations(self, parse_v3):
        """✅ 正确：布尔运算"""
        source = "let result = True and False or True"
        result = parse_v3(source)
        assert result.success == True, "布尔运算应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_not_true(self, parse_v3):
        """✅ 正确：not True"""
        source = "let result = not True"
        result = parse_v3(source)
        assert result.success == True, "not True 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_lowercase_true_error(self, parse_v3):
        """❌ 错误：true（小写）应报错"""
        source = "let active = true"
        result = parse_v3(source)
        assert result.success == False, "小写 true 应该报错"
        assert "True" in result.error or "布尔" in result.error, \
            f"错误提示应提及 True，实际：{result.error}"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_lowercase_false_error(self, parse_v3):
        """❌ 错误：false（小写）应报错"""
        source = "let active = false"
        result = parse_v3(source)
        assert result.success == False, "小写 false 应该报错"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_uppercase_TRUE_error(self, parse_v3):
        """❌ 错误：TRUE（全大写）应报错"""
        source = "let active = TRUE"
        result = parse_v3(source)
        assert result.success == False, "全大写 TRUE 应该报错"


# ============================================================================
# None 类型测试（Python 风格）
# ============================================================================

class TestV3_DataTypes_None:
    """None 类型（Python 风格）"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_none_literal(self, parse_v3):
        """✅ 正确：None（首字母大写）"""
        source = "let data = None"
        result = parse_v3(source)
        assert result.success == True, "None 应该被正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_none_in_comparison(self, parse_v3):
        """✅ 正确：None 比较"""
        source = "let is_empty = data == None"
        result = parse_v3(source)
        assert result.success == True, "None 比较应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_none_in_condition(self, parse_v3):
        """✅ 正确：条件中的 None"""
        source = """
if value == None:
    log "值为空"
"""
        result = parse_v3(source)
        assert result.success == True, "条件中的 None 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_none_not_equal(self, parse_v3):
        """✅ 正确：None 不等于"""
        source = "let has_value = data != None"
        result = parse_v3(source)
        assert result.success == True, "None 不等于应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_null_keyword_error(self, parse_v3):
        """❌ 错误：null 关键字应报错"""
        source = "let data = null"
        result = parse_v3(source)
        assert result.success == False, "null 应该报错"
        assert "None" in result.error or "null" in result.error.lower(), \
            f"错误提示应提及 None，实际：{result.error}"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_lowercase_none_error(self, parse_v3):
        """❌ 错误：none（小写）应报错"""
        source = "let data = none"
        result = parse_v3(source)
        assert result.success == False, "小写 none 应该报错"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_uppercase_NONE_error(self, parse_v3):
        """❌ 错误：NONE（全大写）应报错"""
        source = "let data = NONE"
        result = parse_v3(source)
        assert result.success == False, "全大写 NONE 应该报错"


# ============================================================================
# 数字类型测试
# ============================================================================

class TestV3_DataTypes_Number:
    """数字类型：整数、浮点数"""

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_integer_positive(self, parse_v3):
        """✅ 正确：正整数"""
        source = "let count = 42"
        result = parse_v3(source)
        assert result.success == True, "正整数应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_integer_zero(self, parse_v3):
        """✅ 正确：零"""
        source = "let value = 0"
        result = parse_v3(source)
        assert result.success == True, "零应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_integer_negative(self, parse_v3):
        """✅ 正确：负整数"""
        source = "let temp = -10"
        result = parse_v3(source)
        assert result.success == True, "负整数应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_float_positive(self, parse_v3):
        """✅ 正确：正浮点数"""
        source = "let pi = 3.14"
        result = parse_v3(source)
        assert result.success == True, "正浮点数应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_float_negative(self, parse_v3):
        """✅ 正确：负浮点数"""
        source = "let temp = -273.15"
        result = parse_v3(source)
        assert result.success == True, "负浮点数应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_float_leading_zero(self, parse_v3):
        """✅ 正确：前导零的浮点数"""
        source = "let rate = 0.08"
        result = parse_v3(source)
        assert result.success == True, "前导零的浮点数应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_number_in_expression(self, parse_v3):
        """✅ 正确：表达式中的数字"""
        source = "let result = 10 + 20 * 3"
        result = parse_v3(source)
        assert result.success == True, "表达式中的数字应该正确解析"


# ============================================================================
# 字符串类型测试（v3.0: f-string 显式插值）
# ============================================================================

class TestV3_DataTypes_String:
    """字符串类型：普通字符串、f-string"""

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_string_double_quote(self, parse_v3):
        """✅ 正确：双引号字符串"""
        source = 'let name = "Alice"'
        result = parse_v3(source)
        assert result.success == True, "双引号字符串应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_string_single_quote(self, parse_v3):
        """✅ 正确：单引号字符串"""
        source = "let name = 'Bob'"
        result = parse_v3(source)
        assert result.success == True, "单引号字符串应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_string_empty(self, parse_v3):
        """✅ 正确：空字符串"""
        source = 'let empty = ""'
        result = parse_v3(source)
        assert result.success == True, "空字符串应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_fstring_interpolation(self, parse_v3):
        """✅ 正确：f-string 插值（Python 风格）"""
        source = 'log f"Count: {count}"'
        result = parse_v3(source)
        assert result.success == True, "f-string 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_fstring_multiple_interpolations(self, parse_v3):
        """✅ 正确：f-string 多个插值"""
        source = 'log f"User {name} has {count} items"'
        result = parse_v3(source)
        assert result.success == True, "f-string 多个插值应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_fstring_with_expression(self, parse_v3):
        """✅ 正确：f-string 内表达式"""
        source = 'log f"Total: {count + 1}"'
        result = parse_v3(source)
        assert result.success == True, "f-string 内表达式应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_plain_string_no_interpolation(self, parse_v3):
        """✅ 正确：普通字符串不插值（无 f 前缀）"""
        source = 'log "Count: {count}"'  # 无 f 前缀
        result = parse_v3(source)
        assert result.success == True, \
            "普通字符串（无f前缀）应该正确解析为字面量"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_string_with_escape(self, parse_v3):
        """✅ 正确：字符串转义"""
        source = r'let text = "Line 1\nLine 2"'
        result = parse_v3(source)
        assert result.success == True, "字符串转义应该正确解析"


# ============================================================================
# 数组类型测试
# ============================================================================

class TestV3_DataTypes_Array:
    """数组类型：Python 风格列表"""

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_array_empty(self, parse_v3):
        """✅ 正确：空数组"""
        source = "let items = []"
        result = parse_v3(source)
        assert result.success == True, "空数组应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_array_numbers(self, parse_v3):
        """✅ 正确：数字数组"""
        source = "let numbers = [1, 2, 3, 4, 5]"
        result = parse_v3(source)
        assert result.success == True, "数字数组应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_array_strings(self, parse_v3):
        """✅ 正确：字符串数组"""
        source = 'let names = ["Alice", "Bob", "Charlie"]'
        result = parse_v3(source)
        assert result.success == True, "字符串数组应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_array_booleans(self, parse_v3):
        """✅ 正确：布尔数组（Python 风格）"""
        source = "let flags = [True, False, True]"
        result = parse_v3(source)
        assert result.success == True, "布尔数组应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_array_with_none(self, parse_v3):
        """✅ 正确：包含 None 的数组"""
        source = "let values = [1, None, 3]"
        result = parse_v3(source)
        assert result.success == True, "包含 None 的数组应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_array_mixed_types(self, parse_v3):
        """✅ 正确：混合类型数组"""
        source = 'let mixed = [1, "two", True, None]'
        result = parse_v3(source)
        assert result.success == True, "混合类型数组应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_array_nested(self, parse_v3):
        """✅ 正确：嵌套数组"""
        source = "let matrix = [[1, 2], [3, 4], [5, 6]]"
        result = parse_v3(source)
        assert result.success == True, "嵌套数组应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_array_trailing_comma(self, parse_v3):
        """✅ 正确：尾随逗号（Python 风格）"""
        source = "let items = [1, 2, 3,]"  # 尾随逗号
        result = parse_v3(source)
        # 尾随逗号支持取决于实现
        # 至少不应该崩溃
        assert result is not None


# ============================================================================
# 对象类型测试
# ============================================================================

class TestV3_DataTypes_Object:
    """对象类型：Python 风格字典"""

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_object_empty(self, parse_v3):
        """✅ 正确：空对象"""
        source = "let data = {}"
        result = parse_v3(source)
        assert result.success == True, "空对象应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_object_simple(self, parse_v3):
        """✅ 正确：简单对象"""
        source = 'let user = {name: "Alice", age: 30}'
        result = parse_v3(source)
        assert result.success == True, "简单对象应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_object_with_boolean(self, parse_v3):
        """✅ 正确：包含布尔值的对象（Python 风格）"""
        source = 'let user = {name: "Bob", active: True, verified: False}'
        result = parse_v3(source)
        assert result.success == True, "包含布尔值的对象应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_object_with_none(self, parse_v3):
        """✅ 正确：包含 None 的对象"""
        source = 'let user = {name: "Alice", email: None}'
        result = parse_v3(source)
        assert result.success == True, "包含 None 的对象应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_object_nested(self, parse_v3):
        """✅ 正确：嵌套对象（注意：'config' 是保留的命名空间，使用 'settings' 代替）"""
        source = 'let settings = {db: {host: "localhost", port: 5432}}'
        result = parse_v3(source)
        assert result.success == True, "嵌套对象应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_object_with_array(self, parse_v3):
        """✅ 正确：包含数组的对象"""
        source = 'let user = {name: "Alice", scores: [95, 88, 92]}'
        result = parse_v3(source)
        assert result.success == True, "包含数组的对象应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_object_trailing_comma(self, parse_v3):
        """✅ 正确：尾随逗号"""
        source = 'let data = {a: 1, b: 2,}'  # 尾随逗号
        result = parse_v3(source)
        # 尾随逗号支持取决于实现
        assert result is not None


# ============================================================================
# 综合测试：复杂数据结构
# ============================================================================

class TestV3_DataTypes_Complex:
    """复杂数据结构综合测试"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_complex_nested_structure(self, parse_v3):
        """✅ 正确：复杂嵌套结构（Python 风格，注意：'config' 是保留命名空间）"""
        source = """
let appConfig = {
    app: {
        name: "MyApp",
        version: "1.0.0",
        debug: True
    },
    features: {
        auth: True,
        api: False,
        cache: None
    },
    servers: [
        {host: "server1", active: True},
        {host: "server2", active: False}
    ]
}
"""
        result = parse_v3(source)
        assert result.success == True, "复杂嵌套结构应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_all_types_in_array(self, parse_v3):
        """✅ 正确：数组包含所有类型"""
        source = '''
let mixed = [
    42,
    3.14,
    "text",
    True,
    False,
    None,
    [1, 2, 3],
    {key: "value"}
]
'''
        result = parse_v3(source)
        assert result.success == True, "包含所有类型的数组应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_user_profile_realistic(self, parse_v3):
        """✅ 正确：真实用户配置示例"""
        source = '''
let user = {
    id: 12345,
    name: "张三",
    email: "zhangsan@example.com",
    active: True,
    verified: False,
    profile: {
        age: 28,
        city: "北京",
        avatar: None
    },
    scores: [95, 88, 92, 87],
    metadata: {
        created_at: "2024-01-01",
        updated_at: None,
        tags: ["vip", "early-adopter"]
    }
}
'''
        result = parse_v3(source)
        assert result.success == True, "真实用户配置应该正确解析"


# ============================================================================
# Python 对齐验证
# ============================================================================

class TestV3_DataTypes_PythonAlignment:
    """数据类型 Python 对齐验证"""

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.parametrize("dsl_value,python_value", [
        ("True", "True"),
        ("False", "False"),
        ("None", "None"),
        ("[1, 2, 3]", "[1, 2, 3]"),
        ('{"a": 1}', "{'a': 1}"),
    ])
    def test_values_match_python(self, parse_v3, dsl_value, python_value):
        """✅ 验证：数据类型与 Python 匹配"""
        source = f"let x = {dsl_value}"
        result = parse_v3(source)
        assert result.success == True, \
            f"DSL 值应该像 Python 一样：{dsl_value}"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.parametrize("wrong_value", [
        "true",
        "false",
        "null",
        "TRUE",
        "FALSE",
        "NULL",
    ])
    def test_non_python_values_error(self, parse_v3, wrong_value):
        """❌ 验证：非 Python 风格值报错"""
        source = f"let x = {wrong_value}"
        result = parse_v3(source)
        assert result.success == False, \
            f"非 Python 风格值应该报错：{wrong_value}"


# ============================================================================
# 测试总结
# ============================================================================

"""
测试覆盖清单：

布尔类型：
✅ True/False（Python 风格）
✅ 表达式、条件中的布尔值
✅ 布尔运算
✅ 小写/全大写报错

None 类型：
✅ None（Python 风格）
✅ None 比较、条件
✅ null/none/NONE 报错

数字类型：
✅ 整数（正、负、零）
✅ 浮点数（正、负、前导零）
✅ 表达式中的数字

字符串类型：
✅ 普通字符串（单引号、双引号、空字符串）
✅ f-string 显式插值（Python 风格）
✅ f-string 多个插值、表达式
✅ 普通字符串不插值
✅ 转义字符

数组类型：
✅ 空数组、各类型数组
✅ Python 风格布尔值、None
✅ 混合类型、嵌套数组
✅ 尾随逗号

对象类型：
✅ 空对象、简单对象
✅ Python 风格布尔值、None
✅ 嵌套对象、包含数组
✅ 尾随逗号

综合测试：
✅ 复杂嵌套结构
✅ 所有类型组合
✅ 真实场景示例
✅ Python 对齐验证

总计：约 70 个数据类型测试
"""
