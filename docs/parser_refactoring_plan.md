# Parser 重构计划

## 当前状态
- **文件**: `src/flowby/parser.py`
- **总行数**: 3272 行
- **解析方法行数**: 3178 行
- **问题**: 单文件过大，难以维护

## 结构分析

| 区域 | 行数 | 占比 |
|------|------|------|
| Expressions | 659 | 20.7% |
| Control Flow | 521 | 16.4% |
| Helpers | 476 | 15.0% |
| Actions | 258 | 8.1% |
| Wait | 243 | 7.6% |
| Modules | 206 | 6.5% |
| Functions | 166 | 5.2% |
| Variables | 111 | 3.5% |
| Log/Extract | 152 | 4.8% |
| Others | 603 | 19.0% |

## 拆分方案

### 方案 A：按功能完全拆分（推荐）

```
src/flowby/parser/
├── __init__.py           # 主入口，导出 Parser 类
├── base.py              # 基础 Parser 类（核心方法）
├── expressions.py        # 表达式解析（~659 行）
├── control_flow.py       # 控制流解析（~521 行）
├── statements.py         # 语句解析（~429 行）
├── actions.py           # 浏览器动作（~641 行）
├── modules.py           # 模块系统（~206 行）
└── helpers.py           # 辅助方法（~476 行）
```

**优点**：
- 每个文件大小适中（200-700行）
- 职责清晰，易于维护
- 符合单一职责原则

**缺点**：
- 需要大量重构工作
- 可能影响现有测试
- 需要仔细处理模块间依赖

### 方案 B：Mixin 模式（轻量级）

保持 `parser.py` 为主类，将各功能提取为 Mixin：

```python
# parser_expressions_mixin.py
class ExpressionParserMixin:
    def _parse_expression(self): ...
    def _parse_logical_or(self): ...
    # ...

# parser.py
from .parser_expressions_mixin import ExpressionParserMixin
from .parser_control_flow_mixin import ControlFlowParserMixin
# ...

class Parser(ExpressionParserMixin, ControlFlowParserMixin, ...):
    def __init__(self): ...
    def parse(self): ...
```

**优点**：
- 改动较小，风险低
- 向后兼容，不影响现有代码
- 逐步迁移，可以增量重构

**缺点**：
- 仍然是紧耦合
- Mixin 顺序可能引起问题
- 没有完全解决大文件问题

## 推荐方案：方案 B（Mixin 模式）

**原因**：
1. **风险可控**：向后兼容，不破坏现有功能
2. **增量迁移**：可以逐步提取，每次提取后都能运行测试
3. **实用性**：项目未发布，但有 562 个测试，需要保证稳定性

## 实施步骤

### Phase 1: 提取 Expressions（最大模块）
1. 创建 `src/flowby/parser/` 目录
2. 创建 `expressions_mixin.py`，提取所有表达式解析方法
3. 在 `parser.py` 中继承 `ExpressionParserMixin`
4. 运行测试验证

### Phase 2: 提取 Control Flow
1. 创建 `control_flow_mixin.py`
2. 提取控制流解析方法
3. 运行测试验证

### Phase 3: 提取 Actions
1. 创建 `actions_mixin.py`
2. 提取浏览器动作解析方法
3. 运行测试验证

### Phase 4: 提取其他模块
- `modules_mixin.py` - 模块系统
- `statements_mixin.py` - 语句解析
- `helpers_mixin.py` - 辅助方法

### Phase 5: 优化和文档
- 添加每个 Mixin 的文档
- 更新 CLAUDE.md
- 创建架构图

## 预期效果

**重构前**:
```
parser.py: 3272 行
```

**重构后**:
```
parser/
├── __init__.py           # ~50 行（主入口）
├── base.py              # ~200 行（核心方法）
├── expressions_mixin.py  # ~659 行
├── control_flow_mixin.py # ~521 行
├── actions_mixin.py     # ~641 行
├── statements_mixin.py   # ~429 行
├── modules_mixin.py     # ~206 行
└── helpers_mixin.py     # ~476 行
```

**改进**:
- ✅ 单文件行数从 3272 减少到最大 659
- ✅ 职责清晰，易于定位问题
- ✅ 便于新功能开发
- ✅ 向后兼容，测试不受影响

## 时间估算
- Phase 1-2: 2-3 小时
- Phase 3-4: 2-3 小时
- Phase 5: 1 小时
- **总计**: 5-7 小时

## 风险评估
- **低风险**：Mixin 模式向后兼容
- **测试覆盖**：562 个测试确保功能正确
- **回滚方案**：Git 版本控制，随时可回退
