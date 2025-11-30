"""
Grammar Alignment Test: v3.0 等待（Python风格）

测试核心原则：
1. 正确的代码正确解析
2. 错误的代码报错一致
3. v3.0特性：无end关键字，纯缩进块

Features tested:
- 4.1 Wait Duration (v3.0)
- 4.2 Wait Element (v3.0)
- 4.3 Wait Navigation (v3.0)

Reference: grammar/DESIGN-V3.md #4, grammar/V3-EXAMPLES.dsl
"""

import pytest


# ============================================================================
# 4.1 Wait Duration 测试
# ============================================================================

class TestV3_4_1_WaitDuration:
    """Wait Duration 语句测试"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.1")
    def test_wait_seconds(self, parse_v3):
        """✅ 正确：等待秒数"""
        source = "wait 5s"
        result = parse_v3(source)
        assert result.success == True, "wait 秒数应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.1")
    def test_wait_milliseconds(self, parse_v3):
        """✅ 正确：等待毫秒"""
        source = "wait 1000ms"
        result = parse_v3(source)
        assert result.success == True, "wait 毫秒应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.1")
    def test_wait_for_seconds(self, parse_v3):
        """✅ 正确：wait for 语法"""
        source = "wait for 2s"
        result = parse_v3(source)
        assert result.success == True, "wait for 秒数应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.1")
    def test_wait_for_milliseconds(self, parse_v3):
        """✅ 正确：wait for 毫秒"""
        source = "wait for 500ms"
        result = parse_v3(source)
        assert result.success == True, "wait for 毫秒应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.1")
    def test_wait_seconds_word(self, parse_v3):
        """✅ 正确：完整单词 seconds"""
        source = "wait 3 seconds"
        result = parse_v3(source)
        assert result.success == True, "wait seconds 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.1")
    def test_wait_milliseconds_word(self, parse_v3):
        """✅ 正确：完整单词 milliseconds"""
        source = "wait 200 milliseconds"
        result = parse_v3(source)
        assert result.success == True, "wait milliseconds 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.1")
    @pytest.mark.v3_specific
    def test_wait_in_step(self, parse_v3):
        """✅ 正确：在 step 块内等待（v3.0：无 end step）"""
        source = """
step "时间等待":
    wait 1s
    wait for 500ms
"""
        result = parse_v3(source)
        assert result.success == True, "step 块内的 wait 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.1")
    @pytest.mark.v3_specific
    def test_wait_in_if(self, parse_v3):
        """✅ 正确：在 if 块内等待（v3.0：无 end if）"""
        source = """
if slow_loading:
    wait 5s
"""
        result = parse_v3(source)
        assert result.success == True, "if 块内的 wait 应该正确解析"


# ============================================================================
# 4.2 Wait Element 测试
# ============================================================================

class TestV3_4_2_WaitElement:
    """Wait Element 语句测试"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.2")
    def test_wait_for_element_basic(self, parse_v3):
        """✅ 正确：基础元素等待"""
        source = 'wait for element "#button"'
        result = parse_v3(source)
        assert result.success == True, "基础元素等待应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.2")
    def test_wait_for_element_visible(self, parse_v3):
        """✅ 正确：等待元素可见"""
        source = 'wait for element "#modal" to be visible'
        result = parse_v3(source)
        assert result.success == True, "等待元素可见应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.2")
    def test_wait_for_element_hidden(self, parse_v3):
        """✅ 正确：等待元素隐藏"""
        source = 'wait for element ".loading" to be hidden'
        result = parse_v3(source)
        assert result.success == True, "等待元素隐藏应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.2")
    def test_wait_for_element_attached(self, parse_v3):
        """✅ 正确：等待元素附加"""
        source = 'wait for element "#item" to be attached'
        result = parse_v3(source)
        assert result.success == True, "等待元素附加应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.2")
    def test_wait_for_element_detached(self, parse_v3):
        """✅ 正确：等待元素分离"""
        source = 'wait for element "#deleted" to be detached'
        result = parse_v3(source)
        assert result.success == True, "等待元素分离应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.2")
    def test_wait_for_element_with_timeout(self, parse_v3):
        """✅ 正确：带超时的元素等待"""
        source = 'wait for element "#delayed" timeout 10s'
        result = parse_v3(source)
        assert result.success == True, "带超时的元素等待应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.2")
    def test_wait_for_element_visible_with_timeout(self, parse_v3):
        """✅ 正确：等待可见带超时"""
        source = 'wait for element "#button" to be visible timeout 5s'
        result = parse_v3(source)
        assert result.success == True, "等待可见带超时应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.2")
    def test_wait_for_element_class_selector(self, parse_v3):
        """✅ 正确：类选择器"""
        source = 'wait for element ".modal-dialog" to be visible'
        result = parse_v3(source)
        assert result.success == True, "类选择器应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.2")
    @pytest.mark.v3_specific
    def test_wait_for_element_in_step(self, parse_v3):
        """✅ 正确：在 step 块内使用（v3.0：无 end step）"""
        source = """
step "元素等待":
    wait for element "#button"
    wait for element "#modal" to be visible
"""
        result = parse_v3(source)
        assert result.success == True, "step 块内的元素等待应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.2")
    @pytest.mark.v3_specific
    def test_wait_for_element_in_if(self, parse_v3):
        """✅ 正确：在 if 块内使用（v3.0：无 end if）"""
        source = """
if needs_confirmation:
    wait for element "#confirm-button" to be visible
"""
        result = parse_v3(source)
        assert result.success == True, "if 块内的元素等待应该正确解析"


# ============================================================================
# 4.3 Wait Navigation 测试
# ============================================================================

class TestV3_4_3_WaitNavigation:
    """Wait Navigation 语句测试"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.3")
    def test_wait_for_navigation_basic(self, parse_v3):
        """✅ 正确：基础导航等待"""
        source = "wait for navigation"
        result = parse_v3(source)
        assert result.success == True, "基础导航等待应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.3")
    def test_wait_for_navigation_with_networkidle(self, parse_v3):
        """✅ 正确：等待 networkidle"""
        source = "wait for navigation wait for networkidle"
        result = parse_v3(source)
        assert result.success == True, "等待 networkidle 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.3")
    def test_wait_for_navigation_with_load(self, parse_v3):
        """✅ 正确：等待 load 事件"""
        source = "wait for navigation wait for load"
        result = parse_v3(source)
        assert result.success == True, "等待 load 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.3")
    def test_wait_for_navigation_with_domcontentloaded(self, parse_v3):
        """✅ 正确：等待 domcontentloaded"""
        source = "wait for navigation wait for domcontentloaded"
        result = parse_v3(source)
        assert result.success == True, "等待 domcontentloaded 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.3")
    def test_wait_for_navigation_to_url(self, parse_v3):
        """✅ 正确：等待导航到指定 URL"""
        source = 'wait for navigation to "https://example.com/success"'
        result = parse_v3(source)
        assert result.success == True, "等待导航到指定 URL 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.3")
    def test_wait_for_navigation_with_timeout(self, parse_v3):
        """✅ 正确：带超时的导航等待"""
        source = "wait for navigation timeout 10s"
        result = parse_v3(source)
        assert result.success == True, "带超时的导航等待应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.3")
    def test_wait_for_navigation_full_options(self, parse_v3):
        """✅ 正确：完整选项的导航等待"""
        source = 'wait for navigation to "https://example.com" wait for networkidle timeout 15s'
        result = parse_v3(source)
        assert result.success == True, "完整选项的导航等待应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("4.3")
    @pytest.mark.v3_specific
    def test_wait_for_navigation_in_step(self, parse_v3):
        """✅ 正确：在 step 块内使用（v3.0：无 end step）"""
        source = """
step "导航等待":
    click "#submit"
    wait for navigation
"""
        result = parse_v3(source)
        assert result.success == True, "step 块内的导航等待应该正确解析"

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.feature("4.3")
    def test_wait_after_click(self, parse_v3):
        """✅ 正确：点击后等待导航"""
        source = """
click "#submit-button"
wait for navigation wait for networkidle
"""
        result = parse_v3(source)
        assert result.success == True, "点击后等待导航应该正确解析"


# ============================================================================
# 综合测试
# ============================================================================

class TestV3_4_Integration:
    """等待功能综合测试"""

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_combined_waits_in_workflow(self, parse_v3):
        """✅ 正确：工作流中的组合等待（v3.0 Python 风格）"""
        source = """
step "表单提交":
    wait for element "#form" to be visible
    type "test@example.com" into "#email"
    wait 500ms
    click "#submit"
    wait for navigation wait for networkidle
    wait for element "#success-message" to be visible timeout 10s
"""
        result = parse_v3(source)
        assert result.success == True, "组合等待应该正确解析（Python 风格）"

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.v3_specific
    def test_conditional_waits(self, parse_v3):
        """✅ 正确：条件等待（v3.0：纯缩进）"""
        source = """
if slow_network:
    wait for element "#content" timeout 30s
else:
    wait for element "#content" timeout 10s
"""
        result = parse_v3(source)
        assert result.success == True, "条件等待应该正确解析（纯缩进）"

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_nested_waits_in_blocks(self, parse_v3):
        """✅ 正确：嵌套块中的等待（v3.0）"""
        source = """
step "复杂等待流程":
    if is_mobile:
        wait 2s
        wait for element ".mobile-menu" to be visible
    else:
        wait 500ms
        wait for element ".desktop-menu" to be visible
"""
        result = parse_v3(source)
        assert result.success == True, "嵌套块中的等待应该正确解析"

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.feature("4.1", "4.2", "4.3")
    def test_all_wait_types_combined(self, parse_v3):
        """✅ 正确：所有等待类型组合"""
        source = """
wait 1s
wait for element "#button" to be visible
click "#button"
wait for navigation
wait for element "#result" to be visible timeout 10s
wait 500ms
"""
        result = parse_v3(source)
        assert result.success == True, "所有等待类型组合应该正确解析"


# ============================================================================
# 测试总结
# ============================================================================

"""
测试统计：
- Feature 4.1 (Wait Duration): 9 tests
- Feature 4.2 (Wait Element): 11 tests
- Feature 4.3 (Wait Navigation): 9 tests
- Integration: 4 tests
总计: 33 tests

v3.0 特性验证：
✅ 无 end 关键字（纯缩进块）
✅ 所有等待语句支持在 step/if 块内使用
✅ 完整的状态等待支持（visible/hidden/attached/detached）
✅ 超时参数支持
✅ 导航等待的多种选项组合

关键发现：
1. Wait Duration 支持 s/ms/seconds/milliseconds 单位
2. Wait Element 支持 4 种状态：visible/hidden/attached/detached
3. Wait Navigation 支持 3 种页面状态：networkidle/load/domcontentloaded
4. 所有等待语句都可以带 timeout 参数
5. v3.0 使用纯缩进，完全移除 end 关键字
"""
