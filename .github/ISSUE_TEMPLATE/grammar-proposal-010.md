---
name: Grammar Proposal #010 Discussion
about: Discussion for Resource Constructor Refactoring Proposal
title: '[Grammar Proposal #010] Resource Constructor Refactoring'
labels: grammar-proposal, breaking-change
assignees: ''
---

# 🎯 Grammar Proposal #010: Resource Constructor Refactoring

## 📋 提案概述

**提案编号**: #010
**提出日期**: 2025-11-30
**提出人**: Flowby Core Team
**状态**: 📝 Draft → 💭 Under Discussion
**目标版本**: v6.0
**影响级别**: MAJOR (Breaking Change)

**提案文档**: [PROPOSAL-010-resource-constructor.md](../../grammar/proposals/PROPOSAL-010-resource-constructor.md)
**PR**: https://github.com/btrobot/flowby/pull/new/proposal/010-resource-constructor

---

## 🎬 摘要

本提案建议将 `resource` 特殊语句重构为 `Resource()` 内置构造函数，实现更灵活的动态 API 客户端创建。

### 当前语法（v5.1）
```dsl
resource api:
    spec: "api.yml"
    base_url: "https://api.example.com"
    auth: {type: "bearer", token: env.TOKEN}
```

### 提议语法（v6.0）
```dsl
let api = Resource("api.yml",
    base_url = "https://api.example.com",
    auth = {type: "bearer", token: dynamic_token}
)
```

---

## 🔥 核心动机

当前 `resource` 语句存在以下局限性：

### 1️⃣ 无法支持运行时动态配置
```dsl
# ❌ 当前无法实现
step "动态获取 token":
    let login_response = http.post(AUTH_URL, credentials)
    let token = login_response.access_token

    # 如何使用这个 token 创建 resource？
```

### 2️⃣ 无法创建多个实例
```dsl
# ❌ 当前需要声明多个 resource
resource dev_api from "api.yml"
resource prod_api from "api.yml"

# ✅ 提议方案
let dev_api = Resource("api.yml", base_url = DEV_URL)
let prod_api = Resource("api.yml", base_url = PROD_URL)
```

### 3️⃣ 无法在条件/循环中创建
```dsl
# ❌ 当前无法实现
for env in ["dev", "staging", "prod"]:
    # 无法动态创建 resource
```

---

## ✨ 方案优势

1. **语法一致性** - 与 `let x = ...` 模式统一，符合 v3.0 Python 风格
2. **灵活性提升** - 支持运行时动态配置、多实例、条件创建
3. **降低复杂度** - 移除特殊语句，统一为构造函数
4. **实现简单** - 复用 90% 现有代码（`ResourceNamespace`, `OpenAPISpec`）
5. **架构契合** - 完美融入三阶段解释器模型

---

## ⚠️ 影响评估

### Breaking Change
- 影响级别: **MAJOR**
- 受影响代码: 估计 80-95% 的 resource 使用场景
- 迁移难度: **中等**（提供自动化迁移工具）

### 迁移策略（渐进式废弃）
1. **v5.2** (2周后): 添加 `Resource()` 函数，两种语法并存
2. **v5.3** (1个月后): `resource` 语句触发废弃警告
3. **v6.0** (3个月后): 完全移除 `resource` 语句

---

## 💬 征求意见

请社区成员就以下方面提供反馈：

### 1. 动机分析
- [ ] 是否同意当前 `resource` 语句存在这些局限性？
- [ ] 这些场景是否是真实需求？
- [ ] 还有其他痛点场景吗？

### 2. 方案设计
- [ ] `Resource()` 构造函数方案是否合理？
- [ ] 语法设计是否清晰易用？
- [ ] 参数设计是否完善？

### 3. 迁移策略
- [ ] 迁移时间线（3个月）是否合理？
- [ ] 是否需要更长的过渡期？
- [ ] 自动化迁移工具是否足够？

### 4. 替代方案
- [ ] 是否有更好的方案？
- [ ] 是否可以保留 `resource` 语句并增强？

---

## 📊 技术细节

### 实现改动
- **移除**: `RESOURCE` token, `_parse_resource()`, `ResourceStatement`, `visit_ResourceStatement()`
- **新增**: `builtin_Resource()` 函数（~50 行）
- **复用**: `ResourceNamespace`, `OpenAPISpec`（无需改动）

### 工作量估算
- 核心实现: 2-3 天
- 测试覆盖: 1-2 天
- 迁移工具: 1-2 天
- 文档更新: 1 天
- **总计**: 约 1 周

---

## 🗳️ 投票与反馈

请在评论中表达您的意见，使用以下格式：

**支持 / 反对 / 中立**

**理由**:
- （您的观点）

**建议**:
- （可选的改进建议）

---

## 📅 讨论时间表

- **提案发布**: 2025-11-30
- **社区讨论**: 2025-11-30 ~ 2025-12-07 (1 周)
- **核心团队评审**: 2025-12-08 ~ 2025-12-10 (3 天)
- **最终决策**: 2025-12-10

---

## 📎 相关资料

- **提案文档**: [PROPOSAL-010-resource-constructor.md](../../grammar/proposals/PROPOSAL-010-resource-constructor.md)
- **原始提案**: [PROPOSAL-007-openapi-resource-statement.md](../../grammar/proposals/PROPOSAL-007-openapi-resource-statement.md)
- **实现代码**:
  - [resource_namespace.py](../../src/flowby/resource_namespace.py)
  - [openapi_loader.py](../../src/flowby/openapi_loader.py)

---

**期待您的宝贵意见！** 🌸
