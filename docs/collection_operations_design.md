# 集合操作方法设计

## 概述
为 Flowby DSL 添加函数式集合操作方法，提升数据处理能力。

## 语法设计

### 方式 1：链式方法调用（推荐）

```python
# 过滤
let adults = users.filter(u => u.age >= 18)

# 映射
let names = users.map(u => u.name)

# 归约
let total = prices.reduce((sum, price) => sum + price, 0)

# 链式调用
let result = items
    .filter(x => x > 0)
    .map(x => x * 2)
    .reduce((sum, x) => sum + x, 0)
```

### 方式 2：全局函数（备选）

```python
let adults = filter(users, u => u.age >= 18)
let names = map(users, u => u.name)
```

## 方法列表

### 核心方法（优先实现）

1. **filter(predicate)** - 过滤
   ```python
   let evens = [1, 2, 3, 4].filter(x => x % 2 == 0)
   # => [2, 4]
   ```

2. **map(transform)** - 映射
   ```python
   let doubled = [1, 2, 3].map(x => x * 2)
   # => [2, 4, 6]
   ```

3. **reduce(reducer, initial)** - 归约
   ```python
   let sum = [1, 2, 3].reduce((acc, x) => acc + x, 0)
   # => 6
   ```

4. **find(predicate)** - 查找第一个匹配元素
   ```python
   let user = users.find(u => u.id == 123)
   # => {id: 123, name: "Alice"} 或 None
   ```

5. **findIndex(predicate)** - 查找索引
   ```python
   let index = users.findIndex(u => u.name == "Bob")
   # => 1 或 -1
   ```

### 布尔判断方法

6. **some(predicate)** - 是否存在满足条件的元素
   ```python
   let hasAdult = users.some(u => u.age >= 18)
   # => True 或 False
   ```

7. **every(predicate)** - 是否所有元素都满足条件
   ```python
   let allAdults = users.every(u => u.age >= 18)
   # => True 或 False
   ```

### 辅助方法

8. **sort(comparator?)** - 排序
   ```python
   let sorted = [3, 1, 2].sort()  # => [1, 2, 3]
   let byAge = users.sort((a, b) => a.age - b.age)
   ```

9. **reverse()** - 反转
   ```python
   let reversed = [1, 2, 3].reverse()  # => [3, 2, 1]
   ```

10. **slice(start, end?)** - 切片
    ```python
    let sub = items.slice(1, 3)  # => [items[1], items[2]]
    ```

11. **join(separator)** - 连接成字符串
    ```python
    let csv = ["a", "b", "c"].join(", ")  # => "a, b, c"
    ```

## 实现方案

### 方案 A：作为内置方法（推荐）

在 `ExpressionEvaluator` 中处理方法调用时，检测数组/列表类型，提供这些方法。

**实现位置**：
- `src/flowby/expression_evaluator.py` - 方法调用处理
- `src/flowby/builtin_functions.py` - 可选，作为全局函数

**优点**：
- 符合现代语言习惯（JS, Python, Rust）
- 链式调用，代码简洁
- 不污染全局命名空间

**缺点**：
- 需要支持 Lambda 表达式（箭头函数）

### 方案 B：作为全局函数

添加到 `builtin_functions.py`，使用函数调用语法。

**优点**：
- 实现简单，不需要 Lambda
- 可以使用命名函数

**缺点**：
- 代码不够简洁
- 无法链式调用

## Lambda 表达式语法

为支持集合操作，需要添加 Lambda 表达式：

```python
# 单参数
x => x * 2

# 多参数
(a, b) => a + b

# 完整写法
(x, y) => {
    let result = x + y
    return result
}
```

**Lexer 变更**：
- 添加 `TokenType.ARROW` (`=>`)

**Parser 变更**：
- 添加 `_parse_lambda_expression()`
- 在 `_parse_primary()` 中处理

**AST 节点**：
```python
@dataclass
class LambdaExpression(Expression):
    parameters: List[str]
    body: Expression or List[ASTNode]
    line: int
```

## 实施步骤

### Phase 1: Lambda 表达式支持
1. 添加 `TokenType.ARROW`
2. 实现 `LambdaExpression` AST 节点
3. 实现 Parser 解析
4. 实现 Interpreter 执行（创建闭包）
5. 测试 Lambda 表达式

### Phase 2: 核心集合方法
1. 实现 `filter()`
2. 实现 `map()`
3. 实现 `reduce()`
4. 测试三个核心方法

### Phase 3: 扩展方法
1. 实现 `find()`, `findIndex()`
2. 实现 `some()`, `every()`
3. 实现 `sort()`, `reverse()`
4. 实现 `slice()`, `join()`

### Phase 4: 文档和示例
1. 更新 grammar/MASTER.md
2. 创建示例脚本
3. 更新 CHANGELOG.md

## 时间估算
- Phase 1 (Lambda): 2-3 小时
- Phase 2 (核心方法): 1-2 小时
- Phase 3 (扩展方法): 1-2 小时
- Phase 4 (文档): 0.5 小时
- **总计**: 4.5-7.5 小时

## 示例脚本

```python
# examples/collection_operations_demo.flow

step "集合操作演示":
    let numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Filter: 过滤偶数
    let evens = numbers.filter(x => x % 2 == 0)
    log f"偶数: {evens}"  # [2, 4, 6, 8, 10]

    # Map: 平方
    let squares = numbers.map(x => x * x)
    log f"平方: {squares}"  # [1, 4, 9, 16, 25, ...]

    # Reduce: 求和
    let sum = numbers.reduce((acc, x) => acc + x, 0)
    log f"总和: {sum}"  # 55

    # 链式调用
    let result = numbers
        .filter(x => x > 5)           # [6, 7, 8, 9, 10]
        .map(x => x * 2)              # [12, 14, 16, 18, 20]
        .reduce((acc, x) => acc + x, 0)  # 80
    log f"链式结果: {result}"

    # 对象数组
    let users = [
        {name: "Alice", age: 25},
        {name: "Bob", age: 17},
        {name: "Charlie", age: 30}
    ]

    let adults = users.filter(u => u.age >= 18)
    let names = adults.map(u => u.name)
    log f"成年人: {names}"  # ["Alice", "Charlie"]

    # Find
    let bob = users.find(u => u.name == "Bob")
    log f"找到: {bob.name}, {bob.age}"

    # Some / Every
    let hasMinor = users.some(u => u.age < 18)
    let allAdults = users.every(u => u.age >= 18)
    log f"有未成年人: {hasMinor}"  # True
    log f"全是成年人: {allAdults}"  # False
```
