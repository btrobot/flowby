# AI 执行任务：文档语法清理

**任务 ID：** TASK-001
**创建时间：** 2025-12-01
**优先级：** 🔴 高
**预计时间：** 95 分钟
**任务类型：** 批量文本替换和修改

---

## 一、任务概述

### 背景

Flowby DSL 在 v3.0 版本进行了重大语法革命，采用 Python 风格的纯缩进语法。但文档中仍有 100+ 处 v2.0 旧语法残留，需要系统清理。

### 目标

清理所有核心文档和辅助文档中的旧语法，确保文档一致性 100%。

### 你的职责

作为**执行者 AI**，你负责：
1. ✅ 按照本文档的指示批量修改文件
2. ✅ 严格遵循修改模板
3. ✅ 保持代码格式（4 空格缩进）
4. ✅ 完成后运行验证脚本
5. ✅ 填写执行报告

### 不要做的事

1. ❌ **不要修改 CHANGELOG.md** - 这是历史文档，由架构师 AI 手动处理
2. ❌ **不要修改 MASTER.md** - 需要理解上下文，由架构师 AI 处理
3. ❌ **不要修改 Proposal 文档** - 需要分类判断，由架构师 AI 处理
4. ❌ **不要自己决定修改策略** - 严格按照本文档的模板
5. ❌ **不要修改源代码** - 只修改文档

---

## 二、修改规则

### 规则 1：删除 `end` 关键字

**适用：** 所有代码块中的 `end if`, `end step`, `end for`, `end while`, `end when`, `end function`

**模式识别：**
```regex
end if
end step
end for
end while
end when
end function
```

**操作：** 直接删除整行

**注意：**
- 删除 `end` 行后，检查上一行的缩进是否正确
- 不要破坏代码块的缩进结构

### 规则 2：替换 `null` 为 `None`

**适用：** 所有出现 `null` 的地方

**模式识别：**
```regex
\bnull\b
```

**操作：** 替换为 `None`（大写 N）

**示例：**
- `let data = null` → `let data = None`
- `Null` → `None`
- `NULL` → `None`

**不要替换：**
- 在英文句子中的 "null" 单词（如 "null pointer"）
- 在注释中说明"旧语法使用 null"的地方

### 规则 3：保持缩进一致

**标准：** 4 空格缩进

**检查：**
- 每个代码块的缩进必须是 4 的倍数
- 不要混用 Tab 和空格
- 删除 `end` 后，确保后续代码的缩进正确

---

## 三、文件清单和修改指令

### Phase 1：核心语法参考文档（必须完成）

#### 文件 1：`grammar/DSL-SYNTAX-CHEATSHEET.md`

**位置：** 16 处 `end` 关键字

**行号：** 48, 65, 75, 84, 97, 109, 117, 124, 914, 945, 954, 961, 970, 992, 1005, 1006

**任务：**
1. 打开文件
2. 搜索所有 `end if`, `end step`, `end for`, `end while`
3. 删除这些行
4. 检查代码块缩进是否正确
5. 保存文件

**修改示例：**

**修改前：**
```markdown
## Step 块

```flow
step "登录":
    navigate to "https://example.com"
    fill "#username" with "user"
end step
```
```

**修改后：**
```markdown
## Step 块

```flow
step "登录":
    navigate to "https://example.com"
    fill "#username" with "user"
```
```

---

#### 文件 2：`grammar/DSL-GRAMMAR-QUICK-REFERENCE.md`

**位置：** 10 处 `end` + 2 处 `null`

**行号（end）：** 89, 107, 128, 143, 1707, 1741, 1752, 1764, 1777, 1778

**任务：**
1. 搜索并删除所有 `end` 关键字行
2. 搜索 `null` 并替换为 `None`
3. 检查修改后的代码块格式

**null 替换位置：**
- 行 642: `| NULL` → `| None`
- 行 658: `let mixed = ["text", 123, true, null]` → `let mixed = ["text", 123, True, None]`

---

#### 文件 3：`grammar/V3-EBNF.md`

**位置：** 12 处 `end` + 1 处 `null`

**行号（end）：** 83, 94, 104, 122, 133, 162, 172, 202, 723, 724, 725, 726

**任务：**
1. 删除所有 `end` 关键字行
2. 行 737：`| null字面量 | \`null\` | \`None\` | ✅ 100% |` → `| None字面量 | \`None\` | \`None\` | ✅ 100% |`

---

### Phase 2：辅助文档

#### 文件 4：`grammar/V3-EXAMPLES.flow`

**位置：** 6 处 `end` + 1 处 `null`

**行号（end）：** 35, 42, 44, 58, 88, 96

**任务：**
1. 删除所有 `end` 行
2. 行 349: `let nil = null` → `let nil = None`
3. 确保这是一个可运行的 .flow 文件

**重要：** 这是可执行代码，修改后必须确保语法正确！

---

#### 文件 5：`tests/grammar_alignment/TEST-PLAN.md`

**位置：** 5 处 `end` + 4 处 `null`

**行号（end）：** 476, 500, 503, 511, 515

**任务：**
1. 删除 `end` 关键字行
2. 搜索 `null` 并判断：
   - 如果是示例代码中的 `null` → 替换为 `None`
   - 如果是测试说明"检测 null 关键字报错" → 保留原文

---

#### 文件 6：`ARCHITECTURE.md`

**位置：** 2 处 `end` + 1 处 `null`

**行号：** 113, 1326

**任务：**
1. 检查这两处 `end` 的上下文
2. 如果是示例代码 → 删除
3. 如果是说明性文字"v3.0 移除了 end 关键字" → 保留

**行 116 的 `null`：**
- 检查上下文，如果是"空值改为 None 而非 null" → 保留说明，但确保示例使用 `None`

---

#### 文件 7：`CLAUDE.md`

**位置：** 2 处 `end`

**行号：** 136, 141

**任务：**
1. 检查上下文
2. 这两处应该是说明性文字："移除所有 end 关键字"
3. **保留原文不修改**（这是在描述语法变更）

---

#### 文件 8：`QUICK_REFERENCE.md`

**位置：** 1 处 `end`

**行号：** 135

**任务：**
1. 检查是否是代码示例
2. 如果是 → 删除
3. 如果是说明文字 → 保留

---

### Phase 3：文档扫描检查（重要！）

**位置：** `docs/analysis/语义检查系统完整分析报告.md`

**位置：** 5 处 `null`

**任务：**
1. 打开文件搜索 `null`
2. 检查每一处的上下文：
   - 如果是错误消息示例："无法对 null 值进行操作" → 改为 "无法对 None 值进行操作"
   - 如果是代码示例中的 `null` → 改为 `None`
3. 确保修改后语义正确

---

## 四、验证步骤

### 步骤 1：运行搜索验证

完成所有修改后，运行以下命令：

```bash
cd E:\cf\ads\flowby

# 检查是否还有 end 关键字（排除 CHANGELOG、MASTER、Proposal）
find . -type f -name "*.md" \
  -not -path "./.git/*" \
  -not -path "./grammar/CHANGELOG.md" \
  -not -path "./grammar/MASTER.md" \
  -not -path "./grammar/proposals/*" \
  -not -path "./SYNTAX_CLEANUP_ANALYSIS.md" \
  -not -path "./.ai-tasks/*" \
  | xargs grep -n "end if\|end step\|end for\|end while\|end when\|end function"

# 应该返回空（或只有 CLAUDE.md 中的说明性文字）

# 检查 null 关键字
find . -type f \( -name "*.md" -o -name "*.flow" \) \
  -not -path "./.git/*" \
  -not -path "./grammar/CHANGELOG.md" \
  -not -path "./SYNTAX_CLEANUP_ANALYSIS.md" \
  -not -path "./.ai-tasks/*" \
  | xargs grep -n "\\bnull\\b" | head -20

# 应该大幅减少（只剩说明性文字）
```

### 步骤 2：检查文件完整性

```bash
# 确保文件没有损坏
for file in grammar/DSL-SYNTAX-CHEATSHEET.md \
            grammar/DSL-GRAMMAR-QUICK-REFERENCE.md \
            grammar/V3-EBNF.md \
            grammar/V3-EXAMPLES.flow; do
  if [ -f "$file" ]; then
    echo "✓ $file exists"
    lines=$(wc -l < "$file")
    echo "  Lines: $lines"
  else
    echo "✗ $file MISSING!"
  fi
done
```

### 步骤 3：语法检查（针对 .flow 文件）

```bash
# 检查 V3-EXAMPLES.flow 是否可以解析
python -c "
from src.flowby.lexer import Lexer
from src.flowby.parser import Parser

with open('grammar/V3-EXAMPLES.flow', 'r', encoding='utf-8') as f:
    source = f.read()

try:
    tokens = Lexer().tokenize(source)
    ast = Parser().parse(tokens)
    print('✓ V3-EXAMPLES.flow 语法正确')
except Exception as e:
    print(f'✗ V3-EXAMPLES.flow 有语法错误: {e}')
"
```

---

## 五、执行报告模板

完成所有任务后，请创建文件 `.ai-tasks/TASK-001-report.md` 并填写以下内容：

```markdown
# TASK-001 执行报告

**执行者：** [你的名字/ID]
**开始时间：** YYYY-MM-DD HH:MM
**结束时间：** YYYY-MM-DD HH:MM
**实际耗时：** XX 分钟

---

## 执行统计

### Phase 1：核心语法参考文档

| 文件 | 状态 | end 删除 | null 替换 | 备注 |
|------|------|----------|----------|------|
| DSL-SYNTAX-CHEATSHEET.md | ✅ | 16 | 0 | |
| DSL-GRAMMAR-QUICK-REFERENCE.md | ✅ | 10 | 2 | |
| V3-EBNF.md | ✅ | 12 | 1 | |

### Phase 2：辅助文档

| 文件 | 状态 | end 删除 | null 替换 | 备注 |
|------|------|----------|----------|------|
| V3-EXAMPLES.flow | ✅ | 6 | 1 | 语法验证通过 |
| TEST-PLAN.md | ✅ | 5 | 2 | 保留了2处说明性文字 |
| ARCHITECTURE.md | ✅ | 0 | 0 | 2处为说明性文字已保留 |
| CLAUDE.md | ✅ | 0 | 0 | 2处为说明性文字已保留 |
| QUICK_REFERENCE.md | ✅ | 1 | 0 | |

### Phase 3：其他文档

| 文件 | 状态 | null 替换 | 备注 |
|------|------|----------|------|
| docs/analysis/语义检查系统完整分析报告.md | ✅ | 5 | 错误消息已更新 |

---

## 验证结果

### 搜索验证

```bash
# end 关键字残留检查
[粘贴命令输出]

# null 关键字残留检查
[粘贴命令输出]
```

### 语法验证

```bash
# V3-EXAMPLES.flow 解析结果
[粘贴命令输出]
```

---

## 遇到的问题

### 问题 1：[如果有问题，描述问题]

**位置：** 文件名:行号
**描述：** [问题详情]
**解决方案：** [如何处理]
**需要人工审查：** 是/否

### 问题 2：...

---

## 最终统计

- **处理文件数：** X 个
- **删除 end 关键字：** X 处
- **替换 null：** X 处
- **保留说明性文字：** X 处
- **发现问题：** X 个
- **需要人工审查：** X 个

---

## 建议

[如果有任何建议或发现的改进点]

---

## 签名

执行完成，请求架构师 AI 审查。

**执行者：** [你的名字]
**日期：** YYYY-MM-DD
```

---

## 六、常见问题

### Q1: 删除 `end` 后代码块格式乱了怎么办？

**A:** 检查上一行的缩进。通常是因为删除 `end` 后，下一个代码块的缩进没有正确对齐。

**示例：**
```markdown
# 错误 ❌
if x > 0:
    log "Yes"
let y = 2  # 缺少空行

# 正确 ✅
if x > 0:
    log "Yes"

let y = 2  # 有空行分隔
```

### Q2: 不确定某个 `null` 是否应该替换？

**A:** 检查上下文：
- **代码示例中** → 替换为 `None`
- **说明性文字** "v2.0 使用 null" → 可以保留，但在同一段落提供 v3.0 对照："v3.0 使用 None"
- **错误消息** "无法对 null 操作" → 替换为 "无法对 None 操作"

### Q3: 发现一个文件有大量修改，不确定是否正确？

**A:**
1. 先备份该文件：`cp file.md file.md.backup`
2. 进行修改
3. 使用 diff 检查：`diff file.md.backup file.md`
4. 在报告中标记"需要人工审查"

### Q4: 某个文件找不到或权限错误？

**A:**
1. 检查路径是否正确：`ls -la grammar/DSL-SYNTAX-CHEATSHEET.md`
2. 检查是否在正确的工作目录：`pwd` 应该显示 `E:\cf\ads\flowby`
3. 在报告中记录问题

---

## 七、紧急联系

如果遇到以下情况，**立即停止**并报告：

1. ❌ 发现文件被删除或严重损坏
2. ❌ Git 状态显示异常（如数百个文件被修改）
3. ❌ 验证脚本报告语法错误
4. ❌ 不确定某个修改是否正确且影响重大

**报告方式：** 在执行报告中明确说明，等待架构师 AI 审查。

---

## 八、成功标准

任务被视为成功完成，当且仅当：

1. ✅ 所有指定文件已修改
2. ✅ 验证脚本通过（无或极少残留）
3. ✅ V3-EXAMPLES.flow 语法正确
4. ✅ 没有破坏文件结构
5. ✅ 执行报告完整准确

---

**祝执行顺利！** 🚀

如有任何疑问，请在报告中详细说明，等待人工审查。
