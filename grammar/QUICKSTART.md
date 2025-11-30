# 语法治理系统 - 快速入门

> **目的**: 帮助你快速掌握如何使用语法治理系统来控制 DSL 的发展

---

## 🎯 核心理念

```
GRAMMAR-MASTER.md (语法宪法)
      ↓
 定义项目的能力边界
      ↓
所有代码必须符合这个规范
      ↓
 自动检查确保同步
```

---

## 📚 三个核心文档

### 1. **GRAMMAR-MASTER.md** - 语法主控文档
- **用途**: 唯一的语法真理源，列出所有支持的语法特性
- **包含**: 49 个已实现的特性，状态、parser方法、测试覆盖
- **查看**: 想知道 "我们支持什么语法？" → 看这个文档

### 2. **GRAMMAR-GOVERNANCE.md** - 语法治理流程
- **用途**: 定义如何添加、修改、删除语法的流程
- **包含**: 变更流程、版本控制策略、设计原则
- **查看**: 想知道 "如何改变语法？" → 看这个文档

### 3. **check_grammar_sync.py** - 自动检查脚本
- **用途**: 自动验证文档和代码的同步状态
- **功能**: 检测未文档化的代码、缺失的实现、缺失的测试
- **使用**: `python scripts/check_grammar_sync.py`

---

## 🚀 日常使用

### 场景 1: 我想查看某个语法是否支持

```bash
# 方法 1: 直接查看 GRAMMAR-MASTER.md
grep -i "navigate" docs/GRAMMAR-MASTER.md

# 方法 2: 查看速查表
cat docs/DSL-SYNTAX-CHEATSHEET.md
```

### 场景 2: 我想添加新语法

```bash
# 步骤 1: 在 GRAMMAR-MASTER.md 添加一行，状态标记为 ❌

# 步骤 2: 实现 parser 方法
# 编辑 src/registration_system/dsl/parser.py

# 步骤 3: 添加 AST 节点（如需要）
# 编辑 src/registration_system/dsl/ast_nodes.py

# 步骤 4: 添加测试
# 编辑 tests/test_xxx.py

# 步骤 5: 检查同步
python scripts/check_grammar_sync.py

# 步骤 6: 更新 GRAMMAR-MASTER.md 状态为 ✅

# 步骤 7: 更新其他文档
# - docs/DSL-GRAMMAR.ebnf
# - docs/DSL-GRAMMAR-QUICK-REFERENCE.md
# - docs/DSL-SYNTAX-CHEATSHEET.md
```

### 场景 3: 我修改了 parser，想确保文档同步

```bash
# 运行同步检查
python scripts/check_grammar_sync.py

# 如果有问题，会显示：
# - 未文档化的 parser 方法
# - 缺失的实现
# - 缺失的测试

# 查看建议修复
python scripts/check_grammar_sync.py --fix-status
```

### 场景 4: 我想知道项目的语法统计

```bash
# 查看 GRAMMAR-MASTER.md 底部的统计部分
tail -100 docs/GRAMMAR-MASTER.md

# 或运行检查脚本
python scripts/check_grammar_sync.py
```

---

## 📊 当前状态总览

```
✅ 49 个已实现的特性
✅ 39 个有文档的 parser 方法
✅ 100% 的代码和文档同步
✅ 0 个缺测试的特性
✅ 0 个部分实现的特性
```

**分类统计**:
- 变量与赋值: 3 个
- 控制流: 4 个
- 导航: 3 个
- 等待: 3 个
- 选择: 2 个
- 动作: 10 个
- 断言: 4 个
- 服务调用: 1 个
- 数据提取: 1 个
- 工具: 2 个
- 表达式: 9 个层次
- 数据类型: 7 个

---

## 🔍 常用命令

### 检查同步状态
```bash
cd E:\cf\ads\flowby
python scripts/check_grammar_sync.py
```

### 查看详细输出
```bash
python scripts/check_grammar_sync.py --verbose
```

### 获取修复建议
```bash
python scripts/check_grammar_sync.py --fix-status
```

### 查找特定语法
```bash
# 在 GRAMMAR-MASTER.md 中搜索
grep -i "keyword" docs/GRAMMAR-MASTER.md

# 在所有文档中搜索
grep -r "keyword" docs/
```

### 验证 DSL 脚本
```bash
regflow your_script.flow
```

---

## 🎯 语法复杂度控制

### 当前限制
```
✅ 语句类型: 25/30 (83%)
✅ 表达式层次: 9/10 (90%)
✅ 关键字: 80+/100 (80%)
```

### 规则
- ⚠️ 当接近限制时，考虑合并相似功能
- ⚠️ 不要无限制地添加新语法
- ⚠️ 简洁性优于功能丰富性

---

## 🚦 状态标记含义

| 标记 | 含义 | 行动 |
|------|------|------|
| ✅ | 已实现且有测试 | 可以使用 |
| ⚠️ | 已实现但缺测试 | 需要添加测试 |
| 🚧 | 部分实现 | 需要完成实现 |
| ❌ | 未实现 | 计划中 |
| 🗑️ | 已废弃 | 将在下个版本移除 |

---

## 📝 变更控制清单

### 添加新语法前，确保：
- [ ] 语法是否真的必要？
- [ ] 是否与现有语法一致？
- [ ] 是否会增加学习成本？
- [ ] 是否有更简单的实现方式？
- [ ] 是否会破坏向后兼容性？

### 提交前，确保：
- [ ] GRAMMAR-MASTER.md 已更新
- [ ] Parser 方法已实现
- [ ] 测试已添加
- [ ] 所有文档已同步
- [ ] `python scripts/check_grammar_sync.py` 通过
- [ ] 所有测试通过 (`pytest`)

---

## 🎓 最佳实践

### DO ✅

1. **总是从 GRAMMAR-MASTER.md 开始**
   - 先文档化，后实现
   - 确保设计经过思考

2. **保持语法一致性**
   - 相似功能用相似语法
   - 关键字命名要直观

3. **及时运行同步检查**
   - 每次修改 parser 后运行
   - 提交前必须通过

4. **完整的测试覆盖**
   - 正常情况
   - 异常情况
   - 边界情况

### DON'T ❌

1. **不要先写代码再写文档**
   - 这会导致文档和实现脱节
   - 设计会不够深思熟虑

2. **不要添加"可能有用"的语法**
   - 只添加明确需要的
   - 避免过度设计

3. **不要忽略测试**
   - 没有测试的功能不算完成
   - 会导致回归问题

4. **不要随意破坏兼容性**
   - 必须经过废弃流程
   - 必须提供迁移路径

---

## 📈 成功指标

### 短期（当前）
- ✅ 文档和代码 100% 同步
- ✅ 所有特性都有测试
- ✅ check_grammar_sync.py 通过

### 中期（持续）
- ✅ 新特性都遵循流程添加
- ✅ 语法复杂度保持在限制内
- ✅ 零未文档化的代码

### 长期（目标）
- ✅ 语法稳定，很少变更
- ✅ 社区贡献者能轻松参与
- ✅ 文档成为学习的首选资源

---

## 🆘 常见问题

### Q: 我应该先看哪个文档？
**A**:
- 想了解支持什么 → `GRAMMAR-MASTER.md`
- 想快速查找语法 → `DSL-SYNTAX-CHEATSHEET.md`
- 想了解完整语法 → `DSL-GRAMMAR.ebnf`
- 想添加新功能 → `GRAMMAR-GOVERNANCE.md`

### Q: check_grammar_sync.py 报错怎么办？
**A**:
1. 查看错误类型（未文档化/缺实现/缺测试）
2. 运行 `--fix-status` 查看建议
3. 按建议修复
4. 重新运行检查

### Q: 如何确保我的改动不破坏现有功能？
**A**:
1. 运行完整测试: `pytest tests/`
2. 运行同步检查: `python scripts/check_grammar_sync.py`
3. 验证示例脚本: `regflow examples/flows/*.flow`

### Q: 语法达到复杂度上限怎么办？
**A**:
1. 审查现有语法，找出很少使用的
2. 考虑合并相似功能
3. 评估新功能的必要性
4. 如果确实需要，讨论提高限制

---

## 📞 获取帮助

- **查看文档**: `docs/` 目录下的所有文档
- **运行检查**: `python scripts/check_grammar_sync.py --help`
- **查看示例**: `examples/flows/` 目录
- **运行测试**: `pytest tests/ -v`

---

## 🎉 总结

**核心原则**: **GRAMMAR-MASTER.md 是唯一真理源**

**日常流程**:
1. 查语法 → 看 GRAMMAR-MASTER.md
2. 改语法 → 按 GRAMMAR-GOVERNANCE.md 流程
3. 检查同步 → 运行 check_grammar_sync.py
4. 提交前 → 确保所有检查通过

**记住**: 控制语法 = 控制项目核心能力 = 掌控项目方向

---

**维护者**: Flowby Core Team
**更新日期**: 2025-11-25
**状态**: ✅ Active
