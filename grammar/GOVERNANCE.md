# DSL Grammar Governance - 语法治理方案

> **问题**: 失去了对语法的总体把控，不清楚系统到底有哪些语法
> **方案**: 建立语法治理体系，以 GRAMMAR-MASTER.md 为唯一真理源

---

## 🎯 核心原则

### 1. 单一真理源 (Single Source of Truth)

```
┌─────────────────────────────────────┐
│     GRAMMAR-MASTER.md               │  ← 唯一权威
│  (定义所有已实现的语法)             │
└────────────┬────────────────────────┘
             │
             ├─→ parser.py (实现必须符合)
             ├─→ tests/ (测试必须覆盖)
             ├─→ DSL-GRAMMAR.ebnf (形式化定义)
             └─→ 其他文档 (参考文档)
```

**规则**:
- ✅ GRAMMAR-MASTER.md 定义了什么 = 项目支持什么
- ✅ 如果不在 GRAMMAR-MASTER.md，就不是正式功能
- ✅ 任何语法变更必须先更新 GRAMMAR-MASTER.md

---

## 📋 现状分析

### 当前问题

1. **文档分散**
   - ❌ DSL-GRAMMAR.ebnf (形式化，但难读)
   - ❌ DSL-GRAMMAR-QUICK-REFERENCE.md (快速参考)
   - ❌ DSL-SYNTAX-CHEATSHEET.md (速查表)
   - ❌ 技术分析文档 (深度分析)
   - ❌ 没有明确的"什么是正式支持的"

2. **规范与实现脱节**
   - ❌ parser.py 实现了新功能，但文档未更新
   - ❌ 文档写了，但实现不完整
   - ❌ 测试覆盖不完整

3. **变更控制缺失**
   - ❌ 没有明确的语法变更流程
   - ❌ 没有版本控制
   - ❌ 没有兼容性策略

### 解决方案

✅ **GRAMMAR-MASTER.md** 作为控制中心：
- 清晰的特性矩阵（25 个语句类型，状态标记）
- 实现状态追踪（✅ 已实现、⚠️ 缺测试、🚧 部分实现、❌ 未实现）
- Parser 方法映射
- 测试覆盖追踪
- 变更控制流程

---

## 🚦 语法治理流程

### 流程 1: 添加新语法

```
步骤 1: 提出需求
   ├─ 在 GRAMMAR-MASTER.md 添加新行
   ├─ 状态标记为 ❌ Not Implemented
   ├─ 写清楚语法、用途、示例
   └─ 提交 PR / 讨论

步骤 2: 设计评审
   ├─ 语法是否与现有一致？
   ├─ 是否有歧义？
   ├─ 是否会破坏兼容性？
   └─ 批准后进入实现

步骤 3: 实现
   ├─ parser.py 添加 _parse_xxx() 方法
   ├─ ast_nodes.py 添加 AST 节点（如需要）
   ├─ interpreter.py 添加执行逻辑
   └─ GRAMMAR-MASTER.md 更新为 🚧 Partial

步骤 4: 测试
   ├─ tests/ 添加测试用例
   ├─ 覆盖正常/异常/边界情况
   └─ GRAMMAR-MASTER.md 更新测试列

步骤 5: 文档同步
   ├─ DSL-GRAMMAR.ebnf 添加 EBNF 规则
   ├─ DSL-GRAMMAR-QUICK-REFERENCE.md 添加示例
   ├─ DSL-SYNTAX-CHEATSHEET.md 添加速查
   └─ GRAMMAR-MASTER.md 更新为 ✅ Implemented & Tested

步骤 6: 验收
   ├─ 检查 Grammar Conformance Checklist
   ├─ 所有测试通过
   ├─ 文档完整
   └─ Commit & Merge
```

### 流程 2: 修改已有语法

```
步骤 1: 标记变更
   ├─ GRAMMAR-MASTER.md 添加新行（新语法）
   ├─ 旧语法标记为 🗑️ Deprecated
   └─ 写明变更原因和迁移路径

步骤 2: 实现新语法
   ├─ 保持旧语法兼容（至少 1 个版本）
   ├─ 添加 deprecation warning
   └─ 实现新语法

步骤 3: 迁移期
   ├─ 文档同时标注新旧语法
   ├─ 提供迁移脚本/指南
   └─ 更新示例到新语法

步骤 4: 移除旧语法
   ├─ 下一个大版本移除
   ├─ 从 GRAMMAR-MASTER.md 删除 🗑️ 行
   └─ 清理代码
```

### 流程 3: 移除语法

```
步骤 1: 废弃标记
   ├─ GRAMMAR-MASTER.md 标记为 🗑️ Deprecated
   ├─ 添加 deprecation warning
   └─ 文档注明将在哪个版本移除

步骤 2: 废弃期（至少 1 个大版本）
   ├─ 保持功能可用
   ├─ 警告用户迁移
   └─ 提供替代方案

步骤 3: 移除
   ├─ parser.py 删除相关代码
   ├─ GRAMMAR-MASTER.md 删除该行
   └─ 更新所有文档
```

---

## 📊 语法状态管理

### 状态定义

| 状态 | 图标 | 含义 | parser.py | tests/ | docs/ |
|------|------|------|-----------|--------|-------|
| **Implemented & Tested** | ✅ | 完全可用 | ✅ | ✅ | ✅ |
| **Needs Tests** | ⚠️ | 功能实现但缺测试 | ✅ | ❌ | ✅ |
| **Partial** | 🚧 | 部分实现，不稳定 | 🚧 | 部分 | ✅ |
| **Not Implemented** | ❌ | 计划中，未实现 | ❌ | ❌ | ✅ |
| **Deprecated** | 🗑️ | 即将移除 | ✅ | ✅ | 标注废弃 |

### 状态转换

```
❌ Not Implemented
   ↓ (开始实现)
🚧 Partial
   ↓ (实现完成)
⚠️ Needs Tests
   ↓ (添加测试)
✅ Implemented & Tested
   ↓ (决定废弃)
🗑️ Deprecated
   ↓ (下一个大版本)
[删除]
```

---

## 🎯 项目控制建议

### 建议 1: 每周语法审查

**目的**: 确保 GRAMMAR-MASTER.md 与实际代码同步

**步骤**:
```bash
# 1. 检查是否有未文档化的 parser 方法
grep "def _parse_" src/registration_system/dsl/parser.py | \
  wc -l  # 应该等于 GRAMMAR-MASTER.md 中的语句数量

# 2. 检查测试覆盖率
pytest tests/ --cov=src/registration_system/dsl/parser \
  --cov-report=html

# 3. 检查是否有 ⚠️ 或 🚧 状态
# 应该尽快修复

# 4. 检查 🗑️ 状态
# 计划移除时间
```

### 建议 2: 语法冻结期

**目的**: 在稳定版本发布前，冻结语法变更

**规则**:
- 🔒 冻结期间只能修 bug，不能添加新语法
- 🔒 已有语法不能改动（除非是 critical bug）
- 🔒 只允许完善测试和文档

**时机**:
- 主版本发布前 2 周
- 重要部署前 1 周

### 建议 3: 语法版本控制

**方案**: 语法版本独立于项目版本

```
项目版本: 1.2.3
语法版本: DSL v2.0

对应关系:
- 项目 1.x → DSL v1.0
- 项目 2.x → DSL v2.0
- 项目 3.x → DSL v3.0 (Breaking changes)
```

**兼容性策略**:
- ✅ Minor 版本（2.1, 2.2）只能添加语法，不能改/删
- ✅ Major 版本（3.0）可以破坏兼容性
- ✅ 废弃至少保留 1 个 minor 版本

### 建议 4: 语法复杂度控制

**目的**: 防止语法过度复杂

**指标**:
```
✅ 语句类型 ≤ 30 个
✅ 表达式优先级层次 ≤ 10 个
✅ 每个语句的变体 ≤ 5 个
✅ 关键字总数 ≤ 100 个
```

**当前状态** (v2.0):
```
语句类型: 25/30 ✅
优先级层次: 9/10 ✅
关键字: 80+/100 ✅
```

**规则**:
- ❌ 达到上限前不再添加新语法
- ✅ 考虑合并相似语法
- ✅ 考虑废弃很少使用的语法

### 建议 5: 实现 "Grammar Linter"

**目的**: 自动检查 GRAMMAR-MASTER.md 与代码的一致性

**功能**:
```python
# scripts/check_grammar_sync.py

1. 解析 GRAMMAR-MASTER.md
2. 提取所有 ✅ 状态的特性
3. 检查 parser.py 中是否有对应方法
4. 检查 tests/ 中是否有测试
5. 生成报告

输出:
✅ All 25 features have parser methods
⚠️ 3 features missing tests:
   - Feature 6.7 (Press)
   - Feature 8.1 (Call Service)
   - Feature 10.2 (Screenshot)
❌ 1 parser method not documented:
   - _parse_experimental_feature()
```

**集成到 CI**:
```yaml
# .github/workflows/grammar-check.yml
- name: Check Grammar Sync
  run: python scripts/check_grammar_sync.py

- name: Fail if out of sync
  run: |
    if [ $? -ne 0 ]; then
      echo "Grammar and implementation are out of sync!"
      exit 1
    fi
```

---

## 📐 语法设计原则

### 1. 一致性原则

**示例 - 好的设计**:
```flow
# 所有"选择"类操作都用 select
select "#username"
select option "USA" from "#country"

# 所有"等待"类操作都用 wait
wait 2 seconds
wait for element "#button"
wait for navigation
```

**示例 - 不好的设计**:
```flow
# ❌ 不一致
select "#username"
choose option "USA"  # 应该用 select option

wait 2 seconds
pause for element "#button"  # 应该用 wait for
```

### 2. 明确性原则

**示例 - 好的设计**:
```flow
# 明确的关键字
navigate to "https://example.com"
wait for element "#button"
click "#submit"
```

**示例 - 不好的设计**:
```flow
# ❌ 歧义
go "https://example.com"  # 是 navigate 还是别的？
wait "#button"            # 等待什么？时间？元素？
hit "#submit"             # hit 和 click 有什么区别？
```

### 3. 简洁性原则

**示例 - 好的设计**:
```flow
# 可选部分用 [ ]
type "text" [into SEL] [slowly]
click [SEL]
```

**示例 - 不好的设计**:
```flow
# ❌ 过于冗长
type text "text" into element "#input" with speed slowly
click on element "#button" with method left_click
```

### 4. 扩展性原则

**示例 - 好的设计**:
```flow
# 可扩展的服务调用
call "http.get" with url="..." into response
call "custom.provider" with params... into result
```

**示例 - 不好的设计**:
```flow
# ❌ 内置硬编码
http_get url="..."  # 无法扩展到自定义服务
```

---

## 🔧 实施步骤

### Phase 1: 建立基础 (1-2 天)

- [x] ✅ 创建 GRAMMAR-MASTER.md
- [ ] ⏳ 验证所有 25 个特性状态
- [ ] ⏳ 检查测试覆盖率
- [ ] ⏳ 更新状态图标

### Phase 2: 同步文档 (2-3 天)

- [ ] ⏳ 确保 DSL-GRAMMAR.ebnf 与 GRAMMAR-MASTER.md 一致
- [ ] ⏳ 确保 Quick Reference 与 GRAMMAR-MASTER.md 一致
- [ ] ⏳ 确保 Cheatsheet 与 GRAMMAR-MASTER.md 一致
- [ ] ⏳ 交叉检查所有示例

### Phase 3: 自动化检查 (3-5 天)

- [ ] ⏳ 实现 `check_grammar_sync.py`
- [ ] ⏳ 添加 CI 检查
- [ ] ⏳ 测试覆盖率要求 ≥ 90%

### Phase 4: 流程培训 (1 天)

- [ ] ⏳ 团队培训：如何使用 GRAMMAR-MASTER.md
- [ ] ⏳ 代码审查清单
- [ ] ⏳ 示例演示

---

## 📊 成功指标

### 短期目标 (1 个月)

- ✅ GRAMMAR-MASTER.md 成为团队的首选参考
- ✅ 所有语法特性有明确状态
- ✅ 测试覆盖率 ≥ 90%
- ✅ 文档同步率 = 100%

### 中期目标 (3 个月)

- ✅ 自动化检查集成到 CI
- ✅ 零 ⚠️ 和 🚧 状态
- ✅ 语法变更流程标准化
- ✅ 团队完全采用新流程

### 长期目标 (6 个月)

- ✅ 语法版本独立管理
- ✅ 完善的兼容性策略
- ✅ 社区贡献者能轻松参与语法设计
- ✅ 语法设计模式文档化

---

## 🎓 团队培训材料

### 快速入门

**新成员**:
1. 阅读 `GRAMMAR-MASTER.md` 了解所有语法
2. 阅读 `DSL-SYNTAX-CHEATSHEET.md` 快速查找
3. 查看 `examples/flows/` 学习实际用法

**开发者**:
1. 理解语法治理流程
2. 学习如何添加新语法（6 步流程）
3. 学习如何运行 grammar sync 检查

**维护者**:
1. 掌握版本控制策略
2. 学习语法设计原则
3. 学习如何进行语法审查

### Cheat Sheet

```bash
# 查看当前语法状态
cat docs/GRAMMAR-MASTER.md | grep "| ✅"  # 已实现
cat docs/GRAMMAR-MASTER.md | grep "| ⚠️"  # 缺测试
cat docs/GRAMMAR-MASTER.md | grep "| 🚧"  # 部分实现

# 检查同步状态
python scripts/check_grammar_sync.py

# 运行所有语法测试
pytest tests/ -v -k "test_"

# 生成覆盖率报告
pytest tests/ --cov=src/registration_system/dsl \
  --cov-report=html

# 验证 DSL 脚本
regflow --check-only examples/flows/your_script.flow
```

---

## 📞 支持与反馈

### 遇到问题？

1. **语法不清楚？**
   - 查看 `GRAMMAR-MASTER.md` 第一时间确认
   - 查看 `DSL-SYNTAX-CHEATSHEET.md` 快速参考
   - 查看 `examples/flows/` 实际示例

2. **发现 bug？**
   - 检查 `GRAMMAR-MASTER.md` 确认是否是已知问题
   - 提交 Issue 并引用对应的特性编号（如 "Feature 6.7"）

3. **想添加新语法？**
   - 先在 `GRAMMAR-MASTER.md` 添加 ❌ 行
   - 提交 PR 讨论
   - 按照 6 步流程实施

---

## 🎉 总结

### 核心理念

```
GRAMMAR-MASTER.md = 项目的"宪法"
            ↓
      定义什么是合法的
            ↓
   所有实现必须遵守
            ↓
    变更必须经过流程
```

### 立即行动

1. **今天**: 阅读 `GRAMMAR-MASTER.md`，熟悉所有 25 个语法特性
2. **本周**: 验证所有特性状态，修复 ⚠️ 和 🚧
3. **本月**: 实施自动化检查，确保同步

### 最终目标

**让每个团队成员都能自信地回答**:
- ✅ 我们支持哪些语法？→ 看 GRAMMAR-MASTER.md
- ✅ 某个特性实现了吗？→ 看 GRAMMAR-MASTER.md 的状态列
- ✅ 如何添加新语法？→ 看 GRAMMAR-GOVERNANCE.md 的流程
- ✅ 文档和代码一致吗？→ 运行 check_grammar_sync.py

---

**记住**: 控制语法 = 控制项目的核心能力边界

**维护者**: Registration System Core Team
**创建日期**: 2025-11-25
**文档状态**: ✅ Active
