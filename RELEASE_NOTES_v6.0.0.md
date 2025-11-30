# Release Notes - Flowby v6.0.0

**发布日期**: 2025-11-30
**语法版本**: 6.0.0
**发布类型**: 🔴 MAJOR (Breaking Changes)
**标签**: v6.0.0

---

## 📣 重要公告

**这是一个包含破坏性变更的主要版本！**

v6.0.0 移除了 `resource` 语句语法，引入了新的 `Resource()` 构造函数。所有使用 `resource` 语句的代码需要迁移到新语法。

---

## 🚀 核心变更

### ✨ 新增功能

#### 1. **Resource() 构造函数** (Grammar Proposal #010)

现代化的 API 客户端创建方式，替代 v4.2 的 `resource` 语句。

**特性：**
- ✅ **动态配置**：运行时生成 token、URL 等
- ✅ **函数式 API**：与其他内置函数一致
- ✅ **完整参数支持**：base_url, auth, timeout, headers, resilience, mock
- ✅ **自动上下文注入**：无需手动传递 ExecutionContext
- ✅ **更好的测试性**：可单元测试，易于模拟

**语法示例：**

```dsl
# 基本用法
let api = Resource("openapi/spec.yml")

# 完整配置
let api = Resource("spec.yml",
    base_url = "https://api.example.com",
    timeout = 60,
    auth = {type: "bearer", token: env.API_TOKEN},
    headers = {"X-Client": "flowby"},
    resilience = {
        retry: {max_retries: 3, strategy: "exponential"}
    }
)

# 动态配置（关键优势）
step "登录并初始化 API":
    let login_response = http.post(
        "https://auth.example.com/login",
        body = {username: env.USER, password: env.PASS}
    )

    # 使用登录返回的 token 动态创建 API 客户端
    let api = Resource("spec.yml",
        auth = {type: "bearer", token: login_response.access_token}
    )

    let user_data = api.getUserProfile()
    log f"欢迎, {user_data.name}!"
```

**技术细节：**
- 新增 `Resource()` 内置函数（`builtin_functions.py`，110 行）
- 自动注入 ExecutionContext（`expression_evaluator.py`）
- 词法分析器支持首字母大写标识符（`lexer.py`）
- 完整的参数验证和错误处理

---

### 🗑️ 移除功能 (BREAKING CHANGES)

#### 1. **移除 `resource` 语句语法**

旧的声明式 `resource` 语句已完全移除。

**移除的语法：**
```dsl
# ❌ 已移除：简单形式
resource api from "spec.yml"

# ❌ 已移除：配置块形式
resource api:
    spec: "spec.yml"
    base_url: "https://api.example.com"
    timeout: 60
```

**技术变更：**
- 删除 `TokenType.RESOURCE` 枚举
- 删除 `ResourceStatement` AST 节点
- 删除 `_parse_resource()` 解析方法
- 删除 `_execute_resource()` 执行方法
- 总计删除 **340 行代码**

---

## 📦 迁移指南

### 快速迁移

#### **简单用法**

```dsl
# 旧代码（v4.2-v5.1）
resource user_api from "openapi/users.yml"

# 新代码（v6.0+）
let user_api = Resource("openapi/users.yml")
```

#### **带配置**

```dsl
# 旧代码
resource api:
    spec: "api.yml"
    base_url: "https://api.example.com"
    timeout: 60
    auth: {type: "bearer", token: "secret"}

# 新代码
let api = Resource("api.yml",
    base_url = "https://api.example.com",
    timeout = 60,
    auth = {type: "bearer", token: "secret"}
)
```

### 迁移检查清单

- [ ] **搜索旧语法**：在代码库中搜索 `resource ` 关键字
- [ ] **更新声明**：将 `resource X from Y` 改为 `let X = Resource(Y)`
- [ ] **更新配置块**：将配置块语法改为命名参数语法
- [ ] **测试验证**：运行测试确保 API 调用正常工作
- [ ] **更新文档**：更新项目文档和示例代码

### 自动化迁移工具（可选）

如果有大量代码需要迁移，可以使用以下正则表达式辅助：

```regex
# 查找简单形式
resource\s+(\w+)\s+from\s+"([^"]+)"

# 替换为
let $1 = Resource("$2")
```

---

## 🧪 测试覆盖

### 新增测试

- ✅ **17 个专项单元测试**（`test_resource_constructor.py`）
  - 基本功能测试：3 个
  - 参数测试：4 个
  - 验证测试：4 个
  - 错误处理测试：2 个
  - 动态使用测试：3 个
  - 兼容性测试：1 个（已删除）

### 回归测试

- ✅ **1099 个测试全部通过**
- ✅ **0 个失败**
- ✅ **10 个跳过**（正常）

### 测试文件

```
tests/
├── unit/dsl/
│   └── test_resource_constructor.py         (新增, 402 行)
├── test_resource_constructor.flow            (新增, 27 行)
└── test_resource_constructor_simple_api.yml  (新增, 55 行)
```

---

## 📊 代码统计

### 新增代码

| 文件 | 行数 | 说明 |
|------|------|------|
| `builtin_functions.py` | +110 | Resource() 函数实现 |
| `expression_evaluator.py` | +20 | Context 自动注入 |
| `lexer.py` | +10 | 大写标识符支持 |
| `test_resource_constructor.py` | +424 | 单元测试 |
| `test_resource_constructor.flow` | +27 | 集成测试 |
| `test_resource_constructor_simple_api.yml` | +55 | 测试数据 |
| **总计** | **+646** | |

### 删除代码

| 文件 | 行数 | 说明 |
|------|------|------|
| `interpreter.py` | -133 | _execute_resource() 方法 |
| `parser.py` | -134 | _parse_resource() 方法 |
| `ast_nodes.py` | -44 | ResourceStatement 类 |
| `lexer.py` | -6 | RESOURCE token |
| `test_resource_constructor.py` | -23 | 兼容性测试 |
| **总计** | **-340** | |

### 文档更新

| 文件 | 变更 | 说明 |
|------|------|------|
| `CHANGELOG.md` | +12 -5 | 添加 v6.0 变更记录 |
| `grammar/CHANGELOG.md` | +73 -6 | 详细语法文档 |
| `README.md` | +1 -1 | 更新示例 |
| `example-resource-basic.flow` | +3 -3 | 更新示例代码 |
| **总计** | **+89 -15** | |

**净增加**: +395 行（代码 + 测试 + 文档）

---

## 🔗 相关资源

### 文档

- [CHANGELOG.md](./CHANGELOG.md) - 完整变更日志
- [grammar/CHANGELOG.md](./grammar/CHANGELOG.md) - 语法变更详情
- [Grammar Proposal #010](./grammar/proposals/010-resource-constructor.md) - 提案文档

### 提交历史

```
8d39e4b docs: update documentation for v6.0 Resource() constructor
dc62c1f refactor(dsl): remove deprecated resource statement
3e1cdd7 feat(dsl): implement Resource() constructor function
c751a93 Merge proposal #010: Approve Resource Constructor Refactoring
```

### 示例代码

- [example-resource-basic.flow](./examples/api_integration/example-resource-basic.flow) - 基本用法示例
- [test_resource_constructor.flow](./tests/test_resource_constructor.flow) - 测试示例

---

## 🐛 已知问题

无已知问题。

---

## ⬆️ 升级步骤

### 1. 备份代码

```bash
git checkout -b backup-before-v6
git push origin backup-before-v6
```

### 2. 更新依赖

```bash
pip install --upgrade flowby
```

### 3. 迁移代码

使用上述迁移指南更新代码。

### 4. 运行测试

```bash
pytest tests/
```

### 5. 验证功能

运行关键流程确保一切正常。

---

## 💡 最佳实践

### 推荐的 Resource() 用法

#### 1. **基础 API 集成**

```dsl
# 简洁明了
let github_api = Resource("specs/github.yml")
let repos = github_api.listRepos(org="flowby")
```

#### 2. **环境配置**

```dsl
# 使用环境变量
let api = Resource("spec.yml",
    base_url = env.API_BASE_URL,
    auth = {type: "bearer", token: env.API_TOKEN}
)
```

#### 3. **动态认证**

```dsl
# 先登录，再创建 API 客户端
step "OAuth 认证流程":
    let oauth_response = http.post(
        "https://oauth.example.com/token",
        body = {
            grant_type: "client_credentials",
            client_id: env.CLIENT_ID,
            client_secret: env.CLIENT_SECRET
        }
    )

    let api = Resource("spec.yml",
        auth = {
            type: "bearer",
            token: oauth_response.access_token
        }
    )
```

#### 4. **错误处理**

```dsl
# 带重试机制
let api = Resource("spec.yml",
    base_url = "https://api.example.com",
    timeout = 30,
    resilience = {
        retry: {
            max_retries: 3,
            strategy: "exponential",
            backoff_base: 2
        }
    }
)
```

---

## 🙏 致谢

感谢所有参与 Grammar Proposal #010 讨论和实现的贡献者！

---

## 📞 支持

如有问题或需要帮助：

- **问题反馈**: [GitHub Issues](https://github.com/your-org/flowby/issues)
- **文档**: [完整文档](https://flowby.dev/docs)
- **社区**: [讨论区](https://github.com/your-org/flowby/discussions)

---

**Flowby Team**
2025-11-30
