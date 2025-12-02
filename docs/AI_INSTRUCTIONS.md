# AI 工作指令 - Flowby 测试重建

## 欢迎

你的任务是重建 Flowby DSL 项目的测试套件。这是一个有明确目标和质量标准的长期任务。

## 快速开始

1. **阅读主计划**: `docs/TEST_REBUILD_PLAN.md`（~200 行，包含所有细节）
2. **查看当前进度**: `python scripts/task_tracker.py status`
3. **选择下一个任务**: 从 Phase 1 的 Task 1.1 开始
4. **执行任务**: 按照计划文档中的详细说明
5. **质量检查**: `python scripts/quality_check.py <test_file>`
6. **更新进度**: `python scripts/task_tracker.py complete <task_id> <coverage> <tests>`
7. **提交代码**: 按照提交规范提交

## 核心原则（必读）

### 🚨 绝对禁止

1. **不要修改业务代码**: `src/` 目录下的所有文件都不能修改
2. **不要破坏现有测试**: 确保 `pytest tests/` 始终全部通过
3. **不要跳过质量检查**: 每个任务完成后必须运行质量检查脚本

### ✅ 必须遵守

1. **保持绿色**: 任何时候运行测试都必须通过
2. **增量进行**: 一次只做一个任务
3. **先添加后删除**: 重构时先创建新测试，确认通过后再删除旧测试
4. **运行验证**: 每个任务完成后运行所有验证脚本

## 标准工作流程

每个任务的标准流程（Copy & Paste）:

```bash
# Step 1: 查看任务详情
# 在 docs/TEST_REBUILD_PLAN.md 找到当前任务的详细说明

# Step 2: 创建测试文件
# 根据任务要求创建新的测试文件

# Step 3: 运行新测试
pytest <new_test_file> -v

# Step 4: 运行所有测试（确保没有破坏）
pytest tests/ -x

# Step 5: 检查覆盖率
pytest tests/ --cov=src/flowby --cov-report=term | grep TOTAL

# Step 6: 质量检查
python scripts/quality_check.py <new_test_file>

# Step 7: 验证通过
python scripts/verify_tests.py

# Step 8: 更新进度
python scripts/task_tracker.py complete <task_id> <coverage_delta> <tests_added>
# 例如: python scripts/task_tracker.py complete 2.1 59.0 52

# Step 9: 提交
git add .
git commit -m "test: <task description>

<details>

Coverage:
- <module>: <before>% → <after>%

Tests added: <count>
"
```

## 任务清单速查

### Phase 1: 准备工作（约 1 小时）
- [ ] Task 1.1: 创建单元测试模板
- [ ] Task 1.2: 创建集成测试模板
- [ ] Task 1.3: 创建验证脚本

### Phase 2: 补充集成测试（约 8-10 小时，**重点**）
- [ ] Task 2.1: Runner 集成测试（11% → 70%, ~52 tests）
- [ ] Task 2.2: Response Handler（17% → 70%, ~40 tests）
- [ ] Task 2.3: Resource Integration（19% → 70%, ~35 tests）
- [ ] Task 2.4: Resilience（21% → 70%, ~30 tests）

### Phase 3: 补充单元测试（约 10-12 小时）
- [ ] Task 3.1: Interpreter（50% → 75%, ~60 tests）
- [ ] Task 3.2: Expression Evaluator（46% → 75%, ~100 tests）

### Phase 4: E2E 测试（约 6-8 小时）
- [ ] Task 4.1: Web 自动化 E2E（~10 scenarios）
- [ ] Task 4.2: API 测试 E2E（~10 scenarios）

### Phase 5: 重构现有测试（约 15-20 小时）
- [ ] Task 5.1: 拆分 test_v3_02_control_flow.py
- [ ] Task 5.2: 拆分 test_expression_evaluator.py

### Phase 6: 文档和工具（约 4-6 小时）
- [ ] Task 6.1: 编写测试文档
- [ ] Task 6.2: 创建测试生成脚本
- [ ] Task 6.3: 创建覆盖率监控脚本

## 质量标准

每个任务完成后，必须满足以下标准：

### 1. 代码质量（80 分以上）

运行质量检查：
```bash
python scripts/quality_check.py <test_file>
```

必须通过的检查项：
- ✅ Black 代码格式化
- ✅ Flake8 代码风格
- ✅ 所有测试可执行
- ✅ 测试命名规范
- ✅ 文档完整性
- ✅ 使用 Fixture
- ✅ 断言质量
- ✅ 覆盖率贡献
- ✅ 无重复代码

### 2. 测试覆盖率

运行覆盖率检查：
```bash
pytest <test_file> --cov=src/flowby/<module> --cov-report=term
```

要求：
- 单个模块覆盖率达到任务目标（通常 70-75%）
- 总覆盖率不下降

### 3. 测试通过率

运行所有测试：
```bash
pytest tests/ -v
```

要求：
- 100% 通过（0 失败）
- 允许少量 skipped（已存在的）

## 示例：完成 Task 2.1

以 Task 2.1（Runner 集成测试）为例，展示完整流程：

### 1. 阅读任务要求

在 `docs/TEST_REBUILD_PLAN.md` 中找到 Task 2.1：

```
Task 2.1: 创建 Runner 集成测试
目标: runner.py 覆盖率 11% → 70%
文件: tests/integration/test_runner.py
要测试的场景: 10 个（见详细列表）
预计新增: ~52 个测试用例
```

### 2. 创建测试文件

```python
# tests/integration/test_runner.py
"""
ScriptRunner 集成测试

测试 runner.py 的完整执行流程
"""

import pytest
from pathlib import Path
from flowby.runner import ScriptRunner


class TestScriptRunner:
    """ScriptRunner 集成测试"""

    @pytest.fixture
    def runner(self, tmp_path):
        """创建测试用的 runner"""
        return ScriptRunner(output_dir=tmp_path)

    @pytest.fixture
    def simple_script(self, tmp_path):
        """创建简单测试脚本"""
        script_path = tmp_path / "test.flow"
        script_path.write_text('''
let x = 10
let y = 20
let result = x + y
log f"Result: {result}"
''')
        return script_path

    def test_run_simple_script_success(self, runner, simple_script):
        """✅ 运行简单脚本成功"""
        result = runner.run(simple_script)

        assert result.success is True
        assert result.exit_code == 0
        assert result.task_id is not None

    # ... 继续添加其他 51 个测试
```

### 3. 运行测试

```bash
pytest tests/integration/test_runner.py -v
```

输出应该类似：
```
tests/integration/test_runner.py::TestScriptRunner::test_run_simple_script_success PASSED
...
===================== 52 passed in 2.31s ======================
```

### 4. 检查覆盖率

```bash
pytest tests/integration/test_runner.py --cov=src/flowby/runner --cov-report=term
```

输出应该显示：
```
src/flowby/runner.py    206     61    70%
```

### 5. 质量检查

```bash
python scripts/quality_check.py tests/integration/test_runner.py
```

应该得到 80 分以上。

### 6. 更新进度

```bash
python scripts/task_tracker.py complete 2.1 59.0 52
```

### 7. 提交

```bash
git add tests/integration/test_runner.py
git commit -m "test: add runner integration tests

添加 ScriptRunner 集成测试，覆盖运行、错误处理、超时等场景

Coverage:
- runner.py: 11% → 72%

Tests added: 52
"
```

## 遇到问题怎么办？

### 测试失败

1. 查看详细错误：`pytest <test_file> -vvs`
2. 检查是否修改了业务代码（不应该）
3. 检查 fixture 是否正确
4. 对比计划文档中的示例

### 覆盖率不达标

1. 运行覆盖率报告：`pytest --cov-report=html`
2. 打开 `htmlcov/index.html` 查看未覆盖的代码
3. 添加测试覆盖缺失的分支

### 质量检查不通过

1. 查看具体失败的检查项
2. 运行 `black <file>` 修复格式
3. 运行 `flake8 <file>` 查看风格问题
4. 增加断言、文档、fixture

### 不确定如何编写

1. 查看 `tests/templates/` 中的模板
2. 参考现有的类似测试文件
3. 查看计划文档中的示例代码

## 进度跟踪

随时可以查看进度：

```bash
python scripts/task_tracker.py status
```

输出示例：
```
============================================================
测试重建进度
============================================================
任务进度: 3/18 (16.7%)
覆盖率:   62.5% / 80.0%
============================================================

阶段进度:

准备工作: 3/3
  ✅ 1.1: 创建单元测试模板 (+0.0%, 0 tests)
  ✅ 1.2: 创建集成测试模板 (+0.0%, 0 tests)
  ✅ 1.3: 创建验证脚本 (+0.0%, 0 tests)

补充集成测试: 0/4
  ⏳ 2.1: Runner 集成测试
  ⏳ 2.2: Response Handler 集成测试
  ⏳ 2.3: Resource Integration 测试
  ⏳ 2.4: Resilience 集成测试
...
```

## 提交规范

每个任务的提交消息格式：

```
test: <简短描述>

<详细说明>

Coverage:
- <module>.py: <before>% → <after>%

Tests added: <count>
```

示例：

```
test: add response handler integration tests

添加 ResponseHandler 集成测试，覆盖 JSON/HTML/XML 响应解析、
状态码处理、Cookie 处理等场景

Coverage:
- response_handler.py: 17% → 72%

Tests added: 40
```

## 最终目标

完成所有任务后，应达到：

- ✅ 总覆盖率 >= 80%
- ✅ 执行层覆盖率 >= 75%
- ✅ 集成层覆盖率 >= 70%
- ✅ 所有测试通过
- ✅ 代码质量优秀
- ✅ 测试结构清晰
- ✅ 文档完善

## 重要提醒

1. **不要着急**：质量比速度重要
2. **频繁验证**：每完成一个小功能就运行测试
3. **遵循模板**：使用提供的测试模板
4. **查看示例**：计划文档中有大量示例
5. **保持沟通**：遇到问题记录在提交消息中

---

**准备好了吗？开始 Task 1.1！**

查看详细说明：`docs/TEST_REBUILD_PLAN.md` 第 105 行
