# Grammar Proposal #010: Resource Constructor Refactoring

> **提案编号**: #010
> **提出日期**: 2025-11-30
> **提出人**: Flowby Core Team
> **状态**: 💭 Under Discussion
> **目标版本**: v6.0
> **影响级别**: MAJOR (Breaking Change)  

---

## 1. 摘要

本提案建议将 `resource` 特殊语句重构为 `Resource()` 内置构造函数，实现更灵活的动态 API 客户端创建，解决当前静态初始化的局限性。

---

## 2. 动机

### 2.1 当前问题

现有的 `resource` 语句采用声明式语法，参数在声明时静态绑定：

```dsl
# 当前语法 - 参数在声明时就固定了
resource user_api:
    spec: "openapi/user-service.yml"
    base_url: "https://api.example.com"      # ← 编译时确定
    auth: {type: "bearer", token: env.TOKEN}  # ← 只能用 env
    timeout: 30
```

### 2.2 局限性场景

#### 场景 1：运行时动态配置

```dsl
# ❌ 无法实现：根据用户输入选择环境
let environment = input("选择环境 (dev/prod): ")

resource api:
    base_url: environment == "prod" ? PROD_URL : DEV_URL  # 不支持表达式
```

#### 场景 2：动态获取 Token

```dsl
step "登录获取 token":
    let response = http.post(LOGIN_URL, credentials)
    let token = response.access_token
    
    # ❌ 无法实现：如何把动态获取的 token 传给已声明的 resource？
```

#### 场景 3：多实例创建

```dsl
# ❌ 无法实现：为每个环境创建不同配置的 API 客户端
for env in ["dev", "staging", "prod"]:
    # 需要动态创建多个实例
```

### 2.3 问题本质

| 方面 | 当前设计 | 理想设计 |
|------|---------|---------|
| **初始化时机** | 声明时（静态） | 可延迟到使用时（动态） |
| **参数来源** | 字面量 + env | 任意表达式 + 运行时变量 |
| **灵活性** | 单一配置 | 可根据条件创建多个实例 |
| **语法类型** | 特殊语句 | 普通表达式 |

---

## 3. 设计方案

### 3.1 新语法：`Resource()` 构造函数

将 `resource` 从特殊语句改为内置构造函数，返回 `ResourceNamespace` 对象。

#### 基本语法

```dsl
let api = Resource(spec_file, [options])
```

#### 参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `spec_file` | String | ✅ | OpenAPI 规范文件路径 |
| `base_url` | String | ❌ | API 基础 URL（覆盖 OpenAPI 定义） |
| `auth` | Object | ❌ | 认证配置 |
| `timeout` | Integer | ❌ | 请求超时时间（秒），默认 30 |
| `headers` | Object | ❌ | 默认 HTTP headers |
| `response_mapping` | Object | ❌ | 响应数据映射配置 |
| `validate_response` | Boolean | ❌ | 是否验证响应，默认 True |
| `resilience` | Object | ❌ | 弹性处理配置（重试+断路器） |
| `mock` | Object | ❌ | Mock 模式配置 |

### 3.2 语法示例

#### 基本用法

```dsl
# 最简形式
let user_api = Resource("openapi/user-service.yml")

# 使用 API
let user = user_api.getUser(userId = 123)
log f"用户: {user.name}"
```

#### 带配置

```dsl
let api = Resource("openapi/api.yml",
    base_url = "https://api.example.com/v1",
    auth = {type: "bearer", token: env.API_TOKEN},
    timeout = 60,
    headers = {"X-Client-ID": "flowby"}
)
```

#### 动态配置（核心优势）

```dsl
step "动态初始化 API":
    # 先登录获取 token
    let login_response = http.post("https://auth.example.com/login", {
        username: env.USERNAME,
        password: env.PASSWORD
    })
    let token = login_response.access_token
    
    # 使用动态 token 创建 API 客户端
    let api = Resource("api.yml", 
        auth = {type: "bearer", token: token}
    )
    
    # 调用 API
    let user = api.getUser(userId = 123)
```

#### 多实例支持

```dsl
# 为不同环境创建不同的 API 客户端
let dev_api = Resource("api.yml", 
    base_url = "https://dev.api.example.com"
)
let prod_api = Resource("api.yml", 
    base_url = "https://api.example.com"
)

# 根据条件使用
let api = is_production ? prod_api : dev_api
let users = api.listUsers()
```

#### 条件创建

```dsl
let environment = input("选择环境 (dev/prod): ", default = "dev")

let api = Resource("api.yml",
    base_url = environment == "prod" 
        ? "https://api.example.com" 
        : "https://dev.api.example.com",
    timeout = environment == "prod" ? 60 : 10
)
```

#### 循环中创建

```dsl
let environments = ["dev", "staging", "prod"]
let apis = []

for env in environments:
    let api = Resource("api.yml",
        base_url = f"https://{env}.api.example.com"
    )
    apis.append(api)
```

---

## 4. 对比分析

### 4.1 语法对比

| 方面 | 旧 `resource` 语句 | 新 `Resource()` 构造函数 |
|------|-------------------|-------------------------|
| **语法类型** | 特殊语句 | 普通表达式 |
| **赋值方式** | `resource name:` 隐式绑定 | `let name = Resource(...)` 显式赋值 |
| **初始化时机** | 解析时/顶层 | 运行时/任意位置 |
| **参数类型** | 字面量 + env | 任意表达式 |
| **多实例** | 需要多个 resource 声明 | 自然支持 |
| **条件逻辑** | 不支持 | 完全支持 |

### 4.2 代码对比

**旧语法**:
```dsl
resource user_api:
    spec: "openapi/user-service.yml"
    base_url: "https://api.example.com"
    auth: {type: "bearer", token: env.TOKEN}
    timeout: 30

step "使用 API":
    let user = user_api.getUser(userId = 123)
```

**新语法**:
```dsl
let user_api = Resource("openapi/user-service.yml",
    base_url = "https://api.example.com",
    auth = {type: "bearer", token: env.TOKEN},
    timeout = 30
)

step "使用 API":
    let user = user_api.getUser(userId = 123)
```

---

## 5. 实现计划

### 5.1 代码改动

#### 移除

| 文件 | 改动 |
|------|------|
| `lexer.py` | 移除 `RESOURCE` token（可选保留用于错误提示） |
| `parser.py` | 移除 `_parse_resource()` 方法 |
| `ast_nodes.py` | 移除 `ResourceStatement` 类 |
| `interpreter.py` | 移除 `_execute_resource()` 方法 |

#### 新增/修改

| 文件 | 改动 |
|------|------|
| `builtin_functions.py` | 添加 `Resource()` 内置函数 |
| `expression_evaluator.py` | 处理 `Resource()` 调用，返回 `ResourceNamespace` |
| `resource_namespace.py` | 保持不变（复用现有实现） |

### 5.2 实现步骤

1. **Phase 1: 添加 Resource() 函数** (2-3 天)
   - 在 `builtin_functions.py` 注册 `Resource` 函数
   - 在 `expression_evaluator.py` 实现调用逻辑
   - 复用 `OpenAPISpec` 和 `ResourceNamespace`

2. **Phase 2: 废弃 resource 语句** (1 天)
   - 标记 `resource` 语句为废弃
   - 添加迁移警告信息

3. **Phase 3: 移除旧代码** (1 天)
   - 移除 `_parse_resource()`
   - 移除 `ResourceStatement`
   - 移除 `_execute_resource()`

4. **Phase 4: 测试和文档** (2 天)
   - 更新所有测试用例
   - 更新文档和示例

### 5.3 伪代码实现

```python
# builtin_functions.py

def builtin_Resource(spec_file: str, **kwargs) -> ResourceNamespace:
    """
    Resource 构造函数
    
    创建基于 OpenAPI 规范的 API 客户端
    
    Args:
        spec_file: OpenAPI 规范文件路径
        **kwargs: 配置选项 (base_url, auth, timeout, headers, ...)
    
    Returns:
        ResourceNamespace 对象
    """
    from .openapi_loader import OpenAPISpec
    from .resource_namespace import ResourceNamespace
    
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
```

---

## 6. 向后兼容

### 6.1 迁移策略

#### 选项 A：立即移除（Breaking Change）

- 在 v6.0 中直接移除 `resource` 语句
- 提供迁移指南和脚本

#### 选项 B：渐进式废弃（推荐）

1. **v5.2**: 添加 `Resource()` 函数，两种语法并存
2. **v5.3**: 标记 `resource` 语句为废弃，运行时警告
3. **v6.0**: 移除 `resource` 语句

### 6.2 迁移示例

**旧代码**:
```dsl
resource user_api from "openapi/user-service.yml"
```

**新代码**:
```dsl
let user_api = Resource("openapi/user-service.yml")
```

**带配置的迁移**:

```dsl
# 旧
resource api:
    spec: "api.yml"
    base_url: "https://api.example.com"
    auth: {type: "bearer", token: env.TOKEN}

# 新
let api = Resource("api.yml",
    base_url = "https://api.example.com",
    auth = {type: "bearer", token: env.TOKEN}
)
```

### 6.3 自动迁移脚本

可提供脚本自动转换旧语法：

```bash
flowby migrate --from v5 --to v6 script.flow
```

---

## 7. 设计优势总结

| 优势 | 说明 |
|------|------|
| **一致性** | 与其他对象创建方式一致（`let x = ...`） |
| **灵活性** | 参数可以是任意表达式 |
| **简洁性** | 去掉一个特殊语句，减少语法复杂度 |
| **动态性** | 可在任意代码位置创建，支持条件逻辑 |
| **可组合性** | 可作为表达式参与其他运算 |
| **多实例** | 自然支持创建多个不同配置的实例 |

---

## 8. 风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| 破坏现有代码 | 中 | 提供迁移期和迁移脚本 |
| 用户学习成本 | 低 | 新语法更直观，符合编程习惯 |
| 实现复杂度 | 低 | 复用现有 ResourceNamespace |

---

## 9. 替代方案

### 9.1 方案 B：延迟配置

```dsl
resource api from "api.yml"  # 先声明

step "配置":
    api.configure(auth = {token: dynamic_token})  # 运行时更新
```

**问题**: 需要引入可变状态，不符合声明式风格。

### 9.2 方案 C：类型+实例化分离

```dsl
resourceType UserAPI from "api.yml"  # 声明类型
let api = new UserAPI(auth = ...)     # 实例化
```

**问题**: 引入两个新关键字，过于复杂。

### 9.3 结论

`Resource()` 构造函数是最佳方案，简洁、灵活、一致。

---

## 10. 参考

- [PROPOSAL-007-openapi-resource-statement.md](../../grammar/proposals/PROPOSAL-007-openapi-resource-statement.md) - 原始 resource 语句提案
- [resource_namespace.py](../../src/flowby/resource_namespace.py) - ResourceNamespace 实现
- [openapi_loader.py](../../src/flowby/openapi_loader.py) - OpenAPI 加载器

---

## 11. 决策

- [ ] 批准提案
- [ ] 确定迁移策略（立即移除 / 渐进式废弃）
- [ ] 确定目标版本（v5.2 / v6.0）

---

**反馈和讨论**: 欢迎在 GitHub Issues 或 Discussions 中提出意见。
