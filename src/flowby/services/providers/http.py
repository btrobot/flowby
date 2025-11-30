"""
HTTP 请求服务提供者
"""

import time
from typing import Dict, Any, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..provider import ServiceProvider
from ..errors import ServiceError


class HttpProvider(ServiceProvider):
    """HTTP 请求服务提供者

    支持 GET, POST, PUT, DELETE, PATCH 等 HTTP 方法
    提供统一的响应格式和错误处理
    """

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        settings,
        **kwargs
    ):
        """
        初始化 HTTP 提供者

        Args:
            name: 提供者名称
            config: 提供者配置
            settings: 全局设置
            **kwargs: 其他参数
        """
        super().__init__(name, config, settings, **kwargs)

        # HTTP Session（延迟初始化）
        self.session: Optional[requests.Session] = None

        # 从配置中读取默认值
        self.default_timeout = self.config.get('default_timeout', 30)
        self.default_headers = self.config.get('default_headers', {})
        self.verify_ssl = self.config.get('verify_ssl', True)
        self.proxies = self.config.get('proxies', {})

    def initialize(self) -> None:
        """
        初始化 HTTP Session

        创建 requests.Session 并配置连接池、默认请求头等
        """
        self.session = requests.Session()

        # 设置默认请求头
        if self.default_headers:
            self.session.headers.update(self.default_headers)

        # 配置连接池适配器
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=Retry(total=0)  # 重试由 ServiceRegistry 处理
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # 设置代理
        if self.proxies:
            self.session.proxies.update(self.proxies)

    def get_methods(self) -> List[str]:
        """
        获取支持的方法列表

        Returns:
            方法名列表
        """
        return ['get', 'post', 'put', 'delete', 'patch', 'request']

    def close(self) -> None:
        """关闭 Session，释放资源"""
        if self.session:
            self.session.close()
            self.session = None

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        verify: Optional[bool] = None,
        allow_redirects: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送 GET 请求

        Args:
            url: 请求 URL（支持 {variable} 插值）
            params: 查询参数
            headers: 请求头（覆盖默认值）
            timeout: 超时时间（秒），None 使用默认值
            verify: 是否验证 SSL 证书，None 使用配置值
            allow_redirects: 是否允许重定向
            **kwargs: 传递给 requests 的其他参数

        Returns:
            标准化的响应对象
        """
        return self._request(
            'GET',
            url,
            params=params,
            headers=headers,
            timeout=timeout,
            verify=verify,
            allow_redirects=allow_redirects,
            **kwargs
        )

    def post(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        verify: Optional[bool] = None,
        allow_redirects: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送 POST 请求

        Args:
            url: 请求 URL
            data: Form 数据或原始字符串
            json: JSON 数据（自动序列化并设置 Content-Type）
            params: 查询参数
            headers: 请求头
            timeout: 超时时间（秒）
            verify: 是否验证 SSL 证书
            allow_redirects: 是否允许重定向
            **kwargs: 其他参数

        Returns:
            标准化的响应对象
        """
        return self._request(
            'POST',
            url,
            data=data,
            json=json,
            params=params,
            headers=headers,
            timeout=timeout,
            verify=verify,
            allow_redirects=allow_redirects,
            **kwargs
        )

    def put(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送 PUT 请求

        Args:
            url: 请求 URL
            data: Form 数据或原始字符串
            json: JSON 数据
            **kwargs: 其他参数（同 post）

        Returns:
            标准化的响应对象
        """
        return self._request('PUT', url, data=data, json=json, **kwargs)

    def delete(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送 DELETE 请求

        Args:
            url: 请求 URL
            params: 查询参数
            **kwargs: 其他参数（同 get）

        Returns:
            标准化的响应对象
        """
        return self._request('DELETE', url, params=params, **kwargs)

    def patch(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送 PATCH 请求

        Args:
            url: 请求 URL
            data: Form 数据或原始字符串
            json: JSON 数据
            **kwargs: 其他参数（同 post）

        Returns:
            标准化的响应对象
        """
        return self._request('PATCH', url, data=data, json=json, **kwargs)

    def request(
        self,
        http_method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        通用 HTTP 请求方法

        Args:
            http_method: HTTP 方法（GET, POST, PUT, DELETE, PATCH, etc.）
            url: 请求 URL
            **kwargs: 请求参数

        Returns:
            标准化的响应对象
        """
        return self._request(http_method.upper(), url, **kwargs)

    def _request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        统一的 HTTP 请求处理

        流程:
        1. 合并默认配置（headers, timeout, verify）
        2. 发送 HTTP 请求
        3. 解析响应
        4. 错误处理
        5. 返回标准化响应对象

        Args:
            method: HTTP 方法
            url: 请求 URL
            **kwargs: 请求参数

        Returns:
            标准化的响应对象
        """
        if not self.session:
            raise ServiceError(
                "HTTP Session 未初始化，请先调用 initialize()",
                provider=self.name,
                method=method
            )

        # 合并请求头
        headers = self._merge_headers(kwargs.pop('headers', None))

        # 设置超时
        timeout = kwargs.pop('timeout', None)
        if timeout is None:
            timeout = self.default_timeout

        # 设置 SSL 验证
        verify = kwargs.pop('verify', None)
        if verify is None:
            verify = self.verify_ssl

        # 记录开始时间
        start_time = time.time()

        try:
            # 发送 HTTP 请求
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
                verify=verify,
                **kwargs
            )

            # 计算耗时
            elapsed = time.time() - start_time

            # 解析响应
            return self._parse_response(response, elapsed)

        except requests.exceptions.Timeout as e:
            elapsed = time.time() - start_time
            return self._handle_error(e, url, elapsed, "请求超时")

        except requests.exceptions.SSLError as e:
            elapsed = time.time() - start_time
            return self._handle_error(e, url, elapsed, "SSL 证书验证失败")

        except requests.exceptions.ConnectionError as e:
            elapsed = time.time() - start_time
            return self._handle_error(e, url, elapsed, "无法连接到服务器")

        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start_time
            return self._handle_error(e, url, elapsed, "请求失败")

        except Exception as e:
            elapsed = time.time() - start_time
            return self._handle_error(e, url, elapsed, f"未知错误: {str(e)}")

    def _parse_response(
        self,
        response: requests.Response,
        elapsed: float
    ) -> Dict[str, Any]:
        """
        解析 requests.Response 为标准响应对象

        Args:
            response: requests.Response 对象
            elapsed: 请求耗时（秒）

        Returns:
            标准化的响应对象
        """
        # 提取基本信息
        result = {
            'status_code': response.status_code,
            'ok': 200 <= response.status_code < 300,
            'headers': dict(response.headers),
            'url': response.url,
            'elapsed': elapsed,
            'error': None
        }

        # 获取响应文本
        try:
            result['text'] = response.text
        except Exception:
            result['text'] = ''

        # 尝试解析 JSON
        result['data'] = None
        if response.text:
            try:
                result['data'] = response.json()
            except ValueError:
                # 不是 JSON 格式，保持 data=None
                pass

        # 如果是错误状态码，设置错误信息
        if not result['ok']:
            result['error'] = f"HTTP {response.status_code}"
            if response.reason:
                result['error'] += f": {response.reason}"

        return result

    def _handle_error(
        self,
        error: Exception,
        url: str,
        elapsed: float,
        message: str
    ) -> Dict[str, Any]:
        """
        统一错误处理，将异常转换为标准错误响应对象

        Args:
            error: 异常对象
            url: 请求 URL
            elapsed: 已耗时（秒）
            message: 错误消息

        Returns:
            标准错误响应对象
        """
        return {
            'status_code': 0,
            'ok': False,
            'headers': {},
            'data': None,
            'text': '',
            'url': url,
            'elapsed': elapsed,
            'error': f"{message}: {str(error)}"
        }

    def _merge_headers(
        self,
        custom_headers: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        合并默认请求头和自定义请求头

        优先级: 自定义 > 默认

        Args:
            custom_headers: 自定义请求头

        Returns:
            合并后的请求头
        """
        if custom_headers:
            # 创建副本，避免修改原对象
            merged = self.default_headers.copy()
            merged.update(custom_headers)
            return merged
        return self.default_headers.copy()

    def __repr__(self) -> str:
        return f"HttpProvider(name={self.name!r}, timeout={self.default_timeout}s)"
