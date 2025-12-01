"""
事件监听器

用于收集控制台日志和网络请求信息
"""

import re
from datetime import datetime
from typing import TYPE_CHECKING, List, Dict, Any

if TYPE_CHECKING:
    from playwright.sync_api import Page, ConsoleMessage, Request, Response

from .config import DiagnosisConfig, DEFAULT_DIAGNOSIS_CONFIG


class DiagnosisListeners:
    """诊断信息监听器"""

    def __init__(self, page: "Page", config: DiagnosisConfig = None):
        """
        初始化监听器

        Args:
            page: Playwright 页面对象
            config: 诊断配置
        """
        self.page = page
        self.config = config or DEFAULT_DIAGNOSIS_CONFIG
        self.console_logs: List[Dict[str, Any]] = []
        self.network_logs: List[Dict[str, Any]] = []
        self._request_map: Dict[str, Dict[str, Any]] = {}  # 用于匹配请求和响应
        self._setup_listeners()

    def _setup_listeners(self):
        """设置事件监听器"""
        # 控制台日志监听
        self.page.on("console", self._on_console)

        # 网络请求监听
        self.page.on("request", self._on_request)
        self.page.on("response", self._on_response)
        self.page.on("requestfailed", self._on_request_failed)

    def _on_console(self, msg: "ConsoleMessage"):
        """处理控制台消息"""
        msg_type = msg.type
        allowed_levels = self.config.console_filter.levels

        # 过滤级别
        if msg_type not in allowed_levels:
            return

        # 限制数量
        if len(self.console_logs) >= self.config.console_filter.max_entries:
            return

        log_entry = {
            "type": msg_type,
            "text": msg.text,
            "timestamp": datetime.now().isoformat(),
        }

        # 获取位置信息（如果可用）
        try:
            location = msg.location
            if location:
                log_entry["location"] = {
                    "url": location.get("url", ""),
                    "line": location.get("lineNumber", 0),
                    "column": location.get("columnNumber", 0),
                }
        except Exception:
            pass

        self.console_logs.append(log_entry)

    def _on_request(self, request: "Request"):
        """处理请求开始"""
        url = request.url

        # 过滤静态资源
        if not self.config.network_filter.include_assets:
            if self._is_asset_url(url):
                return

        request_id = self._get_request_id(request)

        self._request_map[request_id] = {
            "url": url,
            "method": request.method,
            "headers": dict(request.headers) if request.headers else {},
            "post_data": request.post_data[:500] if request.post_data else None,
            "resource_type": request.resource_type,
            "timestamp": datetime.now().isoformat(),
        }

    def _on_response(self, response: "Response"):
        """处理响应"""
        request = response.request
        request_id = self._get_request_id(request)

        if request_id not in self._request_map:
            return

        request_data = self._request_map[request_id]
        status = response.status

        # 只记录失败请求
        if self.config.network_filter.only_failed and status < 400:
            del self._request_map[request_id]
            return

        log_entry = {
            **request_data,
            "status": status,
            "status_text": response.status_text,
            "response_headers": dict(response.headers) if response.headers else {},
            "failed": False,
            "response_timestamp": datetime.now().isoformat(),
        }

        self.network_logs.append(log_entry)
        del self._request_map[request_id]

    def _on_request_failed(self, request: "Request"):
        """处理请求失败"""
        request_id = self._get_request_id(request)

        if request_id in self._request_map:
            request_data = self._request_map[request_id]
        else:
            url = request.url
            if not self.config.network_filter.include_assets and self._is_asset_url(url):
                return

            request_data = {
                "url": url,
                "method": request.method,
                "resource_type": request.resource_type,
                "timestamp": datetime.now().isoformat(),
            }

        log_entry = {
            **request_data,
            "failed": True,
            "failure_text": request.failure,
            "response_timestamp": datetime.now().isoformat(),
        }

        self.network_logs.append(log_entry)

        if request_id in self._request_map:
            del self._request_map[request_id]

    def _get_request_id(self, request: "Request") -> str:
        """生成请求唯一标识"""
        return f"{request.method}:{request.url}:{id(request)}"

    def _is_asset_url(self, url: str) -> bool:
        """判断是否是静态资源 URL"""
        for pattern in self.config.network_filter.exclude_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        return False

    def clear(self):
        """清空所有日志"""
        self.console_logs.clear()
        self.network_logs.clear()
        self._request_map.clear()

    def detach(self):
        """移除事件监听器"""
        try:
            self.page.remove_listener("console", self._on_console)
            self.page.remove_listener("request", self._on_request)
            self.page.remove_listener("response", self._on_response)
            self.page.remove_listener("requestfailed", self._on_request_failed)
        except Exception:
            pass
