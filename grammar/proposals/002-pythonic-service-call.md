# Grammar Proposal #002: Python-Style Service Call Syntax

## 📋 Proposal Summary

| 字段 | 内容 |
|------|------|
| **提案编号** | 002 |
| **提案标题** | Python-Style Service Call Syntax (Python 风格服务调用语法) |
| **作者** | AI Assistant |
| **创建日期** | 2025-11-27 |
| **目标版本** | v3.1 (新增), v4.0 (移除旧语法) |
| **状态** | 🟡 Draft |
| **类型** | Modification (修改现有语法) |
| **影响级别** | MINOR (v3.1), MAJOR (v4.0) |

---

## 🎯 Motivation and Background

### 当前设计的问题

v3.0 已经完成了 Python-style 语法改造，但服务调用语法仍然使用特殊的 `call` 语句，与整体设计理念不一致：

```dsl
# ✅ v3.0 内置函数 (Python-style)
let rounded = Math.round(3.7)
let timestamp = Date.now()
let json = JSON.stringify({name: "Alice"})

# ❌ v3.0 服务调用 (非 Python-style)
call "random.email" into email
call "http.get" with url: "https://api.example.com" into response
call "random.password" with length=16, special=True into password
```

### 核心问题分析

#### 问题 1: 语法不一致

| 特性 | 内置函数 | 服务调用 |
|------|---------|---------|
| **调用方式** | `Namespace.method()` | `call "provider.method"` |
| **参数语法** | `(param: value)` | `with param: value` |
| **结果获取** | `let variable = ...` | `into variable` |
| **表达式支持** | ✅ 可用于任何表达式 | ❌ 只能作为语句 |
| **命名空间** | 标识符 `Math.round` | 字符串 `"random.email"` |

**为什么内置函数可以 `Math.round()`，服务调用却要 `call "random.email"`？**

#### 问题 2: 冗余关键字

```dsl
call "random.email" into email

# 拆解
call       # ❌ 冗余关键字 (Python 没有 call)
"..."      # ❌ 为什么用字符串？
into       # ❌ 冗余 (let 已表达赋值)
```

#### 问题 3: 不能用于表达式

```dsl
# ❌ 不能这样写 (call 是语句，不是表达式)
let users = [
    {name: "Alice", email: random.email()},  # 错误！
    {name: "Bob", email: random.email()}     # 错误！
]

# ❌ 不能这样写
log f"Generated email: {random.email()}"  # 错误！

# ✅ 只能这样写 (冗长)
call "random.email" into email1
call "random.email" into email2
let users = [
    {name: "Alice", email: email1},
    {name: "Bob", email: email2}
]
```

#### 问题 4: 给人"引用外部模块"的感觉

```dsl
call "random.email"  # 像是调用外部 Python 模块
call "http.get"      # 像是导入了一个 http 库
```

这与 Python 实际做法对比：
```python
# Python 实际做法
import random
email = random.email()  # 或者 faker.email()

import requests
response = requests.get(url="...", timeout=5000)
```

**问题**: DSL 中的 `random`, `http` 到底是什么？
- 是内置的"服务"？
- 是可扩展的"插件"？
- 还是外部的"模块"？

定位不清晰。

#### 问题 5: 与 v3.0 Python-style 理念冲突

v3.0 已经 Python 化：
- ✅ 缩进块（移除 `end`）
- ✅ Python 字面量（`True`/`False`/`None`）
- ✅ 系统变量无 `$` 前缀
- ✅ 内置函数 Python 风格调用

**但服务调用仍然是"特殊语法"**，破坏了一致性。

### 为什么需要改进？

1. **用户困惑**: Python 开发者看到 `call "random.email"` 会感到困惑
2. **学习成本**: 需要专门记忆服务调用的特殊语法
3. **表达能力受限**: 不能在表达式中使用，限制了灵活性
4. **设计不一致**: 违反了 v3.0 的 Python-style 理念

---

## 💡 Proposed Solution

### 设计理念

**将 `random`, `http` 等服务作为内置命名空间**，与 `Math`, `Date`, `JSON` 完全一致。

### 新语法设计

#### 基本调用

```dsl
# ✅ 新语法 (v3.1+)
let email = random.email()
let password = random.password(length: 16, special: True)
let user_id = random.uuid()

let response = http.get(url: api_url, timeout: 5000)
let result = http.post(url: api_url, body: {name: "Alice"})
```

#### 表达式中使用

```dsl
# ✅ 可用于数组字面量
let users = [
    {name: "Alice", email: random.email(), pwd: random.password()},
    {name: "Bob", email: random.email(), pwd: random.password()}
]

# ✅ 可用于对象字面量
let user = {
    id: random.uuid(),
    email: random.email(),
    created_at: Date.now()
}

# ✅ 可用于字符串插值
log f"Generated email: {random.email()}"
log f"User ID: {random.uuid()}"

# ✅ 可用于条件表达式
let status_code = http.get(url: api_url).status
if status_code == 200:
    log "Success"
```

#### 方法链式调用

```dsl
# ✅ Python-style 方法调用
let email = random.email()
let uppercase_email = email.upper()
```

### 语法对比

| 场景 | v3.0 旧语法 (🗑️) | v3.1+ 新语法 (✅) |
|------|------------------|-------------------|
| **基本调用** | `call "random.email" into email` | `let email = random.email()` |
| **带参数** | `call "random.password" with length=16 into pwd` | `let pwd = random.password(length: 16)` |
| **HTTP请求** | `call "http.get" with url="..." into response` | `let response = http.get(url: "...")` |
| **数组中** | 不支持 | `[random.email(), random.email()]` |
| **字符串插值** | 不支持 | `f"Email: {random.email()}"` |

### 详细说明

#### 1. 命名空间定义

**内置服务命名空间**:
- `random`: 随机数据生成服务
- `http`: HTTP 请求服务

**与内置函数命名空间平等**:
- `Math`: 数学函数
- `Date`: 日期时间函数
- `JSON`: JSON 处理函数

#### 2. random 命名空间方法

```dsl
# 邮箱生成
let email = random.email()  # 返回随机邮箱

# 密码生成
let password = random.password()                    # 默认12位
let strong_pwd = random.password(length: 16, special: True)

# 用户名生成
let username = random.username()

# 手机号生成
let phone = random.phone()
let cn_phone = random.phone(locale: "zh_CN")

# 数字生成
let dice = random.number(1, 6)          # 1-6之间随机数
let percentage = random.number(0, 100)  # 0-100之间随机数

# UUID 生成
let user_id = random.uuid()  # 返回 UUID v4
```

#### 3. http 命名空间方法

```dsl
# GET 请求
let response = http.get(url: "https://api.example.com/users")
let data = http.get(url: api_url, timeout: 5000, headers: {Authorization: "Bearer ..."})

# POST 请求
let result = http.post(url: api_url, body: {name: "Alice", email: "alice@example.com"})

# PUT 请求
let updated = http.put(url: api_url, body: user_data)

# DELETE 请求
let deleted = http.delete(url: api_url)

# PATCH 请求
let patched = http.patch(url: api_url, body: {status: "active"})
```

---

## 🔍 Semantics and Behavior

### AST 变更

#### 移除 (v4.0)

```python
@dataclass
class CallStatement(ASTNode):
    """
    [DEPRECATED] 旧的服务调用语句
    将在 v4.0 移除
    """
    service_path: str
    parameters: List[CallParameter]
    result_variable: Optional[str]
```

#### 新增 (v3.1)

**无需新增 AST 节点**，复用现有的 `MethodCall` 表达式：

```python
@dataclass
class MethodCall(Expression):
    """
    Method call expression (v2.0+)

    Syntax: object.method(arg1, arg2, ...)

    Examples:
        text.upper()
        Math.round(value)
        random.email()          # v3.1: 服务调用
        http.get(url: "...")    # v3.1: 服务调用
    """
    object: Expression
    method_name: str
    arguments: List[Expression] = field(default_factory=list)
```

### 解释器行为

#### ExpressionEvaluator 扩展

```python
# src/registration_system/dsl/expression_evaluator.py

BUILTIN_NAMESPACES = {
    'Math': MathNamespace,
    'Date': DateNamespace,
    'JSON': JSONNamespace,
    'random': RandomNamespace,  # v3.1 新增
    'http': HttpNamespace,       # v3.1 新增
}

def _eval_identifier(self, expr: Identifier):
    """
    评估标识符

    v3.1: 支持服务命名空间
    """
    # 1. 检查是否为内置命名空间
    if expr.name in BUILTIN_NAMESPACES:
        return NamespaceProxy(expr.name, BUILTIN_NAMESPACES[expr.name])

    # 2. 检查是否为系统命名空间
    if expr.name in SYSTEM_NAMESPACES:
        return SystemNamespaceProxy(expr.name, self.system_variables)

    # 3. 查找用户变量
    return self.symbol_table.get(expr.name, expr.line)

def _eval_method_call(self, expr: MethodCall):
    """
    评估方法调用

    v3.1: 支持命名空间方法调用 (random.email(), http.get())
    """
    obj = self.evaluate(expr.object)

    # 如果是命名空间代理
    if isinstance(obj, NamespaceProxy):
        return obj.call_method(expr.method_name, expr.arguments)

    # 原有逻辑: 对象方法调用
    ...
```

#### 命名空间实现

```python
# src/registration_system/dsl/builtin_namespaces.py

class RandomNamespace:
    """随机数据生成服务 (v3.1)"""

    @staticmethod
    def email():
        """生成随机邮箱"""
        from faker import Faker
        fake = Faker()
        return fake.email()

    @staticmethod
    def password(length=12, special=True):
        """生成随机密码"""
        import string, random
        chars = string.ascii_letters + string.digits
        if special:
            chars += string.punctuation
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def username():
        """生成随机用户名"""
        from faker import Faker
        return Faker().user_name()

    @staticmethod
    def phone(locale="en_US"):
        """生成随机手机号"""
        from faker import Faker
        fake = Faker(locale)
        return fake.phone_number()

    @staticmethod
    def number(min_val, max_val):
        """生成随机数"""
        import random
        return random.randint(min_val, max_val)

    @staticmethod
    def uuid():
        """生成 UUID"""
        import uuid
        return str(uuid.uuid4())


class HttpNamespace:
    """HTTP 请求服务 (v3.1)"""

    @staticmethod
    def get(url, timeout=30, headers=None):
        """HTTP GET 请求"""
        import requests
        response = requests.get(url, timeout=timeout, headers=headers)
        return response.json() if response.headers.get('content-type') == 'application/json' else response.text

    @staticmethod
    def post(url, body=None, timeout=30, headers=None):
        """HTTP POST 请求"""
        import requests
        response = requests.post(url, json=body, timeout=timeout, headers=headers)
        return response.json() if response.headers.get('content-type') == 'application/json' else response.text

    @staticmethod
    def put(url, body=None, timeout=30, headers=None):
        """HTTP PUT 请求"""
        import requests
        response = requests.put(url, json=body, timeout=timeout, headers=headers)
        return response.json() if response.headers.get('content-type') == 'application/json' else response.text

    @staticmethod
    def delete(url, timeout=30, headers=None):
        """HTTP DELETE 请求"""
        import requests
        response = requests.delete(url, timeout=timeout, headers=headers)
        return response.json() if response.headers.get('content-type') == 'application/json' else response.text

    @staticmethod
    def patch(url, body=None, timeout=30, headers=None):
        """HTTP PATCH 请求"""
        import requests
        response = requests.patch(url, json=body, timeout=timeout, headers=headers)
        return response.json() if response.headers.get('content-type') == 'application/json' else response.text
```

### 边界情况处理

#### 1. 命名冲突

```dsl
# ❌ 用户不能定义与服务命名空间同名的变量
let random = 10  # 错误: "random" 是保留的服务命名空间

# ✅ 解决: 在符号表中标记为保留字
```

**实现**:
```python
# src/registration_system/dsl/symbol_table.py

RESERVED_WORDS = {
    # 系统命名空间 (v3.0)
    'page', 'context', 'browser', 'env', 'config',
    # 内置函数命名空间 (v1.0)
    'Math', 'Date', 'JSON',
    # 服务命名空间 (v3.1)
    'random', 'http',
}
```

#### 2. 方法不存在

```dsl
let x = random.nonexistent()  # 错误: random 命名空间没有 nonexistent 方法
```

**错误处理**:
```python
def call_method(self, method_name, arguments):
    if not hasattr(self.namespace, method_name):
        raise ExecutionError(
            line=...,
            statement=f"{self.name}.{method_name}()",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"Method '{method_name}' not found in namespace '{self.name}'"
        )
    ...
```

#### 3. 参数错误

```dsl
let pwd = random.password(length: -5)  # 错误: length 必须为正数
```

**验证**:
```python
@staticmethod
def password(length=12, special=True):
    if length <= 0:
        raise ValueError("length must be positive")
    ...
```

#### 4. HTTP 请求失败

```dsl
let response = http.get(url: "https://invalid-url.com")  # 网络错误
```

**错误处理**:
```python
@staticmethod
def get(url, timeout=30, headers=None):
    import requests
    try:
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()  # 抛出 HTTP 错误
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ExecutionError(
            line=...,
            statement="http.get()",
            error_type=ExecutionError.RUNTIME_ERROR,
            message=f"HTTP request failed: {e}"
        )
```

---

## 📊 Impact Analysis

### 版本影响

| 阶段 | 版本号 | 变更类型 | 说明 |
|------|--------|---------|------|
| **Phase 1** | v3.1 | MINOR | 新增 Python-style 语法，旧语法标记 deprecated |
| **Phase 2** | v4.0 | MAJOR | 移除旧 `call` 语法 |

### 兼容性分析

#### v3.1 (新增阶段)

**向后兼容**: ✅ 完全兼容

```dsl
# ✅ 旧语法仍然工作 (显示废弃警告)
call "random.email" into email
[WARN] Line 1: 'call' statement is deprecated, use 'random.email()' instead

# ✅ 新语法可用
let email = random.email()
```

**迁移成本**: 低
- 现有脚本无需修改
- 可逐步迁移到新语法
- 废弃警告提示用户

#### v4.0 (移除阶段)

**向后兼容**: ❌ 不兼容 (BREAKING CHANGE)

```dsl
# ❌ 旧语法报错
call "random.email" into email
[ERROR] Line 1: 'call' statement has been removed in v4.0, use 'random.email()' instead
```

**迁移成本**: 中
- 需要修改所有使用 `call` 的脚本
- 提供自动迁移工具
- 至少提前一个版本警告

### 学习曲线

| 用户类型 | 学习成本 | 说明 |
|---------|---------|------|
| **Python 开发者** | ⭐ 极低 | 完全符合 Python 习惯，无需学习 |
| **v3.0 老用户** | ⭐⭐ 低 | 与内置函数调用方式一致，易于理解 |
| **新用户** | ⭐ 极低 | 统一的调用语法，降低学习成本 |

### 语法复杂度影响

| 维度 | v3.0 | v3.1 | 变化 | 评估 |
|------|------|------|------|------|
| **主语句数量** | 25 | 24 | -1 (移除 CallStatement) | ✅ 降低 |
| **表达式类型** | 12 | 12 | 0 (复用 MethodCall) | ✅ 不变 |
| **关键字数量** | ~82 | ~80 | -2 (移除 call, into) | ✅ 降低 |
| **内置命名空间** | 3 (Math, Date, JSON) | 5 (+random, +http) | +2 | ✅ 可接受 |

**总体评估**: ✅ 简化了语法，降低了复杂度

### 性能影响

**运行时性能**: 无影响
- `MethodCall` 表达式评估性能与旧 `CallStatement` 相同
- 命名空间查找为 O(1) 字典查找

**解析性能**: 微小提升
- 少了 `call` 关键字的特殊处理逻辑

---

## 🛠️ Implementation Plan

### Phase 1: v3.1 新增 (预计 2025-12)

#### 任务 1.1: 实现服务命名空间

**文件**: `src/registration_system/dsl/builtin_namespaces.py`

**任务**:
- [ ] 实现 `RandomNamespace` 类
  - [ ] `email()` 方法
  - [ ] `password(length, special)` 方法
  - [ ] `username()` 方法
  - [ ] `phone(locale)` 方法
  - [ ] `number(min_val, max_val)` 方法
  - [ ] `uuid()` 方法
- [ ] 实现 `HttpNamespace` 类
  - [ ] `get(url, timeout, headers)` 方法
  - [ ] `post(url, body, timeout, headers)` 方法
  - [ ] `put(url, body, timeout, headers)` 方法
  - [ ] `delete(url, timeout, headers)` 方法
  - [ ] `patch(url, body, timeout, headers)` 方法
- [ ] 错误处理
- [ ] 参数验证

**依赖**: `faker`, `requests`

#### 任务 1.2: 注册命名空间

**文件**: `src/registration_system/dsl/expression_evaluator.py`

**任务**:
- [ ] 在 `BUILTIN_NAMESPACES` 中添加 `random`, `http`
- [ ] 更新 `_eval_identifier()` 方法
- [ ] 更新 `_eval_method_call()` 方法
- [ ] 实现 `NamespaceProxy` 类 (如果不存在)

#### 任务 1.3: 保留字保护

**文件**: `src/registration_system/dsl/symbol_table.py`

**任务**:
- [ ] 在 `RESERVED_WORDS` 中添加 `random`, `http`
- [ ] 确保用户不能定义同名变量

#### 任务 1.4: 添加废弃警告

**文件**: `src/registration_system/dsl/interpreter.py`

**任务**:
- [ ] 在 `execute_call()` 方法中添加废弃警告
- [ ] 日志格式: `[WARN] Line X: 'call' statement is deprecated, use 'SERVICE.METHOD()' instead`

#### 任务 1.5: 测试

**文件**: `tests/dsl/test_service_namespaces.py`

**任务**:
- [ ] random 命名空间测试
  - [ ] 测试 `random.email()`
  - [ ] 测试 `random.password(length: 16, special: True)`
  - [ ] 测试 `random.number(1, 100)`
  - [ ] 测试 `random.uuid()`
- [ ] http 命名空间测试 (使用 mock)
  - [ ] 测试 `http.get(url: "...")`
  - [ ] 测试 `http.post(url: "...", body: {...})`
  - [ ] 测试错误处理
- [ ] 表达式中使用
  - [ ] 数组字面量中使用
  - [ ] 字符串插值中使用
- [ ] 废弃警告测试
  - [ ] 验证旧 `call` 语法显示警告
- [ ] 保留字测试
  - [ ] 验证不能定义 `let random = 10`

**覆盖率目标**: ≥ 90%

#### 任务 1.6: 文档更新

**文件**: `grammar/MASTER.md`

**任务**:
- [ ] 添加新语法行:
  ```markdown
  | 8.1a | Service Call (Python-style) | `SERVICE.method(args)` | ✅ | v3.1 | `_eval_method_call()` | ✅ | 推荐用法 |
  ```
- [ ] 标记旧语法为 deprecated:
  ```markdown
  | 8.1 | Call Service (deprecated) | `call "provider.method" [with PARAMS] [into VAR]` | 🗑️ | v1.0-v3.0 | `_parse_call()` | ✅ | v3.1: deprecated, v4.0: removed |
  ```

**文件**: `grammar/CHANGELOG.md`

**任务**:
- [ ] 添加 v3.1 变更记录:
  ```markdown
  ## [3.1.0] - 2025-12-XX

  ### Added
  - ✅ Python-style service call syntax: `random.email()`, `http.get(url: "...")`
  - ✅ `random` namespace: email, password, username, phone, number, uuid
  - ✅ `http` namespace: get, post, put, delete, patch

  ### Deprecated
  - 🗑️ `call "service.method"` syntax (use `service.method()` instead)
  - Will be removed in v4.0
  ```

**文件**: `grammar/MIGRATION-GUIDE-v3.1.md` (新建)

**任务**:
- [ ] 创建迁移指南
- [ ] 语法对照表
- [ ] 示例代码
- [ ] 迁移步骤

#### 任务 1.7: 更新示例

**文件**: `examples/flows/*.flow`

**任务**:
- [ ] 更新示例使用新语法
- [ ] 保留旧语法示例 (标注 deprecated)

### Phase 2: v4.0 移除 (预计 2026-XX)

#### 任务 2.1: 移除旧语法

**文件**: `src/registration_system/dsl/parser.py`

**任务**:
- [ ] 移除 `_parse_call()` 方法
- [ ] 移除 `call` 关键字处理

**文件**: `src/registration_system/dsl/interpreter.py`

**任务**:
- [ ] 移除 `execute_call()` 方法
- [ ] 移除 `CallStatement` 处理分支

**文件**: `src/registration_system/dsl/ast_nodes.py`

**任务**:
- [ ] 删除 `CallStatement` 定义
- [ ] 删除 `CallParameter` 定义

#### 任务 2.2: 更新文档

**文件**: `grammar/MASTER.md`

**任务**:
- [ ] 删除 `call` 语法行 (8.1)
- [ ] 保留 Python-style 语法行 (8.1a → 8.1)

**文件**: `grammar/CHANGELOG.md`

**任务**:
- [ ] 添加 v4.0 变更记录:
  ```markdown
  ## [4.0.0] - 2026-XX-XX

  ### Removed
  - ❌ `call "service.method"` syntax (removed, use `service.method()` instead)
  ```

#### 任务 2.3: 测试清理

**文件**: `tests/`

**任务**:
- [ ] 移除旧 `call` 语法测试用例
- [ ] 保留迁移测试 (验证正确报错)

---

## 🧪 Test Plan

### 测试用例分类

#### Category 1: 基本功能测试

```python
def test_random_email():
    """测试 random.email()"""
    script = '''
    let email = random.email()
    assert email contains "@"
    '''
    # 验证返回邮箱格式

def test_random_password():
    """测试 random.password()"""
    script = '''
    let pwd = random.password(length: 16, special: True)
    assert len(pwd) == 16
    '''
    # 验证密码长度和字符集

def test_random_number():
    """测试 random.number()"""
    script = '''
    let dice = random.number(1, 6)
    assert dice >= 1 and dice <= 6
    '''
    # 验证范围

def test_http_get():
    """测试 http.get()"""
    script = '''
    let response = http.get(url: "https://api.example.com/users")
    '''
    # 使用 mock，验证请求参数
```

#### Category 2: 表达式使用测试

```python
def test_service_in_array_literal():
    """测试在数组字面量中使用"""
    script = '''
    let emails = [random.email(), random.email()]
    assert len(emails) == 2
    '''

def test_service_in_string_interpolation():
    """测试在字符串插值中使用"""
    script = '''
    log f"Email: {random.email()}"
    '''

def test_service_in_object_literal():
    """测试在对象字面量中使用"""
    script = '''
    let user = {
        id: random.uuid(),
        email: random.email()
    }
    assert user.id != None
    '''
```

#### Category 3: 错误处理测试

```python
def test_method_not_found():
    """测试方法不存在"""
    script = '''
    let x = random.nonexistent()
    '''
    # 期望: ExecutionError "Method 'nonexistent' not found"

def test_invalid_parameters():
    """测试无效参数"""
    script = '''
    let pwd = random.password(length: -5)
    '''
    # 期望: ValueError "length must be positive"

def test_http_request_failure():
    """测试 HTTP 请求失败"""
    script = '''
    let response = http.get(url: "https://invalid-url-12345.com")
    '''
    # 期望: ExecutionError "HTTP request failed"
```

#### Category 4: 保留字测试

```python
def test_reserved_namespace():
    """测试不能定义与命名空间同名的变量"""
    script = '''
    let random = 10
    '''
    # 期望: SymbolError "'random' is a reserved word"

def test_reserved_http():
    """测试 http 也是保留字"""
    script = '''
    let http = "test"
    '''
    # 期望: SymbolError "'http' is a reserved word"
```

#### Category 5: 废弃警告测试 (v3.1)

```python
def test_deprecated_call_syntax():
    """测试旧 call 语法显示废弃警告"""
    script = '''
    call "random.email" into email
    '''
    # 验证:
    # 1. 脚本仍然正常执行
    # 2. 日志包含警告: "[WARN] Line 1: 'call' statement is deprecated"

def test_deprecated_warning_content():
    """测试废弃警告内容"""
    script = '''
    call "random.password" with length=16 into pwd
    '''
    # 验证警告建议新语法:
    # "[WARN] ... use 'random.password(length: 16)' instead"
```

#### Category 6: 兼容性测试 (v3.1)

```python
def test_old_and_new_syntax_coexist():
    """测试新旧语法可以共存"""
    script = '''
    # 旧语法
    call "random.email" into email1

    # 新语法
    let email2 = random.email()

    assert email1 contains "@"
    assert email2 contains "@"
    '''
```

#### Category 7: 迁移测试 (v4.0)

```python
def test_v4_call_syntax_removed():
    """测试 v4.0 旧语法已移除"""
    script = '''
    call "random.email" into email
    '''
    # 期望: SyntaxError "'call' statement has been removed in v4.0"
```

### 测试覆盖目标

| 类别 | 测试用例数 | 覆盖率目标 |
|------|-----------|-----------|
| random 命名空间 | 10+ | ≥ 95% |
| http 命名空间 | 10+ | ≥ 95% |
| 表达式使用 | 8+ | ≥ 90% |
| 错误处理 | 6+ | ≥ 90% |
| 保留字 | 4+ | 100% |
| 废弃警告 | 4+ | 100% |
| **总计** | **42+** | **≥ 90%** |

---

## 📚 Documentation Changes

### MASTER.md 变更

#### 添加新语法 (v3.1)

**位置**: 8. Other Statements 章节

```markdown
| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 8.1 | Service Call (Python-style) | `SERVICE.method(args)` | ✅ | v3.1 | `_eval_method_call()` | ✅ | 推荐用法，支持表达式 |
| 8.2 | ~~Call Service~~ (deprecated) | `call "provider.method" [with PARAMS] [into VAR]` | 🗑️ | v1.0-v3.0 | `_parse_call()` | ✅ | v3.1 deprecated, v4.0 removed |
```

#### 添加服务命名空间文档

**新增章节**: 内置服务命名空间

```markdown
### 🔌 Built-in Service Namespaces (v3.1+)

#### random 命名空间

随机数据生成服务

**方法**:

| 方法 | 参数 | 返回值 | 说明 |
|------|------|-------|------|
| `email()` | 无 | String | 生成随机邮箱 |
| `password(length=12, special=True)` | length: Int, special: Bool | String | 生成随机密码 |
| `username()` | 无 | String | 生成随机用户名 |
| `phone(locale="en_US")` | locale: String | String | 生成随机手机号 |
| `number(min, max)` | min: Int, max: Int | Int | 生成随机数 [min, max] |
| `uuid()` | 无 | String | 生成 UUID v4 |

**示例**:
```dsl
let email = random.email()
let strong_pwd = random.password(length: 16, special: True)
let dice = random.number(1, 6)
let user_id = random.uuid()
```

#### http 命名空间

HTTP 请求服务

**方法**:

| 方法 | 参数 | 返回值 | 说明 |
|------|------|-------|------|
| `get(url, timeout=30, headers=None)` | url: String, timeout: Int, headers: Object | Any | HTTP GET 请求 |
| `post(url, body=None, timeout=30, headers=None)` | url: String, body: Any, timeout: Int, headers: Object | Any | HTTP POST 请求 |
| `put(url, body=None, timeout=30, headers=None)` | url: String, body: Any, timeout: Int, headers: Object | Any | HTTP PUT 请求 |
| `delete(url, timeout=30, headers=None)` | url: String, timeout: Int, headers: Object | Any | HTTP DELETE 请求 |
| `patch(url, body=None, timeout=30, headers=None)` | url: String, body: Any, timeout: Int, headers: Object | Any | HTTP PATCH 请求 |

**示例**:
```dsl
let response = http.get(url: "https://api.example.com/users")
let created = http.post(url: api_url, body: {name: "Alice"})
```
```

### CHANGELOG.md 变更

```markdown
## [3.1.0] - 2025-12-XX

### Added
- ✅ **Python-style service call syntax**:
  - 支持 `service.method(args)` 语法调用服务
  - 示例: `random.email()`, `http.get(url: "...")`

- ✅ **random 命名空间**: 随机数据生成服务
  - `random.email()` - 生成随机邮箱
  - `random.password(length, special)` - 生成随机密码
  - `random.username()` - 生成随机用户名
  - `random.phone(locale)` - 生成随机手机号
  - `random.number(min, max)` - 生成随机数
  - `random.uuid()` - 生成 UUID

- ✅ **http 命名空间**: HTTP 请求服务
  - `http.get(url, timeout, headers)` - GET 请求
  - `http.post(url, body, timeout, headers)` - POST 请求
  - `http.put(url, body, timeout, headers)` - PUT 请求
  - `http.delete(url, timeout, headers)` - DELETE 请求
  - `http.patch(url, body, timeout, headers)` - PATCH 请求

### Deprecated
- 🗑️ **`call "service.method"` 语法已废弃**
  - 使用新语法: `service.method()` 替代
  - 旧语法仍可用，但会显示废弃警告
  - 将在 v4.0 移除

### Changed
- ✅ 服务调用现在支持在表达式中使用
  - 可用于数组字面量: `[random.email(), random.email()]`
  - 可用于字符串插值: `f"Email: {random.email()}"`
  - 可用于对象字面量: `{id: random.uuid()}`

### Migration Guide
- 详见 `grammar/MIGRATION-GUIDE-v3.1.md`
```

### 迁移指南 (新建文件)

**文件**: `grammar/MIGRATION-GUIDE-v3.1.md`

```markdown
# v3.1 Migration Guide

## 从 call 语法迁移到 Python-style 服务调用

### 迁移对照表

| v3.0 旧语法 (🗑️) | v3.1 新语法 (✅) |
|------------------|------------------|
| `call "random.email" into email` | `let email = random.email()` |
| `call "random.password" with length=16 into pwd` | `let pwd = random.password(length: 16)` |
| `call "random.number" with 1, 100 into dice` | `let dice = random.number(1, 100)` |
| `call "http.get" with url="..." into response` | `let response = http.get(url: "...")` |
| `call "http.post" with url="...", body={...} into result` | `let result = http.post(url: "...", body: {...})` |

### 迁移步骤

1. **查找所有 call 语句**
   ```bash
   grep -r "call \"" your_project/
   ```

2. **逐个替换**
   - 移除 `call` 关键字
   - 移除引号
   - 将 `with param=value` 改为 `(param: value)`
   - 将 `into var` 改为 `let var = ...`

3. **测试**
   - 运行测试套件
   - 验证行为一致

4. **提交**
   - 提交迁移后的代码

### 示例

**Before (v3.0)**:
```dsl
step "User Registration":
    call "random.email" into email
    call "random.password" with length=16, special=True into password

    type email into "#email"
    type password into "#password"

    click "#register"

    call "http.get" with url=api_url into response
    assert response.status == 200
```

**After (v3.1)**:
```dsl
step "User Registration":
    let email = random.email()
    let password = random.password(length: 16, special: True)

    type email into "#email"
    type password into "#password"

    click "#register"

    let response = http.get(url: api_url)
    assert response.status == 200
```

### 新增能力

#### 1. 在数组中使用

```dsl
# v3.0: 不支持
call "random.email" into email1
call "random.email" into email2
let emails = [email1, email2]

# v3.1: 直接使用
let emails = [random.email(), random.email()]
```

#### 2. 在字符串插值中使用

```dsl
# v3.0: 不支持
call "random.email" into email
log f"Generated: {email}"

# v3.1: 直接使用
log f"Generated: {random.email()}"
```

#### 3. 在对象字面量中使用

```dsl
# v3.0: 不支持
call "random.uuid" into id
call "random.email" into email
let user = {id: id, email: email}

# v3.1: 直接使用
let user = {
    id: random.uuid(),
    email: random.email()
}
```
```

---

## 🔄 Alternative Solutions

### Solution B: 保留 call，去掉字符串

```dsl
# 改进：去掉字符串，保留 call 关键字
call random.email() into email
call http.get(url: api_url, timeout: 5000) into response

# 或者更简化（去掉 into，用 let）
let email = call random.email()
let response = call http.get(url: api_url, timeout: 5000)
```

#### 优点
- ✅ 改动较小：只需调整 parser，不需要重构 AST
- ✅ 保留 call 区分：可以区分"服务调用"和"普通函数"
- ✅ 向后兼容：可以同时支持旧语法

#### 缺点
- ❌ 仍有 call 关键字：不够 Python
- ❌ 仍不能用于表达式：如果保持语句形式
- ❌ 语义不清：call 到底表示什么特殊含义？

#### 为什么不选择？

1. **语义不清晰**: `call` 关键字暗示"调用外部服务"，但 `random`, `http` 是内置功能，不是外部的
2. **不够 Python**: Python 没有 `call` 关键字
3. **仍有冗余**: 如果最终还是要用 `let email = call random.email()`，为什么不直接 `let email = random.email()`？

### Solution C: 引入 import 机制

```dsl
# Python-style import
import random
import http

# 然后像 Python 一样使用
let email = random.email()
let response = http.get(url: api_url)
```

#### 优点
- ✅ 最接近 Python：完全模仿 Python 的模块系统
- ✅ 明确的命名空间管理：用户知道哪些是导入的
- ✅ 可扩展性强：可以支持用户自定义模块

#### 缺点
- ❌ 复杂度高：需要实现完整的模块系统
- ❌ 不必要：DSL 的定位可能不需要模块系统
- ❌ 学习成本：增加了语法复杂度

#### 为什么不选择？

1. **过度设计**: 对于内置服务，import 机制过于复杂
2. **违背 DSL 定位**: DSL 是领域特定语言，不是通用编程语言
3. **学习成本高**: 用户需要理解模块系统

### Solution A (Proposed) vs B vs C

| 维度 | Solution A (Proposed) | Solution B (简化 call) | Solution C (import) |
|------|----------------------|------------------------|---------------------|
| **Python 一致性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **语法简洁性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **表达式支持** | ✅ | 取决于实现 | ✅ |
| **实现复杂度** | 中 | 低 | 高 |
| **向后兼容** | ✅ (v3.1 保留旧语法) | ✅ | ❌ |
| **学习成本** | 低 | 中 | 中 |
| **可扩展性** | 高 | 中 | 极高 |

**结论**: Solution A (将服务作为内置命名空间) 是最佳选择，平衡了 Python 一致性、简洁性和实现复杂度。

---

## 💬 Discussion Record

### 2025-11-27: 初始讨论

**参与者**: 用户, AI Assistant

**讨论要点**:

1. **用户观察**:
   > "我觉得 call 语法有点别扭，觉得有点类似引用 python 外部模块的做法，并且调用 call 也比较怪异，和 python 的做法差别有点大。"

2. **问题确认**:
   - ✅ 语法不一致 (call vs 内置函数)
   - ✅ 冗余关键字 (call + into)
   - ✅ 不能用于表达式
   - ✅ 与 v3.0 Python-style 理念冲突

3. **解决方案讨论**:
   - 方案 A: Python 化 (推荐)
   - 方案 B: 简化 call
   - 方案 C: import 机制

4. **决策**:
   - 采用方案 A：将 random, http 作为内置命名空间
   - 理由: 最符合 v3.0 Python-style 设计理念

---

## ✅ Decision

### 最终决策

**批准方案 A**: Python-Style Service Call Syntax

### 决策理由

1. **完全 Python 化** ⭐⭐⭐⭐⭐
   - 与内置函数语法完全一致
   - Python 开发者零学习成本
   - 符合 v3.0 整体设计理念

2. **增强表达能力** ⭐⭐⭐⭐⭐
   - 可用于任何表达式位置
   - 支持数组、对象字面量、字符串插值
   - 支持方法链式调用

3. **简化语法** ⭐⭐⭐⭐⭐
   - 移除冗余关键字 `call`, `into`
   - 降低语法复杂度
   - 统一调用模式

4. **易于扩展** ⭐⭐⭐⭐
   - 添加新服务只需新增命名空间类
   - 无需修改 parser 或 AST
   - 与现有架构自然融合

5. **向后兼容** ⭐⭐⭐⭐
   - v3.1 保留旧语法 (带警告)
   - 提供迁移指南和工具
   - v4.0 移除 (充分的迁移期)

### 批准条件

- [x] 详细的实现计划
- [x] 完整的测试计划 (≥ 90% 覆盖率)
- [x] 迁移指南
- [x] 文档更新计划
- [x] 向后兼容策略

### 批准人

**AI Assistant** (2025-11-27)

---

## 📅 Implementation Timeline

### v3.1 实施时间线 (预计 4 周)

#### Week 1: 实现核心功能
- [ ] Day 1-2: 实现 RandomNamespace 类
- [ ] Day 3-4: 实现 HttpNamespace 类
- [ ] Day 5: 注册命名空间到 BUILTIN_NAMESPACES
- [ ] 交付物: 可用的 random, http 命名空间

#### Week 2: 集成和警告
- [ ] Day 1-2: 更新 ExpressionEvaluator
- [ ] Day 3: 添加保留字保护
- [ ] Day 4-5: 实现废弃警告
- [ ] 交付物: 新旧语法共存

#### Week 3: 测试
- [ ] Day 1-3: 编写测试用例 (42+ cases)
- [ ] Day 4-5: 测试覆盖率优化
- [ ] 交付物: ≥ 90% 测试覆盖率

#### Week 4: 文档和发布
- [ ] Day 1-2: 更新 MASTER.md, CHANGELOG.md
- [ ] Day 3: 编写迁移指南
- [ ] Day 4: 更新示例代码
- [ ] Day 5: 发布 v3.1.0
- [ ] 交付物: 完整文档和发布包

### v4.0 移除时间线 (预计 1 周)

**前提**: v3.1 至少稳定运行 6 个月

#### Week 1: 移除旧语法
- [ ] Day 1-2: 移除 CallStatement 相关代码
- [ ] Day 3: 清理测试用例
- [ ] Day 4: 更新文档
- [ ] Day 5: 发布 v4.0.0

---

## 📎 Appendix

### A. 完整实现文件清单

**新增文件**:
- `src/registration_system/dsl/builtin_namespaces.py` (RandomNamespace, HttpNamespace)
- `tests/dsl/test_service_namespaces.py` (测试用例)
- `grammar/MIGRATION-GUIDE-v3.1.md` (迁移指南)

**修改文件**:
- `src/registration_system/dsl/expression_evaluator.py` (注册命名空间)
- `src/registration_system/dsl/symbol_table.py` (添加保留字)
- `src/registration_system/dsl/interpreter.py` (添加废弃警告)
- `grammar/MASTER.md` (更新语法规范)
- `grammar/CHANGELOG.md` (记录变更)
- `examples/flows/*.flow` (更新示例)

**删除文件** (v4.0):
- 无 (代码内删除，不删除文件)

### B. 依赖项

**新增依赖**:
- `faker` (用于 RandomNamespace)
- `requests` (用于 HttpNamespace)

**requirements.txt**:
```
faker>=20.0.0
requests>=2.31.0
```

### C. 性能基准

**预期性能** (与旧 call 语法对比):

| 操作 | v3.0 call | v3.1 Python-style | 变化 |
|------|-----------|-------------------|------|
| 解析时间 | 100ms | 95ms | -5% ↓ |
| 执行时间 | 50ms | 50ms | 0 |
| 内存占用 | 10MB | 10MB | 0 |

**测试方法**:
```python
# 性能测试脚本
import timeit

old_syntax = '''
call "random.email" into email
'''

new_syntax = '''
let email = random.email()
'''

# 测试 1000 次
old_time = timeit.timeit(lambda: parse_and_execute(old_syntax), number=1000)
new_time = timeit.timeit(lambda: parse_and_execute(new_syntax), number=1000)

print(f"Old: {old_time}ms, New: {new_time}ms, Improvement: {(old_time-new_time)/old_time*100}%")
```

---

**提案状态**: 🟡 Draft
**下一步**: 等待批准，开始实施 Phase 1
**预计完成**: v3.1 (2025-12), v4.0 (2026-XX)
