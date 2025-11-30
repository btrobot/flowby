# v3.1 迁移指南

## 📋 概述

本指南帮助你从 v3.0 的 `call` 语法迁移到 v3.1 的 Python-style 服务调用语法。

**版本信息**:
- **v3.0**: 旧语法（`call "service.method"`）
- **v3.1**: 新语法（`service.method()`）+ 旧语法兼容（带废弃警告）
- **v4.0**: 仅新语法（旧语法移除）

**迁移策略**: v3.1 提供至少一个版本的兼容期，推荐在 v4.0 发布前完成迁移。

---

## 🎯 为什么要迁移？

### 旧语法的问题

```dsl
# ❌ v3.0 旧语法
call "random.email" into email
call "http.get" with url: "https://api.example.com" into response
```

**问题**:
1. ❌ 与内置函数语法不一致（`Math.round()` vs `call "random.email"`）
2. ❌ 冗余关键字（`call` + `into`）
3. ❌ 不能在表达式中使用
4. ❌ 违背 v3.0 Python-style 设计理念

### 新语法的优势

```dsl
# ✅ v3.1 新语法
let email = random.email()
let response = http.get(url: "https://api.example.com")
```

**优势**:
1. ✅ 完全 Python 化，与内置函数一致
2. ✅ 语法简洁，无冗余关键字
3. ✅ 可在任何表达式中使用
4. ✅ 降低学习成本

---

## 📊 迁移对照表

### 基本调用

| v3.0 旧语法 (🗑️) | v3.1 新语法 (✅) |
|------------------|------------------|
| `call "random.email" into email` | `let email = random.email()` |
| `call "random.password" into pwd` | `let pwd = random.password()` |
| `call "random.uuid" into id` | `let id = random.uuid()` |

### 带参数调用

| v3.0 旧语法 (🗑️) | v3.1 新语法 (✅) |
|------------------|------------------|
| `call "random.password" with length=16 into pwd` | `let pwd = random.password(length: 16)` |
| `call "random.password" with length=16, special=True into pwd` | `let pwd = random.password(length: 16, special: True)` |
| `call "random.number" with 1, 100 into dice` | `let dice = random.number(1, 100)` |
| `call "random.phone" with locale="zh_CN" into phone` | `let phone = random.phone(locale: "zh_CN")` |

### HTTP 请求

| v3.0 旧语法 (🗑️) | v3.1 新语法 (✅) |
|------------------|------------------|
| `call "http.get" with url="..." into response` | `let response = http.get(url: "...")` |
| `call "http.post" with url="...", body={name: "Alice"} into result` | `let result = http.post(url: "...", body: {name: "Alice"})` |
| `call "http.get" with url="...", timeout=5000, headers={...} into data` | `let data = http.get(url: "...", timeout: 5000, headers: {...})` |

---

## 🔧 迁移步骤

### Step 1: 查找所有 call 语句

```bash
# Linux/Mac
grep -r 'call "' your_project/

# Windows PowerShell
Select-String -Path your_project\*.flow -Pattern 'call "'

# 或使用 IDE 全局搜索
```

### Step 2: 逐个替换

#### 替换规则

1. **移除 `call` 关键字和引号**
   ```dsl
   # Before
   call "random.email" into email

   # After
   random.email() into email  # 中间步骤
   ```

2. **将 `with param=value` 改为 `(param: value)`**
   ```dsl
   # Before
   call "random.password" with length=16, special=True into pwd

   # After
   random.password(length: 16, special: True) into pwd  # 中间步骤
   ```

3. **将 `into var` 改为 `let var = ...`**
   ```dsl
   # Before
   random.password(length: 16, special: True) into pwd

   # After
   let pwd = random.password(length: 16, special: True)  # 完成
   ```

### Step 3: 测试

运行测试套件确保行为一致：

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/dsl/test_service_namespaces.py -v
```

### Step 4: 提交

```bash
git add .
git commit -m "refactor: migrate from call syntax to Python-style service calls (v3.1)"
git push
```

---

## 📝 完整迁移示例

### Before (v3.0)

```dsl
step "User Registration":
    # 生成测试数据
    call "random.email" into email
    call "random.password" with length=16, special=True into password
    call "random.uuid" into user_id

    # 填写表单
    type email into "#email"
    type password into "#password"
    click "#register"

    # 调用 API
    call "http.get" with url="https://api.example.com/users" into users
    call "http.post" with url="https://api.example.com/users", body={name: "Alice", email: email} into created

    # 验证
    assert created.status == "success"
```

### After (v3.1)

```dsl
step "User Registration":
    # 生成测试数据
    let email = random.email()
    let password = random.password(length: 16, special: True)
    let user_id = random.uuid()

    # 填写表单
    type email into "#email"
    type password into "#password"
    click "#register"

    # 调用 API
    let users = http.get(url: "https://api.example.com/users")
    let created = http.post(url: "https://api.example.com/users", body: {name: "Alice", email: email})

    # 验证
    assert created.status == "success"
```

---

## 🎁 新增能力

v3.1 新语法支持旧语法无法实现的功能：

### 1. 在数组中使用

```dsl
# ❌ v3.0: 不支持
call "random.email" into email1
call "random.email" into email2
let emails = [email1, email2]

# ✅ v3.1: 直接使用
let emails = [random.email(), random.email()]
```

### 2. 在对象字面量中使用

```dsl
# ❌ v3.0: 不支持
call "random.uuid" into id
call "random.email" into email
let user = {id: id, email: email}

# ✅ v3.1: 直接使用
let user = {
    id: random.uuid(),
    email: random.email(),
    created_at: Date.now()
}
```

### 3. 在字符串插值中使用

```dsl
# ❌ v3.0: 不支持
call "random.email" into email
log f"Generated: {email}"

# ✅ v3.1: 直接使用
log f"Generated email: {random.email()}"
log f"User ID: {random.uuid()}"
```

### 4. 嵌套调用

```dsl
# ❌ v3.0: 不支持
call "random.email" into email
# 无法将 email 转大写后再用

# ✅ v3.1: Python-style 方法调用
let email = random.email()
let uppercase_email = email.upper()
```

### 5. 条件表达式中使用

```dsl
# ❌ v3.0: 不支持
call "random.number" with 1, 10 into score
if score > 5:
    log "High score"

# ✅ v3.1: 直接使用
if random.number(1, 10) > 5:
    log "High score"
```

---

## 📚 服务命名空间 API

### random 命名空间

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
let email = random.email()                           # test123@example.com
let pwd = random.password(length: 16, special: True) # A3$fG9&kL2@mN5!p
let username = random.username()                     # user_alice
let phone = random.phone(locale: "zh_CN")           # 138-1234-5678
let dice = random.number(1, 6)                       # 1-6 之间
let id = random.uuid()                               # 550e8400-e29b-41d4-a716...
```

### http 命名空间

| 方法 | 参数 | 返回值 | 说明 |
|------|------|-------|------|
| `get(url, timeout=30, headers=None)` | url: String, timeout: Int, headers: Object | Any | HTTP GET 请求 |
| `post(url, body=None, timeout=30, headers=None)` | url: String, body: Any, ... | Any | HTTP POST 请求 |
| `put(url, body=None, timeout=30, headers=None)` | url: String, body: Any, ... | Any | HTTP PUT 请求 |
| `delete(url, timeout=30, headers=None)` | url: String, timeout: Int, ... | Any | HTTP DELETE 请求 |
| `patch(url, body=None, timeout=30, headers=None)` | url: String, body: Any, ... | Any | HTTP PATCH 请求 |

**示例**:
```dsl
# GET 请求
let users = http.get(url: "https://api.example.com/users")
let data = http.get(
    url: "https://api.example.com/data",
    timeout: 5,
    headers: {Authorization: "Bearer token123"}
)

# POST 请求
let created = http.post(
    url: "https://api.example.com/users",
    body: {name: "Alice", email: "alice@example.com"}
)

# PUT 请求
let updated = http.put(
    url: "https://api.example.com/users/123",
    body: {status: "active"}
)

# DELETE 请求
let deleted = http.delete(url: "https://api.example.com/users/123")

# PATCH 请求
let patched = http.patch(
    url: "https://api.example.com/users/123",
    body: {email: "newemail@example.com"}
)
```

---

## ⚠️ 常见问题

### Q1: 旧语法还能用吗？

**A**: 可以，但会显示废弃警告。

```dsl
call "random.email" into email

# 输出:
# [DEPRECATED] Line 1: 'call' 语句已在 v3.1 废弃，将在 v4.0 移除
#   当前: call "random.email" ...
#   建议: let email = random.email()
#   详见迁移指南: grammar/MIGRATION-GUIDE-v3.1.md
```

### Q2: 什么时候必须迁移？

**A**: v4.0 发布前必须完成迁移（预计 2026 年）。

- **v3.1** (2025-12): 新旧语法共存，建议迁移
- **v4.0** (2026-XX): 旧语法移除，必须迁移

### Q3: 我可以混用新旧语法吗？

**A**: 可以，v3.1 支持混用，但不推荐。

```dsl
# ✅ 可以混用（不推荐）
let email = random.email()          # 新语法
call "random.password" into pwd     # 旧语法

# ✅ 推荐：统一使用新语法
let email = random.email()
let pwd = random.password()
```

### Q4: 如何批量迁移？

**A**: 使用正则表达式替换（谨慎使用，建议逐个检查）：

```regex
# 查找模式（示例）
call "(\w+)\.(\w+)" into (\w+)

# 替换为
let $3 = $1.$2()
```

**注意**: 带参数的调用较复杂，建议手动迁移。

### Q5: 迁移后性能有变化吗？

**A**: 无影响，解析和执行性能相同。

### Q6: random, http 可以作为变量名吗？

**A**: 不可以，它们是保留字。

```dsl
# ❌ 错误
let random = 10  # RuntimeError: 不能定义变量 'random'：这是保留的命名空间

# ✅ 正确
let random_value = 10
```

保留的命名空间: `Math`, `Date`, `JSON`, `UUID`, `Hash`, `Base64`, `random`, `http`, `page`, `context`, `browser`, `env`, `config`

---

## 🔄 自动化迁移工具（可选）

如果你有大量脚本需要迁移，可以创建自动化脚本：

```python
#!/usr/bin/env python3
"""
自动迁移 call 语法到 Python-style 调用

用法: python migrate_call_syntax.py <file_or_directory>
"""

import re
import sys
from pathlib import Path


def migrate_call_syntax(content: str) -> str:
    """迁移 call 语法"""

    # Pattern 1: call "service.method" into var
    pattern1 = r'call\s+"(\w+)\.(\w+)"\s+into\s+(\w+)'
    replacement1 = r'let \3 = \1.\2()'
    content = re.sub(pattern1, replacement1, content)

    # Pattern 2: call "service.method" with param=value into var (简化版)
    # 注意：复杂参数需要手动处理
    pattern2 = r'call\s+"(\w+)\.(\w+)"\s+with\s+([^i]+?)\s+into\s+(\w+)'
    def replace_with_params(match):
        service = match.group(1)
        method = match.group(2)
        params = match.group(3).strip()
        var = match.group(4)
        # 简单替换 = 为 :
        params = params.replace('=', ': ')
        return f'let {var} = {service}.{method}({params})'

    content = re.sub(pattern2, replace_with_params, content)

    return content


def main():
    if len(sys.argv) < 2:
        print("用法: python migrate_call_syntax.py <file_or_directory>")
        sys.exit(1)

    path = Path(sys.argv[1])

    if path.is_file():
        files = [path]
    elif path.is_dir():
        files = list(path.rglob("*.flow"))
    else:
        print(f"错误: {path} 不存在")
        sys.exit(1)

    for file_path in files:
        print(f"处理: {file_path}")
        content = file_path.read_text(encoding='utf-8')
        migrated = migrate_call_syntax(content)

        if content != migrated:
            file_path.write_text(migrated, encoding='utf-8')
            print(f"  ✓ 已迁移")
        else:
            print(f"  - 无需更改")


if __name__ == '__main__':
    main()
```

**使用方法**:
```bash
# 迁移单个文件
python scripts/migrate_call_syntax.py examples/flows/test.flow

# 迁移整个目录
python scripts/migrate_call_syntax.py examples/flows/

# 建议先备份
cp -r examples/flows examples/flows.backup
```

**注意**: 自动化工具可能无法处理所有复杂情况，建议人工审查迁移结果。

---

## 📞 获取帮助

如果遇到迁移问题，请：

1. **查看文档**: `grammar/MASTER.md` - 完整语法参考
2. **查看示例**: `examples/flows/` - 迁移后的示例脚本
3. **运行测试**: `pytest tests/dsl/test_service_namespaces.py -v`
4. **提交 Issue**: [GitHub Issues](https://github.com/your-repo/issues)

---

## 📈 迁移进度跟踪

创建迁移清单跟踪进度：

```markdown
## 迁移清单

- [ ] examples/flows/user_registration.flow
- [ ] examples/flows/api_testing.flow
- [ ] tests/integration/test_*.flow
- [ ] ...

## 迁移统计

- 总文件数: XX
- 已迁移: XX
- 待迁移: XX
- 完成度: XX%
```

---

**最后更新**: 2025-11-27
**适用版本**: v3.1+
**移除旧语法版本**: v4.0 (预计 2026 年)
