# Grammar Proposal #003: Unified Selector Expression Support

> **提案编号**: #003
> **提出日期**: 2025-11-28
> **提出人**: DSL Core Team
> **状态**: 📝 Under Review
> **目标版本**: 3.2.0
> **影响级别**: PATCH (Bug Fix) + MINOR (Enhancement)

---

## 📋 提案摘要

修复 7 个 Action 语句中选择器参数的表达式解析不一致问题，统一所有选择器参数都支持完整的表达式语法。

**问题**: 当前部分 Actions 的选择器参数仅支持字符串字面量或简单标识符，不支持成员访问、数组索引、f-string 等复杂表达式，导致用户体验不一致且需要使用变通方案。

**解决方案**: 统一使用 `_parse_expression()` 解析所有选择器参数，使其支持完整的表达式语法。

---

## 🎯 动机和背景

### 问题描述

在 v3.1 中，不同 Action 语句的选择器参数解析方式不一致：

**当前行为**:
```dsl
# ✅ 字符串字面量 - 支持
click "#submit"
clear "#input"
hover "#menu"

# ✅ 简单标识符 - 支持
click btn_selector
clear input_var
hover menu_selector

# ❌ 成员访问 - 不支持（被字符串字面量阻断）
click config.button_selector  # 解析失败
clear form.input_selector
hover nav.menu_selector

# ❌ 数组索引 - 不支持
click buttons[0]
clear inputs[index]

# ❌ f-string - 不支持
click f"#{id}-button"
clear f"input-{field_name}"
```

**根本原因**:

Parser 中存在错误的解析模式：

```python
# ❌ 当前错误模式（7 个 Actions 都有这个问题）
selector = None
if self._check(TokenType.STRING):
    selector = self._advance().value  # 直接取字面量，阻断表达式解析
elif self._check(TokenType.IDENTIFIER):
    selector = self._parse_expression()  # 仅标识符开头能用表达式
```

**导致的问题**:
1. **不一致性**: `navigate to config.url` ✅ 支持，但 `click config.button` ❌ 不支持
2. **功能限制**: 无法使用配置驱动、数组操作、动态构建等高级特性
3. **用户困扰**: 需要使用变通方案（临时变量或 `where css=...`）

### 为什么现有功能不够？

**当前做法（变通方案）**:

```dsl
# 方案 1: 使用临时变量
let selector = config.button_selector
click selector

# 方案 2: 使用 select + click
select button where css = config.button_selector
click

# 方案 3: 提前构建字符串
let btn = f"#{id}-button"
click btn
```

**问题**:
- 代码冗长，需要额外变量
- `select + click` 模式不自然
- 与其他语句行为不一致（如 `navigate to` 完全支持表达式）

---

## 💡 提议的解决方案

### 语法设计

#### 统一解析模式

将所有选择器参数改为统一的表达式解析：

```python
# ✅ 修复后的统一模式
selector = None
if self._check(TokenType.STRING) or self._check(TokenType.IDENTIFIER):
    selector = self._parse_expression()  # 统一使用表达式解析
```

#### 具体语法

修复后，所有选择器参数都支持完整表达式：

```dsl
# ✅ 字符串字面量（向后兼容）
click "#submit"
clear "#input"
hover "#menu"
check "#agree"
upload file "/path/file.pdf" to "#upload"

# ✅ 变量引用
click button_selector
clear input_var
hover menu_selector

# ✅ 成员访问（新支持）
click config.button_selector
clear form.input_selector
hover nav.menu_selector

# ✅ 数组索引（新支持）
click buttons[0]
clear inputs[index]
hover menu_items[i]

# ✅ 字符串拼接（新支持）
click base_selector + "-button"
clear "input-" + field_name

# ✅ f-string（新支持）
click f"#{id}-button"
clear f"input-{field_name}"
hover f".menu-{section}"
```

### 详细说明

#### 核心机制

1. **解析阶段**（Parser）:
   - 移除字符串字面量的特殊处理
   - 统一使用 `_parse_expression()` 解析选择器参数
   - 字符串字面量作为 `Literal` 表达式节点（向后兼容）

2. **求值阶段**（Executor）:
   - 如果参数是表达式对象，调用 `evaluate_expression()` 求值
   - 如果参数是字符串，直接使用（向后兼容旧代码）
   - 确保最终结果是字符串类型

3. **类型安全**:
   - 所有选择器最终都必须求值为字符串
   - 非字符串结果自动转为字符串

#### 受影响的 Actions

| # | Action | 参数 | 当前状态 | 修复后 |
|---|--------|------|---------|-------|
| 1 | `clear [SELECTOR]` | selector | 🟡 半支持 | ✅ 完全支持 |
| 2 | `click [SELECTOR]` | selector | 🟡 半支持 | ✅ 完全支持 |
| 3 | `double click [SELECTOR]` | selector | 🟡 半支持 | ✅ 完全支持 |
| 4 | `right click [SELECTOR]` | selector | 🟡 半支持 | ✅ 完全支持 |
| 5 | `hover [SELECTOR]` | selector | 🟡 半支持 | ✅ 完全支持 |
| 6 | `check/uncheck SELECTOR` | selector | ⚠️ 仅字面量 | ✅ 完全支持 |
| 7 | `upload file PATH to SELECTOR` | file_path, selector | 🟡 半支持 | ✅ 完全支持 |

### 使用示例

#### 示例 1: 配置驱动

```dsl
/**meta
desc: 从配置对象读取选择器
*/

let config = {
    submit_button: "#submit-btn",
    email_input: "#email",
    agree_checkbox: "#agree"
}

# v3.2: 直接使用成员访问
click config.submit_button
clear config.email_input
check config.agree_checkbox
```

#### 示例 2: 数组操作

```dsl
/**meta
desc: 批量点击按钮列表
*/

let buttons = ["#btn1", "#btn2", "#btn3"]

for btn in buttons:
    click btn  # v3.2: 直接使用变量
    wait 500 ms
```

#### 示例 3: 动态构建

```dsl
/**meta
desc: 动态构建选择器
*/

let user_id = "12345"
let field_name = "email"

# v3.2: f-string 直接使用
click f"#user-{user_id}-submit"
clear f"input-{field_name}"
hover f".profile-{user_id}"
```

#### 示例 4: 条件选择

```dsl
/**meta
desc: 根据条件选择不同按钮
*/

let is_mobile = True
let button_selector = is_mobile ? "#mobile-btn" : "#desktop-btn"

# v3.2: 三元表达式结果
click button_selector
```

---

## 🔍 语义和行为

### 执行语义

1. **解析阶段**:
   - 选择器参数解析为表达式 AST 节点
   - 字符串字面量解析为 `Literal` 节点
   - 标识符解析为 `Identifier` 或更复杂的表达式

2. **执行阶段**:
   ```python
   # Executor 伪代码
   if isinstance(selector, Expression):
       resolved = evaluate_expression(selector, context)
       selector_str = str(resolved)
   else:
       selector_str = selector  # 向后兼容字符串
   ```

3. **类型转换**:
   - 最终选择器必须是字符串
   - 非字符串自动通过 `str()` 转换
   - 数字、布尔值等都转为字符串

### 作用域规则

- 表达式在当前作用域求值
- 可以访问所有可见变量
- 遵循标准表达式求值规则

### 错误处理

| 错误情况 | 行为 | 示例 |
|---------|------|------|
| 未定义变量 | 运行时错误 | `click undefined_var` |
| 类型错误 | 自动转字符串 | `click 123` → `"123"` |
| 空选择器 | 运行时错误 | `click ""` |
| 非字符串结果 | 自动转换 | `click True` → `"True"` |

---

## 📊 影响分析

### 版本影响

- [x] **PATCH** (Bug Fix - 修复解析不一致)
  - 修复错误的解析逻辑
  - 字符串字面量应被解析为表达式
- [x] **MINOR** (New Feature - 扩展表达式支持)
  - 新增成员访问、数组索引等支持
  - 完全向后兼容

**版本号**: 3.1.0 → 3.2.0

### 兼容性

#### 向后兼容性

- ✅ 与现有语法 100% 兼容
- **原因**: 字符串字面量是表达式的子集

**v3.1 代码在 v3.2 中完全有效**:
```dsl
# v3.1 语法在 v3.2 中仍然有效
click "#submit"          # ✓ 字符串字面量（作为表达式解析）
click button_selector    # ✓ 变量引用
clear                    # ✓ 无参数形式
```

#### 现有功能影响

| 现有功能 | 影响 | 说明 |
|---------|------|------|
| 字符串字面量 | 无 | 仍然工作（作为表达式） |
| 变量引用 | 无 | 行为不变 |
| 其他 Actions | 无 | 不受影响 |
| 表达式系统 | 扩展 | 新增使用场景 |

### 学习曲线

- **新手**: 容易（行为更一致）
- **现有用户**: 非常容易（无需迁移）
- **原因**: 向后兼容，新功能是自然扩展

### 语法复杂度

**v3.1 状态**:
```
语句类型: 25/30
表达式层次: 9/10
关键字: 80+/100
```

**v3.2 添加后**:
```
语句类型: 25/30  (无变化)
表达式层次: 9/10 (无变化)
关键字: 80+/100  (无变化)
```

**评估**: ✅ 在限制内（仅修复现有特性，未增加新语句或关键字）

---

## 🛠️ 实施方案

### Parser 变更

**修改的方法** (7 个):

1. `_parse_clear()` - parser.py:794-806
2. `_parse_click()` - parser.py:736-773
3. `_parse_click_multiword()` - parser.py:698-734
4. `_parse_hover()` - parser.py:775-792
5. `_parse_check()` - parser.py:856-862
6. `_parse_upload()` - parser.py:864-906 (两个参数)

**修改模式**:

```python
# 修改前
selector = None
if self._check(TokenType.STRING):
    selector = self._advance().value  # ❌
elif self._check(TokenType.IDENTIFIER):
    selector = self._parse_expression()  # 半支持

# 修改后
selector = None
if self._check(TokenType.STRING) or self._check(TokenType.IDENTIFIER):
    selector = self._parse_expression()  # ✅ 统一支持
```

**特殊情况处理**:

`_parse_click()` 和 `_parse_click_multiword()` 需要避免将 `and` 关键字误解析为选择器：

```python
# 修改后（带 and 检测）
selector = None
if self._check(TokenType.STRING):
    selector = self._parse_expression()
elif self._check(TokenType.IDENTIFIER):
    # 检查是否是 "and" 关键字
    if self._peek().value.lower() != "and":
        selector = self._parse_expression()
```

### Interpreter 变更

**无需修改** - 现有的 Executor 已经正确处理表达式对象：

```python
# interaction.py 中已有的正确逻辑
if isinstance(selector, Expression):
    resolved_selector = str(evaluate_expression(selector, context))
else:
    resolved_selector = context.resolve_variables(selector)
```

### Lexer 变更

**无需变更** - 使用现有 Token

### 实现难度

- [x] **简单**
  - 只需修改 parser 的 7 个方法
  - 每个方法改动 2-5 行
  - 不涉及 AST 节点变更
  - 不涉及 Executor 变更
  - 预计用时：1-2 小时

### 依赖项

- [x] 依赖现有的表达式解析系统
- [x] 依赖现有的 `_parse_expression()` 方法
- [x] 无额外依赖

---

## 🧪 测试计划

### 测试用例

#### 向后兼容性测试 (7 tests)

```python
def test_clear_string_literal():
    """测试字符串字面量仍然工作"""
    source = """
    clear "#input"
    """
    # 断言: 解析成功，选择器为 "#input"

def test_click_variable():
    """测试变量引用仍然工作"""
    source = """
    let selector = "#button"
    click selector
    """
    # 断言: 解析成功，点击正确的按钮
```

#### 新功能测试 (21 tests)

**成员访问** (7 tests):
```python
def test_click_member_access():
    """测试成员访问"""
    source = """
    let config = {button: "#submit"}
    click config.button
    """
    # 断言: 解析成功，点击 "#submit"
```

**数组索引** (7 tests):
```python
def test_clear_array_index():
    """测试数组索引"""
    source = """
    let inputs = ["#input1", "#input2"]
    clear inputs[0]
    """
    # 断言: 解析成功，清空 "#input1"
```

**f-string** (7 tests):
```python
def test_hover_fstring():
    """测试 f-string"""
    source = """
    let id = "123"
    hover f"#item-{id}"
    """
    # 断言: 解析成功，悬停在 "#item-123"
```

#### 错误处理测试 (3 tests)

```python
def test_click_undefined_variable():
    """测试未定义变量"""
    source = """
    click undefined_var
    """
    # 断言: 抛出 NameError

def test_click_empty_selector():
    """测试空选择器"""
    source = """
    click ""
    """
    # 断言: 运行时错误

def test_click_and_keyword():
    """测试 and 关键字不被误解析"""
    source = """
    click "#button" and wait 5
    """
    # 断言: 正确解析为 click + wait
```

### 测试覆盖率目标

- [x] 行覆盖率 ≥ 90%
- [x] 分支覆盖率 ≥ 85%
- [x] 所有 7 个 Actions 都有测试
- [x] 所有表达式类型都有测试

### 测试文件

- 新建: `tests/dsl/test_v3_2_selector_expressions.py` (31 tests)
- 更新: `tests/grammar_alignment/test_v3_06_actions.py` (确保回归测试)

---

## 📚 文档变更

### 需要更新的文档

- [ ] `MASTER.md` - 更新 7 个 Actions 的 Notes 列
- [ ] `CHANGELOG.md` - 添加 v3.2.0 变更记录
- [ ] `ACTIONS-EXPRESSION-ANALYSIS.md` - 标记为已完成
- [ ] `DSL-GRAMMAR.ebnf` - 更新 Action 规则（如需要）
- [ ] `DSL-GRAMMAR-QUICK-REFERENCE.md` - 添加新示例
- [ ] `DSL-SYNTAX-CHEATSHEET.md` - 更新速查表

### 文档更新计划

**MASTER.md 更新**:
```markdown
| 6.6 | Clear | `clear [SEL]` | ✅ | v1.0/v3.2 | `_parse_clear()` | ✅ | **v3.2: 完全表达式支持** |
| 6.2 | Click | `click [SEL]` | ✅ | v1.0/v3.2 | `_parse_click()` | ✅ | **v3.2: 完全表达式支持** |
...
```

**CHANGELOG.md 新增**:
```markdown
## [3.2.0] - 2025-11-28

### 🐛 Fixed (Bug Fix)
- 修复 7 个 Actions 的选择器参数解析不一致问题
- 字符串字面量现在正确解析为表达式

### ✨ Added (Enhancement)
- 所有选择器参数现在支持完整表达式语法
- 支持成员访问、数组索引、f-string 等
```

---

## 🔄 替代方案

### 方案 1: 保持现状（拒绝）

**理由**:
- 不一致性影响用户体验
- 需要大量变通代码
- 与设计原则冲突（一致性原则）

### 方案 2: 仅修复 Bug，不扩展功能（不推荐）

**理由**:
- 解析字符串字面量为表达式本身就是 Bug 修复
- 表达式支持是修复的自然结果
- 分离修复和扩展会增加复杂度

### 采用的方案: 统一修复 + 扩展（推荐）

**理由**:
- 一次性解决所有问题
- 向后兼容
- 提升一致性和易用性
- 实现简单，风险低

---

## 💬 讨论记录

### 关键反馈

**技术可行性**:
> ✅ 修改量小（~20 行代码），风险低，完全向后兼容

**用户价值**:
> ✅ 显著提升易用性，减少变通代码，统一行为

**设计一致性**:
> ✅ 与 `navigate to`、`type into`、`select option` 等语句行为一致

### 设计决策

**决策 1**: 统一使用 `_parse_expression()` 而非特殊处理字符串
- **理由**: 字符串字面量是表达式的子集，应统一处理

**决策 2**: 在 Parser 层面修复，不修改 Executor
- **理由**: Executor 已经正确处理表达式对象，无需改动

**决策 3**: 包含在 v3.2 而非 v3.1.1
- **理由**: 虽然是 Bug 修复，但同时扩展了功能，符合 MINOR 版本定义

---

## ✅ 决策

### 核心团队评审

- [ ] 技术可行性: 待评审
- [ ] 语法一致性: 待评审
- [ ] 复杂度控制: 待评审
- [ ] 文档完整性: 待评审

### 最终决定

- **状态**: 📝 Under Review
- **提议日期**: 2025-11-28
- **审批人**: 待定
- **预计实施**: v3.2.0

### 批准标准

1. ✅ 向后兼容 v3.1
2. ✅ 测试覆盖率 ≥ 90%
3. ✅ 所有 7 个 Actions 都修复
4. ✅ 文档完整更新
5. ✅ `check_sync.py` 通过

---

## 📅 实施时间线

### Phase 1: 设计评审
- [ ] 技术评审（预计 1 天）
- [ ] 社区讨论（如需要）

### Phase 2: 实施阶段
- [ ] Parser 修改（1-2 小时）
- [ ] 测试编写（2-3 小时）
- [ ] 代码审查

### Phase 3: 文档阶段
- [ ] MASTER.md 更新
- [ ] CHANGELOG.md 更新
- [ ] 其他文档更新

### Phase 4: 验收阶段
- [ ] 所有测试通过
- [ ] check_sync.py 验证
- [ ] 版本号更新到 v3.2.0

**预计总用时**: 1 天

---

## 📎 附录

### 参考资料

- ACTIONS-EXPRESSION-ANALYSIS.md (完整分析报告)
- MASTER.md (语法主控文档)
- GOVERNANCE.md (治理流程)

### 相关文件

**需要修改的代码**:
- `src/registration_system/dsl/parser.py` (7 个方法)

**需要添加的测试**:
- `tests/dsl/test_v3_2_selector_expressions.py` (新建)

**需要更新的文档**:
- `grammar/MASTER.md`
- `grammar/CHANGELOG.md`
- `ACTIONS-EXPRESSION-ANALYSIS.md`

### 相关提交

- 无（新提案）

---

**提案状态**: 📝 Under Review
**最后更新**: 2025-11-28
**维护者**: DSL Core Team
