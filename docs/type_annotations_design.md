# 类型标注（Type Annotations）设计

## 概述
为 Flowby DSL 添加可选的类型标注，提升代码可读性和错误检测能力。

## 语法设计

### 变量声明

```python
# 基本类型
let name: str = "Alice"
let age: int = 25
let score: float = 98.5
let active: bool = True

# 集合类型
let items: list = [1, 2, 3]
let user: dict = {name: "Bob", age: 30}

# 可选类型（允许 None）
let email: str? = None
let response: dict? = http.get(url)

# 类型推断（省略类型）
let count = 10  # 推断为 int
let names = ["Alice", "Bob"]  # 推断为 list
```

### 函数参数和返回值

```python
# 基本函数类型
function greet(name: str) -> str:
    return f"Hello, {name}!"

# 多参数
function add(a: int, b: int) -> int:
    return a + b

# 可选参数
function format(text: str, uppercase: bool?) -> str:
    if uppercase:
        return text.upper()
    return text

# 无返回值
function log(message: str) -> None:
    log message
```

### Lambda 表达式类型

```python
# 简单 Lambda（类型推断）
let double = (x: int) => x * 2

# 显式返回类型
let add: (int, int) -> int = (a, b) => a + b

# 集合操作中的类型
let evens: list<int> = numbers.filter((x: int) => x % 2 == 0)
```

## 类型系统

### 基本类型

1. **str** - 字符串
2. **int** - 整数
3. **float** - 浮点数
4. **bool** - 布尔值
5. **None** - 空值
6. **list** - 列表
7. **dict** - 字典

### 泛型类型

```python
# 列表类型
let numbers: list<int> = [1, 2, 3]
let names: list<str> = ["Alice", "Bob"]

# 字典类型
let user: dict<str, any> = {name: "Alice", age: 25}
let scores: dict<str, int> = {alice: 100, bob: 95}
```

### 联合类型

```python
# 多种可能类型
let value: int | str = 42
let response: dict | None = http.get(url)

# 可选类型语法糖
let name: str? = None  # 等价于 str | None
```

### 函数类型

```python
# 函数类型签名
let callback: (int) -> bool = x => x > 0
let comparator: (int, int) -> int = (a, b) => a - b

# 作为参数
function apply(fn: (int) -> int, value: int) -> int:
    return fn(value)
```

## 实现方案

### 方案 A：静态类型检查（推荐）

在 **Parser 阶段**进行类型检查，提前发现类型错误。

**实现位置**：
- `src/flowby/parser.py` - 解析类型标注
- `src/flowby/type_checker.py` - 类型检查器（新文件）
- `src/flowby/ast_nodes.py` - 添加类型信息到 AST

**工作流程**：
```
源代码
  ↓
[Lexer] 词法分析
  ↓
[Parser] 语法分析 + 类型标注解析
  ↓
[TypeChecker] 类型检查（新增）
  ↓
[Interpreter] 解释执行
```

**优点**：
- 提前发现类型错误
- 不影响运行时性能
- 更好的开发体验

**缺点**：
- 实现复杂度高
- 需要类型推断系统

### 方案 B：运行时类型检查（简化版）

在 **Interpreter 执行时**检查类型。

**优点**：
- 实现简单
- 渐进式迁移

**缺点**：
- 运行时才发现错误
- 性能开销

## 语法变更

### Lexer 变更

添加新 Token：
```python
class TokenType(Enum):
    # ... 现有 tokens
    COLON_TYPE = auto()  # : (类型标注用，与控制流的 : 区分)
    ARROW_TYPE = auto()  # -> (函数返回类型)
    QUESTION = auto()    # ? (可选类型)
    PIPE_TYPE = auto()   # | (联合类型)
    LT_TYPE = auto()     # < (泛型)
    GT_TYPE = auto()     # > (泛型)
```

### Parser 变更

添加类型解析方法：
```python
def _parse_type_annotation(self) -> TypeAnnotation:
    """
    解析类型标注

    语法:
        type_annotation ::= basic_type
                          | optional_type
                          | union_type
                          | generic_type
                          | function_type
    """
    pass

def _parse_let_with_type(self) -> LetStatement:
    """
    解析带类型的 let 语句

    语法: let name: type = value
    """
    pass
```

### AST 节点变更

```python
@dataclass
class TypeAnnotation(ASTNode):
    """类型标注节点"""
    type_name: str
    generic_params: List['TypeAnnotation'] = field(default_factory=list)
    is_optional: bool = False
    line: int = 0

@dataclass
class LetStatement(ASTNode):
    """let 语句（带类型）"""
    name: str
    value: Expression
    type_annotation: Optional[TypeAnnotation] = None  # 新增
    line: int = 0
```

## 实施步骤

### Phase 1: 基础类型标注（2-3 小时）
1. 添加 Token 类型
2. 实现基本类型解析（str, int, float, bool）
3. 修改 LetStatement, ConstStatement 支持类型
4. 简单的类型检查（字面量类型匹配）

### Phase 2: 函数类型（2-3 小时）
1. 函数参数类型标注
2. 函数返回类型标注
3. 类型检查（参数/返回值）

### Phase 3: 高级类型（3-4 小时）
1. 可选类型（`str?`）
2. 联合类型（`int | str`）
3. 泛型类型（`list<int>`）

### Phase 4: 类型推断（4-5 小时）
1. 字面量类型推断
2. 表达式类型推断
3. 函数调用类型推断

### Phase 5: 测试和文档（1-2 小时）
1. 单元测试
2. 集成测试
3. 文档和示例

**总计**: 12-18 小时

## 示例脚本

```python
# examples/type_annotations_demo.flow

# 基本类型
let name: str = "Alice"
let age: int = 25
let score: float = 98.5
let active: bool = True

# 可选类型
let email: str? = None
email = "alice@example.com"

# 集合类型
let numbers: list<int> = [1, 2, 3, 4, 5]
let user: dict<str, any> = {
    name: "Bob",
    age: 30,
    email: "bob@example.com"
}

# 函数类型
function greet(name: str) -> str:
    return f"Hello, {name}!"

function add(a: int, b: int) -> int:
    return a + b

function divide(a: float, b: float) -> float?:
    if b == 0:
        return None
    return a / b

# 使用
let greeting: str = greet("Alice")
let sum: int = add(10, 20)
let result: float? = divide(10.0, 0.0)

# 类型检查示例
# ❌ 类型错误（如果启用严格模式）
# let num: int = "not a number"  # TypeError: Expected int, got str
# let result: str = add(1, 2)    # TypeError: Expected str, got int

log success "类型标注示例完成"
```

## 错误消息示例

```
# 类型不匹配
[TypeError] at line 10: Type mismatch
  Expected: int
  Got: str
  Expression: let age: int = "25"
  Help: Convert string to int or change type annotation

# 函数返回类型错误
[TypeError] at line 20: Function return type mismatch
  Function: add(a: int, b: int) -> int
  Expected return type: int
  Got: str
  Help: Ensure all return statements match the declared type

# 可选类型检查
[TypeError] at line 30: Using possibly None value
  Variable: email (type: str?)
  Operation: email.upper()
  Help: Check for None before using: if email: email.upper()
```

## 配置选项

```python
# 在脚本开头配置类型检查级别
# type-check: strict   # 严格模式，所有变量必须标注
# type-check: lenient  # 宽松模式，允许无标注
# type-check: off      # 关闭类型检查

# 或通过 CLI
# flowby script.flow --type-check strict
```

## 与现有代码兼容

类型标注是**可选的**，现有代码无需修改即可运行：

```python
# 无类型标注（现有代码）
let name = "Alice"
let age = 25

# 带类型标注（新代码）
let email: str = "alice@example.com"

# 混合使用
let score = 98.5          # 类型推断为 float
let grade: str = "A"      # 显式类型标注
```

## 未来扩展

1. **自定义类型**（type alias）
   ```python
   type UserId = int
   type Callback = (int) -> bool
   ```

2. **接口类型**（interface）
   ```python
   interface User:
       name: str
       age: int
       email: str?
   ```

3. **类型守卫**（type guards）
   ```python
   if isinstance(value, str):
       # value 在此块中类型为 str
   ```

## 参考

- **TypeScript**: 类型系统设计
- **Python Type Hints**: 语法风格
- **Rust**: 类型推断系统
