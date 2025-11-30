"""
Grammar Alignment Test: v3.0 系统变量（无$前缀）

⭐ v3.0 核心变更：系统变量作为内置全局对象，无 $ 前缀

测试核心原则：
1. 正确的代码（无$前缀）正确解析
2. 错误的代码（有$前缀）报错一致

Features tested:
- page.* (v3.0: 无 $ 前缀)
- env.* (v3.0: 无 $ 前缀)
- browser.* (v3.0: 无 $ 前缀)
- context.* (v3.0: 无 $ 前缀)
- config.* (v3.0: 无 $ 前缀)

Reference: grammar/DESIGN-V3.md, grammar/PYTHON-ALIGNMENT-REVIEW.md
"""

import pytest


# ============================================================================
# page 命名空间测试（无 $ 前缀）
# ============================================================================

class TestV3_SystemVariables_Page:
    """page 命名空间：页面相关变量（无 $ 前缀）"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_page_url(self, parse_v3):
        """✅ 正确：page.url（无 $ 前缀）"""
        source = 'log f"当前URL: {page.url}"'
        result = parse_v3(source)
        assert result.success == True, "page.url 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_page_title(self, parse_v3):
        """✅ 正确：page.title（无 $ 前缀）"""
        source = 'log f"页面标题: {page.title}"'
        result = parse_v3(source)
        assert result.success == True, "page.title 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_page_origin(self, parse_v3):
        """✅ 正确：page.origin（无 $ 前缀）"""
        source = 'log page.origin'
        result = parse_v3(source)
        assert result.success == True, "page.origin 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_page_in_condition(self, parse_v3):
        """✅ 正确：条件中使用 page 变量"""
        source = '''
if page.url == "https://example.com":
    log "正确的页面"
'''
        result = parse_v3(source)
        assert result.success == True, "条件中的 page 变量应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_page_with_dollar_error(self, parse_v3):
        """❌ 错误：$page.url 应报错"""
        source = 'log $page.url'
        result = parse_v3(source)
        assert result.success == False, "$page.url 应该报错"
        assert "$" in result.error or "page.url" in result.error, \
            f"错误提示应提及 $ 前缀或 page.url，实际：{result.error}"


# ============================================================================
# env 命名空间测试（无 $ 前缀）
# ============================================================================

class TestV3_SystemVariables_Env:
    """env 命名空间：环境变量（无 $ 前缀）"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_env_variable(self, parse_v3):
        """✅ 正确：env.API_KEY（无 $ 前缀）"""
        source = 'log f"API Key: {env.API_KEY}"'
        result = parse_v3(source)
        assert result.success == True, "env.API_KEY 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_env_multiple_vars(self, parse_v3):
        """✅ 正确：多个 env 变量"""
        source = '''
let host = env.DB_HOST
let port = env.DB_PORT
let user = env.DB_USER
'''
        result = parse_v3(source)
        assert result.success == True, "多个 env 变量应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_env_in_condition(self, parse_v3):
        """✅ 正确：条件中的 env 变量"""
        source = '''
if env.DEBUG == "true":
    log "调试模式"
'''
        result = parse_v3(source)
        assert result.success == True, "条件中的 env 变量应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_env_with_dollar_error(self, parse_v3):
        """❌ 错误：$env.API_KEY 应报错"""
        source = 'log $env.API_KEY'
        result = parse_v3(source)
        assert result.success == False, "$env.API_KEY 应该报错"


# ============================================================================
# browser 命名空间测试（无 $ 前缀）
# ============================================================================

class TestV3_SystemVariables_Browser:
    """browser 命名空间：浏览器信息（无 $ 前缀）"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_browser_name(self, parse_v3):
        """✅ 正确：browser.name（无 $ 前缀）"""
        source = 'log f"浏览器: {browser.name}"'
        result = parse_v3(source)
        assert result.success == True, "browser.name 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_browser_version(self, parse_v3):
        """✅ 正确：browser.version（无 $ 前缀）"""
        source = 'log browser.version'
        result = parse_v3(source)
        assert result.success == True, "browser.version 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_browser_with_dollar_error(self, parse_v3):
        """❌ 错误：$browser.name 应报错"""
        source = 'log $browser.name'
        result = parse_v3(source)
        assert result.success == False, "$browser.name 应该报错"


# ============================================================================
# context 命名空间测试（无 $ 前缀）
# ============================================================================

class TestV3_SystemVariables_Context:
    """context 命名空间：执行上下文（无 $ 前缀）"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_context_task_id(self, parse_v3):
        """✅ 正确：context.task_id（无 $ 前缀）"""
        source = 'log f"任务ID: {context.task_id}"'
        result = parse_v3(source)
        assert result.success == True, "context.task_id 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_context_execution_id(self, parse_v3):
        """✅ 正确：context.execution_id（无 $ 前缀）"""
        source = 'log context.execution_id'
        result = parse_v3(source)
        assert result.success == True, "context.execution_id 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_context_start_time(self, parse_v3):
        """✅ 正确：context.start_time（无 $ 前缀）"""
        source = 'let start = context.start_time'
        result = parse_v3(source)
        assert result.success == True, "context.start_time 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_context_with_dollar_error(self, parse_v3):
        """❌ 错误：$context.task_id 应报错"""
        source = 'log $context.task_id'
        result = parse_v3(source)
        assert result.success == False, "$context.task_id 应该报错"


# ============================================================================
# config 命名空间测试（无 $ 前缀）
# ============================================================================

class TestV3_SystemVariables_Config:
    """config 命名空间：配置变量（无 $ 前缀）"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_config_variable(self, parse_v3):
        """✅ 正确：config.base_url（无 $ 前缀）"""
        source = 'navigate to config.base_url'
        result = parse_v3(source)
        assert result.success == True, "config.base_url 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_config_in_fstring(self, parse_v3):
        """✅ 正确：f-string 中的 config 变量"""
        source = 'log f"Base URL: {config.base_url}"'
        result = parse_v3(source)
        assert result.success == True, "f-string 中的 config 变量应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    @pytest.mark.feature("system-var")
    def test_config_with_dollar_error(self, parse_v3):
        """❌ 错误：$config.base_url 应报错"""
        source = 'log $config.base_url'
        result = parse_v3(source)
        assert result.success == False, "$config.base_url 应该报错"


# ============================================================================
# 系统变量综合测试
# ============================================================================

class TestV3_SystemVariables_Combined:
    """系统变量综合使用测试"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_multiple_namespaces(self, parse_v3):
        """✅ 正确：多个命名空间组合使用"""
        source = '''
step "系统信息":
    log f"当前URL: {page.url}"
    log f"浏览器: {browser.name}"
    log f"任务ID: {context.task_id}"
    log f"API Key: {env.API_KEY}"
    log f"配置: {config.base_url}"
'''
        result = parse_v3(source)
        assert result.success == True, "多个命名空间组合应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_system_vars_in_expressions(self, parse_v3):
        """✅ 正确：表达式中的系统变量"""
        source = '''
let is_local = page.origin == config.local_origin
let has_api_key = env.API_KEY != None
'''
        result = parse_v3(source)
        assert result.success == True, "表达式中的系统变量应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_system_vars_in_assert(self, parse_v3):
        """✅ 正确：断言中的系统变量"""
        source = '''
assert page.url == config.expected_url
assert browser.name == "Chrome"
'''
        result = parse_v3(source)
        assert result.success == True, "断言中的系统变量应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_system_vars_in_when(self, parse_v3):
        """✅ 正确：when 块中的系统变量"""
        source = '''
when browser.name:
    "Chrome":
        log "Chrome 浏览器"
    "Firefox":
        log "Firefox 浏览器"
'''
        result = parse_v3(source)
        assert result.success == True, "when 块中的系统变量应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_realistic_usage(self, parse_v3):
        """✅ 正确：真实使用场景"""
        source = '''
step "环境检查":
    """检查测试环境配置"""

    # 检查页面
    if page.url != config.base_url:
        log f"错误：当前页面 {page.url} 不匹配配置 {config.base_url}"

    # 检查环境变量
    if env.ENVIRONMENT == None:
        log "警告：未设置 ENVIRONMENT 变量"

    # 记录浏览器信息
    log f"浏览器: {browser.name} {browser.version}"
    log f"任务: {context.task_id} (执行: {context.execution_id})"
'''
        result = parse_v3(source)
        assert result.success == True, "真实使用场景应该正确解析"


# ============================================================================
# Python 对齐验证
# ============================================================================

class TestV3_SystemVariables_PythonAlignment:
    """系统变量 Python 对齐验证"""

    @pytest.mark.v3
    @pytest.mark.python_aligned
    def test_looks_like_python_globals(self, parse_v3):
        """✅ 验证：看起来像 Python 全局对象"""
        # 类似 Python 的 os.environ, sys.version 等
        source = '''
log f"Environment: {env.API_KEY}"
log f"Page URL: {page.url}"
log f"Browser: {browser.name}"
'''
        result = parse_v3(source)
        assert result.success == True, \
            "系统变量应该像 Python 全局对象一样"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.parametrize("namespace", [
        "page",
        "env",
        "browser",
        "context",
        "config",
    ])
    def test_no_dollar_prefix_all_namespaces(self, parse_v3, namespace):
        """✅ 验证：所有命名空间都无 $ 前缀"""
        source = f'log {namespace}.property'
        result = parse_v3(source)
        assert result.success == True, \
            f"{namespace} 命名空间应该无 $ 前缀"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.parametrize("namespace", [
        "page",
        "env",
        "browser",
        "context",
        "config",
    ])
    def test_dollar_prefix_all_namespaces_error(self, parse_v3, namespace):
        """❌ 验证：所有命名空间的 $ 前缀都报错"""
        source = f'log ${namespace}.property'
        result = parse_v3(source)
        assert result.success == False, \
            f"${namespace} 应该报错"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    def test_comparison_with_python(self, parse_v3):
        """✅ 验证：与 Python 风格对比"""
        dsl_code = '''
# DSL v3.0
log env.API_KEY
log page.url
log browser.name
'''

        python_equiv = '''
# Python
import os, sys
print(os.environ['API_KEY'])
print(page.url)  # 假设 page 是全局对象
print(browser.name)  # 假设 browser 是全局对象
'''
        # DSL 代码应该能解析，且风格与 Python 相似
        result = parse_v3(dsl_code)
        assert result.success == True, \
            "系统变量风格应该与 Python 全局对象相似"


# ============================================================================
# 错误提示一致性测试
# ============================================================================

class TestV3_SystemVariables_ErrorMessages:
    """系统变量错误提示一致性测试"""

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.parametrize("wrong_syntax,correct_syntax", [
        ("$page.url", "page.url"),
        ("$env.API_KEY", "env.API_KEY"),
        ("$browser.name", "browser.name"),
        ("$context.task_id", "context.task_id"),
        ("$config.base_url", "config.base_url"),
    ])
    def test_error_suggests_correction(self, parse_v3, wrong_syntax, correct_syntax):
        """❌ 验证：错误提示建议正确语法"""
        source = f'log {wrong_syntax}'
        result = parse_v3(source)
        assert result.success == False, \
            f"{wrong_syntax} 应该报错"

        # 错误提示应该包含：
        # 1. 提及 $ 前缀错误
        # 2. 建议正确语法（可选）
        assert "$" in result.error or correct_syntax in result.error, \
            f"错误提示应提及 $ 前缀或建议正确语法 {correct_syntax}"


# ============================================================================
# 测试总结
# ============================================================================

"""
测试覆盖清单：

page 命名空间：
✅ page.url, page.title, page.origin
✅ 条件中使用
✅ $page.url 报错

env 命名空间：
✅ env.API_KEY 等环境变量
✅ 多个 env 变量
✅ 条件中使用
✅ $env.* 报错

browser 命名空间：
✅ browser.name, browser.version
✅ $browser.* 报错

context 命名空间：
✅ context.task_id, context.execution_id, context.start_time
✅ $context.* 报错

config 命名空间：
✅ config.base_url 等配置
✅ f-string 中使用
✅ $config.* 报错

综合测试：
✅ 多个命名空间组合
✅ 表达式、断言、when 块中使用
✅ 真实使用场景

Python 对齐验证：
✅ 像 Python 全局对象
✅ 所有命名空间无 $ 前缀
✅ 所有 $ 前缀都报错
✅ 与 Python 风格对比

错误提示：
✅ 错误提示建议正确语法

总计：约 40 个系统变量测试
"""
