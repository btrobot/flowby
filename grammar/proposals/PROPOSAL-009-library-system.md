# Grammar Proposal #009: Library System (模块化代码复用)

> **提案编号**: #009
> **提出日期**: 2025-11-29
> **提出人**: Core Team
> **状态**: ✅ Approved
> **目标版本**: 5.0.0
> **影响级别**: MINOR (向后兼容的新功能)

---

## 📋 提案摘要

引入 library 系统,通过 `library` 声明、`export` 关键字和 `import` 语句,实现模块化代码复用和命名空间隔离,解决大型 flow 文件中函数库混乱和代码重复的问题。

---

## 🎯 动机和背景

### 问题描述

当前 DSL 已支持函数定义(v4.0+),但缺乏模块化机制,导致：

**示例场景 - 当前 600+ 行的 flow 文件**:
```flow
# factory_ai_registration_v4.3_refactored.flow (1438 tokens, 600+ 行)

# 40+ 行工具函数定义
function log_phase_start(phase_num, phase_name):
    log "阶段 [{phase_num}]: {phase_name}"
    log "--------------------------------------------------"

function validate_not_empty(field_name, value):
    if value == "":
        abort_workflow("验证失败: {field_name} 不能为空")
    end if

function generate_random_number(min_val, max_val):
    # ... 10 行实现
    return random_num

# ... 更多 20+ 个工具函数

# 400+ 行业务逻辑
step "阶段 1: 数据准备":
    log_phase_start(1, "数据准备")  # 使用工具函数
    # ...
end step
```

**问题**:
1. ❌ **命名空间污染**: 所有函数在全局作用域,容易命名冲突
2. ❌ **代码重复**: 多个 flow 文件需要复制粘贴相同的工具函数
3. ❌ **难以维护**: 工具函数与业务逻辑混在一起,600+ 行难以导航
4. ❌ **缺乏复用**: 无法在多个项目间共享通用函数库
5. ❌ **缺乏封装**: 无法区分公共 API 和内部实现

**实际案例**:
- `factory_ai_registration_v4.3_refactored.flow`: 600+ 行,包含 25+ 个工具函数
- 多个 flow 文件重复定义 `log_phase_start`, `validate_not_empty` 等函数
- 工具函数修改需要同步更新所有使用它的文件

### 为什么现有功能不够？

- ❌ **函数 (v4.0+)**: 只能在当前文件定义,无法跨文件复用
- ❌ **注释分隔**: 无法真正隔离代码,只是视觉上的组织
- ❌ **复制粘贴**: 导致代码重复和维护困难

### 实际需求场景

1. **工具函数库**: 将 `log_*`, `validate_*`, `generate_*` 等函数提取到 `libs/utils.flow`
2. **业务函数库**: 将特定领域的函数提取到 `libs/ai_registration.flow`
3. **跨项目复用**: 创建通用的 `libs/logging.flow`, `libs/validation.flow` 供多个项目使用
4. **清晰的 API**: 通过 `export` 明确哪些函数是公共 API,哪些是内部实现

---

## 💡 提议的解决方案

### 语法设计

#### 基本形式

```bnf
library_file ::= "library" identifier NEWLINE
                 [ const_definition | function_definition | export_statement ]*

export_statement ::= "export" ( const_definition | function_definition )

import_statement ::= "import" identifier "from" string_literal
                   | "from" string_literal "import" identifier ( "," identifier )*
```

#### 具体语法

**库文件 (library file)**:
```flow
library logging

# 导出的公共 API
export const LOG_LEVEL_DEBUG = "debug"
export const LOG_LEVEL_INFO = "info"

export function log_phase_start(phase_num, phase_name):
    """记录阶段开始"""
    log info "阶段 [{phase_num}]: {phase_name}"
    log info "--------------------------------------------------"

export function log_phase_end(phase_num, phase_name):
    """记录阶段结束"""
    log success "阶段 [{phase_num}] 完成: {phase_name}"

# 私有辅助函数 (不导出)
function _format_timestamp():
    """内部函数,不对外暴露"""
    return "2025-11-29 10:00:00"
```

**主流程文件 (flow file)**:
```flow
# 导入整个模块
import logging from "libs/logging.flow"

step "开始":
    logging.log_phase_start(1, "数据准备")
    # ...
    logging.log_phase_end(1, "数据准备")
end step
```

**或使用 from-import 语法**:
```flow
# 导入特定成员
from "libs/logging.flow" import log_phase_start, log_phase_end

step "开始":
    log_phase_start(1, "数据准备")  # 直接使用,无需模块前缀
    # ...
    log_phase_end(1, "数据准备")
end step
```

### 详细说明

#### 参数说明

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| library name | identifier | ✅ | 库的名称,必须与文件名匹配 |
| module alias | identifier | ✅ | 导入后的模块别名 |
| file path | string | ✅ | 相对路径,基于当前文件所在目录 |
| member names | identifier list | ✅ | from-import 时指定要导入的成员名 |

#### 选项说明

- **library 声明**: 必须在文件首行(注释和空行除外)
- **export 关键字**: 显式标记导出的函数/常量
- **路径解析**:
  - 相对路径基于当前文件所在目录
  - 支持 `libs/`, `../common/` 等相对路径
  - 不支持绝对路径(安全考虑)

### 使用示例

#### 示例 1: 基本用法 - 日志库

**库文件: `libs/logging.flow`**:
```flow
/**meta
desc: 通用日志工具库
grammar-version: 5.0.0
*/

library logging

export function log_phase_start(phase_num, phase_name):
    """记录阶段开始"""
    log info "阶段 [{phase_num}]: {phase_name}"
    log info "--------------------------------------------------"

export function log_phase_end(phase_num, phase_name):
    """记录阶段结束"""
    log success "阶段 [{phase_num}] 完成: {phase_name}"
    log info "=================================================="

export function log_error_with_screenshot(error_msg):
    """记录错误并截图"""
    log error "错误: {error_msg}"
    screenshot as "error-{error_msg}"

# 内部辅助函数 (不导出)
function _get_timestamp():
    return "2025-11-29"
```

**主流程文件: `flows/registration.flow`**:
```flow
/**meta
desc: 用户注册流程
*/

import logging from "libs/logging.flow"

step "阶段 1: 数据准备":
    logging.log_phase_start(1, "数据准备")

    navigate to "https://example.com/register"

    logging.log_phase_end(1, "数据准备")
end step

step "阶段 2: 填写表单":
    logging.log_phase_start(2, "填写表单")

    try:
        fill "#username" with "testuser"
        fill "#email" with "test@example.com"
    catch error:
        logging.log_error_with_screenshot(error.message)
        exit 1
    end try

    logging.log_phase_end(2, "填写表单")
end step
```

**预期输出**:
```
[INFO] 阶段 [1]: 数据准备
[INFO] --------------------------------------------------
...
[INFO] ✓ 阶段 [1] 完成: 数据准备
[INFO] ==================================================
```

#### 示例 2: 验证函数库

**库文件: `libs/validation.flow`**:
```flow
library validation

export function validate_not_empty(field_name, value):
    """验证字段非空"""
    if value == "":
        log error "验证失败: {field_name} 不能为空"
        exit 1
    end if
    log success "✓ {field_name} 验证通过"

export function validate_email(email):
    """验证邮箱格式"""
    # 简单的邮箱验证逻辑
    if not email contains "@":
        log error "验证失败: 邮箱格式不正确"
        exit 1
    end if
    log success "✓ 邮箱格式验证通过"

export function validate_length(field_name, value, min_len, max_len):
    """验证字符串长度"""
    let length = value.length
    if length < min_len or length > max_len:
        log error "验证失败: {field_name} 长度必须在 {min_len}-{max_len} 之间"
        exit 1
    end if
    log success "✓ {field_name} 长度验证通过"
```

**使用: `flows/user_registration.flow`**:
```flow
from "libs/validation.flow" import validate_not_empty, validate_email, validate_length

let username = "testuser"
let email = "test@example.com"

validate_not_empty("用户名", username)
validate_length("用户名", username, 3, 20)
validate_not_empty("邮箱", email)
validate_email(email)

log info "所有验证通过,开始注册"
```

#### 示例 3: 高级用法 - 多库组合

**库文件: `libs/random_utils.flow`**:
```flow
library random_utils

export function generate_random_number(min_val, max_val):
    """生成随机数"""
    # 简化的随机数生成逻辑
    return min_val + 42  # 示例实现

export function generate_random_string(length):
    """生成随机字符串"""
    return "random_" + length
```

**主流程: `flows/factory_ai_registration.flow` (优化后)**:
```flow
/**meta
desc: 工厂 AI 注册流程 - 使用模块化设计
grammar-version: 5.0.0
*/

# 导入多个库
import logging from "libs/logging.flow"
from "libs/validation.flow" import validate_not_empty, validate_email
from "libs/random_utils.flow" import generate_random_number

# ============================================================
# 配置
# ============================================================
const FACTORY_NAME = "深圳智能制造示范工厂"
const PLATFORM_URL = "https://ai-factory.example.com"

# ============================================================
# 主流程 (业务逻辑清晰,工具函数已模块化)
# ============================================================

step "阶段 1: 数据准备":
    logging.log_phase_start(1, "数据准备")

    let factory_code = "F" + generate_random_number(1000, 9999)
    let admin_email = "admin@factory.com"

    validate_not_empty("工厂代码", factory_code)
    validate_email(admin_email)

    logging.log_phase_end(1, "数据准备")
end step

step "阶段 2: 系统注册":
    logging.log_phase_start(2, "系统注册")

    navigate to PLATFORM_URL + "/register"
    fill "#factory_code" with factory_code
    fill "#factory_name" with FACTORY_NAME

    logging.log_phase_end(2, "系统注册")
end step
```

**对比效果**:
- **优化前**: 600+ 行 (工具函数 + 业务逻辑混在一起)
- **优化后**:
  - 主流程: ~100 行 (只包含业务逻辑)
  - `libs/logging.flow`: ~30 行
  - `libs/validation.flow`: ~40 行
  - `libs/random_utils.flow`: ~20 行
  - **总计**: ~190 行,但可读性和可维护性大幅提升

#### 示例 4: 库之间的依赖

**基础库: `libs/core.flow`**:
```flow
library core

export function get_timestamp():
    """获取时间戳"""
    return "2025-11-29 10:00:00"

export const APP_VERSION = "5.0.0"
```

**高级库: `libs/advanced_logging.flow`**:
```flow
library advanced_logging

# 库可以导入其他库
import core from "core.flow"

export function log_with_timestamp(message):
    """带时间戳的日志"""
    let timestamp = core.get_timestamp()
    log info "[{timestamp}] {message}"

export function log_version():
    """记录版本信息"""
    log info "应用版本: {core.APP_VERSION}"
```

**主流程使用**:
```flow
from "libs/advanced_logging.flow" import log_with_timestamp, log_version

log_version()
log_with_timestamp("流程开始")
```

---

## 🔍 语义和行为

### 执行语义

#### 1. Library 文件解析阶段

**加载时机**: 当 import 语句被解析时,立即加载对应的库文件

**加载过程**:
1. 解析库文件的 `library` 声明,验证名称匹配
2. 解析所有 `const` 和 `function` 定义
3. 收集所有 `export` 标记的成员
4. 验证约束条件:
   - ✅ 只能包含 `const` 和 `function` 定义
   - ❌ 不能包含 `step`, `log`, `wait` 等可执行语句
   - ❌ 不能包含 `navigate`, `click` 等操作语句

**库文件约束**:
```flow
library my_lib

# ✅ 允许: 常量定义
export const MAX_RETRIES = 3

# ✅ 允许: 函数定义
export function retry_operation():
    return "ok"

# ❌ 禁止: 可执行语句
log "This is not allowed"  # 解析错误

# ❌ 禁止: Step 语句
step "test":  # 解析错误
    navigate to "..."
end step

# ❌ 禁止: 直接操作
wait 1 s  # 解析错误
```

#### 2. Import 语句执行阶段

**Import 语法 1: 模块导入**:
```flow
import logging from "libs/logging.flow"
```

**行为**:
1. 加载 `libs/logging.flow` (相对于当前文件)
2. 创建命名空间对象 `logging`
3. 将所有 `export` 的成员添加到 `logging` 对象
4. 在当前作用域注册 `logging` 标识符

**访问语法**: `logging.log_phase_start(1, "test")`

**Import 语法 2: From-Import**:
```flow
from "libs/logging.flow" import log_phase_start, log_phase_end
```

**行为**:
1. 加载 `libs/logging.flow`
2. 检查 `log_phase_start` 和 `log_phase_end` 是否被 export
3. 在当前作用域直接注册这两个标识符(无命名空间前缀)

**访问语法**: `log_phase_start(1, "test")` (直接使用,无前缀)

#### 3. 模块缓存机制

**缓存策略**:
- 每个库文件在同一次执行中只加载一次
- 使用绝对路径作为缓存键
- 后续 import 直接返回缓存的模块对象

**示例**:
```flow
# file1.flow
import logging from "libs/logging.flow"  # 第一次加载

# file2.flow (被 file1 导入)
import logging from "logging.flow"  # 命中缓存,不重复加载
```

#### 4. 循环导入检测

**检测机制**: 维护导入栈,检测循环依赖

**示例**:
```flow
# a.flow
library a
import b from "b.flow"  # 导入 b

# b.flow
library b
import a from "a.flow"  # 导入 a -> 检测到循环依赖
```

**错误信息**:
```
[ERROR] 循环导入检测:
  a.flow -> b.flow -> a.flow
  不允许循环依赖
```

### 作用域规则

#### 库文件作用域

**独立作用域**: 每个库文件拥有独立的全局作用域

**示例**:
```flow
# libs/a.flow
library a
let internal_var = 42  # 库 a 的内部变量
export function get_value():
    return internal_var

# libs/b.flow
library b
let internal_var = 99  # 库 b 的内部变量 (不冲突)
export function get_value():
    return internal_var

# main.flow
import a from "libs/a.flow"
import b from "libs/b.flow"

log a.get_value()  # 输出: 42
log b.get_value()  # 输出: 99
```

#### Export 可见性

**规则**:
- 只有 `export` 标记的成员对外可见
- 未 export 的成员仅在库内部可见

**示例**:
```flow
# libs/utils.flow
library utils

export function public_func():
    return _private_func() + 10

function _private_func():  # 未 export,外部不可访问
    return 42

# main.flow
import utils from "libs/utils.flow"

log utils.public_func()    # ✅ 正确: 60
log utils._private_func()  # ❌ 错误: _private_func 未导出
```

### 错误处理

| 错误情况 | 行为 | 示例 |
|---------|------|------|
| 库文件不存在 | 抛出 FileNotFoundError | `import foo from "libs/missing.flow"` |
| library 名称不匹配 | 抛出 LibraryNameMismatchError | 文件名 `a.flow` 但声明 `library b` |
| 导入的成员未 export | 抛出 ImportError | `from "lib.flow" import private_func` |
| 库文件包含可执行语句 | 抛出 LibraryConstraintViolation | library 文件中包含 `log`, `step` |
| 循环导入 | 抛出 CircularImportError | A → B → A |
| 重复导入相同名称 | 抛出 NameConflictError | `import a; import a` |
| 路径解析失败 | 抛出 PathResolutionError | 使用绝对路径或 `..` 超出项目根 |

---

## 📊 影响分析

### 版本影响

- [x] **MINOR** (向后兼容的新功能)
  - 新增 library/export/import 语句
  - 不影响现有代码(无 import 语句的文件正常运行)
  - 纯新增功能,无破坏性变更

- [ ] MAJOR (不兼容变更)
- [ ] PATCH (bug 修复)

### 兼容性

#### 向后兼容性

- ✅ **完全向后兼容**
- **原因**:
  - 现有 flow 文件无需修改,继续正常运行
  - library/export/import 是新增关键字,不影响现有语法
  - 不修改任何现有语句的语义

#### 现有功能影响

| 现有功能 | 影响 | 说明 |
|---------|------|------|
| 函数定义 (v4.0+) | 扩展 | 可以在 library 中定义并 export |
| 常量定义 (v3.0+) | 扩展 | 可以在 library 中定义并 export |
| 作用域系统 | 扩展 | 新增库作用域和模块命名空间 |
| 符号表 | 扩展 | 需要支持模块对象和成员访问 |
| 所有其他语句 | 无 | 不受影响 |

### 学习曲线

- **新手**: 中等
  - 需要理解模块化概念
  - 但语法简单直观,类似 Python/JavaScript
  - 文档和示例充足

- **现有用户**: 容易
  - 熟悉其他语言模块系统的开发者很容易理解
  - 可选功能,不强制使用
  - 逐步迁移,先在大型项目中使用

### 语法复杂度

**当前状态** (v4.3.0):
```
语句类型: 27/30
表达式层次: 9/10
关键字: 88/100
```

**添加后** (v5.0.0):
```
语句类型: 31/35  (+4: library declaration, export, import, member access - 在限制内 ✅)
表达式层次: 10/10 (+1: member access expression - 已达上限 ⚠️)
关键字: 91/100   (+3: library, export, import, from - 还有 9 个空位)
```

**评估**: ✅ 在调整后的限制内

**详细分析**:
- **语句类型**: 31/35 = 88.6% (还有 4 个空位) ✅
  - v5.0 将限制从 30 提升到 35
  - 为未来特性预留空间
- **表达式层次**: 10/10 = 100% (已达上限) ⚠️
  - 成员访问表达式是第 10 层
  - 未来新特性如需新增表达式层级需谨慎评估
- **关键字**: 91/100 = 91% (还有 9 个空位) ✅
  - 新增 4 个关键字: library, export, import, from
  - 仍有较大余地

---

## 🛠️ 实现方案

### Lexer 变更

**新增 Token**:
```python
class TokenType(Enum):
    # ... 现有 tokens
    LIBRARY = "LIBRARY"     # library 关键字
    EXPORT = "EXPORT"       # export 关键字
    IMPORT = "IMPORT"       # import 关键字
    FROM = "FROM"           # from 关键字
    DOT = "DOT"             # . (成员访问)
```

**关键字映射**:
```python
KEYWORDS = {
    # ... 现有关键字
    "library": TokenType.LIBRARY,
    "export": TokenType.EXPORT,
    "import": TokenType.IMPORT,
    "from": TokenType.FROM,
}
```

**实现难度**: ✅ 简单 (0.5 天)

### Parser 变更

#### 新增 AST 节点

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class LibraryDeclaration(ASTNode):
    """Library 声明语句"""
    name: str
    line: int = 0

@dataclass
class ExportStatement(ASTNode):
    """Export 语句"""
    target: ASTNode  # FunctionDeclaration 或 ConstDeclaration
    line: int = 0

@dataclass
class ImportStatement(ASTNode):
    """Import 语句"""
    module_alias: str        # 模块别名
    module_path: str         # 文件路径
    members: Optional[List[str]] = None  # from-import 时的成员列表
    line: int = 0

@dataclass
class MemberAccessExpression(Expression):
    """成员访问表达式: module.member"""
    object: Expression       # 对象表达式
    member: str             # 成员名称
    line: int = 0
```

#### Parser 方法

**解析 Library 声明**:
```python
def _parse_library_declaration(self) -> LibraryDeclaration:
    """
    解析 library 声明

    语法:
        library identifier
    """
    line = self._peek().line
    self._consume(TokenType.LIBRARY, "期望 'library'")

    name_token = self._consume(TokenType.IDENTIFIER, "期望库名称")
    name = name_token.value

    # 验证 library 声明必须在文件开头
    if len(self.ast.statements) > 0:
        raise ParseError(f"library 声明必须在文件开头 (行 {line})")

    return LibraryDeclaration(name=name, line=line)
```

**解析 Export 语句**:
```python
def _parse_export_statement(self) -> ExportStatement:
    """
    解析 export 语句

    语法:
        export const NAME = value
        export function name(...): ... end function
    """
    line = self._peek().line
    self._consume(TokenType.EXPORT, "期望 'export'")

    # export 后面必须跟 const 或 function
    if self._check(TokenType.CONST):
        target = self._parse_const_declaration()
    elif self._check(TokenType.FUNCTION):
        target = self._parse_function_declaration()
    else:
        raise ParseError(f"export 后面必须是 const 或 function (行 {line})")

    return ExportStatement(target=target, line=line)
```

**解析 Import 语句**:
```python
def _parse_import_statement(self) -> ImportStatement:
    """
    解析 import 语句

    语法 1: import alias from "path"
    语法 2: from "path" import name1, name2, ...
    """
    line = self._peek().line

    # 语法 1: import alias from "path"
    if self._match(TokenType.IMPORT):
        alias_token = self._consume(TokenType.IDENTIFIER, "期望模块别名")
        alias = alias_token.value

        self._consume(TokenType.FROM, "期望 'from'")

        path_token = self._consume(TokenType.STRING, "期望文件路径")
        path = path_token.value

        return ImportStatement(
            module_alias=alias,
            module_path=path,
            members=None,
            line=line
        )

    # 语法 2: from "path" import name1, name2, ...
    elif self._match(TokenType.FROM):
        path_token = self._consume(TokenType.STRING, "期望文件路径")
        path = path_token.value

        self._consume(TokenType.IMPORT, "期望 'import'")

        # 解析成员列表
        members = []
        members.append(self._consume(TokenType.IDENTIFIER, "期望成员名称").value)

        while self._match(TokenType.COMMA):
            members.append(self._consume(TokenType.IDENTIFIER, "期望成员名称").value)

        return ImportStatement(
            module_alias=None,
            module_path=path,
            members=members,
            line=line
        )

    else:
        raise ParseError(f"期望 'import' 或 'from' (行 {line})")
```

**解析成员访问表达式**:
```python
def _parse_postfix_expression(self) -> Expression:
    """
    解析后缀表达式 (包括成员访问)

    语法:
        primary_expression ( "." identifier )*
    """
    expr = self._parse_primary_expression()

    while self._match(TokenType.DOT):
        line = self._previous().line
        member_token = self._consume(TokenType.IDENTIFIER, "期望成员名称")
        member = member_token.value

        expr = MemberAccessExpression(
            object=expr,
            member=member,
            line=line
        )

    return expr
```

**实现难度**: ⏱️ 中等 (2-3 天)
- 需要修改语句解析主循环
- 需要添加表达式层级 (成员访问)
- 需要完善的错误检查

### Module System 实现

**新增模块: `src/registration_system/dsl/module_system.py`**:

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set
import os

@dataclass
class Module:
    """模块对象"""
    name: str                          # 模块名称
    path: str                          # 文件路径
    exports: Dict[str, any]            # 导出的成员 {name: value}
    scope: Dict[str, any]              # 模块作用域

class ModuleLoader:
    """模块加载器"""

    def __init__(self, parser, interpreter):
        self.parser = parser
        self.interpreter = interpreter
        self.module_cache: Dict[str, Module] = {}  # 路径 -> 模块对象
        self.loading_stack: List[str] = []         # 导入栈 (循环检测)

    def load_module(self, module_path: str, current_file_path: str) -> Module:
        """
        加载模块

        Args:
            module_path: 相对路径 (如 "libs/logging.flow")
            current_file_path: 当前文件的绝对路径

        Returns:
            Module 对象

        Raises:
            FileNotFoundError: 文件不存在
            CircularImportError: 循环导入
            LibraryConstraintViolation: 库文件约束违反
        """
        # 1. 解析绝对路径
        abs_path = self._resolve_path(module_path, current_file_path)

        # 2. 检查缓存
        if abs_path in self.module_cache:
            return self.module_cache[abs_path]

        # 3. 检查循环导入
        if abs_path in self.loading_stack:
            raise CircularImportError(
                f"检测到循环导入: {' -> '.join(self.loading_stack)} -> {abs_path}"
            )

        # 4. 加载文件
        self.loading_stack.append(abs_path)

        try:
            module = self._load_and_parse(abs_path)
            self.module_cache[abs_path] = module
            return module
        finally:
            self.loading_stack.pop()

    def _resolve_path(self, module_path: str, current_file_path: str) -> str:
        """
        解析模块路径

        Args:
            module_path: 相对路径 (如 "libs/logging.flow")
            current_file_path: 当前文件绝对路径

        Returns:
            模块文件的绝对路径
        """
        current_dir = Path(current_file_path).parent
        target_path = (current_dir / module_path).resolve()

        if not target_path.exists():
            raise FileNotFoundError(f"模块文件不存在: {module_path} (解析为 {target_path})")

        return str(target_path)

    def _load_and_parse(self, abs_path: str) -> Module:
        """
        加载并解析库文件

        Args:
            abs_path: 库文件的绝对路径

        Returns:
            Module 对象

        Raises:
            LibraryNameMismatchError: library 名称与文件名不匹配
            LibraryConstraintViolation: 库文件包含非法语句
        """
        # 读取文件
        with open(abs_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # 解析 AST
        ast = self.parser.parse(source_code, file_path=abs_path)

        # 验证第一条语句是 library 声明
        if not ast.statements or not isinstance(ast.statements[0], LibraryDeclaration):
            raise LibraryConstraintViolation(
                f"库文件必须以 'library' 声明开头: {abs_path}"
            )

        library_decl = ast.statements[0]
        module_name = library_decl.name

        # 验证 library 名称与文件名匹配 (可选)
        file_stem = Path(abs_path).stem
        if module_name != file_stem:
            raise LibraryNameMismatchError(
                f"library 名称 '{module_name}' 与文件名 '{file_stem}' 不匹配"
            )

        # 验证库文件约束
        self._validate_library_constraints(ast)

        # 执行库文件 (收集 exports)
        exports = self._execute_library(ast, abs_path)

        return Module(
            name=module_name,
            path=abs_path,
            exports=exports,
            scope={}  # 库的内部作用域
        )

    def _validate_library_constraints(self, ast):
        """
        验证库文件约束

        库文件只能包含:
        - library 声明
        - const 定义
        - function 定义
        - export 语句

        不能包含:
        - step 语句
        - 可执行语句 (log, wait, navigate, click, 等)
        """
        forbidden_types = [
            'StepBlock', 'LogStatement', 'WaitStatement',
            'NavigateStatement', 'ClickStatement', 'FillStatement',
            'AssertStatement', 'ExitStatement'
        ]

        for stmt in ast.statements:
            stmt_type = type(stmt).__name__

            # 跳过允许的语句
            if stmt_type in ['LibraryDeclaration', 'ConstDeclaration',
                             'FunctionDeclaration', 'ExportStatement']:
                continue

            # 检查禁止的语句
            if stmt_type in forbidden_types:
                raise LibraryConstraintViolation(
                    f"库文件不能包含 {stmt_type} (行 {stmt.line})"
                )

    def _execute_library(self, ast, abs_path: str) -> Dict[str, any]:
        """
        执行库文件,收集 export 的成员

        Args:
            ast: 库文件的 AST
            abs_path: 文件路径

        Returns:
            exports 字典 {name: value}
        """
        exports = {}

        # 创建库的独立作用域
        library_scope = {}

        for stmt in ast.statements:
            if isinstance(stmt, LibraryDeclaration):
                continue

            elif isinstance(stmt, ExportStatement):
                # 执行被 export 的语句
                target = stmt.target

                if isinstance(target, ConstDeclaration):
                    # 执行常量定义
                    name = target.name
                    value = self.interpreter.evaluate(target.value)
                    library_scope[name] = value
                    exports[name] = value

                elif isinstance(target, FunctionDeclaration):
                    # 定义函数
                    name = target.name
                    func_obj = self.interpreter.create_function(target)
                    library_scope[name] = func_obj
                    exports[name] = func_obj

            elif isinstance(stmt, ConstDeclaration):
                # 非 export 的常量 (仅库内可见)
                name = stmt.name
                value = self.interpreter.evaluate(stmt.value)
                library_scope[name] = value

            elif isinstance(stmt, FunctionDeclaration):
                # 非 export 的函数 (仅库内可见)
                name = stmt.name
                func_obj = self.interpreter.create_function(stmt)
                library_scope[name] = func_obj

        return exports

# 自定义异常
class CircularImportError(Exception):
    pass

class LibraryNameMismatchError(Exception):
    pass

class LibraryConstraintViolation(Exception):
    pass
```

**实现难度**: ⏱️ 困难 (4-5 天)
- 需要实现完整的模块加载系统
- 路径解析、缓存、循环检测
- 独立作用域管理
- 大量边界情况处理

### Interpreter 变更

**处理 Import 语句**:
```python
def _execute_import(self, statement: ImportStatement) -> None:
    """执行 import 语句"""

    # 获取当前文件路径
    current_file = self.context.current_file

    # 加载模块
    module = self.module_loader.load_module(
        statement.module_path,
        current_file
    )

    # 语法 1: import alias from "path"
    if statement.members is None:
        # 创建模块对象
        module_obj = ModuleObject(module.exports)

        # 注册到当前作用域
        self.symbol_table.define(
            statement.module_alias,
            module_obj
        )

    # 语法 2: from "path" import name1, name2
    else:
        for member_name in statement.members:
            # 检查成员是否存在
            if member_name not in module.exports:
                raise ImportError(
                    f"模块 '{module.name}' 未导出成员 '{member_name}' "
                    f"(行 {statement.line})"
                )

            # 直接注册到当前作用域
            self.symbol_table.define(
                member_name,
                module.exports[member_name]
            )
```

**处理成员访问表达式**:
```python
def _evaluate_member_access(self, expr: MemberAccessExpression) -> any:
    """评估成员访问表达式"""

    # 评估对象表达式
    obj = self.expression_evaluator.evaluate(expr.object)

    # 检查对象是否是模块对象
    if not isinstance(obj, ModuleObject):
        raise RuntimeError(
            f"只有模块对象支持成员访问 (行 {expr.line})"
        )

    # 访问成员
    member_name = expr.member
    if member_name not in obj.exports:
        raise AttributeError(
            f"模块未导出成员 '{member_name}' (行 {expr.line})"
        )

    return obj.exports[member_name]
```

**ModuleObject 类**:
```python
@dataclass
class ModuleObject:
    """模块对象 (用于 import alias)"""
    exports: Dict[str, any]

    def __repr__(self):
        return f"<Module: {list(self.exports.keys())}>"
```

**实现难度**: ⏱️ 中等 (2-3 天)
- 需要集成 ModuleLoader
- 需要处理作用域注册
- 需要支持成员访问表达式

### 总实现难度

- **Lexer**: 0.5 天
- **Parser**: 2-3 天
- **Module System**: 4-5 天
- **Interpreter**: 2-3 天
- **单元测试**: 2-3 天
- **集成测试**: 1-2 天
- **文档编写**: 2-3 天

**总计**: 14-20 天 (约 3-4 周)

### 依赖项

- [x] 依赖现有的 Parser 和 Interpreter 基础设施
- [x] 依赖现有的作用域系统 (需扩展支持模块作用域)
- [x] 依赖现有的符号表 (需扩展支持模块对象)
- [ ] 无外部依赖

---

## 🧪 测试计划

### 测试用例

#### 正常情况

**test_library_basic.py**:
```python
def test_library_declaration():
    """测试 library 声明"""
    source = """
    library my_lib

    export const VERSION = "1.0"
    export function hello():
        return "world"
    """
    # 断言: 解析成功, library 名称为 "my_lib"

def test_import_module():
    """测试模块导入"""
    # libs/logging.flow
    library_source = """
    library logging
    export function log_info(msg):
        log info msg
    """

    # main.flow
    main_source = """
    import logging from "libs/logging.flow"
    logging.log_info("测试消息")
    """
    # 断言: 导入成功, 函数调用成功

def test_from_import():
    """测试 from-import"""
    main_source = """
    from "libs/logging.flow" import log_info, log_error
    log_info("测试")
    """
    # 断言: 成员导入成功, 可直接调用

def test_module_scope_isolation():
    """测试模块作用域隔离"""
    # libs/a.flow
    a_source = """
    library a
    let internal = 42
    export function get_value():
        return internal
    """

    # libs/b.flow
    b_source = """
    library b
    let internal = 99
    export function get_value():
        return internal
    """

    # main.flow
    main_source = """
    import a from "libs/a.flow"
    import b from "libs/b.flow"

    let val_a = a.get_value()
    let val_b = b.get_value()
    """
    # 断言: val_a == 42, val_b == 99 (作用域隔离)
```

#### 边界情况

**test_library_edge_cases.py**:
```python
def test_module_caching():
    """测试模块缓存"""
    main_source = """
    import logging from "libs/logging.flow"
    import logging2 from "libs/logging.flow"
    """
    # 断言: logging.flow 只加载一次

def test_nested_imports():
    """测试嵌套导入 (库导入库)"""
    # libs/core.flow
    core_source = """
    library core
    export const VERSION = "1.0"
    """

    # libs/utils.flow
    utils_source = """
    library utils
    import core from "core.flow"

    export function get_version():
        return core.VERSION
    """

    # main.flow
    main_source = """
    import utils from "libs/utils.flow"
    let ver = utils.get_version()
    """
    # 断言: ver == "1.0"

def test_import_same_name_conflict():
    """测试重复导入相同名称"""
    main_source = """
    import a from "libs/a.flow"
    import a from "libs/b.flow"  # 冲突
    """
    # 断言: 抛出 NameConflictError
```

#### 异常情况

**test_library_errors.py**:
```python
def test_library_file_not_found():
    """测试库文件不存在"""
    source = """
    import missing from "libs/missing.flow"
    """
    # 断言: 抛出 FileNotFoundError

def test_circular_import():
    """测试循环导入"""
    # libs/a.flow
    a_source = """
    library a
    import b from "b.flow"
    """

    # libs/b.flow
    b_source = """
    library b
    import a from "a.flow"
    """
    # 断言: 抛出 CircularImportError

def test_import_non_exported_member():
    """测试导入未导出的成员"""
    # libs/utils.flow
    lib_source = """
    library utils
    function private_func():
        return 42
    """

    # main.flow
    main_source = """
    from "libs/utils.flow" import private_func
    """
    # 断言: 抛出 ImportError

def test_library_contains_executable_statements():
    """测试库文件包含可执行语句"""
    lib_source = """
    library bad_lib

    log "This should not be allowed"

    export function foo():
        return 42
    """
    # 断言: 抛出 LibraryConstraintViolation

def test_library_name_mismatch():
    """测试 library 名称与文件名不匹配"""
    # 文件名: a.flow
    # 内容:
    lib_source = """
    library b
    """
    # 断言: 抛出 LibraryNameMismatchError

def test_member_access_on_non_module():
    """测试在非模块对象上使用成员访问"""
    source = """
    let x = 42
    log x.member
    """
    # 断言: 抛出 RuntimeError
```

### 测试覆盖率目标

- [ ] 行覆盖率 ≥ 90%
- [ ] 分支覆盖率 ≥ 85%
- [ ] 所有错误路径都有测试
- [ ] 所有边界情况都有测试

### 集成测试

**test_library_integration.py**:
```python
def test_real_world_refactoring():
    """
    测试真实场景: 重构 factory_ai_registration.flow

    将 600+ 行文件拆分为:
    - main.flow (100 行)
    - libs/logging.flow (30 行)
    - libs/validation.flow (40 行)
    - libs/random_utils.flow (20 行)

    验证:
    1. 功能完全一致
    2. 代码可读性提升
    3. 可维护性提升
    """
    # 执行重构后的 main.flow
    # 对比输出与重构前的 factory_ai_registration.flow
    # 断言: 输出完全一致
```

---

## 📚 文档变更

### 需要更新的文档

- [ ] `MASTER.md` - 添加 Feature 5.1, 5.2, 5.3
  ```markdown
  | 5.1 | Library Declaration | `library NAME` | ✅ | v5.0 | `_parse_library_declaration()` | ✅ | Module definition |
  | 5.2 | Export Statement | `export (const|function)` | ✅ | v5.0 | `_parse_export_statement()` | ✅ | Export members |
  | 5.3 | Import Statement | `import ALIAS from "PATH"` / `from "PATH" import ...` | ✅ | v5.0 | `_parse_import_statement()` | ✅ | Module import |
  | 5.4 | Member Access | `module.member` | ✅ | v5.0 | `_parse_postfix_expression()` | ✅ | Access module members |
  ```

- [ ] `CHANGELOG.md` - 添加到 [5.0.0] Unreleased
  ```markdown
  ## [5.0.0] - Unreleased

  ### Added
  - **Library System**: 模块化代码复用机制
    - `library NAME` 声明库文件
    - `export const/function` 导出成员
    - `import ALIAS from "PATH"` 导入模块
    - `from "PATH" import name1, name2` 导入特定成员
    - `module.member` 成员访问表达式
    - 独立作用域隔离
    - 模块缓存和循环导入检测
  ```

- [ ] `DSL-GRAMMAR.ebnf` - 添加 EBNF 规则
  ```ebnf
  (* Library System - v5.0+ *)
  library_file         = library_declaration , { statement } ;
  library_declaration  = "library" , identifier , NEWLINE ;
  export_statement     = "export" , ( const_declaration | function_declaration ) ;

  import_statement     = "import" , identifier , "from" , string_literal
                       | "from" , string_literal , "import" , identifier , { "," , identifier } ;

  member_access        = primary_expression , { "." , identifier } ;
  ```

- [ ] `DSL-GRAMMAR-QUICK-REFERENCE.md` - 添加快速参考

- [ ] `DSL-SYNTAX-CHEATSHEET.md` - 添加速查表
  ```markdown
  ## 模块化 (v5.0+)

  ### Library 定义
  ```flow
  library logging

  export const VERSION = "1.0"
  export function log_info(msg):
      log info msg
  ```

  ### Import 使用
  ```flow
  # 导入整个模块
  import logging from "libs/logging.flow"
  logging.log_info("测试")

  # 导入特定成员
  from "libs/logging.flow" import log_info
  log_info("测试")
  ```
  ```

- [ ] `02-MODULE-DETAILS.md` - 添加 Module System 模块说明

- [ ] `04-API-REFERENCE.md` - 添加使用指南
  - Library 文件编写指南
  - Import 语句使用指南
  - 最佳实践和设计模式
  - 常见错误和解决方案

- [ ] 添加示例到 `examples/flows/`
  - `examples/libs/logging.flow` - 日志工具库
  - `examples/libs/validation.flow` - 验证函数库
  - `examples/libs/random_utils.flow` - 随机数工具库
  - `examples/flows/modular_registration.flow` - 使用模块化的主流程

- [ ] 添加教程: `docs/TUTORIAL-LIBRARY-SYSTEM.md`
  - 从单文件到多文件的重构步骤
  - 库文件组织最佳实践
  - 常见模式和反模式

---

## 🔄 替代方案

### 方案 1: Include (C 风格文件包含)

**语法**:
```flow
include "libs/logging.flow"

# logging.flow 的内容直接插入到这里

log_phase_start(1, "测试")
```

**优点**:
- 实现简单 (文本替换)
- 无需命名空间

**缺点**:
- ❌ 命名空间污染 (所有符号都在全局作用域)
- ❌ 无法控制可见性 (无 export 机制)
- ❌ 容易重复包含 (需要 include guard)
- ❌ 难以追踪符号来源

### 方案 2: Python 风格 Import (无 library 声明)

**语法**:
```flow
# 直接导入 .flow 文件,无需 library 声明
import "libs/logging.flow" as logging

logging.log_phase_start(1, "测试")
```

**优点**:
- 无需 library 声明
- 语法更简洁

**缺点**:
- ❌ 无法区分库文件和主流程文件
- ❌ 库文件可能包含可执行语句 (污染)
- ❌ 无法显式控制导出 (所有符号都可访问)
- ❌ 容易误用 (导入包含 step 的文件)

### 方案 3: JavaScript 风格 ES6 Module

**语法**:
```flow
# 库文件
export const VERSION = "1.0"
export function log_info(msg):
    log info msg

# 主文件
import { log_info } from "./libs/logging.flow"
log_info("测试")
```

**优点**:
- 类似主流语言 (JavaScript)
- 支持解构导入

**缺点**:
- ❌ 无法区分库文件和主流程文件 (无 library 声明)
- ❌ 语法复杂 (花括号解构)
- ❌ 与 DSL 的简洁风格不符

### 不做任何改变

**当前做法**:
```flow
# 600+ 行文件,工具函数与业务逻辑混在一起
function log_phase_start(phase_num, phase_name):
    log "阶段 [{phase_num}]: {phase_name}"

# ... 更多 20+ 个工具函数

# 业务逻辑
step "阶段 1":
    log_phase_start(1, "测试")
end step
```

**为什么不够**:
- ❌ 代码重复 (多个文件需要复制粘贴)
- ❌ 难以维护 (600+ 行难以导航)
- ❌ 命名空间污染 (所有函数在全局作用域)
- ❌ 无法跨项目复用

---

## 💬 讨论记录

### 设计决策

**决策 1: 为什么需要 library 声明？**
- **理由**:
  - 明确区分库文件和主流程文件
  - 强制约束 (库文件不能包含可执行语句)
  - **验证 library 名称与文件名必须匹配** (防止混淆，强制执行 ✅)
  - 类似 MT4 的设计,用户已熟悉
- **✅ 确认**: library 名称强制与文件名匹配 (无 .flow 扩展名)

**决策 2: 为什么需要显式 export？**
- **理由**:
  - 清晰的公共 API (区分公共接口和内部实现)
  - 避免命名空间污染
  - 支持库内部重构 (私有函数可以随意修改)
  - 类似主流语言 (Python, JavaScript, Rust)

**决策 3: 为什么支持两种 import 语法？**
- **理由**:
  - `import alias from "path"`: 适合导入整个模块,保持命名空间清晰
  - `from "path" import ...`: 适合导入少量成员,减少代码冗长
  - 两种语法互补,满足不同场景需求
  - 类似 Python 的设计,用户容易理解

**决策 4: 为什么不支持相对导入 (如 `import .logging`)？**
- **理由**:
  - 相对路径字符串 `"libs/logging.flow"` 更直观
  - 避免引入 `.` 和 `..` 语法 (增加复杂度)
  - 路径解析逻辑更简单

**决策 5: 为什么不支持通配符导入 (如 `from "lib" import *`)？**
- **理由**:
  - 通配符导入破坏可读性 (不知道导入了哪些符号)
  - 容易命名冲突
  - 违反显式优于隐式原则
  - Python 社区也不推荐通配符导入

**决策 6: 为什么完全禁止循环导入？**
- **理由**:
  - 循环导入是设计缺陷的标志 (应该重构代码结构)
  - 简化实现复杂度 (无需处理部分初始化状态)
  - 避免运行时不可预测的行为
  - 强制开发者设计清晰的依赖层次
- **✅ 确认**: 完全禁止循环导入，运行时检测并抛出 CircularImportError

**决策 7: 版本号选择 (v5.0 vs v4.4)**
- **理由**:
  - Module System 是重大新特性 (4 个新语句类型)
  - 改变了代码组织方式 (从单文件到多文件)
  - 提升了语法复杂度限制 (30→35)
  - 符合语义化版本规范 (MINOR 版本应递增主版本号)
- **✅ 确认**: 使用 v5.0.0 作为版本号

---

## ✅ 决策

### 核心团队评审

- [x] 技术可行性: ✅ 已确认
- [x] 语法一致性: ✅ 已确认
- [x] 复杂度控制: ✅ 已确认 (31/35 语句, 91/100 关键字, 限制已调整)
- [x] 文档完整性: ✅ 已确认

### 最终决定

- **状态**: ✅ Approved (设计评审完成)
- **决定日期**: 2025-11-29
- **决策者**: Core Team
- **理由**:
  - 解决了 600+ 行文件的代码重复和维护问题
  - 语法设计清晰，与主流语言一致
  - 语法复杂度在调整后的限制内 (31/35)
  - 向后 100% 兼容

### 已确认的设计决策 ✅

1. ✅ **Library 名称强制与文件名匹配** (无 .flow 扩展名)
   - 例如: 文件 `logging.flow` 必须声明 `library logging`
   - 不匹配将抛出 LibraryNameMismatchError

2. ✅ **完全禁止循环导入**
   - 运行时检测并抛出 CircularImportError
   - 强制开发者设计清晰的依赖层次

3. ✅ **版本号使用 v5.0.0**
   - 符合语义化版本规范 (重大新特性)
   - 提升语法复杂度限制 (30→35)

4. ✅ **不支持绝对路径导入**
   - 仅支持相对路径 (安全考虑)
   - 路径基于当前文件所在目录

5. ✅ **模块缓存策略**
   - 使用绝对路径作为缓存键
   - 每个库文件在同一次执行中只加载一次

### 待未来讨论的问题 (v5.1+)

1. 是否需要 `as` 关键字支持别名？(如 `import logging as log`)
   - 当前设计: 不支持
   - 未来可能性: v5.1+ 考虑添加

2. 是否需要支持库文件的版本控制？
   - 当前设计: 不支持
   - 未来可能性: v5.2+ 考虑添加

3. 是否支持包 (package) 概念？
   - 当前设计: 仅支持单文件库
   - 未来可能性: v6.0+ 考虑添加

---

## 📅 实施时间线

_如果批准,预计时间线_

### Phase 1: 设计阶段 (完成 ✅)
- [x] 提案编写
- [x] 核心团队评审
- [x] 确定最终设计
- [x] 确认关键决策:
  - Library 名称强制与文件名匹配
  - 完全禁止循环导入
  - 版本号使用 v5.0.0
  - 语句类型限制调整: 30→35

### Phase 2: 实施阶段 (14-18 天)
- [ ] Lexer 实现 (0.5 天)
  - 添加 LIBRARY, EXPORT, IMPORT, FROM, DOT tokens
- [ ] Parser 实现 (2-3 天)
  - `_parse_library_declaration()`
  - `_parse_export_statement()`
  - `_parse_import_statement()`
  - `_parse_postfix_expression()` (成员访问)
  - AST 节点定义
- [ ] Module System 实现 (4-5 天)
  - ModuleLoader 类
  - 路径解析
  - 模块缓存
  - 循环导入检测
  - 库文件约束验证
- [ ] Interpreter 实现 (2-3 天)
  - `_execute_import()`
  - `_evaluate_member_access()`
  - ModuleObject 类
  - 作用域集成
- [ ] 单元测试 (2-3 天)
  - Parser 测试
  - Module System 测试
  - Interpreter 测试
- [ ] 集成测试 (1-2 天)
  - 真实场景测试
  - 重构 factory_ai_registration.flow

### Phase 3: 文档阶段 (2-3 天)
- [ ] 更新 MASTER.md
- [ ] 更新 CHANGELOG.md
- [ ] 更新 EBNF 语法
- [ ] 更新快速参考和速查表
- [ ] 编写使用指南
- [ ] 编写教程
- [ ] 添加示例文件

### Phase 4: 验收阶段 (2 天)
- [ ] Code Review
- [ ] 性能测试
- [ ] 安全审查 (路径遍历漏洞)
- [ ] 用户验收测试

**总计**: 约 20-25 天 (4-5 周)

---

## 📎 附录

### 参考资料

- Python import system: https://docs.python.org/3/reference/import.html
- JavaScript ES6 modules: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules
- Rust module system: https://doc.rust-lang.org/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html
- MT4 MQL4 #include: https://docs.mql4.com/basis/preprosessor/include

### 相关提案

- PROPOSAL-008: Function Statement (v4.0) - 函数定义的基础
- PROPOSAL-003: Const Declaration (v3.0) - 常量定义

### 设计灵感

本提案的设计借鉴了:
1. **Python**: `from ... import ...` 语法, 显式 import
2. **MT4/MQL4**: `library` 关键字, 独立库文件概念
3. **Rust**: 显式 `export` (pub), 严格的可见性控制
4. **JavaScript**: 模块对象和成员访问

### 实现挑战

1. **路径解析**: 需要正确处理相对路径、符号链接、跨平台路径分隔符
2. **循环导入**: 需要维护导入栈,正确检测和报告循环依赖
3. **作用域管理**: 库文件需要独立作用域,避免污染全局命名空间
4. **缓存一致性**: 需要确保同一文件不被重复加载,但修改后需要重新加载
5. **错误报告**: 需要清晰的错误信息 (文件路径、行号、具体问题)

---

**提案状态**: ✅ Approved (设计评审完成)
**最后更新**: 2025-11-29
**维护者**: Core Team
**下一步**: 开始实施 Phase 2 (Lexer/Parser/Module System)
