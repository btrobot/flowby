# DSL Grammar Master Control Document

> **Version**: 2.0
> **Status**: Active
> **Last Updated**: 2025-11-25
> **Purpose**: Single Source of Truth for DSL Grammar

---

## 🎯 Purpose

This document serves as the **authoritative grammar control** for the Registration System DSL. All implementation must conform to this specification.

**Key Principle**:
- ✅ **This document defines what IS implemented**
- ✅ **If it's not here, it's not supported**
- ✅ **Changes here require corresponding code changes**

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
| 1.1 | Let Declaration | `let VAR = expr` | ✅ | v1.0 | `_parse_let_statement()` | ✅ | VR-VAR-003 checks current scope only (changed in v2.0) |
| 1.2 | Const Declaration | `const VAR = expr` | ✅ | v1.0 | `_parse_const_statement()` | ✅ | VR-VAR-004 prevents modification |
| 1.3 | Assignment | `VAR = expr` | ✅ | v1.0 | `_parse_assignment()` | ✅ | VR-VAR-002 checks if defined |

**Test Coverage**: `tests/test_variables.py`

---

## 2. Control Flow (4 features)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 2.1 | Step Block | `step "name" [with diagnosis LEVEL]: ... end step` | ✅ | v1.0 | `_parse_step()` | ✅ | 6 diagnosis levels |
| 2.2 | If-Else | `if COND: ... [else: ...] end if` | ✅ | v1.0 | `_parse_if()` | ✅ | Nested if supported |
| 2.3 | When-Otherwise | `when VAR: "val": ... otherwise: ... end when` | ✅ | v1.0 | `_parse_when()` | ✅ | Pattern matching |
| 2.4 | For-Each Loop | `for VAR in EXPR: ... end for` | ✅ | v1.0 | `_parse_for_each_loop()` | ✅ | Iterates arrays |

**Test Coverage**: `tests/test_control_flow.py`

---

## 3. Navigation (3 features)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 3.1 | Navigate To | `navigate to URL [wait for STATE]` | ✅ | v1.0 | `_parse_navigate()` | ✅ | 3 page states |
| 3.2 | Go Back/Forward | `go back` / `go forward` | ✅ | v1.0 | `_parse_go()` | ✅ | Browser history |
| 3.3 | Reload | `reload` | ✅ | v1.0 | `_parse_reload()` | ✅ | Refresh page |

**Test Coverage**: `tests/test_navigation.py`

**Page States**: `networkidle`, `domcontentloaded`, `load`

---

## 4. Wait (3 forms)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 4.1 | Wait Duration | `wait [for] N [UNIT]` | ✅ | v1.0 | `_parse_wait()` | ✅ | Units: s, ms, seconds, milliseconds |
| 4.2 | Wait Element | `wait for element SEL [to be STATE] [timeout N]` | ✅ | v1.0 | `_parse_wait_for()` | ✅ | 4 element states |
| 4.3 | Wait Navigation | `wait for navigation [to URL] [wait for STATE] [timeout N]` | ✅ | v1.0 | `_parse_wait_for()` | ✅ | Navigation completion |

**Test Coverage**: `tests/test_wait.py`

**Element States**: `visible`, `hidden`, `attached`, `detached`

---

## 5. Selection (2 features)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 5.1 | Select Element | `select SEL [where COND and COND ...]` | ✅ | v1.0 | `_parse_select()` | ✅ | Multiple where conditions |
| 5.2 | Select Option | `select option VAL from SEL` | ✅ | v1.0 | `_parse_select_option()` | ✅ | Dropdown selection |

**Test Coverage**: `tests/test_selection.py`

**Where Conditions**: `text/value/class/id/name/href/src/alt/title contains/equals/matches EXPR`

---

## 6. Actions (10 features)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 6.1 | Type | `type EXPR [into SEL] [slowly\|fast]` | ✅ | v1.0 | `_parse_type()` | ✅ | Typing modifiers |
| 6.2 | Click | `click [SEL]` | ✅ | v1.0 | `_parse_click()` | ✅ | Left click |
| 6.3 | Double Click | `double click [SEL]` | ✅ | v1.0 | `_parse_click()` | ✅ | Double click |
| 6.4 | Right Click | `right click [SEL]` | ✅ | v1.0 | `_parse_click()` | ✅ | Context menu |
| 6.5 | Hover | `hover [over] SEL` | ✅ | v1.0 | `_parse_hover()` | ✅ | Mouse hover |
| 6.6 | Clear | `clear [SEL]` | ✅ | v1.0 | `_parse_clear()` | ✅ | Clear input |
| 6.7 | Press | `press KEY` | ✅ | v1.0 | `_parse_press()` | ✅ | Keyboard keys |
| 6.8 | Scroll | `scroll to top\|bottom\|SEL\|PIXELS` | ✅ | v1.0 | `_parse_scroll()` | ✅ | 4 scroll targets |
| 6.9 | Check/Uncheck | `check\|uncheck SEL` | ✅ | v1.0 | `_parse_check()` | ✅ | Checkbox |
| 6.10 | Upload | `upload file PATH [to SEL]` | ✅ | v1.0 | `_parse_upload()` | ✅ | File upload |

**Test Coverage**: `tests/test_actions.py`

---

## 7. Assertions (4 types)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 7.1 | Assert URL | `assert url contains\|equals\|matches EXPR` | ✅ | v1.0 | `_parse_assert()` | ✅ | URL checks |
| 7.2 | Assert Element | `assert SEL exists\|visible\|hidden` | ✅ | v1.0 | `_parse_assert()` | ✅ | Element state |
| 7.3 | Assert Text/Value | `assert SEL has text\|value EXPR` | ✅ | v1.0 | `_parse_assert()` | ✅ | Content checks |
| 7.4 | Assert Attribute | `assert SEL has ATTR EXPR` | ✅ | v1.0 | `_parse_assert()` | ✅ | Attribute checks |

**Test Coverage**: `tests/test_assertions.py`

---

## 8. Service Call (1 feature)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 8.1 | Call Service | `call "provider.method" [with PARAMS] [into VAR]` | ✅ | v1.0 | `_parse_call()` | ✅ | Extensible providers |

**Test Coverage**: `tests/test_service_call.py`

**Built-in Services**:
- `http.get`, `http.post`, `http.put`, `http.delete`, `http.patch`
- `random.email`, `random.password`, `random.username`, `random.phone`, `random.number`, `random.uuid`

---

## 9. Data Extraction (1 feature)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 9.1 | Extract | `extract text\|value\|attr "NAME" from SEL [pattern REGEX] into VAR` | ✅ | v1.0 | `_parse_extract_statement()` | ✅ | Regex support |

**Test Coverage**: `tests/test_extraction.py`

---

## 10. Utilities (2 features)

| # | Feature | Syntax | Status | Since | Parser Method | Tests | Notes |
|---|---------|--------|--------|-------|---------------|-------|-------|
| 10.1 | Log | `log EXPR` | ✅ | v1.0 | `_parse_log_statement()` | ✅ | String interpolation |
| 10.2 | Screenshot | `screenshot [of SEL] [as NAME] [fullpage]` | ✅ | v1.0 | `_parse_screenshot()` | ✅ | Image capture |

**Test Coverage**: `tests/test_utilities.py`

---

## 📈 Expression System

### Operator Precedence (9 levels)

| Level | Operators | Associativity | Since | Parser Method |
|-------|-----------|---------------|-------|---------------|
| 1 (Low) | `or` | Left | v1.0 | `_parse_logical_or()` |
| 2 | `and` | Left | v1.0 | `_parse_logical_and()` |
| 3 | `not` | Right | v1.0 | `_parse_logical_not()` |
| 4 | `==`, `!=`, `>`, `<`, `>=`, `<=` | Left | v1.0 | `_parse_comparison()` |
| 5 | `+`, `-` | Left | v1.0 | `_parse_additive()` |
| 6 | `*`, `/`, `%` | Left | v1.0 | `_parse_multiplicative()` |
| 7 | Unary `-`, `not` | Right | v1.0 | `_parse_unary()` |
| 8 | `.`, `[]`, `()` | Left | v1.0 | `_parse_postfix()` |
| 9 (High) | Literals, Variables | - | v1.0 | `_parse_primary()` |

**Test Coverage**: `tests/test_expressions.py`

---

## 🎨 Data Types

| Type | Syntax | Examples | Since | Parser Method |
|------|--------|----------|-------|---------------|
| String | `"text"`, `'text'` | `"Hello"` | v1.0 | `_parse_primary()` |
| String Interpolation | `"text {expr} text"` | `"Count: {x + 1}"` | v2.0 | `_parse_string_interpolation()` |
| Number | `123`, `3.14` | `-10`, `0.5` | v1.0 | `_parse_primary()` |
| Boolean | `true`, `false` | - | v1.0 | `_parse_primary()` |
| Null | `null` | - | v1.0 | `_parse_primary()` |
| Array | `[expr, ...]` | `[1, 2, 3]` | v1.0 | `_parse_array_literal()` |
| Object | `{key: val, ...}` | `{name: "Alice"}` | v1.0 | `_parse_object_literal()` |

**Test Coverage**: `tests/test_data_types.py`

---

## 🔧 System Variables (5 namespaces)

| Namespace | Properties | Example | Since | Status |
|-----------|-----------|---------|-------|--------|
| `$context` | `task_id`, `execution_id`, `start_time`, `step_name`, `status` | `$context.task_id` | v2.0 | ✅ |
| `$page` | `url`, `title`, `origin` | `$page.url` | v2.0 | ✅ |
| `$browser` | `name`, `version` | `$browser.name` | v2.0 | ✅ |
| `$env` | Any environment variable | `$env.API_KEY` | v2.0 | ✅ |
| `$config` | Any config key | `$config.base_url` | v2.0 | ✅ |

**Test Coverage**: `tests/test_system_variables.py`

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

**Test Coverage**: `tests/test_builtin_functions.py`

---

## 📝 Comments & Metadata

| Feature | Syntax | Status |
|---------|--------|--------|
| Line Comment | `# comment` | ✅ |
| Block Comment | `/* ... */` | ✅ |
| Meta Block | `/**meta ... */` | ✅ |

**Meta Fields**: `pass`, `desc`, `symbol`

---

## 📊 Summary Statistics

```
Total Statement Types:   25
Total Expression Levels:  9
Total Operators:         15
Total Built-in Functions: 19
Total System Variables:   5 namespaces
Total Token Types:       188+
Total Lines of Parser:   1,900

Implementation Status:
✅ Implemented & Tested: 25/25 (100%)
⚠️ Needs Tests:          0/25 (0%)
🚧 Partial:              0/25 (0%)
❌ Not Implemented:      0/25 (0%)
```

---

## 🔒 Validation Rules (VR)

| Rule ID | Description | Enforced By | Status |
|---------|-------------|-------------|--------|
| VR-VAR-001 | Variable must be defined before use | Parser | ✅ |
| VR-VAR-002 | Assignment target must exist | Parser | ✅ |
| VR-VAR-003 | No duplicate declarations in same scope | Parser | ✅ |
| VR-VAR-004 | Cannot modify constants | Parser | ✅ |

**Test Coverage**: `tests/test_validation_rules.py`

---

## 🚦 Grammar Change Control Process

### When Adding New Syntax

1. ✅ Update this document first (add row with ❌ status)
2. ✅ Implement parser method
3. ✅ Add AST node if needed
4. ✅ Add tests
5. ✅ Update this document (change to ✅)
6. ✅ Update EBNF grammar
7. ✅ Update other documentation

### When Removing Syntax

1. ✅ Mark as 🗑️ in this document
2. ✅ Deprecation warning for 1 version
3. ✅ Remove in next version
4. ✅ Update all documentation

### When Changing Syntax

1. ✅ Document both old and new syntax
2. ✅ Implement new syntax
3. ✅ Deprecate old syntax (🗑️)
4. ✅ Update tests
5. ✅ Migration guide

---

## 🎯 Version History

| Version | Date | Changes | Commit |
|---------|------|---------|--------|
| **2.0** | 2025-11-25 | Current version | `e695496` |
| 1.0 | 2024-XX-XX | Initial release | - |

### v2.0 Changes

- ✅ VR-VAR-003 now only checks current scope (allows shadowing)
- ✅ Complete symbol table system
- ✅ String interpolation
- ✅ System variables ($context, $page, etc.)
- ✅ Built-in functions (Math, Date, JSON)

---

## 📖 Related Documents

### Source Files (Implementation)
- `src/registration_system/dsl/parser.py` - Parser implementation
- `src/registration_system/dsl/lexer.py` - Lexer implementation
- `src/registration_system/dsl/ast_nodes.py` - AST node definitions
- `src/registration_system/dsl/interpreter.py` - Interpreter
- `src/registration_system/dsl/symbol_table.py` - Symbol table

### Specification Documents (Reference)
- `docs/DSL-GRAMMAR.ebnf` - Complete EBNF specification
- `docs/DSL-GRAMMAR-QUICK-REFERENCE.md` - Quick reference
- `docs/DSL-SYNTAX-CHEATSHEET.md` - Syntax cheatsheet
- `docs/DSL-GRAMMAR-INDEX.md` - Documentation index

### Technical Documents (Deep Dive)
- `docs/technical-analysis/01-PROJECT-OVERVIEW.md` - Project overview
- `docs/technical-analysis/02-MODULE-DETAILS.md` - Module details
- `docs/technical-analysis/03-CORE-ALGORITHMS.md` - Algorithms
- `docs/technical-analysis/04-API-REFERENCE.md` - API reference

---

## ✅ Grammar Conformance Checklist

Use this checklist to ensure grammar changes are complete:

- [ ] GRAMMAR-MASTER.md updated
- [ ] Parser method implemented
- [ ] AST node added (if needed)
- [ ] Tests added/updated
- [ ] DSL-GRAMMAR.ebnf updated
- [ ] Quick reference updated
- [ ] Cheatsheet updated
- [ ] Technical docs updated
- [ ] Examples added
- [ ] All tests passing

---

## 🔍 Quick Verification Commands

```bash
# Verify all grammar features have tests
pytest tests/ -v

# Check parser coverage
pytest tests/ --cov=src/registration_system/dsl/parser

# Run specific grammar tests
pytest tests/test_expressions.py -v
pytest tests/test_control_flow.py -v

# Validate a DSL script
regflow examples/flows/your_script.flow

# Check for VR violations
regflow --check-only examples/flows/your_script.flow
```

---

**Maintained by**: Registration System Core Team
**Last Review**: 2025-11-25
**Next Review**: TBD

---

**Remember**: This document is the **Single Source of Truth** for grammar. When in doubt, refer here first.
