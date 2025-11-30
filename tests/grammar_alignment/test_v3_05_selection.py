"""
Grammar Alignment Test: v3.0 选择（Python风格）

测试核心原则：
1. 正确的代码正确解析
2. 错误的代码报错一致
3. v3.0特性：无end关键字，纯缩进块

Features tested:
- 5.1 Select Element (v3.0)
- 5.2 Select Option (v3.0)

Reference: grammar/DESIGN-V3.md #5, grammar/V3-EXAMPLES.dsl
"""

import pytest


# ============================================================================
# 5.1 Select Element 测试
# ============================================================================

class TestV3_5_1_SelectElement:
    """Select Element 语句测试"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.1")
    def test_select_basic(self, parse_v3):
        """✅ 正确：基础元素选择"""
        source = 'select "input"'
        result = parse_v3(source)
        assert result.success == True, "基础元素选择应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.1")
    def test_select_where_name_equals(self, parse_v3):
        """✅ 正确：按 name 属性选择"""
        source = 'select "input" where name equals "username"'
        result = parse_v3(source)
        assert result.success == True, "按 name 选择应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.1")
    def test_select_where_text_contains(self, parse_v3):
        """✅ 正确：按文本包含选择"""
        source = 'select "button" where text contains "Submit"'
        result = parse_v3(source)
        assert result.success == True, "按文本包含选择应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.1")
    def test_select_where_text_equals(self, parse_v3):
        """✅ 正确：按文本相等选择"""
        source = 'select "button" where text equals "Click Me"'
        result = parse_v3(source)
        assert result.success == True, "按文本相等选择应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.1")
    def test_select_where_href_contains(self, parse_v3):
        """✅ 正确：按 href 包含选择"""
        source = 'select "a" where href contains "/admin"'
        result = parse_v3(source)
        assert result.success == True, "按 href 包含选择应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.1")
    def test_select_where_class_equals(self, parse_v3):
        """✅ 正确：按 class 选择"""
        source = 'select "div" where class equals "active"'
        result = parse_v3(source)
        assert result.success == True, "按 class 选择应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.1")
    def test_select_where_id_contains(self, parse_v3):
        """✅ 正确：按 id 包含选择"""
        source = 'select "div" where id contains "main"'
        result = parse_v3(source)
        assert result.success == True, "按 id 包含选择应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.1")
    def test_select_where_src_contains(self, parse_v3):
        """✅ 正确：按 src 包含选择"""
        source = 'select "img" where src contains "logo"'
        result = parse_v3(source)
        assert result.success == True, "按 src 包含选择应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.1")
    def test_select_where_value_equals(self, parse_v3):
        """✅ 正确：按 value 选择"""
        source = 'select "input" where value equals "test"'
        result = parse_v3(source)
        assert result.success == True, "按 value 选择应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.1")
    def test_select_multiple_conditions(self, parse_v3):
        """✅ 正确：多个条件选择"""
        source = 'select "div" where class equals "active" and id contains "main"'
        result = parse_v3(source)
        assert result.success == True, "多个条件选择应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.1")
    def test_select_matches_operator(self, parse_v3):
        """✅ 正确：matches 操作符"""
        source = 'select "input" where name matches "user.*"'
        result = parse_v3(source)
        assert result.success == True, "matches 操作符应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.1")
    @pytest.mark.v3_specific
    def test_select_in_step(self, parse_v3):
        """✅ 正确：在 step 块内使用（v3.0：无 end step）"""
        source = """
step "元素选择":
    select "input" where name equals "username"
    select "button" where text contains "Submit"
"""
        result = parse_v3(source)
        assert result.success == True, "step 块内的 select 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.1")
    @pytest.mark.v3_specific
    def test_select_in_if(self, parse_v3):
        """✅ 正确：在 if 块内使用（v3.0：无 end if）"""
        source = """
if has_filter:
    select "div" where class equals "filtered"
"""
        result = parse_v3(source)
        assert result.success == True, "if 块内的 select 应该正确解析"


# ============================================================================
# 5.2 Select Option 测试
# ============================================================================

class TestV3_5_2_SelectOption:
    """Select Option 语句测试"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.2")
    def test_select_option_basic(self, parse_v3):
        """✅ 正确：基础选项选择"""
        source = 'select option "China" from "#country"'
        result = parse_v3(source)
        assert result.success == True, "基础选项选择应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.2")
    def test_select_option_class_selector(self, parse_v3):
        """✅ 正确：类选择器"""
        source = 'select option "English" from ".language-selector"'
        result = parse_v3(source)
        assert result.success == True, "类选择器应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.2")
    def test_select_option_attribute_selector(self, parse_v3):
        """✅ 正确：属性选择器"""
        source = 'select option "Large" from \'select[name="size"]\''
        result = parse_v3(source)
        assert result.success == True, "属性选择器应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.2")
    def test_select_option_with_variable(self, parse_v3):
        """✅ 正确：使用变量值"""
        source = """
let country_code = "US"
select option country_code from "#country-select"
"""
        result = parse_v3(source)
        assert result.success == True, "使用变量的选项选择应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.2")
    @pytest.mark.v3_specific
    def test_select_option_in_step(self, parse_v3):
        """✅ 正确：在 step 块内使用（v3.0：无 end step）"""
        source = """
step "下拉选择":
    select option "China" from "#country"
    select option "English" from "#language"
"""
        result = parse_v3(source)
        assert result.success == True, "step 块内的 select option 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.2")
    @pytest.mark.v3_specific
    def test_select_option_in_if(self, parse_v3):
        """✅ 正确：在 if 块内使用（v3.0：无 end if）"""
        source = """
if needs_selection:
    select option "Premium" from "#plan-selector"
"""
        result = parse_v3(source)
        assert result.success == True, "if 块内的 select option 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("5.2")
    @pytest.mark.python_aligned
    def test_select_option_with_fstring(self, parse_v3):
        """✅ 正确：使用 f-string（v3.0 Python 风格）"""
        source = """
let size = "L"
select option f"Size {size}" from "#size-selector"
"""
        result = parse_v3(source)
        assert result.success == True, "f-string 选项值应该正确解析"


# ============================================================================
# 综合测试
# ============================================================================

class TestV3_5_Integration:
    """选择功能综合测试"""

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_combined_selection_workflow(self, parse_v3):
        """✅ 正确：组合选择工作流（v3.0 Python 风格）"""
        source = """
step "表单填写":
    select "input" where name equals "email"
    type "user@example.com"
    select option "China" from "#country"
    select option "English" from "#language"
    select "button" where text contains "Submit"
    click
"""
        result = parse_v3(source)
        assert result.success == True, "组合选择工作流应该正确解析（Python 风格）"

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.v3_specific
    def test_conditional_selection(self, parse_v3):
        """✅ 正确：条件选择（v3.0：纯缩进）"""
        source = """
if user_type == "admin":
    select option "Administrator" from "#role-selector"
else:
    select option "User" from "#role-selector"
"""
        result = parse_v3(source)
        assert result.success == True, "条件选择应该正确解析（纯缩进）"

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_nested_selection(self, parse_v3):
        """✅ 正确：嵌套块中的选择（v3.0）"""
        source = """
step "复杂选择":
    if has_options:
        select "div" where class equals "active"
        if needs_filter:
            select option "Filtered" from "#filter"
"""
        result = parse_v3(source)
        assert result.success == True, "嵌套块中的选择应该正确解析"

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.feature("5.1", "5.2")
    def test_all_selection_types(self, parse_v3):
        """✅ 正确：所有选择类型组合"""
        source = """
select "input" where name equals "username"
select "button" where text contains "Submit"
select option "China" from "#country"
select "a" where href contains "/admin"
"""
        result = parse_v3(source)
        assert result.success == True, "所有选择类型组合应该正确解析"


# ============================================================================
# 测试总结
# ============================================================================

"""
测试统计：
- Feature 5.1 (Select Element): 13 tests
- Feature 5.2 (Select Option): 7 tests
- Integration: 4 tests
总计: 24 tests

v3.0 特性验证：
✅ 无 end 关键字（纯缩进块）
✅ Select Element 支持多种条件和操作符
✅ Select Option 支持变量和 f-string
✅ 所有选择语句支持在 step/if 块内使用
✅ Python 风格的组合和嵌套

关键发现：
1. Select Element 支持 where 条件：equals/contains/matches
2. 支持多种属性：name/text/href/class/id/src/value
3. 支持多个条件组合（and 连接）
4. Select Option 支持 CSS 选择器和属性选择器
5. v3.0 使用纯缩进，完全移除 end 关键字
"""
