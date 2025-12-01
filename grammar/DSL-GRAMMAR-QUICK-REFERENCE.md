# DSL Grammar Reference - Quick Guide

> **Version**: 6.6
> **Generated**: 2025-12-01
> **Complete EBNF**: See [DSL-GRAMMAR.ebnf](./DSL-GRAMMAR.ebnf)

---

## 语法概览

### 程序结构

```bnf
program ::= statement*

statement ::= variable_declaration
            | control_flow
            | navigation
            | action
            | assertion
            | service_call
            | extraction
            | log
            | screenshot
```

---

## 1. 变量声明

### Let 语句（可变变量）

```bnf
let_statement ::= "let" IDENTIFIER "=" expression
```

**示例：**
```flow
let email = "user@test.com"
let count = 0
let items = [1, 2, 3]
let user = {name: "Alice", age: 30}
```

### Const 语句（常量）

```bnf
const_statement ::= "const" IDENTIFIER "=" expression
```

**示例：**
```flow
const MAX_RETRIES = 3
const API_KEY = "your-key"
```

### 赋值语句

```bnf
assignment ::= IDENTIFIER "=" expression
```

**示例：**
```flow
count = count + 1
email = "new@test.com"
```

---

## 2. 控制流

### Step 块（步骤）

```bnf
step_block ::= "step" STRING [ "with" "diagnosis" diagnosis_level ] ":"
               statement*
               "end" "step"

diagnosis_level ::= "none" | "minimal" | "basic" | "standard" | "detailed" | "full"
```

**示例：**
```flow
step "登录流程" with diagnosis detailed:
    navigate to "https://example.com/login"
    type "user@test.com" into "#email"
    click "#submit"
```

### If 块（条件）

```bnf
if_block ::= "if" expression ":"
             INDENT statement* DEDENT
             [ "else" ":" INDENT statement* DEDENT ]
```

**示例：**
```flow
if age >= 18:
    log "Adult"
else:
    log "Minor"
```

### When 块（模式匹配）

```bnf
when_block ::= "when" STRING ":"
               INDENT ( STRING ":" INDENT statement* DEDENT )+
               [ "otherwise" ":" INDENT statement* DEDENT ]
               DEDENT
```

**示例：**
```flow
when status:
    "success":
        log "OK"
    "error":
        log "Failed"
    otherwise:
        log "Unknown"
```

### For 循环（遍历）

```bnf
for_loop ::= "for" IDENTIFIER "in" expression ":"
             INDENT statement* DEDENT
```

**示例：**
```flow
for item in items:
    log "Item: {item}"
```

### While 循环（条件循环）- v3.0

```bnf
while_loop ::= "while" expression ":"
               INDENT statement* DEDENT
```

**示例：**
```flow
# 基本 while 循环
let count = 0
while count < 5:
    log f"Count: {count}"
    count = count + 1

# while True + break
let retry = 0
while True:
    let status = check_status()
    if status.success:
        break
    retry = retry + 1
    wait 1
```

### Break 语句（退出循环）- v3.0

```bnf
break_statement ::= "break"
```

**说明**: 立即退出当前循环（while 或 for）

**示例：**
```flow
let i = 0
while i < 100:
    if i == 10:
        break
    i = i + 1
```

### Continue 语句（跳过迭代）- v3.0

```bnf
continue_statement ::= "continue"
```

**说明**: 跳过当前迭代，继续下一次循环

**示例：**
```flow
let i = 0
while i < 10:
    i = i + 1
    if i % 2 == 0:
        continue
    log f"Odd: {i}"
```

---

## 3. 导航

### Navigate（导航到 URL）

```bnf
navigate ::= "navigate" "to" expression
             [ "wait" "for" ("networkidle" | "domcontentloaded" | "load") ]
```

**示例：**
```flow
navigate to "https://example.com"
navigate to $config.base_url + "/login" wait for networkidle
```

### Go（前进/后退）

```bnf
go ::= "go" ("back" | "forward")
```

**示例：**
```flow
go back
go forward
```

### Reload（刷新）

```bnf
reload ::= "reload"
```

**示例：**
```flow
reload
```

---

## 4. 等待

### Wait 时长

```bnf
wait_duration ::= "wait" [ "for" ] expression [ ("seconds" | "milliseconds" | "s" | "ms") ]
```

**示例：**
```flow
# 字面量（向后兼容）
wait 2 seconds
wait for 1000 ms
wait 5

# 表达式（v6.0.2 新增）
wait delay_time s                  # 变量
wait (retry * 2) s                 # 算术表达式
wait (base_delay + offset) ms      # 复杂表达式
# 注意：使用表达式时，时间单位是必需的
```

### Wait 元素

```bnf
wait_element ::= "wait" "for" "element" selector
                 [ "to" "be" ("visible" | "hidden" | "attached" | "detached") ]
                 [ "timeout" expression ]
```

**示例：**
```flow
wait for element "#username"
wait for element ".modal" to be visible
wait for element "#loading" to be hidden timeout 5000
```

### Wait 导航

```bnf
wait_navigation ::= "wait" "for" "navigation"
                    [ "to" expression ]
                    [ "wait" "for" page_state ]
                    [ "timeout" expression ]
```

**示例：**
```flow
wait for navigation
wait for navigation to "https://example.com/dashboard"
```

---

## 5. 选择与动作

### Select（选择元素）

```bnf
select ::= "select" selector
           [ "where" condition ( "and" condition )* ]
```

**示例：**
```flow
select "#username"
select "button" where text contains "Submit"
select "input" where name equals "email" and class contains "required"
```

### Type（输入文本）

```bnf
type ::= "type" expression [ "into" selector ] [ ("slowly" | "fast") ]
```

**示例：**
```flow
type "user@test.com" into "#email"
type "password123"  # 输入到当前选中元素
type "text" slowly
```

### Click（点击）

```bnf
click ::= ("click" | "double" "click" | "right" "click") [ selector ]
```

**示例：**
```flow
click "#submit-button"
double click ".item"
right click "#context-menu-trigger"
click  # 点击当前选中元素
```

### Hover（悬停）

```bnf
hover ::= "hover" [ "over" ] selector
```

**示例：**
```flow
hover "#menu-item"
hover over ".tooltip-trigger"
```

### Clear（清空）

```bnf
clear ::= "clear" [ selector ]
```

**示例：**
```flow
clear "#input-field"
clear  # 清空当前选中元素
```

### Press（按键）

```bnf
press ::= "press" expression
```

**示例：**
```flow
press "Enter"
press "Escape"
press "Control+A"
```

### Scroll（滚动）

```bnf
scroll ::= "scroll" ( "to" ("top" | "bottom")
                    | "to" selector
                    | expression )
```

**示例：**
```flow
scroll to top
scroll to bottom
scroll to "#footer"
scroll 500  # 滚动 500 像素
```

### Check/Uncheck（勾选/取消勾选）

```bnf
check ::= ("check" | "uncheck") selector
```

**示例：**
```flow
check "#agree-terms"
uncheck "#newsletter"
```

### Upload（上传文件）

```bnf
upload ::= "upload" "file" expression [ "to" selector ]
```

**示例：**
```flow
upload file "path/to/file.pdf" to "#file-input"
```

---

## 6. 断言

### Assert Expression (v2.0, v4.3+)

```bnf
assert_expr ::= "assert" expression [ "," message_expression ]
```

**示例：**
```flow
# 基本断言
assert x > 5
assert status == 200
assert user.age >= 18, "User must be adult"

# v4.3+: 动态错误消息
assert condition, error_msg                          # 变量消息
assert is_valid, get_error_message()                 # 函数调用消息
assert x > 0, "Value must be positive, got {x}"      # 自动插值
assert x > 0, f"Value must be positive, got {x}"     # f-string（可选）
```

### Assert URL

```bnf
assert_url ::= "assert" "url" ("contains" | "equals" | "matches") expression
```

**示例：**
```flow
assert url contains "example.com"
assert url equals "https://example.com/dashboard"
```

### Assert Element

```bnf
assert_element ::= "assert" selector ("exists" | "visible" | "hidden"
                                      | "has" "text" expression
                                      | "has" "value" expression
                                      | "has" attribute expression)
```

**示例：**
```flow
assert "#header" exists
assert ".modal" visible
assert "#loading" hidden
assert ".welcome" has text "Welcome!"
assert "#username" has value "user@test.com"
assert "img" has src "logo.png"
```

### Exit Statement (v4.1)

```bnf
exit_statement ::= "exit" [ INTEGER ] [ "," STRING ]
```

**语义：**
- `exit` - 成功退出（code=0）
- `exit 0` - 明确指定成功退出
- `exit 1` - 失败退出
- `exit "message"` - 失败并带消息（code=1）
- `exit 0, "message"` - 成功并带消息
- `exit 1, "message"` - 失败并带消息

**示例：**
```flow
# 成功退出
exit
exit 0
exit 0, "Processing completed"

# 失败退出
exit 1
exit "Validation failed"
exit 1, "User not authenticated"

# 条件性退出
if user_type == "guest":
    exit 0, "Guest users skip verification"

if validation_errors > 0:
    exit 1, "Form validation failed"
```

**与 assert 的区别：**
- `assert`: 验证预期条件（失败抛出错误）
- `exit`: 受控终止执行（正常控制流）

---

## 7. 服务调用

```bnf
service_call ::= "call" STRING
                 [ param ("," param)* ]
                 [ "into" IDENTIFIER ]

param ::= IDENTIFIER "=" expression
```

**示例：**
```flow
call "http.get" with url="https://api.example.com/users" into response

call "http.post" with
    url="https://api.example.com/users",
    json={name: "Alice", email: "alice@test.com"},
    headers={"Authorization": "Bearer token"}
into result

call "random.email" with domain="test.com" into email
```

---

## 8. 提取数据

```bnf
extract ::= "extract" ("text" | "value" | "attr" STRING) "from" selector
            [ "pattern" STRING ]
            "into" IDENTIFIER
```

**示例：**
```flow
extract text from ".username" into username
extract value from "#age-input" into age
extract attr "href" from "a.profile-link" into link

extract text from ".email" pattern "\w+@\w+\.\w+" into email
```

---

## 9. 日志

```bnf
log ::= "log" [ level ] expression

level ::= "debug" | "info" | "success" | "warning" | "error"
```

**示例：**
```flow
# 默认级别（info）
log "Hello, World!"
log "User: {username}, Age: {age}"       # ✅ 自动插值
log count + 10

# v4.3+: 显式级别
log debug "调试信息"              # 🔍
log info "普通消息"
log success "操作成功"            # ✓
log warning "注意事项"            # ⚠
log error "发生错误"              # ✗

# 支持字符串插值和表达式
log success "用户 {username} 注册成功"       # ✅ 自动插值（推荐）
log success f"用户 {username} 注册成功"      # ✅ f-string（可选）
log error error_msg                         # ✅ 变量
```

**字符串插值**：
- 自动插值：`"text {expr}"` - 推荐，更简洁
- f-string：`f"text {expr}"` - 可选，与 Python 风格一致
- 两种语法完全等效

**日志级别（v4.3+）：**
- `debug`: 🔍 调试信息
- `info`: 普通信息（默认）
- `success`: ✓ 成功消息
- `warning`: ⚠ 警告消息
- `error`: ✗ 错误消息

---

## 10. 截图

```bnf
screenshot ::= "screenshot" [ "of" selector ]
               [ "as" STRING ]
               [ "fullpage" ]
```

**示例：**
```flow
screenshot
screenshot as "homepage"
screenshot of "#main-content"
screenshot fullpage as "full-page"
```

---

## 11. 表达式

### 运算符优先级（从低到高）

| 优先级 | 运算符 | 说明 | 示例 |
|--------|--------|------|------|
| 1 | `or` | 逻辑或 | `a or b` |
| 2 | `and` | 逻辑与 | `a and b` |
| 3 | `not` | 逻辑非 | `not a` |
| 4 | `==`, `!=`, `>`, `<`, `>=`, `<=` | 比较 | `a > b` |
| 5 | `+`, `-` | 加减 | `a + b` |
| 6 | `*`, `/`, `%` | 乘除模 | `a * b` |
| 7 | `-`, `not` | 一元 | `-a` |
| 8 | `.`, `[]`, `()` | 成员访问、数组访问、调用 | `obj.prop`, `arr[0]`, `func()` |

### 字面量

```bnf
literal ::= STRING           # "hello" or 'hello'
          | NUMBER           # 123 or 123.45
          | BOOLEAN          # True or False
          | NONE             # None
          | array_literal    # [1, 2, 3]
          | object_literal   # {name: "Alice"}
```

### 字符串插值

```flow
let name = "Alice"
let message = "Hello, {name}!"  # 结果: "Hello, Alice!"
```

### 数组字面量

```flow
let arr = [1, 2, 3, 4, 5]
let mixed = ["text", 123, True, None]
```

### 对象字面量

```flow
let user = {
    name: "Alice",
    age: 30,
    email: "alice@test.com"
}
```

### 成员访问

```flow
let email = user.email
let title = response.data.title
```

### 数组访问

```flow
let first = items[0]
let last = items[items.length - 1]
```

### 方法调用

```flow
let abs_value = Math.abs(-10)
let max_value = Math.max(1, 5, 3)
let timestamp = Date.now()
let json_str = JSON.stringify(obj)
```

---

## 12. 系统变量

系统变量以 `$` 开头，只读。

### $context（执行上下文）

```flow
$context.task_id
$context.execution_id
$context.start_time
$context.step_name
$context.status
```

### $page（当前页面）

```flow
$page.url
$page.title
$page.origin
```

### $browser（浏览器信息）

```flow
$browser.name
$browser.version
```

### $env（环境变量）

```flow
$env.API_KEY
$env.DATABASE_URL
```

### $config（配置变量）

```flow
$config.base_url
$config.timeout
```

---

## 13. 内置函数

### Math

```flow
Math.abs(-10)           # 10
Math.round(3.7)         # 4
Math.ceil(3.2)          # 4
Math.floor(3.7)         # 3
Math.max(1, 5, 3)       # 5
Math.min(1, 5, 3)       # 1
Math.random()           # 0.xxx
Math.pow(2, 10)         # 1024
Math.sqrt(16)           # 4
```

### Date

```flow
Date.now()                           # 1700000000000 (timestamp)
Date.format("YYYY-MM-DD")            # "2025-11-25"
Date.from_timestamp(1700000000000)   # "2023-11-15 00:00:00"
```

### JSON

```flow
JSON.stringify(obj)     # 对象转 JSON 字符串
JSON.parse(json_str)    # JSON 字符串转对象
```

### 全局函数

```flow
Number("123")           # 123.0
String(456)             # "456"
Boolean(0)              # false
isNaN(value)            # 检查是否 NaN
isFinite(value)         # 检查是否有限数
```

---

## 11. REST API Integration (v4.2)

### OpenAPI Resource Statement

```bnf
resource_statement ::= "resource" IDENTIFIER "from" STRING
                     | "resource" IDENTIFIER ":" resource_config

resource_config ::= ("spec" ":" STRING)?
                    ("base_url" ":" STRING)?
                    ("auth" ":" object)?
                    ("timeout" ":" NUMBER)?
                    ("headers" ":" object)?
                    ("response_mapping" ":" object)?
                    ("validate_response" ":" BOOLEAN)?
                    ("resilience" ":" object)?
                    ("mock" ":" object)?
```

### 基本用法

**简单形式：**
```flow
# 定义资源
resource user_api from "openapi/user-service.yml"

# 调用 API 操作
let user = user_api.getUser(userId=123)
log "User: {user.name}, Email: {user.email}"

# POST 请求
let new_user = user_api.createUser(data={name: "Alice", email: "alice@example.com"})
```

**完整配置：**
```flow
resource user_api:
    spec: "openapi/user-service.yml"
    base_url: "https://api.example.com/v1"
    auth: {type: "bearer", token: $env.API_TOKEN}
    timeout: 30
    headers: {"X-Client-ID": "flowby"}

    # Response mapping (Phase 3)
    response_mapping: {
        field_mapping: {userId: "user_id"},
        exclude_fields: ["internal"]
    }
    validate_response: true

    # Resilience (Phase 4)
    resilience: {
        retry: {
            max_retries: 3,
            strategy: "exponential",
            base_delay: 1.0,
            jitter: true
        },
        circuit_breaker: {
            failure_threshold: 5,
            recovery_timeout: 60
        }
    }

    # Mock mode (Phase 5)
    mock: {
        enabled: false,
        responses: {
            getUser: {data: {id: 1, name: "Mock User"}}
        }
    }
```

### 认证支持 (Phase 2)

```flow
# Bearer token
resource api:
    spec: "openapi.yml"
    auth: {type: "bearer", token: $env.TOKEN}

# API Key
resource api:
    spec: "openapi.yml"
    auth: {type: "apiKey", key: $env.API_KEY, in: "header", name: "X-API-Key"}

# Basic auth
resource api:
    spec: "openapi.yml"
    auth: {type: "basic", username: "user", password: "pass"}
```

### 响应映射 (Phase 3)

```flow
resource api:
    spec: "openapi.yml"
    response_mapping: {
        field_mapping: {
            userId: "user_id",
            fullName: "full_name"
        },
        exclude_fields: ["internal_id", "metadata"],
        include_only: ["id", "name", "email"]
    }
    validate_response: true  # Validate against OpenAPI schema
```

### 弹性处理 (Phase 4)

```flow
resource api:
    spec: "openapi.yml"
    resilience: {
        # Retry configuration
        retry: {
            max_retries: 3,
            strategy: "exponential",  # or "fixed", "linear"
            base_delay: 1.0,
            max_delay: 60.0,
            jitter: true,
            retry_on: [500, 502, 503, 504]
        },

        # Circuit breaker
        circuit_breaker: {
            failure_threshold: 5,
            recovery_timeout: 60,
            half_open_max_calls: 3
        }
    }
```

### Mock 模式 (Phase 5)

```flow
resource api:
    spec: "openapi.yml"
    mock: {
        enabled: true,  # Enable mock mode
        responses: {
            getUser: {
                data: {id: 1, name: "Mock User"},
                status: 200
            },
            listUsers: {
                data: [{id: 1}, {id: 2}],
                delay: 0.5  # Simulate network delay
            }
        },
        record_calls: true  # Record all API calls for testing
    }
```

### 完整示例

```flow
# 定义 API 资源
resource github_api:
    spec: "https://api.github.com/openapi.json"
    base_url: "https://api.github.com"
    auth: {type: "bearer", token: $env.GITHUB_TOKEN}
    timeout: 30
    resilience: {
        retry: {max_retries: 3, strategy: "exponential"}
    }

# 获取用户信息
step "Get GitHub User":
    let user = github_api.getUser(username="octocat")

    if user.status == 200:
        log "Name: {user.data.name}"
        log "Repos: {user.data.public_repos}"
        log "Followers: {user.data.followers}"
    else:
        log "Error: {user.status}"
        exit

# 列出仓库
step "List Repositories":
    let repos = github_api.listUserRepos(username="octocat", per_page=10)

    for repo in repos.data:
        log "Repository: {repo.name} ⭐ {repo.stargazers_count}"
```

### 实施阶段

| Phase | 特性 | 状态 |
|-------|------|------|
| Phase 1 | 基本 OpenAPI 集成、自动生成方法 | ✅ 完成 |
| Phase 2 | 认证支持 (Bearer, API Key, Basic) | ✅ 完成 |
| Phase 3 | 响应映射、字段转换、模式验证 | ✅ 完成 |
| Phase 4 | 弹性处理 (重试、断路器) | ✅ 完成 |
| Phase 5 | Mock 模式 (测试支持) | ✅ 完成 |

---

## 12. 用户自定义函数 (v4.3)

### 函数定义

```bnf
function_definition ::= "function" IDENTIFIER "(" [ parameter_list ] ")" ":"
                        statement*

parameter_list ::= IDENTIFIER ( "," IDENTIFIER )*
```

**示例：**
```flow
# 无参数函数
function greet():
    log "Hello, World!"

# 带参数函数
function add(a, b):
    return a + b

# 多个参数
function calculate_total(price, quantity, tax_rate):
    let subtotal = price * quantity
    let tax = subtotal * tax_rate
    return subtotal + tax
```

### Return 语句

```bnf
return_statement ::= "return" [ expression ]
```

**说明**: 从函数返回值并终止执行

**示例：**
```flow
function max(a, b):
    if a > b:
        return a
    return b

function is_valid_email(email):
    return email contains "@" and email contains "."

function get_status():
    return  # 返回 None
```

### 函数调用

```bnf
function_call ::= IDENTIFIER "(" [ argument_list ] ")"

argument_list ::= expression ( "," expression )*
```

**示例：**
```flow
# 基本调用
greet()

# 带参数调用
let sum = add(10, 20)
let total = calculate_total(100, 3, 0.1)

# 嵌套调用
let max_value = max(add(10, 20), add(15, 25))

# 在表达式中调用
if is_valid_email(user_email):
    log "Email is valid"
```

### 核心特性

**✅ 支持**:
- ✅ 局部作用域（函数内变量独立）
- ✅ 参数传递（按值传递）
- ✅ 返回值（任意类型）
- ✅ 访问全局常量（`const` 定义的变量）
- ✅ 函数组合（函数调用其他函数）
- ✅ 提前返回（`return` 可在任意位置）

**❌ 不支持**:
- ❌ 递归（运行时检测并报错）
- ❌ 闭包（无法捕获外部变量）
- ❌ 默认参数
- ❌ 可变参数 (`*args`)
- ❌ 关键字参数
- ❌ 函数重载

### 作用域规则

```flow
# 全局变量
const TAX_RATE = 0.1
let global_counter = 0

function calculate_price(price):
    # 局部变量
    let discount = 10
    let final_price = price - discount

    # 可以读取全局常量
    let tax = final_price * TAX_RATE

    # ❌ 不能修改全局变量
    # global_counter = global_counter + 1  # 错误！

    return final_price + tax

let result = calculate_price(100)
# discount 在此处不可见
```

### 完整示例

```flow
# 定义辅助函数
function is_length_valid(text, min_len, max_len):
    let length = len(text)
    return length >= min_len and length <= max_len

function validate_username(username):
    if not is_length_valid(username, 3, 20):
        log "❌ 用户名长度必须在 3-20 字符之间"
        return False
    log "✓ 用户名格式正确"
    return True

function validate_email(email):
    if not (email contains "@" and email contains "."):
        log "❌ 邮箱格式不正确"
        return False
    log "✓ 邮箱格式正确"
    return True

# 主流程
let username = "alice_wang"
let email = "alice@example.com"

if validate_username(username) and validate_email(email):
    log "✅ 验证通过"
else:
    log "❌ 验证失败"
```

---

## 13. 模块系统 (v5.0)

### Library Declaration

```bnf
library_declaration ::= "library" IDENTIFIER
```

**示例**:
```flow
# File: libs/helpers.flow
library helpers

export const VERSION = "1.0.0"

export function greet(name):
    return "Hello, {name}!"
```

### Export Statement

```bnf
export_statement ::= "export" ("const" | "function") ...
```

**导出常量**:
```flow
export const MAX_RETRIES = 3
export const API_BASE = "https://api.example.com"
```

**导出函数**:
```flow
export function validate_email(email):
    return email contains "@" and email contains "."
```

### Import Statement

```bnf
import_statement ::= "import" IDENTIFIER "from" STRING
                   | "from" STRING "import" identifier_list

identifier_list ::= IDENTIFIER ("," IDENTIFIER)*
```

**Import with alias**:
```flow
import helpers from "libs/helpers.flow"

log helpers.VERSION
let msg = helpers.greet("Alice")
```

**From-import (specific members)**:
```flow
from "libs/helpers.flow" import greet, VERSION

log VERSION
log greet("Bob")
```

### Member Access

```bnf
member_access ::= module_name "." member_name
```

**示例**:
```flow
import validators from "libs/validators.flow"

if validators.validate_email("user@example.com"):
    log "Valid email"
```

### 完整示例

```flow
# File: libs/validators.flow
library validators

export const EMAIL_PATTERN = "^[a-zA-Z0-9._%+-]+@.+\\..+$"

export function validate_email(email):
    if email contains "@" and email contains ".":
        return true
    return false

export function validate_age(age):
    return age >= 18 and age <= 120

# File: main.flow
import validators from "libs/validators.flow"

let email = input("Email: ")
let age = input("Age: ", type=integer)

if validators.validate_email(email) and validators.validate_age(age):
    log "✅ 验证通过"
else:
    log "❌ 验证失败"
```

---

## 14. Input Expression (v5.1)

### 基本语法

```bnf
input_expression ::= "input" "(" expression ["," parameter_list] ")"

parameter_list ::= parameter ("," parameter)*

parameter ::= "default" "=" expression
            | "type" "=" ("text" | "password" | "integer" | "float")
```

### 基本输入

```flow
let name = input("Enter your name: ")
log "Hello, {name}!"
```

### 带默认值（CI/CD 友好）

```flow
let email = input("Email: ", default="test@example.com")
let url = input("URL: ", default="https://example.com")
```

### 类型转换

```flow
# Integer conversion
let age = input("Age: ", type=integer)

# Float conversion
let price = input("Price: ", type=float)

# Password input (no echo)
let password = input("Password: ", type=password)
```

### 组合参数

```flow
let retry_count = input("Retry count: ", default="3", type=integer)
let timeout = input("Timeout (s): ", default="30.0", type=float)
```

### 实战示例

```flow
# Interactive configuration
let env = input("Environment [dev/prod]: ", default="dev")
let debug = input("Enable debug? [yes/no]: ", default="no")

if debug == "yes":
    const LOG_LEVEL = "DEBUG"
else:
    const LOG_LEVEL = "INFO"

let max_retries = input("Max retries: ", default="3", type=integer)

# Use configured values
for attempt in range(1, max_retries + 1):
    log "Attempt {attempt}/{max_retries} in {env} environment"
    # ... automation logic ...
```

### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `prompt` | String/Expr | ✅ | - | 提示文本 |
| `default` | Any/Expr | ❌ | None | 默认值（空输入时使用） |
| `type` | Keyword | ❌ | text | 输入类型：text, password, integer, float |

### 类型转换行为

| Type | 行为 | 错误处理 |
|------|------|----------|
| `text` | 返回字符串（默认） | 无 |
| `password` | 无回显输入，返回字符串 | 无 |
| `integer` | 转换为整数 | ValueError if invalid |
| `float` | 转换为浮点数 | ValueError if invalid |

---

## 15. Lambda Expressions (v6.4)

### 基本语法

```bnf
lambda_expression ::= lambda_parameters "=>" expression

lambda_parameters ::= IDENTIFIER                  # Single: x => expr
                    | "(" ")"                     # No params: () => expr
                    | "(" identifier_list ")"     # Multiple: (x, y) => expr
```

### 示例

```flow
# Lambda 定义
let double = x => x * 2
let add = (x, y) => x + y
let is_positive = x => x > 0

# Lambda 调用
log double(5)          # 10
log add(3, 7)          # 10
log is_positive(-5)    # False

# 作为参数传递（与集合方法配合使用）
let numbers = [1, 2, 3, 4, 5]
let evens = numbers.filter(x => x % 2 == 0)      # [2, 4]
let doubled = numbers.map(x => x * 2)            # [2, 4, 6, 8, 10]
let sum = numbers.reduce((acc, x) => acc + x, 0) # 15
```

### 特性

- ✅ 闭包支持（捕获外层作用域变量）
- ✅ 作为参数传递
- ✅ 存储在变量中
- ✅ 表达式体（单一表达式返回）
- ❌ 不支持语句块（只能是单一表达式）

---

## 16. Collection Methods (v6.4, v6.5)

### Core Collection Methods (v6.4)

#### filter() - 过滤数组

```bnf
filter_method ::= expression "." "filter" "(" predicate ")"
```

```flow
let numbers = [1, 2, 3, 4, 5, 6]
let evens = numbers.filter(x => x % 2 == 0)       # [2, 4, 6]
let large = numbers.filter(x => x > 3)            # [4, 5, 6]
```

#### map() - 转换数组

```bnf
map_method ::= expression "." "map" "(" transform ")"
```

```flow
let numbers = [1, 2, 3]
let doubled = numbers.map(x => x * 2)             # [2, 4, 6]
let squared = numbers.map(x => x * x)             # [1, 4, 9]
```

#### reduce() - 累积值

```bnf
reduce_method ::= expression "." "reduce" "(" reducer "," initial ")"
```

```flow
let numbers = [1, 2, 3, 4]
let sum = numbers.reduce((acc, x) => acc + x, 0)  # 10
let product = numbers.reduce((acc, x) => acc * x, 1)  # 24
```

#### find() - 查找元素

```bnf
find_method ::= expression "." "find" "(" predicate ")"
```

```flow
let numbers = [1, 2, 3, 4, 5]
let found = numbers.find(x => x > 3)              # 4
let notFound = numbers.find(x => x > 10)          # None
```

#### findIndex() - 查找索引

```bnf
findIndex_method ::= expression "." "findIndex" "(" predicate ")"
```

```flow
let numbers = [1, 2, 3, 4, 5]
let index = numbers.findIndex(x => x > 3)         # 3
let notFound = numbers.findIndex(x => x > 10)     # -1
```

#### some() - 任意匹配

```bnf
some_method ::= expression "." "some" "(" predicate ")"
```

```flow
let numbers = [1, 2, 3, 4, 5]
let hasEven = numbers.some(x => x % 2 == 0)       # True
let hasNegative = numbers.some(x => x < 0)        # False
```

#### every() - 全部匹配

```bnf
every_method ::= expression "." "every" "(" predicate ")"
```

```flow
let numbers = [2, 4, 6, 8]
let allEven = numbers.every(x => x % 2 == 0)      # True
let allPositive = numbers.every(x => x > 0)       # True
```

### Extended Collection Methods (v6.5)

#### sort() - 排序数组

```bnf
sort_method ::= expression "." "sort" "(" [ comparator ] ")"
```

```flow
let numbers = [3, 1, 4, 1, 5, 9]
let sorted = numbers.sort()                        # [1, 1, 3, 4, 5, 9]

let users = [{name: "Bob", age: 30}, {name: "Alice", age: 25}]
let byAge = users.sort((a, b) => a.age - b.age)    # 按年龄排序
```

#### reverse() - 反转数组

```bnf
reverse_method ::= expression "." "reverse" "(" ")"
```

```flow
let numbers = [1, 2, 3, 4, 5]
let reversed = numbers.reverse()                   # [5, 4, 3, 2, 1]
```

#### slice() - 切片数组

```bnf
slice_method ::= expression "." "slice" "(" start [ "," end ] ")"
```

```flow
let numbers = [1, 2, 3, 4, 5]
let slice1 = numbers.slice(1, 3)                   # [2, 3]
let slice2 = numbers.slice(2)                      # [3, 4, 5]
```

#### join() - 连接为字符串

```bnf
join_method ::= expression "." "join" "(" separator ")"
```

```flow
let words = ["Hello", "Flowby", "DSL"]
let sentence = words.join(" ")                     # "Hello Flowby DSL"
let csv = ["a", "b", "c"].join(",")                # "a,b,c"
```

#### unique() - 去重

```bnf
unique_method ::= expression "." "unique" "(" ")"
```

```flow
let numbers = [1, 2, 2, 3, 1, 4, 3]
let unique = numbers.unique()                      # [1, 2, 3, 4]
```

#### length() - 获取长度

```bnf
length_method ::= expression "." "length" "(" ")"
```

```flow
let numbers = [1, 2, 3, 4, 5]
let count = numbers.length()                       # 5
```

### 方法链式调用

```flow
let numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 链式调用
let result = numbers
    .filter(x => x > 5)                            # [6, 7, 8, 9, 10]
    .map(x => x * 2)                               # [12, 14, 16, 18, 20]
    .reduce((acc, x) => acc + x, 0)                # 80

# 复杂链式
let stats = [85, 92, 78, 95, 88, 91]
    .filter(x => x >= 80)                          # [85, 92, 95, 88, 91]
    .sort()                                        # [85, 88, 91, 92, 95]
    .slice(0, 3)                                   # [85, 88, 91]
```

---

## 17. Utility Functions (v6.6)

### String Methods (v6.6)

#### capitalize() - 首字母大写

```bnf
capitalize_method ::= expression "." "capitalize" "(" ")"
```

```flow
let title = "hello world"
let capitalized = title.capitalize()               # "Hello world"
```

#### padStart() - 左填充

```bnf
padStart_method ::= expression "." "padStart" "(" length "," fillStr ")"
```

```flow
let id = "5"
let paddedId = id.padStart(3, "0")                 # "005"
```

#### padEnd() - 右填充

```bnf
padEnd_method ::= expression "." "padEnd" "(" length "," fillStr ")"
```

```flow
let code = "A"
let paddedCode = code.padEnd(4, "0")               # "A000"
```

#### repeat() - 重复字符串

```bnf
repeat_method ::= expression "." "repeat" "(" count ")"
```

```flow
let pattern = "="
let line = pattern.repeat(40)                      # "======...======"
let laugh = "ha".repeat(3)                         # "hahaha"
```

### Array Utility Methods (v6.6)

#### flatten() - 展平嵌套数组

```bnf
flatten_method ::= expression "." "flatten" "(" [ depth ] ")"
```

```flow
let nested = [[1, 2], [3, 4], [5, 6]]
let flat = nested.flatten()                        # [1, 2, 3, 4, 5, 6]

let deep = [1, [2, [3, [4]]]]
let flat2 = deep.flatten(2)                        # [1, 2, 3, [4]]
```

#### chunk() - 分块数组

```bnf
chunk_method ::= expression "." "chunk" "(" size ")"
```

```flow
let numbers = [1, 2, 3, 4, 5, 6, 7]
let chunks = numbers.chunk(3)                      # [[1, 2, 3], [4, 5, 6], [7]]
```

### Dictionary Methods (v6.6)

#### keys() - 获取键列表

```bnf
keys_method ::= expression "." "keys" "(" ")"
```

```flow
let user = {name: "Alice", age: 30, city: "NYC"}
let keys = user.keys()                             # ["name", "age", "city"]
```

#### values() - 获取值列表

```bnf
values_method ::= expression "." "values" "(" ")"
```

```flow
let scores = {math: 95, english: 88, science: 92}
let values = scores.values()                       # [95, 88, 92]
```

#### entries() - 获取键值对

```bnf
entries_method ::= expression "." "entries" "(" ")"
```

```flow
let user = {name: "Alice", age: 30}
let entries = user.entries()                       # [["name", "Alice"], ["age", 30]]
```

### Global Utility Functions (v6.6)

#### zip() - 合并数组

```flow
let ids = [1, 2, 3]
let names = ["Alice", "Bob", "Charlie"]
let combined = zip(ids, names)                     # [[1, "Alice"], [2, "Bob"], [3, "Charlie"]]
```

#### sleep() - 暂停执行

```flow
log "Starting..."
sleep(2)                                           # 暂停 2 秒
log "Done!"
```

### 实战示例

```flow
# 数据转换管道
let users = [
    {name: "alice", age: 25, active: True},
    {name: "bob", age: 30, active: False},
    {name: "charlie", age: 35, active: True}
]

let activeUsers = users
    .filter(u => u.active)
    .map(u => u.name.capitalize())
    .join(", ")

log "Active users: {activeUsers}"                  # "Alice, Charlie"

# 数据格式化
let headers = ["ID", "Name", "Score"]
let row = [1, "Alice", 95]
let pairs = zip(headers, row)                      # [["ID", 1], ["Name", "Alice"], ["Score", 95]]

# 批量处理
let items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
let batches = items.chunk(3)

for batch in batches:
    log "Processing: {batch}"
    sleep(0.5)
```

---

## 18. 注释

```flow
# 单行注释

"""
多行注释
可以跨多行
"""
```

---

## 16. 完整示例

```flow
# 配置
const BASE_URL = "https://example.com"
const TEST_USER = "user@test.com"
const TEST_PASS = "password123"

# 步骤 1: 导航到登录页
step "导航到登录页" with diagnosis standard:
    navigate to BASE_URL + "/login"
    wait for element "#login-form"

    assert url contains "/login"
    assert "#login-form" exists
    assert "#login-form" visible

# 步骤 2: 填写表单
step "填写登录表单":
    select "#email"
    type TEST_USER

    select "#password"
    type TEST_PASS

    screenshot as "login-form-filled"

# 步骤 3: 提交登录
step "提交登录":
    click "#submit-button"
    wait for navigation

    assert url contains "/dashboard"
    assert ".welcome-message" exists

    extract text from ".username" into username
    log "登录成功，用户名: {username}"

# 步骤 4: 验证登录状态
step "验证登录状态":
    call "http.get" with
        url=BASE_URL + "/api/me",
        headers={"Authorization": "Bearer " + $context.token}
    into user_info

    if user_info.status_code == 200:
        log "用户信息: {JSON.stringify(user_info.data)}"
    else:
        log "获取用户信息失败"
```

---

## 17. 语法图例说明

```
::=     定义为
|       或
[ ]     可选
( )     分组
{ }     重复 0 次或多次
+       重复 1 次或多次
*       重复 0 次或多次
" "     字面量/关键字
```

---

**完整 EBNF 语法**: [DSL-GRAMMAR.ebnf](./DSL-GRAMMAR.ebnf)
**版本**: 6.6
**最后更新**: 2025-12-01
