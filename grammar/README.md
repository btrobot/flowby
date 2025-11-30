# DSL Grammar Governance System

> **语法治理系统** - Registration System DSL 的语法宪法和变更管理中心
>
> **Version**: 2.0.0
> **Date**: 2025-11-25
> **Status**: ✅ Production Ready

---

## 🎯 什么是语法治理系统？

这是一个完整的 DSL 语法版本管理和变更控制系统，确保语法的可持续演进和向后兼容性。

**核心目标**:
- ✅ 提供语法的单一真理源
- ✅ 规范化语法变更流程
- ✅ 追踪版本历史和兼容性
- ✅ 自动化验证文档-代码同步
- ✅ 控制语法复杂度增长

---

## 📚 核心文档（必读）

### 1. [MASTER.md](./MASTER.md) - 语法主控文档 ⭐

**用途**: 单一真理源，定义所有支持的语法特性

**包含内容**:
- 49个语法特性完整定义
- 25个语句类型（变量、控制流、导航、等待、选择、动作、断言、服务调用、提取、工具）
- 9级表达式优先级
- 7种数据类型
- 5个系统变量命名空间
- 19个内置函数
- 每个特性包含：ID | 名称 | 语法 | 状态 | 版本 | 方法 | 测试 | 说明

**何时查看**:
- 查询某个语法是否支持
- 查看特性的实现状态
- 了解特性的添加版本
- 查找 parser 方法名

### 2. [GOVERNANCE.md](./GOVERNANCE.md) - 治理流程规范

**用途**: 定义如何添加、修改、删除语法

**包含内容**:
- 6步添加新语法流程
- 修改现有语法流程（废弃 → 过渡 → 移除）
- 5种状态定义（✅⚠️🚧❌🗑️）
- 语法设计4大原则
- 复杂度控制规则（语句≤30, 表达式≤10, 关键字≤100）
- 版本控制策略
- DO/DON'T 最佳实践

**何时查看**:
- 想要添加新语法特性
- 想要修改现有语法
- 需要废弃某个特性
- 了解语法设计原则

### 3. [CHANGELOG.md](./CHANGELOG.md) - 变更历史

**用途**: 记录所有版本的语法变更

**包含内容**:
- 语义化版本规范（MAJOR.MINOR.PATCH）
- v2.0.0 完整变更日志（Added/Changed/Fixed/Deprecated/Removed）
- v1.0.0 基线版本
- v1.0 → v2.0 迁移指南（带代码示例）
- 兼容性矩阵
- 未来版本计划（v2.1.0）
- 支持策略

**何时查看**:
- 升级语法版本
- 查看历史变更
- 了解兼容性
- 编写迁移指南

### 4. [CHANGE-MANAGEMENT.md](./CHANGE-MANAGEMENT.md) - 完整管理指南

**用途**: 深入理解整个语法治理系统

**包含内容**:
- 系统概述（6大核心组件）
- 文档体系详解
- 完整的变更管理流程图
- 版本控制系统详解
- 变更分类和处理（MINOR/MAJOR/PATCH）
- 自动化工具使用指南
- 6个实际使用场景
- 版本演进示例
- 最佳实践汇总

**何时查看**:
- 全面了解治理系统
- 查找详细的使用场景
- 了解工具使用方法
- 学习最佳实践

### 5. [QUICKSTART.md](./QUICKSTART.md) - 快速入门（5分钟）

**用途**: 快速上手语法治理系统

**包含内容**:
- 3步快速开始
- 4个日常使用场景
- 常用命令参考
- 当前系统状态
- 最佳实践速查
- FAQ

**何时查看**:
- 首次使用系统
- 需要快速查命令
- 查看系统当前状态

### 6. [SUMMARY.md](./SUMMARY.md) - 系统总结

**用途**: 整个治理系统的总结和统计

**包含内容**:
- 完成的工作总览
- 系统能力说明
- 解决的问题列表
- 成功指标
- 使用指南

**何时查看**:
- 了解系统能力
- 查看统计数据
- 向他人介绍系统

---

## 🔧 自动化工具

### [tools/check_sync.py](./tools/check_sync.py)

**功能**: 自动检查文档和代码的同步状态

**用法**:
```bash
# 基本检查
python grammar/tools/check_sync.py

# 详细输出
python grammar/tools/check_sync.py --verbose

# 获取修复建议
python grammar/tools/check_sync.py --fix-status
```

**检查项目**:
- ✅ MASTER.md 中的特性是否有对应的 parser 方法
- ✅ parser.py 中的方法是否在文档中记录
- ✅ 特性的测试覆盖情况
- ✅ 特性状态统计

**当前结果**:
```
[OK] Status: SYNCED
     49 个特性已文档化
     50 个 parser 方法
     0 个未文档化方法
```

### [tools/check_version.py](./tools/check_version.py)

**功能**: 检查 DSL 脚本与语法版本的兼容性

**用法**:
```bash
# 检查单个脚本
python grammar/tools/check_version.py script.flow

# 显示使用的特性
python grammar/tools/check_version.py script.flow --show-features

# 生成迁移报告
python grammar/tools/check_version.py script.flow --migration-report

# 检查对特定版本的兼容性
python grammar/tools/check_version.py script.flow --target-version 1.0.0
```

**检查项目**:
- ✅ 特性是否在目标版本中可用
- ✅ 是否使用了废弃特性
- ✅ 是否使用了已移除的特性
- ✅ 生成迁移建议

---

## 📝 提案系统

所有语法变更必须通过标准化的提案流程。

### 目录结构

```
proposals/
├── README.md                    # 提案流程说明
├── TEMPLATE.md                  # 标准提案模板
├── EXAMPLE-001-try-catch.md     # 完整示例
└── archived/                    # 已完成的提案
```

### 提案流程（7步）

1. **创建提案** - 使用 TEMPLATE.md
2. **提交讨论** - PR + Issue
3. **社区讨论** - 标签：grammar-proposal
4. **核心团队评审** - 决定是否批准
5. **实施** - 按照 GOVERNANCE.md 的 6 步流程
6. **验收** - 测试通过、文档完整
7. **发布** - 更新 CHANGELOG、归档提案

### 提案状态

- 💭 **Under Discussion** - 讨论中
- ✅ **Approved** - 已批准，等待实施
- 🚧 **In Progress** - 实施中
- ✨ **Completed** - 已完成并发布
- ❌ **Rejected** - 已拒绝
- ⏸️ **Deferred** - 推迟到未来版本

### 如何创建提案

```bash
# 1. 复制模板
cp grammar/proposals/TEMPLATE.md \
   grammar/proposals/PROPOSAL-002-my-feature.md

# 2. 编辑提案，填写完整信息
vim grammar/proposals/PROPOSAL-002-my-feature.md

# 3. 提交 PR
git checkout -b proposal/002-my-feature
git add grammar/proposals/PROPOSAL-002-*.md
git commit -m "proposal: add my-feature grammar proposal"
git push origin proposal/002-my-feature

# 4. 创建 Issue 并关联 PR
# 添加标签：grammar-proposal
```

---

## 📊 当前状态

### 语法版本

```
当前版本:     2.0.0 (2025-11-25)
前一版本:     1.0.0 (支持中，仅修复bug)
支持策略:     当前版本 + 前一版本
```

### 特性统计

```
语句类型:         25 / 30  (83%)
表达式层次:       9 / 10   (90%)
关键字:           80+ / 100 (80%+)
内置函数:         19
系统变量命名空间:  5
数据类型:         7
VR规则:           4
```

### 实现状态

```
✅ 已实现并测试:   25/25  (100%)
⚠️ 需要测试:       0/25   (0%)
🚧 部分实现:       0/25   (0%)
❌ 未实现:         0/25   (0%)
🗑️ 已废弃:         0/25   (0%)
```

### 同步状态

```
特性总数:         49
已文档化:         49   (100%)
已实现方法:       50
已文档化方法:     39   (78%)
未文档化方法:     0    (0%)

同步状态:         ✅ SYNCED
最后验证:         2025-11-25
```

---

## 🚀 快速使用指南

### 场景1: 我想查看支持哪些语法

```bash
# 查看主控文档
cat grammar/MASTER.md

# 使用 grep 查找特定语法
grep -i "navigate" grammar/MASTER.md
```

### 场景2: 我想添加新语法特性

```bash
# 步骤1: 创建提案
cp grammar/proposals/TEMPLATE.md \
   grammar/proposals/PROPOSAL-002-my-feature.md

# 步骤2: 参考示例
cat grammar/proposals/EXAMPLE-001-try-catch.md

# 步骤3: 遵循治理流程
cat grammar/GOVERNANCE.md

# 步骤4: 实施后验证
python grammar/tools/check_sync.py
```

### 场景3: 我想检查脚本兼容性

```bash
# 检查单个脚本
python grammar/tools/check_version.py examples/flows/script.flow

# 显示使用的特性
python grammar/tools/check_version.py examples/flows/script.flow --show-features

# 批量检查
for f in examples/flows/*.flow; do
  python grammar/tools/check_version.py "$f"
done
```

### 场景4: 我想发布新版本

```bash
# 1. 更新 CHANGELOG.md
vim grammar/CHANGELOG.md

# 2. 验证同步
python grammar/tools/check_sync.py

# 3. 运行测试
pytest tests/

# 4. 创建标签
git tag -a grammar-v2.1.0 -m "Grammar version 2.1.0"
git push origin grammar-v2.1.0

# 5. 归档提案
mv grammar/proposals/PROPOSAL-*.md grammar/proposals/archived/
```

---

## 📖 学习路径

### 路径A: 快速入门（15分钟）

1. [QUICKSTART.md](./QUICKSTART.md) - 5分钟
2. [MASTER.md](./MASTER.md) - 浏览特性列表 - 10分钟

### 路径B: 语法维护者（1.5小时）

1. [MASTER.md](./MASTER.md) - 10分钟
2. [GOVERNANCE.md](./GOVERNANCE.md) - 15分钟
3. [CHANGELOG.md](./CHANGELOG.md) - 10分钟
4. [proposals/README.md](./proposals/README.md) - 10分钟
5. [proposals/EXAMPLE-001-try-catch.md](./proposals/EXAMPLE-001-try-catch.md) - 20分钟
6. [CHANGE-MANAGEMENT.md](./CHANGE-MANAGEMENT.md) - 30分钟
7. 实践工具 - 5分钟

### 路径C: 完整理解（2小时）

按顺序阅读所有文档：
1. QUICKSTART.md
2. MASTER.md
3. GOVERNANCE.md
4. CHANGELOG.md
5. proposals/README.md + EXAMPLE
6. CHANGE-MANAGEMENT.md
7. SUMMARY.md
8. 实践所有工具

---

## ❓ 常见问题

**Q: 为什么需要语法治理系统？**
A: 随着 DSL 的演进，语法特性会不断增加和变化。没有系统化的管理，会导致：
- 不知道支持哪些语法
- 文档和代码不一致
- 版本兼容性混乱
- 语法无序增长失控

**Q: 我想添加新语法，从哪里开始？**
A:
1. 阅读 [GOVERNANCE.md](./GOVERNANCE.md) 了解 6 步流程
2. 使用 [proposals/TEMPLATE.md](./proposals/TEMPLATE.md) 创建提案
3. 参考 [proposals/EXAMPLE-001-try-catch.md](./proposals/EXAMPLE-001-try-catch.md)

**Q: 如何验证文档和代码同步？**
A: 运行 `python grammar/tools/check_sync.py`，工具会自动检查并报告。

**Q: 语法版本如何管理？**
A: 采用语义化版本（MAJOR.MINOR.PATCH）：
- MAJOR: 不兼容的变更（如移除特性）
- MINOR: 新增功能，向后兼容
- PATCH: Bug修复

详见 [CHANGELOG.md](./CHANGELOG.md)

**Q: 提案被拒绝了怎么办？**
A: 提案被拒绝通常有明确的理由。可以：
- 查看评审意见
- 修改提案解决问题
- 重新提交
- 或者接受决定，归档提案

**Q: 工具报告不同步怎么办？**
A:
1. 查看具体的不同步项
2. 更新 MASTER.md 或修改代码
3. 重新运行工具验证
4. 所有修改必须经过 Code Review

---

## 🔗 相关资源

### 实现代码

- `src/registration_system/dsl/parser.py` - Parser 实现
- `src/registration_system/dsl/lexer.py` - Lexer 实现
- `src/registration_system/dsl/ast_nodes.py` - AST 节点定义
- `src/registration_system/dsl/interpreter.py` - Interpreter 实现
- `src/registration_system/dsl/symbol_table.py` - 符号表实现

### 其他文档

- `docs/DSL-GRAMMAR.ebnf` - EBNF 完整规范
- `docs/DSL-GRAMMAR-QUICK-REFERENCE.md` - BNF 样式快速参考
- `docs/DSL-SYNTAX-CHEATSHEET.md` - 表格式语法速查表
- `docs/technical-analysis/` - 技术深度分析（4个文档）
- `docs/README.md` - 文档中心主索引

### 测试

- `tests/` - 所有语法特性的测试用例
- 运行: `pytest tests/ -v`

---

## 📧 联系和贡献

### 维护团队

**Team**: Registration System Core Team
**Contact**: 提交 Issue 到项目仓库

### 贡献指南

如需贡献：
1. 遵循提案流程（添加新特性）
2. 遵循 Git 提交规范
3. 确保所有测试通过
4. 运行 `check_sync.py` 验证同步
5. 更新相关文档

### 报告问题

发现问题时：
1. 检查是否已有相关 Issue
2. 创建新 Issue，描述清楚
3. 提供复现步骤
4. 附上相关代码示例

---

## 📜 许可证

本项目遵循项目主许可证。

---

**System Version**: 2.0.0
**Last Updated**: 2025-11-25
**Status**: ✅ Production Ready
**Maintainer**: Registration System Core Team

---

**记住**: 语法治理不仅仅是版本控制，这是确保 DSL 可持续发展的基础设施！🚀
