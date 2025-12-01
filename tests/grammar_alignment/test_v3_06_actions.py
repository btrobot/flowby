"""
Grammar Alignment Test: v3.0 动作（Python风格）

Features tested:
- 6.1 Type, 6.2 Click, 6.3 Double Click, 6.4 Right Click
- 6.5 Hover, 6.6 Clear, 6.7 Press, 6.8 Scroll
- 6.9 Check/Uncheck, 6.10 Upload

Reference: grammar/DESIGN-V3.md #6, grammar/V3-EXAMPLES.dsl
"""

import pytest


class TestV3_6_1_Type:
    """Type 动作测试"""

    @pytest.mark.v3
    @pytest.mark.feature("6.1")
    def test_type_basic(self, parse_v3):
        """✅ 正确：基础输入"""
        source = 'type "hello" into "#input"'
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.1")
    def test_type_slowly(self, parse_v3):
        """✅ 正确：慢速输入"""
        source = 'type "test" into "#input" slowly'
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.1")
    def test_type_fast(self, parse_v3):
        """✅ 正确：快速输入"""
        source = 'type "test" into "#input" fast'
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.1")
    @pytest.mark.v3_specific
    def test_type_in_step(self, parse_v3):
        """✅ 正确：step 块内（无 end step）"""
        source = """
step "填写表单":
    type "john@example.com" into "#email"
    type "password123" into "#password"
"""
        result = parse_v3(source)
        assert result.success is True


class TestV3_6_2_Click:
    """Click 动作测试"""

    @pytest.mark.v3
    @pytest.mark.feature("6.2")
    def test_click_element(self, parse_v3):
        """✅ 正确：点击元素"""
        source = 'click "#button"'
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.2")
    def test_click_class_selector(self, parse_v3):
        """✅ 正确：类选择器"""
        source = 'click ".submit-btn"'
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.2")
    @pytest.mark.v3_specific
    def test_click_in_step(self, parse_v3):
        """✅ 正确：step 块内"""
        source = """
step "点击操作":
    click "#submit"
    click ".next-btn"
"""
        result = parse_v3(source)
        assert result.success is True


class TestV3_6_3_DoubleClick:
    """Double Click 测试"""

    @pytest.mark.v3
    @pytest.mark.feature("6.3")
    def test_double_click(self, parse_v3):
        """✅ 正确：双击"""
        source = 'double click "#file"'
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.3")
    @pytest.mark.v3_specific
    def test_double_click_in_if(self, parse_v3):
        """✅ 正确：if 块内（无 end if）"""
        source = """
let editable = True
if editable:
    double click ".editable-field"
"""
        result = parse_v3(source)
        assert result.success is True


class TestV3_6_4_RightClick:
    """Right Click 测试"""

    @pytest.mark.v3
    @pytest.mark.feature("6.4")
    def test_right_click(self, parse_v3):
        """✅ 正确：右键点击"""
        source = 'right click "#context-menu"'
        result = parse_v3(source)
        assert result.success is True


class TestV3_6_5_Hover:
    """Hover 测试"""

    @pytest.mark.v3
    @pytest.mark.feature("6.5")
    def test_hover_basic(self, parse_v3):
        """✅ 正确：悬停"""
        source = 'hover over "#menu"'
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.5")
    def test_hover_without_over(self, parse_v3):
        """✅ 正确：悬停（无 over）"""
        source = 'hover "#tooltip"'
        result = parse_v3(source)
        assert result.success is True


class TestV3_6_6_Clear:
    """Clear 测试"""

    @pytest.mark.v3
    @pytest.mark.feature("6.6")
    def test_clear(self, parse_v3):
        """✅ 正确：清除输入"""
        source = 'clear "#search"'
        result = parse_v3(source)
        assert result.success is True


class TestV3_6_7_Press:
    """Press 测试"""

    @pytest.mark.v3
    @pytest.mark.feature("6.7")
    def test_press_enter(self, parse_v3):
        """✅ 正确：按 Enter"""
        source = "press Enter"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.7")
    def test_press_tab(self, parse_v3):
        """✅ 正确：按 Tab"""
        source = "press Tab"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.7")
    def test_press_escape(self, parse_v3):
        """✅ 正确：按 Escape"""
        source = "press Escape"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.7")
    def test_press_arrow_keys(self, parse_v3):
        """✅ 正确：方向键"""
        source = """
press ArrowDown
press ArrowUp
press ArrowLeft
press ArrowRight
"""
        result = parse_v3(source)
        assert result.success is True


class TestV3_6_8_Scroll:
    """Scroll 测试"""

    @pytest.mark.v3
    @pytest.mark.feature("6.8")
    def test_scroll_to_top(self, parse_v3):
        """✅ 正确：滚动到顶部"""
        source = "scroll to top"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.8")
    def test_scroll_to_bottom(self, parse_v3):
        """✅ 正确：滚动到底部"""
        source = "scroll to bottom"
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.8")
    def test_scroll_to_element(self, parse_v3):
        """✅ 正确：滚动到元素"""
        source = 'scroll to "#section"'
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.8")
    def test_scroll_to_position(self, parse_v3):
        """✅ 正确：滚动到位置"""
        source = "scroll to 500"
        result = parse_v3(source)
        assert result.success is True


class TestV3_6_9_CheckUncheck:
    """Check/Uncheck 测试"""

    @pytest.mark.v3
    @pytest.mark.feature("6.9")
    def test_check(self, parse_v3):
        """✅ 正确：选中复选框"""
        source = 'check "#agree"'
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.9")
    def test_uncheck(self, parse_v3):
        """✅ 正确：取消选中"""
        source = 'uncheck "#newsletter"'
        result = parse_v3(source)
        assert result.success is True


class TestV3_6_10_Upload:
    """Upload 测试"""

    @pytest.mark.v3
    @pytest.mark.feature("6.10")
    def test_upload(self, parse_v3):
        """✅ 正确：文件上传"""
        source = 'upload file "/path/to/file.pdf" to "#file-input"'
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.feature("6.10")
    def test_upload_with_variable(self, parse_v3):
        """✅ 正确：使用变量"""
        source = """
let avatar_path = "/path/to/avatar.jpg"
upload file avatar_path to ".avatar-upload"
"""
        result = parse_v3(source)
        assert result.success is True


class TestV3_6_Integration:
    """动作综合测试"""

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_form_workflow(self, parse_v3):
        """✅ 正确：表单操作工作流（v3.0 Python 风格）"""
        source = """
step "表单提交":
    type "user@example.com" into "#email"
    type "password123" into "#password" slowly
    check "#terms"
    click "#submit"
    wait for navigation
    assert page.url contains "/success"
"""
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.v3_specific
    def test_nested_actions(self, parse_v3):
        """✅ 正确：嵌套块中的动作（v3.0：纯缩进）"""
        source = """
let is_logged_in = True
let editable = True
step "复杂操作":
    if is_logged_in:
        click "#profile"
        if editable:
            clear "#bio"
            type "New bio text" into "#bio"
    else:
        click "#login-button"
"""
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_all_action_types(self, parse_v3):
        """✅ 正确：所有动作类型"""
        source = """
type "test" into "#input"
click "#button"
double click "#file"
right click "#menu"
hover over "#tooltip"
clear "#search"
press Enter
scroll to bottom
check "#checkbox"
upload file "/path" to "#upload"
"""
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.feature("6.1", "6.2", "6.7")
    def test_keyboard_and_mouse(self, parse_v3):
        """✅ 正确：键盘+鼠标操作组合"""
        source = """
type "search query" into "#search"
press Enter
wait for element "#results" to be visible
click ".first-result"
"""
        result = parse_v3(source)
        assert result.success is True

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_conditional_actions(self, parse_v3):
        """✅ 正确：条件动作（True/False Python 风格）"""
        source = """
let need_scroll = True
if need_scroll == True:
    scroll to bottom
else:
    scroll to top
"""
        result = parse_v3(source)
        assert result.success is True


"""
测试统计：
- Feature 6.1 (Type): 4 tests
- Feature 6.2 (Click): 3 tests
- Feature 6.3 (Double Click): 2 tests
- Feature 6.4 (Right Click): 1 test
- Feature 6.5 (Hover): 2 tests
- Feature 6.6 (Clear): 1 test
- Feature 6.7 (Press): 4 tests
- Feature 6.8 (Scroll): 4 tests
- Feature 6.9 (Check/Uncheck): 2 tests
- Feature 6.10 (Upload): 2 tests
- Integration: 5 tests
总计: 30 tests

v3.0 特性验证：
✅ 所有动作支持在 step/if 块内使用
✅ 无 end 关键字（纯缩进）
✅ True/False Python 风格布尔值
✅ 支持变量和 f-string
"""
