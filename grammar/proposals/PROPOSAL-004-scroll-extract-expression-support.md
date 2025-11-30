# Grammar Proposal #004: Scroll & Extract Expression Support

> **提案编号**: #004
> **提出日期**: 2025-11-28
> **提出人**: DSL Core Team
> **状态**: 📝 Under Review
> **目标版本**: 3.3.0
> **影响级别**: PATCH (Bug Fix)

---

## 📋 提案摘要

修复 `scroll` 和 `extract` 语句中选择器参数的表达式解析不一致问题，统一所有选择器参数都支持完整的表达式语法。

**问题**: `scroll to "selector"` 和 `extract ... from "selector"` 中的字符串字面量绕过了表达式解析，导致无法使用 f-string、成员访问、数组索引等表达式特性。

**解决方案**: 与 v3.2 修复 Actions 的模式一致，统一使用 `_parse_expression()` 解析选择器参数。

---

## 🎯 动机和背景

### 问题描述

在 v3.2 中，我们修复了 7 个 Action 语句（click, hover, clear, check, upload 等）的选择器表达式支持。但是在代码审查中发现，`scroll` 和 `extract` 语句仍然存在相同的问题。

**当前行为**:
```dsl
# ✅ 字符串字面量 - 支持（但绕过表达式解析）
scroll to "#section"
extract text from "#code" into result

# ✅ 简单标识符 - 支持（通过表达式）
scroll to section_selector
extract text from input_selector into data

# ❌ 成员访问 - 不支持（被字符串字面量阻断）
scroll to config.section_selector  # 解析失败（如果用字符串）
extract text from form.input_selector into result

# ❌ 数组索引 - 不支持
scroll to sections[0]
extract text from inputs[index] into data

# ❌ f-string - 不支持
scroll to f"#{id}-section"
extract text from f"#input-{field}" into result
```

**根本原因**:

Parser 中存在与 v3.2 修复前相同的错误模式：

**1. `_parse_scroll()` (parser.py:829-831)**:
```python
# ❌ 当前错误模式
if self._check(TokenType.STRING):
    selector = self._advance().value  # 直接取字面量，阻断表达式解析
    return ScrollAction(target="element", selector=selector, line=line)
```

**2. `_parse_extract_statement()` (parser.py:1637-1640)**:
```python
# ❌ 当前错误模式
if self._check(TokenType.STRING):
    selector = self._consume(TokenType.STRING, "期望选择器").value  # 直接取值
else:
    selector = self._parse_expression()
```

**导致的问题**:
1. **Bug**: 字符串字面量绕过表达式解析，导致 f-string、成员访问等特性无法使用
2. **不一致性**: v3.2 已修复 Actions，但 scroll 和 extract 仍有相同问题
3. **用户困扰**: 需要使用临时变量作为变通方案

### 为什么现有功能不够？

**当前做法（变通方案）**:

```dsl
# 方案 1: 使用临时变量
let section_sel = f"#{id}-section"
scroll to section_sel

let input_sel = config.input_selector
extract text from input_sel into result

# 方案 2: 仅使用标识符（不直接使用字符串）
# 必须提前声明变量，无法内联表达式
```

**问题**:
- 代码冗长，需要额外变量
- 与 v3.2 Actions 行为不一致（click 已支持表达式）
- 字符串字面量"看起来"能用，但实际上被降级为纯字面量

---

## 💡 提议的解决方案

### 语法设计

**修改前** (v3.2 及之前):
```dsl
# scroll 语句
scroll to top                        # ✅ 关键字
scroll to element "selector"         # ✅ 完整语法（表达式支持）
scroll to "selector"                 # ⚠️  简化语法（绕过表达式）
scroll to variable                   # ✅ 变量（表达式支持）
scroll to 500                        # ✅ 数字

# extract 语句
extract text from "selector" into var    # ⚠️  字符串（绕过表达式）
extract text from variable into var      # ✅ 变量（表达式支持）
```

**修改后** (v3.3):
```dsl
# scroll 语句 - 选择器完全支持表达式
scroll to config.section                 # ✅ 成员访问
scroll to sections[0]                    # ✅ 数组索引
scroll to f"#{id}-section"               # ✅ f-string
scroll to base + "-section"              # ✅ 字符串拼接

# extract 语句 - 选择器完全支持表达式
extract text from config.input into data         # ✅ 成员访问
extract text from inputs[index] into result      # ✅ 数组索引
extract text from f"#field-{name}" into value    # ✅ f-string
extract text from prefix + "-input" into data    # ✅ 字符串拼接
```

### 实现细节

#### 1. `_parse_scroll()` 修复

**修改前**:
```python
def _parse_scroll(self) -> ScrollAction:
    """解析 scroll 语句"""
    line = self._peek().line
    self._consume(TokenType.SCROLL, "期望 'scroll'")
    self._consume(TokenType.TO, "期望 'to'")

    # scroll to top / bottom
    if self._check_any(TokenType.TOP, TokenType.BOTTOM):
        target_token = self._advance()
        return ScrollAction(target=target_token.value.lower(), line=line)

    # scroll to element "selector"
    if self._check(TokenType.ELEMENT):
        self._advance()
        selector_token = self._consume(TokenType.STRING, "期望选择器字符串")
        return ScrollAction(target="element", selector=selector_token.value, line=line)

    # ❌ 问题代码：字符串绕过表达式
    if self._check(TokenType.STRING):
        selector = self._advance().value
        return ScrollAction(target="element", selector=selector, line=line)

    # scroll to 500 (数字位置)
    if self._check(TokenType.NUMBER):
        position = self._advance().value
        return ScrollAction(target="position", selector=position, line=line)

    # scroll to variable (变量)
    if self._check(TokenType.IDENTIFIER):
        expr = self._parse_expression()
        return ScrollAction(target="element", selector=expr, line=line)

    raise ParserError(...)
```

**修改后**:
```python
def _parse_scroll(self) -> ScrollAction:
    """解析 scroll 语句 (v3.3: 完全表达式支持)"""
    line = self._peek().line
    self._consume(TokenType.SCROLL, "期望 'scroll'")
    self._consume(TokenType.TO, "期望 'to'")

    # scroll to top / bottom (关键字)
    if self._check_any(TokenType.TOP, TokenType.BOTTOM):
        target_token = self._advance()
        return ScrollAction(target=target_token.value.lower(), line=line)

    # scroll to element "selector" (完整语法，保持兼容)
    if self._check(TokenType.ELEMENT):
        self._advance()
        # v3.3: element 后的选择器也支持表达式
        if self._check(TokenType.STRING) or self._check(TokenType.IDENTIFIER):
            selector_expr = self._parse_expression()
        else:
            raise ParserError(...)
        return ScrollAction(target="element", selector=selector_expr, line=line)

    # scroll to <number> (数字位置)
    if self._check(TokenType.NUMBER):
        position = self._advance().value
        return ScrollAction(target="position", selector=position, line=line)

    # ✅ v3.3: 统一表达式支持（字符串或标识符）
    if self._check(TokenType.STRING) or self._check(TokenType.IDENTIFIER):
        selector = self._parse_expression()
        return ScrollAction(target="element", selector=selector, line=line)

    raise ParserError(...)
```

**关键变化**:
1. ✅ 字符串字面量走 `_parse_expression()` 而非 `self._advance().value`
2. ✅ `scroll to element "selector"` 中的选择器也改用表达式
3. ✅ 支持所有表达式类型（f-string, 成员访问, 数组索引等）
4. ✅ 100% 向后兼容（字符串字面量是表达式的子集）

#### 2. `_parse_extract_statement()` 修复

**修改前**:
```python
def _parse_extract_statement(self) -> ExtractStatement:
    """解析 extract 语句"""
    ...
    # from
    self._consume(TokenType.FROM, "期望 'from'")

    # ❌ 问题代码：字符串绕过表达式
    if self._check(TokenType.STRING):
        selector = self._consume(TokenType.STRING, "期望选择器").value
    else:
        selector = self._parse_expression()
    ...
```

**修改后**:
```python
def _parse_extract_statement(self) -> ExtractStatement:
    """解析 extract 语句 (v3.3: 完全表达式支持)"""
    ...
    # from
    self._consume(TokenType.FROM, "期望 'from'")

    # ✅ v3.3: 选择器支持完整表达式
    if self._check(TokenType.STRING) or self._check(TokenType.IDENTIFIER):
        selector = self._parse_expression()
    else:
        raise ParserError(
            self._peek().line,
            self._peek().column,
            self._peek().type.name,
            self._peek().value,
            "期望选择器字符串或表达式",
            "STRING | IDENTIFIER"
        )
    ...
```

**关键变化**:
1. ✅ 统一模式：`if self._check(TokenType.STRING) or self._check(TokenType.IDENTIFIER):`
2. ✅ 统一使用 `_parse_expression()` 解析
3. ✅ 添加明确的错误处理
4. ✅ 100% 向后兼容

---

## 📊 语义和行为

### 表达式支持

修复后，`scroll` 和 `extract` 的选择器参数支持以下表达式：

| 表达式类型 | 示例 | 说明 |
|-----------|------|------|
| 字符串字面量 | `"#section"` | 向后兼容，现在作为表达式 |
| 变量引用 | `section_selector` | 与修复前行为一致 |
| 成员访问 | `config.section` | ⭐ 新增能力 |
| 数组索引 | `selectors[0]` | ⭐ 新增能力 |
| f-string | `f"#{id}-section"` | ⭐ 新增能力 |
| 字符串拼接 | `base + "-section"` | ⭐ 新增能力 |
| 复杂表达式 | `items[index].selector` | ⭐ 新增能力 |

### 完整示例

```dsl
step "v3.3 Scroll & Extract Expression Examples":
    # === Scroll 表达式示例 ===

    # 字符串字面量（向后兼容）
    scroll to "#section1"

    # 变量引用
    let section_sel = "#section2"
    scroll to section_sel

    # 成员访问
    let config = {section: "#main-content"}
    scroll to config.section

    # 数组索引
    let sections = ["#intro", "#features", "#pricing"]
    scroll to sections[0]
    scroll to sections[1]

    # f-string（动态构建）
    let section_id = "pricing"
    scroll to f"#{section_id}"

    # 字符串拼接
    let prefix = "#section"
    scroll to prefix + "-intro"

    # 复杂表达式
    let pages = [
        {id: "home", selector: "#home-section"},
        {id: "about", selector: "#about-section"}
    ]
    scroll to pages[0].selector

    # === Extract 表达式示例 ===

    # 字符串字面量（向后兼容）
    extract text from "#code" into verification_code

    # 变量引用
    let input_sel = "#username"
    extract text from input_sel into username

    # 成员访问
    let form = {
        username_input: "#user",
        email_input: "#email"
    }
    extract text from form.username_input into user
    extract text from form.email_input into email

    # 数组索引
    let inputs = ["#field1", "#field2", "#field3"]
    extract text from inputs[0] into field1_value
    extract text from inputs[1] into field2_value

    # f-string（动态构建）
    let field_name = "username"
    extract text from f"#input-{field_name}" into user_input

    # 字符串拼接
    let base_sel = "#form"
    extract text from base_sel + "-username" into username

    # 复杂表达式
    let form_fields = [
        {name: "user", selector: "#username"},
        {name: "pass", selector: "#password"}
    ]
    extract text from form_fields[0].selector into username_value
    extract text from form_fields[1].selector into password_value

    log "All v3.3 expression tests passed!"
```

---

## 🔄 影响分析

### 1. 向后兼容性

**兼容性等级**: ✅ **100% 向后兼容**

**原因**:
- 字符串字面量是表达式的子集
- `"#section"` 解析为 `Literal("#section")`，运行时求值结果完全相同
- 标识符解析行为未改变
- 关键字语法（`scroll to top/bottom`）未改变

**测试验证**:
```dsl
# v3.2 代码（修复前）
scroll to "#section"               # ✅ 仍然工作
scroll to section_var              # ✅ 仍然工作
extract text from "#code" into x   # ✅ 仍然工作

# v3.3 代码（修复后）- 相同结果
scroll to "#section"               # ✅ 工作（现在是 Literal 表达式）
scroll to section_var              # ✅ 工作（行为不变）
extract text from "#code" into x   # ✅ 工作（现在是 Literal 表达式）
```

### 2. 复杂度影响

**代码复杂度**: ⬇️ **降低**

**原因**:
- 消除特殊情况处理（字符串字面量的直接取值）
- 统一解析路径（所有选择器都走表达式）
- 与 v3.2 修复后的 Actions 保持一致

**修改行数**: ~10 行代码（2 个方法，每个约 5 行）

### 3. 性能影响

**性能**: ➡️ **无明显影响**

- 字符串字面量从 `self._advance().value` 改为 `_parse_expression()`
- `_parse_expression()` 对字面量的开销极小（单次函数调用 + AST 节点创建）
- 运行时求值结果相同（Literal 节点直接返回值）

### 4. 用户体验

**提升**:
1. ✅ **一致性**: 所有语句的选择器参数行为一致
2. ✅ **功能性**: 解锁 f-string、成员访问、数组索引等高级特性
3. ✅ **无需迁移**: 现有代码无需修改

---

## 🧪 测试计划

### 1. 向后兼容性测试

```python
def test_scroll_backward_compatibility():
    """v3.3: 确保 scroll 字符串字面量仍然工作"""
    script = '''
    step "scroll test":
        scroll to "#section"
        scroll to top
        scroll to bottom
    '''
    ast = parse_script(script)

    # 验证 scroll to "#section" 生成 Literal 表达式
    scroll_stmt = ast.steps[0].statements[0]
    assert isinstance(scroll_stmt.selector, Literal)
    assert scroll_stmt.selector.value == "#section"

def test_extract_backward_compatibility():
    """v3.3: 确保 extract 字符串字面量仍然工作"""
    script = '''
    step "extract test":
        extract text from "#code" into result
    '''
    ast = parse_script(script)

    # 验证 selector 是 Literal 表达式
    extract_stmt = ast.steps[0].statements[0]
    assert isinstance(extract_stmt.selector, Literal)
    assert extract_stmt.selector.value == "#code"
```

### 2. 新功能测试

```python
def test_scroll_member_access():
    """v3.3: scroll 支持成员访问"""
    script = '''
    step "scroll member access":
        let config = {section: "#main"}
        scroll to config.section
    '''
    ast = parse_script(script)

    scroll_stmt = ast.steps[0].statements[1]
    assert isinstance(scroll_stmt.selector, MemberAccess)
    assert scroll_stmt.selector.object.name == "config"
    assert scroll_stmt.selector.member == "section"

def test_scroll_array_indexing():
    """v3.3: scroll 支持数组索引"""
    script = '''
    step "scroll array":
        let sections = ["#intro", "#features"]
        scroll to sections[0]
    '''
    ast = parse_script(script)

    scroll_stmt = ast.steps[0].statements[1]
    assert isinstance(scroll_stmt.selector, ArrayAccess)

def test_scroll_f_string():
    """v3.3: scroll 支持 f-string"""
    script = '''
    step "scroll f-string":
        let id = "section1"
        scroll to f"#{id}"
    '''
    ast = parse_script(script)

    scroll_stmt = ast.steps[0].statements[1]
    assert isinstance(scroll_stmt.selector, StringInterpolation)

def test_extract_member_access():
    """v3.3: extract 支持成员访问"""
    script = '''
    step "extract member access":
        let form = {input: "#username"}
        extract text from form.input into user
    '''
    ast = parse_script(script)

    extract_stmt = ast.steps[0].statements[1]
    assert isinstance(extract_stmt.selector, MemberAccess)

def test_extract_array_indexing():
    """v3.3: extract 支持数组索引"""
    script = '''
    step "extract array":
        let inputs = ["#field1", "#field2"]
        extract text from inputs[0] into value
    '''
    ast = parse_script(script)

    extract_stmt = ast.steps[0].statements[1]
    assert isinstance(extract_stmt.selector, ArrayAccess)

def test_extract_f_string():
    """v3.3: extract 支持 f-string"""
    script = '''
    step "extract f-string":
        let name = "username"
        extract text from f"#input-{name}" into user
    '''
    ast = parse_script(script)

    extract_stmt = ast.steps[0].statements[1]
    assert isinstance(extract_stmt.selector, StringInterpolation)

def test_extract_string_concat():
    """v3.3: extract 支持字符串拼接"""
    script = '''
    step "extract concat":
        let base = "#input"
        extract text from base + "-user" into value
    '''
    ast = parse_script(script)

    extract_stmt = ast.steps[0].statements[1]
    assert isinstance(extract_stmt.selector, BinaryOp)
    assert extract_stmt.selector.operator == "+"
```

### 3. 边缘情况测试

```python
def test_scroll_element_keyword_with_expression():
    """v3.3: scroll to element 后支持表达式"""
    script = '''
    step "scroll element expr":
        let sel = "#section"
        scroll to element sel
    '''
    ast = parse_script(script)

    scroll_stmt = ast.steps[0].statements[1]
    assert isinstance(scroll_stmt.selector, Identifier)
    assert scroll_stmt.selector.name == "sel"

def test_scroll_complex_expression():
    """v3.3: scroll 支持复杂表达式"""
    script = '''
    step "scroll complex":
        let pages = [{id: "home", sel: "#home"}]
        scroll to pages[0].sel
    '''
    ast = parse_script(script)

    scroll_stmt = ast.steps[0].statements[1]
    assert isinstance(scroll_stmt.selector, MemberAccess)
    assert isinstance(scroll_stmt.selector.object, ArrayAccess)
```

### 4. 回归测试

- 运行所有现有 `scroll` 和 `extract` 相关测试
- 确保 v3.2 Actions 测试仍然通过
- 验证整体测试套件通过率 ≥ 95%

---

## 📖 文档变更

### 1. MASTER.md

**Feature Matrix 更新**:

| ID | 功能 | 语法 | 已实现 | 版本 | Parser方法 | 测试 | 备注 |
|----|------|------|--------|------|-----------|------|------|
| 6.8 | Scroll | `scroll to [top\|bottom\|SEL\|NUM]` | ✅ | v1.0/**v3.3** | `_parse_scroll()` | ✅ | **v3.3: 完全表达式支持** |
| 7.5 | Extract | `extract [text\|attr\|html] from SEL into VAR` | ✅ | v1.0/**v3.3** | `_parse_extract_statement()` | ✅ | **v3.3: 完全表达式支持** |

**v3.3 Examples**:
```dsl
**v3.3 Examples** (⭐ Scroll & Extract Expression Support):
```dsl
# v3.3: Scroll with full expression support
scroll to config.section_selector      # Member access
scroll to sections[0]                  # Array indexing
scroll to f"#{id}-section"             # f-string
scroll to base + "-section"            # String concatenation

# v3.3: Extract with full expression support
extract text from config.input into data          # Member access
extract text from inputs[index] into value        # Array indexing
extract text from f"#field-{name}" into result    # f-string
extract text from prefix + "-input" into data     # String concatenation
```
```

### 2. CHANGELOG.md

添加 v3.3.0 版本记录（详见下一节）

---

## 🔄 替代方案

### 方案 A: 仅修复 scroll（部分修复）

**描述**: 只修复 `_parse_scroll()`，不修复 `_parse_extract_statement()`

**优点**: 工作量更小

**缺点**:
- ❌ 不一致性仍然存在
- ❌ extract 仍有 Bug
- ❌ 不符合"彻底修复"原则

**决定**: ❌ 不采用（必须全部修复）

### 方案 B: 延迟到 v4.0（破坏性修复）

**描述**: 等到下一个主版本再修复，允许破坏性更改

**优点**: 可以移除一些向后兼容代码

**缺点**:
- ❌ 用户需要等待更长时间
- ❌ Bug 继续存在
- ❌ 没有必要（当前方案 100% 兼容）

**决定**: ❌ 不采用（Bug 应尽快修复）

### 方案 C: 本提案（完全修复）

**描述**: v3.3 完全修复 scroll 和 extract，与 v3.2 修复模式一致

**优点**:
- ✅ 彻底解决问题
- ✅ 100% 向后兼容
- ✅ 代码一致性
- ✅ 用户体验提升

**决定**: ✅ **采用**

---

## ✅ 验收标准

### 1. 功能验收

- [ ] `scroll to "string"` 解析为 Literal 表达式
- [ ] `scroll to config.selector` 支持成员访问
- [ ] `scroll to selectors[0]` 支持数组索引
- [ ] `scroll to f"#{id}"` 支持 f-string
- [ ] `extract text from "string" into var` 解析为 Literal 表达式
- [ ] `extract text from config.input into var` 支持成员访问
- [ ] `extract text from inputs[0] into var` 支持数组索引
- [ ] `extract text from f"#{name}" into var` 支持 f-string

### 2. 兼容性验收

- [ ] 所有现有 scroll 测试通过
- [ ] 所有现有 extract 测试通过
- [ ] 所有 v3.2 Actions 测试仍然通过
- [ ] 整体测试套件通过率 ≥ 95%

### 3. 文档验收

- [ ] MASTER.md 更新 scroll 和 extract 版本标记
- [ ] CHANGELOG.md 添加 v3.3.0 条目
- [ ] v3.3 示例代码添加到 MASTER.md
- [ ] check_sync.py 验证通过

### 4. 代码质量验收

- [ ] 代码与 v3.2 修复模式一致
- [ ] 无新增复杂度
- [ ] 消除冗余代码路径
- [ ] 错误处理完整

---

## 📅 实施计划

1. **Step 1: 设计审查** (5分钟)
   - 语法一致性检查
   - 向后兼容性验证
   - 复杂度评估

2. **Step 2: 代码实现** (15分钟)
   - 修改 `_parse_scroll()` (parser.py:~815-850)
   - 修改 `_parse_extract_statement()` (parser.py:~1637-1640)
   - 代码审查

3. **Step 3: 测试** (20分钟)
   - 编写 8 个新测试（scroll 4个, extract 4个）
   - 运行回归测试
   - 验证通过率

4. **Step 4: 文档更新** (10分钟)
   - 更新 MASTER.md
   - 更新 CHANGELOG.md
   - 添加示例代码

5. **Step 5: 验证** (5分钟)
   - 运行 check_sync.py
   - 最终回归测试
   - 版本打标签

**总估时**: ~55 分钟

---

## 🎯 成功指标

- ✅ scroll 和 extract 完全支持表达式
- ✅ 100% 向后兼容
- ✅ 代码一致性（与 v3.2 修复模式一致）
- ✅ 所有测试通过
- ✅ 文档完整更新
- ✅ 无新增复杂度

---

**提案状态**: 📝 Under Review
**下一步**: 设计审查 → 批准 → 实施

---

**生成日期**: 2025-11-28
**相关提案**: PROPOSAL-003 (v3.2 Actions 修复)
**相关文档**: BACKWARD-COMPATIBILITY-CLEANUP-ANALYSIS.md
