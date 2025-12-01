"""
Grammar Alignment Test: v3.0 工具（Python风格）

Features tested:
- 10.1 Log (支持 f-string)
- 10.2 Screenshot

Reference: grammar/DESIGN-V3.md #10, grammar/V3-EXAMPLES.dsl
"""

import pytest


class TestV3_10_1_Log:
    """Log 语句测试"""

    @pytest.mark.v3
    @pytest.mark.feature("10.1")
    def test_log_plain_string(self, parse_v3):
        """✅ 正确：普通字符串日志"""
        source = 'log "开始测试"'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("10.1")
    @pytest.mark.python_aligned
    def test_log_fstring(self, parse_v3):
        """✅ 正确：f-string 日志（v3.0 Python 风格）"""
        source = 'let username = "admin"\nlog f"用户名: {username}"'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("10.1")
    @pytest.mark.python_aligned
    def test_log_fstring_multiple_vars(self, parse_v3):
        """✅ 正确：多变量 f-string"""
        source = 'let score = 95\nlet grade = "A"\nlog f"分数: {score}, 等级: {grade}"'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("10.1")
    @pytest.mark.python_aligned
    def test_log_fstring_expression(self, parse_v3):
        """✅ 正确：表达式 f-string"""
        source = 'let x = 5\nlet y = 3\nlog f"计算结果: {x + y * 2}"'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("10.1")
    @pytest.mark.python_aligned
    def test_log_system_variable(self, parse_v3):
        """✅ 正确：系统变量日志（无 $ 前缀）"""
        source = 'log f"当前URL: {page.url}"'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("10.1")
    @pytest.mark.v3_specific
    def test_log_in_step(self, parse_v3):
        """✅ 正确：step 块内（无 end step）"""
        source = """
let username = "admin"
step "日志输出":
    log "步骤开始"
    log f"用户: {username}"
    log "步骤结束"
"""
        result = parse_v3(source)
        assert result.success == True


class TestV3_10_2_Screenshot:
    """Screenshot 语句测试"""

    @pytest.mark.v3
    @pytest.mark.feature("10.2")
    def test_screenshot_basic(self, parse_v3):
        """✅ 正确：基础截图"""
        source = "screenshot"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("10.2")
    def test_screenshot_fullpage(self, parse_v3):
        """✅ 正确：全页面截图"""
        source = "screenshot fullpage"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("10.2")
    def test_screenshot_with_name(self, parse_v3):
        """✅ 正确：命名截图"""
        source = 'screenshot as "homepage"'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("10.2")
    def test_screenshot_of_element(self, parse_v3):
        """✅ 正确：元素截图"""
        source = 'screenshot of "#main-content"'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("10.2")
    def test_screenshot_of_element_named(self, parse_v3):
        """✅ 正确：命名元素截图"""
        source = 'screenshot of ".modal" as "modal-view"'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("10.2")
    def test_screenshot_fullpage_named(self, parse_v3):
        """✅ 正确：命名全页面截图"""
        source = 'screenshot of "body" fullpage as "full-page"'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("10.2")
    @pytest.mark.v3_specific
    def test_screenshot_in_step(self, parse_v3):
        """✅ 正确：step 块内（无 end step）"""
        source = """
step "截图记录":
    screenshot as "before"
    click "#submit"
    screenshot as "after"
"""
        result = parse_v3(source)
        assert result.success == True


class TestV3_10_Integration:
    """工具功能综合测试"""

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_log_and_screenshot_workflow(self, parse_v3):
        """✅ 正确：日志+截图工作流（v3.0 Python 风格）"""
        source = """
let test_name = "homepage"
step "测试流程":
    log f"开始测试: {test_name}"
    screenshot as "start"
    navigate to config.base_url
    log f"URL: {page.url}"
    screenshot fullpage as "loaded"
    log "测试完成"
"""
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_conditional_logging(self, parse_v3):
        """✅ 正确：条件日志（True/False Python 风格）"""
        source = """
let debug = True
let details = "debug info"
if debug == True:
    log f"调试信息: {details}"
    screenshot as "debug"
"""
        result = parse_v3(source)
        assert result.success == True


"""
测试统计：
- Feature 10.1 (Log): 6 tests
- Feature 10.2 (Screenshot): 7 tests
- Integration: 2 tests
总计: 15 tests

v3.0特性验证：
✅ f-string 完整支持（Python风格）
✅ 系统变量无$前缀
✅ True/False（Python风格）
✅ 无 end 关键字
"""
