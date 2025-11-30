# DSL v3.0 EBNF语法规范（Python化版本）

> **版本**: 3.0
> **目标受众**: Python程序员
> **设计原则**: 纯Python风格，93%语法兼容
> **状态**: 设计中
> **符号约定**: ISO/IEC 14977 EBNF
> **最后更新**: 2025-11-26

---

## 📐 EBNF符号约定

```
=       定义
|       或（选择）
[]      可选（0或1次）
{}      重复（0或多次）
()      分组
" "     终结符（字面量）
' '     终结符（字面量）
(* *)   注释
;       规则结束
```

---

## 🎯 顶层结构

```ebnf
(* 程序入口 *)
Program = { Statement } ;

(* 语句 *)
Statement = VariableDeclaration
          | Assignment
          | IfBlock
          | StepBlock
          | WhenBlock
          | ForEachLoop
          | NavigateStatement
          | WaitStatement
          | SelectStatement
          | ActionStatement
          | AssertStatement
          | CallStatement
          | ExtractStatement
          | LogStatement
          | ScreenshotStatement
          | GoStatement
          | ReloadStatement
          | NEWLINE
          ;
```

---

## 1️⃣ 变量与赋值

```ebnf
(* 1.1 Let声明 *)
VariableDeclaration = "let" Identifier "=" Expression NEWLINE ;

(* 1.2 Const声明 *)
ConstDeclaration = "const" Identifier "=" Expression NEWLINE ;

(* 1.3 赋值 *)
Assignment = Identifier "=" Expression NEWLINE ;

(* 标识符 *)
Identifier = Letter { Letter | Digit | "_" } ;
Letter = "a" | "b" | ... | "z" | "A" | "B" | ... | "Z" ;
Digit = "0" | "1" | ... | "9" ;
```

---

## 2️⃣ 控制流（v3.0核心变更）

### 2.1 Step块

```ebnf
(* v3.0: 删除 end step *)
StepBlock = "step" StringLiteral [ "with" "diagnosis" DiagnosisLevel ] ":"
            NEWLINE INDENT
            { Statement }
            DEDENT ;

DiagnosisLevel = "none" | "minimal" | "standard" | "detailed" | "verbose" | "debug" ;
```

**v2.0对比**:
```ebnf
(* v2.0: 使用 end step *)
StepBlock = "step" StringLiteral [ "with" "diagnosis" DiagnosisLevel ] ":"
            NEWLINE
            { Statement }
            "end" "step" NEWLINE ;
```

### 2.2 If-Else块

```ebnf
(* v3.0: 删除 end if *)
IfBlock = "if" Expression ":" NEWLINE INDENT
          { Statement }
          DEDENT
          { ElseIfClause }
          [ ElseClause ] ;

ElseIfClause = "else" "if" Expression ":" NEWLINE INDENT
               { Statement }
               DEDENT ;

ElseClause = "else" ":" NEWLINE INDENT
             { Statement }
             DEDENT ;
```

**v2.0对比**:
```ebnf
(* v2.0: 使用 end if *)
IfBlock = "if" Expression ":" NEWLINE
          { Statement }
          { ElseIfClause }
          [ ElseClause ]
          "end" "if" NEWLINE ;
```

### 2.3 When-Otherwise块

```ebnf
(* v3.0: 删除 end when, v3.1: 支持 OR 模式 *)
WhenBlock = "when" Expression ":" NEWLINE INDENT
            { WhenCase }
            [ OtherwiseCase ]
            DEDENT ;

(* WhenCase 支持任意表达式，v3.1: 支持 OR 模式（| 分隔多个值） *)
WhenCase = Expression { "|" Expression } ":" NEWLINE INDENT
           { Statement }
           DEDENT ;

OtherwiseCase = "otherwise" ":" NEWLINE INDENT
                { Statement }
                DEDENT ;
```

**v3.1 新增**: OR 模式示例
```python
when http_status:
    200 | 201 | 204:
        log "Success"
    400 | 401 | 403:
        log "Client Error"
    otherwise:
        log "Other Status"
```

**v2.0对比**:
```ebnf
(* v2.0: 使用 end when *)
WhenBlock = "when" Expression ":" NEWLINE
            { WhenCase }
            [ OtherwiseCase ]
            "end" "when" NEWLINE ;
```

### 2.4 For-Each循环

```ebnf
(* v3.0: 删除 end for, v4.0: 支持多变量解包 *)
ForEachLoop = "for" VariableList "in" Expression ":" NEWLINE INDENT
              { Statement }
              DEDENT ;

(* v4.0: 支持单变量或多变量（逗号分隔） *)
VariableList = Identifier { "," Identifier } ;
```

**Examples**:
```dsl
(* Single variable *)
for item in items:
    log item

(* Two variables - tuple unpacking *)
for key, value in pairs:
    log key, value

(* Three variables *)
for a, b, c in triplets:
    log a, b, c

(* enumerate() with multi-variable *)
for index, item in enumerate(items):
    log index, item
```

**v2.0对比**:
```ebnf
(* v2.0: 使用 end for *)
ForEachLoop = "for" Identifier "in" Expression ":" NEWLINE
              { Statement }
              "end" "for" NEWLINE ;
```

---

## 3️⃣ 导航

```ebnf
(* 3.1 Navigate To *)
NavigateStatement = "navigate" "to" Expression
                    [ "wait" "for" PageState ]
                    NEWLINE ;

PageState = "networkidle" | "domcontentloaded" | "load" ;

(* 3.2 Go Back/Forward *)
GoStatement = "go" ( "back" | "forward" ) NEWLINE ;

(* 3.3 Reload *)
ReloadStatement = "reload" NEWLINE ;
```

---

## 4️⃣ 等待

```ebnf
(* 4.1 Wait Duration *)
WaitDuration = "wait" [ "for" ] Number TimeUnit NEWLINE ;

TimeUnit = "s" | "ms" | "seconds" | "milliseconds" ;

(* 4.2 Wait Element *)
WaitElement = "wait" "for" "element" Selector
              [ "to" "be" ElementState ]
              [ "timeout" Number TimeUnit ]
              NEWLINE ;

ElementState = "visible" | "hidden" | "attached" | "detached" ;

(* 4.3 Wait Navigation *)
WaitNavigation = "wait" "for" "navigation"
                 [ "to" Expression ]
                 [ "wait" "for" PageState ]
                 [ "timeout" Number TimeUnit ]
                 NEWLINE ;

WaitStatement = WaitDuration | WaitElement | WaitNavigation ;
```

---

## 5️⃣ 选择

```ebnf
(* 5.1 Select Element *)
SelectStatement = "select" Selector
                  { "where" Condition }
                  NEWLINE ;

Condition = AttributeName ComparisonOp Expression ;
AttributeName = "text" | "value" | "class" | "id" | "name" | "href" | "src" | "alt" | "title" ;
ComparisonOp = "contains" | "equals" | "matches" ;

(* 5.2 Select Option *)
SelectOption = "select" "option" Expression "from" Selector NEWLINE ;
```

---

## 6️⃣ 动作

```ebnf
(* 6.1 Type *)
TypeAction = "type" Expression
             [ "into" Selector ]
             [ "slowly" | "fast" ]
             NEWLINE ;

(* 6.2 Click *)
ClickAction = "click" [ Selector ] NEWLINE ;

(* 6.3 Double Click *)
DoubleClickAction = "double" "click" [ Selector ] NEWLINE ;

(* 6.4 Right Click *)
RightClickAction = "right" "click" [ Selector ] NEWLINE ;

(* 6.5 Hover *)
HoverAction = "hover" [ "over" ] Selector NEWLINE ;

(* 6.6 Clear *)
ClearAction = "clear" [ Selector ] NEWLINE ;

(* 6.7 Press *)
PressAction = "press" KeyName NEWLINE ;
KeyName = "Enter" | "Tab" | "Escape" | "Space" | "ArrowUp" | "ArrowDown" | ... ;

(* 6.8 Scroll *)
ScrollAction = "scroll" "to" ScrollTarget NEWLINE ;
ScrollTarget = "top" | "bottom" | Selector | Number ;

(* 6.9 Check/Uncheck *)
CheckAction = ( "check" | "uncheck" ) Selector NEWLINE ;

(* 6.10 Upload *)
UploadAction = "upload" "file" Expression [ "to" Selector ] NEWLINE ;

ActionStatement = TypeAction
                | ClickAction
                | DoubleClickAction
                | RightClickAction
                | HoverAction
                | ClearAction
                | PressAction
                | ScrollAction
                | CheckAction
                | UploadAction
                ;
```

---

## 7️⃣ 断言

```ebnf
(* v2.0实际实现：通用表达式断言 *)
AssertStatement = "assert" Expression [ "," StringLiteral ] NEWLINE ;

(* v1.0特定语法（未实现） *)
AssertURL = "assert" "url" ( "contains" | "equals" | "matches" ) Expression NEWLINE ;
AssertElement = "assert" Selector ( "exists" | "visible" | "hidden" ) NEWLINE ;
AssertText = "assert" Selector "has" ( "text" | "value" ) Expression NEWLINE ;
AssertAttribute = "assert" Selector "has" Identifier Expression NEWLINE ;
```

---

## 8️⃣ 服务调用

```ebnf
CallStatement = "call" StringLiteral
                [ "with" ParameterList ]
                [ "into" Identifier ]
                NEWLINE ;

ParameterList = Parameter { "," Parameter } ;
Parameter = Identifier ":" Expression ;
```

---

## 9️⃣ 数据提取

```ebnf
ExtractStatement = "extract" ExtractType
                   [ "pattern" StringLiteral ]
                   "from" Selector
                   "into" Identifier
                   NEWLINE ;

ExtractType = "text" | "value" | ( "attr" StringLiteral ) ;
```

---

## 🔟 工具

```ebnf
(* 10.1 Log *)
LogStatement = "log" Expression NEWLINE ;

(* 10.2 Screenshot *)
ScreenshotStatement = "screenshot"
                      [ "of" Selector ]
                      [ "as" Expression ]
                      [ "fullpage" ]
                      NEWLINE ;
```

---

## 📈 表达式系统

### 优先级层次（9级）

```ebnf
(* Level 1: Logical or (最低) *)
Expression = LogicalAndExpr { "or" LogicalAndExpr } ;

(* Level 2: Logical and *)
LogicalAndExpr = LogicalNotExpr { "and" LogicalNotExpr } ;

(* Level 3: Logical not *)
LogicalNotExpr = [ "not" ] ComparisonExpr ;

(* Level 4: Comparison *)
ComparisonExpr = AdditiveExpr [ ComparisonOp AdditiveExpr ] ;
ComparisonOp = "==" | "!=" | ">" | "<" | ">=" | "<=" ;

(* Level 5: Additive *)
AdditiveExpr = MultiplicativeExpr { ( "+" | "-" ) MultiplicativeExpr } ;

(* Level 6: Multiplicative *)
MultiplicativeExpr = UnaryExpr { ( "*" | "/" | "%" ) UnaryExpr } ;

(* Level 7: Unary *)
UnaryExpr = [ "-" | "+" ] PostfixExpr ;

(* Level 8: Postfix *)
PostfixExpr = PrimaryExpr { PostfixOp } ;
PostfixOp = MemberAccess | ArrayAccess | FunctionCall ;

MemberAccess = "." Identifier ;
ArrayAccess = "[" Expression "]" ;
FunctionCall = "(" [ ArgumentList ] ")" ;

ArgumentList = Expression { "," Expression } ;

(* Level 9: Primary (最高) *)
PrimaryExpr = Literal
            | Identifier
            | SystemVariable
            | "(" Expression ")"
            ;
```

---

## 🎨 数据类型

```ebnf
Literal = StringLiteral
        | FStringLiteral
        | NumberLiteral
        | BooleanLiteral
        | NoneLiteral
        | ArrayLiteral
        | ObjectLiteral
        ;

(* String - Plain (v3.0: 不插值，无f前缀) *)
StringLiteral = '"' { Character } '"'
              | "'" { Character } "'" ;

(* String Interpolation - f-string (v3.0: 显式f前缀) *)
FStringLiteral = 'f"' { Character | InterpolationExpr } '"'
               | "f'" { Character | InterpolationExpr } "'" ;
InterpolationExpr = "{" Expression "}" ;

(* Number *)
NumberLiteral = [ "-" ] Integer [ "." Integer ] ;
Integer = Digit { Digit } ;

(* Boolean - Python风格 (v3.0: 首字母大写) *)
BooleanLiteral = "True" | "False" ;

(* None - Python风格 (v3.0: 而非null) *)
NoneLiteral = "None" ;

(* Array *)
ArrayLiteral = "[" [ Expression { "," Expression } [ "," ] ] "]" ;

(* Object *)
ObjectLiteral = "{" [ ObjectPair { "," ObjectPair } [ "," ] ] "}" ;
ObjectPair = ( Identifier | StringLiteral ) ":" Expression ;
```

---

## 🔧 系统变量（v3.0: 去掉$前缀，Python风格）

```ebnf
(* v3.0: 系统变量作为内置全局对象，无$前缀 *)
SystemVariable = Namespace "." Property ;

Namespace = "context" | "page" | "browser" | "env" | "config" ;

(* Context命名空间 *)
Property = "task_id" | "execution_id" | "start_time" | "step_name" | "status"
         (* Page命名空间 *)
         | "url" | "title" | "origin"
         (* Browser命名空间 *)
         | "name" | "version"
         (* Env/Config: 任意标识符 *)
         | Identifier
         ;

(* 示例 *)
(* page.url         - 当前页面URL *)
(* env.API_KEY      - 环境变量（类似Python的os.environ） *)
(* browser.name     - 浏览器名称 *)
(* config.base_url  - 配置项 *)
```

**v2.0对比**:
```ebnf
(* v2.0: 使用$前缀（Shell风格） *)
SystemVariable = "$" Namespace "." Property ;

(* v2.0示例: $page.url, $env.API_KEY *)
```

---

## 📚 内置函数（v2.0+）

```ebnf
(* Math命名空间 *)
MathFunction = "Math" "." MathMethod "(" [ ArgumentList ] ")" ;
MathMethod = "abs" | "round" | "ceil" | "floor" | "max" | "min"
           | "random" | "pow" | "sqrt" ;

(* Date命名空间 *)
DateFunction = "Date" "." DateMethod "(" [ ArgumentList ] ")" ;
DateMethod = "now" | "format" | "from_timestamp" ;

(* JSON命名空间 *)
JSONFunction = "JSON" "." JSONMethod "(" ArgumentList ")" ;
JSONMethod = "stringify" | "parse" ;

(* 全局函数 *)
GlobalFunction = GlobalMethod "(" ArgumentList ")" ;
GlobalMethod = "Number" | "String" | "Boolean" | "isNaN" | "isFinite" ;
```

---

## 🔤 选择器

```ebnf
Selector = Expression ;  (* 运行时求值为字符串 *)

(* 选择器语法（字符串内容，非DSL语法） *)
(* 支持CSS选择器和XPath *)
(*
CSS示例:
  "#id"
  ".class"
  "input[name='username']"
  "div > p:first-child"

XPath示例:
  "//div[@id='content']"
  "//button[contains(text(), 'Submit')]"
*)
```

---

## 🔢 词法Token（v3.0变更）

### 新增Token

```ebnf
(* v3.0新增：缩进token *)
INDENT = (* 缩进增加，由词法分析器生成 *) ;
DEDENT = (* 缩进减少，由词法分析器生成 *) ;
```

### 删除Token

```ebnf
(* v2.0 token（v3.0已删除） *)
(* END = "end" ; *)  (* 已删除 *)
```

### 保留Token

```ebnf
(* 基础token *)
NEWLINE = "\n" | "\r\n" ;
COLON = ":" ;
EOF = (* 文件结束 *) ;

(* 关键字token *)
LET = "let" ;
CONST = "const" ;
IF = "if" ;
ELSE = "else" ;
STEP = "step" ;
WHEN = "when" ;
OTHERWISE = "otherwise" ;
FOR = "for" ;
IN = "in" ;
(* ... 更多关键字 ... *)

(* 运算符token *)
PLUS = "+" ;
MINUS = "-" ;
STAR = "*" ;
SLASH = "/" ;
PERCENT = "%" ;
EQ = "==" ;
NE = "!=" ;
GT = ">" ;
LT = "<" ;
GE = ">=" ;
LE = "<=" ;
and = "and" ;
or = "or" ;
not = "not" ;
(* ... 更多运算符 ... *)
```

---

## 📝 注释（v3.0: Python风格）

```ebnf
(* 行注释 - 与Python相同 *)
LineComment = "#" { Character } NEWLINE ;

(* 块注释 - Python三引号风格 (v3.0变更) *)
BlockComment = '"""' { Character } '"""' ;

(* 元数据块 - v3.0已删除 *)
(* 不再支持 /**meta ... */ 语法 *)
(* 如需元数据，使用模块级变量或注释： *)
(*   # pass: example-test *)
(*   # desc: 测试示例 *)
```

**v2.0对比**:
```ebnf
(* v2.0: C风格块注释 *)
BlockComment = "/*" { Character } "*/" ;

(* v2.0: JavaDoc风格元数据块 *)
MetaBlock = "/**meta" NEWLINE
            { MetaField }
            "*/" NEWLINE ;
MetaField = MetaKey ":" { Character } NEWLINE ;
MetaKey = "pass" | "desc" | "symbol" ;
```

---

## 🔄 缩进语义（v3.0核心）

### 缩进栈算法

```
状态:
  indent_stack: List[Int]  (* 缩进栈，初始为[0] *)
  current_indent: Int      (* 当前行缩进量 *)

规则:
  1. 行首空格/Tab计数为缩进量
  2. 空行和纯注释行不影响缩进栈
  3. current_indent > stack.top:
       生成 INDENT token
       push current_indent 到栈
  4. current_indent < stack.top:
       循环 pop 直到 stack.top <= current_indent
       每次pop生成1个 DEDENT token
       如果 stack.top != current_indent: 报错
  5. current_indent == stack.top:
       无操作
  6. EOF: 循环pop所有剩余缩进，生成DEDENT
```

### 缩进验证

```
约束:
  1. 每级缩进必须是4的倍数
  2. 缩进增加必须正好+4
  3. 缩进减少必须匹配栈中某个历史缩进
  4. 禁止缩进跳跃（0→8跳过4）
  5. 同一文件统一使用空格或Tab
```

---

## ✅ 形式化验证性质

### 块结构完整性

```
∀ block: Block,
  block.start ⟹ block.has_colon ∧ block.has_indent
  block.end ⟹ block.has_dedent

翻译：
  每个块开始必须有冒号和INDENT
  每个块结束必须有DEDENT
```

### 缩进一致性

```
∀ stmt₁, stmt₂ ∈ same_block,
  indent(stmt₁) = indent(stmt₂)

翻译：
  同一块内所有语句缩进相同
```

### 嵌套正确性

```
∀ block_outer, block_inner,
  block_inner ⊆ block_outer ⟹
  indent(block_inner) = indent(block_outer) + 4

翻译：
  内层块缩进比外层多4
```

---

## 📊 EBNF vs v2.0对比总结

### 控制流变更（缩进机制）

| 语法元素 | v2.0 | v3.0 | 变更 |
|---------|------|------|------|
| Step块结束 | `end step` | DEDENT | 删除关键字 |
| If块结束 | `end if` | DEDENT | 删除关键字 |
| When块结束 | `end when` | DEDENT | 删除关键字 |
| For块结束 | `end for` | DEDENT | 删除关键字 |
| END token | 定义 | 删除 | 词法层删除 |
| INDENT token | 无 | 新增 | 词法层新增 |
| DEDENT token | 无 | 新增 | 词法层新增 |
| 缩进语义 | 无 | 强制4空格 | 语义层新增 |

### Python对齐变更（v3.0核心改进）

| 语法元素 | v2.0 (非Python) | v3.0 (Python风格) | 对齐度 |
|---------|----------------|------------------|--------|
| 布尔字面量 | `true`, `false` | `True`, `False` | ✅ 100% |
| null字面量 | `null` | `None` | ✅ 100% |
| 系统变量 | `$page.url` | `page.url` | ✅ 去掉Shell风格 |
| 字符串插值 | `"text {x}"` 自动 | `f"text {x}"` 显式 | ✅ 100% |
| 块注释 | `/* ... */` | `""" ... """` | ✅ 100% |
| 元数据块 | `/**meta ... */` | **已删除** | ✅ 无JavaDoc风格 |
| 逻辑运算符 | `and/or/not` | `and/or/not` | ✅ 100% (已有) |
| 冒号标记 | `:` | `:` | ✅ 100% (已有) |
| 行注释 | `#` | `#` | ✅ 100% (已有) |

**总体Python对齐度**: 93%+

---

## 🔍 完整示例的EBNF推导（v3.0 Python风格）

### 示例程序

```dsl
step "用户登录":
    if user.active:
        log f"登录用户: {user.name}"
        let success = True
    else:
        log "用户未激活"
        let success = False
```

### EBNF推导

```
Program
└── Statement
    └── StepBlock
        ├── "step"
        ├── StringLiteral("用户登录")
        ├── ":"
        ├── NEWLINE
        ├── INDENT
        ├── Statement
        │   └── IfBlock
        │       ├── "if"
        │       ├── Expression
        │       │   └── MemberAccess
        │       │       ├── Identifier(user)
        │       │       ├── "."
        │       │       └── Identifier(active)
        │       ├── ":"
        │       ├── NEWLINE
        │       ├── INDENT
        │       ├── Statement
        │       │   └── LogStatement
        │       │       ├── "log"
        │       │       └── FStringLiteral(f"登录用户: {user.name}")  ⬅ f-string
        │       ├── Statement
        │       │   └── VariableDeclaration
        │       │       ├── "let"
        │       │       ├── Identifier(success)
        │       │       ├── "="
        │       │       └── BooleanLiteral(True)  ⬅ True (Python风格)
        │       ├── DEDENT
        │       ├── ElseClause
        │       │   ├── "else"
        │       │   ├── ":"
        │       │   ├── NEWLINE
        │       │   ├── INDENT
        │       │   ├── Statement
        │       │   │   └── LogStatement
        │       │   │       ├── "log"
        │       │   │       └── StringLiteral("用户未激活")
        │       │   ├── Statement
        │       │   │   └── VariableDeclaration
        │       │   │       ├── "let"
        │       │   │       ├── Identifier(success)
        │       │   │       ├── "="
        │       │   │       └── BooleanLiteral(False)  ⬅ False (Python风格)
        │       │   └── DEDENT
        └── DEDENT
```

**关键点**:
- ✅ 使用 `True`/`False` 而非 `true`/`false`
- ✅ 使用 `f"text {expr}"` 而非 `"text {expr}"`
- ✅ 使用 `user.active` 而非 `$user.active`
- ✅ 块结束用 DEDENT 而非 `end` 关键字

---

## 📖 参考文档

- ISO/IEC 14977:1996 - EBNF标准
- Python Language Reference - Lexical Analysis (Python 3.12)
- PEP 8 - Style Guide for Python Code (缩进规范)
- `DESIGN-V3.md` - v3.0完整语法规范（Python化版本）
- `V3-EXAMPLES.flow` - 完整示例集（Python风格）
- `PYTHON-ALIGNMENT-REVIEW.md` - Python对齐度审查报告

---

## 🔧 实现检查清单

### Lexer实现（lexer_v3.py）

**Python对齐token**:
- [ ] `True`/`False` token（首字母大写）
- [ ] `None` token（而非null）
- [ ] `f"..."` f-string解析（显式f前缀）
- [ ] `"""..."""` 块注释解析（三引号）
- [ ] 删除 `$` token（系统变量无前缀）
- [ ] 删除 `/**meta */` 解析（元数据块已删除）

**缩进机制token**:
- [ ] INDENT token生成
- [ ] DEDENT token生成
- [ ] 删除 END token

### Parser实现（parser_v3.py）

**Python对齐语法**:
- [ ] 布尔字面量: `True`/`False`
- [ ] Null字面量: `None`
- [ ] f-string解析: `f"text {expr}"` 插值
- [ ] 普通字符串: `"text"` 不插值（无f）
- [ ] 系统变量: `page.url` 而非 `$page.url`
- [ ] 块注释: `"""..."""`
- [ ] 删除元数据块解析

**缩进机制**:
- [ ] 基于INDENT/DEDENT的块解析
- [ ] 删除所有END token依赖

---

**维护者**: DSL v3.0设计组
**最后更新**: 2025-11-26
**状态**: 设计阶段（Phase 0.1 完成，等待实现）
**Python对齐度**: 93%+

---

**重要说明**:
- 本EBNF规范必须与 `DESIGN-V3.md` 和 `V3-EXAMPLES.flow` 保持同步
- 任何语法变更都应同时更新三份文档
- v3.0完全不兼容v2.0，这是破坏性变更
- 设计定位：**为Python程序员编写的DSL**
