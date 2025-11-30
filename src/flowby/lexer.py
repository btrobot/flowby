"""
词法分析器 v3.0 (Lexer V3 - Python风格)

将 .dsl 文件的文本转换为 Token 流（支持缩进语义）

v3.0 核心变更:
    1. ✅ 新增 INDENT/DEDENT tokens（替代 END token）
    2. ✅ Python风格布尔值：True/False（首字母大写）
    3. ✅ Python风格 None（替代 null）
    4. ✅ 显式 f-string：f"text {x}"（需要 f 前缀）
    5. ✅ 三引号注释：\"\"\" ... \"\"\"（Python风格）
    6. ✅ 系统变量无$前缀：page.url（而非 $page.url）

缩进栈算法（参考 Python PEP 8）:
    - indent_stack: List[int] = [0]  # 缩进栈
    - 每级缩进必须是 4 的倍数
    - 缩进增加生成 INDENT token
    - 缩进减少生成 DEDENT token(s)
    - EOF 时清空栈生成所有剩余 DEDENT

示例:
    输入（v3.0）:
        step "登录":
            if user.active:
                log f"用户: {user.name}"
                let success = True

    输出 Tokens:
        [STEP, STRING("登录"), COLON, NEWLINE,
         INDENT,  # +4空格
         IF, IDENTIFIER(user), DOT, IDENTIFIER(active), COLON, NEWLINE,
         INDENT,  # +4空格
         LOG, FSTRING("用户: {user.name}"), NEWLINE,
         LET, IDENTIFIER(success), EQUALS_SIGN, TRUE, NEWLINE,
         DEDENT,  # 回退到step级
         DEDENT]  # 回退到顶层
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional
from .errors import LexerError


class TokenType(Enum):
    """Token 类型枚举 (v3.0)"""

    # === v3.0 新增：缩进 tokens ===
    INDENT = auto()          # 缩进增加
    DEDENT = auto()          # 缩进减少

    # === 关键字 ===
    # 变量定义
    LET = auto()             # let 关键字
    CONST = auto()           # const 关键字

    # 导航
    NAVIGATE = auto()
    TO = auto()
    GO = auto()
    BACK = auto()
    FORWARD = auto()
    RELOAD = auto()

    # 等待
    WAIT = auto()
    FOR = auto()
    UNTIL = auto()
    ELEMENT = auto()
    NAVIGATION = auto()

    # 选择和动作
    SELECT = auto()
    WHERE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()             # NOT 关键字（逻辑非）
    TYPE = auto()
    CLICK = auto()
    DOUBLE_CLICK = auto()
    RIGHT_CLICK = auto()
    HOVER = auto()
    OVER = auto()
    OF = auto()              # of 关键字（用于 screenshot of selector）
    CLEAR = auto()
    PRESS = auto()
    SCROLL = auto()
    CHECK = auto()
    UNCHECK = auto()
    UPLOAD = auto()
    FILE = auto()
    FROM = auto()
    OPTION = auto()

    # 服务调用
    INTO = auto()

    # 提取语句
    EXTRACT = auto()         # extract 关键字
    ATTR = auto()            # attr 关键字
    PATTERN = auto()         # pattern 关键字

    # 日志
    LOG = auto()             # log 关键字

    # 循环
    WHILE = auto()           # while 关键字 (v3.0)
    BREAK = auto()           # break 关键字 (v3.0)
    CONTINUE = auto()        # continue 关键字 (v3.0)

    # === v3.0 变更：Python风格布尔值和None ===
    TRUE = auto()            # True（Python风格，首字母大写）
    FALSE = auto()           # False（Python风格，首字母大写）
    NONE = auto()            # None（Python风格，替代null）

    # 断言/验证
    ASSERT = auto()
    EXIT = auto()            # exit 语句 (v4.1)

    # 模块系统 (v5.0)
    LIBRARY = auto()         # library 声明 (v5.0)
    EXPORT = auto()          # export 语句 (v5.0)
    IMPORT = auto()          # import 语句 (v5.0)
    # FROM = auto()          # 已存在 (line 92, 用于 upload/select)

    # 断言条件
    URL = auto()
    CONTAINS = auto()
    EQUALS = auto()
    MATCHES = auto()
    EXISTS = auto()
    VISIBLE = auto()
    HIDDEN = auto()
    TEXT = auto()
    VALUE = auto()
    IN = auto()
    WITH = auto()        # 用于 with diagnosis
    DIAGNOSIS = auto()   # 诊断级别

    # 诊断级别
    DIAG_NONE = auto()       # 重命名避免与 None 字面量冲突
    MINIMAL = auto()
    BASIC = auto()
    STANDARD = auto()
    DETAILED = auto()
    FULL = auto()

    # 截图
    SCREENSHOT = auto()
    AS = auto()
    FULLPAGE = auto()

    # === v3.0 变更：删除 END token ===
    # END = auto()  # 已删除，使用 DEDENT 替代

    # 控制流
    STEP = auto()
    IF = auto()
    ELSE = auto()
    WHEN = auto()
    OTHERWISE = auto()

    # 函数定义 (v4.3)
    FUNCTION = auto()        # function 关键字
    RETURN = auto()          # return 关键字

    # 元素类型
    INPUT = auto()
    BUTTON = auto()
    LINK = auto()
    TEXTAREA = auto()
    DIV = auto()
    SPAN = auto()

    # 修饰符
    SLOWLY = auto()
    FAST = auto()

    # 页面状态
    NETWORKIDLE = auto()
    DOMCONTENTLOADED = auto()
    LOAD = auto()

    # 元素状态
    ATTACHED = auto()
    DETACHED = auto()

    # 滚动目标
    TOP = auto()
    BOTTOM = auto()

    # === 字面量 ===
    STRING = auto()          # "text" or 'text'（普通字符串，不插值）
    FSTRING = auto()         # f"text {x}"（v3.0: 显式 f 前缀）
    INTEGER = auto()         # 整数（v4.0）
    NUMBER = auto()          # 浮点数 123.45
    IDENTIFIER = auto()      # 标识符（变量名）

    # === v3.0 删除：系统变量 token ===
    # SYSTEM_VAR = auto()  # 已删除，系统变量现在是普通标识符（无$前缀）

    # === 运算符和标点 ===
    EQUALS_SIGN = auto()     # =
    COLON = auto()           # :
    COMMA = auto()           # ,

    # 算术运算符
    PLUS = auto()            # +
    MINUS = auto()           # -
    STAR = auto()            # *
    SLASH = auto()           # /
    PERCENT = auto()         # %

    # 比较运算符
    GT = auto()              # >
    LT = auto()              # <
    GTE = auto()             # >=
    LTE = auto()             # <=
    EQ = auto()              # ==
    NEQ = auto()             # !=

    # 括号和分隔符
    LPAREN = auto()          # (
    RPAREN = auto()          # )
    LBRACKET = auto()        # [
    RBRACKET = auto()        # ]
    LBRACE = auto()          # {
    RBRACE = auto()          # }
    DOT = auto()             # .
    PIPE = auto()            # | (v3.1: OR pattern in when statement)

    # === 特殊 ===
    NEWLINE = auto()         # \n
    EOF = auto()             # 文件结束


@dataclass
class Token:
    """
    Token 数据类 (v3.0)

    Attributes:
        type: Token 类型
        value: Token 值
        line: 行号（从 1 开始）
        column: 列号（从 1 开始）
    """
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        if self.value:
            return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"
        return f"Token({self.type.name}, {self.line}:{self.column})"


class Lexer:
    """
    词法分析器 v3.0（Python风格）

    将源代码文本转换为 Token 流，支持 INDENT/DEDENT 机制
    """

    # === v3.0 关键字映射（Python风格）===
    KEYWORDS = {
        # 变量定义
        'let': TokenType.LET,
        'const': TokenType.CONST,

        # 导航
        'navigate': TokenType.NAVIGATE,
        'to': TokenType.TO,
        'go': TokenType.GO,
        'back': TokenType.BACK,
        'forward': TokenType.FORWARD,
        'reload': TokenType.RELOAD,

        # 等待
        'wait': TokenType.WAIT,
        'for': TokenType.FOR,
        'until': TokenType.UNTIL,
        'element': TokenType.ELEMENT,
        'navigation': TokenType.NAVIGATION,

        # 选择和动作
        'select': TokenType.SELECT,
        'where': TokenType.WHERE,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
        'type': TokenType.TYPE,
        'click': TokenType.CLICK,
        'double_click': TokenType.DOUBLE_CLICK,
        'right_click': TokenType.RIGHT_CLICK,
        'hover': TokenType.HOVER,
        'over': TokenType.OVER,
        'of': TokenType.OF,
        'clear': TokenType.CLEAR,
        'press': TokenType.PRESS,
        'scroll': TokenType.SCROLL,
        'check': TokenType.CHECK,
        'uncheck': TokenType.UNCHECK,
        'upload': TokenType.UPLOAD,
        'file': TokenType.FILE,
        'from': TokenType.FROM,
        'option': TokenType.OPTION,

        # 服务调用
        'into': TokenType.INTO,

        # 提取语句
        'extract': TokenType.EXTRACT,
        'attr': TokenType.ATTR,
        'pattern': TokenType.PATTERN,

        # 日志
        'log': TokenType.LOG,

        # 循环
        'while': TokenType.WHILE,     # v3.0 while 循环
        'break': TokenType.BREAK,     # v3.0 退出循环
        'continue': TokenType.CONTINUE,  # v3.0 跳过迭代

        # 函数 (v4.3)
        'function': TokenType.FUNCTION,  # v4.3 函数定义
        'return': TokenType.RETURN,      # v4.3 返回语句

        # === v3.0 变更：Python风格布尔值和None ===
        'True': TokenType.TRUE,      # 首字母大写
        'False': TokenType.FALSE,    # 首字母大写
        'None': TokenType.NONE,      # 首字母大写

        # === v3.0 删除：v2.0 风格布尔值 ===
        # 'true': TokenType.TRUE,    # 已删除
        # 'false': TokenType.FALSE,  # 已删除
        # 'null': TokenType.NULL,    # 已删除

        # 断言/验证
        'assert': TokenType.ASSERT,
        'exit': TokenType.EXIT,

        # 模块系统 (v5.0)
        'library': TokenType.LIBRARY,
        'export': TokenType.EXPORT,
        'import': TokenType.IMPORT,
        # 'from': TokenType.FROM,  # 已存在 (line 304, 用于 upload/select)

        # 断言条件
        'url': TokenType.URL,
        'contains': TokenType.CONTAINS,
        'equals': TokenType.EQUALS,
        'matches': TokenType.MATCHES,
        'exists': TokenType.EXISTS,
        'visible': TokenType.VISIBLE,
        'hidden': TokenType.HIDDEN,
        'text': TokenType.TEXT,
        'value': TokenType.VALUE,
        'in': TokenType.IN,
        'with': TokenType.WITH,
        'diagnosis': TokenType.DIAGNOSIS,

        # 诊断级别（'none'会与None字面量冲突，需特殊处理）
        'none': TokenType.DIAG_NONE,  # 诊断级别的none
        'minimal': TokenType.MINIMAL,
        'basic': TokenType.BASIC,
        'standard': TokenType.STANDARD,
        'detailed': TokenType.DETAILED,
        'full': TokenType.FULL,

        # 截图
        'screenshot': TokenType.SCREENSHOT,
        'as': TokenType.AS,
        'fullpage': TokenType.FULLPAGE,

        # === v3.0 删除：END 关键字 ===
        # 'end': TokenType.END,  # 已删除

        # 控制流
        'step': TokenType.STEP,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'when': TokenType.WHEN,
        'otherwise': TokenType.OTHERWISE,

        # 元素类型
        'input': TokenType.INPUT,
        'button': TokenType.BUTTON,
        'link': TokenType.LINK,
        'textarea': TokenType.TEXTAREA,
        'div': TokenType.DIV,
        'span': TokenType.SPAN,

        # 修饰符
        'slowly': TokenType.SLOWLY,
        'fast': TokenType.FAST,

        # 页面状态
        'networkidle': TokenType.NETWORKIDLE,
        'domcontentloaded': TokenType.DOMCONTENTLOADED,
        'load': TokenType.LOAD,

        # 元素状态
        'attached': TokenType.ATTACHED,
        'detached': TokenType.DETACHED,

        # 滚动目标
        'top': TokenType.TOP,
        'bottom': TokenType.BOTTOM,
    }

    def __init__(self):
        """初始化词法分析器 v3.0"""
        self.source = ""
        self.source_lines: List[str] = []
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

        # === v3.0 新增：缩进栈 ===
        self.indent_stack: List[int] = [0]  # 缩进栈，初始为 [0]
        self.at_line_start = True  # 是否在行首
        self.pending_dedents = 0  # 待发出的 DEDENT 数量

        # 文件级缩进方式跟踪（检测混用 Tab 和空格）
        self.file_indent_type: Optional[str] = None  # None | 'spaces' | 'tabs'

    def tokenize(self, source: str) -> List[Token]:
        """
        对源代码进行词法分析（v3.0 支持缩进）

        Args:
            source: 源代码文本

        Returns:
            Token 列表

        Raises:
            LexerError: 词法分析错误
        """
        self.source = source
        self.source_lines = source.split('\n')
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.indent_stack = [0]
        self.at_line_start = True
        self.pending_dedents = 0

        while not self._is_at_end():
            self._scan_token()

        # === v3.0 新增：EOF 时生成所有剩余 DEDENT ===
        self._generate_dedents_at_eof()

        # 添加 EOF token
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))

        return self.tokens

    def _scan_token(self):
        """扫描下一个 token（v3.0 支持缩进处理）"""
        # === v3.0 新增：处理待发出的 DEDENT ===
        if self.pending_dedents > 0:
            self.pending_dedents -= 1
            self.tokens.append(Token(TokenType.DEDENT, "", self.line, self.column))
            return

        # === v3.0 新增：行首缩进处理 ===
        if self.at_line_start:
            self._handle_indentation()
            self.at_line_start = False

            # 处理完缩进后可能需要立即返回 INDENT/DEDENT
            if self.tokens and self.tokens[-1].type in (TokenType.INDENT, TokenType.DEDENT):
                return

        # 跳过空白符（但保留换行）
        while not self._is_at_end() and self._peek() in ' \t\r':
            self._advance()

        if self._is_at_end():
            return

        # 保存 token 开始位置
        start_line = self.line
        start_column = self.column

        char = self._peek()

        # 换行
        if char == '\n':
            self._advance()
            self.tokens.append(Token(TokenType.NEWLINE, '\n', start_line, start_column))
            self.at_line_start = True  # v3.0: 标记下一行需要处理缩进
            return

        # 注释
        if char == '#':
            self._skip_line_comment()
            return

        # === v3.0 新增：三引号块注释 ===
        if char == '"' and self._peek(1) == '"' and self._peek(2) == '"':
            self._skip_triple_quote_comment()
            return

        # === v3.0 变更：f-string 处理 ===
        # 检测 f" 或 f'
        if char == 'f' and self._peek(1) in ('"', "'"):  # 使用元组避免空字符串匹配
            self._scan_fstring()
            return

        # 字符串（普通，不插值）
        if char in '"\'':
            self._scan_string()
            return

        # === v3.0 删除：系统变量 $ 前缀处理 ===
        # 不再支持 $page.url，系统变量现在是普通标识符 page.url

        # 数字
        if char.isdigit():
            self._scan_number()
            return

        # 标识符或关键字（v3.0: 包括系统变量，如 page.url）
        if char.isalpha() or char == '_':
            self._scan_identifier()
            return

        # 运算符和标点
        if char == '=':
            self._advance()
            # 检查 ==
            if self._peek() == '=':
                self._advance()
                self.tokens.append(Token(TokenType.EQ, '==', start_line, start_column))
            else:
                self.tokens.append(Token(TokenType.EQUALS_SIGN, '=', start_line, start_column))
            return

        if char == '!':
            self._advance()
            # 检查 !=
            if self._peek() == '=':
                self._advance()
                self.tokens.append(Token(TokenType.NEQ, '!=', start_line, start_column))
            else:
                # 单独的 ! 表示逻辑非
                self.tokens.append(Token(TokenType.NOT, '!', start_line, start_column))
            return

        if char == '>':
            self._advance()
            if self._peek() == '=':
                self._advance()
                self.tokens.append(Token(TokenType.GTE, '>=', start_line, start_column))
            else:
                self.tokens.append(Token(TokenType.GT, '>', start_line, start_column))
            return

        if char == '<':
            self._advance()
            if self._peek() == '=':
                self._advance()
                self.tokens.append(Token(TokenType.LTE, '<=', start_line, start_column))
            else:
                self.tokens.append(Token(TokenType.LT, '<', start_line, start_column))
            return

        if char == '+':
            self._advance()
            self.tokens.append(Token(TokenType.PLUS, '+', start_line, start_column))
            return

        if char == '-':
            self._advance()
            self.tokens.append(Token(TokenType.MINUS, '-', start_line, start_column))
            return

        if char == '*':
            self._advance()
            self.tokens.append(Token(TokenType.STAR, '*', start_line, start_column))
            return

        if char == '/':
            self._advance()
            # v3.0: 删除 /* */ 多行注释支持（已改用 """ """）
            self.tokens.append(Token(TokenType.SLASH, '/', start_line, start_column))
            return

        if char == '%':
            self._advance()
            self.tokens.append(Token(TokenType.PERCENT, '%', start_line, start_column))
            return

        if char == '(':
            self._advance()
            self.tokens.append(Token(TokenType.LPAREN, '(', start_line, start_column))
            return

        if char == ')':
            self._advance()
            self.tokens.append(Token(TokenType.RPAREN, ')', start_line, start_column))
            return

        if char == '[':
            self._advance()
            self.tokens.append(Token(TokenType.LBRACKET, '[', start_line, start_column))
            return

        if char == ']':
            self._advance()
            self.tokens.append(Token(TokenType.RBRACKET, ']', start_line, start_column))
            return

        if char == '.':
            self._advance()
            self.tokens.append(Token(TokenType.DOT, '.', start_line, start_column))
            return

        if char == ':':
            self._advance()
            self.tokens.append(Token(TokenType.COLON, ':', start_line, start_column))
            return

        if char == ',':
            self._advance()
            self.tokens.append(Token(TokenType.COMMA, ',', start_line, start_column))
            return

        if char == '{':
            self._advance()
            self.tokens.append(Token(TokenType.LBRACE, '{', start_line, start_column))
            return

        if char == '}':
            self._advance()
            self.tokens.append(Token(TokenType.RBRACE, '}', start_line, start_column))
            return

        if char == '|':
            self._advance()
            self.tokens.append(Token(TokenType.PIPE, '|', start_line, start_column))
            return

        # 未知字符
        raise LexerError(
            self.line,
            self.column,
            f"未知字符: {char!r}",
            self._get_current_line()
        )

    # ========== v3.0 新增：缩进处理核心算法 ==========

    def _handle_indentation(self):
        """
        处理行首缩进（v3.0 核心算法）

        算法（参考 Python PEP 8）:
            1. 计算当前行缩进量（空格/Tab）
            2. 跳过空行和纯注释行（不影响缩进栈）
            3. 与栈顶比较:
               - current_indent > stack.top: 生成 INDENT，push 到栈
               - current_indent < stack.top: 循环 pop，生成 DEDENT(s)
               - current_indent == stack.top: 无操作

        验证规则:
            - 每级缩进必须是 4 的倍数
            - 缩进增加必须正好 +4
            - 缩进减少必须匹配栈中历史缩进
        """
        # 使用循环跳过所有空行和纯注释行（包括它们的 newline）
        while True:
            # 检查并跳过空行
            if self._is_blank_line():
                # 跳过空白符
                while not self._is_at_end() and self._peek() in ' \t':
                    self._advance()
                # 跳过 newline
                if self._peek() == '\n':
                    self._advance()  # _advance() 内部会更新行号，不需要手动设置
                    # 继续处理下一行
                    continue
                else:
                    # 文件结尾
                    return

            # 计算缩进量（必须在检查注释之前，因为注释可能有缩进）
            indent_level = 0
            start_pos = self.pos
            uses_spaces = False
            uses_tabs = False

            while not self._is_at_end() and self._peek() in ' \t':
                char = self._peek()
                if char == ' ':
                    indent_level += 1
                    uses_spaces = True
                elif char == '\t':
                    indent_level += 4  # Tab = 4 空格
                    uses_tabs = True
                self._advance()

            # 检查是否是纯注释行
            if self._peek() == '#':
                # 跳过注释内容
                self._skip_line_comment()
                # 跳过 newline（注释行不产生任何 token）
                if self._peek() == '\n':
                    self._advance()  # _advance() 内部会更新行号，不需要手动设置
                # 继续处理下一行
                continue

            # 检查是否是三引号注释行
            if self._peek() == '"' and self._peek(1) == '"' and self._peek(2) == '"':
                # 跳过整个三引号块
                self._skip_triple_quote_comment()
                # 跳过三引号后的空白（如果三引号结束后是行尾）
                while not self._is_at_end() and self._peek() in ' \t':
                    self._advance()
                # 如果三引号后是 newline，跳过它
                if self._peek() == '\n':
                    self._advance()  # _advance() 内部会更新行号，不需要手动设置
                # 继续处理下一行
                continue

            # 找到了非注释、非空行，处理缩进
            break

        # 验证：禁止在同一行混合空格和 Tab
        if uses_spaces and uses_tabs:
            raise LexerError(
                self.line,
                self.column,
                "缩进错误：禁止在同一行混合使用空格和 Tab\n请统一使用 4 个空格或 1 个 Tab",
                self._get_current_line()
            )

        # 验证：文件内禁止混用空格和 Tab（不同行之间）
        if uses_spaces or uses_tabs:
            current_indent_type = 'spaces' if uses_spaces else 'tabs'
            if self.file_indent_type is None:
                # 第一次遇到缩进，记录文件使用的缩进方式
                self.file_indent_type = current_indent_type
            elif self.file_indent_type != current_indent_type:
                # 文件内混用不同缩进方式
                raise LexerError(
                    self.line,
                    self.column,
                    f"缩进错误：文件内混用 Tab 和空格\n"
                    f"之前使用 {'空格' if self.file_indent_type == 'spaces' else 'Tab'}，此行使用 {'空格' if current_indent_type == 'spaces' else 'Tab'}\n"
                    f"请在整个文件中统一使用 4 个空格或 1 个 Tab",
                    self._get_current_line()
                )

        # 验证：缩进必须是 4 的倍数
        if indent_level % 4 != 0:
            raise LexerError(
                self.line,
                self.column,
                f"缩进错误：缩进量 {indent_level} 不是 4 的倍数\n每级缩进必须是 4 个空格或 1 个 Tab",
                self._get_current_line()
            )

        # 获取栈顶缩进
        current_stack_top = self.indent_stack[-1]

        # 情况1: 缩进增加
        if indent_level > current_stack_top:
            # 验证：缩进增加必须正好 +4
            if indent_level != current_stack_top + 4:
                raise LexerError(
                    self.line,
                    self.column,
                    f"缩进错误：缩进跳跃（{current_stack_top} → {indent_level}）\n"
                    f"每次缩进只能增加 4 个空格（或 1 个 Tab）",
                    self._get_current_line()
                )

            self.indent_stack.append(indent_level)
            self.tokens.append(Token(TokenType.INDENT, "", self.line, 1))

        # 情况2: 缩进减少
        elif indent_level < current_stack_top:
            # 循环 pop 直到找到匹配的缩进级别
            while len(self.indent_stack) > 1 and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                self.pending_dedents += 1

            # 验证：减少后的缩进必须匹配栈中某个历史缩进
            if self.indent_stack[-1] != indent_level:
                raise LexerError(
                    self.line,
                    self.column,
                    f"缩进错误：缩进量 {indent_level} 不匹配任何历史缩进级别\n"
                    f"有效的缩进级别：{self.indent_stack}",
                    self._get_current_line()
                )

            # 发出第一个 DEDENT，其余的在下次 _scan_token 调用时发出
            if self.pending_dedents > 0:
                self.pending_dedents -= 1
                self.tokens.append(Token(TokenType.DEDENT, "", self.line, 1))

        # 情况3: 缩进相同
        else:
            # 无操作
            pass

    def _generate_dedents_at_eof(self):
        """
        在文件结束时生成所有剩余的 DEDENT token

        将缩进栈清空到 [0]
        """
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, "", self.line, self.column))

    def _is_blank_line(self) -> bool:
        """检查当前行是否为空行（只包含空白符）"""
        saved_pos = self.pos
        saved_column = self.column

        # 跳过空白符
        while not self._is_at_end() and self._peek() in ' \t':
            self._advance()

        # 检查是否到达换行或文件末尾
        is_blank = self._is_at_end() or self._peek() == '\n'

        # 恢复位置
        self.pos = saved_pos
        self.column = saved_column

        return is_blank

    # ========== v3.0 变更：字符串处理 ==========

    def _scan_string(self):
        """
        扫描普通字符串字面量（v3.0: 不插值）

        v3.0 变更：普通字符串 "text" 不支持插值
        需要插值必须使用 f-string: f"text {x}"
        """
        start_line = self.line
        start_column = self.column

        quote = self._advance()  # 消费开始的引号
        value = ""

        while not self._is_at_end() and self._peek() != quote:
            char = self._advance()

            # 处理转义字符
            if char == '\\':
                if self._is_at_end():
                    raise LexerError(
                        self.line,
                        self.column,
                        "字符串未结束（遇到文件结尾）",
                        self._get_current_line()
                    )

                next_char = self._advance()
                if next_char == 'n':
                    value += '\n'
                elif next_char == 't':
                    value += '\t'
                elif next_char == '\\':
                    value += '\\'
                elif next_char == quote:
                    value += quote
                elif next_char == '{':
                    # 转义的 \{ 表示字面量 {
                    value += '{'
                else:
                    value += next_char
            else:
                value += char

        if self._is_at_end():
            raise LexerError(
                start_line,
                start_column,
                "字符串未结束（遇到文件结尾）",
                self._get_current_line()
            )

        self._advance()  # 消费结束的引号

        self.tokens.append(Token(TokenType.STRING, value, start_line, start_column))

    def _scan_fstring(self):
        """
        扫描 f-string 字面量（v3.0 新增）

        语法: f"text {expr}" 或 f'text {expr}'
        支持字符串插值表达式
        """
        start_line = self.line
        start_column = self.column

        self._advance()  # 消费 'f'
        quote = self._advance()  # 消费开始的引号

        value = ""

        while not self._is_at_end() and self._peek() != quote:
            char = self._advance()

            # 处理转义字符
            if char == '\\':
                if self._is_at_end():
                    raise LexerError(
                        self.line,
                        self.column,
                        "f-string 未结束（遇到文件结尾）",
                        self._get_current_line()
                    )

                next_char = self._advance()
                if next_char == 'n':
                    value += '\n'
                elif next_char == 't':
                    value += '\t'
                elif next_char == '\\':
                    value += '\\'
                elif next_char == quote:
                    value += quote
                elif next_char == '{':
                    # 转义的 \{ 表示字面量 {
                    value += '{'
                else:
                    value += next_char
            else:
                # f-string 中的 {expr} 保留原样（Parser 负责展开）
                value += char

        if self._is_at_end():
            raise LexerError(
                start_line,
                start_column,
                "f-string 未结束（遇到文件结尾）",
                self._get_current_line()
            )

        self._advance()  # 消费结束的引号

        self.tokens.append(Token(TokenType.FSTRING, value, start_line, start_column))

    # ========== v3.0 新增：三引号注释 ==========

    def _skip_triple_quote_comment(self):
        """
        跳过三引号注释（v3.0 Python 风格）

        语法: \"\"\" ... \"\"\"
        替代 v2.0 的 /* ... */ 注释
        """
        start_line = self.line
        start_column = self.column

        # 消费开始的 """
        self._advance()  # "
        self._advance()  # "
        self._advance()  # "

        # 查找结束的 """
        while not self._is_at_end():
            if self._peek() == '"' and self._peek(1) == '"' and self._peek(2) == '"':
                # 消费结束的 """
                self._advance()
                self._advance()
                self._advance()
                return

            self._advance()

        # 未找到结束标记
        raise LexerError(
            start_line,
            start_column,
            "未闭合的三引号注释：缺少 \"\"\"",
            self._get_current_line()
        )

    def _skip_line_comment(self):
        """跳过行注释（从 # 到行尾，不包括换行符）"""
        while not self._is_at_end() and self._peek() != '\n':
            self._advance()

    # ========== 通用辅助方法 ==========

    def _scan_number(self):
        """
        扫描数字（v4.0: 区分整数和浮点数）

        返回:
            - TokenType.INTEGER: 整数字面量（如 5, 123）
            - TokenType.NUMBER: 浮点数字面量（如 3.14, 5.0）或带时间单位的数字
        """
        start_line = self.line
        start_column = self.column

        value = ""
        has_decimal_point = False  # v4.0: 跟踪是否有小数点
        has_time_unit = False      # v4.0: 跟踪是否有时间单位

        # 整数部分
        while not self._is_at_end() and self._peek().isdigit():
            value += self._advance()

        # 小数部分
        if not self._is_at_end() and self._peek() == '.':
            # 检查小数点后是否有数字
            if self.pos + 1 < len(self.source) and self.source[self.pos + 1].isdigit():
                has_decimal_point = True  # v4.0: 标记为浮点数
                value += self._advance()  # 消费 .
                while not self._is_at_end() and self._peek().isdigit():
                    value += self._advance()

        # 时间单位（支持 s, ms, sec, second, seconds）
        # v4.0: 带时间单位的数字被视为浮点数（时间值概念）
        if not self._is_at_end():
            remaining = self.source[self.pos:]

            # ms (必须先检查)
            if remaining.startswith('ms'):
                has_time_unit = True
                value += self._advance()  # m
                value += self._advance()  # s
            # seconds
            elif remaining.lower().startswith('seconds'):
                has_time_unit = True
                for _ in range(7):
                    value += self._advance()
            # second
            elif remaining.lower().startswith('second'):
                has_time_unit = True
                for _ in range(6):
                    value += self._advance()
            # sec
            elif remaining.lower().startswith('sec'):
                has_time_unit = True
                for _ in range(3):
                    value += self._advance()
            # s
            elif remaining.startswith('s'):
                has_time_unit = True
                value += self._advance()

        # v4.0: 根据是否有小数点或时间单位决定 token 类型
        if has_decimal_point or has_time_unit:
            # 浮点数或带时间单位的数字
            self.tokens.append(Token(TokenType.NUMBER, value, start_line, start_column))
        else:
            # 整数
            self.tokens.append(Token(TokenType.INTEGER, value, start_line, start_column))

    def _scan_identifier(self):
        """
        扫描标识符或关键字（v3.0: 区分大小写）

        v3.0 变更：
        - True/False/None 必须首字母大写
        - 关键字仍然不区分大小写（除布尔值和 None）
        """
        start_line = self.line
        start_column = self.column

        value = ""
        while not self._is_at_end() and (self._peek().isalnum() or self._peek() in '_'):
            value += self._advance()

        # === v3.0 特殊处理：True/False/None 必须大小写匹配 ===
        if value in ('True', 'False', 'None'):
            token_type = self.KEYWORDS[value]
            self.tokens.append(Token(token_type, value, start_line, start_column))
            return

        # === v3.0 检测错误的布尔/null 关键字并报错 ===
        # 检测小写或全大写的布尔/null 关键字
        if value.lower() in ('true', 'false', 'null', 'none'):
            # 如果是诊断级别的 'none'（小写且是关键字），允许通过
            if value.lower() == 'none' and value.lower() in self.KEYWORDS:
                token_type = self.KEYWORDS[value.lower()]
                self.tokens.append(Token(token_type, value, start_line, start_column))
                return

            # 获取正确的 Python 风格写法
            correct_form = {
                'true': 'True',
                'false': 'False',
                'null': 'None',
                'none': 'None'
            }.get(value.lower(), value)

            # 如果是诊断级别的 'none'，需要上下文判断（这里简化处理，统一提示使用 None）
            raise LexerError(
                line=start_line,
                column=start_column,
                message=f"v3.0 使用 Python 风格字面量：应该使用 '{correct_form}' 而不是 '{value}'",
                suggestion=f"将 '{value}' 改为 '{correct_form}'"
            )

        # 其他关键字不区分大小写
        # v6.0: 首字母大写的标识符（如 Resource）不视为关键字，作为标识符处理
        # 这允许使用 Resource() 作为内置函数，同时保留 resource 关键字
        if value[0].isupper():
            # 首字母大写，视为标识符（类名、构造函数等）
            token_type = TokenType.IDENTIFIER
        else:
            # 首字母小写，检查是否为关键字
            token_type = self.KEYWORDS.get(value.lower(), TokenType.IDENTIFIER)

        self.tokens.append(Token(token_type, value, start_line, start_column))

    def _peek(self, offset: int = 0) -> str:
        """
        查看当前字符（不消费）

        Args:
            offset: 偏移量（0 表示当前字符）

        Returns:
            字符，如果到达末尾返回空字符串
        """
        pos = self.pos + offset
        if pos >= len(self.source):
            return ''
        return self.source[pos]

    def _advance(self) -> str:
        """
        消费当前字符并前进

        Returns:
            被消费的字符
        """
        if self._is_at_end():
            return ''

        char = self.source[self.pos]
        self.pos += 1

        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def _is_at_end(self) -> bool:
        """检查是否到达源代码末尾"""
        return self.pos >= len(self.source)

    def _get_current_line(self) -> str:
        """获取当前行的完整文本（用于错误报告）"""
        if 1 <= self.line <= len(self.source_lines):
            return self.source_lines[self.line - 1]
        return ""
