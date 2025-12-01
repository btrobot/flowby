# AI 执行任务：修复示例文件问题

**任务 ID：** TASK-002
**创建时间：** 2025-12-02
**优先级：** 🟡 中等
**预计时间：** 15 分钟
**任务类型：** 代码修复

---

## 一、任务概述

### 背景

TASK-001 执行过程中发现了两个预存在的问题：
1. V3-EXAMPLES.flow 中存在 VR-003 违规（重复声明）
2. DSL-SYNTAX-CHEATSHEET.md 中布尔值大小写不统一

这些问题影响文档质量和示例可运行性，需要尽快修复。

### 目标

修复示例文件中的语法错误和文档不一致，确保所有示例代码可以正确运行。

### 你的职责

作为**执行者 AI**，你负责：
1. ✅ 修复 V3-EXAMPLES.flow 中的 VR-003 违规
2. ✅ 统一 DSL-SYNTAX-CHEATSHEET.md 中的布尔值大小写
3. ✅ 运行语法验证
4. ✅ 填写执行报告

### 不要做的事

1. ❌ **不要修改其他文件** - 只修改指定的 2 个文件
2. ❌ **不要修改注释** - 只修改代码和表格内容
3. ❌ **不要改变代码逻辑** - 只修复语法问题

---

## 二、修复任务

### 任务 1：修复 V3-EXAMPLES.flow VR-003 违规

#### 问题描述

**位置：** `grammar/V3-EXAMPLES.flow` 第 45-58 行

**当前代码（❌ 错误）：**
```flow
step "条件处理":
    if score >= 90:
        log "成绩优秀"
        const grade = "A"
    else if score >= 80:
        log "成绩良好"
        const grade = "B"     # ❌ VR-003: 重复声明 const grade
    else if score >= 70:
        log "成绩中等"
        const grade = "C"     # ❌ VR-003: 重复声明 const grade
    else:
        log "需要努力"
        const grade = "F"     # ❌ VR-003: 重复声明 const grade
```

**问题分析：**
- 在不同的 if-else 分支中多次使用 `const grade = ...` 声明同一个变量
- 违反了 VR-003 规则：同一作用域不能重复声明变量
- if-else 所有分支属于同一个作用域（step 块的子作用域）

#### 修复方案

**正确代码（✅ 修复后）：**
```flow
step "条件处理":
    let grade = ""            # 在 if-else 之前声明
    if score >= 90:
        log "成绩优秀"
        grade = "A"           # 改为赋值
    else if score >= 80:
        log "成绩良好"
        grade = "B"           # 改为赋值
    else if score >= 70:
        log "成绩中等"
        grade = "C"           # 改为赋值
    else:
        log "需要努力"
        grade = "F"           # 改为赋值
```

#### 修改步骤

1. 在第 46 行（`if score >= 90:` 之前）插入新行：`let grade = ""`
2. 修改第 48 行：`const grade = "A"` → `grade = "A"`
3. 修改第 51 行：`const grade = "B"` → `grade = "B"`
4. 修改第 54 行：`const grade = "C"` → `grade = "C"`
5. 修改第 57 行：`const grade = "F"` → `grade = "F"`

**关键点：**
- 使用 `let` 而不是 `const`，因为变量会被多次赋值
- 初始化为空字符串 `""`
- 确保缩进正确（4 空格，与 if 语句同级）

---

### 任务 2：统一布尔值大小写

#### 问题描述

**位置：** `grammar/DSL-SYNTAX-CHEATSHEET.md` 第 380 行

**当前内容（❌ 错误）：**
```markdown
| **布尔** | `true`, `false` |
```

**问题分析：**
- v3.0 采用 Python 风格，布尔值应为 `True`, `False`（首字母大写）
- 与文档其他部分不一致
- 与实际语法规范不符

#### 修复方案

**正确内容（✅ 修复后）：**
```markdown
| **布尔** | `True`, `False` |
```

#### 修改步骤

1. 找到第 380 行的字面量表格
2. 将 `true` 改为 `True`
3. 将 `false` 改为 `False`

**注意：**
- 只修改表格中的这一行
- 不要修改其他地方出现的 true/false（如注释、说明文字）

---

## 三、验证步骤

### 验证 1：V3-EXAMPLES.flow 语法检查

运行以下命令验证语法正确：

```bash
cd E:\cf\ads\flowby

python -c "
from src.flowby.lexer import Lexer
from src.flowby.parser import Parser

with open('grammar/V3-EXAMPLES.flow', 'r', encoding='utf-8') as f:
    source = f.read()

try:
    tokens = Lexer().tokenize(source)
    ast = Parser().parse(tokens)
    print('✅ V3-EXAMPLES.flow 语法正确')
except Exception as e:
    print(f'✗ V3-EXAMPLES.flow 有语法错误: {e}')
"
```

**预期输出：** `✅ V3-EXAMPLES.flow 语法正确`

### 验证 2：运行完整测试套件

```bash
pytest tests/ -v -q
```

**预期输出：** 所有测试通过，无新增失败

### 验证 3：手动检查修改

```bash
# 检查 V3-EXAMPLES.flow 的修改
git diff grammar/V3-EXAMPLES.flow

# 检查 DSL-SYNTAX-CHEATSHEET.md 的修改
git diff grammar/DSL-SYNTAX-CHEATSHEET.md
```

**预期：**
- V3-EXAMPLES.flow: 新增 1 行，修改 4 行
- DSL-SYNTAX-CHEATSHEET.md: 修改 1 行

---

## 四、执行报告模板

完成所有任务后，请创建文件 `.ai-tasks/TASK-002-report.md` 并填写以下内容：

```markdown
# TASK-002 执行报告

**执行者：** [你的名字/ID]
**开始时间：** YYYY-MM-DD HH:MM
**结束时间：** YYYY-MM-DD HH:MM
**实际耗时：** XX 分钟

---

## 执行统计

### 任务 1：V3-EXAMPLES.flow VR-003 修复

| 项目 | 状态 | 详情 |
|------|------|------|
| 新增声明行 | ✅ | let grade = "" |
| 修改行数 | ✅ | 4 行（const → 赋值） |
| 语法验证 | ✅ | 通过 |

### 任务 2：布尔值大小写统一

| 项目 | 状态 | 详情 |
|------|------|------|
| 修改位置 | ✅ | 第 380 行 |
| 修改内容 | ✅ | true/false → True/False |

---

## 验证结果

### 语法验证

```bash
# V3-EXAMPLES.flow 验证
python -c "..."

输出：
[粘贴验证输出]
```

### 测试套件

```bash
pytest tests/ -v -q

输出：
[粘贴测试结果]
```

---

## 遇到的问题

[如果没有问题，写"无"]

### 问题 1：[如果有问题，描述]

**位置：** 文件名:行号
**描述：** [问题详情]
**解决方案：** [如何处理]

---

## 最终统计

- **修改文件数：** 2 个
- **新增代码行：** 1 行
- **修改代码行：** 5 行
- **语法验证：** 通过 ✅
- **测试结果：** 通过 ✅

---

## 签名

执行完成，请求架构师 AI 审查。

**执行者：** [你的名字]
**日期：** YYYY-MM-DD
```

---

## 五、常见问题

### Q1: 为什么不能在每个分支中使用 const？

**A:** 在 Flowby DSL 中，if-else 的所有分支共享同一个作用域。多次声明 `const grade` 会违反 VR-003 规则（同一作用域不能重复声明）。

### Q2: 为什么使用 let 而不是 const？

**A:** 因为 `grade` 变量会在不同分支中被赋予不同的值，需要可变性。`const` 声明的变量不能被重新赋值（VR-002 规则）。

### Q3: 初始值为什么用空字符串 ""？

**A:** 因为 `grade` 最终会被赋值为字符串（"A", "B", "C", "F"），使用相同类型的初始值是最佳实践。也可以使用 `None`，但空字符串更明确。

### Q4: 为什么不修改注释中的 true/false？

**A:** 注释是说明性文字，可能在描述旧版本语法或者其他编程语言的约定。只需要确保代码示例和正式语法定义使用正确的 `True/False`。

---

## 六、成功标准

任务被视为成功完成，当且仅当：

1. ✅ V3-EXAMPLES.flow 语法验证通过
2. ✅ 所有测试套件通过（无新增失败）
3. ✅ Git diff 显示正确的修改（+1 行，~5 行）
4. ✅ 没有引入其他问题
5. ✅ 执行报告完整填写

---

**祝执行顺利！** 🚀

这是一个简单的任务，应该在 15 分钟内完成。如有任何疑问，请在报告中详细说明。
