# Grammar Directory Structure

> **语法治理目录结构说明**
>
> **创建日期**: 2025-11-25
> **最后更新**: 2025-11-25

---

## 📁 目录结构

```
grammar/                                    # 语法治理专用目录
│
├── README.md                              # 主入口文档 (420行)
│   ├─ 系统概述
│   ├─ 核心文档导航
│   ├─ 工具使用指南
│   ├─ 提案流程说明
│   ├─ 当前状态统计
│   ├─ 快速使用指南 (4个场景)
│   ├─ 学习路径 (3条)
│   └─ FAQ
│
├── MASTER.md                              # 语法主控文档 (419行) ⭐
│   ├─ 49个语法特性完整定义
│   ├─ 25个语句类型 (10大类)
│   ├─ 9级表达式优先级
│   ├─ 7种数据类型
│   ├─ 5个系统变量命名空间
│   ├─ 19个内置函数
│   └─ 每个特性: ID | 名称 | 语法 | 状态 | 版本 | 方法 | 测试 | 说明
│
├── GOVERNANCE.md                          # 治理流程文档 (527行)
│   ├─ 6步添加新语法流程
│   ├─ 修改现有语法流程
│   ├─ 废弃策略 (最少2版本过渡)
│   ├─ 5种状态定义 (✅⚠️🚧❌🗑️)
│   ├─ 语法设计4大原则
│   ├─ 复杂度控制 (语句≤30, 表达式≤10, 关键字≤100)
│   └─ DO/DON'T 最佳实践
│
├── CHANGELOG.md                           # 变更历史 (576行)
│   ├─ 语义化版本规范
│   ├─ v2.0.0 变更日志 (Added/Changed/Fixed/Deprecated/Removed)
│   ├─ v1.0.0 基线版本
│   ├─ v1.0 → v2.0 迁移指南
│   ├─ 兼容性矩阵
│   └─ 未来版本计划 (v2.1.0)
│
├── CHANGE-MANAGEMENT.md                   # 完整管理指南 (905行)
│   ├─ 系统概述 (6大核心组件)
│   ├─ 文档体系详解
│   ├─ 完整的变更管理流程图
│   ├─ 版本控制系统详解
│   ├─ 变更分类 (MINOR/MAJOR/PATCH)
│   ├─ 自动化工具使用指南
│   ├─ 6个实际使用场景
│   ├─ 版本演进示例
│   └─ 最佳实践汇总
│
├── QUICKSTART.md                          # 快速入门 (327行)
│   ├─ 3步快速开始
│   ├─ 4个日常使用场景
│   ├─ 常用命令参考
│   ├─ 当前系统状态
│   ├─ 最佳实践速查
│   └─ FAQ
│
├── SUMMARY.md                             # 系统总结 (553行)
│   ├─ 完成的工作总览
│   ├─ 系统能力说明
│   ├─ 解决的问题列表
│   ├─ 成功指标
│   └─ 使用指南
│
├── DIRECTORY-STRUCTURE.md                 # 本文档 (目录结构说明)
│
├── proposals/                             # 提案系统目录
│   ├── README.md                          # 提案流程说明 (254行)
│   │   ├─ 7步提案流程
│   │   ├─ 状态标记说明
│   │   ├─ 活跃提案追踪
│   │   └─ 最佳实践
│   │
│   ├── TEMPLATE.md                        # 标准提案模板 (477行)
│   │   ├─ 提案元信息
│   │   ├─ 动机和背景
│   │   ├─ 提议的解决方案
│   │   ├─ 使用示例 (至少3个)
│   │   ├─ 影响分析
│   │   ├─ 实现方案
│   │   ├─ 测试计划
│   │   ├─ 文档变更清单
│   │   ├─ 替代方案
│   │   ├─ 讨论记录
│   │   ├─ 决策部分
│   │   └─ 实施时间线
│   │
│   ├── EXAMPLE-001-try-catch.md           # 示例提案 (752行)
│   │   └─ 完整的 try-catch 异常处理提案示例
│   │
│   └── archived/                          # 已归档的提案
│       └─ (已完成或已拒绝的提案存放处)
│
└── tools/                                 # 自动化工具目录
    ├── check_sync.py                      # 文档-代码同步检查器 (427行)
    │   ├─ 解析 MASTER.md 提取所有特性
    │   ├─ 解析 parser.py 提取所有方法
    │   ├─ 交叉检查文档和代码
    │   ├─ 生成同步报告
    │   └─ 当前状态: ✅ SYNCED (49/49)
    │
    └── check_version.py                   # 版本兼容性检查器 (487行)
        ├─ 提取脚本声明的语法版本
        ├─ 检测脚本使用的特性
        ├─ 比对特性版本数据库
        ├─ 生成兼容性报告
        └─ 提供迁移建议
```

---

## 📊 统计数据

### 文件统计

| 类别 | 文件数 | 总行数 | 说明 |
|------|--------|--------|------|
| **核心文档** | 7 | ~3,700 | 主控、治理、历史、指南、入门、总结、说明 |
| **提案系统** | 3 + 目录 | ~1,500 | 模板、流程、示例、归档目录 |
| **自动化工具** | 2 | ~900 | 同步检查、版本检查 |
| **总计** | **13** | **~6,100** | 完整的语法治理系统 |

### 语法特性统计

```
语句类型:         25 / 30  (83%)
表达式层次:       9 / 10   (90%)
关键字:           80+ / 100 (80%+)
内置函数:         19
系统变量命名空间:  5
数据类型:         7
VR规则:           4

总特性数:         49
文档化:           49 (100%)
实现状态:         25/25 语句类型 (100%)
同步状态:         ✅ SYNCED
```

---

## 🎯 目录用途

### 为什么需要独立目录？

1. **清晰的组织结构**
   - 所有语法治理内容集中在一个地方
   - 与通用文档分离，职责明确
   - 更容易找到相关文件

2. **逻辑分组**
   - 核心文档 (MASTER, GOVERNANCE, CHANGELOG等)
   - 提案系统 (proposals/)
   - 自动化工具 (tools/)
   - 三者紧密关联，放在一起更合理

3. **专业化管理**
   - 语法是DSL的核心，值得独立目录
   - 类似"宪法"级别的重要性
   - 变更需要严格的流程控制

4. **易于维护**
   - 所有语法相关的修改都在这个目录
   - 提案、文档、工具统一维护
   - 减少文档目录的复杂度

---

## 📖 快速导航

### 我想...

| 需求 | 文件 | 说明 |
|------|------|------|
| **了解整个系统** | [README.md](./README.md) | 主入口，完整指南 |
| **查看支持的语法** | [MASTER.md](./MASTER.md) | 49个特性完整列表 |
| **添加新语法** | [GOVERNANCE.md](./GOVERNANCE.md) | 6步添加流程 |
| **查看历史变更** | [CHANGELOG.md](./CHANGELOG.md) | 版本历史和迁移指南 |
| **深入理解系统** | [CHANGE-MANAGEMENT.md](./CHANGE-MANAGEMENT.md) | 完整管理指南 |
| **快速上手** | [QUICKSTART.md](./QUICKSTART.md) | 5分钟入门 |
| **创建提案** | [proposals/TEMPLATE.md](./proposals/TEMPLATE.md) | 提案模板 |
| **学习提案流程** | [proposals/README.md](./proposals/README.md) | 7步流程 |
| **查看提案示例** | [proposals/EXAMPLE-001-try-catch.md](./proposals/EXAMPLE-001-try-catch.md) | try-catch 示例 |
| **验证同步** | 运行 `tools/check_sync.py` | 文档-代码同步检查 |
| **检查兼容性** | 运行 `tools/check_version.py` | 版本兼容性检查 |

---

## 🔄 与其他文档的关系

### 主文档目录 (`docs/`)

`docs/README.md` 是整个项目的文档中心，包含：
- 快速参考文档
- 系统分析文档 (7部分)
- 技术分析文档 (4个)
- 语法规范文档 (EBNF等)
- **指向 `grammar/` 的链接**

### 语法目录 (`grammar/`)

`grammar/README.md` 是语法治理的入口，专注于：
- 语法特性定义
- 变更管理流程
- 提案系统
- 自动化工具

### 两者关系

```
docs/
├── README.md                     # 主文档中心
│   ├─ 系统分析
│   ├─ 技术文档
│   ├─ 语法规范 (EBNF)
│   └─ 👉 指向 grammar/
│
grammar/
└── README.md                     # 语法治理入口
    ├─ 语法定义 (MASTER.md)
    ├─ 变更流程 (GOVERNANCE.md)
    ├─ 历史追踪 (CHANGELOG.md)
    ├─ 提案系统 (proposals/)
    └─ 自动化工具 (tools/)
```

---

## 🚀 常用命令

```bash
# 查看整个语法治理系统
cat grammar/README.md

# 查看所有支持的语法
cat grammar/MASTER.md

# 查看语法变更历史
cat grammar/CHANGELOG.md

# 验证文档和代码同步
python grammar/tools/check_sync.py

# 检查脚本兼容性
python grammar/tools/check_version.py script.flow

# 创建新提案
cp grammar/proposals/TEMPLATE.md \
   grammar/proposals/PROPOSAL-002-my-feature.md

# 查看提案流程
cat grammar/proposals/README.md

# 查看提案示例
cat grammar/proposals/EXAMPLE-001-try-catch.md
```

---

## ✅ 完成检查清单

- [x] 创建 `grammar/` 目录结构
- [x] 移动所有语法治理文档 (6个)
- [x] 移动提案系统 (3个文档)
- [x] 移动自动化工具 (2个脚本)
- [x] 创建 `grammar/README.md` 入口文档
- [x] 更新工具脚本中的路径配置
- [x] 更新 `docs/README.md` 中的所有引用
- [x] 验证工具正常工作 (✅ SYNCED)
- [x] 使用 `git mv` 保留文件历史
- [x] 创建本说明文档

---

## 📞 获取帮助

**主入口**: [grammar/README.md](./README.md)

**问题类型**:
- 语法特性查询 → [MASTER.md](./MASTER.md)
- 添加新特性 → [GOVERNANCE.md](./GOVERNANCE.md)
- 历史变更 → [CHANGELOG.md](./CHANGELOG.md)
- 提案相关 → [proposals/README.md](./proposals/README.md)
- 工具使用 → [README.md](./README.md) FAQ 部分

---

**创建日期**: 2025-11-25
**维护者**: Registration System Core Team
**状态**: ✅ Complete

**记住**: 所有语法相关的内容都在这个目录！🚀
