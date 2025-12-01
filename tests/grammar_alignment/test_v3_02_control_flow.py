"""
Grammar Alignment Test: v3.0 控制流（无end关键字）

⭐ v3.0 核心变更：所有控制流块使用纯缩进，删除 end 关键字

测试核心原则：
1. 正确的代码（无end）正确解析
2. 错误的代码（有end）报错一致

Features tested:
- 2.1 Step Block (v3.0: 无 end step)
- 2.2 If-Else (v3.0: 无 end if)
- 2.3 When-Otherwise (v3.0: 无 end when)
- 2.4 For-Each Loop (v3.0: 无 end for)

Reference: grammar/DESIGN-V3.md #2, grammar/V3-EBNF.md
"""

import pytest
from registration_system.dsl.ast_nodes import Program
from registration_system.dsl.interpreter import Interpreter
from registration_system.dsl.context import ExecutionContext


# ============================================================================
# 2.1 Step Block 测试（无 end step）
# ============================================================================


class TestV3_2_1_StepBlock:
    """Step 块测试（纯缩进，无 end step）"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.1")
    def test_step_basic(self, parse_v3):
        """✅ 正确：基本 step 块（无 end step）"""
        source = """
step "test":
    let x = 1
"""
        result = parse_v3(source)
        assert result.success == True, "基本 step 块应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.1")
    def test_step_multiple_statements(self, parse_v3):
        """✅ 正确：step 块包含多个语句"""
        source = """
step "登录流程":
    let email = "test@example.com"
    let password = "secret"
    log f"开始登录: {email}"
"""
        result = parse_v3(source)
        assert result.success == True, "step 块内多个语句应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.1")
    def test_step_with_nested_if(self, parse_v3):
        """✅ 正确：step 块内嵌套 if"""
        source = """
step "检查状态":
    if status == "active":
        log "用户活跃"
    else:
        log "用户未激活"
"""
        result = parse_v3(source)
        assert result.success == True, "step 块内嵌套 if 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.1")
    def test_step_with_diagnosis(self, parse_v3):
        """✅ 正确：step 块带 diagnosis 选项"""
        source = """
step "测试" with diagnosis detailed:
    let x = 1
"""
        result = parse_v3(source)
        assert result.success == True, "step 块的 diagnosis 选项应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.1")
    def test_nested_step_blocks(self, parse_v3):
        """✅ 正确：嵌套 step 块"""
        source = """
step "外层步骤":
    step "内层步骤":
        let x = 1
    let y = 2
"""
        result = parse_v3(source)
        assert result.success == True, "嵌套 step 块应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.1")
    def test_consecutive_steps(self, parse_v3):
        """✅ 正确：连续的 step 块"""
        source = """
step "步骤1":
    let x = 1

step "步骤2":
    let y = 2

step "步骤3":
    let z = 3
"""
        result = parse_v3(source)
        assert result.success == True, "连续的 step 块应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.1")
    def test_step_with_end_keyword_error(self, parse_v3):
        """❌ 错误：step 块使用 end step 应报错"""
        source = """
step "test":
    let x = 1
end step
"""
        result = parse_v3(source)
        assert result.success == False, "使用 end step 应该报错"
        assert (
            "end" in result.error.lower() or "缩进" in result.error
        ), "错误提示应提及 end 关键字或缩进"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.1")
    def test_step_empty_block_error(self, parse_v3):
        """❌ 错误：空 step 块应报错"""
        source = """
step "test":
"""
        result = parse_v3(source)
        assert result.success == False, "空 step 块应该报错"
        assert (
            "块" in result.error or "body" in result.error.lower() or "语句" in result.error
        ), "错误提示应提及空块"


# ============================================================================
# 2.2 If-Else 测试（无 end if）
# ============================================================================


class TestV3_2_2_IfElse:
    """If-Else 块测试（纯缩进，无 end if）"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.2")
    def test_if_basic(self, parse_v3):
        """✅ 正确：基本 if 语句（无 end if）"""
        source = """
if x > 0:
    let y = 1
"""
        result = parse_v3(source)
        assert result.success == True, "基本 if 语句应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.2")
    def test_if_else(self, parse_v3):
        """✅ 正确：if-else 语句"""
        source = """
if x > 0:
    let y = 1
else:
    let y = 0
"""
        result = parse_v3(source)
        assert result.success == True, "if-else 语句应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.2")
    def test_if_else_if(self, parse_v3):
        """✅ 正确：if-else if 链"""
        source = """
if score > 90:
    let grade = "A"
else if score > 80:
    let grade = "B"
else if score > 70:
    let grade = "C"
else:
    let grade = "F"
"""
        result = parse_v3(source)
        assert result.success == True, "if-else if 链应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.2")
    @pytest.mark.python_aligned
    def test_if_with_python_bool(self, parse_v3):
        """✅ 正确：if 条件使用 Python 布尔值"""
        source = """
if active == True:
    log "激活"
else:
    log "未激活"
"""
        result = parse_v3(source)
        assert result.success == True, "if 条件使用 True/False 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.2")
    @pytest.mark.python_aligned
    def test_if_with_none_check(self, parse_v3):
        """✅ 正确：if 条件检查 None"""
        source = """
if data == None:
    log "数据为空"
else:
    log "数据存在"
"""
        result = parse_v3(source)
        assert result.success == True, "if 条件检查 None 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.2")
    def test_nested_if(self, parse_v3):
        """✅ 正确：嵌套 if 语句"""
        source = """
if x > 0:
    if y > 0:
        let z = 1
    else:
        let z = 2
else:
    let z = 3
"""
        result = parse_v3(source)
        assert result.success == True, "嵌套 if 语句应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.2")
    def test_if_with_complex_condition(self, parse_v3):
        """✅ 正确：if 复杂条件"""
        source = """
if x > 0 and y < 10 or z == 5:
    let result = True
"""
        result = parse_v3(source)
        assert result.success == True, "if 复杂条件应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.2")
    def test_if_with_end_keyword_error(self, parse_v3):
        """❌ 错误：if 语句使用 end if 应报错"""
        source = """
if x > 0:
    let y = 1
end if
"""
        result = parse_v3(source)
        assert result.success == False, "使用 end if 应该报错"
        assert "end" in result.error.lower() or "缩进" in result.error, "错误提示应提及 end 关键字"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.2")
    def test_if_missing_colon_error(self, parse_v3):
        """❌ 错误：if 缺少冒号"""
        source = """
if x > 0
    let y = 1
"""
        result = parse_v3(source)
        assert result.success == False, "if 缺少冒号应该报错"
        assert ":" in result.error or "冒号" in result.error, "错误提示应提及冒号"


# ============================================================================
# 2.3 When-Otherwise 测试（无 end when）
# ============================================================================


class TestV3_2_3_WhenOtherwise:
    """When-Otherwise 块测试（纯缩进，无 end when）"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.3")
    def test_when_basic(self, parse_v3):
        """✅ 正确：基本 when 语句（无 end when）"""
        source = """
when status:
    "active":
        let x = 1
    "inactive":
        let x = 2
"""
        result = parse_v3(source)
        assert result.success == True, "基本 when 语句应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.3")
    def test_when_with_otherwise(self, parse_v3):
        """✅ 正确：when 带 otherwise 分支"""
        source = """
when status:
    "pending":
        let x = 1
    "processing":
        let x = 2
    otherwise:
        let x = 3
"""
        result = parse_v3(source)
        assert result.success == True, "when 带 otherwise 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.3")
    def test_when_multiple_cases(self, parse_v3):
        """✅ 正确：when 多个分支"""
        source = """
when code:
    "200":
        log "成功"
    "404":
        log "未找到"
    "500":
        log "服务器错误"
    otherwise:
        log "未知状态"
"""
        result = parse_v3(source)
        assert result.success == True, "when 多个分支应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.3")
    def test_when_nested_statements(self, parse_v3):
        """✅ 正确：when 分支内嵌套语句"""
        source = """
when status:
    "active":
        if score > 90:
            log "优秀活跃用户"
        else:
            log "普通活跃用户"
    otherwise:
        log "非活跃用户"
"""
        result = parse_v3(source)
        assert result.success == True, "when 分支内嵌套语句应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.3")
    def test_when_with_end_keyword_error(self, parse_v3):
        """❌ 错误：when 语句使用 end when 应报错"""
        source = """
when status:
    "active":
        let x = 1
end when
"""
        result = parse_v3(source)
        assert result.success == False, "使用 end when 应该报错"
        assert "end" in result.error.lower() or "缩进" in result.error, "错误提示应提及 end 关键字"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.3")
    def test_when_missing_colon_error(self, parse_v3):
        """❌ 错误：when 缺少冒号"""
        source = """
when status
    "active":
        let x = 1
"""
        result = parse_v3(source)
        assert result.success == False, "when 缺少冒号应该报错"

    # === v3.1 OR 模式测试 ===

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.3")
    @pytest.mark.v31
    def test_when_or_pattern_basic(self, parse_v3):
        """✅ 正确：基本 OR 模式（v3.1）"""
        source = """
when status:
    "active" | "verified":
        log "Access granted"
    "inactive" | "suspended":
        log "Access denied"
"""
        result = parse_v3(source)
        assert result.success == True, "OR 模式应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.3")
    @pytest.mark.v31
    def test_when_or_pattern_numbers(self, parse_v3):
        """✅ 正确：数字 OR 模式（v3.1）"""
        source = """
when http_status:
    200 | 201 | 204:
        log "Success"
    400 | 401 | 403:
        log "Client error"
    500 | 502 | 503:
        log "Server error"
"""
        result = parse_v3(source)
        assert result.success == True, "数字 OR 模式应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.3")
    @pytest.mark.v31
    def test_when_or_pattern_mixed(self, parse_v3):
        """✅ 正确：混合 OR 模式和单值（v3.1）"""
        source = """
when user_role:
    "admin" | "moderator":
        access_level = "high"
    "user":
        access_level = "normal"
    otherwise:
        access_level = "guest"
"""
        result = parse_v3(source)
        assert result.success == True, "混合 OR 模式应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.3")
    @pytest.mark.v31
    def test_when_or_pattern_three_values(self, parse_v3):
        """✅ 正确：三个值的 OR 模式（v3.1）"""
        source = """
when priority:
    1 | 2 | 3:
        log "High priority"
    4 | 5 | 6:
        log "Medium priority"
    7 | 8 | 9:
        log "Low priority"
"""
        result = parse_v3(source)
        assert result.success == True, "三值 OR 模式应该正确解析"


# ============================================================================
# 2.4 For-Each Loop 测试（无 end for）
# ============================================================================


class TestV3_2_4_ForEachLoop:
    """For-Each 循环测试（纯缩进，无 end for）"""

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.4")
    def test_for_basic(self, parse_v3):
        """✅ 正确：基本 for 循环（无 end for）"""
        source = """
for item in items:
    log f"Item: {item}"
"""
        result = parse_v3(source)
        assert result.success == True, "基本 for 循环应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.4")
    def test_for_multiple_statements(self, parse_v3):
        """✅ 正确：for 循环包含多个语句"""
        source = """
for user in users:
    log f"用户: {user.name}"
    let email = user.email
    log f"邮箱: {email}"
"""
        result = parse_v3(source)
        assert result.success == True, "for 循环内多个语句应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.4")
    def test_for_with_nested_if(self, parse_v3):
        """✅ 正确：for 循环内嵌套 if"""
        source = """
for item in items:
    if item > 0:
        log f"正数: {item}"
    else:
        log f"非正数: {item}"
"""
        result = parse_v3(source)
        assert result.success == True, "for 循环内嵌套 if 应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.4")
    def test_nested_for_loops(self, parse_v3):
        """✅ 正确：嵌套 for 循环"""
        source = """
for row in matrix:
    for col in row:
        log f"值: {col}"
"""
        result = parse_v3(source)
        assert result.success == True, "嵌套 for 循环应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.4")
    @pytest.mark.python_aligned
    def test_for_looks_like_python(self, parse_v3):
        """✅ 验证：for 循环看起来像 Python"""
        source = """
for user in users:
    if user.active == True:
        log f"Active: {user.name}"
"""
        # 这段代码应该让 Python 程序员感觉很熟悉
        result = parse_v3(source)
        assert result.success == True, "for 循环应该像 Python 一样"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.4")
    def test_for_with_end_keyword_error(self, parse_v3):
        """❌ 错误：for 循环使用 end for 应报错"""
        source = """
for item in items:
    log item
end for
"""
        result = parse_v3(source)
        assert result.success == False, "使用 end for 应该报错"
        assert "end" in result.error.lower() or "缩进" in result.error, "错误提示应提及 end 关键字"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.feature("2.4")
    def test_for_missing_colon_error(self, parse_v3):
        """❌ 错误：for 缺少冒号"""
        source = """
for item in items
    log item
"""
        result = parse_v3(source)
        assert result.success == False, "for 缺少冒号应该报错"


# ============================================================================
# 综合测试：控制流组合
# ============================================================================


class TestV3_ControlFlow_Complex:
    """控制流复杂组合测试"""

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_all_control_structures_combined(self, parse_v3):
        """✅ 正确：所有控制结构组合"""
        source = """
step "复杂流程":
    let items = [1, 2, 3]

    for item in items:
        if item > 1:
            when item:
                "2":
                    log "二"
                "3":
                    log "三"
                otherwise:
                    log "其他"
        else:
            log "一"
"""
        result = parse_v3(source)
        assert result.success == True, "所有控制结构组合应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    @pytest.mark.python_aligned
    def test_python_style_control_flow(self, parse_v3):
        """✅ 验证：Python 风格的控制流"""
        source = """
step "用户验证":
    if user == None:
        log "用户不存在"
    else:
        if user.active == True:
            for role in user.roles:
                when role:
                    "admin":
                        log "管理员权限"
                    "user":
                        log "普通用户权限"
                    otherwise:
                        log "未知角色"
        else:
            log "用户未激活"
"""
        result = parse_v3(source)
        assert result.success == True, "Python 风格的控制流应该正确解析"

    @pytest.mark.v3
    @pytest.mark.syntax
    def test_deep_nesting(self, parse_v3):
        """✅ 正确：深层嵌套（5层）"""
        source = """
step "level1":
    for a in list1:
        if a > 0:
            when a:
                "1":
                    for b in list2:
                        if b > 0:
                            log "深层嵌套"
"""
        result = parse_v3(source)
        assert result.success == True, "深层嵌套应该正确解析"


# ============================================================================
# Python 对齐验证
# ============================================================================


class TestV3_ControlFlow_PythonAlignment:
    """控制流 Python 对齐验证"""

    @pytest.mark.v3
    @pytest.mark.python_aligned
    @pytest.mark.parametrize(
        "dsl_code,python_equiv",
        [
            ("if x > 0:\n    let y = 1", "if x > 0:\n    y = 1"),
            ("for item in items:\n    log item", "for item in items:\n    print(item)"),
            ("if x:\n    let a = 1\nelse:\n    let a = 2", "if x:\n    a = 1\nelse:\n    a = 2"),
        ],
    )
    def test_structure_matches_python(self, parse_v3, dsl_code, python_equiv):
        """✅ 验证：结构与 Python 匹配"""
        # DSL 代码应该能解析
        result = parse_v3(dsl_code)
        assert result.success == True, f"DSL 代码应该像 Python 一样解析：{dsl_code}"

    @pytest.mark.v3
    @pytest.mark.python_aligned
    def test_no_end_keyword_like_python(self, parse_v3):
        """✅ 验证：像 Python 一样没有 end 关键字"""
        # Python 程序员的直觉写法
        source = """
for user in users:
    if user.active:
        log f"Active user: {user.name}"
"""
        result = parse_v3(source)
        assert result.success == True, "Python 程序员的直觉写法应该能正确解析"


# ============================================================================
# 测试总结
# ============================================================================

"""
测试覆盖清单：

2.1 Step Block:
✅ 基本 step 块（无 end step）
✅ 多个语句
✅ 嵌套 if
✅ diagnosis 选项
✅ 嵌套 step
✅ 连续 step
✅ end step 报错
✅ 空块报错

2.2 If-Else:
✅ 基本 if（无 end if）
✅ if-else
✅ if-else if 链
✅ Python 布尔值
✅ None 检查
✅ 嵌套 if
✅ 复杂条件
✅ end if 报错
✅ 缺少冒号报错

2.3 When-Otherwise:
✅ 基本 when（无 end when）
✅ otherwise 分支
✅ 多个分支
✅ 嵌套语句
✅ end when 报错
✅ 缺少冒号报错

2.4 For-Each Loop:
✅ 基本 for（无 end for）
✅ 多个语句
✅ 嵌套 if
✅ 嵌套 for
✅ Python 风格
✅ end for 报错
✅ 缺少冒号报错

综合测试：
✅ 所有控制结构组合
✅ Python 风格验证
✅ 深层嵌套
✅ 结构与 Python 匹配

总计：约 55 个控制流测试
"""


# ============================================================================
# v4.0 enumerate() 和多变量循环测试
# ============================================================================


class TestV4_Enumerate:
    """v4.0: enumerate() 函数和多变量循环测试"""

    @staticmethod
    def _make_program(statements):
        """辅助函数：将语句列表包装为 Program 对象"""
        if isinstance(statements, Program):
            return statements
        return Program(statements=statements, line=1)

    @pytest.mark.v40
    @pytest.mark.syntax
    def test_enumerate_basic(self, parse_v3):
        """✅ 正确：基本 enumerate 用法"""
        source = """
let items = ["a", "b", "c"]
for index, item in enumerate(items):
    log f"{index}: {item}"
"""
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v40
    @pytest.mark.syntax
    def test_enumerate_with_start(self, parse_v3):
        """✅ 正确：enumerate 使用 start 参数"""
        source = """
let items = ["a", "b", "c"]
for index, item in enumerate(items, start=1):
    log f"{index}: {item}"
"""
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v40
    @pytest.mark.syntax
    def test_multi_var_loop_basic(self, parse_v3):
        """✅ 正确：基本多变量循环"""
        source = """
let pairs = [[1, "a"], [2, "b"], [3, "c"]]
for key, value in pairs:
    log f"{key} = {value}"
"""
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v40
    @pytest.mark.syntax
    def test_multi_var_three_vars(self, parse_v3):
        """✅ 正确：三变量循环"""
        source = """
let triplets = [[1, 2, 3], [4, 5, 6]]
for a, b, c in triplets:
    log f"{a}, {b}, {c}"
"""
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v40
    @pytest.mark.syntax
    def test_enumerate_nested(self, parse_v3):
        """✅ 正确：嵌套 enumerate 循环"""
        source = """
let matrix = [["a", "b"], ["c", "d"]]
for i, row in enumerate(matrix):
    for j, item in enumerate(row):
        log f"[{i},{j}] = {item}"
"""
        result = parse_v3(source)
        assert result.success == True

    @pytest.mark.v40
    @pytest.mark.execution
    def test_enumerate_execution(self, parse):
        """✅ 执行：enumerate 返回正确的索引和值"""
        code = """
let items = ["apple", "banana", "cherry"]
let result = []
for index, item in enumerate(items):
    result = result + [[index, item]]
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        result = interpreter.symbol_table.get("result", [])
        assert result == [[0, "apple"], [1, "banana"], [2, "cherry"]]

    @pytest.mark.v40
    @pytest.mark.execution
    def test_enumerate_start_execution(self, parse):
        """✅ 执行：enumerate start 参数工作正常"""
        code = """
let items = ["apple", "banana", "cherry"]
let result = []
for index, item in enumerate(items, start=1):
    result = result + [[index, item]]
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        result = interpreter.symbol_table.get("result", [])
        assert result == [[1, "apple"], [2, "banana"], [3, "cherry"]]

    @pytest.mark.v40
    @pytest.mark.execution
    def test_multi_var_execution(self, parse):
        """✅ 执行：多变量循环正确解包"""
        code = """
let pairs = [[1, "a"], [2, "b"], [3, "c"]]
let keys = []
let values = []
for key, value in pairs:
    keys = keys + [key]
    values = values + [value]
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        keys = interpreter.symbol_table.get("keys", [])
        values = interpreter.symbol_table.get("values", [])
        assert keys == [1, 2, 3]
        assert values == ["a", "b", "c"]

    @pytest.mark.v40
    @pytest.mark.execution
    def test_enumerate_with_break(self, parse):
        """✅ 执行：enumerate 循环支持 break"""
        code = """
let items = ["a", "b", "c", "d"]
let result = []
for index, item in enumerate(items):
    if index == 2:
        break
    result = result + [item]
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        result = interpreter.symbol_table.get("result", [])
        assert result == ["a", "b"]

    @pytest.mark.v40
    @pytest.mark.execution
    def test_enumerate_with_continue(self, parse):
        """✅ 执行：enumerate 循环支持 continue"""
        code = """
let items = ["a", "b", "c", "d"]
let result = []
for index, item in enumerate(items):
    if index == 1:
        continue
    result = result + [item]
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        result = interpreter.symbol_table.get("result", [])
        assert result == ["a", "c", "d"]

    @pytest.mark.v40
    @pytest.mark.error
    def test_unpack_count_mismatch_error(self, parse):
        """❌ 错误：解包数量不匹配"""
        code = """
let pairs = [[1, "a"], [2, "b", "extra"]]
for key, value in pairs:
    log key
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)

        with pytest.raises(Exception, match="解包值数量不匹配"):
            interpreter.execute(program)

    @pytest.mark.v40
    @pytest.mark.error
    def test_unpack_non_iterable_error(self, parse):
        """❌ 错误：无法解包非可迭代类型"""
        code = """
let items = [1, 2, 3]
for key, value in items:
    log key
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)

        with pytest.raises(Exception, match="无法解包类型"):
            interpreter.execute(program)

    @pytest.mark.v40
    @pytest.mark.execution
    def test_backward_compatible_single_var(self, parse):
        """✅ 向后兼容：单变量循环仍然工作"""
        code = """
let items = [1, 2, 3]
let result = []
for item in items:
    result = result + [item]
"""
        ast = parse(code)
        program = self._make_program(ast)
        context = ExecutionContext("test-task")
        interpreter = Interpreter(context)
        interpreter.execute(program)

        result = interpreter.symbol_table.get("result", [])
        assert result == [1, 2, 3]
