"""
AST (Abstract Syntax Tree) 节点定义

定义了 DSL 的抽象语法树节点类型。每个节点代表 DSL 中的一种语法结构。

节点层次:
    ASTNode (基类)
    ├── Program (程序根节点)
    ├── Statement (语句基类)
    │   ├── NavigationStatement (导航语句)
    │   │   ├── NavigateToStatement
    │   │   ├── GoBackStatement
    │   │   ├── GoForwardStatement
    │   │   └── ReloadStatement
    │   ├── WaitStatement (等待语句)
    │   │   ├── WaitDurationStatement
    │   │   ├── WaitForStateStatement
    │   │   ├── WaitForElementStatement
    │   │   ├── WaitForNavigationStatement
    │   │   └── WaitUntilStatement
    │   ├── SelectStatement (选择语句)
    │   ├── ActionStatement (动作语句)
    │   │   ├── TypeAction
    │   │   ├── ClickAction
    │   │   ├── HoverAction
    │   │   ├── ClearAction
    │   │   ├── PressAction
    │   │   ├── ScrollAction
    │   │   ├── SelectOptionAction
    │   │   ├── CheckAction
    │   │   └── UploadAction
    │   ├── AssertStatement (断言语句)
    │   ├── ScreenshotStatement (截图语句)
    │   ├── StepBlock (步骤块)
    │   └── ConditionalBlock (条件块)
    │       ├── IfBlock
    │       └── WhenBlock
    └── Condition (条件表达式)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any
from enum import Enum


# ============================================================
# 基础节点
# ============================================================

@dataclass
class ASTNode:
    """
    AST 节点基类

    所有 AST 节点的基类，包含行号信息用于错误报告

    Attributes:
        line: 节点在源文件中的行号（从 1 开始）
    """
    line: int

    def to_dict(self) -> dict:
        """
        序列化为字典格式，用于自省测试

        递归处理所有字段，将 AST 节点转换为嵌套字典结构

        Returns:
            字典格式的节点表示
        """
        from dataclasses import fields
        from typing import List

        result = {'type': self.__class__.__name__, 'line': self.line}

        for field in fields(self):
            value = getattr(self, field.name)

            # 跳过 None 值，使输出更简洁
            if value is None:
                continue

            # 如果是 AST 节点，递归序列化
            if isinstance(value, ASTNode):
                result[field.name] = value.to_dict()
            # 如果是 AST 节点列表，递归序列化每个元素
            elif isinstance(value, list):
                result[field.name] = [
                    item.to_dict() if isinstance(item, ASTNode) else item
                    for item in value
                ]
            # 如果是元组列表（如 elif_clauses），特殊处理
            elif isinstance(value, tuple):
                # 用于 elif_clauses: (condition, statements)
                serialized = []
                for item in value:
                    if isinstance(item, list):
                        # statements list
                        serialized.append([i.to_dict() if isinstance(i, ASTNode) else i for i in item])
                    elif isinstance(item, ASTNode):
                        serialized.append(item.to_dict())
                    else:
                        serialized.append(item)
                result[field.name] = serialized
            else:
                # 普通值直接添加
                result[field.name] = value

        return result


# ============================================================
# 程序根节点
# ============================================================

@dataclass
class Program(ASTNode):
    """
    程序根节点

    代表整个 .flow 文件

    Attributes:
        statements: 顶层语句列表
    """
    statements: List[ASTNode] = field(default_factory=list)


# ============================================================
# 导航语句
# ============================================================

@dataclass
class NavigateToStatement(ASTNode):
    """
    导航到 URL 语句

    语法: navigate to "url"

    Attributes:
        url: 目标 URL（可能包含变量引用）
    """
    url: str


@dataclass
class GoBackStatement(ASTNode):
    """
    返回上一页语句

    语法: go back
    """
    pass


@dataclass
class GoForwardStatement(ASTNode):
    """
    前进到下一页语句

    语法: go forward
    """
    pass


@dataclass
class ReloadStatement(ASTNode):
    """
    刷新页面语句

    语法: reload
    """
    pass


# ============================================================
# 等待语句
# ============================================================

@dataclass
class WaitDurationStatement(ASTNode):
    """
    等待固定时间语句 (v6.0.2: 支持数值表达式)

    语法:
        wait 3s / wait 500ms              # 字面量
        wait delay_time s                 # 变量
        wait (retry * 2) s                # 表达式

    Attributes:
        duration: 时间值（可以是 float 或 Expression）
            - 如果是 float: 已转换为秒的字面量
            - 如果是 Expression: 需要在运行时求值
        unit: 时间单位字符串（s, ms等），仅在 duration 为 Expression 时使用
    """
    duration: Any  # float (字面量) 或 Expression (表达式)
    unit: Optional[str] = None  # v6.0.2: 时间单位（仅表达式需要）


@dataclass
class WaitForStateStatement(ASTNode):
    """
    等待页面状态语句

    语法: wait for networkidle / wait for load

    Attributes:
        state: 页面状态（networkidle, domcontentloaded, load）
    """
    state: str


@dataclass
class WaitForElementStatement(ASTNode):
    """
    等待元素出现语句

    语法: wait for element "selector"
          wait for element "selector" to be visible
          wait for element "selector" to be visible timeout 10s

    Attributes:
        selector: CSS/XPath 选择器（字符串或表达式）
        state: 元素状态（visible, hidden, attached, detached, None）
        timeout: 超时时间（秒，可选）
    """
    selector: Any  # str 或 Expression
    state: Optional[str] = None
    timeout: Optional[float] = None


@dataclass
class WaitForNavigationStatement(ASTNode):
    """
    等待导航完成语句

    语法: wait for navigation
          wait for navigation to "url"
          wait for navigation wait for networkidle
          wait for navigation timeout 10s

    Attributes:
        url: 目标 URL（可选，字符串或表达式）
        page_state: 页面状态（networkidle, load, domcontentloaded, None）
        timeout: 超时时间（秒，可选）
    """
    url: Optional[Any] = None
    page_state: Optional[str] = None
    timeout: Optional[float] = None


@dataclass
class WaitUntilStatement(ASTNode):
    """
    等待条件满足语句

    语法: wait until url contains "text"

    Attributes:
        condition: 条件表达式
    """
    condition: 'Condition'


# ============================================================
# 选择语句
# ============================================================

@dataclass
class SelectStatement(ASTNode):
    """
    选择元素语句

    语法: select input where name="email"
          select button where text contains "Submit"

    Attributes:
        element_type: 元素类型（input, button, element, etc.）
        conditions: 属性条件列表 [(attribute, operator, value), ...]
                   operator 可以是: "=", "contains", "equals", "matches"
    """
    element_type: str
    conditions: List[tuple[str, str, str]] = field(default_factory=list)


# ============================================================
# 动作语句
# ============================================================

@dataclass
class TypeAction(ASTNode):
    """
    输入文本动作 (v3.0 - 支持 into 选择器)

    语法: type expression [into selector] [slowly|fast]

    示例:
        type "literal string"              # 字符串字面量
        type email                         # 变量引用
        type user.email                    # 成员访问
        type "Hello {user.name}"           # 字符串插值
        type "text" into "#selector"       # v3.0: 指定选择器
        type slowly password               # 带模式的变量引用

    Attributes:
        text: 要输入的文本表达式（Expression,运行时求值后转为字符串）
        selector: 目标选择器（可选，None 表示使用当前选中元素）
        mode: 输入模式（slowly, fast, None）
    """
    text: Any  # Expression - 运行时求值
    selector: Optional[Any] = None  # str 或 Expression
    mode: Optional[str] = None


@dataclass
class ClickAction(ASTNode):
    """
    点击动作

    语法: click [selector]
          click and wait 3s
          double_click [selector]
          right_click [selector]

    Attributes:
        click_type: 点击类型（click, double_click, right_click）
        selector: 选择器（可选，None 表示点击当前选中元素）
        wait_duration: 点击后等待时间（秒，可选）
    """
    click_type: str = "click"
    selector: Optional[Any] = None
    wait_duration: Optional[float] = None


@dataclass
class HoverAction(ASTNode):
    """
    悬停动作

    语法: hover
          hover over "selector"

    Attributes:
        selector: 选择器（可选，None 表示悬停在当前选中元素）
    """
    selector: Optional[str] = None


@dataclass
class ClearAction(ASTNode):
    """
    清空输入动作 (v3.0: 支持可选选择器)

    语法:
        clear                # 清空当前焦点元素
        clear "#search"      # 清空指定元素

    Attributes:
        selector: 元素选择器（可选）
    """
    selector: Optional[Any] = None  # str 或 Expression


@dataclass
class PressAction(ASTNode):
    """
    按键动作

    语法: press Enter / press Tab

    Attributes:
        key_name: 按键名称
    """
    key_name: str


@dataclass
class ScrollAction(ASTNode):
    """
    滚动动作

    语法: scroll to top
          scroll to bottom
          scroll to element "selector"

    Attributes:
        target: 滚动目标（top, bottom, element）
        selector: 元素选择器（当 target 为 element 时）
    """
    target: str
    selector: Optional[str] = None


@dataclass
class SelectOptionAction(ASTNode):
    """
    选择下拉框选项动作

    语法: select option "value" from "selector"
          select option option_var from selector_var  # v2.0 支持表达式

    Attributes:
        option_value: 选项值（字符串或表达式）
        selector: 下拉框选择器（字符串或表达式）
    """
    option_value: Any  # str 或 Expression
    selector: Any  # str 或 Expression


@dataclass
class CheckAction(ASTNode):
    """
    复选框操作动作

    语法: check "selector"
          uncheck "selector"

    Attributes:
        action: 操作类型（check, uncheck）
        selector: 复选框选择器
    """
    action: str
    selector: str


@dataclass
class UploadAction(ASTNode):
    """
    文件上传动作

    语法: upload file "path" to "selector"

    Attributes:
        file_path: 文件路径
        selector: 文件上传控件选择器
    """
    file_path: str
    selector: str


# ============================================================
# 验证语句
# ============================================================

class ConditionOperator(Enum):
    """条件操作符 (v1.0 兼容)"""
    CONTAINS = "contains"
    EQUALS = "equals"
    MATCHES = "matches"
    EXISTS = "exists"
    VISIBLE = "visible"
    HIDDEN = "hidden"


@dataclass
class Condition(ASTNode):
    """
    条件表达式 (v1.0 兼容模式)

    用于 verify 语句、if 语句、when 语句等

    注意: v2.0 推荐直接使用 Expression,这个类保留用于向后兼容

    Attributes:
        condition_type: 条件类型（url, element, text, value）
        operator: 操作符（contains, equals, matches, exists, visible, hidden）
        value: 期望值
        selector: 选择器（可选，用于 element/text/value 条件）
    """
    condition_type: str
    operator: str
    value: Optional[str] = None
    selector: Optional[str] = None


@dataclass
class AssertStatement(ASTNode):
    """
    断言语句 (Assert Statement) - v2.0 简化语法，v4.3 增强

    语法: assert expression [, message_expression]

    示例:
        assert x > 5
        assert user.age >= 18, "User must be adult"
        assert arr.length() > 0, "Array should not be empty"
        assert status == 200 OR status == 201
        assert condition, error_msg  # v4.3: 支持变量和表达式

    Attributes:
        condition: 条件表达式（Expression）
        message: 可选的错误消息（字符串字面量或表达式）v4.3+
    """
    condition: Any  # Expression
    message: Optional[Any] = None  # v4.3: 可以是字符串或表达式


@dataclass
class ExitStatement(ASTNode):
    """
    退出语句 (Exit Statement) - v4.0

    语法: exit [code] [, "message"]

    示例:
        exit                    # 退出，code=0
        exit 1                  # 退出，code=1
        exit "Failed"           # 退出，code=1，消息
        exit 0, "Success"       # 退出，code=0，消息

    Attributes:
        code: 退出码（0=成功，非0=失败），默认0
        message: 可选的退出消息
    """
    code: Optional[int] = 0
    message: Optional[str] = None


# ============================================================
# 截图语句
# ============================================================

@dataclass
class ScreenshotStatement(ASTNode):
    """
    截图语句 (v2.0 完整语法)

    语法:
        screenshot                              # 全屏截图，自动命名
        screenshot as "name"                    # 全屏截图，指定名称
        screenshot fullpage as "name"           # 全页面截图（滚动）
        screenshot of "#selector"               # 元素截图，自动命名
        screenshot as "name" of "#selector"     # 元素截图，指定名称
        screenshot as name_var of selector_var  # v2.0 支持表达式

    Attributes:
        name: 截图名称（可选，None 表示自动生成，可以是字符串或表达式）
        fullpage: 是否全页面截图（滚动截图）
        selector: 元素选择器（可选，None 表示全屏截图，可以是字符串或表达式）
    """
    name: Optional[Any] = None  # str 或 Expression 或 None
    fullpage: bool = False
    selector: Optional[Any] = None  # str 或 Expression 或 None


# ============================================================
# 步骤块
# ============================================================

@dataclass
class StepBlock(ASTNode):
    """
    步骤块 (v3.0: 支持 diagnosis 选项)

    语法:
        step "name":
            ...

        step "name" if condition:
            ...

        step "name" with diagnosis detailed:
            ...

    Attributes:
        name: 步骤名称
        condition: 条件表达式（可选）
        diagnosis: 诊断级别（可选，如 "detailed", "simple"）
        statements: 步骤内的语句列表
    """
    name: str
    statements: List[ASTNode] = field(default_factory=list)
    condition: Optional[Condition] = None
    diagnosis: Optional[str] = None


# ============================================================
# 条件块
# ============================================================

@dataclass
class IfBlock(ASTNode):
    """
    if-else-if-else 条件块 (支持 v2.0 表达式和 else-if)

    语法:
        v1.0: if url contains "text"
        v2.0: if age > 18
              if $page.url contains "success"

        支持 else-if:
        if score >= 90:
            log "A"
        else if score >= 80:
            log "B"
        else if score >= 70:
            log "C"
        else:
            log "F"
        end if

    Attributes:
        condition: 条件表达式（可以是 Condition 或 Expression）
        then_statements: if 块中的语句
        elif_clauses: else-if 子句列表 [(condition, statements), ...]
        else_statements: else 块中的语句（可选）
    """
    condition: Any  # Condition 或 Expression
    then_statements: List[ASTNode] = field(default_factory=list)
    elif_clauses: List[tuple[Any, List[ASTNode]]] = field(default_factory=list)
    else_statements: List[ASTNode] = field(default_factory=list)


@dataclass
class WhenClause:
    """
    when 子句（v3.0: switch/match case，v3.1: 支持 OR 模式）

    Attributes:
        case_values: case 值表达式列表（支持 OR 模式: 200 | 201 | 204）
        statements: 语句列表
        line: 行号
    """
    case_values: List[Any] = field(default_factory=list)  # List[Expression] - OR 模式支持
    statements: List[ASTNode] = field(default_factory=list)
    line: int = 0


@dataclass
class WhenBlock(ASTNode):
    """
    when-otherwise 多分支条件块（v3.0: switch/match 语法）

    语法:
        when status:
            "active":
                ...
            "inactive":
                ...
            otherwise:
                ...

    Attributes:
        value_expression: 要匹配的表达式（如 status）
        when_clauses: case 子句列表
        otherwise_statements: otherwise 块中的语句（可选）
    """
    value_expression: Any  # Expression - 要匹配的值
    when_clauses: List[WhenClause] = field(default_factory=list)
    otherwise_statements: List[ASTNode] = field(default_factory=list)


# ============================================================
# v2.0 循环语句
# ============================================================

@dataclass
class EachLoop(ASTNode):
    """
    for 循环语句 (v3.0+, v4.0: 支持多变量元组解包)

    语法:
        # 单变量循环
        for item in items:
            log item

        # 多变量循环（元组解包）
        for index, item in enumerate(items):
            log f"Item {index}: {item}"

        for key, value in items:
            log f"{key} = {value}"

    Attributes:
        variable_names: 循环变量名列表（单变量时为 [name]，多变量时为 [name1, name2, ...]）
        iterable: 可迭代对象表达式
        statements: 循环体语句列表

    向后兼容:
        variable_name 属性仍然可用（返回第一个变量名）
    """
    variable_names: List[str] = field(default_factory=list)
    iterable: 'Expression' = None
    statements: List[ASTNode] = field(default_factory=list)

    @property
    def variable_name(self) -> str:
        """向后兼容：返回第一个变量名"""
        return self.variable_names[0] if self.variable_names else ""

    def __post_init__(self):
        """确保 variable_names 是列表"""
        if isinstance(self.variable_names, str):
            # 向后兼容：如果传入的是字符串，转换为列表
            self.variable_names = [self.variable_names]



# ============================================================
# v3.0 While 循环语句
# ============================================================

@dataclass
class WhileLoop(ASTNode):
    """
    while 循环语句 (v3.0)

    语法:
        while condition:
            statement1
            statement2

    语义:
    - 条件驱动的循环,每次迭代前求值条件
    - 不创建新作用域 (与 for 循环不同)
    - 支持 break/continue 控制流
    - 提供死循环保护机制

    示例:
        # 等待元素加载
        let loaded = False
        let timeout = 0
        while not loaded and timeout < 10:
            if element_exists("#content"):
                loaded = True
            else:
                wait 0.5
                timeout = timeout + 0.5

        # 重试机制
        let retry = 0
        while retry < 3:
            try:
                navigate to URL
                break
            catch error:
                retry = retry + 1
                wait 2

    Attributes:
        condition: 循环条件表达式 (必须求值为布尔值)
        statements: 循环体语句列表
    """
    condition: 'Expression'
    statements: List[ASTNode] = field(default_factory=list)


@dataclass
class BreakStatement(ASTNode):
    """
    break 语句 (v3.0)

    语法:
        break

    语义:
    - 立即退出最内层 while 循环
    - 只能在 while 循环内使用
    - v3.0 暂不支持 for 循环中使用

    示例:
        while True:
            let response = http.get(url=STATUS_URL)
            if response.ok and response.data.status == "completed":
                break  # 任务完成,退出循环
            wait 2

    Attributes:
        无额外属性 (仅继承 line 信息)
    """
    pass


@dataclass
class ContinueStatement(ASTNode):
    """
    continue 语句 (v3.0)

    语法:
        continue

    语义:
    - 跳过当前迭代的剩余语句
    - 直接进入下一次循环条件判断
    - 只能在 while 循环内使用
    - v3.0 暂不支持 for 循环中使用

    示例:
        let items = ["item1", "", "item3", None]
        while items.length() > 0:
            let item = items.pop(0)
            if item == "" or item == None:
                continue  # 跳过无效项
            process(item)

    Attributes:
        无额外属性 (仅继承 line 信息)
    """
    pass


# ============================================================
# v4.3 函数定义
# ============================================================

@dataclass
class FunctionDefNode(ASTNode):
    """
    函数定义节点 (Function Definition) - v4.3

    语法:
        function functionName(param1, param2):
            statement1
            statement2
            return expression

    语义:
    - 定义用户自定义函数
    - 函数具有独立的局部作用域
    - 参数按值传递 (pass by value)
    - 支持访问全局常量,不可修改全局变量
    - 不支持递归调用 (运行时检测并拒绝)
    - 不支持闭包 (不可访问外层函数的局部变量)

    示例:
        # 基础函数
        function add(a, b):
            return a + b

        # 带局部变量的函数
        function isStrongPassword(password):
            if len(password) < 8:
                return False

            let has_upper = False
            let has_lower = False
            let has_digit = False

            for char in password:
                if char >= "A" and char <= "Z":
                    has_upper = True
                if char >= "a" and char <= "z":
                    has_lower = True
                if char >= "0" and char <= "9":
                    has_digit = True

            return has_upper and has_lower and has_digit

        # 调用其他函数
        function validateUser(email, password):
            if not isValidEmail(email):
                return False
            if not isStrongPassword(password):
                return False
            return True

    Attributes:
        name: 函数名
        params: 参数名列表
        body: 函数体语句列表
    """
    name: str
    params: List[str] = field(default_factory=list)
    body: List[ASTNode] = field(default_factory=list)


@dataclass
class ReturnNode(ASTNode):
    """
    return 语句节点 (Return Statement) - v4.3

    语法:
        return expression
        return

    语义:
    - 从函数中返回值
    - 可以返回表达式结果
    - 可以无返回值 (return None)
    - 只能在函数体内使用

    示例:
        function add(a, b):
            return a + b

        function logAndReturn(value):
            log f"Returning: {value}"
            return value

        function doSomething():
            log "Done"
            return  # 无返回值

    Attributes:
        value: 返回值表达式 (None 表示无返回值)
    """
    value: Optional['Expression'] = None


# ============================================================
# 变量和数据操作
# ============================================================

@dataclass
class SetVariableStatement(ASTNode):
    """
    设置变量语句 (已弃用，使用 LetStatement 或 Assignment 代替)

    语法: set variable_name = "value"

    Attributes:
        name: 变量名
        value: 变量值
    """
    name: str
    value: str


# ============================================================
# v2.0 变量定义语句
# ============================================================

@dataclass
class LetStatement(ASTNode):
    """
    let 变量定义语句 (v2.0)

    语法: let variable_name = expression

    Attributes:
        name: 变量名
        value: 表达式节点
    """
    name: str
    value: 'Expression'


@dataclass
class ConstStatement(ASTNode):
    """
    const 常量定义语句 (v2.0)

    语法: const CONSTANT_NAME = expression

    Attributes:
        name: 常量名
        value: 表达式节点
    """
    name: str
    value: 'Expression'


@dataclass
class Assignment(ASTNode):
    """
    变量赋值语句 (v2.0)

    语法: variable_name = expression

    Attributes:
        name: 变量名
        value: 表达式节点
    """
    name: str
    value: 'Expression'


# ============================================================
# v2.0 表达式节点
# ============================================================

@dataclass
class Expression(ASTNode):
    """
    表达式基类 (v2.0)

    所有表达式节点的基类
    """
    pass


@dataclass
class BinaryOp(Expression):
    """
    二元运算表达式 (v2.0)

    语法: left operator right

    支持的运算符:
        算术: +, -, *, /, %
        比较: >, <, >=, <=, ==, !=, contains, matches, equals
        逻辑: AND, OR

    Attributes:
        left: 左操作数表达式
        operator: 运算符字符串
        right: 右操作数表达式
    """
    left: Expression
    operator: str
    right: Expression


@dataclass
class UnaryOp(Expression):
    """
    一元运算表达式 (v2.0)

    语法: operator operand

    支持的运算符:
        + : 正号
        - : 负号
        NOT : 逻辑非

    Attributes:
        operator: 运算符字符串
        operand: 操作数表达式
    """
    operator: str
    operand: Expression


@dataclass
class Literal(Expression):
    """
    字面量表达式 (v2.0)

    表示常量值:
        字符串: "hello"
        数字: 42, 3.14
        布尔: true, false
        空值: null

    Attributes:
        value: 字面量值 (str/int/float/bool/None)
    """
    value: Any


@dataclass
class Identifier(Expression):
    """
    标识符表达式 (v2.0)

    表示用户定义的变量引用

    语法: variable_name

    Attributes:
        name: 变量名
    """
    name: str


@dataclass
class SystemVariable(Expression):
    """
    系统变量引用表达式 (v2.0)

    表示系统提供的变量

    语法: $namespace.property[.sub_property...]

    示例:
        $context.task_id
        $page.url
        $element.text
        $env.API_TOKEN
        $config.api.base_url

    Attributes:
        path: 系统变量路径 (不含 $ 前缀)
    """
    path: str


@dataclass
class MemberAccess(Expression):
    """
    成员访问表达式 (v2.0)

    语法: object.property

    示例:
        user.email
        config.timeout

    Attributes:
        object: 对象表达式
        property: 属性名
    """
    object: Expression
    property: str


@dataclass
class ArrayAccess(Expression):
    """
    数组访问表达式 (v2.0)

    语法: array[index]

    示例:
        items[0]
        rows[i + 1]

    Attributes:
        array: 数组表达式
        index: 索引表达式
    """
    array: Expression
    index: Expression


@dataclass
class MethodCall(Expression):
    """
    方法调用表达式 (v2.0, v3.2: 支持命名参数)

    语法:
        object.method(arg1, arg2, ...)              # v2.0: 位置参数
        object.method(arg1, name1=val1, name2=val2)  # v3.2: 混合参数
        object.method(name1=val1, name2=val2)        # v3.2: 命名参数

    示例:
        text.toUpperCase()
        text.replace("old", "new")
        arr.push(4)
        text.trim().toLowerCase()  # 链式调用

        # v3.2: 命名参数
        random.password(length=16, special=True)
        http.get(url="https://api.example.com", timeout=10)
        random.password(16, special=True)  # 混合调用

    Attributes:
        object: 对象表达式
        method_name: 方法名
        arguments: 位置参数表达式列表
        kwargs: 命名参数字典 {参数名: 表达式}
    """
    object: Expression
    method_name: str
    arguments: List[Expression] = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)  # v3.2: 命名参数 {name: Expression}


@dataclass
class FunctionCall(Expression):
    """
    函数调用表达式 (v4.3)

    语法:
        functionName(arg1, arg2, ...)

    示例:
        add(1, 2)
        isValidEmail(email)
        max(a, b, c)

    说明:
    - 调用用户定义的函数或内置函数
    - 参数按位置传递（暂不支持命名参数）
    - 函数必须先定义后调用

    Attributes:
        function_name: 函数名
        arguments: 位置参数表达式列表
    """
    function_name: str
    arguments: List[Expression] = field(default_factory=list)


@dataclass
class ArrayLiteral(Expression):
    """
    数组字面量表达式 (v2.0)

    语法: [expression, expression, ...]

    示例:
        []                           # 空数组
        [1, 2, 3]                   # 数字数组
        ["a", "b", "c"]             # 字符串数组
        [1, "text", true]           # 混合类型数组
        [[1, 2], [3, 4]]            # 嵌套数组
        [x + 1, y * 2]              # 表达式元素

    Attributes:
        elements: 元素表达式列表
    """
    elements: List[Expression] = field(default_factory=list)


@dataclass
class ObjectLiteral(Expression):
    """
    对象字面量表达式 (v2.0)

    语法: {key1: value1, key2: value2, ...}

    示例:
        {}                                    # 空对象
        {name: "Alice", age: 25}             # 简单对象
        {x: 10, y: 20, color: "red"}         # 多个属性
        {user: {name: "Bob", age: 30}}       # 嵌套对象
        {count: x + 1, total: sum * 2}       # 表达式值
        {"first-name": "Alice", "last-name": "Smith"}  # 字符串键

    Attributes:
        pairs: 键值对列表 [(key, value_expr), ...]
               key 是字符串，value_expr 是表达式节点
    """
    pairs: List[tuple[str, Expression]] = field(default_factory=list)


@dataclass
class StringInterpolation(Expression):
    """
    字符串插值表达式 (v2.0)

    语法: "text {expression} more text {another_expr}"

    示例:
        "Hello {username}!"
        "Result: {a + b * 2}"
        "URL: {$page.url}"

    Attributes:
        parts: 字符串和表达式的列表
               [str, Expression, str, Expression, ...]
    """
    parts: List[Any]  # List[Union[str, Expression]]


@dataclass
class ExtractStatement(ASTNode):
    """
    提取数据语句 (支持 v2.0 表达式)

    语法:
        v1.0: extract text from "selector" into variable_name
        v2.0: extract text from "selector" into variable_name
              extract attr "href" from "selector" into url
              extract pattern "regex" from "selector" into result

    Attributes:
        extract_type: 提取类型（text, value, attr, pattern）
        selector: 元素选择器或表达式
        variable_name: 存储变量名
        attribute_name: 属性名（当 extract_type 为 attr 时）
        pattern: 正则表达式（当 extract_type 为 pattern 时）
    """
    extract_type: str
    selector: Any  # 可以是字符串或表达式
    variable_name: str
    attribute_name: Optional[str] = None
    pattern: Optional[str] = None


@dataclass
class LogStatement(ASTNode):
    """
    日志输出语句 (支持 v2.0 字符串插值，v4.3+ 日志级别)

    语法:
        v1.0: log "message"
        v2.0: log "message {variable}"
              log "Result: {a + b}"
        v4.3+: log info "message"               # 显式级别
               log debug "debug info"            # 调试信息 🔍
               log success "operation done"      # 成功消息 ✓
               log warning "careful here"        # 警告消息 ⚠
               log error "something wrong"       # 错误消息 ✗
               log success f"用户 {name} 注册成功"  # 级别 + f-string

    支持的级别（v4.3+）:
        - debug: 调试信息（灰色 🔍）
        - info: 普通信息（默认，无图标）
        - success: 成功消息（绿色 ✓）
        - warning: 警告消息（黄色 ⚠）
        - error: 错误消息（红色 ✗）

    Attributes:
        message: 日志消息（可以是字符串或 StringInterpolation 表达式）
        level: 日志级别（debug, info, success, warning, error）默认 info
    """
    message: Any  # str 或 StringInterpolation 或 Expression
    level: str = "info"


@dataclass
class ExpressionStatement(ASTNode):
    """
    表达式语句 (v4.3)

    将表达式包装为语句，用于独立的函数调用等

    语法:
        functionName(args)
        methodCall()

    示例:
        log("Hello")
        doSomething()

    Attributes:
        expression: 表达式节点
    """
    expression: 'Expression'


# ============================================================
# Module System (v5.0)
# ============================================================

@dataclass
class LibraryDeclaration(ASTNode):
    """
    Library 声明语句 (v5.0)

    声明当前文件为库文件，开启独立作用域模式

    语法:
        library NAME

    示例:
        library logging
        library validation

    Attributes:
        name: 库名称（必须与文件名匹配）
        line: 行号（继承自 ASTNode）
    """
    name: str

    def __repr__(self):
        return f"LibraryDeclaration(name={self.name!r}, line={self.line})"


@dataclass
class ExportStatement(ASTNode):
    """
    Export 语句 (v5.0)

    显式标记导出的常量或函数，定义库的公共 API

    语法:
        export const NAME = value
        export function NAME(...): ...

    示例:
        export const VERSION = "1.0"
        export function log_info(msg):
            log info msg

    Attributes:
        target: 被导出的节点 (ConstStatement 或 FunctionDefNode)
        line: 行号（继承自 ASTNode）
    """
    target: ASTNode  # ConstStatement | FunctionDefNode

    def __repr__(self):
        target_type = self.target.__class__.__name__
        target_name = getattr(self.target, 'name', '<unknown>')
        return f"ExportStatement(target={target_type}:{target_name}, line={self.line})"


@dataclass
class ImportStatement(ASTNode):
    """
    Import 语句 (v5.0)

    导入其他库的导出成员

    语法 1 (模块导入):
        import ALIAS from "PATH"

    语法 2 (From-Import):
        from "PATH" import NAME1, NAME2, ...

    示例:
        import logging from "libs/logging.flow"
        from "libs/validation.flow" import validate_email, validate_length

    Attributes:
        module_path: 库文件相对路径
        module_alias: 模块别名 (语法 1) 或 None (语法 2)
        members: 导入的成员列表 (语法 2) 或 None (语法 1)
        line: 行号（继承自 ASTNode）
    """
    module_path: str
    module_alias: Optional[str] = None
    members: Optional[List[str]] = None

    def __repr__(self):
        if self.module_alias:
            return f"ImportStatement(import {self.module_alias} from {self.module_path!r}, line={self.line})"
        else:
            members_str = ', '.join(self.members) if self.members else ''
            return f"ImportStatement(from {self.module_path!r} import {members_str}, line={self.line})"


@dataclass
class MemberAccessExpression(Expression):
    """
    成员访问表达式 (v5.0)

    访问模块对象的导出成员

    语法:
        object.member

    示例:
        logging.log_phase_start
        config.api.base_url

    Attributes:
        object: 对象表达式 (通常是 Literal 或 MemberAccessExpression)
        member: 成员名称
        line: 行号（继承自 Expression -> ASTNode）
    """
    object: Expression
    member: str

    def __repr__(self):
        return f"MemberAccess({self.object}.{self.member}, line={self.line})"


# ============================================================
# Input & Interaction (v5.1)
# ============================================================

@dataclass
class InputExpression(Expression):
    """
    Input 表达式 (v5.1)

    从控制台读取用户输入

    语法:
        input(PROMPT)
        input(PROMPT, default=DEFAULT_VALUE)
        input(PROMPT, type=TYPE)

    示例:
        let name = input("请输入姓名: ")
        let email = input("请输入邮箱: ", default="test@example.com")
        let password = input("请输入密码: ", type=password)
        let age = input("请输入年龄: ", type=integer)

    Attributes:
        prompt: 提示文本表达式
        default_value: 默认值表达式（可选）
        input_type: 输入类型（"text" | "password" | "integer" | "float"）
        line: 行号（继承自 Expression -> ASTNode）
    """
    prompt: Expression
    default_value: Optional[Expression] = None
    input_type: str = "text"

    def __repr__(self):
        parts = [f"prompt={repr(self.prompt)}"]
        if self.default_value:
            parts.append(f"default={repr(self.default_value)}")
        if self.input_type != "text":
            parts.append(f"type={self.input_type}")
        return f"InputExpression({', '.join(parts)}, line={self.line})"


# ============================================================
# 服务调用

# ============================================================
# 便捷函数
# ============================================================

def node_to_string(node: ASTNode, indent: int = 0) -> str:
    """
    将 AST 节点转换为可读的字符串表示

    Args:
        node: AST 节点
        indent: 缩进级别

    Returns:
        格式化的字符串表示
    """
    prefix = "  " * indent
    result = f"{prefix}{node.__class__.__name__}(line={node.line})"

    if isinstance(node, Program):
        result += f" [{len(node.statements)} statements]"
        for stmt in node.statements:
            result += "\n" + node_to_string(stmt, indent + 1)

    elif isinstance(node, NavigateToStatement):
        result += f" url={node.url!r}"

    elif isinstance(node, SelectStatement):
        result += f" element_type={node.element_type!r}"
        for attr, value in node.conditions:
            result += f"\n{prefix}  {attr}={value!r}"

    elif isinstance(node, TypeAction):
        result += f" text={node.text!r} mode={node.mode}"

    elif isinstance(node, StepBlock):
        result += f" name={node.name!r}"
        if node.condition:
            result += f" if {node.condition}"
        for stmt in node.statements:
            result += "\n" + node_to_string(stmt, indent + 1)

    elif isinstance(node, IfBlock):
        result += f" condition={node.condition}"
        result += f"\n{prefix}  then:"
        for stmt in node.then_statements:
            result += "\n" + node_to_string(stmt, indent + 2)
        for i, (elif_cond, elif_stmts) in enumerate(node.elif_clauses):
            result += f"\n{prefix}  elif[{i}] condition={elif_cond}:"
            for stmt in elif_stmts:
                result += "\n" + node_to_string(stmt, indent + 2)
        if node.else_statements:
            result += f"\n{prefix}  else:"
            for stmt in node.else_statements:
                result += "\n" + node_to_string(stmt, indent + 2)

    return result
