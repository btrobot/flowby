"""
内置服务提供者
"""

from typing import Dict, Type
from ..provider import ServiceProvider

from .random import RandomProvider
from .http import HttpProvider

# 内置提供者注册表
BUILTIN_PROVIDERS: Dict[str, Type[ServiceProvider]] = {
    "random": RandomProvider,
    "http": HttpProvider,
}
