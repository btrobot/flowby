"""
Grammar Alignment Test: v3.0 断言（Python风格）

Features tested:
- 7.x Assert Expression (v2.0通用表达式断言)

Reference: grammar/DESIGN-V3.md #7, grammar/V3-EXAMPLES.dsl
"""

import pytest


class TestV3_7_AssertExpression:
    """Assert 表达式断言测试（v2.0实现）"""

    @pytest.mark.v3
    @pytest.mark.feature("7.x")
    def test_assert_basic(self, parse_v3):
        """✅ 正确：基础断言"""
        source = "assert True"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("7.x")
    @pytest.mark.python_aligned
    def test_assert_true_false(self, parse_v3):
        """✅ 正确：True/False 断言（Python 风格）"""
        source = """
assert True
assert False == False
"""
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("7.x")
    def test_assert_comparison(self, parse_v3):
        """✅ 正确：比较表达式断言"""
        source = 'assert score >= 60'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("7.x")
    @pytest.mark.python_aligned
    def test_assert_none(self, parse_v3):
        """✅ 正确：None 断言（Python 风格）"""
        source = "assert data != None"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("7.x")
    @pytest.mark.python_aligned
    def test_assert_system_variable(self, parse_v3):
        """✅ 正确：系统变量断言（无 $ 前缀）"""
        source = 'assert page.url == "https://example.com"'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("7.x")
    def test_assert_with_message(self, parse_v3):
        """✅ 正确：带消息的断言"""
        source = 'assert score >= 60, "分数不及格"'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("7.x")
    def test_assert_logical_and(self, parse_v3):
        """✅ 正确：逻辑 AND 断言"""
        source = "assert score >= 90 and attendance > 80"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("7.x")
    def test_assert_logical_or(self, parse_v3):
        """✅ 正确：逻辑 OR 断言"""
        source = "assert is_admin or is_moderator"
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("7.x")
    def test_assert_complex_expression(self, parse_v3):
        """✅ 正确：复杂表达式断言"""
        source = 'assert (score >= 90 and attendance > 80) or extra_credit == True'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("7.x")
    @pytest.mark.v3_specific
    def test_assert_in_step(self, parse_v3):
        """✅ 正确：step 块内（无 end step）"""
        source = """
step "验证结果":
    assert page.url contains "/success"
    assert element_count > 0
"""
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("7.x")
    @pytest.mark.v3_specific
    def test_assert_in_if(self, parse_v3):
        """✅ 正确：if 块内（无 end if）"""
        source = """
if needs_verification:
    assert verification_code != None
"""
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_assert_workflow(self, parse_v3):
        """✅ 正确：断言工作流（v3.0 Python 风格）"""
        source = """
step "登录验证":
    navigate to config.login_url
    type "admin" into "#username"
    click "#submit"
    wait for navigation
    assert page.url == config.dashboard_url
    assert page.title contains "Dashboard"
"""
        result = parse_v3(source)
        assert result.success == True


"""
测试统计：12 tests
v3.0特性验证：
✅ True/False/None（Python风格）
✅ 系统变量无$前缀
✅ 无end关键字
✅ 逻辑运算符：and/or/not
"""
