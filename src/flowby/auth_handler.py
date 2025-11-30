"""
Authentication Handler - v4.2 Phase 2

支持多种认证方式的认证处理器。

认证类型:
- bearer: Bearer Token 认证
- apikey: API Key 认证（header 或 query）
- basic: HTTP Basic Auth
- oauth2: OAuth2 客户端凭证流
"""

import base64
import requests
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta


class AuthHandler:
    """
    认证处理器

    负责处理各种认证方式，生成相应的 HTTP headers 和参数。
    """

    def __init__(self, auth_config: Dict[str, Any]):
        """
        初始化认证处理器

        Args:
            auth_config: 认证配置字典

        支持的配置格式:

        1. Bearer Token:
            {
                "type": "bearer",
                "token": "eyJhbGciOiJIUzI1NiIs..."
            }

        2. API Key:
            {
                "type": "apikey",
                "key": "X-API-Key",
                "value": "my-api-key-123",
                "location": "header"  # 或 "query"
            }

        3. Basic Auth:
            {
                "type": "basic",
                "username": "user",
                "password": "pass"
            }

        4. OAuth2 (Client Credentials):
            {
                "type": "oauth2",
                "token_url": "https://oauth.example.com/token",
                "client_id": "client123",
                "client_secret": "secret456",
                "scope": "read write"  # 可选
            }

        5. 简化形式（向后兼容 Phase 1）:
            {
                "Authorization": "Bearer token..."
            }
        """
        self.auth_config = auth_config
        self.auth_type = auth_config.get('type', 'custom')

        # OAuth2 token 缓存
        self._oauth2_token = None
        self._oauth2_token_expiry = None

    def get_auth_headers(self) -> Dict[str, str]:
        """
        获取认证 headers

        Returns:
            认证相关的 HTTP headers
        """
        if self.auth_type == 'bearer':
            return self._get_bearer_headers()
        elif self.auth_type == 'apikey':
            if self.auth_config.get('location') == 'header':
                return self._get_apikey_headers()
            else:
                return {}
        elif self.auth_type == 'basic':
            return self._get_basic_headers()
        elif self.auth_type == 'oauth2':
            return self._get_oauth2_headers()
        elif self.auth_type == 'custom':
            # Phase 1 简化形式：直接使用配置作为 headers
            return dict(self.auth_config)
        else:
            raise ValueError(f"不支持的认证类型: {self.auth_type}")

    def get_auth_params(self) -> Dict[str, str]:
        """
        获取认证 query 参数

        Returns:
            认证相关的 query 参数
        """
        if self.auth_type == 'apikey' and self.auth_config.get('location') == 'query':
            return self._get_apikey_params()
        return {}

    def _get_bearer_headers(self) -> Dict[str, str]:
        """Bearer Token 认证"""
        token = self.auth_config.get('token')
        if not token:
            raise ValueError("Bearer 认证缺少 'token' 配置")

        return {
            'Authorization': f'Bearer {token}'
        }

    def _get_apikey_headers(self) -> Dict[str, str]:
        """API Key 认证（header）"""
        key = self.auth_config.get('key')
        value = self.auth_config.get('value')

        if not key or not value:
            raise ValueError("API Key 认证缺少 'key' 或 'value' 配置")

        return {
            key: value
        }

    def _get_apikey_params(self) -> Dict[str, str]:
        """API Key 认证（query）"""
        key = self.auth_config.get('key')
        value = self.auth_config.get('value')

        if not key or not value:
            raise ValueError("API Key 认证缺少 'key' 或 'value' 配置")

        return {
            key: value
        }

    def _get_basic_headers(self) -> Dict[str, str]:
        """HTTP Basic Auth"""
        username = self.auth_config.get('username')
        password = self.auth_config.get('password')

        if not username or not password:
            raise ValueError("Basic Auth 认证缺少 'username' 或 'password' 配置")

        # 编码为 base64
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

        return {
            'Authorization': f'Basic {encoded}'
        }

    def _get_oauth2_headers(self) -> Dict[str, str]:
        """OAuth2 客户端凭证流"""
        # 检查 token 是否有效
        if self._is_oauth2_token_valid():
            return {
                'Authorization': f'Bearer {self._oauth2_token}'
            }

        # 获取新 token
        token = self._fetch_oauth2_token()

        return {
            'Authorization': f'Bearer {token}'
        }

    def _is_oauth2_token_valid(self) -> bool:
        """检查 OAuth2 token 是否有效"""
        if not self._oauth2_token or not self._oauth2_token_expiry:
            return False

        # 提前 60 秒刷新 token
        return datetime.now() < (self._oauth2_token_expiry - timedelta(seconds=60))

    def _fetch_oauth2_token(self) -> str:
        """获取 OAuth2 access token"""
        token_url = self.auth_config.get('token_url')
        client_id = self.auth_config.get('client_id')
        client_secret = self.auth_config.get('client_secret')
        scope = self.auth_config.get('scope', '')

        if not token_url or not client_id or not client_secret:
            raise ValueError(
                "OAuth2 认证缺少 'token_url', 'client_id' 或 'client_secret' 配置"
            )

        # 构建请求
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        }

        if scope:
            data['scope'] = scope

        # 发送请求
        try:
            response = requests.post(
                token_url,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            response.raise_for_status()

            # 解析响应
            token_data = response.json()
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)  # 默认 1 小时

            if not access_token:
                raise ValueError("OAuth2 token 响应中缺少 'access_token'")

            # 缓存 token
            self._oauth2_token = access_token
            self._oauth2_token_expiry = datetime.now() + timedelta(seconds=expires_in)

            return access_token

        except requests.exceptions.RequestException as e:
            raise ValueError(f"获取 OAuth2 token 失败: {str(e)}")


def create_auth_handler(auth_config: Optional[Dict[str, Any]]) -> Optional[AuthHandler]:
    """
    创建认证处理器

    Args:
        auth_config: 认证配置字典

    Returns:
        AuthHandler 实例，如果没有认证配置则返回 None
    """
    if not auth_config:
        return None

    return AuthHandler(auth_config)
