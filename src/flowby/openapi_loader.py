"""
OpenAPI 加载器 - v4.2.1

解析并管理 OpenAPI 3.0 规范文件，用于 resource 语句。

功能:
- 加载 YAML/JSON 格式的 OpenAPI 规范文件
- 智能查找规范文件（脚本目录、项目根目录、当前目录）
- 提取所有 operationId 和对应的操作定义
- 提供 base_url 等配置信息

v4.2.1 新特性:
- 智能路径查找：类似 .env 文件的多位置查找
- 支持相对路径和绝对路径
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class OpenAPISpec:
    """OpenAPI 规范加载器和解析器"""

    def __init__(self, spec_file: str, script_path: Optional[str] = None):
        """
        初始化 OpenAPI 规范加载器

        Args:
            spec_file: OpenAPI 规范文件路径（相对或绝对）
            script_path: DSL 脚本文件路径（用于智能路径查找，v4.2.1）
        """
        self.spec_file = spec_file
        self.script_path = script_path
        self.resolved_path = self._resolve_spec_path()
        self.spec = self._load_spec()
        self.operations = self._extract_operations()

    def _resolve_spec_path(self) -> Path:
        """
        智能解析 OpenAPI 规范文件路径 (v4.2.1)

        查找顺序：
        1. 如果是绝对路径，直接使用
        2. 脚本所在目录（最直观）
        3. 项目根目录
        4. 当前工作目录
        5. OPENAPI_PATH 环境变量指定的目录

        Returns:
            解析后的文件路径

        Raises:
            FileNotFoundError: 所有位置都找不到文件
        """
        spec_path = Path(self.spec_file)

        # 1. 绝对路径直接使用
        if spec_path.is_absolute():
            if spec_path.exists():
                return spec_path
            raise FileNotFoundError(f"OpenAPI 文件不存在: {self.spec_file}")

        # 2-5. 相对路径：查找多个位置
        candidates = self._find_spec_candidates(spec_path)

        for candidate in candidates:
            if candidate.exists():
                return candidate

        # 未找到：生成详细错误信息
        search_locations = '\n  - '.join(str(c) for c in candidates)
        raise FileNotFoundError(
            f"OpenAPI 文件不存在: {self.spec_file}\n"
            f"已搜索以下位置:\n  - {search_locations}"
        )

    def _find_spec_candidates(self, spec_path: Path) -> List[Path]:
        """
        查找 OpenAPI 规范文件的候选位置

        Args:
            spec_path: 相对路径

        Returns:
            按优先级排序的候选路径列表
        """
        candidates = []

        # 1. 脚本所在目录（如果提供了 script_path）
        if self.script_path:
            script_dir = Path(self.script_path).parent
            candidates.append(script_dir / spec_path)

            # 1.1 脚本父目录（处理 flows/xxx.flow 和 openapi/xxx.yml 同级的情况）
            script_parent = script_dir.parent
            candidates.append(script_parent / spec_path)

        # 2. 项目根目录
        project_root = self._find_project_root()
        if project_root:
            candidates.append(project_root / spec_path)

        # 3. 当前工作目录
        candidates.append(Path.cwd() / spec_path)

        # 4. OPENAPI_PATH 环境变量指定的目录
        if 'OPENAPI_PATH' in os.environ:
            openapi_dir = Path(os.environ['OPENAPI_PATH'])
            candidates.append(openapi_dir / spec_path)

        return candidates

    @staticmethod
    def _find_project_root() -> Optional[Path]:
        """
        查找项目根目录

        查找标志：.git, pyproject.toml, setup.py, package.json 等

        Returns:
            项目根目录路径，如果找不到返回 None
        """
        current = Path.cwd()
        markers = ['.git', 'pyproject.toml', 'setup.py', 'package.json', '.project-root']

        # 向上遍历最多 10 层
        for _ in range(10):
            for marker in markers:
                if (current / marker).exists():
                    return current

            parent = current.parent
            if parent == current:  # 到达文件系统根目录
                break
            current = parent

        return None

    def _load_spec(self) -> Dict[str, Any]:
        """
        加载 OpenAPI YAML/JSON 文件

        Returns:
            解析后的 OpenAPI 规范字典

        Raises:
            ValueError: 文件格式不支持或解析失败
        """
        path = self.resolved_path

        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix in ['.yml', '.yaml']:
                    return yaml.safe_load(f)
                elif path.suffix == '.json':
                    return json.load(f)
                else:
                    raise ValueError(f"不支持的文件格式: {path.suffix}（仅支持 .yml, .yaml, .json）")
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 解析失败: {str(e)}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"加载 OpenAPI 文件失败: {str(e)}")

    def _extract_operations(self) -> Dict[str, Dict[str, Any]]:
        """
        从 OpenAPI 提取所有操作

        Returns:
            {operationId: {path, method, parameters, requestBody, responses, ...}}

        Raises:
            ValueError: OpenAPI 格式错误
        """
        operations = {}

        if 'paths' not in self.spec:
            raise ValueError(f"OpenAPI 文件缺少 'paths' 字段: {self.spec_file}")

        for path, methods in self.spec['paths'].items():
            if not isinstance(methods, dict):
                continue

            for method, operation in methods.items():
                # 只处理 HTTP 方法（跳过 $ref, parameters 等特殊字段）
                if method.lower() not in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options', 'trace']:
                    continue

                if not isinstance(operation, dict):
                    continue

                # 必须有 operationId
                if 'operationId' not in operation:
                    print(f"[警告] {path} {method.upper()} 缺少 operationId，跳过")
                    continue

                operation_id = operation['operationId']

                if operation_id in operations:
                    raise ValueError(
                        f"重复的 operationId: {operation_id} "
                        f"(文件: {self.spec_file}, 路径: {path})"
                    )

                operations[operation_id] = {
                    'path': path,
                    'method': method.upper(),
                    'parameters': operation.get('parameters', []),
                    'requestBody': operation.get('requestBody'),
                    'responses': operation.get('responses', {}),
                    'summary': operation.get('summary', ''),
                    'description': operation.get('description', ''),
                    'tags': operation.get('tags', []),
                    'deprecated': operation.get('deprecated', False),
                }

        return operations

    def get_base_url(self) -> Optional[str]:
        """
        获取 OpenAPI 定义的默认 base URL

        Returns:
            默认的 server URL，如果没有定义则返回 None
        """
        if 'servers' in self.spec and len(self.spec['servers']) > 0:
            return self.spec['servers'][0].get('url')
        return None

    def get_operation(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定 operationId 的操作定义

        Args:
            operation_id: 操作 ID

        Returns:
            操作定义字典，如果不存在则返回 None
        """
        return self.operations.get(operation_id)

    def has_operation(self, operation_id: str) -> bool:
        """
        检查是否存在指定的 operationId

        Args:
            operation_id: 操作 ID

        Returns:
            True 如果存在，False 否则
        """
        return operation_id in self.operations

    def list_operations(self) -> List[str]:
        """
        列出所有 operationId

        Returns:
            operationId 列表
        """
        return list(self.operations.keys())

    def get_info(self) -> Dict[str, Any]:
        """
        获取 API 信息（title, version 等）

        Returns:
            info 字段内容
        """
        return self.spec.get('info', {})

    def get_security_config(self, env_var: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        从 OpenAPI 规范提取认证配置

        支持自动从 components.securitySchemes 提取认证配置，
        并从环境变量读取敏感信息（如 token）

        Args:
            env_var: 环境变量名，用于读取 token/key（可选）

        Returns:
            适用于 AuthHandler 的认证配置字典，如果没有定义则返回 None

        示例返回值：
            {
                "type": "bearer",
                "token": "xxx..."  # 从环境变量读取
            }
        """
        import os

        # 1. 检查是否定义了 security schemes
        components = self.spec.get('components', {})
        security_schemes = components.get('securitySchemes', {})

        if not security_schemes:
            return None

        # 2. 获取第一个 security scheme（通常 API 只有一个）
        scheme_name = next(iter(security_schemes.keys()), None)
        if not scheme_name:
            return None

        scheme = security_schemes[scheme_name]
        scheme_type = scheme.get('type', '').lower()

        # 3. 根据类型构建认证配置
        if scheme_type == 'http':
            http_scheme = scheme.get('scheme', '').lower()

            # Bearer Token
            if http_scheme == 'bearer':
                # 从环境变量读取 token
                token = None
                if env_var:
                    token = os.environ.get(env_var)

                if not token:
                    # 尝试默认环境变量名
                    default_env = f"{scheme_name.upper()}_TOKEN"
                    token = os.environ.get(default_env)

                return {
                    'type': 'bearer',
                    'token': token
                } if token else None

            # Basic Auth
            elif http_scheme == 'basic':
                username = os.environ.get(f"{scheme_name.upper()}_USERNAME")
                password = os.environ.get(f"{scheme_name.upper()}_PASSWORD")

                return {
                    'type': 'basic',
                    'username': username,
                    'password': password
                } if username and password else None

        # API Key
        elif scheme_type == 'apikey':
            key_name = scheme.get('name')
            location = scheme.get('in', 'header')  # header or query

            # 从环境变量读取 API key
            api_key = None
            if env_var:
                api_key = os.environ.get(env_var)

            if not api_key:
                default_env = f"{scheme_name.upper()}_KEY"
                api_key = os.environ.get(default_env)

            return {
                'type': 'apikey',
                'key': key_name,
                'value': api_key,
                'location': location
            } if api_key else None

        # OAuth2
        elif scheme_type == 'oauth2':
            flows = scheme.get('flows', {})
            # 支持 clientCredentials flow
            if 'clientCredentials' in flows:
                flow = flows['clientCredentials']
                token_url = flow.get('tokenUrl')

                client_id = os.environ.get(f"{scheme_name.upper()}_CLIENT_ID")
                client_secret = os.environ.get(f"{scheme_name.upper()}_CLIENT_SECRET")
                scope = flow.get('scopes', {})
                scope_str = ' '.join(scope.keys()) if scope else ''

                return {
                    'type': 'oauth2',
                    'token_url': token_url,
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'scope': scope_str
                } if client_id and client_secret else None

        return None

    def __repr__(self) -> str:
        """字符串表示"""
        info = self.get_info()
        title = info.get('title', 'Unknown API')
        version = info.get('version', 'unknown')
        op_count = len(self.operations)
        return f"<OpenAPISpec '{title}' v{version} ({op_count} operations)>"
