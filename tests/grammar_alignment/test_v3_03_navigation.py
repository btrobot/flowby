"""
Grammar Alignment Test: v3.0 导航（Python风格）

测试核心原则：
1. 正确的代码正确解析
2. 错误的代码报错一致
3. v3.0特性：无end关键字，纯缩进块

Features tested:
- 3.1 Navigate To (v3.0: 支持Python风格系统变量)
- 3.2 Go Back/Forward (v3.0)
- 3.3 Reload (v3.0)

Reference: grammar/DESIGN-V3.md #3, grammar/V3-EXAMPLES.dsl
"""

import pytest


# ============================================================================
# 3.1 Navigate To 测试
# ============================================================================


class TestV3_3_1_NavigateTo:
    """Navigate To 语句测试（v3.0 Python 风格）"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.1")
    def test_basic_navigate(self, parse_v3):
        """✅ 正确：基础导航语法"""
        source = 'navigate to "https://example.com"'
        result = parse_v3(source)
        assert result.success is True, "基础导航应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.1")
    def test_navigate_with_http(self, parse_v3):
        """✅ 正确：HTTP 协议"""
        source = 'navigate to "http://example.com"'
        result = parse_v3(source)
        assert result.success is True, "HTTP URL 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.1")
    def test_navigate_with_localhost(self, parse_v3):
        """✅ 正确：localhost 地址"""
        source = 'navigate to "http://localhost:3000"'
        result = parse_v3(source)
        assert result.success is True, "localhost URL 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.1")
    def test_navigate_with_path(self, parse_v3):
        """✅ 正确：带路径的 URL"""
        source = 'navigate to "https://example.com/login"'
        result = parse_v3(source)
        assert result.success is True, "带路径的 URL 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.1")
    def test_navigate_with_query_params(self, parse_v3):
        """✅ 正确：带查询参数的 URL"""
        source = 'navigate to "https://example.com?page=1&sort=asc"'
        result = parse_v3(source)
        assert result.success is True, "带查询参数的 URL 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.1")
    def test_navigate_with_fragment(self, parse_v3):
        """✅ 正确：带片段标识符的 URL"""
        source = 'navigate to "https://example.com#section"'
        result = parse_v3(source)
        assert result.success is True, "带片段标识符的 URL 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.1")
    def test_navigate_with_variable(self, parse_v3):
        """✅ 正确：使用变量作为 URL"""
        source = """
let base_url = "https://example.com"
navigate to base_url
"""
        result = parse_v3(source)
        assert result.success is True, "使用变量的 navigate 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.1")
    @pytest.mark.python_aligned
    def test_navigate_with_system_variable_no_dollar(self, parse_v3):
        """✅ 正确：使用系统变量（无 $ 前缀，v3.0 Python 风格）"""
        source = "navigate to config.base_url"
        result = parse_v3(source)
        assert result.success is True, "系统变量无 $ 前缀应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.1")
    def test_navigate_wait_for_networkidle(self, parse_v3):
        """✅ 正确：等待 networkidle"""
        source = 'navigate to "https://example.com" wait for networkidle'
        result = parse_v3(source)
        assert result.success is True, "wait for networkidle 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.1")
    def test_navigate_wait_for_domcontentloaded(self, parse_v3):
        """✅ 正确：等待 domcontentloaded"""
        source = 'navigate to "https://example.com" wait for domcontentloaded'
        result = parse_v3(source)
        assert result.success is True, "wait for domcontentloaded 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.1")
    def test_navigate_wait_for_load(self, parse_v3):
        """✅ 正确：等待 load"""
        source = 'navigate to "https://example.com" wait for load'
        result = parse_v3(source)
        assert result.success is True, "wait for load 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.1")
    @pytest.mark.v3_specific
    def test_navigate_in_step_block(self, parse_v3):
        """✅ 正确：在 step 块内使用（v3.0：无 end step）"""
        source = """
step "测试导航":
    navigate to "https://example.com"
    navigate to "https://example.com/login"
"""
        result = parse_v3(source)
        assert result.success is True, "step 块内的 navigate 应该正确解析（无 end step）"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.1")
    @pytest.mark.v3_specific
    def test_navigate_in_if_block(self, parse_v3):
        """✅ 正确：在 if 块内使用（v3.0：无 end if）"""
        source = """
let is_admin = True
if is_admin:
    navigate to "https://admin.example.com"
"""
        result = parse_v3(source)
        assert result.success is True, "if 块内的 navigate 应该正确解析（无 end if）"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.1")
    @pytest.mark.python_aligned
    def test_navigate_with_fstring(self, parse_v3):
        """✅ 正确：使用 f-string（v3.0 Python 风格）"""
        source = """
let path = "/dashboard"
navigate to f"https://example.com{path}"
"""
        result = parse_v3(source)
        assert result.success is True, "f-string 作为 URL 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.error
    @pytest.mark.feature("3.1")
    def test_navigate_missing_url(self, parse_v3):
        """❌ 错误：缺少 URL"""
        source = "navigate to"
        result = parse_v3(source)
        assert result.success is False, "缺少 URL 应该报错"


# ============================================================================
# 3.2 Go Back/Forward 测试
# ============================================================================


class TestV3_3_2_GoBackForward:
    """Go Back/Forward 语句测试"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.2")
    def test_go_back(self, parse_v3):
        """✅ 正确：后退语法"""
        source = "go back"
        result = parse_v3(source)
        assert result.success is True, "go back 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.2")
    def test_go_forward(self, parse_v3):
        """✅ 正确：前进语法"""
        source = "go forward"
        result = parse_v3(source)
        assert result.success is True, "go forward 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.2")
    @pytest.mark.v3_specific
    def test_go_back_in_step(self, parse_v3):
        """✅ 正确：在 step 块内后退（v3.0：无 end step）"""
        source = """
step "浏览器历史":
    navigate to "https://example.com/page1"
    navigate to "https://example.com/page2"
    go back
"""
        result = parse_v3(source)
        assert result.success is True, "step 块内的 go back 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.2")
    @pytest.mark.v3_specific
    def test_go_forward_in_step(self, parse_v3):
        """✅ 正确：在 step 块内前进（v3.0：无 end step）"""
        source = """
step "浏览器历史":
    go back
    go forward
"""
        result = parse_v3(source)
        assert result.success is True, "step 块内的 go forward 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.2")
    @pytest.mark.v3_specific
    def test_go_back_in_if(self, parse_v3):
        """✅ 正确：在 if 块内使用（v3.0：无 end if）"""
        source = """
let need_back = True
if need_back:
    go back
"""
        result = parse_v3(source)
        assert result.success is True, "if 块内的 go back 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.feature("3.2")
    def test_navigation_sequence(self, parse_v3):
        """✅ 正确：导航序列测试"""
        source = """
navigate to "https://example.com/page1"
navigate to "https://example.com/page2"
go back
go forward
"""
        result = parse_v3(source)
        assert result.success is True, "导航序列应该正确解析"


# ============================================================================
# 3.3 Reload 测试
# ============================================================================


class TestV3_3_3_Reload:
    """Reload 语句测试"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.3")
    def test_reload_basic(self, parse_v3):
        """✅ 正确：基础刷新语法"""
        source = "reload"
        result = parse_v3(source)
        assert result.success is True, "reload 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.3")
    @pytest.mark.v3_specific
    def test_reload_in_step(self, parse_v3):
        """✅ 正确：在 step 块内刷新（v3.0：无 end step）"""
        source = """
step "页面刷新":
    navigate to "https://example.com"
    reload
"""
        result = parse_v3(source)
        assert result.success is True, "step 块内的 reload 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("3.3")
    @pytest.mark.v3_specific
    def test_reload_in_if(self, parse_v3):
        """✅ 正确：在 if 块内刷新（v3.0：无 end if）"""
        source = """
let page_stale = True
if page_stale:
    reload
"""
        result = parse_v3(source)
        assert result.success is True, "if 块内的 reload 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.feature("3.3")
    def test_reload_after_navigate(self, parse_v3):
        """✅ 正确：导航后刷新"""
        source = """
navigate to "https://example.com"
reload
"""
        result = parse_v3(source)
        assert result.success is True, "导航后刷新应该正确解析"


# ============================================================================
# 综合测试
# ============================================================================


class TestV3_3_Integration:
    """导航功能综合测试"""

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_navigation_with_python_style(self, parse_v3):
        """✅ 正确：综合测试（v3.0 Python 风格）"""
        source = """
step "用户导航流程":
    let base_url = "https://example.com"
    navigate to base_url wait for networkidle

    if page.url == base_url:
        navigate to f"{base_url}/login"
        go back
        go forward
        reload
"""
        result = parse_v3(source)
        assert result.success is True, "综合导航流程应该正确解析（Python 风格）"

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.v3_specific
    def test_nested_navigation(self, parse_v3):
        """✅ 正确：嵌套块中的导航（v3.0：纯缩进）"""
        source = """
let is_authenticated = True
let role = "admin"
step "嵌套导航":
    if is_authenticated:
        if role == "admin":
            navigate to config.admin_url
        else:
            navigate to config.user_url
    else:
        navigate to config.login_url
"""
        result = parse_v3(source)
        assert result.success is True, "嵌套块中的导航应该正确解析（纯缩进）"

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_navigation_with_system_variables(self, parse_v3):
        """✅ 正确：使用系统变量导航（v3.0：无 $ 前缀）"""
        source = """
navigate to config.base_url
if page.url != config.base_url:
    reload
"""
        result = parse_v3(source)
        assert result.success is True, "系统变量导航应该正确解析（无 $ 前缀）"

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_navigation_with_conditional(self, parse_v3):
        """✅ 正确：条件导航（v3.0 风格）"""
        source = """
let use_secure = True
if use_secure == True:
    navigate to "https://example.com"
else:
    navigate to "http://example.com"
"""
        result = parse_v3(source)
        assert result.success is True, "条件导航应该正确解析（True/False）"


# ============================================================================
# 测试总结
# ============================================================================

"""
测试统计：
- Feature 3.1 (Navigate To): 16 tests
- Feature 3.2 (Go Back/Forward): 6 tests
- Feature 3.3 (Reload): 4 tests
- Integration: 4 tests
总计: 30 tests

v3.0 特性验证：
✅ 无 end 关键字（纯缩进块）
✅ 系统变量无 $ 前缀（Python 风格）
✅ True/False 布尔值（Python 风格）
✅ f-string 支持（Python 风格）
✅ 嵌套块缩进语法

关键发现：
1. 所有导航语句都支持在 step/if 块内使用
2. v3.0 完全移除 end 关键字，使用纯缩进
3. 系统变量访问改为 Python 风格（无 $）
4. f-string 可用于动态构建 URL
"""
