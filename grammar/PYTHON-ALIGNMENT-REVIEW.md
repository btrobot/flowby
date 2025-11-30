# DSL v3.0 Python对齐度审查报告

> **目标受众**: Python程序员
> **核心原则**: 最小化心智负担，快速上手
> **审查日期**: 2025-11-26

---

## 🎯 设计定位

**DSL v3.0 = 为Python程序员编写的浏览器自动化DSL**

**目标**:
- Python程序员看到DSL代码，应该感觉像在写Python
- 学习曲线接近零：如果你会Python，你就会DSL
- 语法差异必须有充分理由，且在文档中明确说明

---

## ⚠️ 当前问题：与Python不一致的地方

### 1️⃣ 布尔字面量 ⭐⭐⭐⭐⭐ 必须改

| 当前 v3.0 | Python | 冲突 | 建议 |
|----------|--------|------|------|
| `true`, `false` | `True`, `False` | ❌ 严重 | 改为 `True`, `False` |

**问题**:
```dsl
# 当前v3.0（JavaScript风格）
let active = true
if active == false:
    log "Not active"

# Python程序员会本能写成
let active = True
if active == False:
    log "Not active"
```

**影响**: 所有条件表达式，Python程序员会不断报错

**修订**: ✅ 改为 `True`, `False`（首字母大写）

---

### 2️⃣ null字面量 ⭐⭐⭐⭐⭐ 必须改

| 当前 v3.0 | Python | 冲突 | 建议 |
|----------|--------|------|------|
| `null` | `None` | ❌ 严重 | 改为 `None` |

**问题**:
```dsl
# 当前v3.0（JavaScript风格）
let data = null
if data == null:
    log "No data"

# Python程序员会本能写成
let data = None
if data is None:
    log "No data"
```

**影响**: 所有空值处理

**修订**: ✅ 改为 `None`

**附加问题**: Python用 `is None` 而非 `== None`，是否支持 `is` 运算符？
- 建议：暂不支持 `is`，文档说明用 `== None`

---

### 3️⃣ 系统变量 `$` 前缀 ⭐⭐⭐⭐ 强烈建议改

| 当前 v3.0 | Python风格 | 冲突 | 建议 |
|----------|-----------|------|------|
| `$page.url` | `page.url` | ⚠️ Shell风格 | 去掉 `$` 前缀 |
| `$env.API_KEY` | `env.API_KEY` | ⚠️ Shell风格 | 去掉 `$` 前缀 |

**问题**:
- `$` 前缀来自Shell/PHP，Python没有这个习惯
- Python使用特殊命名约定（如 `__name__`, `__file__`）

**方案A - 去掉$前缀（推荐）**:
```python
# v3.0改进版（更Python化）
log page.url
log browser.name
log env.API_KEY
log config.base_url

# 实现：作为内置全局对象
# 类似Python的 os.environ, sys.argv
```

**方案B - 双下划线前缀**:
```python
# 更接近Python特殊变量
log __page__.url
log __browser__.name
```

**方案C - 保持 `$` 前缀**（不推荐）:
- 理由：明确标识系统变量
- 缺点：不够Python化

**修订**: ✅ 去掉 `$` 前缀，作为内置全局对象

---

### 4️⃣ 字符串插值语法 ⭐⭐⭐ 建议改

| 当前 v3.0 | Python | 冲突 | 建议 |
|----------|--------|------|------|
| `"text {expr}"` | `f"text {expr}"` | ⚠️ 自动插值 | 引入 f-string |

**问题**:
```dsl
# 当前v3.0（自动插值）
log "Count: {count}"        # 自动插值
log "Literal: {count}"      # 无法输出字面量 {count}

# Python程序员期望
log f"Count: {count}"       # 明确插值
log "Literal: {count}"      # 字面量字符串
```

**冲突分析**:
- 当前：所有 `"..."` 字符串都支持插值（隐式）
- Python：需要 `f"..."` 前缀才插值（显式）

**方案A - 引入f-string前缀（推荐）**:
```python
# v3.0改进版
log f"Count: {count}"           # 插值字符串
log "Literal: {count}"          # 普通字符串
log f"User: {user.name}"        # 表达式插值
```

**方案B - 保持当前自动插值**（不推荐）:
- 理由：语法简洁
- 缺点：与Python不一致，无法输出字面量 `{}`

**修订**: ✅ 引入 f-string 语法，`f"..."` 支持插值，`"..."` 为普通字符串

---

### 5️⃣ 块注释语法 ⭐⭐ 建议改

| 当前 v3.0 | Python | 冲突 | 建议 |
|----------|--------|------|------|
| `/* ... */` | `""" ... """` | ⚠️ C风格 | 改为三引号 |

**问题**:
```dsl
# 当前v3.0（C/JavaScript风格）
/*
这是块注释
跨越多行
*/

# Python程序员期望
"""
这是文档字符串
跨越多行
"""
```

**修订**: ✅ 改为 `""" ... """` 块注释

**注意**: Python的三引号通常用于docstring，需在文档中说明DSL用于注释

---

### 6️⃣ 元数据块 ⭐⭐⭐⭐⭐ 必须删除

| 当前 v3.0 | Python | 冲突 | 建议 |
|----------|--------|------|------|
| `/**meta ... */` | 无 | ❌ Java风格 | 删除此特性 |

**问题**:
- 类似JavaDoc，与Python文化不符
- Python使用装饰器 `@decorator` 或模块级变量

**修订**: ✅ **删除元数据块特性**

**替代方案**（如果需要元数据）:
```python
# Python风格：模块级变量
__pass__ = "example-test"
__desc__ = "测试示例"
__symbol__ = "TEST-001"

# 或使用注释
# pass: example-test
# desc: 测试示例
```

---

### 7️⃣ `let` 关键字 ⭐ 保留（有理由）

| 当前 v3.0 | Python | 冲突 | 建议 |
|----------|--------|------|------|
| `let count = 0` | `count = 0` | ⚠️ 显式声明 | 保留，文档说明 |

**Python视角**:
```python
# Python（动态类型）
count = 0      # 直接赋值即声明
```

**DSL保留 `let` 的理由**:
1. **明确变量作用域** - 防止拼写错误意外创建变量
2. **区分声明和赋值** - `let` 声明新变量，`=` 修改已有变量
3. **类型检查友好** - 编译器可以做更好的静态分析

**文档说明**:
```markdown
## 为什么DSL需要 `let`？

Python允许随时创建变量，但这会导致拼写错误难以发现：

```python
# Python
count = 0
# ... 100行代码后
cont = 1  # 拼写错误！创建了新变量，count没变
```

DSL要求显式声明，防止此类错误：

```dsl
let count = 0
# ... 100行代码后
cont = 1  # 错误：cont未声明
```
```

**修订**: ✅ 保留 `let`，在文档中说明理由

---

### 8️⃣ `const` 关键字 ⭐ 保留（有理由）

| 当前 v3.0 | Python | 冲突 | 建议 |
|----------|--------|------|------|
| `const MAX = 3` | `MAX = 3` | ⚠️ Python无const | 保留，文档说明 |

**Python视角**:
```python
# Python约定：大写变量名表示常量
MAX_RETRY = 3  # 约定，但可修改
```

**DSL保留 `const` 的理由**:
- 提供编译时不可变性保证（Python缺失的特性）
- 防止意外修改配置值

**文档说明**:
```markdown
## 为什么DSL有 `const`？

Python通过命名约定表示常量，但无法强制：

```python
# Python
MAX_RETRY = 3
MAX_RETRY = 5  # 允许，但违反约定
```

DSL提供编译时保护：

```dsl
const MAX_RETRY = 3
MAX_RETRY = 5  # 错误：不能修改常量
```
```

**修订**: ✅ 保留 `const`

---

### 9️⃣ `when/otherwise` vs `match/case` ⭐ 保留（兼容性）

| 当前 v3.0 | Python 3.10+ | 冲突 | 建议 |
|----------|-------------|------|------|
| `when VAR: "val": ...` | `match VAR: case "val": ...` | ⚠️ 关键字不同 | 保留 when |

**Python 3.10+ match语法**:
```python
match status:
    case "active":
        print("Active")
    case "inactive":
        print("Inactive")
    case _:
        print("Unknown")
```

**DSL v3.0 when语法**:
```dsl
when status:
    "active":
        log "Active"
    "inactive":
        log "Inactive"
    otherwise:
        log "Unknown"
```

**保留 `when` 的理由**:
1. Python 3.10+才有match，不是所有Python程序员都熟悉
2. `when` 语法更简洁（无需 `case` 关键字）
3. 向后兼容Python 3.9及以下

**文档说明**:
```markdown
## `when` vs Python的 `match`

DSL使用 `when` 而非 `match/case`：
- 更简洁（无需case关键字）
- 兼容Python 3.9及以下
- 功能等价于match语句
```

**修订**: ✅ 保留 `when`，文档说明

---

### 🔟 对象字面量语法 ⭐ 保留（简洁性）

| 当前 v3.0 | Python | 冲突 | 建议 |
|----------|--------|------|------|
| `{name: "Alice"}` | `{"name": "Alice"}` | ⚠️ 键无引号 | 保留，文档说明 |

**Python字典**:
```python
user = {"name": "Alice", "age": 30}  # 键必须是字符串
```

**DSL对象字面量**:
```dsl
let user = {name: "Alice", age: 30}  # 键可以无引号
```

**保留无引号键的理由**:
- 语法更简洁（类似JavaScript）
- 99%的情况键都是标识符

**支持引号键**:
```dsl
let data = {"first-name": "Alice"}  # 特殊字符需要引号
```

**文档说明**:
```markdown
## 对象字面量 vs Python字典

DSL对象类似Python字典，但键可以无引号：

```dsl
# DSL（简洁）
let user = {name: "Alice", age: 30}

# 等价于Python
user = {"name": "Alice", "age": 30}
```
```

**修订**: ✅ 保留无引号键，文档说明

---

## ✅ 修订方案总结

### 必须修改（高优先级）

| # | 问题 | 当前 | 修改为 | 理由 |
|---|------|------|--------|------|
| 1 | 布尔字面量 | `true`, `false` | `True`, `False` | Python标准 |
| 2 | null字面量 | `null` | `None` | Python标准 |
| 3 | 元数据块 | `/**meta ... */` | **删除** | 与Python文化不符 |
| 4 | 块注释 | `/* ... */` | `""" ... """` | Python标准 |
| 5 | 系统变量 | `$page.url` | `page.url` | 去掉Shell风格$ |
| 6 | 字符串插值 | `"text {x}"` | `f"text {x}"` | Python f-string |

### 保留但需文档说明（中优先级）

| # | 特性 | 理由 | 文档重点 |
|---|------|------|----------|
| 7 | `let` 关键字 | 作用域管理，防止拼写错误 | 说明与Python差异 |
| 8 | `const` 关键字 | 不可变性保证 | Python缺失的特性 |
| 9 | `when/otherwise` | 兼容Python 3.9 | 对比match/case |
| 10 | 对象无引号键 | 语法简洁 | 对比Python dict |

---

## 📖 Python程序员快速上手指南（文档框架）

### 核心理念
```markdown
# 给Python程序员的DSL指南

## 快速对比

| Python | DSL v3.0 | 说明 |
|--------|----------|------|
| `True/False` | `True/False` | ✅ 相同 |
| `None` | `None` | ✅ 相同 |
| `if x:` | `if x:` | ✅ 相同 |
| `for i in items:` | `for i in items:` | ✅ 相同 |
| `#注释` | `#注释` | ✅ 相同 |
| `"""注释"""` | `"""注释"""` | ✅ 相同 |
| `f"text {x}"` | `f"text {x}"` | ✅ 相同 |
| `and/or/not` | `and/or/not` | ✅ 相同 |
| `x = 1` | `let x = 1` | ⚠️ 需要 `let` 声明 |
| `MAX = 1` | `const MAX = 1` | ⚠️ DSL有真正的const |
| `match x:` | `when x:` | ⚠️ 关键字不同 |
| `{"key": "val"}` | `{key: "val"}` | ⚠️ 键可以无引号 |
| `os.environ` | `env.API_KEY` | ⚠️ 系统变量无$ |

## 5分钟上手

如果你会Python，你已经会90%的DSL语法了！

只需要记住3个小差异：
1. 声明变量用 `let x = 1`（而非直接 `x = 1`）
2. 常量用 `const MAX = 1`（Python没有）
3. 模式匹配用 `when x:` 而非 `match x:`（兼容Python 3.9）
```

---

## 🎯 下一步行动

### 立即执行
1. ✅ 更新 DESIGN-V3.md
2. ✅ 更新 V3-EBNF.md
3. ✅ 更新 V3-EXAMPLES.dsl
4. ✅ 创建 PYTHON-MIGRATION-GUIDE.md（Python程序员专用指南）

### 重点修改
- `true/false` → `True/False`（全文替换）
- `null` → `None`（全文替换）
- `$page.url` → `page.url`（删除$前缀）
- `"text {x}"` → `f"text {x}"`（引入f-string）
- `/* */` → `""" """`（块注释）
- 删除元数据块 `/**meta ... */`

---

**修订日期**: 2025-11-26
**目标**: 让Python程序员看到DSL就像看到Python代码
