"""
Resource Namespace - v4.2

基于 OpenAPI 规范的动态 REST API 资源命名空间。

功能:
- 根据 OpenAPI 规范动态生成 API 方法
- 自动处理路径参数、查询参数、请求体
- 支持多种认证方式（Bearer、API Key、Basic、OAuth2）
- 支持响应数据映射和验证（Phase 3）
- 支持超时、自定义 headers
"""

import requests
from typing import Dict, Any, Optional, List
from .openapi_loader import OpenAPISpec
from .errors import ExecutionError
from .auth_handler import create_auth_handler, AuthHandler
from .response_handler import create_response_handler, ResponseHandler, ValidationError
from .resilience_handler import create_resilience_handler, ResilienceHandler
from .mock_handler import create_mock_handler, MockHandler


class ResourceNamespace:
    """
    OpenAPI 资源命名空间

    基于 OpenAPI 规范动态生成 API 调用方法。
    每个 operationId 会成为一个可调用的方法。
    """

    def __init__(
        self,
        name: str,
        spec: OpenAPISpec,
        base_url: Optional[str] = None,
        auth: Optional[Dict] = None,
        timeout: Optional[int] = None,
        headers: Optional[Dict] = None,
        response_mapping: Optional[Dict] = None,
        validate_response: bool = True,
        resilience: Optional[Dict] = None,
        mock: Optional[Dict] = None,
        context: Optional['ExecutionContext'] = None
    ):
        """
        初始化资源命名空间

        Args:
            name: 资源名称
            spec: OpenAPI 规范对象
            base_url: API 基础 URL（覆盖 OpenAPI 中的定义）
            auth: 认证配置字典（支持多种认证方式）
            timeout: 请求超时时间（秒）
            headers: 默认 HTTP headers
            response_mapping: 响应数据映射配置（Phase 3）
            validate_response: 是否验证响应数据（默认 True）
            resilience: 弹性处理配置（重试和断路器，Phase 4）
            mock: Mock 模式配置（用于测试，Phase 5）
            context: 执行上下文（用于日志记录）

        认证配置示例:
            # Bearer Token
            auth = {"type": "bearer", "token": "xxx"}

            # API Key (header)
            auth = {"type": "apikey", "key": "X-API-Key", "value": "xxx", "location": "header"}

            # API Key (query)
            auth = {"type": "apikey", "key": "api_key", "value": "xxx", "location": "query"}

            # Basic Auth
            auth = {"type": "basic", "username": "user", "password": "pass"}

            # OAuth2 Client Credentials
            auth = {
                "type": "oauth2",
                "token_url": "https://oauth.example.com/token",
                "client_id": "xxx",
                "client_secret": "yyy"
            }

            # 简化形式（Phase 1 兼容）
            auth = {"Authorization": "Bearer token"}

        响应映射配置示例（Phase 3）:
            response_mapping = {
                "field_mapping": {
                    "userId": "user_id",        # 重命名字段
                    "createdAt": "created_at"
                },
                "exclude_fields": ["internal_field"],  # 排除字段
                "include_only": ["id", "name"],        # 仅包含指定字段
                "default_values": {                    # 默认值
                    "status": "active"
                }
            }

        弹性处理配置示例（Phase 4）:
            resilience = {
                # 重试配置
                "retry": {
                    "max_retries": 3,
                    "strategy": "exponential",  # exponential, fixed, linear
                    "base_delay": 1.0,
                    "jitter": True
                },
                # 断路器配置
                "circuit_breaker": {
                    "failure_threshold": 5,
                    "recovery_timeout": 60,
                    "fallback": lambda: {"status": "service_unavailable"}
                }
            }

        Mock 配置示例（Phase 5）:
            mock = {
                "enabled": True,
                "delay": 0.1,  # 模拟延迟
                "responses": {
                    "getUser": {
                        "status": 200,
                        "data": {"id": 1, "name": "Mock User"}
                    },
                    "createUser": {
                        "file": "mocks/create_user.json"
                    }
                },
                "record_calls": True  # 记录调用历史
            }
        """
        self.name = name
        self.spec = spec
        self.base_url = base_url or spec.get_base_url() or ""
        self.timeout = timeout or 30
        self.default_headers = headers or {}
        self.response_mapping = response_mapping
        self.validate_response = validate_response
        self.context = context

        # 创建认证处理器（Phase 2）
        self.auth_handler = create_auth_handler(auth)

        # 创建弹性处理器（Phase 4）
        self.resilience_handler = create_resilience_handler(resilience)

        # 创建 Mock 处理器（Phase 5）
        self.mock_handler = create_mock_handler(mock)

        # 动态生成所有操作方法
        for operation_id, operation in spec.operations.items():
            # 创建绑定方法
            method = self._make_method(operation_id, operation)
            # 设置为实例属性
            setattr(self, operation_id, method)

    def _make_method(self, operation_id: str, operation: Dict[str, Any]):
        """
        根据 OpenAPI 操作定义生成方法

        Args:
            operation_id: 操作 ID（方法名）
            operation: OpenAPI 操作定义

        Returns:
            可调用的方法
        """
        # 提取路径参数列表（按照定义顺序）
        path_params = [
            p['name'] for p in operation.get('parameters', [])
            if p.get('in') == 'path'
        ]

        def method(*args, **kwargs):
            """动态生成的 API 方法"""
            # 将位置参数映射到路径参数名
            if args:
                if len(args) > len(path_params):
                    raise TypeError(
                        f"{operation_id}() 期望最多 {len(path_params)} 个位置参数"
                        f"（路径参数：{', '.join(path_params)}），但传入了 {len(args)} 个"
                    )

                # 合并位置参数到 kwargs
                combined_kwargs = dict(kwargs)
                for i, arg_value in enumerate(args):
                    param_name = path_params[i]
                    if param_name in combined_kwargs:
                        raise TypeError(
                            f"{operation_id}() 参数 '{param_name}' 同时作为位置参数和关键字参数传入"
                        )
                    combined_kwargs[param_name] = arg_value

                return self._execute_operation(operation_id, operation, combined_kwargs)
            else:
                return self._execute_operation(operation_id, operation, kwargs)

        # 设置方法元数据
        method.__name__ = operation_id
        method.__doc__ = operation.get('summary') or operation.get('description') or f"API operation: {operation_id}"

        return method

    def _execute_operation(
        self,
        operation_id: str,
        operation: Dict[str, Any],
        kwargs: Dict[str, Any]
    ) -> Any:
        """
        执行 OpenAPI 操作

        Args:
            operation_id: 操作 ID
            operation: 操作定义
            kwargs: 调用参数

        Returns:
            API 响应数据

        Raises:
            ExecutionError: API 调用失败
        """
        # Phase 5: 检查是否启用 Mock 模式
        if self.mock_handler and self.mock_handler.is_enabled():
            if self.mock_handler.has_mock(operation_id):
                try:
                    # 获取 mock 响应
                    mock_response = self.mock_handler.get_mock_response(
                        operation_id,
                        kwargs,
                        logger=self.context.logger if self.context else None
                    )

                    # 记录调用
                    self.mock_handler.record_call(operation_id, kwargs, mock_response)

                    return mock_response

                except Exception as e:
                    # Mock 失败时的错误处理
                    if isinstance(e, ExecutionError):
                        raise

                    error_msg = f"Mock 响应失败: {operation_id}\n"
                    error_msg += f"错误: {str(e)}"
                    raise ExecutionError(
                        line=0,
                        statement=f"{self.name}.{operation_id}()",
                        error_type="MOCK_ERROR",
                        message=error_msg
                    )

        # 定义实际的 HTTP 请求函数
        def execute_http_request():
            """执行 HTTP 请求的内部函数"""
            return self._execute_http_request(operation_id, operation, kwargs)

        try:
            # 如果启用了弹性处理，使用弹性处理器执行
            if self.resilience_handler:
                return self.resilience_handler.execute(
                    operation_name=f"{self.name}.{operation_id}",
                    func=execute_http_request,
                    method=operation['method'],
                    logger=self.context.logger if self.context else None
                )
            else:
                # 否则直接执行
                return execute_http_request()

        except Exception as e:
            # 如果是已经包装过的 ExecutionError，直接抛出
            if isinstance(e, ExecutionError):
                raise

            # 其他异常包装为 ExecutionError
            error_msg = f"API 调用异常: {operation_id}\n"
            error_msg += f"错误类型: {type(e).__name__}\n"
            error_msg += f"错误: {str(e)}"
            raise ExecutionError(
                line=0,
                statement=f"{self.name}.{operation_id}()",
                error_type="RUNTIME_ERROR",
                message=error_msg
            )

    def _execute_http_request(
        self,
        operation_id: str,
        operation: Dict[str, Any],
        kwargs: Dict[str, Any]
    ) -> Any:
        """
        执行实际的 HTTP 请求（由 _execute_operation 或弹性处理器调用）

        Args:
            operation_id: 操作 ID
            operation: 操作定义
            kwargs: 调用参数

        Returns:
            API 响应数据

        Raises:
            ExecutionError: API 调用失败
        """
        try:
            # 1. 构建 URL（替换路径参数）
            url = self._build_url(operation['path'], operation['parameters'], kwargs)

            # 2. 提取 query 参数
            params = self._extract_query_params(operation['parameters'], kwargs)

            # 2.5. 添加认证 query 参数（Phase 2）
            if self.auth_handler:
                auth_params = self.auth_handler.get_auth_params()
                params.update(auth_params)

            # 3. 构建 request body
            json_body = self._build_request_body(operation.get('requestBody'), kwargs, operation['parameters'])

            # 4. 构建 headers
            headers = dict(self.default_headers)
            if self.auth_handler:
                auth_headers = self.auth_handler.get_auth_headers()
                headers.update(auth_headers)

            # 5. 记录日志
            if self.context:
                self.context.logger.info(
                    f"[API] {operation['method']} {url} "
                    f"(resource: {self.name}, operation: {operation_id})"
                )

            # 6. 发送请求
            method_name = operation['method'].lower()
            response = requests.request(
                method=method_name,
                url=url,
                params=params,
                json=json_body if json_body else None,
                headers=headers,
                timeout=self.timeout
            )

            # 7. 检查 HTTP 错误（4xx/5xx 抛异常）
            response.raise_for_status()

            # 8. 解析响应（自动识别 JSON）
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' in content_type:
                data = response.json()
            else:
                data = response.text

            # 8.5. 检测错误响应（v6.0.1）
            # 某些 API 在错误时返回纯文本字符串而不是 HTTP 错误码
            # 例如：5sim API 返回 "no free phones" 字符串
            if isinstance(data, str) and response.status_code == 200:
                # 检测常见的错误模式
                error_indicators = [
                    'error', 'fail', 'invalid', 'not found',
                    'no free', 'unavailable', 'forbidden'
                ]
                data_lower = data.lower()

                if any(indicator in data_lower for indicator in error_indicators):
                    # 将错误字符串包装为统一的错误对象
                    error_msg = f"API 返回错误: {operation_id}\n"
                    error_msg += f"URL: {url}\n"
                    error_msg += f"错误信息: {data}"

                    if self.context:
                        self.context.logger.error(
                            f"[API ERROR STRING] {operation['method']} {url} "
                            f"- {data} "
                            f"(resource: {self.name}, operation: {operation_id})"
                        )

                    raise ExecutionError(
                        line=0,
                        statement=f"{self.name}.{operation_id}()",
                        error_type="API_ERROR",
                        message=error_msg
                    )

            # 9. 响应数据验证和映射（Phase 3）
            if isinstance(data, (dict, list)):
                try:
                    # 创建响应处理器
                    response_handler = create_response_handler(
                        operation,
                        self.response_mapping,
                        self.validate_response
                    )

                    # 处理响应数据
                    if response_handler:
                        data = response_handler.process(data)

                except ValidationError as e:
                    # 验证错误
                    error_msg = f"响应数据验证失败: {operation_id}\n"
                    error_msg += f"字段: {e.field}\n"
                    error_msg += f"错误: {e.message}\n"
                    if e.value is not None:
                        error_msg += f"实际值: {e.value}"

                    # 🔥 记录验证错误日志（v4.2.1 改进）
                    if self.context:
                        self.context.logger.error(
                            f"[API VALIDATION ERROR] {operation_id} "
                            f"- 字段: {e.field}, 错误: {e.message} "
                            f"(resource: {self.name})"
                        )

                    raise ExecutionError(
                        line=0,
                        statement=f"{self.name}.{operation_id}()",
                        error_type="VALIDATION_ERROR",
                        message=error_msg
                    )

            return data

        except requests.exceptions.HTTPError as e:
            # HTTP 错误（4xx/5xx）
            error_msg = f"API 请求失败: {operation_id}\n"
            error_msg += f"URL: {url}\n"
            error_msg += f"状态码: {e.response.status_code}\n"
            try:
                error_detail = e.response.json()
                error_msg += f"错误详情: {error_detail}"
            except:
                error_msg += f"错误详情: {e.response.text}"

            # 🔥 记录详细错误日志（v4.2.1 改进）
            if self.context:
                self.context.logger.error(
                    f"[API ERROR] {operation['method']} {url} "
                    f"- 状态码: {e.response.status_code} "
                    f"(resource: {self.name}, operation: {operation_id})"
                )
                # 记录错误详情
                try:
                    error_detail = e.response.json()
                    self.context.logger.error(f"[API ERROR] 响应详情: {error_detail}")
                except:
                    error_text = e.response.text[:500]  # 限制长度
                    if error_text:
                        self.context.logger.error(f"[API ERROR] 响应内容: {error_text}")

            raise ExecutionError(
                line=0,
                statement=f"{self.name}.{operation_id}()",
                error_type="API_ERROR",
                message=error_msg
            )

        except requests.exceptions.Timeout:
            # 超时错误
            error_msg = f"API 请求超时: {operation_id}\n"
            error_msg += f"URL: {url}\n"
            error_msg += f"超时时间: {self.timeout}秒"

            # 🔥 记录超时日志（v4.2.1 改进）
            if self.context:
                self.context.logger.error(
                    f"[API TIMEOUT] {operation['method']} {url} "
                    f"- 超时: {self.timeout}秒 "
                    f"(resource: {self.name}, operation: {operation_id})"
                )

            raise ExecutionError(
                line=0,
                statement=f"{self.name}.{operation_id}()",
                error_type="TIMEOUT",
                message=error_msg
            )

        except requests.exceptions.RequestException as e:
            # 其他请求错误（网络错误等）
            error_msg = f"API 请求失败: {operation_id}\n"
            error_msg += f"URL: {url}\n"
            error_msg += f"错误: {str(e)}"

            # 🔥 记录网络错误日志（v4.2.1 改进）
            if self.context:
                self.context.logger.error(
                    f"[API NETWORK ERROR] {operation['method']} {url} "
                    f"- {type(e).__name__}: {str(e)} "
                    f"(resource: {self.name}, operation: {operation_id})"
                )

            raise ExecutionError(
                line=0,
                statement=f"{self.name}.{operation_id}()",
                error_type="NETWORK_ERROR",
                message=error_msg
            )

        except Exception as e:
            # 其他未知错误
            error_msg = f"API 调用异常: {operation_id}\n"
            error_msg += f"错误类型: {type(e).__name__}\n"
            error_msg += f"错误: {str(e)}"

            # 🔥 记录未知错误日志（v4.2.1 改进）
            if self.context:
                self.context.logger.error(
                    f"[API EXCEPTION] {operation_id} "
                    f"- {type(e).__name__}: {str(e)} "
                    f"(resource: {self.name})"
                )

            raise ExecutionError(
                line=0,
                statement=f"{self.name}.{operation_id}()",
                error_type="RUNTIME_ERROR",
                message=error_msg
            )

    def _build_url(
        self,
        path_template: str,
        parameters: List[Dict],
        kwargs: Dict[str, Any]
    ) -> str:
        """
        构建 URL，替换路径参数

        Args:
            path_template: 路径模板（如 /users/{userId}）
            parameters: OpenAPI 参数列表
            kwargs: 调用参数

        Returns:
            完整的 URL

        Raises:
            ValueError: 缺少必需的路径参数
        """
        url = self.base_url + path_template

        # 提取路径参数
        path_params = [
            p for p in parameters
            if p.get('in') == 'path'
        ]

        # 替换路径参数
        for param in path_params:
            param_name = param['name']

            if param_name not in kwargs:
                if param.get('required', False):
                    raise ValueError(f"缺少必需的路径参数: {param_name}")
                continue

            param_value = kwargs[param_name]
            url = url.replace(f"{{{param_name}}}", str(param_value))

        return url

    def _extract_query_params(
        self,
        parameters: List[Dict],
        kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        提取 query 参数

        Args:
            parameters: OpenAPI 参数列表
            kwargs: 调用参数

        Returns:
            query 参数字典

        Raises:
            ValueError: 缺少必需的 query 参数
        """
        query_params = {}

        # 提取声明为 query 的参数
        for param in parameters:
            if param.get('in') != 'query':
                continue

            param_name = param['name']

            if param_name in kwargs:
                query_params[param_name] = kwargs[param_name]
            elif param.get('required', False):
                raise ValueError(f"缺少必需的 query 参数: {param_name}")

        return query_params

    def _build_request_body(
        self,
        request_body_spec: Optional[Dict],
        kwargs: Dict[str, Any],
        parameters: List[Dict]
    ) -> Optional[Dict]:
        """
        构建请求体（JSON）

        Args:
            request_body_spec: OpenAPI requestBody 规范
            kwargs: 调用参数
            parameters: OpenAPI 参数列表（用于排除路径/查询参数）

        Returns:
            请求体字典，如果没有则返回 None
        """
        if not request_body_spec:
            return None

        # 提取已知的路径和查询参数名称
        known_param_names = set()
        for param in parameters:
            known_param_names.add(param['name'])

        # 剩余的参数作为 body
        body = {}
        for key, value in kwargs.items():
            if key not in known_param_names:
                body[key] = value

        return body if body else None

    def __repr__(self) -> str:
        """字符串表示"""
        op_count = len(self.spec.operations)
        return f"<ResourceNamespace '{self.name}' ({op_count} operations)>"
