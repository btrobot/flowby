"""
Grammar Alignment Test: v3.0 数据提取（Python风格）

Features tested:
- 9.1 Extract (text/value/attr/pattern)

Reference: grammar/DESIGN-V3.md #9, grammar/V3-EXAMPLES.dsl
"""

import pytest


class TestV3_9_Extract:
    """Extract 数据提取测试"""

    @pytest.mark.v3
    @pytest.mark.feature("9.1")
    def test_extract_text(self, parse_v3):
        """✅ 正确：提取文本"""
        source = 'extract text from "#title" into page_title'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("9.1")
    def test_extract_value(self, parse_v3):
        """✅ 正确：提取值"""
        source = 'extract value from "#input" into input_value'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("9.1")
    def test_extract_attr_href(self, parse_v3):
        """✅ 正确：提取 href 属性"""
        source = 'extract attr "href" from "#link" into link_url'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("9.1")
    def test_extract_attr_src(self, parse_v3):
        """✅ 正确：提取 src 属性"""
        source = 'extract attr "src" from "img.logo" into logo_src'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("9.1")
    def test_extract_pattern(self, parse_v3):
        """✅ 正确：正则提取"""
        source = 'extract text from "#code" pattern "\d{6}" into verification_code'
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.feature("9.1")
    @pytest.mark.v3_specific
    def test_extract_in_step(self, parse_v3):
        """✅ 正确：step 块内（无 end step）"""
        source = """
step "数据提取":
    extract text from "#title" into page_title
    extract value from "#input" into input_value
"""
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v3
    @pytest.mark.integration
    @pytest.mark.python_aligned
    def test_extract_and_use(self, parse_v3):
        """✅ 正确：提取并使用（v3.0 f-string）"""
        source = """
step "提取并验证":
    extract text from "#username" into display_name
    log f"当前用户: {display_name}"
    assert display_name != None
"""
        result = parse_v3(source)
        assert result.success == True


"""
测试统计：7 tests
v3.0特性验证：
✅ 4种提取类型：text/value/attr/pattern
✅ 无 end 关键字
✅ 支持 f-string 使用提取结果
✅ None（Python风格）
"""
