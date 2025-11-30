# Grammar Feature Coverage Validation Report

**Generated**: 2025-11-29 20:49:43

---

## 📊 Overall Statistics

| Metric | Value | Status |
|--------|-------|--------|
| Total Features | 74 | - |
| Covered Features | 33 | ⚠️ |
| Missing Features | 41 | ❌ |
| Coverage Percentage | 44.6% | ⚠️ |
| Orphan Tests | 4 | ⚠️ |

## 📂 Coverage by Category

| Category | Total | Covered | Coverage | Status |
|----------|-------|---------|----------|--------|
| Actions | 10 | 10 | ████████████████████ 100% | ✅ |
| Assertions | 5 | 4 | ████████████████░░░░ 80% | ⚠️ |
| Built-in: Date | 3 | 0 | ░░░░░░░░░░░░░░░░░░░░ 0% | ⚠️ |
| Built-in: Global Functions | 5 | 0 | ░░░░░░░░░░░░░░░░░░░░ 0% | ⚠️ |
| Built-in: JSON | 2 | 0 | ░░░░░░░░░░░░░░░░░░░░ 0% | ⚠️ |
| Built-in: Math | 9 | 0 | ░░░░░░░░░░░░░░░░░░░░ 0% | ⚠️ |
| Control Flow | 7 | 4 | ███████████░░░░░░░░░ 57% | ⚠️ |
| Data Extraction | 1 | 1 | ████████████████████ 100% | ✅ |
| Expressions | 9 | 0 | ░░░░░░░░░░░░░░░░░░░░ 0% | ⚠️ |
| Navigation | 3 | 3 | ████████████████████ 100% | ✅ |
| Selection | 2 | 2 | ████████████████████ 100% | ✅ |
| Service Call | 1 | 1 | ████████████████████ 100% | ✅ |
| Unknown | 9 | 0 | ░░░░░░░░░░░░░░░░░░░░ 0% | ⚠️ |
| Utilities | 2 | 2 | ████████████████████ 100% | ✅ |
| Variables & Assignment | 3 | 3 | ████████████████████ 100% | ✅ |
| Wait | 3 | 3 | ████████████████████ 100% | ✅ |

## ❌ Missing Feature Coverage

以下特性在 MASTER.md 中定义，但没有找到对应的测试：

| Feature ID | Feature Name | Category |
|------------|--------------|----------|
| 2.5 | While Loop | Control Flow |
| 2.6 | Break Statement | Control Flow |
| 2.7 | Continue Statement | Control Flow |
| 7.5 | Exit Statement | Assertions |
| 11.1 | OpenAPI Resource Statement | Unknown |
| 12.1 | Function Definition | Unknown |
| 12.2 | Return Statement | Unknown |
| 12.3 | Function Call | Unknown |
| 13.1 | Library Declaration | Unknown |
| 13.2 | Export Statement | Unknown |
| 13.3 | Import Statement | Unknown |
| 13.4 | Member Access | Unknown |
| 14.1 | Input Expression | Unknown |
| expr-level1 | Expression Level 1: or | Expressions |
| expr-level2 | Expression Level 2: and | Expressions |
| expr-level3 | Expression Level 3: not | Expressions |
| expr-level4 | Expression Level 4: ==, !=, >, <, >=, <=, contains, matches, equals | Expressions |
| expr-level5 | Expression Level 5: +, - | Expressions |
| expr-level6 | Expression Level 6: *, /, //, % | Expressions |
| expr-level7 | Expression Level 7: Unary -, not | Expressions |
| expr-level8 | Expression Level 8: ., [], () | Expressions |
| expr-level9 | Expression Level 9: Literals, Variables | Expressions |
| builtin-math-abs | Built-in Function: Math.abs(x) | Built-in: Math |
| builtin-math-round | Built-in Function: Math.round(x) | Built-in: Math |
| builtin-math-ceil | Built-in Function: Math.ceil(x) | Built-in: Math |
| builtin-math-floor | Built-in Function: Math.floor(x) | Built-in: Math |
| builtin-math-max | Built-in Function: Math.max(...args) | Built-in: Math |
| builtin-math-min | Built-in Function: Math.min(...args) | Built-in: Math |
| builtin-math-random | Built-in Function: Math.random() | Built-in: Math |
| builtin-math-pow | Built-in Function: Math.pow(base, exp) | Built-in: Math |
| builtin-math-sqrt | Built-in Function: Math.sqrt(x) | Built-in: Math |
| builtin-date-now | Built-in Function: Date.now() | Built-in: Date |
| builtin-date-format | Built-in Function: Date.format(fmt) | Built-in: Date |
| builtin-date-from_timestamp | Built-in Function: Date.from_timestamp(ts) | Built-in: Date |
| builtin-json-stringify | Built-in Function: JSON.stringify(obj) | Built-in: JSON |
| builtin-json-parse | Built-in Function: JSON.parse(str) | Built-in: JSON |
| builtin-number | Built-in Function: Number(value) | Built-in: Global Functions |
| builtin-string | Built-in Function: String(value) | Built-in: Global Functions |
| builtin-boolean | Built-in Function: Boolean(value) | Built-in: Global Functions |
| builtin-isnan | Built-in Function: isNaN(value) | Built-in: Global Functions |
| builtin-isfinite | Built-in Function: isFinite(value) | Built-in: Global Functions |

## ⚠️ Orphan Tests

以下测试标记的特性在 MASTER.md 中未找到定义：

| Test Feature ID | Test Files |
|----------------|------------|
| 9.2 | test_09_while_loop.py |
| 9.3 | test_09_while_loop.py |
| 9 | test_09_while_loop.py |
| system-var | test_v3_system_variables.py |

## 📋 Detailed Feature Coverage

### Actions

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| 6.1 | Type | ✅ | test_v3_06_actions.py |
| 6.10 | Upload | ✅ | test_v3_06_actions.py |
| 6.2 | Click | ✅ | test_v3_06_actions.py |
| 6.3 | Double Click | ✅ | test_v3_06_actions.py |
| 6.4 | Right Click | ✅ | test_v3_06_actions.py |
| 6.5 | Hover | ✅ | test_v3_06_actions.py |
| 6.6 | Clear | ✅ | test_v3_06_actions.py |
| 6.7 | Press | ✅ | test_v3_06_actions.py |
| 6.8 | Scroll | ✅ | test_v3_06_actions.py |
| 6.9 | Check/Uncheck | ✅ | test_v3_06_actions.py |

### Assertions

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| 7.1 | Assert Expression | ✅ | test_v3_07_assertions.py |
| 7.2 | Assert URL | ✅ | test_v3_07_assertions.py |
| 7.3 | Assert Element | ✅ | test_v3_07_assertions.py |
| 7.4 | Assert Content | ✅ | test_v3_07_assertions.py |
| 7.5 | Exit Statement | ❌ | - |

### Built-in: Date

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| builtin-date-format | Built-in Function: Date.format(fmt) | ❌ | - |
| builtin-date-from_timestamp | Built-in Function: Date.from_timestamp(ts) | ❌ | - |
| builtin-date-now | Built-in Function: Date.now() | ❌ | - |

### Built-in: Global Functions

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| builtin-boolean | Built-in Function: Boolean(value) | ❌ | - |
| builtin-isfinite | Built-in Function: isFinite(value) | ❌ | - |
| builtin-isnan | Built-in Function: isNaN(value) | ❌ | - |
| builtin-number | Built-in Function: Number(value) | ❌ | - |
| builtin-string | Built-in Function: String(value) | ❌ | - |

### Built-in: JSON

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| builtin-json-parse | Built-in Function: JSON.parse(str) | ❌ | - |
| builtin-json-stringify | Built-in Function: JSON.stringify(obj) | ❌ | - |

### Built-in: Math

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| builtin-math-abs | Built-in Function: Math.abs(x) | ❌ | - |
| builtin-math-ceil | Built-in Function: Math.ceil(x) | ❌ | - |
| builtin-math-floor | Built-in Function: Math.floor(x) | ❌ | - |
| builtin-math-max | Built-in Function: Math.max(...args) | ❌ | - |
| builtin-math-min | Built-in Function: Math.min(...args) | ❌ | - |
| builtin-math-pow | Built-in Function: Math.pow(base, exp) | ❌ | - |
| builtin-math-random | Built-in Function: Math.random() | ❌ | - |
| builtin-math-round | Built-in Function: Math.round(x) | ❌ | - |
| builtin-math-sqrt | Built-in Function: Math.sqrt(x) | ❌ | - |

### Control Flow

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| 2.1 | Step Block | ✅ | test_v3_02_control_flow.py |
| 2.2 | If-Else | ✅ | test_v3_02_control_flow.py |
| 2.3 | When-Otherwise | ✅ | test_v3_02_control_flow.py |
| 2.4 | For Loop | ✅ | test_v3_02_control_flow.py |
| 2.5 | While Loop | ❌ | - |
| 2.6 | Break Statement | ❌ | - |
| 2.7 | Continue Statement | ❌ | - |

### Data Extraction

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| 9.1 | Extract | ✅ | test_v3_09_extraction.py, test_09_while_loop.py |

### Expressions

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| expr-level1 | Expression Level 1: or | ❌ | - |
| expr-level2 | Expression Level 2: and | ❌ | - |
| expr-level3 | Expression Level 3: not | ❌ | - |
| expr-level4 | Expression Level 4: ==, !=, >, <, >=, <=, contains, matches, equals | ❌ | - |
| expr-level5 | Expression Level 5: +, - | ❌ | - |
| expr-level6 | Expression Level 6: *, /, //, % | ❌ | - |
| expr-level7 | Expression Level 7: Unary -, not | ❌ | - |
| expr-level8 | Expression Level 8: ., [], () | ❌ | - |
| expr-level9 | Expression Level 9: Literals, Variables | ❌ | - |

### Navigation

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| 3.1 | Navigate To | ✅ | test_v3_03_navigation.py |
| 3.2 | Go Back/Forward | ✅ | test_v3_03_navigation.py |
| 3.3 | Reload | ✅ | test_v3_03_navigation.py |

### Selection

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| 5.1 | Select Element | ✅ | test_v3_05_selection.py |
| 5.2 | Select Option | ✅ | test_v3_05_selection.py |

### Service Call

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| 8.1 | Service Call (Python-style) | ✅ | test_08_service_call.py |

### Unknown

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| 11.1 | OpenAPI Resource Statement | ❌ | - |
| 12.1 | Function Definition | ❌ | - |
| 12.2 | Return Statement | ❌ | - |
| 12.3 | Function Call | ❌ | - |
| 13.1 | Library Declaration | ❌ | - |
| 13.2 | Export Statement | ❌ | - |
| 13.3 | Import Statement | ❌ | - |
| 13.4 | Member Access | ❌ | - |
| 14.1 | Input Expression | ❌ | - |

### Utilities

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| 10.1 | Log | ✅ | test_v3_10_utilities.py |
| 10.2 | Screenshot | ✅ | test_v3_10_utilities.py |

### Variables & Assignment

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| 1.1 | Let Declaration | ✅ | test_v3_01_variables.py |
| 1.2 | Const Declaration | ✅ | test_v3_01_variables.py |
| 1.3 | Assignment | ✅ | test_v3_01_variables.py |

### Wait

| Feature ID | Feature Name | Status | Test Files |
|------------|--------------|--------|------------|
| 4.1 | Wait Duration | ✅ | test_v3_04_wait.py |
| 4.2 | Wait Element | ✅ | test_v3_04_wait.py |
| 4.3 | Wait Navigation | ✅ | test_v3_04_wait.py |
