"""
配置数据结构定义
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class GlobalSettings:
    """全局设置"""
    timeout: int = 30000          # 默认超时时间（毫秒）
    retry_count: int = 3          # 默认重试次数
    retry_delay: int = 1000       # 重试间隔（毫秒）


@dataclass
class ProviderConfig:
    """服务提供者配置"""
    type: str                     # 提供者类型
    config: Dict[str, Any]        # 提供者配置
    timeout: Optional[int] = None # 覆盖全局超时
    retry_count: Optional[int] = None
    retry_delay: Optional[int] = None


@dataclass
class ServicesConfig:
    """服务配置"""
    settings: GlobalSettings = field(default_factory=GlobalSettings)
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)


# 支持的提供者类型
SUPPORTED_PROVIDER_TYPES = [
    'random',
    'http',
    'tempmail',
    'imap',
    'sms_activate',
    '2captcha',
]
