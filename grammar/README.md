# Flowby Grammar Documentation

> **Flowby 语法文档中心** - Elegant Web Automation DSL
>
> **Version**: v5.1
> **Last Updated**: 2025-11-30
> **Status**: ✅ Stable

---

## 🎯 文档概览

这里包含 Flowby DSL 的完整语法规范、变更历史和语言提案。

**核心目标**:
- ✅ 提供语法的权威参考
- ✅ 记录语法演进历史
- ✅ 规范化语法变更流程
- ✅ 支持快速学习和查询

---

## 📚 核心文档

### 1. [MASTER.md](./MASTER.md) - 语法主控文档 ⭐

**用途**: 单一真理源，定义所有支持的语法特性

**包含内容**:
- 14个语法模块完整定义
  - 变量与赋值 (3 features)
  - 控制流 (7 features)
  - 导航 (3 features)
  - 等待 (3 features)
  - 选择 (2 features)
  - 动作 (10 features)
  - 断言与控制 (5 features)
  - 服务调用 (1 feature)
  - 数据提取 (1 feature)
  - 工具函数 (2 features)
  - OpenAPI 资源 (1 feature)
  - 用户函数 (3 features)
  - 模块系统 (4 features)
  - Input 表达式 (1 feature)
- 每个特性包含：语法 | 状态 | 版本 | 方法 | 测试 | 示例

**何时查看**:
- 查询某个语法是否支持
- 了解特性的添加版本
- 查看完整的语法特性列表

---

### 2. [CHANGELOG.md](./CHANGELOG.md) - 变更历史

**用途**: 记录所有版本的语法变更

**包含内容**:
- v5.1: Input 表达式支持
- v5.0: 模块系统（library/import/export）
- v4.3: 用户自定义函数
- v4.2: OpenAPI 资源集成
- v4.0: For 循环多变量解包
- v3.2: 动作语句表达式支持
- v3.1: When OR 模式、For 循环优化
- v3.0: Python 风格缩进块

**何时查看**:
- 了解语法演进历史
- 查看版本间的变化
- 迁移到新版本

---

### 3. [MIGRATION-GUIDE-v3.1.md](./MIGRATION-GUIDE-v3.1.md) - 迁移指南

**用途**: v3.0 到 v3.1 的迁移指南

**包含内容**:
- When 语句 OR 模式支持
- For 循环 `each` 关键字移除
- Service Call Python 风格语法
- 代码示例和最佳实践

**何时查看**:
- 从旧版本升级代码
- 了解语法变更影响

---

## 📖 语法参考文档

### 4. [DSL-GRAMMAR.ebnf](./DSL-GRAMMAR.ebnf) - EBNF 完整规范

**用途**: 形式化语法定义（Extended Backus-Naur Form）

**包含内容**:
- 完整的 EBNF 语法定义
- 所有语句和表达式的形式化规则
- 词法规则和优先级定义

**何时查看**:
- 需要精确的语法定义
- 开发解析器或工具
- 理解语法结构

---

### 5. [DSL-GRAMMAR-QUICK-REFERENCE.md](./DSL-GRAMMAR-QUICK-REFERENCE.md) - BNF 快速参考

**用途**: 简洁的 BNF 样式语法参考

**包含内容**:
- 所有语句类型的 BNF 定义
- 表达式优先级
- 常用模式快速查询

**何时查看**:
- 快速查询语法规则
- 编写代码时参考
- 学习语法结构

---

### 6. [DSL-SYNTAX-CHEATSHEET.md](./DSL-SYNTAX-CHEATSHEET.md) - 语法速查表

**用途**: 表格式语法速查

**包含内容**:
- 所有语法特性的表格总览
- 语法示例和说明
- 按类别组织的速查表

**何时查看**:
- 快速查找语法示例
- 学习新特性
- 作为参考手册

---

### 7. [V3-EBNF.md](./V3-EBNF.md) - V3 语法 EBNF

**用途**: V3.0 版本的详细 EBNF 规范

**包含内容**:
- Python 风格缩进块的形式化定义
- V3.0 特性完整规范
- 与 V2.0 的对比

---

### 8. [V3-EXAMPLES.flow](./V3-EXAMPLES.flow) - V3 语法示例集

**用途**: V3.0+ 语法的实战示例

**包含内容**:
- 所有语法特性的实际代码示例
- 最佳实践演示
- 完整的工作流示例

---

### 9. [V5-EXAMPLES.flow](./V5-EXAMPLES.flow) - V5 语法示例集 ⭐

**用途**: V5.0+ 新特性完整示例

**包含内容**:
- Module System (v5.0) 完整用法
  - Library declaration, Export, Import
  - From-import 和 Member access
- Input Expression (v5.1) 所有特性
  - 基本输入、默认值、类型转换
  - Password 输入、参数组合
- 与现有特性的集成示例
  - User-Defined Functions + Modules
  - Input + Control Flow
- 最佳实践和推荐项目结构
- 12个完整示例，覆盖所有 v5 特性

**何时查看**:
- 学习 v5.0/v5.1 新特性
- 了解模块系统最佳实践
- 掌握交互式输入用法
- 构建模块化的 Flowby 项目

---

### 10. [QUICKSTART.md](./QUICKSTART.md) - 快速开始

**用途**: 5分钟快速上手 Flowby

**包含内容**:
- 基本语法介绍
- Hello World 示例
- 常用模式速览

**何时查看**:
- 初次学习 Flowby
- 快速入门教程
- 基础概念学习

---

## 📝 提案系统

所有语法变更都通过标准化的提案流程。

### 目录结构

```
proposals/
├── README.md                              # 提案流程说明
├── TEMPLATE.md                            # 标准提案模板
├── EXAMPLE-001-try-catch.md              # 完整示例
├── PROPOSAL-002-while-loop.md             # While 循环
├── PROPOSAL-003-unified-selector.md       # 统一选择器
├── PROPOSAL-007-openapi-resource.md       # ⭐ OpenAPI 集成
├── PROPOSAL-008-function-statement.md     # ⭐ 用户函数
├── PROPOSAL-009-library-system.md         # ⭐ 模块系统
├── PROPOSAL-010-input-statement.md        # Input 表达式
└── ...                                    # 更多提案
```

### 提案状态

- ✅ **Completed** - 已完成并发布
- 🚧 **In Progress** - 实施中
- 💭 **Under Discussion** - 讨论中
- ❌ **Rejected** - 已拒绝
- ⏸️ **Deferred** - 推迟

### 如何创建提案

```bash
# 1. 复制模板
cp grammar/proposals/TEMPLATE.md \
   grammar/proposals/PROPOSAL-XXX-feature-name.md

# 2. 编辑提案
# 填写完整信息（动机、设计、示例、影响）

# 3. 提交 PR
git checkout -b proposal/XXX-feature-name
git add grammar/proposals/PROPOSAL-XXX-*.md
git commit -m "proposal: add feature-name proposal"
git push origin proposal/XXX-feature-name

# 4. 创建 GitHub Issue
# 添加标签：grammar-proposal
```

详见 [proposals/README.md](./proposals/README.md)

---

## 🚀 快速使用指南

### 场景 1: 我想查看支持哪些语法

```bash
# 查看主控文档
cat grammar/MASTER.md

# 查找特定语法
grep -i "navigate" grammar/MASTER.md

# 查看语法速查表
cat grammar/DSL-SYNTAX-CHEATSHEET.md
```

### 场景 2: 我想学习语法

**快速入门（5分钟）**:
1. 阅读 [QUICKSTART.md](./QUICKSTART.md)
2. 查看 [V3-EXAMPLES.flow](./V3-EXAMPLES.flow) 或 [V5-EXAMPLES.flow](./V5-EXAMPLES.flow)

**深入学习（30分钟）**:
1. [DSL-SYNTAX-CHEATSHEET.md](./DSL-SYNTAX-CHEATSHEET.md) - 10分钟
2. [MASTER.md](./MASTER.md) - 浏览特性 - 15分钟
3. [V5-EXAMPLES.flow](./V5-EXAMPLES.flow) - v5 新特性示例 - 5分钟

**完整掌握（1小时）**:
1. QUICKSTART.md
2. DSL-SYNTAX-CHEATSHEET.md
3. DSL-GRAMMAR-QUICK-REFERENCE.md
4. MASTER.md
5. V3-EXAMPLES.flow
6. V5-EXAMPLES.flow

### 场景 3: 我想提出新特性

```bash
# 步骤1: 阅读提案流程
cat grammar/proposals/README.md

# 步骤2: 参考示例提案
cat grammar/proposals/EXAMPLE-001-try-catch.md

# 步骤3: 创建提案
cp grammar/proposals/TEMPLATE.md \
   grammar/proposals/PROPOSAL-XXX-my-feature.md

# 步骤4: 提交 PR
# (详见上文"如何创建提案")
```

### 场景 4: 我想查看某个版本的变化

```bash
# 查看变更历史
cat grammar/CHANGELOG.md

# 查看 v3.1 迁移指南
cat grammar/MIGRATION-GUIDE-v3.1.md

# 查看完整语法演进
git log --oneline -- grammar/MASTER.md
```

---

## 📖 推荐学习路径

### 路径 A: 快速入门（15分钟）

1. [QUICKSTART.md](./QUICKSTART.md) - 5分钟
2. [DSL-SYNTAX-CHEATSHEET.md](./DSL-SYNTAX-CHEATSHEET.md) - 10分钟

### 路径 B: 语法使用者（1小时）

1. [QUICKSTART.md](./QUICKSTART.md) - 5分钟
2. [DSL-SYNTAX-CHEATSHEET.md](./DSL-SYNTAX-CHEATSHEET.md) - 15分钟
3. [MASTER.md](./MASTER.md) - 浏览特性列表 - 20分钟
4. [V3-EXAMPLES.flow](./V3-EXAMPLES.flow) + [V5-EXAMPLES.flow](./V5-EXAMPLES.flow) - 实战示例 - 20分钟

### 路径 C: 语法贡献者（2小时）

1. QUICKSTART.md - 5分钟
2. MASTER.md - 20分钟
3. CHANGELOG.md - 15分钟
4. DSL-GRAMMAR.ebnf - 30分钟
5. proposals/README.md - 10分钟
6. proposals/EXAMPLE-001-try-catch.md - 20分钟
7. 实践创建提案 - 20分钟

---

## 📊 当前状态

### 语法版本

```
当前版本:     v5.1 (2025-11-30)
稳定性:       ✅ Stable
下一版本:     v5.2 (计划中)
```

### 特性统计

```
语句类型:         16 个模块
总特性数:         54
用户函数:         ✅ 支持
模块系统:         ✅ 支持
OpenAPI 集成:     ✅ 支持 (5 phases)
Input 表达式:     ✅ 支持
```

### 实现状态

```
✅ 已实现并测试:   100%
核心特性:         稳定
文档覆盖:         完整
```

---

## ❓ 常见问题

**Q: Flowby 是什么？**
A: Flowby 是一个优雅的 Web 自动化 DSL，使用 Python 风格的语法，支持声明式的自动化流程编排。

**Q: 脚本文件使用什么扩展名？**
A: `.flow`

**Q: 如何快速学习语法？**
A:
1. 阅读 [QUICKSTART.md](./QUICKSTART.md)
2. 查看 [DSL-SYNTAX-CHEATSHEET.md](./DSL-SYNTAX-CHEATSHEET.md)
3. 运行 `examples/hello_world.flow`

**Q: 哪里可以找到语法示例？**
A:
- [V3-EXAMPLES.flow](./V3-EXAMPLES.flow) - V3 语法完整示例
- [V5-EXAMPLES.flow](./V5-EXAMPLES.flow) - V5 新特性完整示例 ⭐
- `examples/` 目录 - 实战脚本
- [MASTER.md](./MASTER.md) - 每个特性都有示例

**Q: 如何提出新的语法特性？**
A:
1. 阅读 [proposals/README.md](./proposals/README.md)
2. 使用 [proposals/TEMPLATE.md](./proposals/TEMPLATE.md) 创建提案
3. 提交 PR 并创建 Issue

**Q: 语法版本如何管理？**
A: 采用语义化版本（MAJOR.MINOR.PATCH）：
- MAJOR: 不兼容的重大变更
- MINOR: 新增功能，向后兼容
- PATCH: Bug 修复

详见 [CHANGELOG.md](./CHANGELOG.md)

---

## 🔗 相关资源

### 实现代码

- `src/flowby/parser.py` - Parser 实现
- `src/flowby/lexer.py` - Lexer 实现
- `src/flowby/ast_nodes.py` - AST 节点定义
- `src/flowby/interpreter.py` - Interpreter 实现
- `src/flowby/expression_evaluator.py` - 表达式求值

### 测试

- `tests/unit/` - 单元测试
- `tests/grammar_alignment/` - 语法对齐测试
- `tests/integration/` - 集成测试

运行测试:
```bash
pytest tests/ -v
```

### 示例

- `examples/hello_world.flow` - Hello World
- `examples/web_automation/` - Web 自动化示例
- `examples/api_integration/` - API 集成示例

---

## 📧 联系和贡献

### 维护团队

**Project**: Flowby
**Team**: Flowby Contributors
**Contact**: https://github.com/flowby/flowby

### 贡献指南

如需贡献：
1. Fork 项目仓库
2. 创建 feature 分支
3. 提交 PR（遵循提案流程）
4. 确保测试通过
5. 更新相关文档

详见 [CONTRIBUTING.md](../CONTRIBUTING.md)

### 报告问题

发现问题时：
1. 检查是否已有相关 Issue
2. 创建新 Issue，描述清楚
3. 提供复现步骤和示例代码

---

## 📜 许可证

MIT License - 详见 [LICENSE](../LICENSE)

---

**Version**: v5.1
**Last Updated**: 2025-11-30
**Status**: ✅ Stable
**Maintainer**: Flowby Contributors

---

**记住**: 优雅的语法是自动化的基础！🌸
