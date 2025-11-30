# 语法治理流程总结

## 📋 文档信息

**创建日期**: 2025-11-27
**版本**: 1.0
**目的**: 为开发者提供语法变更的标准流程快速参考

---

## 🎯 核心文档结构

语法治理系统基于以下核心文档：

```
grammar/
├── README.md              # 治理系统概览 (504行)
├── MASTER.md              # 语法规范 - 单一事实来源 (1,008行，v3.0)
├── GOVERNANCE.md          # 治理流程详细说明 (528行)
├── CHANGE-MANAGEMENT.md   # 变更管理指南
├── CHANGELOG.md           # 版本历史记录
├── QUICKSTART.md          # 快速入门指南
├── SUMMARY.md             # 系统总结
├── proposals/             # 提案目录
│   ├── README.md          # 提案系统说明
│   ├── TEMPLATE.md        # 提案模板 (478行)
│   ├── EXAMPLE-001-try-catch.md  # 示例提案
│   └── archived/          # 已归档提案
└── tools/                 # 自动化工具
    ├── check_sync.py      # 同步检查工具
    └── check_semantics.py # 语义验证工具
```

**单一事实来源**: `MASTER.md` 是语法规范的唯一权威文档

---

## 🔄 语法变更三大场景

### 场景 1️⃣: 新增语法特性

**流程**:

```
Step 1: 提交提案
  └─ 使用 proposals/TEMPLATE.md 创建提案文件
  └─ 编号: 001, 002, ... (顺序递增)

Step 2: 更新 MASTER.md
  └─ 添加新特性行，状态标记为 🚧 Partial

Step 3: 实现
  └─ Parser: 添加 _parse_xxx() 方法
  └─ AST: 添加节点定义
  └─ Interpreter: 添加执行逻辑

Step 4: 测试
  └─ 测试覆盖率 ≥ 90%
  └─ 更新 MASTER.md 状态: 🚧 → ⚠️ (有代码但缺测试)

Step 5: 文档同步
  └─ 更新 MASTER.md 状态: ⚠️ → ✅
  └─ 更新 CHANGELOG.md
  └─ 更新示例代码

Step 6: 发布
  └─ 确定版本号 (MAJOR.MINOR.PATCH)
  └─ 标记 git tag
```

**版本影响**: 通常为 MINOR 版本

---

### 场景 2️⃣: 修改现有语法 ⭐ (当前场景)

**流程** (7步标准流程):

```
Step 1: 在 MASTER.md 中标记变更
  ├─ 添加新语法行 (状态: 🚧 Partial)
  ├─ 标记旧语法为 🗑️ Deprecated
  └─ 写明变更原因和迁移路径

Step 2: 提交提案
  ├─ 使用 proposals/TEMPLATE.md
  ├─ 创建 proposals/XXX-feature-name.md
  └─ 详细说明动机、方案、影响

Step 3: 实现新语法
  ├─ 保留旧语法兼容 (至少1个版本)
  ├─ 添加废弃警告 (deprecation warning)
  └─ 实现新语法

Step 4: 测试
  ├─ 新语法测试用例
  ├─ 旧语法兼容测试
  ├─ 覆盖率 ≥ 90%
  └─ 更新 MASTER.md 状态: 🚧 → ⚠️ → ✅

Step 5: 文档同步
  ├─ 更新 MASTER.md (新语法 ✅, 旧语法 🗑️)
  ├─ 更新 CHANGELOG.md
  ├─ 创建迁移指南
  └─ 更新所有示例代码

Step 6: 迁移期 (至少1个版本)
  ├─ 新旧语法并存
  ├─ 旧语法显示警告
  ├─ 文档推荐新语法
  └─ 提供迁移工具/脚本

Step 7: 移除旧语法 (下一个 MAJOR 版本)
  ├─ 从 MASTER.md 中删除 🗑️ 行
  ├─ 从 parser 中删除旧语法代码
  └─ 更新 CHANGELOG.md
```

**版本影响**:
- 添加新语法: MINOR 版本 (如 v3.0 → v3.1)
- 移除旧语法: MAJOR 版本 (如 v3.1 → v4.0)

**重要原则**:
- ✅ 至少保留旧语法 1 个版本
- ✅ 必须提供迁移指南
- ✅ 必须添加废弃警告
- ❌ 不能直接删除旧语法

---

### 场景 3️⃣: 修复 Bug

**流程**:

```
Step 1: 确认 Bug
  └─ 在 MASTER.md 的 Notes 列标注 "Bug: ..."

Step 2: 修复
  └─ 修改 parser/interpreter 代码
  └─ 不改变语法表面形式

Step 3: 测试
  └─ 添加回归测试用例

Step 4: 文档
  └─ 更新 CHANGELOG.md (PATCH 版本)
  └─ 移除 MASTER.md 的 Bug 标注
```

**版本影响**: PATCH 版本

---

## 📊 状态管理

### 特性状态标识

| 状态 | 含义 | 何时使用 |
|------|------|----------|
| ✅ | Implemented | 代码完成 + 测试完成 + 文档完成 |
| ⚠️ | Needs Tests | 代码完成，但测试覆盖不足 |
| 🚧 | Partial | 实现中，尚未完成 |
| ❌ | Not Implemented | 计划中，未开始实现 |
| 🗑️ | Deprecated | 已废弃，将在未来版本移除 |

### 状态转换流程

```
新特性提案
    ↓
❌ Not Implemented (计划中)
    ↓ 开始实现
🚧 Partial (实现中)
    ↓ 代码完成
⚠️ Needs Tests (有代码但缺测试)
    ↓ 测试通过
✅ Implemented (完全实现)
    ↓ 决定废弃
🗑️ Deprecated (废弃标记)
    ↓ MAJOR 版本
删除 (从 MASTER.md 移除)
```

---

## 🎨 设计原则

### 1. 一致性 (Consistency)

**定义**: 相似的操作应该使用相似的语法模式

**示例**:
```dsl
# ✅ 一致: 所有内置命名空间都用相同方式调用
let rounded = Math.round(3.7)
let now = Date.now()
let json = JSON.stringify(data)

# ❌ 不一致: 同样的调用却用不同语法
call "random.email" into email  # 为什么要用 call?
```

**检查清单**:
- [ ] 与现有语法风格一致
- [ ] 与 v3.0 Python-style 理念一致
- [ ] 与同类功能的语法模式一致

### 2. 清晰性 (Clarity)

**定义**: 语法应该明确无歧义，易于理解

**示例**:
```dsl
# ✅ 清晰: 语义明确
let email = random.email()

# ❌ 不清晰: call 的语义是什么？
call "random.email" into email
```

**检查清单**:
- [ ] 语法含义一目了然
- [ ] 无歧义 (只有一种解析方式)
- [ ] 符合直觉 (Python 开发者无学习成本)

### 3. 简洁性 (Simplicity)

**定义**: 避免冗余关键字和复杂结构

**示例**:
```dsl
# ✅ 简洁: 无冗余
let email = random.email()

# ❌ 冗余: call + into 都是多余的
call "random.email" into email
```

**检查清单**:
- [ ] 无冗余关键字
- [ ] 语法结构简单
- [ ] 遵循 KISS 原则

### 4. 可扩展性 (Extensibility)

**定义**: 易于添加新功能而不破坏现有设计

**示例**:
```dsl
# ✅ 可扩展: 添加新服务只需新增命名空间
let email = random.email()
let sms = sms.send(phone: "...", message: "...")  # 新服务

# ❌ 不可扩展: 每次都要特殊处理
call "random.email" into email
call "sms.send" with phone="...", message="..." into result
```

**检查清单**:
- [ ] 添加新功能无需修改语法规则
- [ ] 新功能与现有功能自然融合
- [ ] 不引入特殊 case

---

## 🛡️ 复杂度控制

### 硬性限制

| 类别 | 限制 | 当前状态 | 说明 |
|------|------|---------|------|
| **主语句** | ≤ 30 | 25/30 | 导航、等待、动作等顶层语句 |
| **表达式优先级** | ≤ 10 | 9/10 | 运算符优先级层级 |
| **关键字** | ≤ 100 | ~80/100 | 保留关键字总数 |

### 检查方法

```bash
# 自动检查同步状态
python grammar/tools/check_sync.py

# 检查语义完整性
python grammar/tools/check_semantics.py
```

**超限处理**:
- 主语句超限: 考虑合并相似语句，或提升为表达式
- 优先级超限: 重新设计表达式系统
- 关键字超限: 移除冗余关键字，合并功能

---

## 🔍 同步验证

### 自动化验证工具

#### 1. check_sync.py

**功能**: 检查 MASTER.md 与代码实现的同步状态

**运行**:
```bash
python grammar/tools/check_sync.py
python grammar/tools/check_sync.py --verbose
```

**检查项**:
- ✅ 文档中的 ✅ 特性都有对应 parser 方法
- ✅ 所有 parser 方法都在文档中记录
- ✅ 测试覆盖情况
- ⚠️ 未文档化的方法
- ❌ 缺失的 parser 方法

**输出示例**:
```
======================================================================
Grammar Sync Report
======================================================================

[Feature Statistics]
   Total Features:        49
   [OK] Implemented:      42
   [!]  Needs Tests:      0
   [~]  Partial:          0
   [X]  Not Implemented:  0
   [-]  Deprecated:       7

[Parser Methods]
   Total Methods:         45
   Documented:            45
   Undocumented:          0

======================================================================
[OK] Status: SYNCED
     Grammar and implementation are in sync!
======================================================================
```

#### 2. check_semantics.py

**功能**: 检查 AST 节点与解释器处理器的完整性

**运行**:
```bash
python grammar/tools/check_semantics.py
python grammar/tools/check_semantics.py --verbose
```

**检查项**:
- ✅ 所有 AST 节点都有对应解释器处理器
- ✅ 语句节点在 `_execute_statement()` 中处理
- ✅ 表达式节点在 `ExpressionEvaluator` 中处理
- ⚠️ 未处理的 AST 节点

**输出示例**:
```
======================================================================
Semantic Verification Report
======================================================================

[AST Nodes Statistics]
   Total AST Nodes:       46
   Statement Nodes:       33
   Expression Nodes:      12
   Other Nodes:           1

[Interpreter Handlers]
   Total Handlers:        32
   Handled Nodes:         44
   Coverage:              44/46 (95%)

======================================================================
[OK] Status: SEMANTICS COMPLETE
     All AST nodes have corresponding interpreter handlers!
======================================================================
```

### 手动检查清单

**提交前检查**:
- [ ] 运行 `check_sync.py` 确保同步
- [ ] 运行 `check_semantics.py` 确保语义完整
- [ ] 运行完整测试套件 `pytest tests/`
- [ ] 测试覆盖率 ≥ 90%
- [ ] MASTER.md 状态更新
- [ ] CHANGELOG.md 记录变更
- [ ] 示例代码更新

---

## 📝 提案系统

### 提案模板结构

使用 `grammar/proposals/TEMPLATE.md` 创建提案，包含以下章节：

```markdown
# Grammar Proposal #XXX: [Feature Name]

## 📋 Proposal Summary
   - 提案编号、标题、作者、日期、状态

## 🎯 Motivation and Background
   - 为什么需要这个变更？
   - 当前设计的问题是什么？

## 💡 Proposed Solution
   - 语法设计
   - 详细说明
   - 使用示例

## 🔍 Semantics and Behavior
   - AST 结构
   - 解释器行为
   - 边界情况

## 📊 Impact Analysis
   - 版本影响 (MAJOR/MINOR/PATCH)
   - 兼容性分析
   - 学习曲线
   - 语法复杂度

## 🛠️ Implementation Plan
   - 阶段划分
   - 具体任务

## 🧪 Test Plan
   - 测试用例

## 📚 Documentation Changes
   - MASTER.md 变更
   - CHANGELOG.md 变更
   - 示例代码更新

## 🔄 Alternative Solutions
   - 其他备选方案
   - 对比分析

## 💬 Discussion Record
   - 讨论记录

## ✅ Decision
   - 最终决策

## 📅 Implementation Timeline
   - 时间计划
```

### 提案编号规则

```
001: 第一个提案
002: 第二个提案
...
```

**示例**: `002-pythonic-service-call.md`

### 提案状态

- 🟡 **Draft**: 草稿中
- 🟢 **Approved**: 已批准，待实施
- 🔵 **Implemented**: 已实施
- 🔴 **Rejected**: 已拒绝
- ⚪ **Archived**: 已归档

---

## 🎯 当前任务: Call 语法改进

### 背景

**当前设计问题**:
```dsl
# ❌ 当前语法 (v3.0)
call "random.email" into email
call "http.get" with url: "..." into response

# 对比内置函数
let rounded = Math.round(3.7)  # ✅ Python-style
```

**问题**:
1. ❌ 语法不一致 (call vs 直接调用)
2. ❌ 冗余关键字 (call + into)
3. ❌ 不能用于表达式
4. ❌ 与 v3.0 Python-style 理念冲突

### 改进方案

**推荐设计** (Solution A):
```dsl
# ✅ 新语法 (v3.1+)
let email = random.email()
let password = random.password(length: 16)
let response = http.get(url: "...", timeout: 5000)

# ✅ 可用于表达式
let users = [
    {email: random.email(), pwd: random.password()},
    {email: random.email(), pwd: random.password()}
]

# ✅ 可用于字符串插值
log f"Generated: {random.email()}"
```

**实现方式**:
将 `random`, `http` 作为内置命名空间 (类似 Math, Date, JSON)

### 实施计划

**v3.1 版本** (2025-12):
1. ✅ 新增 Python-style 服务调用语法
2. ✅ 保留旧 `call` 语法，标记为 🗑️ Deprecated
3. ✅ 添加废弃警告
4. ✅ 文档推荐新语法
5. ✅ 提供迁移指南

**v4.0 版本** (2026-XX):
1. ✅ 完全移除 `call` 语法
2. ✅ 只保留 Python-style 调用
3. ✅ 更新 CHANGELOG.md

### 执行步骤

**Step 1: 创建提案** ⬅️ 当前步骤
- [ ] 创建 `proposals/002-pythonic-service-call.md`
- [ ] 详细说明动机、方案、影响

**Step 2: 更新 MASTER.md**
- [ ] 添加新语法行 (状态: 🚧)
- [ ] 标记旧 call 语法为 🗑️

**Step 3: 实现**
- [ ] 添加 RandomNamespace 类
- [ ] 添加 HttpNamespace 类
- [ ] 注册到 BUILTIN_NAMESPACES
- [ ] 保留 CallStatement 处理 (加警告)

**Step 4-7: 测试、文档、迁移、移除**
- [ ] 编写测试用例
- [ ] 更新文档和示例
- [ ] 提供迁移期支持
- [ ] v4.0 移除旧语法

---

## 📚 参考文档

- **治理系统概览**: `grammar/README.md`
- **详细治理流程**: `grammar/GOVERNANCE.md`
- **变更管理指南**: `grammar/CHANGE-MANAGEMENT.md`
- **提案模板**: `grammar/proposals/TEMPLATE.md`
- **语法规范**: `grammar/MASTER.md`
- **版本历史**: `grammar/CHANGELOG.md`

---

## 🔗 相关工具

- **同步检查**: `python grammar/tools/check_sync.py`
- **语义验证**: `python grammar/tools/check_semantics.py`
- **测试套件**: `pytest tests/grammar_alignment/ -v`

---

**文档维护者**: AI Assistant
**最后更新**: 2025-11-27
**适用版本**: v3.0+
