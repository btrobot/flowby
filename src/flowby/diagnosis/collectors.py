"""
信息收集器

各类诊断信息的收集器实现
"""

import json
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Any, List, Optional
from pathlib import Path

if TYPE_CHECKING:
    from playwright.sync_api import Page
    from ..context import ExecutionContext


class BaseCollector:
    """收集器基类"""

    name: str = "base"

    def collect(self, page: "Page", context: "ExecutionContext", **kwargs) -> Dict[str, Any]:
        """
        收集信息

        Args:
            page: Playwright 页面对象
            context: 执行上下文
            **kwargs: 额外参数

        Returns:
            收集到的信息字典
        """
        raise NotImplementedError

    def save(self, data: Dict[str, Any], output_dir: Path) -> str:
        """
        保存收集到的信息

        Args:
            data: 收集到的数据
            output_dir: 输出目录

        Returns:
            保存的文件名
        """
        raise NotImplementedError


class ScreenshotCollector(BaseCollector):
    """截图收集器 - Level 1+"""

    name = "screenshot"

    def collect(self, page: "Page", context: "ExecutionContext", **kwargs) -> Dict[str, Any]:
        return {
            "type": "screenshot",
            "timestamp": datetime.now().isoformat(),
        }

    def save(self, data: Dict[str, Any], output_dir: Path, page: "Page") -> str:
        filename = "screenshot.png"
        filepath = output_dir / filename
        try:
            page.screenshot(path=str(filepath), full_page=True)
            return filename
        except Exception as e:
            return f"截图失败: {e}"


class PageInfoCollector(BaseCollector):
    """页面信息收集器 - Level 1+"""

    name = "page_info"

    def collect(self, page: "Page", context: "ExecutionContext", **kwargs) -> Dict[str, Any]:
        return {
            "url": page.url,
            "title": page.title(),
            "viewport": page.viewport_size,
            "timestamp": datetime.now().isoformat(),
        }

    def save(self, data: Dict[str, Any], output_dir: Path) -> str:
        filename = "page_info.json"
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename


class HtmlSourceCollector(BaseCollector):
    """HTML源码收集器 - Level 2+"""

    name = "html_source"

    def collect(self, page: "Page", context: "ExecutionContext", **kwargs) -> Dict[str, Any]:
        return {
            "content": page.content(),
            "timestamp": datetime.now().isoformat(),
        }

    def save(self, data: Dict[str, Any], output_dir: Path) -> str:
        filename = "page_source.html"
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(data.get("content", ""))
        return filename


class ElementInfoCollector(BaseCollector):
    """元素信息收集器 - Level 2+"""

    name = "element_info"

    def collect(self, page: "Page", context: "ExecutionContext", **kwargs) -> Dict[str, Any]:
        selector = kwargs.get("selector", "")

        result = {
            "selector": selector,
            "timestamp": datetime.now().isoformat(),
            "found_count": 0,
            "elements": [],
            "similar_selectors": [],
        }

        if not selector:
            return result

        try:
            locator = page.locator(selector)
            count = locator.count()
            result["found_count"] = count

            # 收集找到的元素信息
            for i in range(min(count, 5)):  # 最多收集5个
                try:
                    element = locator.nth(i)
                    element_info = {
                        "index": i,
                        "tag_name": element.evaluate("el => el.tagName"),
                        "is_visible": element.is_visible(),
                        "text_content": (element.text_content() or "")[:100],
                        "attributes": {},
                    }

                    # 获取常用属性
                    for attr in ["id", "class", "name", "type", "href", "value"]:
                        val = element.get_attribute(attr)
                        if val:
                            element_info["attributes"][attr] = val

                    result["elements"].append(element_info)
                except Exception:
                    pass

            # 如果没找到，尝试查找相似选择器
            if count == 0:
                result["similar_selectors"] = self._find_similar_selectors(page, selector)

        except Exception as e:
            result["error"] = str(e)

        return result

    def _find_similar_selectors(self, page: "Page", selector: str) -> List[Dict[str, Any]]:
        """查找相似的选择器"""
        similar = []

        # 尝试一些变体
        variants = []

        # 如果是 ID 选择器
        if selector.startswith("#"):
            base = selector[1:]
            variants.extend(
                [
                    f'[id*="{base}"]',
                    f'[id$="{base}"]',
                    f'[id^="{base}"]',
                ]
            )

        # 如果是类选择器
        if selector.startswith("."):
            base = selector[1:]
            variants.extend(
                [
                    f'[class*="{base}"]',
                    f".{base.lower()}",
                    f".{base.upper()}",
                ]
            )

        # 通用变体
        if "button" in selector.lower():
            variants.extend(["button", 'input[type="button"]', 'input[type="submit"]'])
        if "submit" in selector.lower():
            variants.extend(['button[type="submit"]', 'input[type="submit"]', ".submit"])
        if "input" in selector.lower():
            variants.extend(["input", "textarea", ".input"])

        for variant in variants[:10]:  # 最多尝试10个
            try:
                count = page.locator(variant).count()
                if count > 0:
                    similar.append({"selector": variant, "count": count})
            except Exception:
                pass

        return similar[:5]  # 返回最多5个建议

    def save(self, data: Dict[str, Any], output_dir: Path) -> str:
        filename = "element_info.json"
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename


class ConsoleLogCollector(BaseCollector):
    """控制台日志收集器 - Level 3+"""

    name = "console_logs"

    def collect(self, page: "Page", context: "ExecutionContext", **kwargs) -> Dict[str, Any]:
        # 从监听器获取日志
        listeners = kwargs.get("listeners")
        logs = []

        if listeners and hasattr(listeners, "console_logs"):
            logs = listeners.console_logs

        return {
            "logs": logs,
            "total_count": len(logs),
            "error_count": sum(1 for log in logs if log.get("type") == "error"),
            "warning_count": sum(1 for log in logs if log.get("type") == "warning"),
            "timestamp": datetime.now().isoformat(),
        }

    def save(self, data: Dict[str, Any], output_dir: Path) -> str:
        filename = "console_logs.json"
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename


class ContextSnapshotCollector(BaseCollector):
    """执行上下文收集器 - Level 3+"""

    name = "context_snapshot"

    def collect(self, page: "Page", context: "ExecutionContext", **kwargs) -> Dict[str, Any]:
        # 获取变量快照（过滤敏感信息）
        variables = {}
        for key, value in context.variables.items():
            if isinstance(value, dict):
                # 过滤可能的敏感字段
                filtered = {
                    k: v
                    for k, v in value.items()
                    if not any(s in k.lower() for s in ["password", "secret", "token", "key"])
                }
                variables[key] = filtered
            else:
                variables[key] = value

        # 获取执行记录
        execution_records = []
        if hasattr(context, "execution_records"):
            for record in context.execution_records[-20:]:  # 最近20条
                execution_records.append(
                    {
                        "type": record.get("type", ""),
                        "content": record.get("content", ""),
                        "success": record.get("success", True),
                        "timestamp": record.get("timestamp", ""),
                    }
                )

        return {
            "task_id": context.task_id,
            "current_step": getattr(context, "current_step", None),
            "variables": variables,
            "execution_records": execution_records,
            "timestamp": datetime.now().isoformat(),
        }

    def save(self, data: Dict[str, Any], output_dir: Path) -> str:
        filename = "context_snapshot.json"
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename


class NetworkLogCollector(BaseCollector):
    """网络请求收集器 - Level 4+"""

    name = "network_logs"

    def collect(self, page: "Page", context: "ExecutionContext", **kwargs) -> Dict[str, Any]:
        # 从监听器获取网络日志
        listeners = kwargs.get("listeners")
        logs = []

        if listeners and hasattr(listeners, "network_logs"):
            logs = listeners.network_logs

        # 统计
        failed_count = sum(1 for log in logs if log.get("failed", False))
        error_count = sum(1 for log in logs if log.get("status", 200) >= 400)

        return {
            "requests": logs,
            "total_count": len(logs),
            "failed_count": failed_count,
            "error_count": error_count,
            "timestamp": datetime.now().isoformat(),
        }

    def save(self, data: Dict[str, Any], output_dir: Path) -> str:
        filename = "network_logs.json"
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename


class PerformanceCollector(BaseCollector):
    """性能指标收集器 - Level 5+"""

    name = "performance_metrics"

    def collect(self, page: "Page", context: "ExecutionContext", **kwargs) -> Dict[str, Any]:
        try:
            # 获取性能指标
            metrics = page.evaluate(
                """() => {
                const perf = window.performance;
                const timing = perf.timing;
                const navigation = perf.getEntriesByType('navigation')[0] || {};

                return {
                    // 页面加载时间
                    loadTime: timing.loadEventEnd - timing.navigationStart,
                    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    domInteractive: timing.domInteractive - timing.navigationStart,

                    // 网络时间
                    dnsLookup: timing.domainLookupEnd - timing.domainLookupStart,
                    tcpConnect: timing.connectEnd - timing.connectStart,
                    serverResponse: timing.responseEnd - timing.requestStart,

                    // 渲染时间
                    domParsing: timing.domComplete - timing.domInteractive,

                    // 资源数量
                    resourceCount: perf.getEntriesByType('resource').length,

                    // 内存使用 (如果可用)
                    memory: perf.memory ? {
                        usedJSHeapSize: perf.memory.usedJSHeapSize,
                        totalJSHeapSize: perf.memory.totalJSHeapSize,
                    } : null,
                };
            }"""
            )

            return {
                "metrics": metrics,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def save(self, data: Dict[str, Any], output_dir: Path) -> str:
        filename = "performance_metrics.json"
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename


class ViewportCollector(BaseCollector):
    """视口信息收集器 - Level 5+"""

    name = "viewport_info"

    def collect(self, page: "Page", context: "ExecutionContext", **kwargs) -> Dict[str, Any]:
        try:
            viewport_info = page.evaluate(
                """() => {
                return {
                    windowWidth: window.innerWidth,
                    windowHeight: window.innerHeight,
                    documentWidth: document.documentElement.scrollWidth,
                    documentHeight: document.documentElement.scrollHeight,
                    scrollX: window.scrollX,
                    scrollY: window.scrollY,
                    devicePixelRatio: window.devicePixelRatio,
                };
            }"""
            )

            # 如果有目标元素，获取其位置
            selector = kwargs.get("selector", "")
            if selector:
                try:
                    element_rect = page.locator(selector).first.bounding_box()
                    if element_rect:
                        viewport_info["target_element"] = {
                            "selector": selector,
                            "rect": element_rect,
                            "in_viewport": self._is_in_viewport(element_rect, viewport_info),
                        }
                except Exception:
                    pass

            return {
                "viewport": viewport_info,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _is_in_viewport(self, rect: dict, viewport: dict) -> bool:
        """判断元素是否在视口中"""
        if not rect:
            return False

        scroll_x = viewport.get("scrollX", 0)
        scroll_y = viewport.get("scrollY", 0)
        win_width = viewport.get("windowWidth", 0)
        win_height = viewport.get("windowHeight", 0)

        elem_left = rect.get("x", 0)
        elem_top = rect.get("y", 0)
        elem_right = elem_left + rect.get("width", 0)
        elem_bottom = elem_top + rect.get("height", 0)

        return (
            elem_left >= scroll_x
            and elem_top >= scroll_y
            and elem_right <= scroll_x + win_width
            and elem_bottom <= scroll_y + win_height
        )

    def save(self, data: Dict[str, Any], output_dir: Path) -> str:
        filename = "viewport_info.json"
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename


# 收集器注册表
COLLECTORS = {
    "screenshot": ScreenshotCollector(),
    "page_info": PageInfoCollector(),
    "html_source": HtmlSourceCollector(),
    "element_info": ElementInfoCollector(),
    "console_logs": ConsoleLogCollector(),
    "context_snapshot": ContextSnapshotCollector(),
    "network_logs": NetworkLogCollector(),
    "performance_metrics": PerformanceCollector(),
    "viewport_info": ViewportCollector(),
}


def get_collector(name: str) -> Optional[BaseCollector]:
    """获取指定名称的收集器"""
    return COLLECTORS.get(name)
