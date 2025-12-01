"""
Built-in Service Namespaces (v3.1+)

提供内置服务命名空间，支持 Python-style 调用:
- random: 随机数据生成服务
- http: HTTP 请求服务

用法:
    let email = random.email()
    let response = http.get(url: "https://api.example.com")
"""

import string
import random as py_random
import uuid as py_uuid
from typing import Optional, Dict, Any


class HttpResponse:
    """
    HTTP 响应包装对象

    提供统一的响应接口，支持访问响应数据和状态。

    属性:
        ok (bool): 请求是否成功 (HTTP 状态码 200-299)
        data (Any): 响应数据（JSON 解析后的对象或文本）
        status_code (int): HTTP 状态码
        headers (Dict): 响应头
        error (str): 错误信息（失败时）

    用法:
        let response = http.post(url: "...", body: {...})
        if response.ok:
            log "成功: {response.data.email}"
        else:
            log "失败: {response.error}"
    """

    def __init__(
        self,
        ok: bool,
        data: Any = None,
        status_code: int = 0,
        headers: Optional[Dict] = None,
        error: Optional[str] = None,
    ):
        self.ok = ok
        self.data = data
        self.status_code = status_code
        self.headers = headers or {}
        self.error = error

    def __getattr__(self, name: str):
        """
        动态属性访问：支持从 JSON 数据中直接访问字段

        当访问的属性不存在于 HttpResponse 自身时，
        尝试从 data 字典中获取该属性。

        示例:
            response.data = {'id': 1, 'name': 'Alice'}
            response.id -> 1 (等同于 response.data['id'])
            response.name -> 'Alice' (等同于 response.data['name'])
        """
        # 避免递归：不要尝试从 data 中获取这些内部属性
        if name in ("ok", "data", "status_code", "headers", "error"):
            raise AttributeError(f"对象 HttpResponse 没有属性 '{name}'")

        # 尝试从 data 字典中获取属性
        if isinstance(self.data, dict) and name in self.data:
            return self.data[name]

        # 属性不存在
        raise AttributeError(f"对象 HttpResponse 没有属性 '{name}'")

    def __eq__(self, other):
        """
        相等性比较：支持与字符串直接比较（用于文本响应）

        示例:
            response.data = "Hello, World!"
            response == "Hello, World!" -> True
        """
        if isinstance(other, str):
            # 如果 data 是字符串，直接比较
            if isinstance(self.data, str):
                return self.data == other
            return False
        return super().__eq__(other)

    def __contains__(self, item):
        """
        包含检查：支持字符串包含检查（用于文本/HTML响应）

        示例:
            response.data = "<html><body>Test</body></html>"
            "<html>" in response -> True (等同于 "<html>" in response.data)
        """
        if isinstance(self.data, str):
            return item in self.data
        return False

    def __str__(self):
        """
        字符串表示：返回 data 的字符串形式（用于 contains 操作符）

        示例:
            response.data = "<html><body>Test</body></html>"
            str(response) -> "<html><body>Test</body></html>"
            response contains "<html>" -> True（通过 to_string() 转换）
        """
        if isinstance(self.data, str):
            return self.data
        return str(self.data)


class RandomNamespace:
    """
    随机数据生成服务命名空间 (v3.1+)

    提供常用的随机数据生成方法，用于测试数据生成。

    方法:
        email(): 生成随机邮箱地址
        password(length, special): 生成随机密码
        username(): 生成随机用户名
        phone(locale): 生成随机手机号
        number(min_val, max_val): 生成随机整数
        uuid(): 生成 UUID v4

    示例:
        let email = random.email()
        let pwd = random.password(length: 16, special: True)
        let dice = random.number(1, 6)
    """

    @staticmethod
    def email() -> str:
        """
        生成随机邮箱地址

        返回:
            str: 格式为 username@domain.com 的随机邮箱

        示例:
            let email = random.email()  # "alice123@example.com"
        """
        try:
            from faker import Faker

            fake = Faker()
            return fake.email()
        except ImportError:
            # Fallback: 如果没有 faker，使用简单随机生成
            username = f"user{py_random.randint(1000, 9999)}"
            domains = ["example.com", "test.com", "demo.com"]
            domain = py_random.choice(domains)
            return f"{username}@{domain}"

    @staticmethod
    def password(length: int = 12, special: bool = True) -> str:
        """
        生成随机密码

        参数:
            length: 密码长度 (默认: 12)
            special: 是否包含特殊字符 (默认: True)

        返回:
            str: 随机密码

        异常:
            ValueError: 如果 length <= 0

        示例:
            let pwd = random.password()                    # 12位，含特殊字符
            let strong = random.password(16, True)
            let simple = random.password(8, False)
        """
        # 类型转换：DSL解析器可能将整数解析为float
        length = int(length)

        if length <= 0:
            raise ValueError(f"Password length must be positive, got {length}")

        # 构建字符集
        chars = string.ascii_letters + string.digits
        if special:
            chars += string.punctuation

        # 生成随机密码
        return "".join(py_random.choice(chars) for _ in range(length))

    @staticmethod
    def username() -> str:
        """
        生成随机用户名

        返回:
            str: 随机用户名

        示例:
            let username = random.username()  # "alice_smith"
        """
        try:
            from faker import Faker

            fake = Faker()
            return fake.user_name()
        except ImportError:
            # Fallback: 简单随机生成
            prefixes = ["user", "test", "demo", "guest"]
            return f"{py_random.choice(prefixes)}{py_random.randint(1000, 9999)}"

    @staticmethod
    def phone(locale: str = "en_US") -> str:
        """
        生成随机手机号

        参数:
            locale: 地区代码 (默认: "en_US")
                   支持: "en_US", "zh_CN", "ja_JP", 等

        返回:
            str: 随机手机号

        示例:
            let phone = random.phone()                # 美国手机号
            let cn_phone = random.phone(locale: "zh_CN")  # 中国手机号
        """
        try:
            from faker import Faker

            fake = Faker(locale)
            return fake.phone_number()
        except ImportError:
            # Fallback: 简单随机生成 (仅 en_US 格式)
            area_code = py_random.randint(200, 999)
            exchange = py_random.randint(200, 999)
            number = py_random.randint(1000, 9999)
            return f"({area_code}) {exchange}-{number}"

    @staticmethod
    def number(min_val: int, max_val: int) -> int:
        """
        生成指定范围内的随机整数 [min_val, max_val]

        参数:
            min_val: 最小值 (包含)
            max_val: 最大值 (包含)

        返回:
            int: 随机整数

        异常:
            ValueError: 如果 min_val > max_val

        示例:
            let dice = random.number(1, 6)       # 1-6
            let percentage = random.number(0, 100)  # 0-100
        """
        # 类型转换：DSL解析器可能将整数解析为float
        min_val = int(min_val)
        max_val = int(max_val)

        if min_val > max_val:
            raise ValueError(f"min_val ({min_val}) must be <= max_val ({max_val})")

        return py_random.randint(min_val, max_val)

    @staticmethod
    def uuid() -> str:
        """
        生成 UUID v4

        返回:
            str: UUID 字符串 (36 字符，含连字符)

        示例:
            let user_id = random.uuid()  # "550e8400-e29b-41d4-a716-446655440000"
        """
        return str(py_uuid.uuid4())


class HttpNamespace:
    """
    HTTP 请求服务命名空间 (v3.1+)

    提供 HTTP 请求方法，用于与 REST API 交互。

    方法:
        get(url, timeout, headers): HTTP GET 请求
        post(url, body, timeout, headers): HTTP POST 请求
        put(url, body, timeout, headers): HTTP PUT 请求
        delete(url, timeout, headers): HTTP DELETE 请求
        patch(url, body, timeout, headers): HTTP PATCH 请求

    示例:
        let response = http.get(url: "https://api.example.com/users")
        let created = http.post(url: api_url, body: {name: "Alice"})
    """

    @staticmethod
    def get(url: str, timeout: int = 30, headers: Optional[Dict[str, str]] = None) -> HttpResponse:
        """
        发送 HTTP GET 请求

        参数:
            url: 请求 URL
            timeout: 超时时间（秒，默认: 30）
            headers: 请求头字典 (可选)

        返回:
            HttpResponse: 响应对象，包含 ok、data、status_code、headers、error 属性

        异常:
            抛出网络异常（timeout, connection error等），由 DSL 解释器捕获并转换为 ExecutionError

        示例:
            let response = http.get(url: "https://api.example.com/users")
            if response.ok:
                log "成功: {response.data}"
            else:
                log "失败: {response.error}"
        """
        import requests

        response = requests.get(url, timeout=timeout, headers=headers)

        # 检查 HTTP 状态码，如果是错误状态（4xx, 5xx）则抛出异常
        response.raise_for_status()

        # 根据 Content-Type 返回 JSON 或文本
        content_type = response.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            data = response.json()
        else:
            data = response.text

        # 返回包装对象
        return HttpResponse(
            ok=response.ok,
            data=data,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    @staticmethod
    def post(
        url: str,
        body: Optional[Any] = None,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
    ) -> HttpResponse:
        """
        发送 HTTP POST 请求

        参数:
            url: 请求 URL
            body: 请求体（字典或其他可 JSON 序列化对象，默认: None）
            timeout: 超时时间（秒，默认: 30）
            headers: 请求头字典 (可选)

        返回:
            HttpResponse: 响应对象，包含 ok、data、status_code、headers、error 属性

        异常:
            抛出网络异常（timeout, connection error等），由 DSL 解释器捕获并转换为 ExecutionError

        示例:
            let response = http.post(url: api_url, body: {name: "Alice"})
            if response.ok:
                log "创建成功: {response.data.id}"
            else:
                log "创建失败: {response.error}"
        """
        import requests

        response = requests.post(url, json=body, timeout=timeout, headers=headers)

        # 检查 HTTP 状态码
        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            data = response.json()
        else:
            data = response.text

        return HttpResponse(
            ok=response.ok,
            data=data,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    @staticmethod
    def put(
        url: str,
        body: Optional[Any] = None,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
    ) -> HttpResponse:
        """
        发送 HTTP PUT 请求

        参数:
            url: 请求 URL
            body: 请求体（字典或其他可 JSON 序列化对象，默认: None）
            timeout: 超时时间（秒，默认: 30）
            headers: 请求头字典 (可选)

        返回:
            HttpResponse: 响应对象，包含 ok、data、status_code、headers、error 属性

        异常:
            抛出网络异常（timeout, connection error等），由 DSL 解释器捕获并转换为 ExecutionError

        示例:
            let response = http.put(url: api_url, body: {status: "active"})
            if response.ok:
                log "更新成功"
        """
        import requests

        response = requests.put(url, json=body, timeout=timeout, headers=headers)

        # 检查 HTTP 状态码
        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            data = response.json()
        else:
            data = response.text

        return HttpResponse(
            ok=response.ok,
            data=data,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    @staticmethod
    def delete(
        url: str, timeout: int = 30, headers: Optional[Dict[str, str]] = None
    ) -> HttpResponse:
        """
        发送 HTTP DELETE 请求

        参数:
            url: 请求 URL
            timeout: 超时时间（秒，默认: 30）
            headers: 请求头字典 (可选)

        返回:
            HttpResponse: 响应对象，包含 ok、data、status_code、headers、error 属性

        异常:
            抛出网络异常（timeout, connection error等），由 DSL 解释器捕获并转换为 ExecutionError

        示例:
            let response = http.delete(url: f"{api_url}/users/{user_id}")
            if response.ok:
                log "删除成功"
        """
        import requests

        response = requests.delete(url, timeout=timeout, headers=headers)

        # 检查 HTTP 状态码
        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            data = response.json()
        else:
            data = response.text

        return HttpResponse(
            ok=response.ok,
            data=data,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    @staticmethod
    def patch(
        url: str,
        body: Optional[Any] = None,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
    ) -> HttpResponse:
        """
        发送 HTTP PATCH 请求

        参数:
            url: 请求 URL
            body: 请求体（字典或其他可 JSON 序列化对象，默认: None）
            timeout: 超时时间（秒，默认: 30）
            headers: 请求头字典 (可选)

        返回:
            HttpResponse: 响应对象，包含 ok、data、status_code、headers、error 属性

        异常:
            抛出网络异常（timeout, connection error等），由 DSL 解释器捕获并转换为 ExecutionError

        示例:
            let response = http.patch(url: api_url, body: {email: new_email})
            if response.ok:
                log "更新成功"
        """
        import requests

        response = requests.patch(url, json=body, timeout=timeout, headers=headers)

        # 检查 HTTP 状态码
        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()
        if "application/json" in content_type:
            data = response.json()
        else:
            data = response.text

        return HttpResponse(
            ok=response.ok,
            data=data,
            status_code=response.status_code,
            headers=dict(response.headers),
        )


# 导出命名空间类
__all__ = ["RandomNamespace", "HttpNamespace", "HttpResponse"]
