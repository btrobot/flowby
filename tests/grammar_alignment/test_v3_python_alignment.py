"""
Grammar Alignment Test: v3.0 Python对齐验证

测试核心原则：
1. 正确的代码正确解析
2. 错误的代码报错一致

Features tested:
- Python布尔值: True/False (v3.0)
- Python None: None (v3.0)
- 系统变量无$前缀: page.url (v3.0)
- f-string显式插值: f"text {x}" (v3.0)
- 无end关键字: 纯缩进 (v3.0)
- 三引号块注释: \"\"\" \"\"\" (v3.0)

Reference: grammar/DESIGN-V3.md, grammar/PYTHON-ALIGNMENT-REVIEW.md
"""

import pytest


# ============================================================================
# 1. 布尔字面量 Python 对齐测试
# ============================================================================


class TestV3_PythonAlignment_Boolean:
    """布尔字面量：True/False（Python风格）"""

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_true_capitalized_correct(self, parse_v3):
        """✅ 正确：True（首字母大写）"""
        # 正确的代码应该正确解析
        source = "let active = True"
        result = parse_v3(source)
        assert result.success is True, "True 应该被正确解析"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_false_capitalized_correct(self, parse_v3):
        """✅ 正确：False（首字母大写）"""
        source = "let verified = False"
        result = parse_v3(source)
        assert result.success is True, "False 应该被正确解析"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_lowercase_true_error(self, parse_v3):
        """❌ 错误：true（小写）应报错"""
        # 错误的代码应该报错
        source = "let active = true"
        result = parse_v3(source)
        assert result.success is False, "小写 true 应该报错"
        # 错误提示应该一致且清晰
        assert "True" in result.error or "布尔值" in result.error, "错误提示应提及 True 或布尔值"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_lowercase_false_error(self, parse_v3):
        """❌ 错误：false（小写）应报错"""
        source = "let verified = false"
        result = parse_v3(source)
        assert result.success is False, "小写 false 应该报错"
        assert "False" in result.error or "布尔值" in result.error, "错误提示应提及 False 或布尔值"


# ============================================================================
# 2. None 字面量 Python 对齐测试
# ============================================================================


class TestV3_PythonAlignment_None:
    """None 字面量：None（Python风格）"""

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_none_capitalized_correct(self, parse_v3):
        """✅ 正确：None（首字母大写）"""
        source = "let data = None"
        result = parse_v3(source)
        assert result.success is True, "None 应该被正确解析"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_null_keyword_error(self, parse_v3):
        """❌ 错误：null 关键字应报错"""
        source = "let data = null"
        result = parse_v3(source)
        assert result.success is False, "null 应该报错"
        assert (
            "None" in result.error or "null" in result.error.lower()
        ), "错误提示应提及 None 或 null"


# ============================================================================
# 3. 系统变量无$前缀 Python 对齐测试
# ============================================================================


class TestV3_PythonAlignment_SystemVariables:
    """系统变量：无$前缀（Python全局对象风格）"""

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_page_url_no_dollar_correct(self, parse_v3):
        """✅ 正确：page.url（无$前缀）"""
        source = 'assert page.url == "https://example.com"'
        result = parse_v3(source)
        assert result.success is True, "page.url 应该被正确解析"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_env_no_dollar_correct(self, parse_v3):
        """✅ 正确：env.API_KEY（无$前缀）"""
        source = "log env.API_KEY"
        result = parse_v3(source)
        assert result.success is True, "env.API_KEY 应该被正确解析"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_dollar_prefix_error(self, parse_v3):
        """❌ 错误：$page.url 应报错"""
        source = 'assert $page.url == "test"'
        result = parse_v3(source)
        assert result.success is False, "$page.url 应该报错"
        assert "$" in result.error or "page.url" in result.error, "错误提示应提及 $ 前缀问题"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_dollar_env_error(self, parse_v3):
        """❌ 错误：$env.API_KEY 应报错"""
        source = "log $env.API_KEY"
        result = parse_v3(source)
        assert result.success is False, "$env.API_KEY 应该报错"


# ============================================================================
# 4. f-string 显式插值 Python 对齐测试
# ============================================================================


class TestV3_PythonAlignment_FString:
    """f-string：显式插值（Python风格）"""

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_fstring_interpolation_correct(self, parse_v3):
        """✅ 正确：f-string 插值"""
        source = 'let count = 10\nlog f"Count: {count}"'
        result = parse_v3(source)
        assert result.success is True, "f-string 应该被正确解析"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_plain_string_no_interpolation_correct(self, parse_v3):
        """✅ 正确：普通字符串不插值"""
        # 这应该被解析为字面量字符串 "Count: {count}"
        source = 'let count = 10\nlog "Count: {count}"'
        result = parse_v3(source)
        assert result.success is True, "普通字符串应该被正确解析（作为字面量）"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_auto_interpolation_disabled(self, parse_v3):
        """✅ 验证：自动插值已禁用"""
        # v2.0 会自动插值，v3.0 不会
        source = 'let x = 5\nlog "Value: {x}"'
        result = parse_v3(source)
        # 应该成功解析，但 {x} 是字面量而非插值
        assert result.success is True
        # 进一步验证：{x} 没有被当作变量引用
        # （这需要执行层面的验证，暂时只验证解析成功）


# ============================================================================
# 5. 无 end 关键字 Python 对齐测试
# ============================================================================


class TestV3_PythonAlignment_NoEndKeyword:
    """纯缩进：无 end 关键字（Python风格）"""

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_if_without_end_correct(self, parse_v3):
        """✅ 正确：if 块无 end if"""
        source = """
let x = 1
if x > 0:
    let y = 1
"""
        result = parse_v3(source)
        assert result.success is True, "无 end if 的 if 块应该正确解析"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_step_without_end_correct(self, parse_v3):
        """✅ 正确：step 块无 end step"""
        source = """
step "test":
    let x = 1
"""
        result = parse_v3(source)
        assert result.success is True, "无 end step 的 step 块应该正确解析"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_end_if_keyword_error(self, parse_v3):
        """❌ 错误：end if 关键字应报错"""
        source = """
let x = 1
if x > 0:
    let y = 1
end if
"""
        result = parse_v3(source)
        assert result.success is False, "end if 应该报错"
        assert (
            "end" in result.error.lower() or "缩进" in result.error
        ), "错误提示应提及 end 关键字或缩进"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_end_step_keyword_error(self, parse_v3):
        """❌ 错误：end step 关键字应报错"""
        source = """
step "test":
    let x = 1
end step
"""
        result = parse_v3(source)
        assert result.success is False, "end step 应该报错"


# ============================================================================
# 6. 三引号块注释 Python 对齐测试
# ============================================================================


class TestV3_PythonAlignment_BlockComment:
    """块注释：三引号（Python风格）"""

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_triple_quote_comment_correct(self, parse_v3):
        """✅ 正确：三引号块注释"""
        source = '''
"""
这是块注释
跨越多行
"""
let x = 1
'''
        result = parse_v3(source)
        assert result.success is True, "三引号块注释应该正确解析"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_c_style_comment_error(self, parse_v3):
        """❌ 错误：C 风格注释应报错"""
        source = "/* comment */ let x = 1"
        result = parse_v3(source)
        assert result.success is False, "C 风格注释应该报错"
        # 错误消息应提到 SLASH 或 / （实际报错："未知的语句开始: SLASH"）
        assert (
            "SLASH" in result.error or "/" in result.error
        ), f"错误提示应提及 SLASH 或 /，实际：{result.error}"


# ============================================================================
# 7. 综合 Python 对齐测试
# ============================================================================


class TestV3_PythonAlignment_Comprehensive:
    """综合测试：多个 Python 对齐特性组合"""

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    @pytest.mark.parametrize(
        "source,should_pass",
        [
            # ✅ 正确的 Python 风格代码
            ("let active = True", True),
            ("let data = None", True),
            ('let user = {name: "Alice"}\nlog f"User: {user.name}"', True),
            ('assert page.url == "test"', True),
            ("let x = 1\nif x > 0:\n    let y = 1", True),
            # ❌ v2.0 风格（应报错）
            ("let active = true", False),  # 小写布尔值
            ("let data = null", False),  # null 而非 None
            ("log $page.url", False),  # $ 前缀
            ("let x = 1\nif x > 0:\n    let y = 1\nend if", False),  # end 关键字
        ],
    )
    def test_python_alignment_consistency(self, parse_v3, source, should_pass):
        """验证 Python 对齐的一致性"""
        result = parse_v3(source)

        if should_pass:
            assert result.success is True, f"Python 风格代码应该解析成功：{source}"
        else:
            assert result.success is False, f"非 Python 风格代码应该报错：{source}"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.syntax
    def test_complex_python_style_code(self, parse_v3):
        """✅ 正确：复杂的 Python 风格代码"""
        source = '''
step "用户登录":
    """登录流程测试"""

    let email = None
    let success = False

    if email == None:
        log "邮箱为空"
        success = False
    else:
        navigate to page.url
        type email into "#email"
        success = True

    assert success == True
'''
        result = parse_v3(source)
        assert result.success is True, "复杂 Python 风格代码应该正确解析"


# ============================================================================
# 8. 错误提示一致性测试
# ============================================================== ==============


class TestV3_ErrorConsistency:
    """验证错误提示的一致性"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.parametrize(
        "source,error_keyword",
        [
            ("let x = true", "True"),  # 应提示使用 True
            ("let x = null", "None"),  # 应提示使用 None
            ("log $page.url", "$"),  # 应提示 $ 前缀错误
            ("let x = 1\nif x:\n    let y = 1\nend if", "end"),  # 应提示 end 关键字错误
        ],
    )
    def test_error_messages_contain_hint(self, parse_v3, source, error_keyword):
        """验证错误提示包含关键提示词"""
        result = parse_v3(source)
        assert result.success is False, f"代码应该报错：{source}"
        assert (
            error_keyword in result.error or error_keyword.lower() in result.error.lower()
        ), f"错误提示应包含 '{error_keyword}'，实际：{result.error}"
