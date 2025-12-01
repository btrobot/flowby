"""
内置函数库 (v2.0+)

提供 DSL 可用的内置函数，包括:
- Math: 数学函数
- Date: 日期时间函数
- JSON: JSON 处理函数
- UUID: UUID 生成
- Hash: 哈希函数
- Base64: Base64 编解码
- random: 随机数据生成服务 (v3.1+)
- http: HTTP 请求服务 (v3.1+)
- len: 获取长度 (v3.4+)
- range: 生成数字序列 (v3.4+)

Fix #18: 添加更多内置函数
v3.1: 添加服务命名空间支持 Python-style 调用
v3.4: 添加 len() 和 range() 支持字符串遍历
"""

import math
import hashlib
import base64
import uuid
import json
import builtins
import os
from datetime import datetime
from typing import Any, List
from pathlib import Path

# v3.1: 导入服务命名空间
from .builtin_namespaces import RandomNamespace, HttpNamespace


class Math:
    """数学函数命名空间"""

    @staticmethod
    def abs(x: float) -> float:
        """绝对值"""
        return abs(x)

    @staticmethod
    def round(x: float) -> int:
        """四舍五入"""
        return round(x)

    @staticmethod
    def ceil(x: float) -> int:
        """向上取整"""
        return math.ceil(x)

    @staticmethod
    def floor(x: float) -> int:
        """向下取整"""
        return math.floor(x)

    @staticmethod
    def max(*args: float) -> float:
        """最大值"""
        if not args:
            raise ValueError("Math.max() requires at least 1 argument")
        return max(args)

    @staticmethod
    def min(*args: float) -> float:
        """最小值"""
        if not args:
            raise ValueError("Math.min() requires at least 1 argument")
        return min(args)

    @staticmethod
    def random() -> float:
        """0-1 随机数"""
        import random
        return random.random()

    @staticmethod
    def pow(base: float, exp: float) -> float:
        """幂运算"""
        return math.pow(base, exp)

    @staticmethod
    def sqrt(x: float) -> float:
        """平方根"""
        return math.sqrt(x)


class Date:
    """日期时间函数命名空间"""

    @staticmethod
    def now() -> int:
        """当前时间戳（毫秒）"""
        return int(datetime.now().timestamp() * 1000)

    @staticmethod
    def format(fmt: str = "YYYY-MM-DD HH:mm:ss") -> str:
        """
        格式化当前日期

        支持的格式:
        - YYYY: 四位年份
        - MM: 两位月份
        - DD: 两位日期
        - HH: 两位小时(24小时制)
        - mm: 两位分钟
        - ss: 两位秒
        """
        # 将常见格式转换为 Python strftime 格式
        fmt = fmt.replace("YYYY", "%Y")
        fmt = fmt.replace("MM", "%m")
        fmt = fmt.replace("DD", "%d")
        fmt = fmt.replace("HH", "%H")
        fmt = fmt.replace("mm", "%M")
        fmt = fmt.replace("ss", "%S")
        return datetime.now().strftime(fmt)

    @staticmethod
    def parse(date_str: str) -> int:
        """解析日期字符串为时间戳（毫秒）"""
        try:
            # 尝试 ISO 格式
            dt = datetime.fromisoformat(date_str)
            return int(dt.timestamp() * 1000)
        except ValueError:
            # 尝试常见格式
            formats = [
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%Y-%m-%d %H:%M:%S",
                "%Y/%m/%d %H:%M:%S",
            ]
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return int(dt.timestamp() * 1000)
                except ValueError:
                    continue
            return 0


class JSON:
    """JSON 处理函数命名空间"""

    @staticmethod
    def stringify(obj: Any) -> str:
        """将对象转换为 JSON 字符串"""
        try:
            return json.dumps(obj, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            raise ValueError(f"无法序列化对象为 JSON: {e}")

    @staticmethod
    def parse(json_str: str) -> Any:
        """解析 JSON 字符串为对象"""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"无效的 JSON 字符串: {e}")


class UUID:
    """UUID 生成函数命名空间"""

    @staticmethod
    def generate() -> str:
        """生成 UUID (v4)"""
        return str(uuid.uuid4())


class Hash:
    """哈希函数命名空间"""

    @staticmethod
    def md5(text: str) -> str:
        """计算 MD5 哈希"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    @staticmethod
    def sha1(text: str) -> str:
        """计算 SHA1 哈希"""
        return hashlib.sha1(text.encode('utf-8')).hexdigest()

    @staticmethod
    def sha256(text: str) -> str:
        """计算 SHA256 哈希"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()


class Base64:
    """Base64 编解码函数命名空间"""

    @staticmethod
    def encode(text: str) -> str:
        """Base64 编码"""
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')

    @staticmethod
    def decode(encoded: str) -> str:
        """Base64 解码"""
        try:
            return base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
        except Exception as e:
            raise ValueError(f"无效的 Base64 字符串: {e}")


# 类型转换函数（全局函数）
def Number(value: Any) -> float:
    """转换为数字"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return float('nan')


def String(value: Any) -> str:
    """转换为字符串"""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def Boolean(value: Any) -> bool:
    """转换为布尔值"""
    if isinstance(value, bool):
        return value
    if isinstance(value, (builtins.int, builtins.float)):
        return value != 0
    if isinstance(value, str):
        return builtins.len(value) > 0
    if value is None:
        return False
    return True


# v4.0: Python-style 类型转换函数
def int(value: Any) -> builtins.int:
    """
    转换为整数（v4.0）

    支持的输入:
    - 整数: 返回原值
    - 浮点数: 截断小数部分（向零取整）
    - 字符串: 解析整数
    - 布尔值: True→1, False→0

    示例:
    >>> int(5.9)
    5
    >>> int("42")
    42
    >>> int(True)
    1
    """
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, builtins.int) and not isinstance(value, bool):
        return value
    if isinstance(value, builtins.float):
        return builtins.int(value)
    if isinstance(value, str):
        try:
            return builtins.int(builtins.float(value))
        except ValueError:
            raise ValueError(f"无法将字符串 '{value}' 转换为整数")
    raise TypeError(f"无法将 {type(value).__name__} 转换为整数")


def float(value: Any) -> builtins.float:
    """
    转换为浮点数（v4.0）

    支持的输入:
    - 浮点数: 返回原值
    - 整数: 转换为浮点数
    - 字符串: 解析浮点数
    - 布尔值: True→1.0, False→0.0

    示例:
    >>> float(5)
    5.0
    >>> float("3.14")
    3.14
    >>> float(True)
    1.0
    """
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (builtins.int, builtins.float)) and not isinstance(value, bool):
        return builtins.float(value)
    if isinstance(value, str):
        try:
            return builtins.float(value)
        except ValueError:
            raise ValueError(f"无法将字符串 '{value}' 转换为浮点数")
    raise TypeError(f"无法将 {type(value).__name__} 转换为浮点数")


def isNaN(value: Any) -> bool:
    """检查是否为 NaN"""
    try:
        num = float(value)
        return math.isnan(num)
    except (ValueError, TypeError):
        return True


def isFinite(value: Any) -> bool:
    """检查是否为有限数"""
    try:
        num = float(value)
        return math.isfinite(num)
    except (ValueError, TypeError):
        return False


def len(value: Any) -> int:
    """
    获取字符串、数组或对象的长度（v4.0: 返回整数）

    支持的类型:
    - str: 字符串长度
    - list: 数组长度
    - tuple: 元组长度
    - dict: 对象键数量

    返回: int (v4.0: 整数类型)

    示例:
    >>> len("Hello")
    5
    >>> len([1, 2, 3])
    3
    >>> len({"a": 1, "b": 2})
    2
    """
    if isinstance(value, (str, list, tuple, dict)):
        return builtins.len(value)
    raise TypeError(f"len() 不支持 {type(value).__name__} 类型")


def range(*args) -> List[int]:
    """
    生成整数序列（v4.0: 返回整数列表）

    用法:
    - range(stop): 生成 0 到 stop-1 的序列
    - range(start, stop): 生成 start 到 stop-1 的序列
    - range(start, stop, step): 生成 start 到 stop-1 的序列，步长为 step

    返回: List[int] (v4.0: 整数列表)

    示例:
    >>> range(5)
    [0, 1, 2, 3, 4]
    >>> range(2, 5)
    [2, 3, 4]
    >>> range(0, 10, 2)
    [0, 2, 4, 6, 8]
    """
    if not args:
        raise ValueError("range() 至少需要 1 个参数")

    # 将所有参数转换为整数
    int_args = []
    for arg in args:
        try:
            int_args.append(int(float(arg)))
        except (ValueError, TypeError):
            raise TypeError(f"range() 参数必须是数字，得到 {type(arg).__name__}")

    # v4.0: 生成range并直接返回整数列表
    if builtins.len(int_args) == 1:
        result = list(builtins.range(int_args[0]))
    elif builtins.len(int_args) == 2:
        result = list(builtins.range(int_args[0], int_args[1]))
    elif builtins.len(int_args) == 3:
        result = list(builtins.range(int_args[0], int_args[1], int_args[2]))
    else:
        raise ValueError(f"range() 最多接受 3 个参数，得到 {builtins.len(int_args)} 个")

    # v4.0: 直接返回整数列表
    return result


def enumerate(iterable, start=0):
    """
    生成带索引的序列（v4.0: 返回 (索引, 元素) 元组列表）

    用法:
    - enumerate(iterable): 生成 (0, item), (1, item), ... 的序列
    - enumerate(iterable, start): 生成 (start, item), (start+1, item), ... 的序列

    返回: List[Tuple[int, Any]] (索引, 元素) 元组列表

    示例:
    >>> enumerate(["a", "b", "c"])
    [(0, "a"), (1, "b"), (2, "c")]
    >>> enumerate(["a", "b", "c"], start=1)
    [(1, "a"), (2, "b"), (3, "c")]
    >>> for index, item in enumerate(items):
    ...     log f"Item {index}: {item}"
    """
    # 验证 iterable
    if not isinstance(iterable, (list, tuple, str)):
        raise TypeError(f"enumerate() 不支持 {type(iterable).__name__} 类型")

    # 验证 start 参数
    try:
        start_index = int(float(start))
    except (ValueError, TypeError):
        raise TypeError(f"enumerate() start 参数必须是数字，得到 {type(start).__name__}")

    # 生成 (index, value) 元组列表
    result = []
    for i, item in builtins.enumerate(iterable, start=start_index):
        result.append((i, item))

    return result


# .env 文件缓存（避免重复读取）
_ENV_CACHE = {}
_ENV_LOADED = False


def _load_env_file():
    """
    加载 .env 文件到缓存

    查找顺序：
    1. 当前工作目录的 .env
    2. 脚本所在目录的 .env
    3. 项目根目录的 .env
    """
    global _ENV_CACHE, _ENV_LOADED

    if _ENV_LOADED:
        return

    # 查找 .env 文件
    search_paths = [
        Path.cwd() / '.env',                          # 当前目录
        Path(__file__).parent.parent.parent / '.env', # 项目根目录
    ]

    env_file = None
    for path in search_paths:
        if path.exists():
            env_file = path
            break

    if not env_file:
        _ENV_LOADED = True
        return

    # 解析 .env 文件
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue

                # 解析 KEY=VALUE 格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # 移除值两端的引号
                    if value and value[0] in ('"', "'") and value[-1] == value[0]:
                        value = value[1:-1]

                    _ENV_CACHE[key] = value

        _ENV_LOADED = True
    except Exception:
        # 加载失败时静默忽略
        _ENV_LOADED = True


def env(key: str, default: Any = None) -> Any:
    """
    获取环境变量（v4.2.1+: 支持 .env 文件）

    从环境变量中读取值，如果不存在则返回默认值。
    支持从 .env 文件和系统环境变量读取。

    Args:
        key: 环境变量名称
        default: 默认值（可选，默认为 None）

    Returns:
        环境变量值或默认值

    Examples:
        >>> env("API_TOKEN", "test_token")
        "production_token"  # 如果 API_TOKEN 存在

        >>> env("MISSING_KEY", "fallback")
        "fallback"  # 如果 MISSING_KEY 不存在

        >>> env("DEBUG")
        None  # 如果 DEBUG 不存在且没有默认值

        >>> env("PORT", 8000)
        8000  # 返回默认值（注意：环境变量总是字符串）

    Notes:
        - 环境变量的值总是字符串类型
        - 如果需要其他类型，请使用 int(), float() 等函数转换
        - 优先级：系统环境变量 > .env 文件 > default 参数
        - 自动查找 .env 文件（当前目录或项目根目录）
    """
    # 首次调用时加载 .env 文件
    _load_env_file()

    # 优先级：系统环境变量 > .env 文件 > default
    value = os.getenv(key)
    if value is not None:
        return value

    value = _ENV_CACHE.get(key)
    if value is not None:
        return value

    return default


# 导出所有内置函数命名空间
BUILTIN_NAMESPACES = {
    # v1.0 内置函数
    'Math': Math,
    'Date': Date,
    'JSON': JSON,
    'UUID': UUID,
    'Hash': Hash,
    'Base64': Base64,
    # v3.1 服务命名空间 (支持 Python-style 调用)
    'random': RandomNamespace,
    'http': HttpNamespace,
}

# ==================== 字符串处理函数 (Python-style, v4.3+) ====================
def upper(text: str) -> str:
    """转换为大写"""
    if not isinstance(text, str):
        raise TypeError(f"upper() 需要字符串参数，得到 {type(text).__name__}")
    return text.upper()


def lower(text: str) -> str:
    """转换为小写"""
    if not isinstance(text, str):
        raise TypeError(f"lower() 需要字符串参数，得到 {type(text).__name__}")
    return text.lower()


def strip(text: str, chars: str = None) -> str:
    """
    去除字符串首尾字符

    Args:
        text: 要处理的字符串
        chars: 要移除的字符集（可选，默认为空白字符）

    Examples:
        >>> strip("  hello  ")
        "hello"
        >>> strip("++hello++", "+")
        "hello"
    """
    if not isinstance(text, str):
        raise TypeError(f"strip() 需要字符串参数，得到 {type(text).__name__}")
    return text.strip(chars) if chars else text.strip()


def split(text: str, sep: str = None, maxsplit: int = -1) -> List[str]:
    """
    分割字符串为列表

    Args:
        text: 要分割的字符串
        sep: 分隔符（可选，默认为任意空白字符）
        maxsplit: 最大分割次数（可选，默认为-1表示不限制）

    Examples:
        >>> split("a,b,c", ",")
        ["a", "b", "c"]
        >>> split("hello world")
        ["hello", "world"]
        >>> split("a:b:c", ":", 1)
        ["a", "b:c"]
    """
    if not isinstance(text, str):
        raise TypeError(f"split() 需要字符串参数，得到 {type(text).__name__}")

    if sep is None:
        return text.split()

    if maxsplit == -1:
        return text.split(sep)

    return text.split(sep, maxsplit)


def join(sep: str, items: list) -> str:
    """
    使用分隔符连接列表元素为字符串

    Args:
        sep: 分隔符
        items: 要连接的列表

    Examples:
        >>> join("-", ["a", "b", "c"])
        "a-b-c"
        >>> join("", ["hello", "world"])
        "helloworld"
    """
    if not isinstance(sep, str):
        raise TypeError(f"join() 第一个参数需要字符串，得到 {type(sep).__name__}")
    if not isinstance(items, list):
        raise TypeError(f"join() 第二个参数需要列表，得到 {type(items).__name__}")
    return sep.join(str(x) for x in items)


def replace(text: str, old: str, new: str, count: int = -1) -> str:
    """
    替换字符串中的子串

    Args:
        text: 原始字符串
        old: 要替换的子串
        new: 新的子串
        count: 替换次数（可选，默认为-1表示全部替换）

    Examples:
        >>> replace("hello world", "world", "python")
        "hello python"
        >>> replace("aaa", "a", "b", 1)
        "baa"
        >>> replace("+44 7868", " ", "")
        "+447868"
    """
    if not isinstance(text, str):
        raise TypeError(f"replace() 第一个参数需要字符串，得到 {type(text).__name__}")
    if not isinstance(old, str):
        raise TypeError(f"replace() 第二个参数需要字符串，得到 {type(old).__name__}")
    if not isinstance(new, str):
        raise TypeError(f"replace() 第三个参数需要字符串，得到 {type(new).__name__}")

    return text.replace(old, new, count) if count != -1 else text.replace(old, new)


def substring(text: str, start: int, end: int = None) -> str:
    """
    提取子字符串（Python 切片操作的函数形式）

    Args:
        text: 原始字符串
        start: 起始索引（包含）
        end: 结束索引（不包含，可选）

    Returns:
        提取的子字符串

    Examples:
        >>> substring("+447868211483", 3)
        "7868211483"
        >>> substring("+447868211483", 0, 3)
        "+44"
        >>> substring("hello", 1, 4)
        "ell"

    Notes:
        - 等价于 Python 的切片语法: text[start:end]
        - 如果省略 end，则提取到字符串末尾
        - 索引从 0 开始
    """
    if not isinstance(text, str):
        raise TypeError(f"substring() 第一个参数需要字符串，得到 {type(text).__name__}")

    try:
        start_idx = int(start)
    except (ValueError, TypeError):
        raise TypeError(f"substring() start 参数必须是整数，得到 {type(start).__name__}")

    if end is None:
        return text[start_idx:]

    try:
        end_idx = int(end)
    except (ValueError, TypeError):
        raise TypeError(f"substring() end 参数必须是整数，得到 {type(end).__name__}")

    return text[start_idx:end_idx]


def startswith(text: str, prefix: str) -> bool:
    """检查字符串是否以指定前缀开头"""
    if not isinstance(text, str):
        raise TypeError(f"startswith() 第一个参数需要字符串，得到 {type(text).__name__}")
    if not isinstance(prefix, str):
        raise TypeError(f"startswith() 第二个参数需要字符串，得到 {type(prefix).__name__}")
    return text.startswith(prefix)


def endswith(text: str, suffix: str) -> bool:
    """检查字符串是否以指定后缀结尾"""
    if not isinstance(text, str):
        raise TypeError(f"endswith() 第一个参数需要字符串，得到 {type(text).__name__}")
    if not isinstance(suffix, str):
        raise TypeError(f"endswith() 第二个参数需要字符串，得到 {type(suffix).__name__}")
    return text.endswith(suffix)


def find(text: str, sub: str, start: int = 0) -> int:
    """
    查找子字符串的位置

    Args:
        text: 原始字符串
        sub: 要查找的子串
        start: 起始搜索位置（可选，默认为0）

    Returns:
        子串的索引位置，未找到返回 -1

    Examples:
        >>> find("hello world", "world")
        6
        >>> find("hello", "x")
        -1
    """
    if not isinstance(text, str):
        raise TypeError(f"find() 第一个参数需要字符串，得到 {type(text).__name__}")
    if not isinstance(sub, str):
        raise TypeError(f"find() 第二个参数需要字符串，得到 {type(sub).__name__}")

    try:
        start_idx = int(start)
    except (ValueError, TypeError):
        raise TypeError(f"find() start 参数必须是整数，得到 {type(start).__name__}")

    return text.find(sub, start_idx)


# ==================== Resource 构造函数 (v6.0+) ====================
def Resource(spec_file: str, context: 'ExecutionContext' = None, **kwargs) -> 'ResourceNamespace':
    """
    创建基于 OpenAPI 规范的 API 客户端 (v6.0+)

    这是 resource 语句的替代方案，支持运行时动态配置。

    Args:
        spec_file: OpenAPI 规范文件路径（YAML 或 JSON）
        context: 执行上下文（由 ExpressionEvaluator 自动注入）
        **kwargs: 配置选项
            - base_url (str): API 基础 URL（覆盖 OpenAPI 定义）
            - auth (dict): 认证配置
                - type: "bearer" | "basic" | "apikey"
                - token/username/password/key: 认证凭据
            - timeout (int): 请求超时时间（秒），默认 30
            - headers (dict): 默认 HTTP headers
            - response_mapping (dict): 响应数据映射配置
            - validate_response (bool): 是否验证响应，默认 True
            - resilience (dict): 弹性处理配置（重试+断路器）
            - mock (dict): Mock 模式配置

    Returns:
        ResourceNamespace: API 客户端对象，支持调用 OpenAPI 定义的操作

    Raises:
        ExecutionError: spec_file 不存在、格式错误、或配置无效

    Examples:
        # 基本用法
        let api = Resource("openapi/user-service.yml")
        let user = api.getUser(userId=123)

        # 带配置
        let api = Resource("api.yml",
            base_url = "https://api.example.com/v1",
            auth = {type: "bearer", token: env.API_TOKEN},
            timeout = 60
        )

        # 动态配置
        step "动态初始化":
            let token = login_response.access_token
            let api = Resource("api.yml",
                auth = {type: "bearer", token: token}
            )

    Note:
        - 此函数需要 context 参数，由 ExpressionEvaluator 自动注入
        - context 参数不应由 DSL 代码显式传递
        - 这是 v6.0 引入的新特性，替代 resource 语句
    """
    from .openapi_loader import OpenAPISpec
    from .resource_namespace import ResourceNamespace
    from .errors import ExecutionError

    # 验证 context
    if context is None:
        raise ExecutionError(
            line=0,
            statement="Resource()",
            error_type=ExecutionError.RUNTIME_ERROR,
            message="Resource() 函数需要执行上下文，但未提供。这通常是内部错误。"
        )

    # 验证 spec_file
    if not spec_file or not isinstance(spec_file, str):
        raise ExecutionError(
            line=0,
            statement=f"Resource({spec_file!r})",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"spec_file 必须是非空字符串，得到 {type(spec_file).__name__}"
        )

    try:
        # 加载 OpenAPI 规范
        spec = OpenAPISpec(spec_file, script_path=context.script_path)

        # 创建并返回 ResourceNamespace
        return ResourceNamespace(
            name=f"Resource({spec_file})",
            spec=spec,
            base_url=kwargs.get('base_url'),
            auth=kwargs.get('auth'),
            timeout=kwargs.get('timeout'),
            headers=kwargs.get('headers'),
            response_mapping=kwargs.get('response_mapping'),
            validate_response=kwargs.get('validate_response', True),
            resilience=kwargs.get('resilience'),
            mock=kwargs.get('mock'),
            context=context
        )
    except FileNotFoundError as e:
        raise ExecutionError(
            line=0,
            statement=f"Resource({spec_file!r})",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"OpenAPI 规范文件未找到: {e}"
        )
    except Exception as e:
        raise ExecutionError(
            line=0,
            statement=f"Resource({spec_file!r})",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"创建 Resource 失败: {e}"
        )


# ============================================================
# v6.6: 实用工具函数
# ============================================================

def sleep(seconds: float) -> None:
    """
    暂停执行指定秒数

    Args:
        seconds: 暂停的秒数（可以是小数）

    Example:
        sleep(1.5)  # 暂停 1.5 秒
    """
    import time
    # 使用 builtins 中的 int 和 float 类型
    import builtins
    if not isinstance(seconds, (builtins.int, builtins.float)):
        from .errors import ExecutionError
        raise ExecutionError(
            line=0,
            statement="sleep",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"sleep() 需要数字参数，但得到 {type(seconds).__name__}"
        )
    if seconds < 0:
        from .errors import ExecutionError
        raise ExecutionError(
            line=0,
            statement="sleep",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"sleep() 时间不能为负数，但得到 {seconds}"
        )
    time.sleep(seconds)


def zip(*arrays) -> list:
    """
    将多个数组合并成键值对数组

    Args:
        *arrays: 多个数组

    Returns:
        合并后的数组 [[item1_from_arr1, item1_from_arr2, ...], ...]

    Example:
        zip([1, 2, 3], ["a", "b", "c"]) => [[1, "a"], [2, "b"], [3, "c"]]
    """
    if len(arrays) == 0:
        return []

    # 验证所有参数都是列表
    for i, arr in enumerate(arrays):
        if not isinstance(arr, list):
            from .errors import ExecutionError
            raise ExecutionError(
                line=0,
                statement="zip",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"zip() 的第 {i+1} 个参数必须是数组，但得到 {type(arr).__name__}"
            )

    # 使用最短数组的长度
    min_length = min(len(arr) for arr in arrays)

    result = []
    for i in range(min_length):
        result.append([arr[i] for arr in arrays])

    return result


# 导出全局函数
BUILTIN_FUNCTIONS = {
    'Number': Number,
    'String': String,
    'Boolean': Boolean,
    'isNaN': isNaN,
    'isFinite': isFinite,
    # v3.4: 添加 len() 和 range() 支持字符串遍历
    'len': len,
    'range': range,
    # v4.0: Python-style 类型转换函数和enumerate
    'int': int,
    'float': float,
    'enumerate': enumerate,
    # v4.2.1: 环境变量函数
    'env': env,
    # v4.3: Python-style 字符串处理函数
    'upper': upper,
    'lower': lower,
    'strip': strip,
    'split': split,
    'join': join,
    'replace': replace,
    'substring': substring,
    'startswith': startswith,
    'endswith': endswith,
    'find': find,
    # v6.0: Resource 构造函数（替代 resource 语句）
    'Resource': Resource,
    # v6.6: 实用工具函数
    'sleep': sleep,
    'zip': zip,
}
