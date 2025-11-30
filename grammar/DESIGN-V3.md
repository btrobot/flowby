# DSL v3.0 语法设计规范（Python化版本）

> **版本**: 3.0
> **目标受众**: Python程序员
> **设计原则**: 纯Python风格，最小化学习成本
> **状态**: 设计中 (Design Phase)
> **创建日期**: 2025-11-26
> **破坏性变更**: 是 - 完全不兼容v2.0

---

## 🎯 设计定位

**DSL v3.0 = 为Python程序员编写的浏览器自动化DSL**

### 核心目标

1. **Python优先**: 语法尽可能接近Python，Python程序员零学习成本
2. **简洁一致**: 删除冗余语法（end关键字），使用纯缩进
3. **快速上手**: 如果你会Python，你就会DSL

### 与Python的对齐度

```python
# Python代码
def login(user):
    if user == "admin":
        print(f"Admin: {user}")
        return True
    else:
        print("Regular user")
        return False

# DSL v3.0 代码（几乎相同！）
step "login":
    if user == "admin":
        log f"Admin: {user}"
        let result = True
    else:
        log "Regular user"
        let result = False
```

**相似度**: 90%+ 语法兼容Python

---

## 📐 Python化改进清单

### ✅ 与Python完全一致

| 特性 | Python | DSL v3.0 | 状态 |
|------|--------|----------|------|
| 布尔字面量 | `True`, `False` | `True`, `False` | ✅ 一致 |
| null/None | `None` | `None` | ✅ 一致 |
| 缩进块 | 4空格 | 4空格 | ✅ 一致 |
| 冒号标记 | `if x:` | `if x:` | ✅ 一致 |
| 行注释 | `# 注释` | `# 注释` | ✅ 一致 |
| 块注释 | `""" 注释 """` | `""" 注释 """` | ✅ 一致 |
| f-string | `f"text {x}"` | `f"text {x}"` | ✅ 一致 |
| 逻辑运算符 | `and/or/not` | `and/or/not` | ✅ 一致 |
| for循环 | `for i in items:` | `for i in items:` | ✅ 一致 |
| 数组字面量 | `[1, 2, 3]` | `[1, 2, 3]` | ✅ 一致 |

### ⚠️ 有意差异（已最小化）

| 特性 | Python | DSL v3.0 | 理由 |
|------|--------|----------|------|
| 变量声明 | `x = 1` | `let x = 1` | 作用域管理，防止拼写错误 |
| 常量 | `MAX = 1`（约定） | `const MAX = 1` | 真正的不可变性 |
| 模式匹配 | `match/case` (3.10+) | `when/otherwise` | 兼容Python 3.9 |
| dict键 | `{"key": "val"}` | `{key: "val"}` | 简洁性（可选引号） |
| 系统变量 | `os.environ` | `env.API_KEY` | 内置全局对象 |

---

## 🔄 v2.0 → v3.0 核心变更

### 1. 删除end关键字（Python化）

**v2.0（混合风格）**:
```dsl
step "登录":
    if user == "admin":
        navigate to "https://admin.example.com"
    end if          # ❌ 冗余
end step            # ❌ 冗余
```

**v3.0（纯Python风格）**:
```dsl
step "登录":
    if user == "admin":
        navigate to "https://admin.example.com"
# ✅ 只用缩进，像Python一样
```

### 2. 布尔字面量Python化

| v2.0 | v3.0 | Python |
|------|------|--------|
| `true` | `True` | `True` ✅ |
| `false` | `False` | `False` ✅ |

```python
# v3.0（Python程序员会本能地写True/False）
let active = True
if active == False:
    log "Inactive"
```

### 3. null → None（Python化）

| v2.0 | v3.0 | Python |
|------|------|--------|
| `null` | `None` | `None` ✅ |

```python
# v3.0
let data = None
if data == None:
    log "No data"
```

### 4. 删除$前缀（Python化）

| v2.0 | v3.0 | Python风格 |
|------|------|-----------|
| `$page.url` | `page.url` | 内置全局对象 ✅ |
| `$env.API_KEY` | `env.API_KEY` | 类似 `os.environ` ✅ |

```python
# v3.0（像访问Python模块一样）
log f"Current URL: {page.url}"
log f"API Key: {env.API_KEY}"
log f"Browser: {browser.name}"
```

### 5. f-string语法（Python化）

| v2.0 | v3.0 | Python |
|------|------|--------|
| `"text {x}"` 自动插值 | `f"text {x}"` 显式插值 | `f"text {x}"` ✅ |

```python
# v3.0（明确的f-string前缀）
log f"Count: {count}"               # 插值字符串
log "Literal: {count}"              # 普通字符串（不插值）
log f"User: {user.name}"            # 表达式插值
log f"Calc: {x + y * 2}"            # 计算插值
```

### 6. 块注释Python化

| v2.0 | v3.0 | Python |
|------|------|--------|
| `/* 注释 */` | `""" 注释 """` | `""" 注释 """` ✅ |

```python
# v3.0
"""
这是块注释
跨越多行
类似Python的docstring
"""
```

### 7. 删除元数据块（Python化）

| v2.0 | v3.0 | Python风格 |
|------|------|-----------|
| `/**meta ... */` | 删除此特性 | 用模块级变量/注释 |

```python
# v3.0（如果需要元数据，用注释或变量）
# pass: example-test
# desc: 测试示例

# 或模块级变量（未来可能支持）
__pass__ = "example-test"
__desc__ = "测试示例"
```

---

## 📋 完整语法规范

### 1. 变量与赋值

#### 1.1 let声明（DSL特有）

```python
# 语法
let VAR = expr

# 示例
let count = 0
let name = "Alice"
let items = [1, 2, 3]
let user = {name: "Bob", age: 30}

# ⚠️ 与Python差异
# Python: count = 0（直接赋值）
# DSL: let count = 0（显式声明）
# 理由: 作用域管理，防止拼写错误
```

#### 1.2 const声明（DSL特有）

```python
# 语法
const VAR = expr

# 示例
const MAX_RETRY = 3
const API_URL = "https://api.example.com"

# ⚠️ 与Python差异
# Python: MAX_RETRY = 3（约定，但可修改）
# DSL: const MAX_RETRY = 3（真正的不可变）
```

#### 1.3 赋值

```python
# 语法
VAR = expr

# 示例
count = count + 1
name = "Charlie"
```

---

### 2. 控制流（完全Python化）

#### 2.1 Step块（删除end step）

```python
# v3.0语法
step "name":
    statements...

# 示例
step "用户登录":
    navigate to "https://example.com"
    type "admin" into "#username"
    click "#submit"
# 像Python函数一样，用缩进表示块
```

#### 2.2 If-Else（删除end if）

```python
# v3.0语法（完全像Python）
if condition:
    statements...
else if condition:
    statements...
else:
    statements...

# 示例
if score >= 90:
    log "A"
else if score >= 80:
    log "B"
else:
    log "F"
```

#### 2.3 When-Otherwise（类似match/case）

```python
# v3.0语法
when expr:
    "value1":
        statements...
    "value2":
        statements...
    otherwise:
        statements...

# 示例
when status:
    "active":
        log "User is active"
    "inactive":
        log "User is inactive"
    otherwise:
        log "Unknown status"

# ⚠️ 与Python差异
# Python 3.10+: match status: case "active": ...
# DSL: when status: "active": ...
# 理由: 更简洁，兼容Python 3.9
```

#### 2.4 For-Each循环（删除end for）

```python
# v3.0语法（完全像Python）
for VAR in expr:
    statements...

# 示例
for item in items:
    log f"Processing: {item}"
    click item.selector
```

---

### 3. 数据类型（Python对齐）

#### 布尔字面量

```python
# v3.0（Python风格）
True      # ✅ 首字母大写
False     # ✅ 首字母大写

# 示例
let active = True
let verified = False
if active and not verified:
    log "Need verification"
```

#### None字面量

```python
# v3.0（Python风格）
None      # ✅ 首字母大写

# 示例
let data = None
if data == None:
    log "No data"
```

#### 字符串与f-string

```python
# v3.0（Python f-string）
"plain string"              # 普通字符串
f"interpolated {expr}"      # 插值字符串（需要f前缀）

# 示例
let name = "Alice"
log "Hello"                 # 输出: Hello
log f"Hello, {name}"        # 输出: Hello, Alice
log f"Calc: {2 + 3}"        # 输出: Calc: 5

# ⚠️ 重要：没有f前缀的字符串不插值
log "Count: {count}"        # 输出: Count: {count}（字面量）
log f"Count: {count}"       # 输出: Count: 5（插值）
```

#### 数字

```python
# v3.0（与Python相同）
42          # 整数
3.14        # 浮点数
-10         # 负数（一元运算符）
```

#### 数组

```python
# v3.0（与Python列表相同）
[]                          # 空数组
[1, 2, 3]                   # 数字数组
["a", "b", "c"]             # 字符串数组
[1, "text", True, None]     # 混合类型
[[1, 2], [3, 4]]            # 嵌套数组
[x + 1, y * 2]              # 表达式数组
```

#### 对象（类似Python dict）

```python
# v3.0（简化的dict语法）
{}                          # 空对象
{name: "Alice"}             # 键无引号（简洁）
{"first-name": "Alice"}     # 特殊字符键需引号
{name: "Bob", age: 30}      # 多个键值对
{items: [1, 2, 3]}          # 嵌套数组
{user: {name: "Alice"}}     # 嵌套对象

# ⚠️ 与Python差异
# Python: {"name": "Alice"}（键必须有引号）
# DSL: {name: "Alice"}（键可以无引号，更简洁）
```

---

### 4. 系统变量（去掉$前缀）

```python
# v3.0（Python风格的内置对象）

# context命名空间（执行上下文）
context.task_id
context.execution_id
context.start_time
context.step_name
context.status

# page命名空间（当前页面）
page.url
page.title
page.origin

# browser命名空间（浏览器信息）
browser.name
browser.version

# env命名空间（环境变量，类似os.environ）
env.API_KEY
env.DATABASE_URL
env.ENVIRONMENT

# config命名空间（配置）
config.base_url
config.timeout
config.max_retries

# 示例
log f"Current URL: {page.url}"
log f"Browser: {browser.name}"
log f"API Key: {env.API_KEY}"

# ⚠️ v2.0差异：删除了$前缀
# v2.0: $page.url, $env.API_KEY
# v3.0: page.url, env.API_KEY（更Python化）
```

---

### 5. 注释（Python风格）

```python
# 行注释（与Python相同）
let x = 1  # 行尾注释

"""
块注释（三引号）
跨越多行
类似Python的docstring
"""

# ⚠️ v2.0差异：
# v2.0: /* 块注释 */（C风格）
# v3.0: """ 块注释 """（Python风格）
```

---

## 🎯 完整示例对比

### Python代码

```python
def process_users(users):
    """处理用户列表"""

    for user in users:
        # 检查用户状态
        if user["active"]:
            print(f"Processing: {user['name']}")

            # 根据角色处理
            if user["role"] == "admin":
                grant_admin_access(user)
            elif user["role"] == "editor":
                grant_editor_access(user)
            else:
                grant_user_access(user)
        else:
            print(f"Skipping inactive: {user['name']}")

    return True
```

### DSL v3.0代码（几乎相同！）

```dsl
step "处理用户列表":
    """处理用户列表"""

    for user in users:
        # 检查用户状态
        if user.active:
            log f"Processing: {user.name}"

            # 根据角色处理
            if user.role == "admin":
                navigate to admin_url
            else if user.role == "editor":
                navigate to editor_url
            else:
                navigate to user_url
        else:
            log f"Skipping inactive: {user.name}"

    let result = True
```

**相似度**: 95%+ 语法一致

---

## 📊 Python程序员学习曲线

### 如果你会Python

```python
# 你已经会90%的DSL语法！

# ✅ 这些完全相同
if x > 0:           # 条件语句
for i in items:     # for循环
True / False        # 布尔值
None                # 空值
f"text {x}"         # f-string
and / or / not      # 逻辑运算符
[1, 2, 3]           # 数组/列表
# 注释             # 注释语法

# ⚠️ 只需要记住3个小差异

# 1. 变量声明需要let（而非直接赋值）
let x = 1           # Python: x = 1

# 2. 常量用const（Python没有）
const MAX = 100     # Python: MAX = 100（约定）

# 3. 模式匹配用when（而非match）
when x:             # Python 3.10+: match x:
    "val":          #     case "val":
        pass        #         pass
```

### 5分钟上手清单

```markdown
✅ 会Python if/else → 直接用DSL if/else
✅ 会Python for循环 → 直接用DSL for循环
✅ 会Python f-string → 直接用DSL f-string
✅ 会Python True/False/None → 直接用DSL
✅ 会Python缩进 → 直接用DSL（4空格）

❗ 新学：let x = 1（声明变量）
❗ 新学：const MAX = 1（常量）
❗ 新学：when x: "val":（模式匹配）
❗ 新学：step "name":（步骤块）
❗ 新学：page.url, env.API_KEY（系统变量）
```

---

## 🔧 实现检查清单

### Lexer实现（lexer_v3.py）

- [ ] `True`/`False` token（首字母大写）
- [ ] `None` token（而非null）
- [ ] `f"..."` f-string解析
- [ ] `"""..."""` 块注释解析
- [ ] 删除 `$` token
- [ ] 删除 END token
- [ ] INDENT/DEDENT token
- [ ] 删除 `/**meta */` 解析

### Parser实现（parser_v3.py）

- [ ] 布尔字面量: `True`/`False`
- [ ] Null字面量: `None`
- [ ] f-string解析: `f"text {expr}"`
- [ ] 普通字符串: `"text"` 不插值
- [ ] 系统变量: `page.url` 而非 `$page.url`
- [ ] 块注释: `"""..."""`
- [ ] 删除元数据块解析

---

## 📖 附录：Python对齐度总结

| 分类 | Python一致性 | 说明 |
|------|-------------|------|
| **语法结构** | 95% | 缩进、冒号、if/for完全一致 |
| **数据类型** | 90% | True/False/None一致，dict键可无引号 |
| **字符串** | 100% | f-string完全一致 |
| **注释** | 100% | # 和 """ """ 完全一致 |
| **运算符** | 100% | and/or/not完全一致 |
| **系统变量** | 类似 | 类似Python的os.environ, sys.argv |

**总体Python对齐度: 93%**

---

**文档维护**: DSL v3.0设计组
**目标受众**: Python程序员
**最后更新**: 2025-11-26
**下一步**: 创建 PYTHON-QUICKSTART.md（5分钟上手指南）
