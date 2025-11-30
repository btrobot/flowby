# Grammar Proposal #XXX: [Feature Name]

> **提案编号**: #XXX
> **提出日期**: YYYY-MM-DD
> **提出人**: Your Name
> **状态**: 📝 Draft | 💭 Under Discussion | ⏳ Pending Review | ✅ Approved | ❌ Rejected
> **目标版本**: X.Y.0
> **影响级别**: MAJOR | MINOR | PATCH

---

## 📋 提案摘要

_用 1-2 句话概述这个提案的核心内容_

---

## 🎯 动机和背景

### 问题描述

_详细描述当前存在的问题或限制_

**示例场景**:
```flow
# 当前的做法（有问题或不够优雅）
...
```

**问题**:
1. ...
2. ...

### 为什么现有功能不够？

_解释为什么现有语法特性无法解决这个问题_

---

## 💡 提议的解决方案

### 语法设计

#### 基本形式

```bnf
proposed_statement ::= "keyword" ...
```

#### 具体语法

```flow
# 语法示例
keyword param1 param2:
    ...
end keyword
```

### 详细说明

#### 参数说明

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| param1 | expr | ✅ | ... |
| param2 | string | ❌ | ... |

#### 选项说明

- `option1`: ...
- `option2`: ...

### 使用示例

#### 示例 1: 基本用法

```flow
/**meta
desc: 基本用法示例
*/

# 使用新语法
proposed_feature param1 param2:
    # ...
end proposed_feature
```

**预期输出**:
```
...
```

#### 示例 2: 高级用法

```flow
# 复杂场景
...
```

#### 示例 3: 与现有功能配合

```flow
# 与其他语法特性配合使用
...
```

---

## 🔍 语义和行为

### 执行语义

_详细说明这个语法在运行时的行为_

1. **初始化阶段**: ...
2. **执行阶段**: ...
3. **清理阶段**: ...

### 作用域规则

_如果涉及变量或作用域，说明作用域规则_

- 变量可见性: ...
- 生命周期: ...

### 错误处理

_说明可能的错误情况和处理方式_

| 错误情况 | 行为 | 示例 |
|---------|------|------|
| ... | ... | ... |

---

## 📊 影响分析

### 版本影响

- [ ] **MAJOR** (不兼容变更)
  - 破坏现有功能: ___
  - 需要迁移: ___

- [ ] **MINOR** (向后兼容的新功能)
  - 新增功能
  - 不影响现有代码

- [ ] **PATCH** (向后兼容的修复)
  - Bug 修复
  - 性能优化

### 兼容性

#### 向后兼容性

- ✅ / ❌ 与现有语法兼容
- **原因**: ...

#### 现有功能影响

| 现有功能 | 影响 | 说明 |
|---------|------|------|
| Feature A | 无 / 修改 / 冲突 | ... |
| Feature B | 无 / 修改 / 冲突 | ... |

### 学习曲线

- **新手**: 容易 / 中等 / 困难
- **现有用户**: 容易 / 中等 / 困难
- **原因**: ...

### 语法复杂度

**当前状态**:
```
语句类型: X/30
表达式层次: Y/10
关键字: Z/100
```

**添加后**:
```
语句类型: X+N/30  (增加 N 个)
表达式层次: Y+M/10 (增加 M 个)
关键字: Z+K/100  (增加 K 个)
```

**评估**: ✅ 在限制内 / ⚠️ 接近限制 / ❌ 超出限制

---

## 🛠️ 实现方案

### Parser 变更

**需要添加/修改的方法**:
```python
def _parse_proposed_feature(self) -> ProposedFeatureNode:
    """
    解析提议的语法特性

    语法:
        keyword param1 param2: ... end keyword
    """
    # 伪代码
    ...
```

**AST 节点**:
```python
@dataclass
class ProposedFeatureNode(ASTNode):
    param1: Expression
    param2: Optional[str]
    body: List[ASTNode]
```

### Interpreter 变更

```python
def visit_proposed_feature(self, node: ProposedFeatureNode):
    """执行提议的语法特性"""
    # 伪代码
    ...
```

### Lexer 变更

**新增 Token**:
- `PROPOSED_KEYWORD`
- ...

### 实现难度

- [ ] **简单** (1-2 天)
  - 只需简单的 parser 修改
  - 不涉及复杂的语义

- [ ] **中等** (3-5 天)
  - 需要 parser + interpreter 修改
  - 涉及中等复杂度的语义

- [ ] **困难** (1-2 周)
  - 需要大量修改
  - 涉及复杂的语义和作用域
  - 需要重构现有代码

### 依赖项

_列出实现这个功能需要的其他模块或功能_

- [ ] 依赖 Feature A
- [ ] 需要先实现 Feature B
- [ ] 无依赖

---

## 🧪 测试计划

### 测试用例

#### 正常情况

```python
def test_proposed_feature_basic():
    """测试基本功能"""
    source = """
    proposed_feature param1 param2:
        ...
    end proposed_feature
    """
    # 断言: ...
```

#### 边界情况

```python
def test_proposed_feature_edge_cases():
    """测试边界情况"""
    # 空参数
    # 最大参数
    # 嵌套使用
    ...
```

#### 异常情况

```python
def test_proposed_feature_errors():
    """测试错误处理"""
    # 缺少参数
    # 类型错误
    # 语法错误
    ...
```

### 测试覆盖率目标

- [ ] 行覆盖率 ≥ 90%
- [ ] 分支覆盖率 ≥ 80%
- [ ] 所有错误路径都有测试

---

## 📚 文档变更

### 需要更新的文档

- [ ] `GRAMMAR-MASTER.md` - 添加新特性行
- [ ] `GRAMMAR-CHANGELOG.md` - 添加变更记录
- [ ] `DSL-GRAMMAR.ebnf` - 添加 EBNF 规则
- [ ] `DSL-GRAMMAR-QUICK-REFERENCE.md` - 添加快速参考
- [ ] `DSL-SYNTAX-CHEATSHEET.md` - 添加速查表
- [ ] `04-API-REFERENCE.md` - 添加 API 说明
- [ ] 添加示例到 `examples/flows/`

### 文档示例

**在 GRAMMAR-MASTER.md 中的条目**:

```markdown
| X.Y | Proposed Feature | `keyword param1 param2: ... end` | ✅ | `_parse_proposed_feature()` | ✅ | 说明 |
```

---

## 🔄 替代方案

### 方案 1: [描述]

**语法**:
```flow
# 替代语法
...
```

**优点**:
- ...

**缺点**:
- ...

### 方案 2: [描述]

**语法**:
```flow
# 另一种替代语法
...
```

**优点**:
- ...

**缺点**:
- ...

### 不做任何改变

**当前做法**:
```flow
# 使用现有语法实现
...
```

**为什么不够**:
- ...

---

## 💬 讨论记录

### 社区反馈

_记录社区讨论的要点_

**支持意见**:
- @user1: ...
- @user2: ...

**反对意见**:
- @user3: ...
- @user4: ...

**问题和疑虑**:
- Q: ...
  A: ...

### 设计决策

_记录重要的设计决策和理由_

**决策 1**: 选择语法形式 A 而不是 B
- **理由**: ...

**决策 2**: ...

---

## ✅ 决策

### 核心团队评审

- [ ] 技术可行性: ✅ / ❌
- [ ] 语法一致性: ✅ / ❌
- [ ] 复杂度控制: ✅ / ❌
- [ ] 文档完整性: ✅ / ❌

### 最终决定

- **状态**: ✅ Approved / ❌ Rejected / ⏸️ Deferred
- **决定日期**: YYYY-MM-DD
- **决策者**: Core Team
- **理由**: ...

### 如果批准

**目标版本**: X.Y.0
**预计发布**: YYYY-MM-DD
**负责人**: @assignee

### 如果拒绝

**拒绝理由**:
1. ...
2. ...

**替代建议**:
- ...

---

## 📅 实施时间线

_如果批准，规划实施时间线_

### Phase 1: 设计阶段 (完成)
- [x] 提案编写
- [x] 社区讨论
- [x] 核心团队评审

### Phase 2: 实施阶段 (预计 X 天)
- [ ] Parser 实现
- [ ] Interpreter 实现
- [ ] AST 节点定义
- [ ] 单元测试

### Phase 3: 文档阶段 (预计 Y 天)
- [ ] 更新所有文档
- [ ] 编写示例
- [ ] 更新 CHANGELOG

### Phase 4: 验收阶段 (预计 Z 天)
- [ ] Code Review
- [ ] 集成测试
- [ ] 性能测试
- [ ] 用户验收测试

---

## 📎 附录

### 参考资料

- [相关提案]
- [外部参考]
- [讨论链接]

### 相关 Issue

- #123 - 相关问题
- #456 - 功能请求

---

**提案状态**: 📝 Draft
**最后更新**: YYYY-MM-DD
**维护者**: Proposal Author
