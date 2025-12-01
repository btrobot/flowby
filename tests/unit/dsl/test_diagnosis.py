"""
诊断功能测试

测试 DSL 诊断模块的功能，包括：
1. DiagnosisLevel 枚举
2. DiagnosisConfig 配置
3. 收集器注册和获取
4. Lexer 诊断 Token
5. Parser 诊断语法
6. 报告生成
7. 清理机制
8. 向后兼容性
9. 模块集成
10. 完整工作流语法
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from flowby.lexer import Lexer, TokenType
from flowby.parser import Parser
from flowby.ast_nodes import AssertStatement
from flowby.diagnosis import (
    DiagnosisLevel,
    DiagnosisConfig,
    DEFAULT_DIAGNOSIS_CONFIG,
)
from flowby.diagnosis.config import get_collectors_for_level, LEVEL_COLLECTORS
from flowby.diagnosis.collectors import (
    get_collector,
    COLLECTORS,
    ScreenshotCollector,
    PageInfoCollector,
    HtmlSourceCollector,
    ElementInfoCollector,
    ConsoleLogCollector,
    ContextSnapshotCollector,
    NetworkLogCollector,
    PerformanceCollector,
    ViewportCollector,
)
from flowby.diagnosis.report import DiagnosisReportGenerator
from flowby.diagnosis.cleanup import DiagnosisCleanup


class TestDiagnosisLevelEnum:
    """测试 DiagnosisLevel 枚举"""

    def test_diagnosis_level_values(self):
        """测试诊断级别枚举值"""
        # Arrange & Act & Assert
        assert DiagnosisLevel.NONE == 0, "NONE 级别应该是 0"
        assert DiagnosisLevel.MINIMAL == 1, "MINIMAL 级别应该是 1"
        assert DiagnosisLevel.BASIC == 2, "BASIC 级别应该是 2"
        assert DiagnosisLevel.STANDARD == 3, "STANDARD 级别应该是 3"
        assert DiagnosisLevel.DETAILED == 4, "DETAILED 级别应该是 4"
        assert DiagnosisLevel.FULL == 5, "FULL 级别应该是 5"

    def test_from_string_lowercase(self):
        """测试从小写字符串解析级别"""
        # Arrange & Act & Assert
        assert DiagnosisLevel.from_string("none") == DiagnosisLevel.NONE, "none 应该解析为 NONE"
        assert (
            DiagnosisLevel.from_string("minimal") == DiagnosisLevel.MINIMAL
        ), "minimal 应该解析为 MINIMAL"
        assert DiagnosisLevel.from_string("basic") == DiagnosisLevel.BASIC, "basic 应该解析为 BASIC"
        assert (
            DiagnosisLevel.from_string("standard") == DiagnosisLevel.STANDARD
        ), "standard 应该解析为 STANDARD"
        assert (
            DiagnosisLevel.from_string("detailed") == DiagnosisLevel.DETAILED
        ), "detailed 应该解析为 DETAILED"
        assert DiagnosisLevel.from_string("full") == DiagnosisLevel.FULL, "full 应该解析为 FULL"

    def test_from_string_uppercase(self):
        """测试从大写字符串解析级别"""
        # Arrange & Act & Assert
        assert (
            DiagnosisLevel.from_string("MINIMAL") == DiagnosisLevel.MINIMAL
        ), "MINIMAL 应该解析为 MINIMAL"
        assert (
            DiagnosisLevel.from_string("DETAILED") == DiagnosisLevel.DETAILED
        ), "DETAILED 应该解析为 DETAILED"

    def test_from_string_mixed_case(self):
        """测试从混合大小写字符串解析级别"""
        # Arrange & Act & Assert
        assert DiagnosisLevel.from_string("Basic") == DiagnosisLevel.BASIC, "Basic 应该解析为 BASIC"

    def test_from_string_invalid(self):
        """测试无效字符串抛出异常"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            DiagnosisLevel.from_string("invalid")

    @pytest.mark.parametrize(
        "level_str,expected_level",
        [
            ("none", DiagnosisLevel.NONE),
            ("minimal", DiagnosisLevel.MINIMAL),
            ("basic", DiagnosisLevel.BASIC),
            ("standard", DiagnosisLevel.STANDARD),
            ("detailed", DiagnosisLevel.DETAILED),
            ("full", DiagnosisLevel.FULL),
        ],
    )
    def test_various_level_strings(self, level_str, expected_level):
        """测试各种级别字符串"""
        # Act
        result = DiagnosisLevel.from_string(level_str)

        # Assert
        assert result == expected_level


class TestDiagnosisConfig:
    """测试 DiagnosisConfig 配置"""

    def test_default_config_level(self):
        """测试默认配置级别"""
        # Arrange
        config = DEFAULT_DIAGNOSIS_CONFIG

        # Act & Assert
        assert config.default_level == DiagnosisLevel.STANDARD, "默认级别应该是 STANDARD"

    def test_error_type_level_mapping_assertion(self):
        """测试断言失败的级别映射"""
        # Arrange
        config = DEFAULT_DIAGNOSIS_CONFIG

        # Act
        level = config.get_level_for_error("ASSERTION_FAILED")

        # Assert
        assert level == DiagnosisLevel.STANDARD, "ASSERTION_FAILED 应该使用 STANDARD 级别"

    def test_error_type_level_mapping_element(self):
        """测试元素未找到的级别映射"""
        # Arrange
        config = DEFAULT_DIAGNOSIS_CONFIG

        # Act
        level = config.get_level_for_error("ELEMENT_NOT_FOUND")

        # Assert
        assert level == DiagnosisLevel.BASIC, "ELEMENT_NOT_FOUND 应该使用 BASIC 级别"

    def test_error_type_level_mapping_timeout(self):
        """测试超时的级别映射"""
        # Arrange
        config = DEFAULT_DIAGNOSIS_CONFIG

        # Act
        level = config.get_level_for_error("TIMEOUT")

        # Assert
        assert level == DiagnosisLevel.DETAILED, "TIMEOUT 应该使用 DETAILED 级别"

    def test_error_type_level_mapping_unknown(self):
        """测试未知错误的级别映射"""
        # Arrange
        config = DEFAULT_DIAGNOSIS_CONFIG

        # Act
        level = config.get_level_for_error("UNKNOWN_ERROR")

        # Assert
        assert level == DiagnosisLevel.STANDARD, "未知错误应该使用默认 STANDARD 级别"

    def test_cleanup_config(self):
        """测试清理配置"""
        # Arrange
        config = DEFAULT_DIAGNOSIS_CONFIG

        # Act & Assert
        assert config.cleanup.enabled == True, "清理应该默认启用"
        assert config.cleanup.max_age_days == 7, "最大保留天数应该是 7"
        assert config.cleanup.max_count == 100, "最大保留数量应该是 100"
        assert config.cleanup.max_size_mb == 500, "最大保留大小应该是 500MB"

    def test_network_filter_config(self):
        """测试网络过滤配置"""
        # Arrange
        config = DEFAULT_DIAGNOSIS_CONFIG

        # Act & Assert
        assert config.network_filter.include_assets == False, "默认不包含静态资源"
        assert config.network_filter.only_failed == False, "默认不仅记录失败请求"

    def test_console_filter_config(self):
        """测试控制台过滤配置"""
        # Arrange
        config = DEFAULT_DIAGNOSIS_CONFIG

        # Act & Assert
        assert "error" in config.console_filter.levels, "应该包含 error 级别"
        assert "warning" in config.console_filter.levels, "应该包含 warning 级别"
        assert config.console_filter.max_entries == 100, "最大条目数应该是 100"

    @pytest.mark.parametrize(
        "error_type,expected_level",
        [
            ("ASSERTION_FAILED", DiagnosisLevel.STANDARD),
            ("ELEMENT_NOT_FOUND", DiagnosisLevel.BASIC),
            ("TIMEOUT", DiagnosisLevel.DETAILED),
            ("UNKNOWN_ERROR", DiagnosisLevel.STANDARD),
        ],
    )
    def test_various_error_type_mappings(self, error_type, expected_level):
        """测试各种错误类型的级别映射"""
        # Arrange
        config = DEFAULT_DIAGNOSIS_CONFIG

        # Act
        level = config.get_level_for_error(error_type)

        # Assert
        assert level == expected_level


class TestCollectorsForLevel:
    """测试各级别对应的收集器"""

    def test_none_level_collectors(self):
        """测试 NONE 级别收集器"""
        # Arrange & Act
        collectors = get_collectors_for_level(DiagnosisLevel.NONE)

        # Assert
        assert collectors == [], "NONE 级别不应该有收集器"

    def test_minimal_level_collectors(self):
        """测试 MINIMAL 级别收集器"""
        # Arrange & Act
        collectors = get_collectors_for_level(DiagnosisLevel.MINIMAL)

        # Assert
        assert "screenshot" in collectors, "MINIMAL 应该包含 screenshot"
        assert "page_info" in collectors, "MINIMAL 应该包含 page_info"
        assert len(collectors) == 2, "MINIMAL 应该有 2 个收集器"

    def test_basic_level_collectors(self):
        """测试 BASIC 级别收集器"""
        # Arrange & Act
        collectors = get_collectors_for_level(DiagnosisLevel.BASIC)

        # Assert
        assert "html_source" in collectors, "BASIC 应该包含 html_source"
        assert "element_info" in collectors, "BASIC 应该包含 element_info"
        assert len(collectors) == 4, "BASIC 应该有 4 个收集器"

    def test_standard_level_collectors(self):
        """测试 STANDARD 级别收集器"""
        # Arrange & Act
        collectors = get_collectors_for_level(DiagnosisLevel.STANDARD)

        # Assert
        assert "console_logs" in collectors, "STANDARD 应该包含 console_logs"
        assert "context_snapshot" in collectors, "STANDARD 应该包含 context_snapshot"
        assert len(collectors) == 6, "STANDARD 应该有 6 个收集器"

    def test_detailed_level_collectors(self):
        """测试 DETAILED 级别收集器"""
        # Arrange & Act
        collectors = get_collectors_for_level(DiagnosisLevel.DETAILED)

        # Assert
        assert "network_logs" in collectors, "DETAILED 应该包含 network_logs"
        assert len(collectors) == 7, "DETAILED 应该有 7 个收集器"

    def test_full_level_collectors(self):
        """测试 FULL 级别收集器"""
        # Arrange & Act
        collectors = get_collectors_for_level(DiagnosisLevel.FULL)

        # Assert
        assert "performance_metrics" in collectors, "FULL 应该包含 performance_metrics"
        assert "viewport_info" in collectors, "FULL 应该包含 viewport_info"
        assert len(collectors) == 9, "FULL 应该有 9 个收集器"

    @pytest.mark.parametrize(
        "level,expected_count",
        [
            (DiagnosisLevel.NONE, 0),
            (DiagnosisLevel.MINIMAL, 2),
            (DiagnosisLevel.BASIC, 4),
            (DiagnosisLevel.STANDARD, 6),
            (DiagnosisLevel.DETAILED, 7),
            (DiagnosisLevel.FULL, 9),
        ],
    )
    def test_various_level_collector_counts(self, level, expected_count):
        """测试各级别收集器数量"""
        # Act
        collectors = get_collectors_for_level(level)

        # Assert
        assert len(collectors) == expected_count


class TestCollectorsRegistry:
    """测试收集器注册表"""

    @pytest.mark.parametrize(
        "collector_name",
        [
            "screenshot",
            "page_info",
            "html_source",
            "element_info",
            "console_logs",
            "context_snapshot",
            "network_logs",
            "performance_metrics",
            "viewport_info",
        ],
    )
    def test_collector_registered(self, collector_name):
        """测试收集器已注册"""
        # Act
        collector = get_collector(collector_name)

        # Assert
        assert collector is not None, f"收集器 {collector_name} 应该已注册"
        assert collector.name == collector_name, f"收集器名称应该是 {collector_name}"

    def test_invalid_collector_name(self):
        """测试无效收集器名返回 None"""
        # Act
        collector = get_collector("invalid")

        # Assert
        assert collector is None, "无效收集器名应该返回 None"

    def test_all_collectors_have_name(self):
        """测试所有收集器都有 name 属性"""
        # Arrange
        expected_collectors = [
            "screenshot",
            "page_info",
            "html_source",
            "element_info",
            "console_logs",
            "context_snapshot",
            "network_logs",
            "performance_metrics",
            "viewport_info",
        ]

        # Act & Assert
        for name in expected_collectors:
            collector = get_collector(name)
            assert hasattr(collector, "name"), f"收集器 {name} 应该有 name 属性"


class TestLexerDiagnosisTokens:
    """测试 Lexer 诊断 Token"""

    @pytest.fixture
    def lexer(self):
        """提供 Lexer 实例"""
        return Lexer()

    def test_with_token(self, lexer):
        """测试 WITH token"""
        # Arrange & Act
        tokens = lexer.tokenize("with")

        # Assert
        assert tokens[0].type == TokenType.WITH, "with 应该生成 WITH token"

    def test_diagnosis_token(self, lexer):
        """测试 DIAGNOSIS token"""
        # Arrange & Act
        tokens = lexer.tokenize("diagnosis")

        # Assert
        assert tokens[0].type == TokenType.DIAGNOSIS, "diagnosis 应该生成 DIAGNOSIS token"

    @pytest.mark.parametrize(
        "text,expected_type",
        [
            ("none", TokenType.DIAG_NONE),  # v3.0: 诊断级别的 none
            ("minimal", TokenType.MINIMAL),
            ("basic", TokenType.BASIC),
            ("standard", TokenType.STANDARD),
            ("detailed", TokenType.DETAILED),
            ("full", TokenType.FULL),
        ],
    )
    def test_diagnosis_level_tokens(self, lexer, text, expected_type):
        """测试诊断级别 tokens"""
        # Act
        tokens = lexer.tokenize(text)

        # Assert
        assert tokens[0].type == expected_type, f"{text} 应该生成 {expected_type}"


class TestParserDiagnosisSyntax:
    """测试 Parser 诊断语法"""

    @pytest.fixture
    def lexer(self):
        """提供 Lexer 实例"""
        return Lexer()

    @pytest.fixture
    def parser(self):
        """提供 Parser 实例"""
        return Parser()

    @pytest.mark.skip(reason="diagnosis syntax not implemented - v2.0 uses simple assert structure")
    @pytest.mark.parametrize(
        "code,expected_type,expected_level",
        [
            ('assert $page.url contains "test" with diagnosis full', "expression", "full"),
            ('assert $element.exists("#btn") with diagnosis minimal', "expression", "minimal"),
            (
                'assert $element.text(".selector") contains "hello" with diagnosis basic',
                "expression",
                "basic",
            ),
            (
                'assert $element.value("#input") equals "x" with diagnosis detailed',
                "expression",
                "detailed",
            ),
            ('assert $page.url equals "http://test.com" with diagnosis none', "expression", "none"),
            ('assert $element.visible(".msg") with diagnosis standard', "expression", "standard"),
        ],
    )
    def test_assert_with_diagnosis_level(self, lexer, parser, code, expected_type, expected_level):
        """测试带诊断级别的断言"""
        # Arrange
        tokens = lexer.tokenize(code)

        # Act
        ast = parser.parse(tokens)
        stmt = ast.statements[0]

        # Assert
        assert isinstance(stmt, AssertStatement), "应该解析为 AssertStatement"
        assert stmt.assert_type == expected_type, f"断言类型应该是 {expected_type}"
        assert stmt.diagnosis_level == expected_level, f"诊断级别应该是 {expected_level}"

    @pytest.mark.skip(reason="diagnosis syntax not implemented - v2.0 uses simple assert structure")
    def test_assert_without_diagnosis_level(self, lexer, parser):
        """测试不带诊断级别的断言"""
        # Arrange
        tokens = lexer.tokenize('assert $page.url contains "test"')

        # Act
        ast = parser.parse(tokens)
        stmt = ast.statements[0]

        # Assert
        assert stmt.diagnosis_level is None, "没有诊断级别时应该是 None"


class TestReportGenerator:
    """测试报告生成器"""

    @pytest.fixture
    def generator(self):
        """提供报告生成器实例"""
        return DiagnosisReportGenerator()

    @pytest.fixture
    def test_data(self):
        """提供测试数据"""
        return {
            "error_info": {
                "type": "ASSERTION_FAILED",
                "message": "URL 断言失败",
                "statement": "assert url contains 'test'",
                "line": 10,
                "level": "STANDARD",
                "timestamp": datetime.now().isoformat(),
            },
            "page_info": {
                "url": "https://example.com",
                "title": "Test Page",
                "viewport": {"width": 1920, "height": 1080},
            },
            "element_info": {
                "selector": "#submit",
                "found_count": 0,
                "elements": [],
                "similar_selectors": [
                    {"selector": "[id*='submit']", "count": 2},
                ],
            },
            "console_logs": {
                "logs": [
                    {"type": "error", "text": "Test error"},
                ],
                "total_count": 1,
                "error_count": 1,
                "warning_count": 0,
            },
            "files": {
                "screenshot": "screenshot.png",
                "page_info": "page_info.json",
            },
        }

    def test_report_generation_basic(self, generator, test_data):
        """测试基本报告生成"""
        # Act
        report = generator.generate(test_data)

        # Assert
        assert "# 错误诊断报告" in report, "报告应该包含标题"
        assert len(report) > 0, "报告不应该为空"

    def test_report_contains_error_info(self, generator, test_data):
        """测试报告包含错误信息"""
        # Act
        report = generator.generate(test_data)

        # Assert
        assert "ASSERTION_FAILED" in report, "报告应该包含错误类型"
        assert "URL 断言失败" in report, "报告应该包含错误消息"

    def test_report_contains_page_info(self, generator, test_data):
        """测试报告包含页面信息"""
        # Act
        report = generator.generate(test_data)

        # Assert
        assert "https://example.com" in report, "报告应该包含页面 URL"

    def test_report_contains_element_info(self, generator, test_data):
        """测试报告包含元素信息"""
        # Act
        report = generator.generate(test_data)

        # Assert
        assert "#submit" in report, "报告应该包含元素选择器"

    def test_report_contains_console_logs(self, generator, test_data):
        """测试报告包含控制台日志"""
        # Act
        report = generator.generate(test_data)

        # Assert
        assert "Test error" in report, "报告应该包含控制台错误"

    def test_report_has_all_sections(self, generator, test_data):
        """测试报告包含所有章节"""
        # Act
        report = generator.generate(test_data)

        # Assert
        assert "## 错误摘要" in report, "报告应该有错误摘要章节"
        assert "## 页面信息" in report, "报告应该有页面信息章节"
        assert "## 元素信息" in report, "报告应该有元素信息章节"
        assert "## 控制台日志" in report, "报告应该有控制台日志章节"
        assert "## 诊断文件" in report, "报告应该有诊断文件章节"


class TestCleanupMechanism:
    """测试清理机制"""

    @pytest.fixture
    def temp_dir(self):
        """提供临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_cleanup_by_count(self, temp_dir):
        """测试按数量清理"""
        # Arrange
        config = DiagnosisConfig()
        config.cleanup.max_count = 3
        config.cleanup.max_age_days = 1
        cleanup = DiagnosisCleanup(base_dir=temp_dir, config=config)

        # 创建测试诊断目录
        task_dir = Path(temp_dir) / "test_task" / "error_diagnosis"
        task_dir.mkdir(parents=True)

        # 创建 5 个测试目录
        for i in range(5):
            diag_dir = task_dir / f"20231101_12000{i}_TEST"
            diag_dir.mkdir()
            (diag_dir / "test.txt").write_text("test")

        # Act
        stats = cleanup.cleanup()

        # Assert
        assert stats["deleted_by_count"] == 2, "应该删除 2 个目录 (5 - 3 = 2)"

        # 验证剩余目录数
        remaining = list(task_dir.iterdir())
        assert len(remaining) == 3, "应该剩余 3 个目录"

    def test_cleanup_stats(self, temp_dir):
        """测试清理统计信息"""
        # Arrange
        config = DiagnosisConfig()
        config.cleanup.max_count = 3
        cleanup = DiagnosisCleanup(base_dir=temp_dir, config=config)

        # 创建测试诊断目录
        task_dir = Path(temp_dir) / "test_task" / "error_diagnosis"
        task_dir.mkdir(parents=True)

        for i in range(3):
            diag_dir = task_dir / f"20231101_12000{i}_TEST"
            diag_dir.mkdir()
            (diag_dir / "test.txt").write_text("test")

        # 先执行清理
        cleanup.cleanup()

        # Act
        info = cleanup.get_stats()

        # Assert
        assert info["count"] == 3, "统计信息应该显示 3 个目录"


class TestIntegration:
    """测试模块集成"""

    def test_execution_context_has_diagnosis_manager(self):
        """测试执行上下文有诊断管理器"""
        # Arrange
        from flowby.context import ExecutionContext

        # Act
        ctx = ExecutionContext("test_task")

        # Assert
        assert ctx.diagnosis_manager is not None, "ExecutionContext 应该有 diagnosis_manager"

    def test_execution_context_has_diagnosis_config(self):
        """测试执行上下文有诊断配置"""
        # Arrange
        from flowby.context import ExecutionContext

        # Act
        ctx = ExecutionContext("test_task")

        # Assert
        assert ctx.diagnosis_config is not None, "ExecutionContext 应该有 diagnosis_config"
        assert (
            ctx.diagnosis_config.default_level == DiagnosisLevel.STANDARD
        ), "默认级别应该是 STANDARD"

    def test_execution_context_diagnosis_listeners_none(self):
        """测试执行上下文诊断监听器初始为 None"""
        # Arrange
        from flowby.context import ExecutionContext

        # Act
        ctx = ExecutionContext("test_task")

        # Assert
        assert ctx.diagnosis_listeners is None, "DiagnosisListeners 初始应该为 None"

    def test_set_diagnosis_config(self):
        """测试设置诊断配置"""
        # Arrange
        from flowby.context import ExecutionContext

        ctx = ExecutionContext("test_task")
        new_config = DiagnosisConfig(default_level=DiagnosisLevel.FULL)

        # Act
        ctx.set_diagnosis_config(new_config)

        # Assert
        assert ctx.diagnosis_config.default_level == DiagnosisLevel.FULL, "设置的配置应该生效"


class TestCompleteWorkflowSyntax:
    """测试完整工作流语法"""

    @pytest.fixture
    def lexer(self):
        """提供 Lexer 实例"""
        return Lexer()

    @pytest.fixture
    def parser(self):
        """提供 Parser 实例"""
        return Parser()

    @pytest.mark.skip(reason="diagnosis syntax not implemented - v2.0 uses simple assert structure")
    def test_complete_workflow_parsing(self, lexer, parser):
        """测试完整工作流解析"""
        # Arrange
        workflow = """
# 测试诊断功能
step "登录测试"
    navigate to "https://example.com/login"
    wait for networkidle
    select input where name="username"
    type "testuser"
    select input where name="password"
    type "password123"
    select button where type="submit"
    click
    wait 2s
    # 使用不同诊断级别的断言
    assert $page.url contains "dashboard" with diagnosis full
    assert $element.exists(".welcome") with diagnosis standard
    assert $element.text(".message") contains "Welcome" with diagnosis minimal
end step
"""

        # Act
        tokens = lexer.tokenize(workflow)
        ast = parser.parse(tokens)

        # Assert
        assert len(ast.statements) == 1, "应该解析出一个 step 块"

    @pytest.mark.skip(reason="diagnosis syntax not implemented - v2.0 uses simple assert structure")
    def test_workflow_assert_statements(self, lexer, parser):
        """测试工作流中的断言语句"""
        # Arrange
        workflow = """
step "登录测试"
    navigate to "https://example.com/login"
    assert $page.url contains "dashboard" with diagnosis full
    assert $element.exists(".welcome") with diagnosis standard
    assert $element.text(".message") contains "Welcome" with diagnosis minimal
end step
"""

        # Act
        tokens = lexer.tokenize(workflow)
        ast = parser.parse(tokens)
        step = ast.statements[0]

        # 找到所有断言语句
        asserts = [s for s in step.statements if isinstance(s, AssertStatement)]

        # Assert
        assert len(asserts) == 3, "应该有 3 个断言语句"

    @pytest.mark.skip(reason="diagnosis syntax not implemented - v2.0 uses simple assert structure")
    def test_workflow_diagnosis_levels(self, lexer, parser):
        """测试工作流中的诊断级别"""
        # Arrange
        workflow = """
step "登录测试"
    assert $page.url contains "dashboard" with diagnosis full
    assert $element.exists(".welcome") with diagnosis standard
    assert $element.text(".message") contains "Welcome" with diagnosis minimal
end step
"""

        # Act
        tokens = lexer.tokenize(workflow)
        ast = parser.parse(tokens)
        step = ast.statements[0]
        asserts = [s for s in step.statements if isinstance(s, AssertStatement)]

        # Assert
        assert asserts[0].diagnosis_level == "full", "第一个断言应该是 full 级别"
        assert asserts[1].diagnosis_level == "standard", "第二个断言应该是 standard 级别"
        assert asserts[2].diagnosis_level == "minimal", "第三个断言应该是 minimal 级别"
