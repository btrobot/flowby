"""
RandomProvider 单元测试

测试 RandomProvider 的所有功能，包括：
1. password 生成 (默认、自定义长度、字符类型)
2. username 生成 (前缀、后缀)
3. string 生成 (各种字符集)
4. number 生成 (范围控制)
5. email 生成 (域名、长度)
6. phone 生成 (国家代码、长度)
7. choice 随机选择
8. 自定义配置测试
"""

import pytest
import re
from flowby.config.schema import ServicesConfig, GlobalSettings, ProviderConfig
from flowby.services import ServiceRegistry


class TestPasswordGeneration:
    """测试密码生成功能"""

    @pytest.fixture
    def registry(self):
        """提供 ServiceRegistry 实例"""
        config = ServicesConfig(
            settings=GlobalSettings(),
            providers={"random": ProviderConfig(type="random", config={})},
        )
        registry = ServiceRegistry(config)
        registry.initialize()
        return registry

    def test_password_default_parameters(self, registry):
        """测试默认参数的密码生成"""
        # Arrange & Act
        password = registry.call("random.password")

        # Assert
        assert len(password) == 12, "默认密码长度应该是 12"
        assert any(c.islower() for c in password), "应包含小写字母"
        assert any(c.isupper() for c in password), "应包含大写字母"
        assert any(c.isdigit() for c in password), "应包含数字"

    def test_password_custom_length(self, registry):
        """测试自定义长度密码生成"""
        # Arrange
        length = 20

        # Act
        password = registry.call("random.password", length=length)

        # Assert
        assert len(password) == length, f"密码长度应该是 {length}"

    def test_password_without_special_characters(self, registry):
        """测试不包含特殊字符的密码"""
        # Arrange
        special_chars = "!@#$%^&*()_+-="

        # Act
        password = registry.call("random.password", length=16, special=False)

        # Assert
        assert len(password) == 16, "密码长度应该是 16"
        assert not any(c in special_chars for c in password), "不应包含特殊字符"

    def test_password_only_numeric(self, registry):
        """测试纯数字密码生成"""
        # Arrange & Act
        password = registry.call(
            "random.password", length=8, special=False, upper=False, lower=False, digits=True
        )

        # Assert
        assert len(password) == 8, "密码长度应该是 8"
        assert password.isdigit(), "应该只包含数字"

    def test_password_uniqueness(self, registry):
        """测试密码唯一性（生成多个密码应该不同）"""
        # Arrange
        num_passwords = 10

        # Act
        passwords = [registry.call("random.password") for _ in range(num_passwords)]

        # Assert
        assert len(set(passwords)) == num_passwords, "生成的密码应该各不相同"

    @pytest.mark.parametrize("length", [8, 12, 16, 20, 24])
    def test_password_various_lengths(self, registry, length):
        """测试各种长度的密码生成"""
        # Act
        password = registry.call("random.password", length=length)

        # Assert
        assert len(password) == length, f"密码长度应该是 {length}"


class TestUsernameGeneration:
    """测试用户名生成功能"""

    @pytest.fixture
    def registry(self):
        """提供 ServiceRegistry 实例"""
        config = ServicesConfig(
            settings=GlobalSettings(),
            providers={"random": ProviderConfig(type="random", config={})},
        )
        registry = ServiceRegistry(config)
        registry.initialize()
        return registry

    def test_username_default_parameters(self, registry):
        """测试默认参数的用户名生成"""
        # Arrange & Act
        username = registry.call("random.username")

        # Assert
        assert len(username) == 8, "默认用户名长度应该是 8"
        assert username.isalnum(), "应该只包含字母和数字"
        assert username.islower() or any(c.isdigit() for c in username), "应该包含小写字母或数字"

    def test_username_with_prefix_and_suffix(self, registry):
        """测试带前缀和后缀的用户名"""
        # Arrange
        length = 6
        prefix = "user_"
        suffix = "_test"

        # Act
        username = registry.call("random.username", length=length, prefix=prefix, suffix=suffix)

        # Assert
        assert username.startswith(prefix), f"应该以 {prefix} 开头"
        assert username.endswith(suffix), f"应该以 {suffix} 结尾"
        assert len(username) == length + len(prefix) + len(
            suffix
        ), "总长度应该是 length + prefix + suffix"

    def test_username_custom_length(self, registry):
        """测试自定义长度用户名"""
        # Arrange
        length = 12

        # Act
        username = registry.call("random.username", length=length)

        # Assert
        assert len(username) == length, f"用户名长度应该是 {length}"

    @pytest.mark.parametrize(
        "length,prefix,suffix",
        [
            (8, "test_", ""),
            (10, "", "_user"),
            (6, "u_", "_001"),
            (12, "admin_", "_prod"),
        ],
    )
    def test_username_various_combinations(self, registry, length, prefix, suffix):
        """测试各种前缀后缀组合"""
        # Act
        username = registry.call("random.username", length=length, prefix=prefix, suffix=suffix)

        # Assert
        if prefix:
            assert username.startswith(prefix), f"应该以 {prefix} 开头"
        if suffix:
            assert username.endswith(suffix), f"应该以 {suffix} 结尾"
        assert len(username) == length + len(prefix) + len(suffix)


class TestStringGeneration:
    """测试随机字符串生成功能"""

    @pytest.fixture
    def registry(self):
        """提供 ServiceRegistry 实例"""
        config = ServicesConfig(
            settings=GlobalSettings(),
            providers={"random": ProviderConfig(type="random", config={})},
        )
        registry = ServiceRegistry(config)
        registry.initialize()
        return registry

    def test_string_alpha_charset(self, registry):
        """测试字母字符集"""
        # Arrange
        length = 10

        # Act
        s = registry.call("random.string", length=length, charset="alpha")

        # Assert
        assert len(s) == length, f"字符串长度应该是 {length}"
        assert s.isalpha(), "应该只包含字母"

    def test_string_numeric_charset(self, registry):
        """测试数字字符集"""
        # Arrange
        length = 10

        # Act
        s = registry.call("random.string", length=length, charset="numeric")

        # Assert
        assert len(s) == length, f"字符串长度应该是 {length}"
        assert s.isdigit(), "应该只包含数字"

    def test_string_alphanumeric_charset(self, registry):
        """测试字母数字字符集"""
        # Arrange
        length = 20

        # Act
        s = registry.call("random.string", length=length, charset="alphanumeric")

        # Assert
        assert len(s) == length, f"字符串长度应该是 {length}"
        assert s.isalnum(), "应该只包含字母和数字"

    def test_string_lower_charset(self, registry):
        """测试小写字母字符集"""
        # Arrange
        length = 10

        # Act
        s = registry.call("random.string", length=length, charset="lower")

        # Assert
        assert len(s) == length, f"字符串长度应该是 {length}"
        assert s.islower(), "应该只包含小写字母"
        assert s.isalpha(), "应该只包含字母"

    def test_string_upper_charset(self, registry):
        """测试大写字母字符集"""
        # Arrange
        length = 10

        # Act
        s = registry.call("random.string", length=length, charset="upper")

        # Assert
        assert len(s) == length, f"字符串长度应该是 {length}"
        assert s.isupper(), "应该只包含大写字母"
        assert s.isalpha(), "应该只包含字母"

    @pytest.mark.parametrize(
        "charset,validator",
        [
            ("alpha", lambda s: s.isalpha()),
            ("numeric", lambda s: s.isdigit()),
            ("alphanumeric", lambda s: s.isalnum()),
            ("lower", lambda s: s.islower() and s.isalpha()),
            ("upper", lambda s: s.isupper() and s.isalpha()),
        ],
    )
    def test_string_various_charsets(self, registry, charset, validator):
        """测试各种字符集"""
        # Arrange
        length = 15

        # Act
        s = registry.call("random.string", length=length, charset=charset)

        # Assert
        assert len(s) == length, f"字符串长度应该是 {length}"
        assert validator(s), f"字符串应该符合 {charset} 字符集规则"


class TestNumberGeneration:
    """测试随机数字生成功能"""

    @pytest.fixture
    def registry(self):
        """提供 ServiceRegistry 实例"""
        config = ServicesConfig(
            settings=GlobalSettings(),
            providers={"random": ProviderConfig(type="random", config={})},
        )
        registry = ServiceRegistry(config)
        registry.initialize()
        return registry

    def test_number_default_range(self, registry):
        """测试默认范围数字生成"""
        # Arrange & Act
        num = registry.call("random.number")

        # Assert
        assert 0 <= num <= 100, "默认范围应该是 0-100"

    def test_number_custom_range(self, registry):
        """测试自定义范围数字生成"""
        # Arrange
        min_val = 50
        max_val = 60

        # Act
        num = registry.call("random.number", min_val=min_val, max_val=max_val)

        # Assert
        assert min_val <= num <= max_val, f"数字应该在 {min_val}-{max_val} 范围内"

    def test_number_negative_range(self, registry):
        """测试负数范围"""
        # Arrange
        min_val = -100
        max_val = -50

        # Act
        num = registry.call("random.number", min_val=min_val, max_val=max_val)

        # Assert
        assert min_val <= num <= max_val, f"数字应该在 {min_val}-{max_val} 范围内"

    @pytest.mark.parametrize(
        "min_val,max_val",
        [
            (0, 10),
            (50, 100),
            (-50, 50),
            (-100, -50),
            (1000, 2000),
        ],
    )
    def test_number_various_ranges(self, registry, min_val, max_val):
        """测试各种数字范围"""
        # Act
        num = registry.call("random.number", min_val=min_val, max_val=max_val)

        # Assert
        assert min_val <= num <= max_val, f"数字应该在 {min_val}-{max_val} 范围内"


class TestEmailGeneration:
    """测试邮箱生成功能"""

    @pytest.fixture
    def registry(self):
        """提供 ServiceRegistry 实例"""
        config = ServicesConfig(
            settings=GlobalSettings(),
            providers={"random": ProviderConfig(type="random", config={})},
        )
        registry = ServiceRegistry(config)
        registry.initialize()
        return registry

    def test_email_default_domain(self, registry):
        """测试默认域名邮箱生成"""
        # Arrange & Act
        email = registry.call("random.email")

        # Assert
        assert "@example.com" in email, "默认域名应该是 example.com"
        assert re.match(r"^[a-z0-9]+@example\.com$", email), "邮箱格式应该正确"

    def test_email_custom_domain(self, registry):
        """测试自定义域名邮箱生成"""
        # Arrange
        domain = "test.org"

        # Act
        email = registry.call("random.email", domain=domain)

        # Assert
        assert f"@{domain}" in email, f"域名应该是 {domain}"

    def test_email_custom_username_length(self, registry):
        """测试自定义用户名长度"""
        # Arrange
        length = 12
        domain = "mail.com"

        # Act
        email = registry.call("random.email", length=length, domain=domain)

        # Assert
        username = email.split("@")[0]
        assert len(username) == length, f"用户名长度应该是 {length}"

    @pytest.mark.parametrize(
        "domain,length",
        [
            ("example.com", 8),
            ("test.org", 10),
            ("mail.com", 12),
            ("custom.net", 15),
        ],
    )
    def test_email_various_combinations(self, registry, domain, length):
        """测试各种域名和长度组合"""
        # Act
        email = registry.call("random.email", domain=domain, length=length)

        # Assert
        username = email.split("@")[0]
        assert len(username) == length, f"用户名长度应该是 {length}"
        assert f"@{domain}" in email, f"域名应该是 {domain}"


class TestPhoneGeneration:
    """测试电话号码生成功能"""

    @pytest.fixture
    def registry(self):
        """提供 ServiceRegistry 实例"""
        config = ServicesConfig(
            settings=GlobalSettings(),
            providers={"random": ProviderConfig(type="random", config={})},
        )
        registry = ServiceRegistry(config)
        registry.initialize()
        return registry

    def test_phone_default_country_code(self, registry):
        """测试默认国家代码电话生成"""
        # Arrange & Act
        phone = registry.call("random.phone")

        # Assert
        assert phone.startswith("+1"), "默认国家代码应该是 +1"
        digits = phone[2:]  # 去掉 +1
        assert len(digits) == 10, "去掉国家代码后应该是 10 位"
        assert digits.isdigit(), "应该只包含数字"

    def test_phone_custom_country_code(self, registry):
        """测试自定义国家代码"""
        # Arrange
        country_code = "86"
        length = 11

        # Act
        phone = registry.call("random.phone", country_code=country_code, length=length)

        # Assert
        assert phone.startswith(f"+{country_code}"), f"国家代码应该是 +{country_code}"
        digits = phone[3:]  # 去掉 +86
        assert len(digits) == length, f"去掉国家代码后应该是 {length} 位"

    def test_phone_first_digit_not_zero(self, registry):
        """测试第一位数字不是 0"""
        # Arrange
        num_tests = 20

        # Act & Assert
        for _ in range(num_tests):
            phone = registry.call("random.phone")
            first_digit = phone[2]  # 跳过 +1
            assert first_digit != "0", "第一位数字不应该是 0"

    @pytest.mark.parametrize(
        "country_code,length",
        [
            ("1", 10),
            ("86", 11),
            ("44", 10),
            ("81", 10),
        ],
    )
    def test_phone_various_country_codes(self, registry, country_code, length):
        """测试各种国家代码"""
        # Act
        phone = registry.call("random.phone", country_code=country_code, length=length)

        # Assert
        assert phone.startswith(f"+{country_code}"), f"国家代码应该是 +{country_code}"
        digits = phone[len(country_code) + 1 :]  # 去掉 +XX
        assert len(digits) == length, f"号码长度应该是 {length}"


class TestChoiceFunction:
    """测试随机选择功能"""

    @pytest.fixture
    def registry(self):
        """提供 ServiceRegistry 实例"""
        config = ServicesConfig(
            settings=GlobalSettings(),
            providers={"random": ProviderConfig(type="random", config={})},
        )
        registry = ServiceRegistry(config)
        registry.initialize()
        return registry

    def test_choice_from_options(self, registry):
        """测试从选项中随机选择"""
        # Arrange
        options = ["red", "green", "blue"]

        # Act
        choice = registry.call("random.choice", options=options)

        # Assert
        assert choice in options, "选择应该在选项列表中"

    def test_choice_empty_options(self, registry):
        """测试空选项列表"""
        # Arrange
        options = []

        # Act
        choice = registry.call("random.choice", options=options)

        # Assert
        assert choice == "", "空选项应该返回空字符串"

    @pytest.mark.parametrize(
        "options",
        [
            (["option1", "option2", "option3"]),
            (["A", "B", "C", "D"]),
            (["1", "2", "3"]),
            (["red", "green", "blue", "yellow"]),
        ],
    )
    def test_choice_various_options(self, registry, options):
        """测试各种选项列表"""
        # Act
        choice = registry.call("random.choice", options=options)

        # Assert
        assert choice in options, "选择应该在选项列表中"


class TestRegistryIntegration:
    """测试通过 Registry 完整调用流程"""

    @pytest.fixture
    def registry(self):
        """提供 ServiceRegistry 实例"""
        config = ServicesConfig(
            settings=GlobalSettings(),
            providers={"random": ProviderConfig(type="random", config={})},
        )
        registry = ServiceRegistry(config)
        registry.initialize()
        return registry

    def test_call_through_registry(self, registry):
        """测试通过 Registry 完整调用链"""
        # Arrange & Act
        password = registry.call("random.password", length=16)
        username = registry.call("random.username", prefix="test_")
        email = registry.call("random.email", domain="test.com")

        # Assert
        assert len(password) == 16, "密码长度应该正确"
        assert username.startswith("test_"), "用户名应该有正确的前缀"
        assert "@test.com" in email, "邮箱应该有正确的域名"

    def test_multiple_calls_produce_different_results(self, registry):
        """测试多次调用产生不同结果"""
        # Arrange
        num_calls = 5

        # Act
        passwords = [registry.call("random.password") for _ in range(num_calls)]
        usernames = [registry.call("random.username") for _ in range(num_calls)]

        # Assert
        assert len(set(passwords)) == num_calls, "每次调用应该产生不同的密码"
        assert len(set(usernames)) == num_calls, "每次调用应该产生不同的用户名"


class TestCustomConfiguration:
    """测试自定义配置的 RandomProvider"""

    def test_custom_charset_configuration(self):
        """测试自定义字符集配置"""
        # Arrange
        config = ServicesConfig(
            settings=GlobalSettings(),
            providers={
                "random": ProviderConfig(
                    type="random", config={"charset_lower": "abc", "charset_numeric": "123"}
                )
            },
        )
        registry = ServiceRegistry(config)
        registry.initialize()

        # Act & Assert
        # 生成的用户名应该只包含自定义字符集 'abc123'
        for _ in range(10):
            username = registry.call("random.username", length=10)
            assert all(c in "abc123" for c in username), "用户名应该只包含自定义字符集中的字符"

    def test_custom_config_affects_string_generation(self):
        """测试自定义配置影响字符串生成"""
        # Arrange
        config = ServicesConfig(
            settings=GlobalSettings(),
            providers={
                "random": ProviderConfig(
                    type="random", config={"charset_lower": "xyz", "charset_numeric": "789"}
                )
            },
        )
        registry = ServiceRegistry(config)
        registry.initialize()

        # Act
        s = registry.call("random.string", length=20, charset="lower")

        # Assert
        assert len(s) == 20, "字符串长度应该正确"
        assert all(c in "xyz" for c in s), "字符串应该只包含自定义的小写字符集"
