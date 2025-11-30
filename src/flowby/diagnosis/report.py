"""
诊断报告生成器

生成 Markdown 格式的诊断报告
"""

from datetime import datetime
from typing import Dict, Any


class DiagnosisReportGenerator:
    """诊断报告生成器"""

    def generate(self, collected_data: Dict[str, Any]) -> str:
        """
        生成诊断报告

        Args:
            collected_data: 收集到的诊断数据

        Returns:
            Markdown 格式的报告内容
        """
        sections = []

        # 标题
        error_info = collected_data.get("error_info", {})
        sections.append(self._generate_header(error_info))

        # 错误摘要
        sections.append(self._generate_error_summary(error_info))

        # 页面信息
        if "page_info" in collected_data:
            sections.append(self._generate_page_info(collected_data["page_info"]))

        # 元素信息
        if "element_info" in collected_data:
            sections.append(self._generate_element_info(collected_data["element_info"]))

        # 控制台日志
        if "console_logs" in collected_data:
            sections.append(self._generate_console_logs(collected_data["console_logs"]))

        # 网络请求
        if "network_logs" in collected_data:
            sections.append(self._generate_network_logs(collected_data["network_logs"]))

        # 执行上下文
        if "context_snapshot" in collected_data:
            sections.append(self._generate_context_snapshot(collected_data["context_snapshot"]))

        # 性能指标
        if "performance_metrics" in collected_data:
            sections.append(self._generate_performance_metrics(collected_data["performance_metrics"]))

        # 视口信息
        if "viewport_info" in collected_data:
            sections.append(self._generate_viewport_info(collected_data["viewport_info"]))

        # 文件列表
        if "files" in collected_data:
            sections.append(self._generate_file_list(collected_data["files"]))

        return "\n\n".join(sections)

    def _generate_header(self, error_info: Dict[str, Any]) -> str:
        """生成报告头部"""
        error_type = error_info.get("type", "UNKNOWN")
        timestamp = error_info.get("timestamp", datetime.now().isoformat())

        return f"""# 错误诊断报告

**错误类型**: {error_type}
**诊断时间**: {timestamp}
**诊断级别**: {error_info.get("level", "STANDARD")}"""

    def _generate_error_summary(self, error_info: Dict[str, Any]) -> str:
        """生成错误摘要"""
        lines = ["## 错误摘要"]

        message = error_info.get("message", "")
        statement = error_info.get("statement", "")
        line = error_info.get("line", 0)

        if statement:
            lines.append(f"\n**失败语句**: `{statement}`")
        if line:
            lines.append(f"**行号**: {line}")
        if message:
            lines.append(f"\n**错误信息**:\n```\n{message}\n```")

        return "\n".join(lines)

    def _generate_page_info(self, page_info: Dict[str, Any]) -> str:
        """生成页面信息"""
        lines = ["## 页面信息"]

        url = page_info.get("url", "")
        title = page_info.get("title", "")
        viewport = page_info.get("viewport", {})

        lines.append(f"\n**URL**: {url}")
        lines.append(f"**标题**: {title}")

        if viewport:
            lines.append(f"**视口大小**: {viewport.get('width', 0)} x {viewport.get('height', 0)}")

        return "\n".join(lines)

    def _generate_element_info(self, element_info: Dict[str, Any]) -> str:
        """生成元素信息"""
        lines = ["## 元素信息"]

        selector = element_info.get("selector", "")
        found_count = element_info.get("found_count", 0)

        lines.append(f"\n**选择器**: `{selector}`")
        lines.append(f"**找到元素数**: {found_count}")

        # 元素详情
        elements = element_info.get("elements", [])
        if elements:
            lines.append("\n### 找到的元素")
            for elem in elements:
                lines.append(f"\n#### 元素 {elem.get('index', 0)}")
                lines.append(f"- **标签**: {elem.get('tag_name', '')}")
                lines.append(f"- **可见**: {'是' if elem.get('is_visible', False) else '否'}")

                text = elem.get("text_content", "")
                if text:
                    lines.append(f"- **文本**: {text[:50]}{'...' if len(text) > 50 else ''}")

                attrs = elem.get("attributes", {})
                if attrs:
                    lines.append("- **属性**:")
                    for k, v in attrs.items():
                        lines.append(f"  - `{k}`: {v}")

        # 相似选择器建议
        similar = element_info.get("similar_selectors", [])
        if similar:
            lines.append("\n### 相似选择器建议")
            for s in similar:
                lines.append(f"- `{s.get('selector', '')}` (找到 {s.get('count', 0)} 个)")

        # 错误信息
        if "error" in element_info:
            lines.append(f"\n**错误**: {element_info['error']}")

        return "\n".join(lines)

    def _generate_console_logs(self, console_data: Dict[str, Any]) -> str:
        """生成控制台日志"""
        lines = ["## 控制台日志"]

        total = console_data.get("total_count", 0)
        errors = console_data.get("error_count", 0)
        warnings = console_data.get("warning_count", 0)

        lines.append(f"\n**总计**: {total} 条")
        lines.append(f"**错误**: {errors} 条")
        lines.append(f"**警告**: {warnings} 条")

        logs = console_data.get("logs", [])
        if logs:
            lines.append("\n### 日志详情")

            # 按类型分组
            errors_list = [l for l in logs if l.get("type") == "error"]
            warnings_list = [l for l in logs if l.get("type") == "warning"]
            others = [l for l in logs if l.get("type") not in ("error", "warning")]

            if errors_list:
                lines.append("\n#### 错误")
                for log in errors_list[:10]:
                    lines.append(f"```\n{log.get('text', '')}\n```")

            if warnings_list:
                lines.append("\n#### 警告")
                for log in warnings_list[:10]:
                    lines.append(f"```\n{log.get('text', '')}\n```")

            if others and len(errors_list) + len(warnings_list) < 10:
                lines.append("\n#### 其他")
                for log in others[:5]:
                    lines.append(f"- [{log.get('type', '')}] {log.get('text', '')[:100]}")

        return "\n".join(lines)

    def _generate_network_logs(self, network_data: Dict[str, Any]) -> str:
        """生成网络请求日志"""
        lines = ["## 网络请求"]

        total = network_data.get("total_count", 0)
        failed = network_data.get("failed_count", 0)
        errors = network_data.get("error_count", 0)

        lines.append(f"\n**总计**: {total} 条")
        lines.append(f"**失败**: {failed} 条")
        lines.append(f"**错误 (4xx/5xx)**: {errors} 条")

        requests = network_data.get("requests", [])
        if requests:
            # 只显示失败和错误的请求
            problem_requests = [r for r in requests
                               if r.get("failed", False) or r.get("status", 200) >= 400]

            if problem_requests:
                lines.append("\n### 问题请求")
                for req in problem_requests[:10]:
                    method = req.get("method", "GET")
                    url = req.get("url", "")
                    status = req.get("status", "")

                    lines.append(f"\n#### {method} {url[:80]}")

                    if req.get("failed"):
                        lines.append(f"- **状态**: 失败")
                        lines.append(f"- **错误**: {req.get('failure_text', '')}")
                    else:
                        lines.append(f"- **状态码**: {status} {req.get('status_text', '')}")

        return "\n".join(lines)

    def _generate_context_snapshot(self, context_data: Dict[str, Any]) -> str:
        """生成执行上下文"""
        lines = ["## 执行上下文"]

        task_id = context_data.get("task_id", "")
        current_step = context_data.get("current_step", "")

        lines.append(f"\n**任务 ID**: {task_id}")
        if current_step:
            lines.append(f"**当前步骤**: {current_step}")

        # 变量
        variables = context_data.get("variables", {})
        if variables:
            lines.append("\n### 变量")
            for key, value in list(variables.items())[:20]:
                if isinstance(value, dict):
                    lines.append(f"\n**{key}**:")
                    for k, v in list(value.items())[:10]:
                        lines.append(f"  - `{k}`: {str(v)[:100]}")
                else:
                    lines.append(f"- `{key}`: {str(value)[:100]}")

        # 执行记录
        records = context_data.get("execution_records", [])
        if records:
            lines.append("\n### 最近执行记录")
            for record in records[-10:]:
                success = "✓" if record.get("success", True) else "✗"
                lines.append(f"- [{success}] {record.get('type', '')}: {record.get('content', '')[:50]}")

        return "\n".join(lines)

    def _generate_performance_metrics(self, perf_data: Dict[str, Any]) -> str:
        """生成性能指标"""
        lines = ["## 性能指标"]

        metrics = perf_data.get("metrics", {})
        if not metrics:
            if "error" in perf_data:
                lines.append(f"\n**错误**: {perf_data['error']}")
            return "\n".join(lines)

        lines.append("\n### 页面加载时间")
        lines.append(f"- **总加载时间**: {metrics.get('loadTime', 0)} ms")
        lines.append(f"- **DOM Content Loaded**: {metrics.get('domContentLoaded', 0)} ms")
        lines.append(f"- **DOM Interactive**: {metrics.get('domInteractive', 0)} ms")

        lines.append("\n### 网络时间")
        lines.append(f"- **DNS 查询**: {metrics.get('dnsLookup', 0)} ms")
        lines.append(f"- **TCP 连接**: {metrics.get('tcpConnect', 0)} ms")
        lines.append(f"- **服务器响应**: {metrics.get('serverResponse', 0)} ms")

        lines.append(f"\n**资源数量**: {metrics.get('resourceCount', 0)}")

        memory = metrics.get("memory")
        if memory:
            used = memory.get("usedJSHeapSize", 0) / 1024 / 1024
            total = memory.get("totalJSHeapSize", 0) / 1024 / 1024
            lines.append(f"\n### 内存使用")
            lines.append(f"- **已使用**: {used:.2f} MB")
            lines.append(f"- **总分配**: {total:.2f} MB")

        return "\n".join(lines)

    def _generate_viewport_info(self, viewport_data: Dict[str, Any]) -> str:
        """生成视口信息"""
        lines = ["## 视口信息"]

        viewport = viewport_data.get("viewport", {})
        if not viewport:
            if "error" in viewport_data:
                lines.append(f"\n**错误**: {viewport_data['error']}")
            return "\n".join(lines)

        lines.append(f"\n**窗口大小**: {viewport.get('windowWidth', 0)} x {viewport.get('windowHeight', 0)}")
        lines.append(f"**文档大小**: {viewport.get('documentWidth', 0)} x {viewport.get('documentHeight', 0)}")
        lines.append(f"**滚动位置**: ({viewport.get('scrollX', 0)}, {viewport.get('scrollY', 0)})")
        lines.append(f"**设备像素比**: {viewport.get('devicePixelRatio', 1)}")

        # 目标元素位置
        target = viewport.get("target_element")
        if target:
            rect = target.get("rect", {})
            lines.append(f"\n### 目标元素")
            lines.append(f"- **选择器**: `{target.get('selector', '')}`")
            lines.append(f"- **位置**: ({rect.get('x', 0)}, {rect.get('y', 0)})")
            lines.append(f"- **大小**: {rect.get('width', 0)} x {rect.get('height', 0)}")
            lines.append(f"- **在视口中**: {'是' if target.get('in_viewport', False) else '否'}")

        return "\n".join(lines)

    def _generate_file_list(self, files: Dict[str, str]) -> str:
        """生成文件列表"""
        lines = ["## 诊断文件"]

        lines.append("\n| 类型 | 文件名 |")
        lines.append("|------|--------|")

        for file_type, filename in files.items():
            lines.append(f"| {file_type} | {filename} |")

        return "\n".join(lines)
