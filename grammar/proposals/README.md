# Grammar Proposals - 语法变更提案

> **目录用途**: 存放所有语法变更提案
>
> **流程**: 提案 → 讨论 → 评审 → 实施 → 发布

---

## 📝 提案流程

### 1. 创建提案

```bash
# 复制模板
cp docs/grammar-proposals/TEMPLATE.md \
   docs/grammar-proposals/PROPOSAL-XXX-feature-name.md

# 编号规则: 按时间顺序递增
# 示例: PROPOSAL-001-try-catch.md
```

### 2. 填写提案

**必填部分**:
- ✅ 提案摘要
- ✅ 动机和背景
- ✅ 提议的解决方案（语法设计）
- ✅ 使用示例（至少 3 个）
- ✅ 影响分析（MAJOR/MINOR/PATCH）
- ✅ 实现方案（伪代码）

**可选部分**:
- 替代方案
- 测试计划
- 实施时间线

### 3. 提交讨论

```bash
# 1. 提交 PR
git checkout -b proposal/xxx-feature-name
git add docs/grammar-proposals/PROPOSAL-XXX-*.md
git commit -m "proposal: add grammar proposal #XXX"
git push origin proposal/xxx-feature-name

# 2. 创建 GitHub Issue
# 标题: [Grammar Proposal #XXX] Feature Name
# 标签: grammar-proposal
# 链接到 PR
```

### 4. 社区讨论

- 核心团队评审
- 社区成员反馈
- 设计迭代
- 更新提案状态: 📝 Draft → 💭 Under Discussion

### 5. 核心团队决策

**评审标准**:
- [ ] 技术可行性
- [ ] 语法一致性
- [ ] 是否真正需要
- [ ] 复杂度影响
- [ ] 维护成本

**决策**:
- ✅ Approved → 进入实施
- ❌ Rejected → 关闭提案
- ⏸️ Deferred → 推迟到后续版本

### 6. 实施

_参见 GRAMMAR-GOVERNANCE.md 的 6 步实施流程_

### 7. 发布

- 更新 GRAMMAR-CHANGELOG.md
- 发布 Release Notes
- 归档提案（移到 `archived/`）

---

## 📊 提案状态

### 状态标记

| 标记 | 状态 | 说明 |
|------|------|------|
| 📝 | Draft | 初稿，编写中 |
| 💭 | Under Discussion | 讨论中 |
| ⏳ | Pending Review | 等待评审 |
| ✅ | Approved | 已批准，待实施 |
| 🚧 | In Progress | 实施中 |
| 🎉 | Implemented | 已实施 |
| ❌ | Rejected | 已拒绝 |
| ⏸️ | Deferred | 推迟 |

### 活跃提案

| # | 标题 | 提出日期 | 状态 | 影响 | 目标版本 |
|---|------|---------|------|------|---------|
| 010 | Resource Constructor Refactoring | 2025-11-30 | 📝 Draft | MAJOR | v6.0 |

### 已归档提案

| # | 标题 | 最终状态 | 发布版本 | 归档日期 |
|---|------|---------|---------|---------|
| - | - | - | - | - |

_无已归档提案_

---

## 🎯 提案最佳实践

### DO ✅

1. **清晰的动机**
   - 解释为什么需要这个功能
   - 提供实际使用场景
   - 说明现有方案的不足

2. **具体的示例**
   - 至少 3 个使用示例
   - 覆盖基本、高级、配合使用
   - 代码可以直接运行

3. **全面的影响分析**
   - 考虑向后兼容性
   - 评估学习成本
   - 分析语法复杂度

4. **可行的实现方案**
   - 提供伪代码
   - 评估实现难度
   - 识别技术风险

### DON'T ❌

1. **避免模糊的需求**
   - ❌ "添加一个更好的循环"
   - ✅ "添加 while 循环，语法为..."

2. **避免过度设计**
   - ❌ 一次添加 10 个相关功能
   - ✅ 先添加核心功能，再迭代

3. **避免忽略兼容性**
   - ❌ 直接改变现有语法含义
   - ✅ 废弃 → 过渡 → 移除

4. **避免缺少示例**
   - ❌ 只有抽象描述
   - ✅ 具体的、可运行的代码示例

---

## 📋 评审检查清单

### 技术评审

- [ ] 语法定义清晰无歧义
- [ ] 与现有语法一致
- [ ] 技术上可实现
- [ ] 性能影响可接受
- [ ] 错误处理完善

### 设计评审

- [ ] 真正解决了问题
- [ ] 没有更简单的方案
- [ ] 学习成本可接受
- [ ] 不增加不必要的复杂度

### 文档评审

- [ ] 提案完整
- [ ] 示例充分
- [ ] 影响分析全面
- [ ] 实现方案清晰

### 流程评审

- [ ] 遵循提案模板
- [ ] 讨论充分
- [ ] 社区意见已考虑
- [ ] 决策有记录

---

## 🎓 示例提案

参见:
- `EXAMPLE-001-try-catch.md` - 异常处理示例
- `EXAMPLE-002-multiline-string.md` - 多行字符串示例

_（这些是示例，仅供参考）_

---

## 📞 获取帮助

### 提案相关问题

- **如何开始**: 复制 `TEMPLATE.md` 并填写
- **如何讨论**: 创建 GitHub Issue
- **如何推进**: 联系核心团队 @core-team

### 联系方式

- **GitHub Issues**: [项目 Issues 页面]
- **团队邮箱**: team@example.com
- **核心团队**: @maintainer1, @maintainer2

---

## 📊 提案统计

### 历史统计

```
总提案数: 0
├── 批准并实施: 0
├── 拒绝: 0
├── 推迟: 0
└── 进行中: 0

批准率: N/A
平均实施时间: N/A
```

### 按影响级别

```
MAJOR 提案: 0
MINOR 提案: 0
PATCH 提案: 0
```

---

## 🎉 成功提案案例

_待添加成功提案的案例研究_

---

**维护者**: Flowby Core Team
**创建日期**: 2025-11-25
**最后更新**: 2025-11-25
