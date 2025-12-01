# 测试修复任务清单

## 问题概述

项目启用了 VR-001 语义规则：**变量使用前必须声明**。
当前有 142 个测试失败，原因是测试代码中使用了未声明的变量。

**错误示例：**
```
[语法错误] 文件 在使用前先用 'let' 或 'const' 声明变量, 第 3 行: 未定义的变量 'x'（VR-001 违规）
```

## 修复原则

**简单规则：在使用变量之前，先用 `let` 声明它们。**

### 修复示例

**修改前（❌ 错误）：**
```python
source = """
if x > 0:
    let y = 1
"""
```

**修改后（✅ 正确）：**
```python
source = """
let x = 1
if x > 0:
    let y = 1
"""
```

---

## 需要修复的文件列表

### 1. tests/grammar_alignment/test_v3_00_indentation.py

**问题：** 多个测试使用了未声明的变量

**需要修复的测试方法：**

#### test_dedent_multiple_levels (行 88-99)
```python
# 当前代码使用了未声明的 x, y
source = """
step "outer":
    if x > 0:
        if y > 0:
            let z = 1
step "sibling":
    let a = 2
"""

# 修复方案：添加变量声明
source = """
let x = 1
let y = 1
step "outer":
    if x > 0:
        if y > 0:
            let z = 1
step "sibling":
    let a = 2
"""
```

#### test_nested_if_blocks (行 118-130)
```python
# 当前代码使用了未声明的 x, y
source = """
if x > 0:
    if y > 0:
        let z = 1
    else:
        let z = 2
else:
    let z = 3
"""

# 修复方案
source = """
let x = 1
let y = 1
if x > 0:
    if y > 0:
        let z = 1
    else:
        let z = 2
else:
    let z = 3
"""
```

#### test_for_loop_indent (行 149-157)
```python
# 当前代码使用了未声明的 items
source = """
for item in items:
    let x = item
    let y = x + 1
"""

# 修复方案
source = """
let items = [1, 2, 3]
for item in items:
    let x = item
    let y = x + 1
"""
```

#### test_when_block_indent (行 162-172)
```python
# 当前代码使用了未声明的 status
source = """
when status:
    "active":
        let x = 1
    "inactive":
        let x = 2
"""

# 修复方案
source = """
let status = "active"
when status:
    "active":
        let x = 1
    "inactive":
        let x = 2
"""
```

#### test_8_space_nested (行 195-199)
```python
# 当前代码
source = 'step "test":\n    if x:\n        let y = 1'

# 修复方案
source = 'let x = True\nstep "test":\n    if x:\n        let y = 1'
```

#### test_12_space_triple_nested (行 201-205)
```python
# 当前代码
source = 'step "test":\n    if x:\n        if y:\n            let z = 1'

# 修复方案
source = 'let x = True\nlet y = True\nstep "test":\n    if x:\n        if y:\n            let z = 1'
```

#### test_two_tabs_nested (行 243-247)
```python
# 当前代码
source = "step \"test\":\n\tif x:\n\t\tlet y = 1"

# 修复方案
source = "let x = True\nstep \"test\":\n\tif x:\n\t\tlet y = 1"
```

#### test_5_level_deep_nesting (行 350-363)
```python
# 当前代码使用了未声明的 a, b, c, d
source = """
step "level1":
    if a:
        step "level2":
            if b:
                step "level3":
                    if c:
                        if d:
                            let e = 1
"""

# 修复方案
source = """
let a = True
let b = True
let c = True
let d = True
step "level1":
    if a:
        step "level2":
            if b:
                step "level3":
                    if c:
                        if d:
                            let e = 1
"""
```

#### test_multiple_dedents_in_sequence (行 365-376)
```python
# 当前代码使用了未声明的 x, y
source = """
if x:
    if y:
        let a = 1
let b = 2
let c = 3
"""

# 修复方案
source = """
let x = True
let y = True
if x:
    if y:
        let a = 1
let b = 2
let c = 3
"""
```

#### test_else_if_chain_indentation (行 378-391)
```python
# 当前代码使用了未声明的 x
source = """
if x == 1:
    let y = "one"
else:
    if x == 2:
        let y = "two"
    else:
        let y = "other"
"""

# 修复方案
source = """
let x = 1
if x == 1:
    let y = "one"
else:
    if x == 2:
        let y = "two"
    else:
        let y = "other"
"""
```

#### test_when_cases_same_indent (行 393-404)
```python
# 当前代码使用了未声明的 status
source = """
when status:
    "active":
        let x = 1
    "pending":
        let x = 2
    "closed":
        let x = 3
"""

# 修复方案
source = """
let status = "active"
when status:
    "active":
        let x = 1
    "pending":
        let x = 2
    "closed":
        let x = 3
"""
```

#### test_for_loop_with_nested_if (行 406-416)
```python
# 当前代码使用了未声明的 items
source = """
for item in items:
    if item > 5:
        let x = "big"
    else:
        let x = "small"
"""

# 修复方案
source = """
let items = [1, 5, 10]
for item in items:
    if item > 5:
        let x = "big"
    else:
        let x = "small"
"""
```

#### test_looks_like_python_if (行 435-442)
```python
# 当前代码使用了未声明的 x
source = """
if x > 0:
    let y = 1
else:
    let y = 2
"""

# 修复方案
source = """
let x = 1
if x > 0:
    let y = 1
else:
    let y = 2
"""
```

#### test_looks_like_python_for (行 444-450)
```python
# 当前代码使用了未声明的 items
source = """
for item in items:
    let x = item
"""

# 修复方案
source = """
let items = [1, 2, 3]
for item in items:
    let x = item
"""
```

---

### 2. tests/grammar_alignment/test_v3_01_variables.py

#### test_assignment_expression (行 92-99)
```python
# 当前代码使用了未声明的 x
source = """
let y = (x = 10)
"""

# 修复方案
source = """
let x = 0
let y = (x = 10)
"""
```

---

### 3. tests/grammar_alignment/test_v3_02_control_flow.py

**几乎所有使用变量的测试都需要修复**

通用修复模式：
- 如果使用 `x`，添加 `let x = 1` 或 `let x = True`
- 如果使用 `items` / `users` / `numbers`，添加 `let items = [1, 2, 3]`
- 如果使用 `status` / `role`，添加 `let status = "active"`
- 如果使用 `count` / `total`，添加 `let count = 0`

**需要修复的测试方法（约30个）：**
- test_step_with_nested_if
- test_if_basic
- test_if_else
- test_if_else_if
- test_if_with_python_bool
- test_if_with_none_check
- test_nested_if
- test_if_with_complex_condition
- test_if_with_end_keyword_error
- test_when_basic
- test_when_with_otherwise
- test_when_multiple_cases
- test_when_nested_statements
- test_when_with_complex_expression
- test_when_string_case
- test_when_number_case
- test_when_boolean_case
- test_when_none_case
- test_for_basic
- test_for_with_array
- test_for_with_range
- test_for_nested
- test_for_with_break
- test_for_with_continue
- test_while_basic
- test_while_with_counter
- test_while_with_break
- test_while_with_continue
- test_while_nested

---

### 4. tests/grammar_alignment/test_v3_03_navigation.py

**约10个测试需要修复**

---

### 5. tests/grammar_alignment/test_v3_04_wait.py

**约5个测试需要修复**

---

### 6. tests/grammar_alignment/test_v3_05_selection.py

**约5个测试需要修复**

---

### 7. tests/grammar_alignment/test_v3_06_actions.py

**约8个测试需要修复**

---

### 8. tests/grammar_alignment/test_v3_07_assertions.py

**约6个测试需要修复**

---

### 9. tests/grammar_alignment/test_v3_09_extraction.py

**约3个测试需要修复**

---

### 10. tests/grammar_alignment/test_v3_10_utilities.py

**约5个测试需要修复**

---

### 11. tests/grammar_alignment/test_v3_builtin_functions.py

**约8个测试需要修复**

---

### 12. tests/grammar_alignment/test_v3_data_types.py

**约4个测试需要修复**

---

### 13. tests/grammar_alignment/test_v3_expressions.py

**约15个测试需要修复**

---

### 14. tests/grammar_alignment/test_v3_python_alignment.py

**约4个测试需要修复**

---

### 15. tests/grammar_alignment/test_v3_system_variables.py

**约3个测试需要修复**

---

### 16. tests/grammar_alignment/test_while_loop.py

**约6个测试需要修复**

---

### 17. tests/unit/dsl/test_expression_evaluator.py

**约8个测试需要修复**

---

### 18. tests/unit/dsl/test_operator_precedence.py

**约12个测试需要修复**

---

## 自动化修复脚本建议

可以编写 Python 脚本来自动化修复：

```python
import re

def fix_test_source(source_code):
    """自动在 source = \"\"\" 后添加变量声明"""

    # 检测使用的变量
    variables_used = set()

    # 常见变量模式
    patterns = {
        r'\bif\s+(\w+)': lambda m: m.group(1),
        r'\bfor\s+\w+\s+in\s+(\w+)': lambda m: m.group(1),
        r'\bwhen\s+(\w+)': lambda m: m.group(1),
    }

    for pattern, extractor in patterns.items():
        for match in re.finditer(pattern, source_code):
            var = extractor(match)
            if var not in ['True', 'False', 'None']:
                variables_used.add(var)

    # 生成声明
    declarations = []
    for var in sorted(variables_used):
        if var in ['items', 'users', 'numbers', 'data']:
            declarations.append(f"let {var} = [1, 2, 3]")
        elif var in ['status', 'role', 'name']:
            declarations.append(f'let {var} = "active"')
        else:
            declarations.append(f"let {var} = 1")

    # 插入声明
    if declarations:
        lines = source_code.split('\n')
        # 在第一个非空行前插入
        for i, line in enumerate(lines):
            if line.strip():
                lines.insert(i, '\n'.join(declarations))
                break
        return '\n'.join(lines)

    return source_code
```

---

## 优先级

**高优先级（先修复这些）：**
1. test_v3_00_indentation.py - 16 个失败
2. test_v3_02_control_flow.py - 30 个失败
3. test_v3_expressions.py - 15 个失败

**中优先级：**
4. test_operator_precedence.py - 12 个失败
5. test_v3_builtin_functions.py - 8 个失败
6. test_expression_evaluator.py - 8 个失败

**低优先级（其余文件）：**
7-18. 其他测试文件

---

## 验证方法

修复后运行测试验证：

```bash
# 验证单个文件
pytest tests/grammar_alignment/test_v3_00_indentation.py -v

# 验证所有测试
pytest tests/ -v --tb=short

# 快速统计
pytest tests/ --tb=no -q | tail -1
```

预期结果：
```
======= 1181 passed, 10 skipped in XX.XXs =======
```

---

## 注意事项

1. **不要修改 Parser 或语义检查逻辑** - VR-001 规则是正确的，应该保留
2. **只修改测试代码** - 在测试的 `source = """..."""` 字符串中添加变量声明
3. **保持代码格式** - 使用正确的缩进（4空格）
4. **合理的初始值** - 根据变量用途选择合适的初始值
   - 布尔条件：`let x = True` 或 `let x = 1`
   - 数组遍历：`let items = [1, 2, 3]`
   - 字符串比较：`let status = "active"`
5. **最小修改原则** - 只添加必要的声明，不改变测试意图

---

## 总结

- **总失败数：** 142 个测试
- **主要原因：** VR-001 语义规则（变量使用前必须声明）
- **修复方法：** 在测试的 source 代码中，使用变量前先用 `let` 声明
- **预计工作量：** 每个测试约 1-2 分钟，总计约 2-3 小时

Good luck! 🚀
