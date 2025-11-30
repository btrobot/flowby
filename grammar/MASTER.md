# DSL Grammar Master Control Document

> **Version**: 5.1 ⭐ **Input Expression & Module System Support**
> **Status**: Active
> **Last Updated**: 2025-11-30
> **Purpose**: Single Source of Truth for DSL Grammar

---

## 🎯 Purpose

This document serves as the **authoritative grammar control** for the Flowby DSL. All implementation must conform to this specification.

**Key Principle**:
- ✅ **This document defines what IS implemented**
- ✅ **If it's not here, it's not supported**
- ✅ **Changes here require corresponding code changes**

---

## 🆕 v3.0 Major Changes

### Python-Style Block Structure

**v3.0 uses indentation-based blocks (like Python), removing all `end` keywords:**

```dsl
# ✅ v3.0 Syntax (Python-style)
step "登录":
    if user == "admin":
        navigate to "https://admin.example.com"
        log "Admin login"
```

```dsl
# ❌ v2.0 Syntax (REMOVED in v3.0)
step "登录":
    if user == "admin":
        navigate to "https://admin.example.com"
        log "Admin login"
    end if
end step
```

### Key v3.0 Features

1. **Indentation-Based Blocks**: 4 spaces per level (or 1 tab = 4 spaces)
2. **Python Literals**: `True`/`False`/`None` (not `True`/`False`/`None`)
3. **Optional Keywords**: Removed (v3.1+: `each` keyword deleted)
4. **Flexible Syntax**: Parameter order flexibility, optional keywords
5. **Token Changes**: `INDENT`/`DEDENT` tokens replace `END` token

---

## 📊 Grammar Feature Matrix

### Legend
- ✅ **Implemented & Tested** - Feature is fully working with tests
- ⚠️ **Implemented, Needs Tests** - Feature works but lacks test coverage
- 🚧 **Partially Implemented** - Feature is incomplete
- ❌ **Not Implemented** - Feature is planned but not coded
- 🗑️ **Deprecated** - Feature is being removed

---

## 1. Variable & Assignment (3 features)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 1.1 | Let Declaration | `let VAR = expr` | ✅ | v1.0 | `_parse_let_statement()` | ✅ | VR-VAR-003 checks current scope only |
| 1.2 | Const Declaration | `const VAR = expr` | ✅ | v1.0 | `_parse_const_statement()` | ✅ | VR-VAR-004 prevents modification |
| 1.3 | Assignment | `VAR = expr` | ✅ | v1.0 | `_parse_assignment()` | ✅ | VR-VAR-002 checks if defined |

**Test Coverage**: `tests/grammar_alignment/test_v3_01_variables.py` (504/508 passing)

**Examples**:
```dsl
# Variable declaration and assignment
let username = "alice"
let age = 25
const MAX_RETRIES = 3

# Assignment
username = "bob"
age = age + 1

# ERROR: Cannot reassign const
# MAX_RETRIES = 5  # VR-VAR-004 violation
```

---

## 2. Control Flow (7 features)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 2.1 | Step Block | `step "name" [with diagnosis LEVEL]:` | ✅ | v1.0/v3.0 | `_parse_step()` | ✅ | v3.0: no `end step` |
| 2.2 | If-Else | `if COND: ... [else: ...]` | ✅ | v1.0/v3.0 | `_parse_if()` | ✅ | v3.0: no `end if` |
| 2.3 | When-Otherwise | `when VAR: VAL1 \| VAL2: ... [otherwise: ...]` | ✅ | v1.0/v3.0/v3.1 | `_parse_when()` | ✅ | v3.0: switch/match semantics; **v3.1: OR pattern support** |
| 2.4 | For Loop | `for VAR[, VAR...] in EXPR:` | ✅ | v1.0/v3.0/v3.1/v4.0 | `_parse_for_each_loop()` | ✅ | v3.1: `each` removed; **v4.0: multi-var unpacking, enumerate()** |
| 2.5 | While Loop | `while COND:` | ✅ | v3.0 | `_parse_while_loop()` | ✅ | Condition-driven iteration |
| 2.6 | Break Statement | `break` | ✅ | v3.0 | `_parse_break()` | ✅ | Exit loop immediately |
| 2.7 | Continue Statement | `continue` | ✅ | v3.0 | `_parse_continue()` | ✅ | Skip to next iteration |

**Test Coverage**: `tests/grammar_alignment/test_v3_02_control_flow.py`

**v3.0 Block Structure**:
```dsl
# Step block with indentation
step "User Registration":
    navigate to "https://example.com/register"
    type username into "#username"
    type email into "#email"
    click "#submit"

# If-else block
if status == 200:
    log "Success"
else:
    log "Failed"

# Nested if blocks
if user_type == "admin":
    if has_permission:
        navigate to "/admin"
    else:
        log "Permission denied"
else:
    navigate to "/user"

# When block (switch/match semantics)
when response.status:
    200:
        log "OK"
    404:
        log "Not Found"
    500:
        log "Server Error"
    otherwise:
        log "Unknown status"

# When block with OR pattern (v3.1)
when http_status:
    200 | 201 | 204:
        log "Success response"
    400 | 401 | 403:
        log "Client error"
    500 | 502 | 503:
        log "Server error"
    otherwise:
        log "Unknown status"

# For loop (v3.0+: Python style, v4.0: multi-var unpacking)
for item in items:
    log item.name
    click item.selector

# v4.0: enumerate() with index
for index, item in enumerate(items):
    log f"{index}: {item.name}"

# v4.0: enumerate() with custom start
for num, user in enumerate(users, start=1):
    log f"User {num}: {user.email}"

# v4.0: multi-variable unpacking
let pairs = [[1, "apple"], [2, "banana"], [3, "cherry"]]
for key, value in pairs:
    log f"{key} = {value}"

# While loop (v3.0)
let count = 0
while count < 5:
    let temp = count * 2  # ✅ 每次迭代独立作用域
    log f"Iteration {count}, temp = {temp}"
    count = count + 1
# log temp  # ❌ temp 不存在（作用域已销毁）

# While with break
let retry = 0
while retry < 10:
    let result = check_status()
    if result.success:
        break
    retry = retry + 1
    wait 1

# While with continue
let i = 0
while i < 10:
    i = i + 1
    if i % 2 == 0:
        continue
    log f"Odd number: {i}"
```

**v3.0 Step Diagnosis** (New Feature):
```dsl
step "Critical Operation" with diagnosis detailed:
    # Detailed diagnostic logging for this step
    let result = api.process()
    assert result.success
```

Diagnosis levels: `minimal`, `simple`, `detailed`, `verbose`, `trace`, `debug`

---

## 3. Navigation (3 features)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 3.1 | Navigate To | `navigate to URL [wait for STATE]` | ✅ | v1.0/v3.0 | `_parse_navigate()` | ✅ | v3.0: full expression support |
| 3.2 | Go Back/Forward | `go back` / `go forward` | ✅ | v1.0 | `_parse_go()` | ✅ | Browser history |
| 3.3 | Reload | `reload` | ✅ | v1.0 | `_parse_reload()` | ✅ | Refresh page |

**Test Coverage**: `tests/grammar_alignment/test_v3_03_navigation.py`

**Page States**: `networkidle`, `domcontentloaded`, `load`

**v3.0 Examples**:
```dsl
# Basic navigation
navigate to "https://example.com"

# With page state
navigate to "https://example.com" wait for networkidle

# v3.0: Expression support (variables, member access, f-strings)
navigate to base_url
navigate to config.login_url
navigate to f"{base_url}/users/{user_id}"

# Browser navigation
go back
go forward
reload
```

---

## 4. Wait (3 forms)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 4.1 | Wait Duration | `wait [for] N [UNIT]` | ✅ | v1.0 | `_parse_wait()` | ✅ | Units: s, ms, seconds, milliseconds |
| 4.2 | Wait Element | `wait for element SEL [to be STATE] [timeout N]` | ✅ | v1.0 | `_parse_wait_for()` | ✅ | 4 element states |
| 4.3 | Wait Navigation | `wait for navigation [to URL] [wait for STATE] [timeout N]` | ✅ | v1.0 | `_parse_wait_for()` | ✅ | Navigation completion |

**Test Coverage**: `tests/grammar_alignment/test_v3_04_wait.py`

**Element States**: `visible`, `hidden`, `attached`, `detached`

**Examples**:
```dsl
# Wait duration
wait 2s
wait for 500ms
wait 1.5 seconds

# Wait for element
wait for element "#loading"
wait for element ".modal" to be visible
wait for element "#spinner" to be hidden timeout 5s

# Wait for navigation
wait for navigation
wait for navigation to "https://success.com"
wait for navigation wait for load timeout 10s

# Wait for page state
wait for networkidle
wait for domcontentloaded
wait for load

# Wait until condition
wait until page_loaded == True
wait until element_count > 0
```

---

## 5. Selection (2 features)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 5.1 | Select Element | `select TYPE [where COND and COND ...]` | ✅ | v1.0/v3.0/v3.1 | `_parse_select()` | ✅ | v3.0: operator support; **v3.1: string expression support** |
| 5.2 | Select Option | `select option VAL from SEL` | ✅ | v1.0 | `_parse_select_option()` | ✅ | Dropdown selection |

**Test Coverage**: `tests/grammar_alignment/test_v3_05_selection.py`

**v3.0 Where Operators**: `=`, `contains`, `equals`, `matches`

**Examples**:
```dsl
# Basic element selection
select input
select button
select "#submit"

# v3.0: Where clause with multiple operators
select input where type = "email"
select button where text contains "Submit"
select link where href equals "/login"
select div where class matches "^modal-"

# Multiple conditions
select input where type = "text" and name = "username"
select button where text contains "Save" and class contains "primary"

# v3.1: String expressions in WHERE clause (⭐ New)
# String concatenation
select input where id = "user-" + user_id
select button where data-id = prefix + "-" + suffix

# Arithmetic expressions → strings
select button where index = count + 1
select input where data-page = page_num * 2

# Member access
select input where name = config.field_name
select button where id = user.button_id

# Array access
select input where id = field_ids[0]
select button where class = button_classes[index]

# Complex expressions
select input where id = base + "-" + (index * 2) + suffix

# Select dropdown option
select option "United States" from "#country"
select option country_value from country_dropdown
```

---

## 6. Actions (10 features)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 6.1 | Type | `type EXPR [into SEL] [slowly\|fast]` | ✅ | v1.0/v3.0 | `_parse_type()` | ✅ | v3.0: into selector |
| 6.2 | Click | `click [SEL]` | ✅ | v1.0/v3.2 | `_parse_click()` | ✅ | v3.2: 完全表达式支持 |
| 6.3 | Double Click | `double click [SEL]` | ✅ | v1.0/v3.2 | `_parse_click_multiword()` | ✅ | v3.2: 完全表达式支持 |
| 6.4 | Right Click | `right click [SEL]` | ✅ | v1.0/v3.2 | `_parse_click_multiword()` | ✅ | v3.2: 完全表达式支持 |
| 6.5 | Hover | `hover [over] SEL` | ✅ | v1.0/v3.2 | `_parse_hover()` | ✅ | v3.2: 完全表达式支持 |
| 6.6 | Clear | `clear [SEL]` | ✅ | v1.0/v3.2 | `_parse_clear()` | ✅ | v3.2: 完全表达式支持 |
| 6.7 | Press | `press KEY` | ✅ | v1.0 | `_parse_press()` | ✅ | Keyboard keys |
| 6.8 | Scroll | `scroll to top\|bottom\|SEL\|PIXELS` | ✅ | v1.0/v3.0 | `_parse_scroll()` | ✅ | v3.0: flexible targets |
| 6.9 | Check/Uncheck | `check\|uncheck SEL` | ✅ | v1.0/v3.2 | `_parse_check()` | ✅ | v3.2: 完全表达式支持 |
| 6.10 | Upload | `upload file PATH to SEL` | ✅ | v1.0/v3.2 | `_parse_upload()` | ✅ | v3.2: 完全表达式支持 |

**Test Coverage**: `tests/grammar_alignment/test_v3_06_actions.py`

**v3.0 Examples**:
```dsl
# Type action
type "hello@example.com"
type username
type f"Welcome {user.name}"

# v3.0: Type into specific selector
type "password123" into "#password"
type credentials.password into password_field

# Type with modifiers
type slowly secret_code
type fast "quick text"

# Click actions
click
click "#submit"
click button_selector

# Double and right click
double click "#file"
right click ".context-menu-trigger"

# Hover
hover ".menu-item"
hover over dropdown_selector  # v3.0: 'over' optional

# Clear input
clear
clear "#search-box"  # v3.0: selector optional

# Press keys
press Enter
press Escape
press Tab

# Scroll
scroll to top
scroll to bottom
scroll to "#section"
scroll to 500  # v3.0: pixel value
scroll to target_element  # v3.0: variable

# Checkbox
check "#agree"
uncheck "#newsletter"

# File upload
upload file "/path/to/file.pdf" to "#file-input"
upload file file_path to upload_selector  # v3.0: expression support
```

**v3.2 Examples** (⭐ Unified Expression Support):
```dsl
# v3.2: Click with full expression support
click config.submit_button           # Member access
click buttons[0]                     # Array indexing
click f"#{id}-submit"                # f-string
click base + "-button"               # String concatenation

# v3.2: Double/Right click with expressions
double click menu_items[index]
right click user.context_selector

# v3.2: Hover with expressions
hover dropdown.selector
hover elements[active_index]
hover f".item-{item_id}"

# v3.2: Clear with expressions
clear config.search_input
clear inputs[0]
clear f"#{prefix}-search"

# v3.2: Check/Uncheck with expressions
check config.terms_checkbox
uncheck options[2]
check f"#agree-{user_id}"

# v3.2: Upload with expressions
upload file paths[0] to config.upload_input
upload file f"{base_dir}/file.pdf" to upload_selectors[index]
upload file user.file_path to f"#{id}-upload"
```

---

## 7. Assertions & Control Flow (5 types)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 7.1 | Assert Expression | `assert EXPR [, message_expr]` | ✅ | v2.0, v4.3+ | `_parse_assert()` | ✅ | General assertions; v4.3: message supports expressions |
| 7.2 | Assert URL | `assert url contains\|equals\|matches EXPR` | ✅ | v1.0 | `_parse_assert()` | ✅ | URL checks |
| 7.3 | Assert Element | `assert SEL exists\|visible\|hidden` | ✅ | v1.0 | `_parse_assert()` | ✅ | Element state |
| 7.4 | Assert Content | `assert SEL has text\|value\|attr EXPR` | ✅ | v1.0 | `_parse_assert()` | ✅ | Content checks |
| 7.5 | Exit Statement | `exit [code] [, "message"]` | ✅ | v4.1 | `_parse_exit()` | ✅ | Controlled termination (success/failure) |

**Test Coverage**:
- `tests/grammar_alignment/test_v3_07_assertions.py` (assertions)
- `tests/unit/test_exit_statement.py` (exit statement)

**Examples**:
```dsl
# v2.0+: General expression assertions
assert x > 5
assert user.age >= 18, "User must be adult"
assert status == 200, "API call failed"

# v4.3+: Dynamic error messages (expressions)
assert condition, error_msg                          # Variable message
assert is_valid, get_error_message()                 # Function call message
assert x > 0, "Value must be positive, got {x}"      # Auto-interpolation
assert x > 0, f"Value must be positive, got {x}"     # f-string (optional)

# Logical assertions
assert x > 5 and x < 10
assert status == 200 or status == 201
assert not error_occurred

# URL assertions
assert url contains "success"
assert url equals "https://example.com/dashboard"
assert url matches "^https://.*\\.com$"

# Element assertions
assert "#success-message" exists
assert ".loading-spinner" hidden
assert "#user-profile" visible

# Content assertions
assert "#welcome" has text "Welcome"
assert "#email" has value user_email
assert "a.download" has href "/downloads/file.pdf"

# Exit statement (v4.1)
exit                                   # Success exit (code=0)
exit 0                                 # Explicit success exit
exit 1                                 # Failure exit
exit "Processing failed"               # Failure with message (code=1)
exit 0, "Processing completed"         # Success with message

# Exit vs Assert
# Assert: Validates expectations (throws error on failure)
assert status == 200, "API call failed"

# Exit: Controlled termination (no exception)
if user_type == "guest":
    exit 0, "Guest users don't require processing"

if validation_failed:
    exit 1, "Validation errors detected"
```

---

## 8. Service Call (1 feature)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 8.1 | Service Call (Python-style) | `SERVICE.method(args)` | ✅ | v3.1 | `_parse_postfix()` | ✅ | **推荐用法**, v3.2+ 支持命名参数（使用 `_parse_method_arguments` 辅助方法） |

**Test Coverage**:
- v3.1: `tests/dsl/test_service_namespaces.py`
- v3.2: `tests/dsl/test_v3_2_kwargs.py`

**Built-in Service Namespaces**:
- `random`: Random data generation (`email`, `password`, `username`, `phone`, `number`, `uuid`)
- `http`: HTTP requests (`get`, `post`, `put`, `delete`, `patch`)

### v3.1+ Python-style Syntax (✅ Recommended)

**v3.1 - Positional Parameters**:
```dsl
# Basic service calls (positional parameters)
let email = random.email()
let password = random.password(16, True)  # length=16, special=True
let user_id = random.uuid()

# HTTP requests
let response = http.get("https://api.example.com/users")
let created = http.post(api_url, {name: "Alice", email: email})
```

**v3.2 - Named Parameters** (⭐ New):
```dsl
# Named parameters (more readable)
let password = random.password(length=16, special=True)
let response = http.get(url="https://api.example.com", timeout=10)

# Mixed parameters (positional first, then named)
let password = random.password(16, special=True)
let response = http.post("https://api.example.com", body={name: "Alice"}, timeout=10)

# Both syntaxes supported
let phone1 = random.phone("zh_CN")           # v3.1 positional
let phone2 = random.phone(locale="zh_CN")    # v3.2 named
```

**Expression Usage** (v3.1+):
```dsl
# Use in arrays
let users = [
    {email: random.email(), password: random.password(16, True)},
    {email: random.email(), password: random.password(16, True)}
]

# Use in string interpolation
log f"Generated email: {random.email()}"

# Python-style string method
let email = random.email()
let uppercase_email = email.upper()
```


---

## 9. Data Extraction (1 feature)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 9.1 | Extract | `extract TYPE from SEL [pattern REGEX] into VAR` | ✅ | v1.0/v3.0 | `_parse_extract_statement()` | ✅ | v3.0: flexible pattern position |

**Test Coverage**: `tests/grammar_alignment/test_v3_09_extraction.py`

**Extract Types**: `text`, `value`, `attr "name"`

**v3.0 Examples**:
```dsl
# Basic extraction
extract text from "#code" into code
extract value from "#email" into user_email
extract attr "href" from "a.download" into download_link

# v3.0: Pattern after selector (flexible position)
extract text from "#verification" pattern "\\d{6}" into code

# v2.0 style (still supported)
extract pattern "\\d{6}" from "#verification" into code

# Expression support
extract text from selector_var into result
extract attr href_attr from link_selector into url
```

---

## 10. Utilities (2 features)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 10.1 | Log | `log [LEVEL] EXPR` | ✅ | v1.0, v4.3+ | `_parse_log_statement()` | ✅ | String interpolation; v4.3+: log levels |
| 10.2 | Screenshot | `screenshot [PARAMS]` | ✅ | v1.0/v3.0 | `_parse_screenshot()` | ✅ | v3.0: flexible order |

**Test Coverage**: `tests/grammar_alignment/test_v3_10_utilities.py`

**v4.3+ Log Levels** (New):
```dsl
# 默认级别（向后兼容）
log "普通消息"                    # info 级别

# 显式级别（v4.3+）
log debug "调试信息"              # 🔍 调试信息
log info "普通信息"               # 普通信息
log success "操作成功"            # ✓ 成功消息
log warning "注意事项"            # ⚠ 警告消息
log error "发生错误"              # ✗ 错误消息

# 支持字符串插值和表达式
log success "用户 {user_name} 注册成功"      # ✅ 自动插值（推荐）
log success f"用户 {user_name} 注册成功"     # ✅ f-string（可选）
log error error_msg                        # ✅ 变量
log debug api_response.status              # ✅ 表达式
```

**Log Level Icons**:
- `debug`: 🔍 (调试信息)
- `info`: (无图标，默认级别)
- `success`: ✓ (成功消息)
- `warning`: ⚠ (警告消息)
- `error`: ✗ (错误消息)

**v3.0 Screenshot Syntax** (Flexible Parameter Order):
```dsl
# Basic screenshot
screenshot

# With name
screenshot as "homepage"

# With selector
screenshot of "#main-content"

# v3.0: Flexible parameter order
screenshot as "homepage" of "#main"
screenshot of ".modal" as "modal-view"

# Fullpage screenshot
screenshot fullpage as "full-page"
screenshot of "body" fullpage as "complete"

# Expression support
screenshot of selector_var as filename_var
```

**Log Examples**:
```dsl
# Simple log
log "Processing started"

# String interpolation
log f"User {username} logged in at {timestamp}"
log "Status: {response.status}, Body: {response.body}"

# Variable logging
log user_data
log response
```

---

## 11. REST API Integration (1 feature)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 11.1 | OpenAPI Resource Statement | `resource NAME from SPEC` or `resource NAME: ...` | ✅ | v4.2/v3.0 | `_parse_resource()` | ✅ | **Phase 1-5 实施完成**: OpenAPI 集成、认证、响应映射、弹性处理、Mock 模式; **v3.0: Python风格缩进，无`end resource`** |

**Test Coverage**:
- Phase 2 (Auth): `tests/unit/test_auth_handler.py` (24 tests)
- Phase 3 (Response): `tests/unit/test_response_handler.py` (39 tests)
- Phase 4 (Resilience): `tests/unit/test_retry_handler.py`, `test_circuit_breaker.py`, `test_resilience_handler.py` (47 tests)
- Phase 5 (Mock): `tests/unit/test_mock_handler.py` (26 tests)
- **Total**: 136 tests passing

**Documentation**:
- Examples: `examples/PHASE*-*.md`
- Proposal: `grammar/proposals/PROPOSAL-007-openapi-resource-statement.md`

---

### 11.1 OpenAPI Resource Statement

**Purpose**: 基于 OpenAPI 规范定义外部 REST API 资源，实现类型安全、自文档化的 API 集成。

#### 基本语法

```dsl
# 形式 1: 简单形式
resource user_api from "openapi/user-service.yml"

# 形式 2: 完整配置
resource user_api:
    spec: "openapi/user-service.yml"
    base_url: "https://api.example.com/v1"
    auth: {type: "bearer", token: ACCESS_TOKEN}
    timeout: 30
    headers: {"X-Client-ID": "dsl"}

    # Phase 3: Response mapping
    response_mapping: {
        field_mapping: {userId: "user_id"},
        exclude_fields: ["internal"]
    }
    validate_response: True

    # Phase 4: Resilience (retry + circuit breaker)
    resilience: {
        retry: {
            max_retries: 3,
            strategy: "exponential",
            base_delay: 1.0,
            jitter: True
        },
        circuit_breaker: {
            failure_threshold: 5,
            recovery_timeout: 60
        }
    }

    # Phase 5: Mock mode (for testing)
    mock: {
        enabled: False,
        responses: {
            getUser: {data: {id: 1, name: "Mock"}}
        },
        record_calls: True
    }

```

#### 基本使用（Phase 1）

```dsl
# Define resource
resource user_api from "openapi/user-service.yml"

# Call API operations (based on operationId in OpenAPI)
let user = user_api.getUser(userId=123)
log f"User: {user.name}, Email: {user.email}"

# POST request
let created = user_api.createUser(name="Alice", email="alice@example.com")

# Query parameters
let users = user_api.listUsers(page=1, limit=10)
```

#### Phase 2: 认证支持

支持多种认证方式:

```dsl
# Bearer Token
resource api1:
    spec: "api.yml"
    auth: {type: "bearer", token: env.API_TOKEN}


# API Key (header)
resource api2:
    spec: "api.yml"
    auth: {type: "apikey", key: "X-API-Key", value: "secret", location: "header"}


# API Key (query)
resource api3:
    spec: "api.yml"
    auth: {type: "apikey", key: "api_key", value: "secret", location: "query"}


# Basic Auth
resource api4:
    spec: "api.yml"
    auth: {type: "basic", username: "user", password: "pass"}


# OAuth2 Client Credentials
resource api5:
    spec: "api.yml"
    auth: {
        type: "oauth2",
        token_url: "https://oauth.example.com/token",
        client_id: "xxx",
        client_secret: "yyy"
    }

```

#### Phase 3: 响应映射和验证

自动验证和转换 API 响应:

```dsl
resource user_api:
    spec: "openapi/user-service.yml"

    # Response mapping
    response_mapping: {
        field_mapping: {
            userId: "user_id",        # Rename fields
            createdAt: "created_at"
        },
        exclude_fields: ["internal_id"],  # Exclude fields
        include_only: ["id", "name", "email"],  # Only include specified
        default_values: {status: "active"}  # Default values
    }

    # Validate response against OpenAPI schema
    validate_response: True


let user = user_api.getUser(userId=123)
# Response is automatically mapped and validated
assert user.user_id == 123  # userId → user_id
assert user.status == "active"  # Default value
```

#### Phase 4: 弹性处理（重试和断路器）

自动重试和断路器保护:

```dsl
resource unstable_api:
    spec: "api.yml"

    resilience: {
        # Retry strategy
        retry: {
            max_retries: 3,
            strategy: "exponential",  # exponential, fixed, linear
            base_delay: 1.0,
            max_delay: 30.0,
            multiplier: 2.0,
            jitter: True,
            retry_on_status: [429, 503, 504],
            only_idempotent: True  # Only retry GET/PUT/DELETE
        },

        # Circuit breaker
        circuit_breaker: {
            failure_threshold: 5,      # Open after 5 consecutive failures
            success_threshold: 2,      # Close after 2 consecutive successes
            recovery_timeout: 60,      # Try recovery after 60s
            window_size: 100,          # Sliding window size
            failure_rate_threshold: 0.5,  # Open if failure rate >= 50%

            # Fallback response when circuit is open
            fallback: {
                status: "degraded",
                message: "Service temporarily unavailable"
            }
        }
    }


# Automatic retry on failures
let user = unstable_api.getUser(userId=123)
# Will retry up to 3 times with exponential backoff

# Circuit breaker opens after threshold
# Subsequent requests fail fast without retry
```

#### Phase 5: Mock 模式（测试支持）

测试时使用 Mock 数据，无需真实 API:

```dsl
resource user_api:
    spec: "openapi/user-service.yml"

    mock: {
        enabled: True,        # Enable mock mode
        delay: 0.1,          # Simulate network delay

        responses: {
            # Static mock response
            getUser: {
                data: {id: 1, name: "Mock User", email: "mock@example.com"}
            },

            # Template with variables
            getUserById: {
                data: {
                    id: "{userId}",
                    name: "User {userId}",
                    email: "user{userId}@example.com"
                }
            },

            # Load from file
            listUsers: {
                file: "test/mocks/users.json"
            },

            # Callable function
            createUser: {
                data: lambda(**kwargs): {
                    "id": 999,
                    "name": kwargs.get("name"),
                    "email": kwargs.get("email"),
                    "created": True
                }
            }
        },

        # Simulate errors
        errors: {
            deleteUser: {
                status: 404,
                message: "User not found"
            }
        },

        # Record all calls for testing
        record_calls: True,

        # Base path for mock files
        base_path: "test/mocks/"
    }


# All calls return mock data, no real HTTP requests
let user = user_api.getUser(userId=123)
assert user.name == "Mock User"

# Template variables are replaced
let user2 = user_api.getUserById(userId=456)
assert user2.id == "456"
assert user2.email == "user456@example.com"

# Error simulation
try:
    user_api.deleteUser(userId=999)
catch error:
    log "Caught simulated 404 error"
```

#### Phase Implementation Summary

| Phase | Feature | Status | Tests | Commit |
|-------|---------|--------|-------|--------|
| **Phase 1** | OpenAPI 基础支持 | ✅ | Integrated | Initial |
| **Phase 2** | 认证（Bearer/APIKey/Basic/OAuth2） | ✅ | 24 tests | `49a5e52` |
| **Phase 3** | 响应映射与验证 | ✅ | 39 tests | `e340bf2` |
| **Phase 4** | 弹性处理（重试+断路器） | ✅ | 47 tests | `d0a9ff7` |
| **Phase 5** | Mock 模式（测试支持） | ✅ | 26 tests | `f76a6ac` |

**Total Tests**: 136 passing (100%)

#### OpenAPI Requirements

**Supported Versions**:
- OpenAPI 3.0.x ✅
- OpenAPI 3.1.x ✅ (planned)

**Required Fields**:
```yaml
openapi: 3.0.0
info:
  title: API Title
  version: 1.0.0
paths:
  /users/{userId}:
    get:
      operationId: getUser  # ✅ Required for method name
      parameters:
        - name: userId
          in: path
          required: True
          schema:
            type: integer
      responses:
        '200':
          description: Success
```

#### Error Handling

```dsl
resource api from "openapi/api.yml"

try:
    let user = api.getUser(userId=999)
catch error:
    # Handles:
    # - Missing required parameters
    # - HTTP errors (4xx/5xx)
    # - Network timeouts
    # - Response validation errors
    # - Circuit breaker open
    log f"API call failed: {error}"
```

#### Best Practices

1. **Use environment variables for secrets**:
   ```dsl
   resource api:
       spec: "api.yml"
       auth: {type: "bearer", token: env.API_TOKEN}  # Don't hardcode tokens
   
   ```

2. **Enable mock mode in tests**:
   ```dsl
   let is_test = env.TEST_MODE == "True"

   resource api:
       spec: "api.yml"
       mock: {
           enabled: is_test,
           responses: {getUser: {file: "test/mocks/user.json"}}
       }
   
   ```

3. **Configure resilience for production**:
   ```dsl
   resource prod_api:
       spec: "api.yml"
       resilience: {
           retry: {max_retries: 3, strategy: "exponential", jitter: True},
           circuit_breaker: {failure_threshold: 5, recovery_timeout: 60}
       }
   
   ```

4. **Use response mapping for consistency**:
   ```dsl
   resource api:
       spec: "api.yml"
       response_mapping: {
           field_mapping: {userId: "user_id"},  # Convert to snake_case
           default_values: {active: True}
       }
   
   ```

---

## 12. User-Defined Functions (v4.3) - 3 features

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 12.1 | Function Definition | `function NAME(PARAMS):` | ✅ | v4.3 | `_parse_function_def()` | ✅ | Python-style indentation, no `end function` |
| 12.2 | Return Statement | `return [EXPR]` | ✅ | v4.3 | `_parse_return_statement()` | ✅ | Only valid inside functions |
| 12.3 | Function Call | `NAME(ARGS)` | ✅ | v4.3 | `_parse_postfix()` | ✅ | Expression or standalone statement |

**Test Coverage**: `tests/dsl/test_v4_3_function.py` (25 tests, 100% passing)

**Documentation**:
- Example: `examples/flows/v4.3_functions_demo.flow`
- Proposal: `grammar/proposals/PROPOSAL-008-function-statement.md`
- EBNF: `docs/DSL-GRAMMAR.ebnf` Section 3.5

---

### 12.1 Function Definition

**Purpose**: 定义可重用的代码块，提升代码可读性和复用性

#### 基本语法

```dsl
# 无参数函数
function greet():
    log "Hello, World!"

# 带参数函数
function add(a, b):
    return a + b

# 带局部变量
function calculate_total(price, quantity, tax_rate):
    let subtotal = price * quantity
    let tax = subtotal * tax_rate
    let total = subtotal + tax
    return total
```

#### 函数调用

```dsl
# 调用无参函数
greet()

# 调用带参函数
let sum = add(10, 20)
let total = calculate_total(100, 3, 0.1)

# 函数调用作为表达式
if is_valid_email("user@example.com"):
    log "Email is valid"
```

#### 核心特性

**✅ 支持的功能**:
- **参数传递**: 支持多参数，按值传递（值拷贝）
- **返回值**: 使用 `return` 语句，可选返回值（默认 None）
- **局部作用域**: 函数内变量独立，不影响全局
- **全局常量访问**: 可读取 `const` 定义的全局常量
- **函数组合**: 可调用其他用户函数和内置函数
- **递归检测**: 运行时检测并拒绝递归调用

**❌ 不支持的功能** (设计决策):
- **递归**: 运行时检测并抛出错误（防止栈溢出）
- **闭包**: 无法访问外层函数的局部变量
- **默认参数**: 所有参数必需，无默认值
- **可变参数**: 参数数量固定
- **命名参数**: 仅支持位置参数

#### 作用域规则

```dsl
# 全局变量
let global_var = 10

# 全局常量
const MAX_VALUE = 100

function example():
    # 局部变量（独立作用域）
    let local_var = 20

    # 可以访问全局常量
    if local_var < MAX_VALUE:
        log "Within limit"

    # 不能修改全局变量
    # global_var = 30  # 会创建新的局部变量，不影响全局

# 函数外无法访问局部变量
# log local_var  # 错误: 未定义
```

#### 参数传递（按值）

```dsl
function double(n):
    n = n * 2  # 修改的是参数副本
    return n

let original = 5
let result = double(original)

log original  # 仍然是 5（未被修改）
log result    # 10
```

---

### 12.2 Return Statement

**Purpose**: 从函数中返回值并提前退出

#### 基本用法

```dsl
# 返回值
function add(a, b):
    return a + b

# 返回 None
function log_message(msg):
    log msg
    return

# 提前返回
function divide_safe(a, b):
    if b == 0:
        log "Error: Division by zero"
        return None
    return a / b
```

#### 控制流

```dsl
function validate_user(email, password):
    # 早期失败返回
    if not is_valid_email(email):
        return False

    if not is_strong_password(password):
        return False

    # 所有验证通过
    return True
```

#### 错误处理

- `return` 只能在函数内使用
- 在函数外使用 `return` 会抛出运行时错误
- 函数执行完毕但没有 `return`，默认返回 `None`

---

### 12.3 Function Call

**Purpose**: 调用用户定义的函数或内置函数

#### 作为表达式

```dsl
# 赋值语句中
let result = add(10, 20)
let area = calculate_area(5, 4)

# 条件语句中
if is_valid_email(user_email):
    log "Valid"

# 循环中
for item in items:
    process_item(item)

# 嵌套调用
let result = add(multiply(2, 3), 5)  # add(6, 5) = 11
```

#### 作为独立语句

```dsl
# 无需返回值的函数调用
greet()
log_message("Starting process")
validate_input(data)
```

#### 函数组合

```dsl
# 调用内置函数
function get_string_length(text):
    return len(text)

# 调用其他用户函数
function validate_credentials(email, password):
    if not is_valid_email(email):
        return False
    if not is_strong_password(password):
        return False
    return True

# 多层组合
function check_and_process(data):
    if validate_data(data):
        return process_data(data)
    return None
```

---

### 实战示例

#### 示例 1: 表单验证

```dsl
# 定义验证函数
function is_valid_email(email):
    return email contains "@" and email contains "."

function is_strong_password(password):
    return len(password) >= 8

function validate_form(email, password):
    if not is_valid_email(email):
        log "Invalid email format"
        return False

    if not is_strong_password(password):
        log "Password too weak"
        return False

    return True

# 使用验证函数
let user_email = "user@example.com"
let user_password = "secret123"

if validate_form(user_email, user_password):
    log "Form validation passed"
else:
    log "Form validation failed"
```

#### 示例 2: 数组处理

```dsl
# 数组统计函数
function sum_array(numbers):
    let total = 0
    for num in numbers:
        total = total + num
    return total

function find_max(numbers):
    let max_value = numbers[0]
    for num in numbers:
        if num > max_value:
            max_value = num
    return max_value

function calculate_average(numbers):
    let total = sum_array(numbers)
    return total / len(numbers)

# 使用
let scores = [85, 92, 78, 95, 88]
log "Total: {sum_array(scores)}"
log "Max: {find_max(scores)}"
log "Average: {calculate_average(scores)}"
```

#### 示例 3: 业务逻辑封装

```dsl
# 电商订单计算
function calculate_subtotal(price, quantity):
    return price * quantity

function calculate_tax(subtotal, rate):
    return subtotal * rate

function apply_discount(total, discount_rate):
    return total * (1 - discount_rate)

function calculate_order_total(price, quantity, tax_rate, has_discount):
    let subtotal = calculate_subtotal(price, quantity)
    let tax = calculate_tax(subtotal, tax_rate)
    let total = subtotal + tax

    if has_discount:
        total = apply_discount(total, 0.15)

    return total

# 计算订单
let order_total = calculate_order_total(100, 3, 0.1, True)
log "Order total: ${order_total}"
```

---

### 最佳实践

1. **函数命名**: 使用动词开头的描述性名称
   - ✅ `validate_email()`, `calculate_total()`, `process_data()`
   - ❌ `email()`, `total()`, `data()`

2. **保持简洁**: 每个函数专注于单一职责
   - ✅ 函数长度 ≤ 20 行
   - ❌ 超过 50 行的复杂函数

3. **避免深层嵌套**: 函数调用链保持简单
   - ✅ 调用深度 ≤ 3 层
   - ❌ 超过 5 层的嵌套调用

4. **参数数量**: 保持参数列表简洁
   - ✅ 参数数量 ≤ 4 个
   - ❌ 超过 5 个参数

5. **使用提前返回**: 优先处理错误情况
   ```dsl
   function process(data):
       if not data:
           return None  # 提前返回

       # 主逻辑
       return process_valid_data(data)
   ```

---

### 错误处理

**常见错误**:

1. **递归调用**:
   ```dsl
   function factorial(n):
       if n <= 1:
           return 1
       return n * factorial(n - 1)  # ❌ 运行时错误: 不支持递归
   ```

2. **return 在函数外**:
   ```dsl
   let x = 10
   return x  # ❌ 错误: return 只能在函数内使用
   ```

3. **参数数量不匹配**:
   ```dsl
   function add(a, b):
       return a + b

   let result = add(10)  # ❌ 错误: 需要 2 个参数，提供了 1 个
   ```

4. **调用未定义函数**:
   ```dsl
   let result = unknown_function()  # ❌ 错误: 未定义的函数
   ```

---

### 性能考虑

- **函数调用开销**: 极小，不影响性能
- **参数传递**: 按值传递，简单类型（数字、字符串）开销很小
- **作用域管理**: 使用栈结构，高效
- **建议**: 对于简单操作，内联代码和函数调用性能相当

---


## 13. Module System (v5.0) - 4 features

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 13.1 | Library Declaration | `library NAME` | ✅ | v5.0 | `_parse_library_declaration()` | ✅ | 库文件声明,必须在文件首行 |
| 13.2 | Export Statement | `export const VAR = expr` / `export function NAME(...)` | ✅ | v5.0 | `_parse_export_statement()` | ✅ | 显式导出常量或函数 |
| 13.3 | Import Statement | `import ALIAS from "PATH"` / `from "PATH" import NAME, ...` | ✅ | v5.0 | `_parse_import_statement()` | ✅ | 模块导入,支持两种语法 |
| 13.4 | Member Access | `module.member` | ✅ | v5.0 | `_parse_postfix()` | ✅ | 访问模块成员 |

**Test Coverage**:
- Unit Tests: Lexer (19/19), Parser (24/24), Core (29/36)
- Integration Tests: 9/10 (90%)
- Examples: `examples/module_system/`

**Documentation**:
- Proposal: `grammar/proposals/PROPOSAL-009-library-system.md`

---

### 13.1 Library Declaration

**Purpose**: 声明库文件,实现模块化代码复用和命名空间隔离

#### 基本语法

**库文件定义**:
```dsl
# 文件: libs/logging.flow
library logging

# 导出的公共 API
export const LOG_LEVEL_DEBUG = "debug"

export function log_phase_start(phase_num, phase_name):
    log info "阶段 [{phase_num}]: {phase_name}"
    log info "--------------------------------------------------"

# 私有辅助函数(不导出)
function _get_timestamp():
    return "2025-11-29"
```

#### 核心特性

**✅ 库文件约束**:
- library 声明必须在文件首行(注释和空行除外)
- 只能包含 const 定义和 function 定义
- 不能包含可执行语句(step, log, wait, navigate, click 等)
- library 名称建议与文件名匹配

**❌ 禁止的语句**:
```dsl
library bad_lib

# ❌ 禁止: 可执行语句
log "This is not allowed"
wait 1 s
navigate to "..."

# ❌ 禁止: step 语句
step "test":
    click "#button"
```

---

### 13.2 Export Statement

**Purpose**: 显式标记导出的常量和函数,控制库的公共 API

#### 基本语法

```dsl
library utils

# 导出常量
export const VERSION = "1.0.0"
export const MAX_RETRIES = 3

# 导出函数
export function validate_email(email):
    return email contains "@" and email contains "."

export function format_date(timestamp):
    return Date.format("%Y-%m-%d")

# 私有函数(不导出)
function _internal_helper():
    return 42
```

#### 可见性规则

- **export 的成员**: 对外可见,可被其他文件导入
- **未 export 的成员**: 仅库内部可见,外部无法访问

---

### 13.3 Import Statement

**Purpose**: 导入其他库的导出成员,实现代码复用

#### 语法 1: 模块导入

```dsl
# 导入整个模块
import logging from "libs/logging.flow"

# 使用模块成员(带命名空间前缀)
logging.log_phase_start(1, "数据准备")
logging.log_phase_end(1, "数据准备")
```

#### 语法 2: From-Import

```dsl
# 导入特定成员
from "libs/logging.flow" import log_phase_start, log_phase_end

# 直接使用(无命名空间前缀)
log_phase_start(1, "数据准备")
log_phase_end(1, "数据准备")
```

#### 路径解析规则

- **相对路径**: 基于当前文件所在目录
  - `import logging from "libs/logging.flow"` - 当前目录的 libs/ 子目录
  - `import utils from "../common/utils.flow"` - 父目录的 common/ 子目录
- **不支持绝对路径**: 出于安全考虑

---

### 13.4 Member Access Expression

**Purpose**: 访问模块对象的导出成员

#### 基本用法

```dsl
# 导入模块
import logging from "libs/logging.flow"
import validation from "libs/validation.flow"

# 成员访问
logging.log_phase_start(1, "测试")
validation.validate_email("test@example.com")

# 嵌套访问(如果模块导出对象)
let value = config.api.base_url
```

---

### 实战示例

#### 示例 1: 优化大型 Flow 文件

**优化前 (600+ 行)**:
```dsl
# factory_ai_registration.flow - 600+ 行
function log_phase_start(phase_num, phase_name):
    log info "阶段 [{phase_num}]: {phase_name}"

function validate_not_empty(field_name, value):
    if value == "":
        exit 1, "验证失败: {field_name} 不能为空"

# ... 20+ 个工具函数

# ... 400+ 行业务逻辑
step "阶段 1":
    log_phase_start(1, "数据准备")
    # ...
```

**优化后 (模块化)**:
```dsl
# libs/logging.flow (30 行)
library logging

export function log_phase_start(phase_num, phase_name):
    log info "阶段 [{phase_num}]: {phase_name}"
    log info "--------------------------------------------------"

export function log_phase_end(phase_num, phase_name):
    log success "阶段 [{phase_num}] 完成: {phase_name}"

# libs/validation.flow (40 行)
library validation

export function validate_not_empty(field_name, value):
    if value == "":
        exit 1, "验证失败: {field_name} 不能为空"

export function validate_email(email):
    if not email contains "@":
        exit 1, "邮箱格式不正确"

# factory_ai_registration.flow (100 行)
import logging from "libs/logging.flow"
from "libs/validation.flow" import validate_not_empty, validate_email

# 业务逻辑清晰可读
step "阶段 1: 数据准备":
    logging.log_phase_start(1, "数据准备")

    let email = "test@example.com"
    validate_email(email)

    logging.log_phase_end(1, "数据准备")
```

#### 示例 2: 跨项目复用

**通用工具库**:
```dsl
# common/libs/random_utils.flow
library random_utils

export function generate_random_email():
    let timestamp = Date.now()
    return f"test_{timestamp}@example.com"

export function generate_random_phone():
    let num = Math.floor(Math.random() * 90000000) + 10000000
    return f"138{num}"
```

**多个项目使用**:
```dsl
# project1/flows/registration.flow
import random_utils from "../common/libs/random_utils.flow"

let email = random_utils.generate_random_email()
let phone = random_utils.generate_random_phone()

# project2/flows/user_creation.flow
from "../common/libs/random_utils.flow" import generate_random_email

let new_user_email = generate_random_email()
```

---

### 模块加载机制

#### 模块缓存

- 每个库文件在同一次执行中只加载一次
- 使用绝对路径作为缓存键
- 后续 import 直接返回缓存的模块对象

#### 循环导入检测

**检测机制**: 维护导入栈,检测循环依赖

```dsl
# libs/a.flow
library a
import b from "b.flow"  # 导入 b

# libs/b.flow
library b
import a from "a.flow"  # 导入 a -> 检测到循环依赖

# 错误信息:
# [ERROR] 循环导入检测:
#   a.flow -> b.flow -> a.flow
#   不允许循环依赖
```

---

### 最佳实践

1. **库文件组织**:
   - 按功能分类: `libs/logging.flow`, `libs/validation.flow`, `libs/random_utils.flow`
   - 保持库文件简洁: 每个库 ≤ 50 行

2. **导出原则**:
   - 只导出公共 API
   - 私有函数用 `_` 前缀命名(约定)

3. **导入风格**:
   - 工具模块: 使用 `import alias` 保持命名空间
   - 频繁使用的函数: 使用 `from...import` 简化调用

4. **路径管理**:
   - 统一使用相对路径
   - 避免深层嵌套 (`../../..` 超过 2 层)

---

### 错误处理

| 错误情况 | 错误类型 | 示例 |
|---------|---------|------|
| 库文件不存在 | FileNotFoundError | `import foo from "libs/missing.flow"` |
| library 名称不匹配 | LibraryNameMismatchError | 文件名 `a.flow` 但声明 `library b` |
| 导入未导出成员 | ImportError | `from "lib.flow" import private_func` |
| 库文件包含可执行语句 | LibraryConstraintViolation | library 文件中包含 `log`, `step` |
| 循环导入 | CircularImportError | A → B → A |
| 重复导入相同名称 | NameConflictError | `import a; import a` |

---

### 实现状态

**当前状态**: ❌ Not Implemented (提案阶段)

**实施计划**:
1. Phase 1: Lexer (0.5 天) - 添加 LIBRARY, EXPORT, IMPORT, FROM, DOT tokens
2. Phase 2: Parser (2-3 天) - 实现解析方法和 AST 节点
3. Phase 3: Module System (4-5 天) - ModuleLoader, 路径解析, 缓存, 循环检测
4. Phase 4: Interpreter (2-3 天) - 执行 import, 成员访问
5. Phase 5: Testing (2-3 天) - 单元测试和集成测试
6. Phase 6: Documentation (2-3 天) - 更新所有文档

**预计工期**: 14-20 天 (3-4 周)

---


## 14. Input Expression (v5.1) - 1 feature

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 14.1 | Input Expression | `input(PROMPT [, default=VAL] [, type=TYPE])` | ✅ | v5.1 | `_parse_input_expression()` | ✅ | 交互式控制台输入，支持默认值和类型转换 |

**Test Coverage**: `tests/dsl/test_input_statement.py` (21/21 passing)

**语法说明**:
```dsl
# 基本输入
let name = input("请输入姓名: ")

# 带默认值（CI/CD 友好）
let email = input("邮箱: ", default="test@example.com")

# 指定类型（自动转换）
let age = input("年龄: ", type=integer)
let price = input("价格: ", type=float)

# 密码输入（不回显）
let password = input("密码: ", type=password)

# 组合使用
let count = input("数量: ", default="10", type=integer)
```

**参数说明**:

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `PROMPT` | String/Expression | ✅ | - | 提示文本，可以是字符串或表达式 |
| `default` | Any/Expression | ❌ | `None` | 默认值，空输入时使用 |
| `type` | Keyword | ❌ | `text` | 输入类型：`text`, `password`, `integer`, `float` |

**类型转换**:

| Type | 行为 | 示例 | 结果 |
|------|------|------|------|
| `text` | 保持字符串 | `input("名称: ")` → 输入 "Alice" | `"Alice"` |
| `password` | 隐藏输入 (getpass) | `input("密码: ", type=password)` | 输入不回显 |
| `integer` | 转换为整数 | `input("年龄: ", type=integer)` → 输入 "25" | `25` (int) |
| `float` | 转换为浮点数 | `input("价格: ", type=float)` → 输入 "99.99" | `99.99` (float) |

---

### 使用场景

#### 场景 1: 调试与人工干预
```dsl
step "填写注册表单" with diagnosis minimal:
    fill "#email" with "test@example.com"
    fill "#password" with "secret123"

    # 人工确认表单填写是否正确
    let confirmed = input("请确认表单是否正确 (y/n): ")
    if confirmed == "y":
        click "#submit"
    else:
        log error "用户取消操作"
        exit
```

#### 场景 2: 动态参数输入
```dsl
# 测试时手动输入测试数据
let username = input("测试用户名: ", default="testuser")
let password = input("测试密码: ", type=password)

step "登录":
    fill "#username" with username
    fill "#password" with password
    click "#login"
```

#### 场景 3: 环境选择
```dsl
# 运行时选择环境
let env = input("请选择环境 (dev/staging/prod): ", default="dev")

when env:
    "dev":
        let base_url = "https://dev.example.com"
    "staging":
        let base_url = "https://staging.example.com"
    "prod":
        let base_url = "https://example.com"

goto base_url
```

#### 场景 4: 验证码处理
```dsl
step "获取验证码":
    click "#send_code"
    wait 2s

    # 需要人工输入验证码
    let code = input("请输入收到的验证码: ")
    fill "#code" with code
    click "#verify"
```

#### 场景 5: 批量数据输入
```dsl
function create_users():
    for i in range(1, 6):
        # 每次循环手动输入用户信息
        let name = input(f"用户 {i} 姓名: ", default=f"User{i}")
        let age = input(f"用户 {i} 年龄: ", default="25", type=integer)

        # 创建用户...
        log f"创建用户: {name}, 年龄: {age}"
```

---

### 交互模式 vs CI/CD 模式

**交互模式** (默认 `is_interactive=True`):
- 从控制台读取用户输入
- 适用于本地调试、手动测试

**非交互模式** (`is_interactive=False`):
- 必须提供 `default` 参数
- 自动使用默认值，不暂停等待输入
- 适用于 CI/CD 环境

```python
# 设置非交互模式（CI/CD）
from registration_system.dsl.context import ExecutionContext

context = ExecutionContext(
    task_id="...",
    is_interactive=False  # 非交互模式
)
```

**DSL 代码兼容性**:
```dsl
# CI/CD 友好：提供默认值
let username = input("用户名: ", default="ci_user")  # ✅ CI/CD可用
let password = input("密码: ", default="ci_pass", type=password)  # ✅ CI/CD可用

# 仅交互模式：无默认值
let code = input("验证码: ")  # ❌ CI/CD会报错
```

---

### 最佳实践

1. **始终提供默认值（CI/CD兼容性）**:
   ```dsl
   # ✅ 推荐：提供默认值
   let env = input("环境: ", default="dev")

   # ❌ 避免：无默认值（CI/CD 不可用）
   let env = input("环境: ")
   ```

2. **使用类型转换确保数据正确性**:
   ```dsl
   # ✅ 推荐：指定类型
   let retry_count = input("重试次数: ", default="3", type=integer)

   # ❌ 避免：字符串手动转换
   let retry_count = Number(input("重试次数: ", default="3"))
   ```

3. **密码输入使用 password 类型**:
   ```dsl
   # ✅ 推荐：密码不回显
   let pwd = input("密码: ", type=password)

   # ❌ 避免：明文显示密码
   let pwd = input("密码: ")
   ```

4. **提示文本清晰明确**:
   ```dsl
   # ✅ 推荐：清晰的提示
   let count = input("请输入要创建的用户数量 (1-100): ", default="10", type=integer)

   # ❌ 避免：模糊的提示
   let count = input("数量: ", type=integer)
   ```

5. **使用动态提示文本**:
   ```dsl
   # ✅ 推荐：提示可以是表达式
   let max_value = 100
   let num = input(f"请输入数字 (最大{max_value}): ", default="50", type=integer)
   ```

---

### 错误处理

| 错误情况 | 错误类型 | 示例 | 解决方案 |
|---------|---------|------|----------|
| 非交互模式无默认值 | ExecutionError | `input("Name: ")` 在 CI/CD | 添加 `default` 参数 |
| 类型转换失败 | ExecutionError | 输入 "abc" 但 `type=integer` | 输入有效数字或捕获异常 |
| 用户中断输入 | ExecutionError | Ctrl+C 终止输入 | 程序抛出异常并退出 |
| 无效类型参数 | ParserError | `type=invalid_type` | 使用有效类型: text, password, integer, float |

**异常示例**:
```dsl
# 示例 1: 类型转换失败
let age = input("年龄: ", type=integer)
# 输入 "abc" -> ExecutionError: 无法将输入 'abc' 转换为 integer

# 示例 2: 非交互模式缺少默认值
let name = input("姓名: ")
# CI/CD环境 -> ExecutionError: input() 需要交互模式，请提供 default 参数
```

---

### 实现状态

**当前状态**: ✅ Fully Implemented (v5.1)

**实现组件**:
- ✅ Lexer: INPUT token (复用已有)
- ✅ AST: InputExpression 节点
- ✅ Parser: `_parse_input_expression()` 方法
- ✅ Evaluator: `_eval_input()` 方法
- ✅ Context: `is_interactive` 属性
- ✅ Tests: 21/21 passing

**Feature ID**: DSL-INPUT-001

---


## 📈 Expression System

### Operator Precedence (9 levels)

| Level | Operators | Associativity | Since | Parser Method |
|-------|-----------|---------------|-------|---------------|
| 1 (Low) | `or` | Left | v1.0 | `_parse_logical_or()` |
| 2 | `and` | Left | v1.0 | `_parse_logical_and()` |
| 3 | `not` | Right | v1.0 | `_parse_logical_not()` |
| 4 | `==`, `!=`, `>`, `<`, `>=`, `<=`, `contains`, `matches`, `equals` | Left | v1.0/v3.0 | `_parse_comparison()` |
| 5 | `+`, `-` | Left | v1.0 | `_parse_additive()` |
| 6 | `*`, `/`, `//`, `%` | Left | v1.0/v4.0 | `_parse_multiplicative()` |
| 6.5 | `**` | Right | v4.0 | `_parse_power()` |
| 7 | Unary `-`, `not` | Right | v1.0 | `_parse_unary()` |
| 8 | `.`, `[]`, `()` | Left | v1.0 | `_parse_postfix()` |
| 9 (High) | Literals, Variables | - | v1.0 | `_parse_primary()` |

**Test Coverage**: `tests/grammar_alignment/test_v3_expressions.py`

**Examples**:
```dsl
# Arithmetic
let result = (a + b) * c / d
let remainder = x % 10

# Comparison
let is_valid = age >= 18 and age < 65
let found = text contains "error"
let matches = email matches "^[a-z]+@[a-z]+\\.[a-z]+$"

# Logical
let can_proceed = is_authenticated and has_permission or is_admin
let should_retry = not success and retry_count < 3

# Member access
let username = user.profile.name
let first_item = items[0]
let last_item = items[len(items) - 1]

# Method calls
let upper = text.toUpper()
let rounded = Math.round(value)
let formatted = Date.format("%Y-%m-%d")
```

---

## 🎨 Data Types

| Type | Syntax | Examples | Since | Status | Notes |
|------|--------|----------|-------|--------|-------|
| String | `"text"`, `'text'` | `"Hello"`, `'World'` | v1.0 | ✅ | Single or double quotes |
| String Interpolation | `"text {expr}"` | `"User: {name}"` | v2.0 | ✅ | Auto-interpolation (recommended) |
| F-String | `f"text {expr}"` | `f"Count: {x + 1}"` | v3.0 | ✅ | Optional f-prefix (Python-style) |
| Integer | `123`, `0`, `-10` | `5`, `999` | v4.0 | ✅ | Whole numbers without decimal point (v4.0: type-aware arithmetic) |
| Number (Float) | `3.14`, `0.5` | `-10.5`, `2.0` | v1.0 | ✅ | Floating-point numbers |
| Boolean | `True`, `False` | - | v1.0/v3.0 | ✅ | v3.0: Python-style (capitalized) |
| None | `None` | - | v1.0/v3.0 | ✅ | v3.0: Python-style (capitalized) |
| Array | `[expr, ...]` | `[1, 2, 3]`, `["a", "b"]` | v1.0 | ✅ | Comma-separated |
| Object | `{key: val, ...}` | `{name: "Alice", age: 25}` | v1.0 | ✅ | Key-value pairs |

**Test Coverage**: `tests/grammar_alignment/test_v3_data_types.py`

**String Interpolation (v2.0+)**:

DSL 支持自动字符串插值，`f` 前缀是可选的：

```dsl
# 自动插值（推荐，更简洁）
log "User: {name}"                       # ✅ 自动识别 { } 插值
log "Count: {count + 5}"                 # ✅ 支持表达式
log success "用户 {name} 注册成功"        # ✅ 带级别

# f-string（可选，与 Python 风格一致）
log f"User: {name}"                      # ✅ 功能完全等效
log f"Count: {count + 5}"                # ✅ 功能完全等效
log success f"用户 {name} 注册成功"       # ✅ 功能完全等效

# 两种语法完全等效，选择您喜欢的风格即可
```

**v4.0 Integer Type & Type Promotion Rules**:

The DSL now distinguishes between integers and floating-point numbers with Python-style type promotion:

| Operation | Type Rules | Result Type | Examples |
|-----------|------------|-------------|----------|
| `int OP int` | Preserves integer | `int` | `5 + 3` → `8` (int), `10 - 2` → `8` (int) |
| `int OP float` | Promotes to float | `float` | `5 + 2.0` → `7.0` (float) |
| `float OP int` | Promotes to float | `float` | `3.5 * 2` → `7.0` (float) |
| `int / int` | **Always float** | `float` | `5 / 2` → `2.5` (float), `6 / 3` → `2.0` (float) |
| `int // int` | Floor division | `int` | `5 // 2` → `2` (int) |
| `int % int` | Modulo | `int` | `7 % 3` → `1` (int) |
| `int ** int` | Power (smart) | `int`/`float` | `2 ** 3` → `8` (int), `2 ** -1` → `0.5` (float) |

**String Interpolation (v4.0)**:
- Integers format without decimal point: `f"{5}"` → `"5"`
- Floats preserve decimal point: `f"{5.0}"` → `"5.0"`, `f"{3.14}"` → `"3.14"`
- Critical for CSS selectors: `f".item-{index}"` where `index=0` → `".item-0"` (not `".item-0.0"`)

**Type Conversion Functions (v4.0)**:
- `int(x)`: Convert to integer (truncates floats, parses strings)
- `float(x)`: Convert to float
- `len(x)`: Returns integer (v4.0: was float in v3.x)
- `range(n)`: Returns list of integers (v4.0: was floats in v3.x)

**v3.0 Literal Changes**:
```dsl
# ✅ v3.0 Python-style literals
let is_active = True
let is_disabled = False
let result = None

# ❌ v2.0 style (will cause LexerError in v3.0)
# let is_active = True   # Error: use True
# let is_disabled = False # Error: use False
# let result = None       # Error: use None
```

**Examples**:
```dsl
# Strings
let name = "Alice"
let message = 'Hello World'

# F-strings (v3.0)
let greeting = f"Hello {name}!"
let url = f"{base_url}/users/{user_id}"

# String interpolation (v2.0+)
let info = "User {name} is {age} years old"

# Numbers
let age = 25
let pi = 3.14159
let negative = -10

# Booleans (v3.0: Python-style)
let is_admin = True
let has_errors = False

# None (v3.0: Python-style)
let optional_value = None

# Arrays
let numbers = [1, 2, 3, 4, 5]
let names = ["Alice", "Bob", "Charlie"]
let mixed = [1, "two", True, None]
let nested = [[1, 2], [3, 4]]

# Objects
let user = {name: "Alice", age: 25, active: True}
let config = {
    base_url: "https://api.example.com",
    timeout: 5000,
    retries: 3
}
```

---

## 🔧 System Variables (5 namespaces)

> **v3.0**: System variables are accessed as built-in global objects without `$` prefix

| Namespace | Properties | Example | Since | Status |
|-----------|-----------|---------|-------|--------|
| `context` | `task_id`, `execution_id`, `start_time`, `step_name`, `status` | `context.task_id` | v3.0 | ✅ |
| `page` | `url`, `title`, `origin` | `page.url` | v3.0 | ✅ |
| `browser` | `name`, `version` | `browser.name` | v3.0 | ✅ |
| `env` | Any environment variable | `env.API_KEY` | v3.0 | ✅ |
| `config` | Any config key | `config.base_url` | v3.0 | ✅ |

**Reserved Words**: System namespace names (`page`, `context`, `browser`, `env`, `config`) cannot be used as variable names.

**Test Coverage**: `tests/grammar_alignment/test_v3_system_variables.py`

**Examples**:
```dsl
# Context variables (v3.0 syntax)
log f"Task ID: {context.task_id}"
log f"Executing step: {context.step_name}"

# Page variables
assert url equals page.url
log f"Page title: {page.title}"

# Browser variables
log f"Browser: {browser.name} {browser.version}"

# Environment variables
let api_key = env.API_KEY
let db_host = env.DATABASE_HOST

# Config variables
navigate to config.base_url
let timeout = config.request_timeout
```

---

## 📚 Built-in Functions

### Math Namespace (9 functions)

| Function | Since | Status | Test |
|----------|-------|--------|------|
| `Math.abs(x)` | v2.0 | ✅ | ✅ |
| `Math.round(x)` | v2.0 | ✅ | ✅ |
| `Math.ceil(x)` | v2.0 | ✅ | ✅ |
| `Math.floor(x)` | v2.0 | ✅ | ✅ |
| `Math.max(...args)` | v2.0 | ✅ | ✅ |
| `Math.min(...args)` | v2.0 | ✅ | ✅ |
| `Math.random()` | v2.0 | ✅ | ✅ |
| `Math.pow(base, exp)` | v2.0 | ✅ | ✅ |
| `Math.sqrt(x)` | v2.0 | ✅ | ✅ |

### Date Namespace (3 functions)

| Function | Since | Status | Test |
|----------|-------|--------|------|
| `Date.now()` | v2.0 | ✅ | ✅ |
| `Date.format(fmt)` | v2.0 | ✅ | ✅ |
| `Date.from_timestamp(ts)` | v2.0 | ✅ | ✅ |

### JSON Namespace (2 functions)

| Function | Since | Status | Test |
|----------|-------|--------|------|
| `JSON.stringify(obj)` | v2.0 | ✅ | ✅ |
| `JSON.parse(str)` | v2.0 | ✅ | ✅ |

### Global Functions (5 functions)

| Function | Since | Status | Test |
|----------|-------|--------|------|
| `Number(value)` | v2.0 | ✅ | ✅ |
| `String(value)` | v2.0 | ✅ | ✅ |
| `Boolean(value)` | v2.0 | ✅ | ✅ |
| `isNaN(value)` | v2.0 | ✅ | ✅ |
| `isFinite(value)` | v2.0 | ✅ | ✅ |

**Test Coverage**: `tests/grammar_alignment/test_v3_builtin_functions.py`

**Examples**:
```dsl
# Math functions
let absolute = Math.abs(-10)           # 10
let rounded = Math.round(3.7)          # 4
let ceiling = Math.ceil(3.2)           # 4
let floored = Math.floor(3.9)          # 3
let maximum = Math.max(10, 20, 5)      # 20
let minimum = Math.min(10, 20, 5)      # 5
let random = Math.random()             # 0.0-1.0
let power = Math.pow(2, 3)             # 8
let root = Math.sqrt(16)               # 4

# Date functions
let timestamp = Date.now()
let formatted = Date.format("%Y-%m-%d")
let from_ts = Date.from_timestamp(1234567890)

# JSON functions
let json_string = JSON.stringify({name: "Alice"})
let parsed = JSON.parse('{"name": "Bob"}')

# Type conversion
let num = Number("123")
let str = String(456)
let bool = Boolean(1)
let is_nan = isNaN("abc")
let is_finite = isFinite(100)
```

---

## 📝 Comments

| Feature | Syntax | Status | Since |
|---------|--------|--------|-------|
| Line Comment | `# comment` | ✅ | v1.0 |
| Block Comment | `""" ... """` | ✅ | v3.0 |

**Examples**:
```dsl
# This is a line comment

"""
This is a block comment
spanning multiple lines
"""
```

---

## 🎯 v3.0 Indentation Rules

### Core Rules

1. **Standard Indent**: 4 spaces per level
2. **Tab Support**: 1 tab = 4 spaces (but don't mix!)
3. **Block Start**: Colon `:` followed by newline and indent
4. **Block End**: Dedent (returning to previous indentation level)
5. **Empty Lines**: Allowed and ignored
6. **Comment Indentation**: Can be at any level

### Valid Indentation

```dsl
step "Example":                    # Level 0 + colon
    let x = 1                      # Level 1 (4 spaces)
    if x > 0:                      # Level 1 + colon
        log "positive"             # Level 2 (8 spaces)
        if x > 5:                  # Level 2 + colon
            log "large"            # Level 3 (12 spaces)
```

### Invalid Indentation

```dsl
# ❌ Inconsistent indentation (2 spaces instead of 4)
step "Bad":
  let x = 1  # Error: should be 4 spaces

# ❌ Mixed tabs and spaces
step "Bad":
    let x = 1   # 4 spaces
	let y = 2   # 1 tab - Error!

# ❌ Indentation jump (skipped level)
step "Bad":
            let x = 1  # Error: too much indent

# ❌ Wrong dedent level
if x > 0:
    let y = 1
      let z = 2  # Error: inconsistent dedent
```

### Error Messages

```
[词法错误] 第 3 行，第 3 列: 缩进错误：缩进量 2 不是 4 的倍数
每级缩进必须是 4 个空格或 1 个 Tab

    1 |   let x = 1

提示：使用 4 个空格或 1 个 Tab 进行缩进
```

---

## 📊 Summary Statistics

```
Total Statement Types:   31/35 (v4.1: +exit; v4.2: +resource; v5.0: +library, export, import; v5.0: limit raised to 35)
Total Expression Levels:  10/10 (v5.0: +member access for modules, at limit)
Total Operators:         18 (v3.0: added contains, matches, equals)
Total Built-in Functions: 20 (v4.0: added enumerate)
Total System Variables:   5 namespaces
Total Token Types:       197+ (v3.0: INDENT/DEDENT, removed END; v3.1: PIPE; v4.1: EXIT; v4.2: RESOURCE; v5.0: LIBRARY, EXPORT, IMPORT, FROM)
Total Lines of Parser:   2,600+ (v3.0: ParserV3; v4.2: +_parse_resource; v5.0: +module parsing)

Grammar Complexity Limits:
   Statement Types:      31/35 (88.6% - still room for 4 more)
   Expression Levels:    10/10 (100% - at limit ⚠️)
   Keywords:             91/100 (91% - room for 9 more)

Implementation Status:
✅ Implemented & Tested: 75/79 features (95%)
⚠️ Needs Tests:          0/79 (0%)
🚧 Partial:              0/79 (0%)
❌ Not Implemented:      4/79 (5%) - v5.0 Module System

Test Status:
✅ Passing:  725/731 (99.2%) (v4.1: +33 exit tests; v4.2: +136 REST API tests; v5.0: +0 module tests)
❌ Failing:  6/731 (0.8% - array concatenation syntax)

REST API Integration Tests (v4.2):
   Phase 2 (Auth):       24 tests ✅
   Phase 3 (Response):   39 tests ✅
   Phase 4 (Resilience): 47 tests ✅
   Phase 5 (Mock):       26 tests ✅
   Total:               136 tests ✅

Module System (v5.0):
   Status:              ❌ Not Implemented
   Proposal:            ✅ PROPOSAL-009-library-system.md
   Estimated Work:      14-20 days (3-4 weeks)
```

---

## 🔒 Validation Rules (VR)

| Rule ID | Description | Enforced By | Status |
|---------|-------------|-------------|--------|
| VR-VAR-001 | Variable must be defined before use | Parser | ✅ |
| VR-VAR-002 | Assignment target must exist | Parser | ✅ |
| VR-VAR-003 | No duplicate declarations in same scope | Parser | ✅ |
| VR-VAR-004 | Cannot modify constants | Parser | ✅ |
| VR-IND-001 | Indentation must be consistent (v3.0) | Lexer | ✅ |
| VR-IND-002 | No mixing tabs and spaces (v3.0) | Lexer | ✅ |
| VR-LIT-001 | Must use Python literals True/False/None (v3.0) | Lexer | ✅ |

**Test Coverage**: `tests/grammar_alignment/test_v3_validation_rules.py`

---

## 🚦 Grammar Change Control Process

### When Adding New Syntax

1. ✅ Update this document first (add row with ❌ status)
2. ✅ Implement parser method
3. ✅ Add AST node if needed
4. ✅ Add tests (achieve 100% coverage)
5. ✅ Update this document (change to ✅)
6. ✅ Update EBNF grammar
7. ✅ Update other documentation

### When Removing Syntax

1. ✅ Mark as 🗑️ in this document
2. ✅ Deprecation warning for 1 version
3. ✅ Remove in next version
4. ✅ Update all documentation

### When Changing Syntax (like v3.0)

1. ✅ Document both old and new syntax
2. ✅ Implement new syntax (breaking change)
3. ✅ Update all tests
4. ✅ Create migration guide
5. ✅ Update version number

---

## 🎯 Version History

| Version | Date | Changes | Commit |
|---------|------|---------|--------|
| **5.0** | TBD | ❌ Library System (模块化代码复用) - library/export/import 语句 | TBD (提案阶段) |
| **4.2** | 2025-11-28 | ⭐ REST API Integration (OpenAPI Resource Statement) - Phase 1-5 完成 | `d0a9ff7`, `f76a6ac` |
| **4.1** | 2025-11-28 | ⭐ Exit statement for controlled termination | TBD |
| **4.0** | 2025-11-28 | ⭐ enumerate() function + multi-variable for loops (tuple unpacking) | `086a224` |
| **3.4** | 2025-11-28 | ⭐ String iteration support (len & range functions) | `77c00cc` |
| **3.3** | 2025-11-28 | ⭐ Scroll & Extract expression support + f-string support for all Actions | `2e72c03` |
| **3.2** | 2025-11-28 | ⭐ Unified selector expression support for Actions | `01f08dd` |
| **3.1** | 2025-11-28 | ⭐ String expressions in WHERE clause + OR pattern in when statement | `ad1593e` |
| **3.0** | 2025-11-26 | 🎉 Python-style syntax | `32fe251` |
| 2.0 | 2025-11-25 | v2.0 features | `e695496` |
| 1.0 | 2024-XX-XX | Initial release | - |
---

### v5.0 Changes (Major Release - Library System) - ❌ Not Implemented

#### Overview
DSL v5.0 将引入完整的模块化系统,通过 `library`、`export` 和 `import` 语句实现代码复用和命名空间隔离,解决大型 flow 文件中的代码重复和维护困难问题。

#### 新特性

**1. Library Declaration** (`library NAME`):
- 声明库文件,实现独立作用域
- 库文件只能包含常量和函数定义
- 禁止可执行语句(step, log, wait等)

**2. Export Statement** (`export const/function`):
- 显式标记导出的常量和函数
- 控制库的公共 API
- 未导出的成员仅库内部可见

**3. Import Statement** (两种语法):
- `import alias from "path"` - 导入整个模块
- `from "path" import name1, name2` - 导入特定成员
- 支持相对路径解析
- 模块缓存和循环导入检测

**4. Member Access** (`module.member`):
- 访问导入模块的导出成员
- 保持命名空间清晰

#### 动机

当前问题:
- ❌ 600+ 行 flow 文件,工具函数与业务逻辑混在一起
- ❌ 多个文件重复定义相同的工具函数
- ❌ 全局作用域污染,容易命名冲突
- ❌ 无法跨项目复用通用函数库

解决方案:
```dsl
# 优化前: 600+ 行单文件
function log_phase_start(phase_num, phase_name):
    log info "阶段 [{phase_num}]: {phase_name}"

# ... 20+ 个工具函数
# ... 400+ 行业务逻辑

# 优化后: 模块化设计
# libs/logging.flow (30 行)
library logging
export function log_phase_start(phase_num, phase_name):
    log info "阶段 [{phase_num}]: {phase_name}"

# main.flow (100 行)
import logging from "libs/logging.flow"
step "阶段 1":
    logging.log_phase_start(1, "数据准备")
```

#### 实现计划

**预计工期**: 14-20 天 (3-4 周)

1. **Phase 1: Lexer** (0.5 天)
   - 添加 LIBRARY, EXPORT, IMPORT, FROM tokens

2. **Phase 2: Parser** (2-3 天)
   - `_parse_library_declaration()`
   - `_parse_export_statement()`
   - `_parse_import_statement()`
   - AST 节点: LibraryDeclaration, ExportStatement, ImportStatement

3. **Phase 3: Module System** (4-5 天)
   - ModuleLoader 类
   - 路径解析和模块缓存
   - 循环导入检测
   - 库文件约束验证

4. **Phase 4: Interpreter** (2-3 天)
   - `_execute_import()`
   - `_evaluate_member_access()`
   - ModuleObject 类

5. **Phase 5: Testing** (2-3 天)
   - 单元测试和集成测试
   - 覆盖率 ≥ 90%

6. **Phase 6: Documentation** (2-3 天)
   - 更新所有文档
   - 编写使用指南和示例

#### 语法复杂度影响

**当前状态** (v4.3):
```
语句类型: 27/30
表达式层次: 9/10
关键字: 88/100
```

**添加后** (v5.0):
```
语句类型: 31/35  (+4: library, export, import, member access - 在限制内 ✅)
表达式层次: 10/10 (+1: member access expression - 已达上限 ⚠️)
关键字: 91/100   (+3: library, export, import, from - 还有 9 个空位)
```

**评估**: ✅ 在调整后的限制内
- **语句类型**: 31/35 = 88.6% (还有 4 个空位) ✅
- **表达式层次**: 10/10 = 100% (已达上限) ⚠️
- **关键字**: 91/100 = 91% (还有 9 个空位) ✅
- **限制调整**: v5.0 将语句类型限制从 30 提升到 35,为未来特性预留空间
- **建议**: 表达式层次已达上限,未来新特性如需新增表达式层级需谨慎评估

#### 向后兼容性

- ✅ **100% 向后兼容**
- ✅ 现有 flow 文件无需修改
- ✅ 纯新增功能,无破坏性变更
- ✅ library/export/import 是新增关键字

#### 相关文档

- 提案: `grammar/proposals/PROPOSAL-009-library-system.md`
- 设计文档: MASTER.md Section 13
- 参考: Python import system, MT4 library, Rust modules

---

### v4.1 Changes (Minor Release - Exit Statement)

#### Overview
DSL v4.1 adds the `exit` statement for controlled script termination, distinguishing graceful exits from validation errors.

#### New Feature: Exit Statement

**Syntax**:
```dsl
exit                              # Success exit (code=0)
exit 0                            # Explicit success exit
exit 1                            # Failure exit
exit "message"                    # Failure with message (code=1)
exit 0, "message"                 # Success with message
exit 1, "message"                 # Failure with message
```

**Key Differences from Assert**:

| Aspect | `assert` | `exit` |
|--------|----------|--------|
| **Purpose** | Validate expectations | Controlled termination |
| **On Failure** | Throws exception (ExecutionError) | Normal flow (EarlyExitException) |
| **Use Case** | Verification requirements | Early termination logic |
| **Status** | Always FAILED on error | COMPLETED (code=0) or FAILED (code≠0) |

**Examples**:
```dsl
# Early exit for special cases
if user_type == "guest":
    exit 0, "Guest users skip processing"

# Conditional failure
if validation_errors > 0:
    exit 1, "Validation failed"

# vs Assert (different semantics)
assert user.is_authenticated, "User must be logged in"  # Throws error
exit 0  # Normal termination
```

**Implementation**:
- **Lexer**: Added `EXIT` token type (line 118)
- **Parser**: Added `_parse_exit()` method (lines 954-997)
- **AST**: Added `ExitStatement` node (lines 490-508)
- **Interpreter**: Added `EarlyExitException` and `_execute_exit()` (lines 128-149, 840-864)

**Testing**:
- ✅ 33 comprehensive tests in `tests/unit/test_exit_statement.py`
- ✅ All tests passing (100%)
- ✅ Coverage: Lexer, Parser, AST, Interpreter, integration scenarios

**Backward Compatibility**:
- ✅ 100% backward compatible
- ✅ Pure feature addition
- ✅ No breaking changes

---

### v4.0 Changes (Major Release - enumerate() and Multi-Variable Loops)

#### Overview
DSL v4.0 brings Python-style `enumerate()` function and multi-variable for loops with tuple unpacking, achieving **90% feature parity with Python for loops**.

#### 1. enumerate() Built-in Function

**Added**: `enumerate(iterable, start=0)` function for indexed iteration

**Syntax**:
```dsl
enumerate(iterable)           # start from 0
enumerate(iterable, start=n)  # start from n
```

**Returns**: List of (index, value) tuples

**Examples**:
```dsl
let items = ["apple", "banana", "cherry"]
let indexed = enumerate(items)
# Result: [(0, "apple"), (1, "banana"), (2, "cherry")]

let numbered = enumerate(items, start=1)
# Result: [(1, "apple"), (2, "banana"), (3, "cherry")]
```

**Use Case - Indexed Iteration**:
```dsl
let products = ["Laptop", "Mouse", "Keyboard"]

for index, product in enumerate(products):
    log f"Item {index}: {product}"
# Output:
# Item 0: Laptop
# Item 1: Mouse
# Item 2: Keyboard

for num, product in enumerate(products, start=1):
    log f"Product #{num}: {product}"
# Output:
# Product #1: Laptop
# Product #2: Mouse
# Product #3: Keyboard
```

#### 2. Multi-Variable For Loops (Tuple Unpacking)

**Added**: Support for multiple loop variables: `for a, b, c in items:`

**Syntax**:
```dsl
for var1, var2 in items:        # 2 variables
    ...

for var1, var2, var3 in items:  # 3 variables
    ...
```

**Examples**:
```dsl
# Two-variable unpacking
let pairs = [[1, "a"], [2, "b"], [3, "c"]]
for key, value in pairs:
    log f"{key} = {value}"

# Three-variable unpacking
let triplets = [[1, 2, 3], [4, 5, 6]]
for a, b, c in triplets:
    log f"{a}, {b}, {c}"
```

**Use Case - Key-Value Iteration**:
```dsl
let config = [
    ["api_key", "abc123"],
    ["base_url", "https://api.example.com"],
    ["timeout", "30"]
]

for key, value in config:
    log f"Config: {key} = {value}"
    # Set environment variable or configuration
```

#### 3. Combined Usage: enumerate() + Multi-Variable Loops

**The Power of Combination**:
```dsl
let users = [
    ["alice@example.com", "Alice"],
    ["bob@example.com", "Bob"]
]

for index, [email, name] in enumerate(users, start=1):
    log f"User {index}: {name} ({email})"
# Output:
# User 1: Alice (alice@example.com)
# User 2: Bob (bob@example.com)
```

**Use Case - Form Filling with Index**:
```dsl
let form_data = [
    ["Name", "John Doe"],
    ["Email", "john@example.com"],
    ["Phone", "555-1234"]
]

for index, [field, value] in enumerate(form_data):
    let selector = f".form-field[data-index=\"{index}\"] input"
    select input where css=selector
    type value
```

#### Error Handling

**Unpacking Count Mismatch**:
```dsl
let pairs = [[1, "a"], [2, "b", "extra"]]  # Mismatched lengths
for key, value in pairs:
    log key
# ❌ Error: 解包值数量不匹配：需要 2 个值，得到 3 个
```

**Non-Iterable Unpacking**:
```dsl
let numbers = [1, 2, 3]  # Not tuples/lists
for key, value in numbers:
    log key
# ❌ Error: 无法解包类型 int（期望 list 或 tuple）
```

#### Technical Implementation

**AST Changes**:
- `EachLoop.variable_name` → `EachLoop.variable_names` (List[str])
- Backward compatible: `variable_name` property returns first variable

**Parser Changes**:
- Support comma-separated variable list: `for a, b, c in ...`
- Validate variable count during unpacking

**Interpreter Changes**:
- Tuple unpacking with validation
- Enhanced error messages with mismatch details

#### Python Alignment

**Feature Parity**: 90% aligned with Python for loops

**Supported**:
- ✅ `enumerate(iterable, start=0)`
- ✅ Tuple unpacking: `for a, b in items:`
- ✅ Nested loops with enumerate
- ✅ break/continue support

**Not Yet Supported** (Future enhancements):
- ❌ `zip()` function
- ❌ For-else clause
- ❌ Unpacking in assignments: `a, b = [1, 2]`
- ❌ List comprehensions

#### Backward Compatibility

- ✅ **100% backward compatible**
- ✅ Single-variable loops work exactly as before
- ✅ No breaking changes to existing syntax

**Migration**: None required - new features only

#### Testing

- ✅ 7 syntax tests (all passing)
- ✅ 2 error handling tests (all passing)
- ✅ 556/562 total tests passing (99.0%)

---

### v3.4 Changes (Minor Release - New Features)

#### New Built-in Functions
**Added**: `len()` and `range()` functions for string iteration and dynamic loops

**Motivation**:
- DSL already supported string indexing (`text[0]`, `text[i]`)
- Missing ability to get dynamic length and generate index sequences
- Cannot implement character-by-character iteration (e.g., OTP digit input)

**1. len() Function**:
```dsl
let text = "Hello"
let length = len(text)     # 5.0

let arr = [1, 2, 3]
let count = len(arr)       # 3.0

let obj = {"a": 1}
let keys = len(obj)        # 1.0
```

**Supported types**: str, list, tuple, dict
**Returns**: float (DSL unified number type)

**2. range() Function**:
```dsl
let nums = range(5)              # [0.0, 1.0, 2.0, 3.0, 4.0]
let nums = range(2, 5)           # [2.0, 3.0, 4.0]
let nums = range(0, 10, 2)       # [0.0, 2.0, 4.0, 6.0, 8.0]
```

**Returns**: List[float] (DSL unified number type)
**Behavior**: Python-compatible range()

#### Use Case: String Iteration
```dsl
let verification_code = "123456"
let code_length = len(verification_code)

for i in range(code_length):
    let digit = verification_code[i]
    let index_int = Math.floor(i)
    let selector = f".otp-input[data-index=\"{index_int}\"]"

    select input where css=selector
    type digit
```

**Benefits**:
- Dynamic length validation
- Precise character-by-character control
- Flexible loop ranges

#### Known Limitation
- ⚠️ range() returns float list; f-string interpolation produces decimals (e.g., `"0.0"`)
- ✅ **Workaround**: Use `Math.floor(i)` to convert to integer before interpolation
- 💡 **Future**: Consider introducing True int type in v4.0 (see `INT-TYPE-IMPLEMENTATION-ANALYSIS.md`)

#### Backward Compatibility
- ✅ 100% backward compatible (new functions only)

---

### v3.3 Changes (Bug Fix)

#### Problem Fixed
- **Bug**: `scroll` and `extract` statements had selector parameters that bypassed expression parsing for string literals
- **Missing Feature**: All Actions (v3.2-fixed) missed f-string support due to incomplete token type checking
- **Impact**:
  - `scroll to "selector"` worked as literal only, couldn't use `scroll to f"#{id}-section"`
  - `extract text from "selector"` worked as literal only, couldn't use expressions
  - All Actions couldn't use f-strings even though they supported other expressions

#### Solution
**1. Scroll & Extract** (Primary fix - completing v3.2 pattern):
```python
# ✅ v3.3: Unified expression support
if self._check(TokenType.STRING) or self._check(TokenType.FSTRING) or self._check(TokenType.IDENTIFIER):
    selector = self._parse_expression()
```

**2. All Actions** (Secondary fix - adding f-string support):
- Added `TokenType.FSTRING` to all expression checks in v3.2-fixed Actions
- Now supports: `click f"#{id}-btn"`, `hover f".item-{index}"`, etc.

#### New Capabilities (v3.3)
```dsl
# Scroll expressions
scroll to f"#{section_id}"                    # f-string
scroll to sections[0]                         # Array indexing
scroll to config.main_section                 # Member access

# Extract expressions
extract text from f"#field-{name}" into value # f-string
extract text from inputs[index] into data     # Array indexing
extract text from form.username into user     # Member access

# All Actions with f-strings
click f"#button-{id}"
hover f".menu-{name}"
clear f"#input-{field}"
check f"#checkbox-{id}"
upload file f"/path/{file}" to f"#upload-{id}"
```

#### Backward Compatibility
- ✅ 100% backward compatible
- String literals still work: `scroll to "#section"` → parsed as `Literal` expression
- All existing tests pass (37/37 Actions + Extraction tests)

---

### v3.2 Changes (Patch + Minor Enhancement)

#### Problem Fixed
- **Bug**: 7 Actions (`click`, `double click`, `right click`, `hover`, `clear`, `check`/`uncheck`, `upload`) had inconsistent selector parameter parsing
- **Root Cause**: String literals bypassed expression parsing via direct token consumption
- **Impact**: String literals worked, but expressions (member access, array indexing, f-strings) failed

#### Solution Implemented
- **Unified Parsing Pattern**: All selector parameters now use `_parse_expression()` consistently
- **7 Parser Methods Modified**:
  1. `_parse_click()` - Click action selector
  2. `_parse_click_multiword()` - Double/right click selectors
  3. `_parse_hover()` - Hover action selector
  4. `_parse_clear()` - Clear action selector (optional)
  5. `_parse_check()` - Check/uncheck action selector
  6. `_parse_upload()` - Upload action file_path and selector

#### New Capabilities (v3.2)
All 7 Actions now support:
- ✅ **Member Access**: `click config.submit_button`
- ✅ **Array Indexing**: `click buttons[0]`
- ✅ **f-strings**: `click f"#{id}-submit"`
- ✅ **String Concatenation**: `click base + "-button"`
- ✅ **Complex Expressions**: `upload file paths[index] to f"#{id}-{type}"`

#### Backward Compatibility
- ✅ **100% Compatible**: String literals are valid expressions (subset)
- ✅ **No Breaking Changes**: All existing v3.1 code continues to work
- ✅ **Pure Enhancement**: Only expands capabilities, no removals

#### Governance Process Followed
- ✅ **Proposal**: `grammar/proposals/PROPOSAL-003-unified-selector-expression-support.md`
- ✅ **Design Review**: Syntax consistency, compatibility, complexity checks passed
- ✅ **Implementation**: 7 Parser methods unified
- ⏳ **Testing**: 31 test cases planned (pending)
- ⏳ **Documentation**: MASTER.md, CHANGELOG.md, PROPOSAL-003 (in progress)
- ⏳ **Validation**: check_sync.py + regression tests (pending)

#### Related Documents
- `ACTIONS-EXPRESSION-ANALYSIS.md` - Detailed problem analysis (800+ lines)
- `grammar/proposals/PROPOSAL-003-unified-selector-expression-support.md` - Formal proposal
- `src/registration_system/dsl/parser.py` - Implementation (lines 698-911)

### v3.1 Changes (Minor Enhancement)

#### New Features
1. ⭐ **String Expressions in WHERE Clause**: Attribute values now support full expressions
   - String concatenation: `select input where id = "user-" + user_id`
   - Arithmetic expressions: `select button where index = count + 1`
   - Member access: `select input where name = config.field_name`
   - Array indexing: `select input where id = field_ids[0]`
   - Complex expressions: `select input where id = base + "-" + (index * 2)`

2. ⭐ **OR Pattern Support in When Statement**: Multiple case values with `|` separator
   - Multi-value matching: `200 | 201 | 204:` matches any of the three values
   - Reduces code duplication for similar case handlers
   - Syntax: `case_value1 | case_value2 | case_value3:`
   - Backward compatible: Single values still work as before

#### OR Pattern Examples
```dsl
# HTTP status code grouping
when http_status:
    200 | 201 | 204:
        log "Success response"
    400 | 401 | 403:
        log "Client error"
    500 | 502 | 503:
        log "Server error"
    otherwise:
        log "Unknown status"

# User role-based access control
when user_role:
    "admin" | "moderator":
        access_level = "high"
    "user":
        access_level = "normal"
    otherwise:
        access_level = "guest"
```

#### Implementation Details
**String Expressions in WHERE Clause**:
- **Parser Changes**: Modified `_parse_where_clause()` to use `_parse_comparison()` for attribute values
- **Executor Changes**: Added expression evaluation in `_build_selector()` using `evaluate_expression()`
- **String Coercion**: All expression results are coerced to strings via `str()` for CSS/XPath compatibility
- **Backward Compatible**: v3.0 syntax still works (pure feature addition)

**OR Pattern in When Statement**:
- **Lexer Changes**: Added `PIPE` token type for `|` separator
- **AST Changes**: `WhenClause.case_value` → `WhenClause.case_values: List[Any]`
- **Parser Changes**: Modified `_parse_when()` to collect multiple case values separated by `|`
- **Interpreter Changes**: Rewrote `_execute_when()` to check match against all case values
- **Backward Compatible**: Single-value cases automatically converted to single-element lists

#### Documentation
- ✅ **SELECT-STATEMENT-EBNF.md**: Complete 650+ line specification updated (WHERE clause expressions)
- ✅ **V3-EBNF.md**: Updated WhenBlock syntax with OR pattern support
- ✅ **PROPOSAL-002**: Post-implementation proposal created (WHERE clause)
- ✅ **MASTER.md**: This document updated with v3.1 examples and OR pattern usage

#### Related Commits
- `ad1593e` - feat(dsl): support string expressions in where clause attribute values (v3.1)
- `0d61c7f` - docs(grammar): update SELECT EBNF to reflect v3.1 string expression support
- `5fd0725` - fix(dsl): add css attribute support in _build_selector
- TBD - feat(dsl): add OR pattern support in when statement (v3.1)

### v3.0 Changes (Breaking)

#### Syntax Changes
- ✅ **REMOVED all `end` keywords** (`end step`, `end if`, `end when`, `end for`)
- ✅ **Indentation-based blocks** (4 spaces or 1 tab)
- ✅ **Python literals**: `True`/`False`/`None` (not `True`/`False`/`None`)
- ✅ **INDENT/DEDENT tokens** replace `END` token

#### New Features
- ✅ **Removed optional keywords**: v3.1 removed `each` keyword entirely
- ✅ **Python-style parameters**: `call "method" with param: value`
- ✅ **Flexible parameter order**: `screenshot of "sel" as "name"`
- ✅ **Step diagnosis**: `step "name" with diagnosis detailed:`
- ✅ **When switch/match**: Cleaner pattern matching semantics
- ✅ **Expression enhancements**: Full f-string support, member access everywhere

#### Implementation
- ✅ **LexerV3**: Complete rewrite with indentation stack
- ✅ **ParserV3**: All block parsing uses INDENT/DEDENT
- ✅ **538 v3.0 tests**: 534 passing (99.3%)
- ✅ **100% feature coverage**: All 76 features tested

#### Migration
- ❌ **No backward compatibility**: v2.0 code will not run in v3.0
- ✅ **Migration required**: Automated tool recommended
- ✅ **Migration guide**: See `V3-MIGRATION-GUIDE.md`

### v2.0 Changes

- ✅ VR-VAR-003 now only checks current scope (allows shadowing)
- ✅ Complete symbol table system
- ✅ String interpolation
- ✅ System variables (context, page, etc.)
- ✅ Built-in functions (Math, Date, JSON)

### v3.0 Changes

- ✅ Python-style indentation blocks (removed `end` keywords)
- ✅ System variables without `$` prefix (context.task_id, page.url)
- ✅ Reserved word protection for system namespaces
- ✅ Python literals (True/False/None instead of True/False/None)
- ✅ Flexible syntax (v3.1: removed `each` keyword from for loops)
- ✅ While loop with break/continue (v3.0.0)

---

## 📖 Related Documents

### Source Files (Implementation)
- `src/registration_system/dsl/parser.py` - v3.0 Parser implementation
- `src/registration_system/dsl/lexer.py` - v3.0 Lexer implementation
- `src/registration_system/dsl/system_namespaces.py` - System namespace proxies (v3.0)
- `src/registration_system/dsl/ast_nodes.py` - AST node definitions
- `src/registration_system/dsl/interpreter.py` - Interpreter
- `src/registration_system/dsl/symbol_table.py` - Symbol table

### Specification Documents (Reference)
- `grammar/V3-REFACTOR-PLAN.md` - v3.0 refactoring plan
- `grammar/MASTER-v2.0-backup.md` - v2.0 specification backup
- `grammar/COVERAGE-REPORT.md` - Feature coverage report
- `docs/DSL-GRAMMAR.ebnf` - Complete EBNF specification

### Migration Documents
- `grammar/V3-MIGRATION-GUIDE.md` - v2.0 → v3.0 migration guide (TODO)
- `grammar/V3-EXAMPLES.flow` - Complete v3.0 examples (TODO)

### Test Files
- `tests/grammar_alignment/test_v3_*.py` - 538 v3.0 grammar tests
- `tests/grammar_alignment/test_09_while_loop.py` - 30 while loop tests (v3.0)
- `tests/grammar_alignment/conftest.py` - Test infrastructure

---

## ✅ Grammar Conformance Checklist

Use this checklist to ensure grammar changes are complete:

- [x] MASTER.md updated to v3.0
- [x] ParserV3 method implemented
- [x] AST nodes updated (StepBlock, WhenBlock, WhileLoop, etc.)
- [x] 538 v3.0 tests added
- [x] 534/538 tests passing (99.3%)
- [ ] DSL-GRAMMAR.ebnf updated (TODO)
- [ ] Quick reference updated (TODO)
- [ ] Migration guide created (TODO)
- [x] Examples in MASTER.md updated
- [x] Core implementation complete

---

## 🔍 Quick Verification Commands

```bash
# Run all v3.0 grammar tests
pytest tests/grammar_alignment/ -v

# Check parser coverage
pytest tests/grammar_alignment/ --cov=src/registration_system/dsl/parser_v3

# Run specific test categories
pytest tests/grammar_alignment/test_v3_00_indentation.py -v
pytest tests/grammar_alignment/test_v3_02_control_flow.py -v
pytest tests/grammar_alignment/test_v3_expressions.py -v

# Validate a DSL v3.0 script
regflow examples/flows/your_script_v3.flow

# Check for VR violations
regflow --check-only examples/flows/your_script_v3.flow

# Performance test
pytest tests/grammar_alignment/ --durations=10
```

---

**Maintained by**: Flowby Core Team
**Last Review**: 2025-11-26
**Next Review**: After v3.0 release stabilization

---

**Remember**: This document is the **Single Source of Truth** for v3.0 grammar. When in doubt, refer here first.
