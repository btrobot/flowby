"""
Config Loader 单元测试

测试 ConfigLoader 核心功能，包括：
1. 基本配置加载
2. 环境变量解析
3. 配置验证
4. 文件错误处理
5. 变量配置加载
6. ConfigError 错误格式化
"""

import os
import tempfile
import pytest
import shutil
from pathlib import Path
from flowby.config import (
    ConfigLoader,
    ConfigError,
    ServicesConfig,
)


class TestBasicConfigLoading:
    """测试基本配置加载"""

    @pytest.fixture
    def temp_dir(self):
        """提供临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def loader(self, temp_dir):
        """提供 ConfigLoader 实例"""
        return ConfigLoader(temp_dir)

    def _write_config(self, temp_dir, filename: str, content: str):
        """写入配置文件"""
        file_path = Path(temp_dir) / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def test_load_empty_services(self, temp_dir, loader):
        """测试加载空服务配置"""
        # Arrange
        self._write_config(temp_dir, "services.yaml", "")

        # Act
        config = loader.load_services()

        # Assert
        assert isinstance(config, ServicesConfig), "应该返回 ServicesConfig 实例"
        assert config.settings.timeout == 30000, "默认 timeout 应该是 30000"
        assert config.settings.retry_count == 3, "默认 retry_count 应该是 3"
        assert len(config.providers) == 0, "空配置应该没有提供者"

    def test_load_services_with_settings(self, temp_dir, loader):
        """测试加载带全局设置的配置"""
        # Arrange
        self._write_config(
            temp_dir,
            "services.yaml",
            """
settings:
  timeout: 60000
  retry_count: 5
  retry_delay: 2000
""",
        )

        # Act
        config = loader.load_services()

        # Assert
        assert config.settings.timeout == 60000, "timeout 应该是 60000"
        assert config.settings.retry_count == 5, "retry_count 应该是 5"
        assert config.settings.retry_delay == 2000, "retry_delay 应该是 2000"

    def test_load_services_with_provider(self, temp_dir, loader):
        """测试加载带提供者的配置"""
        # Arrange
        self._write_config(
            temp_dir,
            "services.yaml",
            """
providers:
  random:
    type: "random"
    config:
      charset: "abc"
""",
        )

        # Act
        config = loader.load_services()

        # Assert
        assert "random" in config.providers, "应该包含 random 提供者"
        assert config.providers["random"].type == "random", "提供者类型应该是 random"
        assert config.providers["random"].config["charset"] == "abc", "配置应该包含 charset"

    def test_load_services_with_multiple_providers(self, temp_dir, loader):
        """测试加载多个提供者"""
        # Arrange
        self._write_config(
            temp_dir,
            "services.yaml",
            """
providers:
  random:
    type: "random"
    config: {}
  email:
    type: "tempmail"
    config:
      domain: "test.com"
    timeout: 60000
""",
        )

        # Act
        config = loader.load_services()

        # Assert
        assert len(config.providers) == 2, "应该有 2 个提供者"
        assert config.providers["random"].type == "random", "random 提供者类型应该正确"
        assert config.providers["email"].type == "tempmail", "email 提供者类型应该是 tempmail"
        assert config.providers["email"].timeout == 60000, "email 提供者应该有自定义 timeout"

    @pytest.mark.parametrize(
        "settings,expected",
        [
            ({"timeout": 60000}, {"timeout": 60000, "retry_count": 3}),
            ({"retry_count": 5}, {"timeout": 30000, "retry_count": 5}),
            ({"retry_delay": 2000}, {"timeout": 30000, "retry_delay": 2000}),
        ],
    )
    def test_various_global_settings(self, temp_dir, loader, settings, expected):
        """测试各种全局设置"""
        # Arrange
        yaml_content = "settings:\n"
        for key, value in settings.items():
            yaml_content += f"  {key}: {value}\n"
        self._write_config(temp_dir, "services.yaml", yaml_content)

        # Act
        config = loader.load_services()

        # Assert
        for key, value in expected.items():
            actual = getattr(config.settings, key)
            assert actual == value, f"{key} 应该是 {value}，实际是 {actual}"


class TestEnvironmentVariableResolution:
    """测试环境变量解析"""

    @pytest.fixture
    def temp_dir(self):
        """提供临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def loader(self, temp_dir):
        """提供 ConfigLoader 实例"""
        return ConfigLoader(temp_dir)

    def _write_config(self, temp_dir, filename: str, content: str):
        """写入配置文件"""
        file_path = Path(temp_dir) / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def test_env_var_resolution(self, temp_dir, loader):
        """测试环境变量解析"""
        # Arrange
        os.environ["TEST_API_KEY"] = "secret123"
        self._write_config(
            temp_dir,
            "services.yaml",
            """
providers:
  api:
    type: "http"
    config:
      api_key: "${TEST_API_KEY}"
""",
        )

        try:
            # Act
            config = loader.load_services()

            # Assert
            assert (
                config.providers["api"].config["api_key"] == "secret123"
            ), "环境变量应该被正确解析"
        finally:
            del os.environ["TEST_API_KEY"]

    def test_env_var_with_env_prefix(self, temp_dir, loader):
        """测试带 ENV: 前缀的环境变量"""
        # Arrange
        os.environ["MY_TOKEN"] = "token456"
        self._write_config(
            temp_dir,
            "services.yaml",
            """
providers:
  api:
    type: "http"
    config:
      token: "${ENV:MY_TOKEN}"
""",
        )

        try:
            # Act
            config = loader.load_services()

            # Assert
            assert (
                config.providers["api"].config["token"] == "token456"
            ), "带 ENV: 前缀的环境变量应该被正确解析"
        finally:
            del os.environ["MY_TOKEN"]

    def test_env_var_with_default(self, temp_dir, loader):
        """测试环境变量默认值"""
        # Arrange
        # 确保变量不存在
        if "NONEXISTENT_VAR" in os.environ:
            del os.environ["NONEXISTENT_VAR"]

        self._write_config(
            temp_dir,
            "services.yaml",
            """
providers:
  api:
    type: "http"
    config:
      key: "${NONEXISTENT_VAR:default_value}"
""",
        )

        # Act
        config = loader.load_services()

        # Assert
        assert config.providers["api"].config["key"] == "default_value", "应该使用默认值"

    def test_env_var_missing_raises_error(self, temp_dir, loader):
        """测试缺失的环境变量报错"""
        # Arrange
        if "MISSING_VAR" in os.environ:
            del os.environ["MISSING_VAR"]

        self._write_config(
            temp_dir,
            "services.yaml",
            """
providers:
  api:
    type: "http"
    config:
      key: "${MISSING_VAR}"
""",
        )

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            loader.load_services()

        error_message = str(exc_info.value)
        assert "MISSING_VAR" in error_message, "错误消息应该包含变量名"
        assert "未设置" in error_message, "错误消息应该说明未设置"

    def test_multiple_env_vars_in_string(self, temp_dir, loader):
        """测试字符串中多个环境变量"""
        # Arrange
        os.environ["HOST"] = "localhost"
        os.environ["PORT"] = "8080"
        self._write_config(
            temp_dir,
            "services.yaml",
            """
providers:
  api:
    type: "http"
    config:
      url: "http://${HOST}:${PORT}"
""",
        )

        try:
            # Act
            config = loader.load_services()

            # Assert
            assert (
                config.providers["api"].config["url"] == "http://localhost:8080"
            ), "多个环境变量应该都被正确替换"
        finally:
            del os.environ["HOST"]
            del os.environ["PORT"]

    @pytest.mark.parametrize(
        "env_var,value,expected",
        [
            ("TEST_KEY", "secret", "secret"),
            ("TEST_TOKEN", "token123", "token123"),
            ("TEST_URL", "https://api.example.com", "https://api.example.com"),
        ],
    )
    def test_various_env_var_values(self, temp_dir, loader, env_var, value, expected):
        """测试各种环境变量值"""
        # Arrange
        os.environ[env_var] = value
        self._write_config(
            temp_dir,
            "services.yaml",
            f"""
providers:
  api:
    type: "http"
    config:
      value: "${{{env_var}}}"
""",
        )

        try:
            # Act
            config = loader.load_services()

            # Assert
            assert config.providers["api"].config["value"] == expected
        finally:
            del os.environ[env_var]


class TestConfigValidation:
    """测试配置验证"""

    @pytest.fixture
    def temp_dir(self):
        """提供临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def loader(self, temp_dir):
        """提供 ConfigLoader 实例"""
        return ConfigLoader(temp_dir)

    def _write_config(self, temp_dir, filename: str, content: str):
        """写入配置文件"""
        file_path = Path(temp_dir) / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def test_invalid_timeout_too_small(self, temp_dir, loader):
        """测试超时值过小"""
        # Arrange
        self._write_config(
            temp_dir,
            "services.yaml",
            """
settings:
  timeout: 500
""",
        )

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            loader.load_services()

        error_message = str(exc_info.value)
        assert "timeout" in error_message, "错误消息应该包含 timeout"
        assert "500" in error_message, "错误消息应该包含无效值"

    def test_invalid_timeout_too_large(self, temp_dir, loader):
        """测试超时值过大"""
        # Arrange
        self._write_config(
            temp_dir,
            "services.yaml",
            """
settings:
  timeout: 400000
""",
        )

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            loader.load_services()

        assert "timeout" in str(exc_info.value), "错误消息应该包含 timeout"

    def test_invalid_retry_count(self, temp_dir, loader):
        """测试无效的重试次数"""
        # Arrange
        self._write_config(
            temp_dir,
            "services.yaml",
            """
settings:
  retry_count: 20
""",
        )

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            loader.load_services()

        assert "retry_count" in str(exc_info.value), "错误消息应该包含 retry_count"

    def test_missing_provider_type(self, temp_dir, loader):
        """测试缺少提供者类型"""
        # Arrange
        self._write_config(
            temp_dir,
            "services.yaml",
            """
providers:
  api:
    config:
      url: "http://test.com"
""",
        )

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            loader.load_services()

        assert "type" in str(exc_info.value), "错误消息应该包含 type"

    def test_unknown_provider_type(self, temp_dir, loader):
        """测试未知的提供者类型"""
        # Arrange
        self._write_config(
            temp_dir,
            "services.yaml",
            """
providers:
  api:
    type: "unknown_type"
    config: {}
""",
        )

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            loader.load_services()

        error_message = str(exc_info.value)
        assert "unknown_type" in error_message, "错误消息应该包含未知类型"
        assert "不支持" in error_message, "错误消息应该说明不支持"

    def test_missing_provider_config(self, temp_dir, loader):
        """测试缺少提供者配置"""
        # Arrange
        self._write_config(
            temp_dir,
            "services.yaml",
            """
providers:
  random:
    type: "random"
""",
        )

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            loader.load_services()

        assert "config" in str(exc_info.value), "错误消息应该包含 config"

    @pytest.mark.parametrize(
        "invalid_config,expected_error",
        [
            ({"timeout": 500}, "timeout"),
            ({"timeout": 400000}, "timeout"),
            ({"retry_count": 20}, "retry_count"),
            ({"retry_count": -1}, "retry_count"),
        ],
    )
    def test_various_invalid_settings(self, temp_dir, loader, invalid_config, expected_error):
        """测试各种无效设置"""
        # Arrange
        yaml_content = "settings:\n"
        for key, value in invalid_config.items():
            yaml_content += f"  {key}: {value}\n"
        self._write_config(temp_dir, "services.yaml", yaml_content)

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            loader.load_services()

        assert expected_error in str(exc_info.value), f"错误消息应该包含 {expected_error}"


class TestFileErrorHandling:
    """测试文件错误处理"""

    @pytest.fixture
    def temp_dir(self):
        """提供临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def loader(self, temp_dir):
        """提供 ConfigLoader 实例"""
        return ConfigLoader(temp_dir)

    def _write_config(self, temp_dir, filename: str, content: str):
        """写入配置文件"""
        file_path = Path(temp_dir) / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def test_file_not_found(self, loader):
        """测试文件不存在"""
        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            loader.load_services("nonexistent.yaml")

        assert "不存在" in str(exc_info.value), "错误消息应该说明文件不存在"

    def test_invalid_yaml_syntax(self, temp_dir, loader):
        """测试无效的 YAML 语法"""
        # Arrange
        self._write_config(
            temp_dir,
            "services.yaml",
            """
providers:
  - invalid: yaml
  syntax: here
""",
        )

        # Act & Assert
        with pytest.raises(ConfigError) as exc_info:
            loader.load_services()

        assert "YAML" in str(exc_info.value), "错误消息应该包含 YAML"

    def test_empty_file_loads_successfully(self, temp_dir, loader):
        """测试空文件成功加载"""
        # Arrange
        self._write_config(temp_dir, "services.yaml", "")

        # Act
        config = loader.load_services()

        # Assert
        assert isinstance(config, ServicesConfig), "空文件应该加载成功"

    @pytest.mark.parametrize(
        "invalid_yaml",
        [
            "providers:\n  - invalid: yaml",
            "settings:\n  timeout: [1, 2, 3]",
            "providers:\n  test:\n    type: random\n  config: {}",  # Wrong indentation
        ],
    )
    def test_various_invalid_yaml_formats(self, temp_dir, loader, invalid_yaml):
        """测试各种无效的 YAML 格式"""
        # Arrange
        self._write_config(temp_dir, "services.yaml", invalid_yaml)

        # Act & Assert
        # 各种无效格式可能抛出 ConfigError, AttributeError, TypeError 等
        with pytest.raises((ConfigError, AttributeError, TypeError)):
            loader.load_services()


class TestVariablesLoading:
    """测试变量配置加载"""

    @pytest.fixture
    def temp_dir(self):
        """提供临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def loader(self, temp_dir):
        """提供 ConfigLoader 实例"""
        return ConfigLoader(temp_dir)

    def _write_config(self, temp_dir, filename: str, content: str):
        """写入配置文件"""
        file_path = Path(temp_dir) / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def test_load_variables(self, temp_dir, loader):
        """测试加载变量配置"""
        # Arrange
        self._write_config(
            temp_dir,
            "variables.yaml",
            """
user:
  first_name: "John"
  last_name: "Doe"
config:
  timeout: 30
""",
        )

        # Act
        variables = loader.load_variables()

        # Assert
        assert variables["user"]["first_name"] == "John", "first_name 应该是 John"
        assert variables["user"]["last_name"] == "Doe", "last_name 应该是 Doe"
        assert variables["config"]["timeout"] == 30, "timeout 应该是 30"

    def test_load_variables_not_found(self, loader):
        """测试变量文件不存在返回空字典"""
        # Act
        variables = loader.load_variables("nonexistent.yaml")

        # Assert
        assert variables == {}, "文件不存在应该返回空字典"

    def test_load_variables_with_env_vars(self, temp_dir, loader):
        """测试变量配置中的环境变量"""
        # Arrange
        os.environ["USER_EMAIL"] = "test@example.com"
        self._write_config(
            temp_dir,
            "variables.yaml",
            """
user:
  email: "${USER_EMAIL}"
""",
        )

        try:
            # Act
            variables = loader.load_variables()

            # Assert
            assert variables["user"]["email"] == "test@example.com", "环境变量应该被正确解析"
        finally:
            del os.environ["USER_EMAIL"]

    def test_load_empty_variables(self, temp_dir, loader):
        """测试加载空变量文件"""
        # Arrange
        self._write_config(temp_dir, "variables.yaml", "")

        # Act
        variables = loader.load_variables()

        # Assert
        assert variables == {} or variables is None, "空文件应该返回空字典或 None"

    @pytest.mark.parametrize(
        "var_name,var_value",
        [
            ("username", "john_doe"),
            ("email", "test@example.com"),
            ("age", 25),
            ("active", True),
        ],
    )
    def test_various_variable_types(self, temp_dir, loader, var_name, var_value):
        """测试各种变量类型"""
        # Arrange
        yaml_content = f"test:\n  {var_name}: "
        if isinstance(var_value, str):
            yaml_content += f'"{var_value}"'
        else:
            yaml_content += str(var_value)

        self._write_config(temp_dir, "variables.yaml", yaml_content)

        # Act
        variables = loader.load_variables()

        # Assert
        assert variables["test"][var_name] == var_value, f"{var_name} 应该是 {var_value}"


class TestConfigErrorFormatting:
    """测试 ConfigError 错误格式化"""

    def test_basic_error(self):
        """测试基本错误消息"""
        # Arrange & Act
        error = ConfigError("测试错误")

        # Assert
        assert "测试错误" in str(error), "错误消息应该包含原始文本"

    def test_error_with_file(self):
        """测试带文件路径的错误"""
        # Arrange & Act
        error = ConfigError("测试错误", file_path="config/test.yaml")

        # Assert
        message = str(error)
        assert "测试错误" in message, "错误消息应该包含原始文本"
        assert "config/test.yaml" in message, "错误消息应该包含文件路径"

    def test_error_with_location(self):
        """测试带位置信息的错误"""
        # Arrange & Act
        error = ConfigError("测试错误", line=10, column=5)

        # Assert
        message = str(error)
        assert "第 10 行" in message, "错误消息应该包含行号"
        assert "第 5 列" in message, "错误消息应该包含列号"

    def test_error_with_suggestion(self):
        """测试带建议的错误"""
        # Arrange & Act
        error = ConfigError("测试错误", suggestion="请检查配置")

        # Assert
        message = str(error)
        assert "建议" in message, "错误消息应该包含建议"
        assert "请检查配置" in message, "错误消息应该包含建议内容"

    def test_error_with_all_fields(self):
        """测试带所有字段的错误"""
        # Arrange & Act
        error = ConfigError(
            "测试错误", file_path="config/test.yaml", line=10, column=5, suggestion="请检查配置"
        )

        # Assert
        message = str(error)
        assert "测试错误" in message, "应该包含错误消息"
        assert "config/test.yaml" in message, "应该包含文件路径"
        assert "第 10 行" in message, "应该包含行号"
        assert "第 5 列" in message, "应该包含列号"
        assert "请检查配置" in message, "应该包含建议"

    @pytest.mark.parametrize(
        "message,file_path,line,column",
        [
            ("错误1", "file1.yaml", 1, 1),
            ("错误2", "file2.yaml", 10, 5),
            ("错误3", "config/test.yaml", 20, 15),
        ],
    )
    def test_various_error_combinations(self, message, file_path, line, column):
        """测试各种错误组合"""
        # Arrange & Act
        error = ConfigError(message, file_path=file_path, line=line, column=column)

        # Assert
        error_str = str(error)
        assert message in error_str, f"错误消息应该包含 {message}"
        assert file_path in error_str, f"错误消息应该包含文件路径 {file_path}"
