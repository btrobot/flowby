# DSL Syntax Cheatsheet

> **Version**: 4.3 | **Generated**: 2025-11-29

快速查找 DSL 语法的参考表。

---

## 📋 目录

- [变量与常量](#变量与常量)
- [控制流](#控制流)
- [导航](#导航)
- [等待](#等待)
- [选择](#选择)
- [动作](#动作)
- [断言](#断言)
- [服务调用](#服务调用)
- [数据提取](#数据提取)
- [其他](#其他)
- [表达式](#表达式)
- [系统变量](#系统变量)
- [内置函数](#内置函数)
- [用户自定义函数](#用户自定义函数)

---

## 变量与常量

| 语法 | 说明 | 示例 |
|------|------|------|
| `let VAR = expr` | 声明可变变量 | `let count = 0` |
| `const VAR = expr` | 声明常量 | `const MAX = 100` |
| `VAR = expr` | 赋值 | `count = count + 1` |

---

## 控制流

### Step 块

```flow
step "步骤名称" [with diagnosis LEVEL]:
    ...
end step
```

| 诊断级别 | 说明 |
|---------|------|
| `none` | 无诊断 |
| `minimal` | 最小诊断 |
| `basic` | 基本诊断 |
| `standard` | 标准诊断 |
| `detailed` | 详细诊断 |
| `full` | 完整诊断 |

**示例：**
```flow
step "登录" with diagnosis standard:
    navigate to "https://example.com"
    click "#login"
end step
```

### If-Else

```flow
if condition:
    ...
[else:
    ...]
end if
```

**示例：**
```flow
if age >= 18:
    log "Adult"
else:
    log "Minor"
end if
```

### When-Otherwise（模式匹配）

```flow
when variable:
    "value1":
        ...
    "value2":
        ...
    [otherwise:
        ...]
end when
```

**示例：**
```flow
when status:
    "success":
        log "OK"
    "error":
        log "Fail"
    otherwise:
        log "Unknown"
end when
```

### For-Each 循环

```flow
for VAR in collection:
    ...
end for
```

**示例：**
```flow
for item in items:
    log "Item: {item}"
end for
```

---

## 导航

| 语法 | 说明 | 示例 |
|------|------|------|
| `navigate to URL` | 导航到 URL | `navigate to "https://example.com"` |
| `navigate to URL wait for STATE` | 导航并等待状态 | `navigate to url wait for networkidle` |
| `go back` | 后退 | `go back` |
| `go forward` | 前进 | `go forward` |
| `reload` | 刷新页面 | `reload` |

**页面状态：**
- `networkidle` - 网络空闲
- `domcontentloaded` - DOM 加载完成
- `load` - 页面完全加载

---

## 等待

| 语法 | 说明 | 示例 |
|------|------|------|
| `wait N [UNIT]` | 等待时长 | `wait 2 seconds`<br>`wait 1000 ms` |
| `wait for element SEL` | 等待元素出现 | `wait for element "#username"` |
| `wait for element SEL to be STATE` | 等待元素状态 | `wait for element ".modal" to be visible` |
| `wait for navigation` | 等待导航完成 | `wait for navigation` |

**时间单位：**
- `seconds` / `s` - 秒
- `milliseconds` / `ms` - 毫秒

**元素状态：**
- `visible` - 可见
- `hidden` - 隐藏
- `attached` - 附加到 DOM
- `detached` - 从 DOM 分离

---

## 选择

| 语法 | 说明 | 示例 |
|------|------|------|
| `select SEL` | 选择元素 | `select "#username"` |
| `select SEL where COND` | 条件选择 | `select "button" where text contains "Submit"` |
| `select option VAL from SEL` | 选择下拉选项 | `select option "USA" from "#country"` |

**条件运算符：**
- `contains` - 包含
- `equals` - 等于
- `matches` - 匹配（正则）

**可检查属性：**
- `text` - 文本内容
- `value` - 值
- `class` - CSS 类
- `id` - ID
- `name` - name 属性
- `href`, `src`, `alt`, `title` - 其他属性

---

## 动作

| 语法 | 说明 | 示例 |
|------|------|------|
| `type TEXT [into SEL]` | 输入文本 | `type "text" into "#input"`<br>`type "text"` |
| `click [SEL]` | 点击 | `click "#button"`<br>`click` |
| `double click [SEL]` | 双击 | `double click ".item"` |
| `right click [SEL]` | 右键点击 | `right click "#menu"` |
| `hover [over] SEL` | 悬停 | `hover "#menu-item"` |
| `clear [SEL]` | 清空输入 | `clear "#input"` |
| `press KEY` | 按键 | `press "Enter"` |
| `scroll to TARGET` | 滚动 | `scroll to top`<br>`scroll to "#footer"`<br>`scroll 500` |
| `check SEL` | 勾选复选框 | `check "#agree"` |
| `uncheck SEL` | 取消勾选 | `uncheck "#newsletter"` |
| `upload file PATH [to SEL]` | 上传文件 | `upload file "file.pdf" to "#input"` |

**输入修饰符：**
- `slowly` - 慢速输入
- `fast` - 快速输入

**滚动目标：**
- `top` - 顶部
- `bottom` - 底部
- `SEL` - 元素
- `NUMBER` - 像素

---

## 断言

| 语法 | 说明 | 示例 |
|------|------|------|
| `assert EXPR` | 表达式断言 (v2.0) | `assert x > 5` |
| `assert EXPR, MSG` | 带消息的断言 | `assert status == 200, "API failed"` |
| `assert EXPR, VAR` | 动态消息 (v4.3+) | `assert is_valid, error_msg` |
| `assert url OP VALUE` | URL 断言 | `assert url contains "example"` |
| `assert SEL exists` | 元素存在 | `assert "#header" exists` |
| `assert SEL visible` | 元素可见 | `assert ".modal" visible` |
| `assert SEL hidden` | 元素隐藏 | `assert "#loading" hidden` |
| `assert SEL has text VAL` | 元素文本 | `assert ".title" has text "Welcome"` |
| `assert SEL has value VAL` | 元素值 | `assert "#input" has value "test"` |
| `assert SEL has ATTR VAL` | 元素属性 | `assert "img" has src "logo.png"` |
| `assert text of SEL OP VAL` | 文本检查 | `assert text of ".msg" equals "OK"` |
| `assert ATTR of SEL OP VAL` | 属性检查 | `assert href of "a" contains "/profile"` |

**断言运算符：**
- `contains` - 包含
- `equals` - 等于
- `matches` - 匹配

### 退出语句 (v4.1)

| 语法 | 说明 | 示例 |
|------|------|------|
| `exit` | 成功退出 (code=0) | `exit` |
| `exit CODE` | 指定退出码 | `exit 0` / `exit 1` |
| `exit "MSG"` | 失败并带消息 (code=1) | `exit "Validation failed"` |
| `exit CODE, "MSG"` | 退出码 + 消息 | `exit 0, "Done"` |

**退出语义：**
- `code=0`: 成功退出 → `COMPLETED`
- `code≠0`: 失败退出 → `FAILED`
- 与 `assert` 区别：`exit` 是正常控制流，`assert` 是验证断言（失败抛错）

**示例：**
```flow
# 条件性成功退出
if user_type == "guest":
    exit 0, "Guest users skip processing"

# 条件性失败退出
if validation_errors > 0:
    exit 1, "Validation failed"
```

---

## 服务调用

```flow
call "provider.method" [with PARAMS] [into VAR]
```

| 参数格式 | 说明 |
|---------|------|
| `param=value` | 单个参数 |
| `param1=val1, param2=val2` | 多个参数 |

**示例：**
```flow
# HTTP GET
call "http.get" with
    url="https://api.example.com/users"
into response

# HTTP POST
call "http.post" with
    url="https://api.example.com/users",
    json={name: "Alice"},
    headers={"Authorization": "Bearer token"}
into result

# 随机数据
call "random.email" with domain="test.com" into email
call "random.password" with length=16 into password
```

**内置服务：**

### HTTP 服务

| 方法 | 说明 | 参数 |
|------|------|------|
| `http.get` | GET 请求 | `url`, `params`, `headers` |
| `http.post` | POST 请求 | `url`, `json`, `data`, `headers` |
| `http.put` | PUT 请求 | `url`, `json`, `data`, `headers` |
| `http.delete` | DELETE 请求 | `url`, `headers` |
| `http.patch` | PATCH 请求 | `url`, `json`, `headers` |

### Random 服务

| 方法 | 说明 | 参数 |
|------|------|------|
| `random.email` | 随机邮箱 | `domain` (可选) |
| `random.password` | 随机密码 | `length`, `include_special` |
| `random.username` | 随机用户名 | `prefix` (可选) |
| `random.phone` | 随机手机号 | `country_code` |
| `random.number` | 随机整数 | `min`, `max` |
| `random.uuid` | UUID | 无 |

---

## 数据提取

```flow
extract TARGET from SEL [pattern REGEX] into VAR
```

| 目标类型 | 说明 | 示例 |
|---------|------|------|
| `text` | 文本内容 | `extract text from ".username" into name` |
| `value` | 输入值 | `extract value from "#age" into age` |
| `attr "name"` | 属性值 | `extract attr "href" from "a" into link` |

**示例：**
```flow
extract text from ".email" into email
extract value from "#age-input" into age
extract attr "href" from ".profile-link" into url

# 使用正则提取
extract text from ".phone" pattern "\d{3}-\d{4}" into phone
```

---

## 其他

| 语法 | 说明 | 示例 |
|------|------|------|
| `log [LEVEL] EXPR` | 输出日志（v4.3+支持级别） | `log "Message"`<br>`log success "Done"`<br>`log error "Failed"` |
| `screenshot [of SEL] [as NAME] [fullpage]` | 截图 | `screenshot`<br>`screenshot as "login"`<br>`screenshot of "#content"` |

**日志级别（v4.3+）：**
- `log debug MSG` - 🔍 调试信息
- `log info MSG` - 普通信息（默认）
- `log success MSG` - ✓ 成功消息
- `log warning MSG` - ⚠ 警告消息
- `log error MSG` - ✗ 错误消息

---

## 表达式

### 运算符优先级

| 优先级 | 运算符 | 说明 | 结合性 |
|--------|--------|------|--------|
| 1（最低） | `or` | 逻辑或 | 左 |
| 2 | `and` | 逻辑与 | 左 |
| 3 | `not` | 逻辑非 | 右 |
| 4 | `==`, `!=`, `>`, `<`, `>=`, `<=` | 比较 | 左 |
| 5 | `+`, `-` | 加减 | 左 |
| 6 | `*`, `/`, `%` | 乘除模 | 左 |
| 7 | `-`, `not` | 一元 | 右 |
| 8（最高） | `.`, `[]`, `()` | 成员、数组、调用 | 左 |

### 字面量

| 类型 | 示例 |
|------|------|
| **字符串** | `"hello"`, `'world'`, `"Hello {name}"`, `f"Hello {name}"` |
| **数字** | `123`, `3.14`, `-10`, `0.5` |
| **布尔** | `true`, `false` |
| **空值** | `null` |
| **数组** | `[1, 2, 3]`, `["a", "b", "c"]` |
| **对象** | `{name: "Alice", age: 30}` |

### 字符串插值

```flow
let name = "Alice"

# 自动插值（推荐）
let greeting = "Hello, {name}!"      # "Hello, Alice!"

# f-string（可选，与 Python 一致）
let greeting2 = f"Hello, {name}!"    # "Hello, Alice!" （等效）

# 支持表达式
let x = 10
let msg = "Value is {x * 2}"         # "Value is 20"
let msg2 = f"Value is {x * 2}"       # "Value is 20" （等效）
```

**说明**：`f` 前缀可选，两种语法完全等效。

### 成员访问

```flow
user.name
response.data.items[0].title
```

### 数组访问

```flow
items[0]
arr[index]
```

### 方法调用

```flow
Math.abs(-10)
str.length()
Date.now()
```

---

## 系统变量

系统变量以 `$` 开头，只读。

| 命名空间 | 说明 | 可用属性 |
|---------|------|---------|
| `$context` | 执行上下文 | `task_id`, `execution_id`, `start_time`, `step_name`, `status` |
| `$page` | 当前页面 | `url`, `title`, `origin` |
| `$browser` | 浏览器 | `name`, `version` |
| `$env` | 环境变量 | `$env.VAR_NAME` |
| `$config` | 配置变量 | `$config.key` |

**示例：**
```flow
log "Task: {$context.task_id}"
log "URL: {$page.url}"
log "API: {$env.API_KEY}"
log "Base: {$config.base_url}"
```

---

## 内置函数

### Math 命名空间

| 函数 | 说明 | 示例 |
|------|------|------|
| `Math.abs(x)` | 绝对值 | `Math.abs(-10)` → `10` |
| `Math.round(x)` | 四舍五入 | `Math.round(3.7)` → `4` |
| `Math.ceil(x)` | 向上取整 | `Math.ceil(3.2)` → `4` |
| `Math.floor(x)` | 向下取整 | `Math.floor(3.7)` → `3` |
| `Math.max(...args)` | 最大值 | `Math.max(1, 5, 3)` → `5` |
| `Math.min(...args)` | 最小值 | `Math.min(1, 5, 3)` → `1` |
| `Math.random()` | 随机数 [0,1) | `Math.random()` → `0.xxx` |
| `Math.pow(base, exp)` | 幂运算 | `Math.pow(2, 10)` → `1024` |
| `Math.sqrt(x)` | 平方根 | `Math.sqrt(16)` → `4` |

### Date 命名空间

| 函数 | 说明 | 示例 |
|------|------|------|
| `Date.now()` | 当前时间戳（毫秒） | `Date.now()` → `1700000000000` |
| `Date.format(fmt)` | 格式化当前时间 | `Date.format("YYYY-MM-DD")` → `"2025-11-25"` |
| `Date.from_timestamp(ts)` | 时间戳转字符串 | `Date.from_timestamp(ts)` → `"2023-11-15 ..."` |

### JSON 命名空间

| 函数 | 说明 | 示例 |
|------|------|------|
| `JSON.stringify(obj)` | 对象转 JSON | `JSON.stringify(user)` → `'{"name":"Alice"}'` |
| `JSON.parse(str)` | JSON 转对象 | `JSON.parse('{"a":1}')` → `{a: 1}` |

### 全局函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `Number(value)` | 转数字 | `Number("123")` → `123.0` |
| `String(value)` | 转字符串 | `String(456)` → `"456"` |
| `Boolean(value)` | 转布尔 | `Boolean(0)` → `false` |
| `isNaN(value)` | 是否 NaN | `isNaN("abc")` → `true` |
| `isFinite(value)` | 是否有限 | `isFinite(123)` → `true` |

---

## 用户自定义函数

> **版本**: v4.3 | **状态**: ✅ Stable

### 函数定义

| 语法 | 说明 | 示例 |
|------|------|------|
| `function NAME():` | 定义无参函数 | `function greet(): log "Hi"` |
| `function NAME(p1, p2):` | 定义带参函数 | `function add(a, b): return a + b` |
| `return [expr]` | 返回值 | `return result` |

**完整示例：**
```flow
# 定义函数
function calculate_total(price, qty, tax):
    let subtotal = price * qty
    let tax_amount = subtotal * tax
    return subtotal + tax_amount

# 调用函数
let total = calculate_total(100, 3, 0.1)
log "Total: {total}"
```

### 核心特性速查

| 特性 | 支持 | 说明 |
|------|------|------|
| 局部作用域 | ✅ | 函数内变量独立 |
| 参数传递 | ✅ | 按值传递 |
| 返回值 | ✅ | 任意类型 |
| 访问全局常量 | ✅ | 可读取 `const` |
| 函数组合 | ✅ | 可调用其他函数 |
| 提前返回 | ✅ | `return` 可在任意位置 |
| 递归 | ❌ | 运行时检测并报错 |
| 闭包 | ❌ | 无法捕获外部变量 |
| 默认参数 | ❌ | 不支持 |

### 作用域示例

```flow
const TAX_RATE = 0.1  # 全局常量

function calc(price):
    let discount = 10  # 局部变量
    return (price - discount) * (1 + TAX_RATE)

let result = calc(100)
# discount 在此处不可见
```

### 常见用例

**1. 表单验证**
```flow
function is_valid_email(email):
    return email contains "@" and email contains "."

if is_valid_email(user_email):
    log "Valid"
```

**2. 数据处理**
```flow
function sum_array(numbers):
    let total = 0
    for num in numbers:
        total = total + num
    return total

let total = sum_array([1, 2, 3, 4, 5])
```

**3. 业务逻辑封装**
```flow
function get_discount(total_spent):
    if total_spent >= 1000:
        return 20
    if total_spent >= 500:
        return 10
    return 0

let discount = get_discount(customer_total)
```

---

## 注释

```flow
# 单行注释

"""
多行注释
可以跨多行
"""
```

---

## 快速示例

### 完整登录流程

```flow
# 配置
const BASE_URL = "https://example.com"

# 导航
step "打开登录页":
    navigate to BASE_URL + "/login"
    wait for element "#login-form"
    assert "#login-form" visible
end step

# 输入
step "填写表单":
    select "#email"
    type "user@test.com"

    select "#password"
    type "password123"
end step

# 提交
step "提交登录":
    click "#submit-button"
    wait for navigation
    assert url contains "/dashboard"
end step

# 验证
step "验证登录":
    extract text from ".username" into username
    log "登录成功: {username}"

    assert ".welcome" exists
    screenshot as "dashboard"
end step
```

### API 调用示例

```flow
# GET 请求
call "http.get" with
    url="https://api.example.com/users/1"
into user

log "User: {user.data.name}"

# POST 请求
call "http.post" with
    url="https://api.example.com/users",
    json={name: "Alice", age: 30},
    headers={"Authorization": "Bearer token"}
into response

if response.status_code == 201:
    log "Created: {response.data.id}"
end if
```

### 循环与条件

```flow
let items = [1, 2, 3, 4, 5]

for item in items:
    if item % 2 == 0:
        log "{item} is even"
    else:
        log "{item} is odd"
    end if
end for
```

---

**完整文档**:
- [完整 EBNF 语法](./DSL-GRAMMAR.ebnf)
- [快速参考](./DSL-GRAMMAR-QUICK-REFERENCE.md)

**版本**: 2.0 | **更新**: 2025-11-25
