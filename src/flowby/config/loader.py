"""
配置加载器

负责加载 YAML 配置文件，解析环境变量
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional

import yaml
from dotenv import load_dotenv

from .schema import (
    ServicesConfig,
    GlobalSettings,
    ProviderConfig,
    SUPPORTED_PROVIDER_TYPES,
)
from .errors import ConfigError


class ConfigLoader:
    """配置加载器"""

    # 环境变量引用模式: ${VAR} 或 ${ENV:VAR} 或 ${ENV:VAR:default}
    ENV_VAR_PATTERN = re.compile(r'\$\{(?:ENV:)?([^}:]+)(?::([^}]*))?\}')

    def __init__(self, config_dir: str = "config"):
        """
        初始化配置加载器

        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self._env_loaded = False

    def _ensure_env_loaded(self):
        """确保环境变量已加载"""
        if self._env_loaded:
            return

        # 尝试加载 .env 文件
        env_file = self.config_dir / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        else:
            # 尝试从当前目录加载
            load_dotenv()

        self._env_loaded = True

    def load_services(self, path: str = "services.yaml") -> ServicesConfig:
        """
        加载服务配置

        Args:
            path: 配置文件路径（相对于 config_dir）

        Returns:
            ServicesConfig 对象

        Raises:
            ConfigError: 配置文件不存在或验证失败
        """
        file_path = self.config_dir / path

        if not file_path.exists():
            raise ConfigError(
                f"配置文件不存在: {path}",
                file_path=str(file_path),
                suggestion=f"请创建配置文件 {file_path}"
            )

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(
                f"YAML 语法错误: {e}",
                file_path=str(file_path)
            )

        if raw_data is None:
            raw_data = {}

        # 解析环境变量
        self._ensure_env_loaded()
        resolved_data = self._resolve_env_vars(raw_data, str(file_path))

        # 转换为配置对象
        return self._parse_services_config(resolved_data, str(file_path))

    def load_variables(self, path: str = "variables.yaml") -> Dict[str, Any]:
        """
        加载变量配置

        Args:
            path: 配置文件路径（相对于 config_dir）

        Returns:
            变量字典

        Raises:
            ConfigError: 配置文件不存在或解析失败
        """
        file_path = self.config_dir / path

        if not file_path.exists():
            # 变量文件是可选的
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(
                f"YAML 语法错误: {e}",
                file_path=str(file_path)
            )

        if raw_data is None:
            return {}

        # 解析环境变量
        self._ensure_env_loaded()
        return self._resolve_env_vars(raw_data, str(file_path))

    def _resolve_env_vars(self, data: Any, file_path: str) -> Any:
        """
        递归解析数据中的环境变量引用

        Args:
            data: 要解析的数据
            file_path: 文件路径（用于错误报告）

        Returns:
            解析后的数据
        """
        if isinstance(data, str):
            return self._resolve_env_string(data, file_path)
        elif isinstance(data, dict):
            return {k: self._resolve_env_vars(v, file_path) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._resolve_env_vars(item, file_path) for item in data]
        else:
            return data

    def _resolve_env_string(self, value: str, file_path: str) -> str:
        """
        解析字符串中的环境变量引用

        Args:
            value: 包含 ${...} 的字符串
            file_path: 文件路径

        Returns:
            解析后的字符串

        Raises:
            ConfigError: 必需的环境变量未设置
        """
        def replace_env_var(match):
            var_name = match.group(1)
            default_value = match.group(2)

            env_value = os.environ.get(var_name)

            if env_value is not None:
                return env_value
            elif default_value is not None:
                return default_value
            else:
                raise ConfigError(
                    f"环境变量 '{var_name}' 未设置",
                    file_path=file_path,
                    suggestion=f"请设置环境变量:\n"
                               f"  1. export {var_name}=your-value\n"
                               f"  2. 或在 .env 文件中添加: {var_name}=your-value\n"
                               f"  3. 或使用默认值: ${{{var_name}:default-value}}"
                )

        return self.ENV_VAR_PATTERN.sub(replace_env_var, value)

    def _parse_services_config(self, data: Dict[str, Any], file_path: str) -> ServicesConfig:
        """
        解析服务配置数据

        Args:
            data: 原始配置数据
            file_path: 文件路径

        Returns:
            ServicesConfig 对象

        Raises:
            ConfigError: 配置验证失败
        """
        # 解析全局设置
        settings_data = data.get('settings', {})
        settings = GlobalSettings(
            timeout=settings_data.get('timeout', 30000),
            retry_count=settings_data.get('retry_count', 3),
            retry_delay=settings_data.get('retry_delay', 1000)
        )

        # 验证设置值
        self._validate_settings(settings, file_path)

        # 解析提供者配置
        providers_data = data.get('providers', {})
        providers = {}

        for name, provider_data in providers_data.items():
            provider = self._parse_provider_config(name, provider_data, file_path)
            providers[name] = provider

        return ServicesConfig(settings=settings, providers=providers)

    def _validate_settings(self, settings: GlobalSettings, file_path: str):
        """验证全局设置"""
        if settings.timeout < 1000:
            raise ConfigError(
                f"timeout 值 {settings.timeout} 小于最小值 1000",
                file_path=file_path,
                suggestion="timeout 应至少为 1000 毫秒"
            )

        if settings.timeout > 300000:
            raise ConfigError(
                f"timeout 值 {settings.timeout} 大于最大值 300000",
                file_path=file_path,
                suggestion="timeout 不应超过 300000 毫秒（5分钟）"
            )

        if settings.retry_count < 0 or settings.retry_count > 10:
            raise ConfigError(
                f"retry_count 值 {settings.retry_count} 不在有效范围 [0, 10]",
                file_path=file_path
            )

        if settings.retry_delay < 0:
            raise ConfigError(
                f"retry_delay 值 {settings.retry_delay} 不能为负数",
                file_path=file_path
            )

    def _parse_provider_config(
        self,
        name: str,
        data: Dict[str, Any],
        file_path: str
    ) -> ProviderConfig:
        """
        解析单个提供者配置

        Args:
            name: 提供者名称
            data: 提供者配置数据
            file_path: 文件路径

        Returns:
            ProviderConfig 对象
        """
        # 验证 type 字段
        if 'type' not in data:
            raise ConfigError(
                f"提供者 '{name}' 缺少 'type' 字段",
                file_path=file_path
            )

        provider_type = data['type']
        if provider_type not in SUPPORTED_PROVIDER_TYPES:
            raise ConfigError(
                f"提供者 '{name}' 的类型 '{provider_type}' 不支持",
                file_path=file_path,
                suggestion=f"支持的类型: {', '.join(SUPPORTED_PROVIDER_TYPES)}"
            )

        # 验证 config 字段
        if 'config' not in data:
            raise ConfigError(
                f"提供者 '{name}' 缺少 'config' 字段",
                file_path=file_path
            )

        return ProviderConfig(
            type=provider_type,
            config=data['config'],
            timeout=data.get('timeout'),
            retry_count=data.get('retry_count'),
            retry_delay=data.get('retry_delay')
        )
