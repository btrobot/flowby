"""
随机数据生成提供者
"""

import random
import string
from typing import List

from ..provider import ServiceProvider


class RandomProvider(ServiceProvider):
    """随机数据生成提供者"""

    def initialize(self) -> None:
        """初始化提供者"""
        # 获取自定义字符集或使用默认值
        self.charset_lower = self.config.get("charset_lower", string.ascii_lowercase)
        self.charset_upper = self.config.get("charset_upper", string.ascii_uppercase)
        self.charset_numeric = self.config.get("charset_numeric", string.digits)
        self.charset_special = self.config.get("charset_special", "!@#$%^&*()_+-=")

    def get_methods(self) -> List[str]:
        """获取支持的方法列表"""
        return ["password", "username", "string", "number", "email", "phone", "choice"]

    def password(
        self,
        length: int = 12,
        special: bool = True,
        upper: bool = True,
        lower: bool = True,
        digits: bool = True,
    ) -> str:
        """
        生成随机密码

        Args:
            length: 密码长度
            special: 是否包含特殊字符
            upper: 是否包含大写字母
            lower: 是否包含小写字母
            digits: 是否包含数字

        Returns:
            随机密码
        """
        chars = ""
        required = []

        if lower:
            chars += self.charset_lower
            required.append(random.choice(self.charset_lower))

        if upper:
            chars += self.charset_upper
            required.append(random.choice(self.charset_upper))

        if digits:
            chars += self.charset_numeric
            required.append(random.choice(self.charset_numeric))

        if special:
            chars += self.charset_special
            required.append(random.choice(self.charset_special))

        if not chars:
            chars = self.charset_lower
            required.append(random.choice(self.charset_lower))

        # 确保密码包含所有必需字符类型
        remaining_length = length - len(required)
        if remaining_length > 0:
            password_chars = required + [random.choice(chars) for _ in range(remaining_length)]
        else:
            password_chars = required[:length]

        # 打乱顺序
        random.shuffle(password_chars)

        return "".join(password_chars)

    def username(self, length: int = 8, prefix: str = "", suffix: str = "") -> str:
        """
        生成随机用户名

        Args:
            length: 随机部分长度
            prefix: 前缀
            suffix: 后缀

        Returns:
            随机用户名
        """
        # 用户名只包含小写字母和数字
        chars = self.charset_lower + self.charset_numeric
        random_part = "".join(random.choice(chars) for _ in range(length))

        return f"{prefix}{random_part}{suffix}"

    def string(self, length: int = 8, charset: str = "alpha") -> str:
        """
        生成随机字符串

        Args:
            length: 字符串长度
            charset: 字符集类型
                - "alpha": 只有字母
                - "lower": 只有小写字母
                - "upper": 只有大写字母
                - "numeric": 只有数字
                - "alphanumeric": 字母和数字
                - "all": 所有字符

        Returns:
            随机字符串
        """
        if charset == "alpha":
            chars = self.charset_lower + self.charset_upper
        elif charset == "lower":
            chars = self.charset_lower
        elif charset == "upper":
            chars = self.charset_upper
        elif charset == "numeric":
            chars = self.charset_numeric
        elif charset == "alphanumeric":
            chars = self.charset_lower + self.charset_upper + self.charset_numeric
        elif charset == "all":
            chars = (
                self.charset_lower
                + self.charset_upper
                + self.charset_numeric
                + self.charset_special
            )
        else:
            chars = self.charset_lower + self.charset_upper

        return "".join(random.choice(chars) for _ in range(length))

    def number(self, min_val: int = 0, max_val: int = 100) -> int:
        """
        生成随机数字

        Args:
            min_val: 最小值
            max_val: 最大值

        Returns:
            随机数字
        """
        return random.randint(min_val, max_val)

    def email(self, domain: str = "example.com", length: int = 8) -> str:
        """
        生成随机邮箱地址

        Args:
            domain: 邮箱域名
            length: 用户名长度

        Returns:
            随机邮箱地址
        """
        username = self.username(length=length)
        return f"{username}@{domain}"

    def phone(self, country_code: str = "1", length: int = 10) -> str:
        """
        生成随机电话号码

        Args:
            country_code: 国家代码
            length: 号码长度

        Returns:
            随机电话号码
        """
        # 确保第一位不是0
        first_digit = random.choice("123456789")
        remaining = "".join(random.choice(self.charset_numeric) for _ in range(length - 1))

        return f"+{country_code}{first_digit}{remaining}"

    def choice(self, options: List[str]) -> str:
        """
        从选项中随机选择

        Args:
            options: 选项列表

        Returns:
            随机选择的选项
        """
        if not options:
            return ""
        return random.choice(options)
