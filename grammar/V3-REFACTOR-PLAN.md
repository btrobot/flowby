# DSL v3.0 Python风格重构计划

> **项目代号**: DSL-v3-Python-Style
> **开始日期**: 2025-11-26
> **目标**: 将DSL从混合语法（冒号+end）重构为纯Python风格（缩进）
> **破坏性变更**: 是（完全放弃v2.0兼容性）
> **预计工期**: 6-8周

---

## 🎯 核心目标

### 语法变更

**从 (v2.0 混合风格):**
```dsl
step "登录":
    if user == "admin":
        navigate to "https://admin.example.com"
    end if
end step
```

**到 (v3.0 纯Python风格):**
```dsl
step "登录":
    if user == "admin":
        navigate to "https://admin.example.com"
```

### 关键变更点
- ✅ 保留冒号 `:`（块开始标记）
- ✅ 使用4空格缩进（块层次）
- ❌ **删除** 所有 `end` 关键字（`end if`, `end step`, `end when`, `end for`）
- ✅ 严格缩进规则（类似Python）

---

## 📋 四阶段实施计划

### 阶段 0: 设计固化（1周）⭐ 当前阶段

**目标**: 完整定义v3.0语法，作为实施的唯一依据

#### 0.1 创建核心设计文档（2天）

**交付物**:
1. `grammar/DESIGN-V3.md` - v3.0完整语法规范
   - 语法设计原则
   - 与v2.0的完整对比表
   - 所有73个特性的v3.0语法示例
   - 缩进规则详细定义
   - 错误处理规范

2. `grammar/V3-EBNF.md` - v3.0 EBNF语法定义
   - 完整形式化语法
   - 缩进token定义
   - 块结构定义

3. `grammar/V3-EXAMPLES.dsl` - 完整示例集
   - 覆盖所有73个特性
   - 复杂嵌套场景
   - 边界情况

#### 0.2 设计评审（1天）

**检查清单**:
- [ ] 所有73个特性都有v3.0语法定义
- [ ] 缩进规则无歧义
- [ ] 错误消息格式清晰
- [ ] 示例代码可读性高
- [ ] 无语法冲突或歧义

#### 0.3 制定测试策略（2天）

**交付物**:
1. `tests/grammar_v3/TEST-PLAN.md` - 测试计划
   - 554个现有测试的改写策略
   - 新增测试清单（缩进边界、错误处理）
   - 测试覆盖率目标（100%）

2. `tests/grammar_v3/conftest.py` - 测试基础设施设计
   - parse_v3 fixture设计
   - 错误断言helper设计
   - AST比较工具设计

**成果标准**:
- ✅ 语法规范完整无歧义
- ✅ 所有团队成员理解v3.0设计
- ✅ 测试策略清晰可执行

---

### 阶段 1: 测试先行（2周）⭐ TDD核心

**目标**: 在实现前完成所有v3.0测试代码

#### 1.1 创建v3测试基础设施（2天）

**任务**:
```
tests/grammar_v3/
├── conftest.py              # parse_v3 fixture (使用未来的v3 parser)
├── test_00_indentation.py   # 纯缩进测试（新增）
└── README.md                # 测试说明
```

**conftest.py 设计**:
```python
@pytest.fixture
def parse_v3(request):
    """v3.0 parser fixture - 目前会失败，等待实现"""
    from registration_system.dsl.parser_v3 import ParserV3
    from registration_system.dsl.lexer_v3 import LexerV3

    def _parse(code: str):
        lexer = LexerV3(code)
        tokens = lexer.tokenize()
        parser = ParserV3(tokens)
        return parser.parse()

    return _parse
```

#### 1.2 编写缩进核心测试（3天）

**test_00_indentation.py** (预计150个测试):
- 基础缩进测试（30个）
  - 单层缩进、多层缩进、空行处理
- 缩进边界测试（40个）
  - 4空格标准、不一致缩进、缩进跳跃
- Tab处理测试（20个）
  - 纯Tab（8空格）、混合空格Tab（报错）
- 错误恢复测试（30个）
  - IndentationError消息格式
  - 错误位置标注
- 复杂嵌套测试（30个）
  - 5层嵌套、if-in-step-in-when

#### 1.3 改写现有554个测试（6天）

**策略**: 逐个测试文件改写

```
Day 1-2: 核心语法测试（170个测试）
├── test_01_variables.py (53个) → test_v3_01_variables.py
├── test_02_control_flow.py (33个) → test_v3_02_control_flow.py
├── test_03_navigation.py (32个) → test_v3_03_navigation.py
└── test_04_wait.py (34个) → test_v3_04_wait.py

Day 3-4: 动作与断言测试（120个测试）
├── test_05_selection.py (27个)
├── test_06_actions.py (44个)
├── test_07_assertions.py (33个)
└── test_08_service_call.py (25个)

Day 5-6: 高级特性测试（264个测试）
├── test_09_extraction.py (24个)
├── test_10_utilities.py (32个)
├── test_expressions.py (75个)
├── test_data_types.py (65个)
├── test_system_variables.py (38个)
└── test_builtin_functions.py (39个)
```

**改写规则**:
```python
# v2.0 测试
def test_if_else(parse):
    code = """
if x > 0:
    let y = 1
end if
"""
    ast = parse(code)
    # ...

# v3.0 测试（删除 end if）
def test_if_else_v3(parse_v3):
    code = """
if x > 0:
    let y = 1
"""
    ast = parse_v3(code)
    # AST断言保持不变
```

#### 1.4 新增v3特定测试（2天）

**新增测试清单**:
1. **缩进一致性测试**（20个）
   - 同级语句缩进必须相同
   - 跨块缩进检查

2. **空行处理测试**（15个）
   - 块内空行、块间空行
   - 空行不影响缩进

3. **注释与缩进测试**（10个）
   - 注释行缩进、行尾注释

4. **错误消息测试**（25个）
   - 每种IndentationError都有测试
   - 验证错误位置和提示文本

**成果标准**:
- ✅ 704个v3.0测试全部编写完成（554旧+150新）
- ✅ 所有测试目前标记为 `@pytest.mark.skip(reason="等待v3实现")`
- ✅ 测试代码覆盖所有73个语法特性

---

### 阶段 2: 词法分析器改造（1.5周）⭐ 技术核心

**目标**: 实现INDENT/DEDENT token生成

#### 2.1 创建LexerV3基础（2天）

**文件**: `src/registration_system/dsl/lexer_v3.py`

**核心数据结构**:
```python
class TokenType(Enum):
    # 新增缩进token
    INDENT = auto()
    DEDENT = auto()

    # 删除END token
    # END = auto()  # 移除

    # 保留其他所有token
    NEWLINE = auto()
    COLON = auto()
    # ...

class LexerV3:
    def __init__(self, source: str):
        self.source = source
        self.indent_stack = [0]  # 缩进栈
        self.pending_dedents = 0  # 待发出的DEDENT数量
        self.at_line_start = True  # 是否在行首
        self.tokens = []
```

#### 2.2 实现缩进栈算法（4天）

**关键方法**:

1. `_handle_indentation()` - 核心算法（~80行）
   - 计算当前行缩进量
   - 与栈顶比较
   - 生成INDENT或DEDENT token

2. `_generate_dedents_at_eof()` - EOF处理（~20行）
   - 文件结束时清空缩进栈

3. `_validate_indentation()` - 验证（~30行）
   - 检测不一致缩进
   - 检测混合空格Tab

**测试驱动开发**:
- 每完成一个方法，立即运行对应的`test_00_indentation.py`测试
- 目标：150个缩进测试全部通过

#### 2.3 集成测试与优化（1天）

**验证点**:
- [ ] 所有150个缩进测试通过
- [ ] 性能测试：1000行DSL代码词法分析 < 100ms
- [ ] 错误消息清晰友好

**成果标准**:
- ✅ LexerV3完全实现INDENT/DEDENT
- ✅ 通过所有缩进测试
- ✅ 错误处理健壮

---

### 阶段 3: 语法分析器改造（2周）⭐ 最大工作量

**目标**: 改造Parser支持INDENT/DEDENT，删除END token依赖

#### 3.1 创建ParserV3基础（2天）

**文件**: `src/registration_system/dsl/parser_v3.py`

**核心变更**:
```python
class ParserV3:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        # 不再需要END token相关逻辑

    def _parse_block(self) -> List[Statement]:
        """
        通用块解析（新方法）

        v2.0: 读取语句直到遇到END token
        v3.0: 读取语句直到遇到DEDENT token
        """
        self._consume(TokenType.INDENT, "期望缩进")
        statements = []

        while not self._check(TokenType.DEDENT):
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        self._consume(TokenType.DEDENT, "期望反缩进")
        return statements
```

#### 3.2 逐个改造块解析方法（8天）

**改造顺序**（由简单到复杂）:

**Day 1: Step块** (`_parse_step`)
- v2.0: `step "name": ... end step`
- v3.0: `step "name": <INDENT> ... <DEDENT>`
- 测试: `test_v3_02_control_flow.py::test_step_*` (9个)

**Day 2: If块** (`_parse_if`)
- v2.0: `if COND: ... end if`
- v3.0: `if COND: <INDENT> ... <DEDENT>`
- 难点: else-if链处理
- 测试: `test_v3_02_control_flow.py::test_if_*` (11个)

**Day 3: When块** (`_parse_when`)
- v2.0: `when VAR: "val": ... end when`
- v3.0: `when VAR: <INDENT> "val": ... <DEDENT>`
- 测试: `test_v3_02_control_flow.py::test_when_*` (8个)

**Day 4: ForEach块** (`_parse_for_each`)
- 如果v2.0已实现
- 测试: `test_v3_02_control_flow.py::test_for_*` (4个)

**Day 5-6: 嵌套块测试**
- 重点测试深度嵌套（5层+）
- If-in-step, when-in-if等组合
- 运行所有554个改写后的测试
- 目标: 通过率 > 90%

**Day 7-8: 错误处理与边界情况**
- 缺少INDENT的错误提示
- 缺少DEDENT的错误恢复
- 文件意外结束处理
- 目标: 通过所有704个测试

#### 3.3 删除END token残留（1天）

**清理检查清单**:
- [ ] TokenType.END 删除
- [ ] Lexer中END相关代码删除
- [ ] Parser中所有 `_consume(TokenType.END)` 删除
- [ ] 错误消息中"end"相关文本更新
- [ ] 搜索代码库确认无残留

**成果标准**:
- ✅ ParserV3完全基于INDENT/DEDENT
- ✅ 通过所有704个v3.0测试
- ✅ 无END token残留代码
- ✅ 错误消息清晰准确

---

### 阶段 4: 文档与验证（1周）

**目标**: 更新所有文档，全面验证系统

#### 4.1 更新语法文档（2天）

**文件更新清单**:
1. `grammar/MASTER.md`
   - 版本: v2.0 → v3.0
   - 所有语法示例更新为缩进风格
   - 删除所有 `end` 关键字引用

2. `grammar/V3-EBNF.md`
   - 添加INDENT/DEDENT token定义
   - 更新块结构EBNF

3. `README.md`
   - 更新快速开始示例
   - 更新语法介绍

4. `docs/syntax-guide.md`（如存在）
   - 完整语法指南重写

#### 4.2 生成新的覆盖率报告（1天）

**运行工具**:
```bash
# 使用现有的覆盖率验证工具
python grammar/verify_grammar_coverage.py --output COVERAGE-REPORT-V3.md
```

**预期结果**:
- 总特性: 73
- 覆盖特性: 73
- 覆盖率: 100%
- 测试总数: 704

#### 4.3 性能基准测试（1天）

**基准测试**:
```python
# tests/performance/test_v3_benchmarks.py

def test_lexer_performance():
    """词法分析性能: 1000行DSL < 100ms"""
    code = generate_large_dsl(lines=1000)
    start = time.time()
    lexer = LexerV3(code)
    tokens = lexer.tokenize()
    duration = time.time() - start
    assert duration < 0.1  # 100ms

def test_parser_performance():
    """语法分析性能: 1000行DSL < 500ms"""
    # ...
```

#### 4.4 最终验证（1天）

**验证检查清单**:
- [ ] 所有704个测试通过（100%）
- [ ] 覆盖率报告100%
- [ ] 性能基准达标
- [ ] 文档示例代码全部可运行
- [ ] 无TODO或FIXME注释残留
- [ ] 代码审查通过

**成果标准**:
- ✅ 文档完整准确
- ✅ 100%测试覆盖
- ✅ 性能达标
- ✅ 系统可发布

---

## 📊 工作量估算

| 阶段 | 主要任务 | 预计工作量 | 难度 |
|------|---------|-----------|------|
| 阶段0: 设计固化 | 编写规范文档 | 1周 (40h) | ⭐⭐⭐ |
| 阶段1: 测试先行 | 704个测试编写 | 2周 (80h) | ⭐⭐⭐⭐ |
| 阶段2: Lexer改造 | 缩进栈算法 | 1.5周 (60h) | ⭐⭐⭐⭐⭐ |
| 阶段3: Parser改造 | 块解析重构 | 2周 (80h) | ⭐⭐⭐⭐⭐ |
| 阶段4: 文档验证 | 文档+测试 | 1周 (40h) | ⭐⭐⭐ |
| **总计** | | **7.5周 (300h)** | |

**风险缓冲**: +0.5周 → **总计8周**

---

## 📈 里程碑

| 里程碑 | 完成标志 | 预计日期 |
|--------|---------|---------|
| M0: 设计完成 | ✅ DESIGN-V3.md通过评审 | Week 1 |
| M1: 测试就绪 | ✅ 704个v3测试编写完成 | Week 3 |
| M2: Lexer完成 | ✅ 150个缩进测试通过 | Week 4.5 |
| M3: Parser完成 | ✅ 704个测试全部通过 | Week 6.5 |
| M4: v3.0发布 | ✅ 文档+验证完成 | Week 8 |

---

## 🎯 成功标准

### 技术标准
- ✅ 零END token残留
- ✅ 704个测试100%通过
- ✅ 73个特性100%覆盖
- ✅ 缩进严格遵循Python规则（4空格）
- ✅ 错误消息清晰（IndentationError格式化）
- ✅ 性能不低于v2.0

### 代码质量标准
- ✅ Lexer代码 < 1000行
- ✅ Parser代码 < 2000行
- ✅ 测试代码行数 > 实现代码行数
- ✅ 无TODO/FIXME残留

### 文档标准
- ✅ MASTER.md完整更新到v3.0
- ✅ 所有示例代码可运行
- ✅ EBNF语法形式化完整

---

## 🚀 下一步行动

### 立即执行（本周）
1. ✅ 创建本计划文档 `V3-REFACTOR-PLAN.md`
2. ⏭️ 创建 `grammar/DESIGN-V3.md`（阶段0核心交付物）
3. ⏭️ 创建 `grammar/V3-EBNF.md`
4. ⏭️ 创建 `grammar/V3-EXAMPLES.dsl`
5. ⏭️ 创建 `tests/grammar_v3/TEST-PLAN.md`

### 本周目标
- 完成阶段0的所有交付物
- 设计评审通过
- 为阶段1做好准备

---

## 📝 变更日志

### 2025-11-26
- 创建v3.0重构计划
- 确定4阶段实施策略
- 明确不考虑v2.0兼容性

---

**项目负责人**: [待定]
**技术评审**: [待定]
**预计完成**: 2025-01-21 (8周后)
