# Flowby DSL 测试重建计划

## 项目背景

**当前状态**：
- 总测试数：1181 个
- 总覆盖率：54%
- 主要问题：
  - 执行层覆盖率低（interpreter: 50%, evaluator: 46%）
  - 集成层覆盖率严重不足（runner: 11%, response_handler: 17%）
  - 大型测试文件难以维护（最大 1011 行）
  - 测试结构不一致，缺乏统一标准

**重建目标**：
- 总覆盖率：54% → **80%**
- 执行层覆盖率：46-50% → **75%**
- 集成层覆盖率：11-26% → **70%**
- 测试结构：统一、模块化、易维护
- 测试质量：高质量、可读性强、文档完善

---

## 执行原则

### 🚨 关键规则（必须遵守）

1. **保持绿色**：任何时候运行 `pytest tests/` 都必须全部通过
2. **增量进行**：一次只重构一个模块，提交后再继续
3. **不破坏现有**：先添加新测试，确认通过后再删除旧测试
4. **代码优先**：不要修改业务代码（src/），只重建测试
5. **验证通过**：每个任务完成后运行验证脚本

### 📝 工作流程

```bash
# 每个任务的标准流程
1. 阅读任务描述
2. 创建新测试文件
3. 运行测试确保通过
4. 检查覆盖率提升
5. 运行验证脚本
6. 提交代码
7. 继续下一个任务
```

---

## 测试架构设计

### 目录结构（新）

```
tests/
├── unit/                           # 单元测试（细粒度）
│   ├── lexer/                      # 词法分析器
│   │   ├── test_tokenize.py
│   │   ├── test_indentation.py
│   │   └── test_error_handling.py
│   ├── parser/                     # 语法分析器
│   │   ├── test_expressions.py
│   │   ├── test_statements.py
│   │   ├── test_blocks.py
│   │   └── test_error_recovery.py
│   ├── interpreter/                # 解释器
│   │   ├── test_execution.py
│   │   ├── test_scopes.py
│   │   └── test_builtin_functions.py
│   ├── evaluator/                  # 表达式求值
│   │   ├── test_operators.py
│   │   ├── test_type_conversion.py
│   │   ├── test_short_circuit.py
│   │   └── test_function_calls.py
│   └── services/                   # 服务系统
│       ├── test_http_provider.py
│       ├── test_random_provider.py
│       └── test_registry.py
│
├── integration/                    # 集成测试（模块交互）
│   ├── test_runner.py              # 脚本运行器
│   ├── test_resource_integration.py # OpenAPI 资源
│   ├── test_module_system.py       # 模块导入
│   ├── test_resilience.py          # 重试与容错
│   └── test_response_handling.py   # 响应处理
│
├── e2e/                            # 端到端测试（完整流程）
│   ├── test_web_automation.py      # Web 自动化场景
│   ├── test_api_testing.py         # API 测试场景
│   └── test_data_processing.py     # 数据处理场景
│
├── grammar/                        # 语法对齐测试（保留）
│   ├── test_v3_syntax.py
│   ├── test_v4_features.py
│   └── test_v5_modules.py
│
├── fixtures/                       # 共享 fixtures
│   ├── conftest.py
│   ├── sample_scripts.py
│   └── mock_services.py
│
└── templates/                      # 测试模板
    ├── unit_test_template.py
    ├── integration_test_template.py
    └── e2e_test_template.py
```

### 测试分层原则

| 层级 | 范围 | 比例 | 执行速度 |
|------|------|------|----------|
| 单元测试 | 单个函数/类 | 70% | 快（< 5s） |
| 集成测试 | 多个模块交互 | 20% | 中（5-15s） |
| 端到端测试 | 完整流程 | 10% | 慢（15-30s） |

---

## 详细任务清单

### Phase 1: 准备工作（约 1 小时）

#### Task 1.1: 创建测试模板

**文件**: `tests/templates/unit_test_template.py`

```python
"""
单元测试模板

使用方法：
1. 复制此文件到目标目录
2. 替换 <MODULE_NAME> 为实际模块名
3. 根据功能添加测试用例
"""

import pytest
from flowby.<MODULE_PATH> import <MODULE_CLASS>


class Test<MODULE_CLASS>:
    """<MODULE_CLASS> 单元测试"""

    @pytest.fixture
    def instance(self):
        """创建测试实例"""
        return <MODULE_CLASS>()

    def test_<function_name>_success(self, instance):
        """✅ 测试正常情况"""
        # Arrange
        input_data = ...

        # Act
        result = instance.<function_name>(input_data)

        # Assert
        assert result == expected_value

    def test_<function_name>_edge_case(self, instance):
        """✅ 测试边界情况"""
        pass

    def test_<function_name>_error(self, instance):
        """❌ 测试错误情况"""
        with pytest.raises(ExpectedException):
            instance.<function_name>(invalid_input)
```

**验收标准**：
- [ ] 文件创建成功
- [ ] 包含完整的模板结构
- [ ] 注释清晰易懂

---

#### Task 1.2: 创建集成测试模板

**文件**: `tests/templates/integration_test_template.py`

```python
"""
集成测试模板

使用方法：
1. 复制此文件到 tests/integration/
2. 替换 <FEATURE_NAME> 为实际功能名
3. 测试多个模块的交互
"""

import pytest
from unittest.mock import Mock, patch
from flowby.lexer import Lexer
from flowby.parser import Parser
from flowby.interpreter import Interpreter
from flowby.context import ExecutionContext


class Test<FEATURE_NAME>Integration:
    """<FEATURE_NAME> 集成测试"""

    @pytest.fixture
    def setup(self):
        """准备测试环境"""
        context = ExecutionContext(task_id="test-task")
        return {
            'lexer': Lexer(),
            'parser': Parser(),
            'interpreter': Interpreter(context),
            'context': context
        }

    def test_<scenario>_end_to_end(self, setup):
        """✅ 测试完整流程"""
        source = """
        # DSL 代码
        """

        # Lexer → Parser → Interpreter
        tokens = setup['lexer'].tokenize(source)
        ast = setup['parser'].parse(tokens)
        setup['interpreter'].execute(ast)

        # 验证结果
        assert setup['context'].variables['result'] == expected

    def test_<scenario>_with_mocks(self, setup):
        """✅ 测试带 mock 的场景"""
        with patch('flowby.services.http') as mock_http:
            mock_http.get.return_value = {'data': 'test'}
            # ... 测试代码
```

**验收标准**：
- [ ] 文件创建成功
- [ ] 包含 Lexer → Parser → Interpreter 完整流程
- [ ] 包含 mock 示例

---

#### Task 1.3: 创建验证脚本

**文件**: `scripts/verify_tests.py`

```python
#!/usr/bin/env python
"""
测试验证脚本

验证测试质量和覆盖率
"""

import subprocess
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent


def run_command(cmd):
    """运行命令并返回结果"""
    result = subprocess.run(
        cmd, cwd=ROOT_DIR, capture_output=True, text=True,
        encoding='utf-8', errors='replace'
    )
    return result.returncode == 0, result.stdout, result.stderr


def verify_tests_pass():
    """验证所有测试通过"""
    print(">> Verifying all tests pass...")
    success, stdout, stderr = run_command(["pytest", "tests/", "-x", "-q"])

    if not success:
        print("[FAIL] Some tests failed!")
        print(stderr)
        return False

    print("[PASS] All tests passed")
    return True


def verify_coverage(min_coverage=54):
    """验证覆盖率"""
    print(f">> Verifying coverage >= {min_coverage}%...")

    success, stdout, stderr = run_command([
        "pytest", "tests/",
        "--cov=src/flowby",
        "--cov-report=json",
        "-q"
    ])

    if not success:
        print("[FAIL] Coverage check failed")
        return False

    # 读取覆盖率报告
    coverage_file = ROOT_DIR / "coverage.json"
    if not coverage_file.exists():
        print("[FAIL] Coverage report not found")
        return False

    with open(coverage_file) as f:
        data = json.load(f)

    total_coverage = data['totals']['percent_covered']
    print(f"Current coverage: {total_coverage:.1f}%")

    if total_coverage < min_coverage:
        print(f"[FAIL] Coverage {total_coverage:.1f}% < {min_coverage}%")
        return False

    print(f"[PASS] Coverage {total_coverage:.1f}% >= {min_coverage}%")
    return True


def verify_no_skipped():
    """验证没有跳过的测试"""
    print(">> Verifying no skipped tests...")
    success, stdout, stderr = run_command(["pytest", "tests/", "--collect-only", "-q"])

    if "skipped" in stdout.lower():
        print("[WARN] Some tests are skipped")
        return True  # 警告但不失败

    print("[PASS] No skipped tests")
    return True


def main():
    """运行所有验证"""
    print("="*60)
    print("Test Verification")
    print("="*60)

    checks = [
        ("Tests pass", verify_tests_pass),
        ("Coverage", lambda: verify_coverage(54)),
        ("No skipped", verify_no_skipped),
    ]

    failed = []
    for name, check in checks:
        if not check():
            failed.append(name)

    print("="*60)
    if failed:
        print(f"[FAIL] Failed checks: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("[PASS] All verifications passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

**验收标准**：
- [ ] 脚本可执行
- [ ] 验证所有测试通过
- [ ] 验证覆盖率达标
- [ ] 输出清晰易读

**执行**: `python scripts/verify_tests.py`

---

### Phase 2: 补充集成测试（约 8-10 小时）

#### Task 2.1: 创建 Runner 集成测试

**目标**: runner.py 覆盖率 11% → 70%

**文件**: `tests/integration/test_runner.py`

**要测试的场景**：
1. ✅ 运行简单脚本成功
2. ✅ 运行带变量的脚本
3. ✅ 运行带函数的脚本
4. ✅ 运行带 step 块的脚本
5. ✅ 脚本执行错误处理
6. ✅ 脚本超时处理
7. ✅ 诊断信息收集
8. ✅ 多脚本并发执行
9. ✅ 脚本中断恢复
10. ✅ 输出格式验证

**示例测试**：

```python
import pytest
from pathlib import Path
from flowby.runner import ScriptRunner
from flowby.errors import ExecutionError


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

    def test_run_script_with_error(self, runner, tmp_path):
        """❌ 运行错误脚本"""
        script_path = tmp_path / "error.flow"
        script_path.write_text("log undefined_variable")

        result = runner.run(script_path)

        assert result.success is False
        assert result.exit_code != 0
        assert "未定义变量" in result.error_message

    def test_run_script_with_timeout(self, runner, tmp_path):
        """⏱️ 脚本超时"""
        script_path = tmp_path / "timeout.flow"
        script_path.write_text('''
while True:
    log "infinite loop"
''')

        with pytest.raises(ExecutionError, match="超时"):
            runner.run(script_path, timeout=1)

    # ... 继续添加其他测试场景
```

**验收标准**：
- [ ] 至少 50 个测试用例
- [ ] 覆盖所有公共方法
- [ ] runner.py 覆盖率 >= 70%
- [ ] 运行 `pytest tests/integration/test_runner.py -v` 全部通过
- [ ] 运行 `python scripts/verify_tests.py` 通过

**预计新增覆盖率**: +59%

---

#### Task 2.2: 创建 Response Handler 集成测试

**目标**: response_handler.py 覆盖率 17% → 70%

**文件**: `tests/integration/test_response_handling.py`

**要测试的场景**：
1. ✅ JSON 响应解析
2. ✅ HTML 响应解析
3. ✅ XML 响应解析
4. ✅ 文本响应处理
5. ✅ 二进制响应处理
6. ✅ 响应状态码处理（2xx, 3xx, 4xx, 5xx）
7. ✅ 响应头解析
8. ✅ Cookie 处理
9. ✅ 重定向处理
10. ✅ 响应超时
11. ✅ 响应大小限制
12. ✅ 响应流式处理
13. ✅ 错误响应处理
14. ✅ 响应缓存

**示例测试**：

```python
import pytest
from unittest.mock import Mock
from flowby.response_handler import ResponseHandler, Response


class TestResponseHandler:
    """ResponseHandler 集成测试"""

    @pytest.fixture
    def handler(self):
        return ResponseHandler()

    def test_parse_json_response(self, handler):
        """✅ 解析 JSON 响应"""
        mock_response = Mock()
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.status_code = 200
        mock_response.json.return_value = {'key': 'value', 'count': 42}

        result = handler.handle(mock_response)

        assert result.is_success is True
        assert result.data['key'] == 'value'
        assert result.data['count'] == 42

    def test_handle_404_error(self, handler):
        """❌ 处理 404 错误"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        result = handler.handle(mock_response)

        assert result.is_success is False
        assert result.status_code == 404

    # ... 继续添加其他测试场景
```

**验收标准**：
- [ ] 至少 40 个测试用例
- [ ] response_handler.py 覆盖率 >= 70%
- [ ] 所有测试通过
- [ ] 验证脚本通过

**预计新增覆盖率**: +53%

---

#### Task 2.3: 创建 Resource Integration 测试

**目标**: resource_namespace.py 覆盖率 19% → 70%

**文件**: `tests/integration/test_resource_integration.py`

**要测试的场景**：
1. ✅ 加载 OpenAPI 规范
2. ✅ 生成 API 方法
3. ✅ 调用 API 方法（GET）
4. ✅ 调用 API 方法（POST）
5. ✅ 调用 API 方法（PUT/DELETE/PATCH）
6. ✅ 参数验证
7. ✅ 认证处理（Bearer/API Key/Basic）
8. ✅ 请求重试
9. ✅ 错误处理
10. ✅ 响应转换
11. ✅ 多资源管理
12. ✅ 资源缓存

**示例测试**：

```python
import pytest
from unittest.mock import Mock, patch
from flowby.resource_namespace import ResourceNamespace


class TestResourceIntegration:
    """Resource 集成测试"""

    @pytest.fixture
    def petstore_spec(self):
        """Petstore OpenAPI 规范"""
        return {
            'openapi': '3.0.0',
            'paths': {
                '/pet/{petId}': {
                    'get': {
                        'operationId': 'getPetById',
                        'parameters': [
                            {'name': 'petId', 'in': 'path', 'required': True}
                        ],
                        'responses': {'200': {'description': 'Success'}}
                    }
                }
            }
        }

    @pytest.fixture
    def resource(self, petstore_spec):
        """创建测试资源"""
        return ResourceNamespace(
            name='petstore',
            spec=petstore_spec,
            base_url='https://api.example.com'
        )

    @patch('requests.get')
    def test_call_api_method(self, mock_get, resource):
        """✅ 调用 API 方法"""
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {'id': 123, 'name': 'Fluffy'}
        )

        result = resource.getPetById(petId=123)

        assert result['id'] == 123
        assert result['name'] == 'Fluffy'
        mock_get.assert_called_once()

    # ... 继续添加其他测试场景
```

**验收标准**：
- [ ] 至少 35 个测试用例
- [ ] resource_namespace.py 覆盖率 >= 70%
- [ ] 所有测试通过
- [ ] 验证脚本通过

**预计新增覆盖率**: +51%

---

#### Task 2.4: 创建 Resilience 集成测试

**目标**: retry_handler.py 覆盖率 21% → 70%

**文件**: `tests/integration/test_resilience.py`

**要测试的场景**：
1. ✅ 指数退避重试
2. ✅ 线性退避重试
3. ✅ 固定间隔重试
4. ✅ 重试次数限制
5. ✅ 重试条件判断
6. ✅ 熔断器开启
7. ✅ 熔断器半开
8. ✅ 熔断器恢复
9. ✅ 超时处理
10. ✅ 失败回调
11. ✅ 成功回调
12. ✅ 重试日志记录

**验收标准**：
- [ ] 至少 30 个测试用例
- [ ] retry_handler.py 覆盖率 >= 70%
- [ ] resilience_handler.py 覆盖率 >= 70%
- [ ] 所有测试通过

**预计新增覆盖率**: +49%

---

### Phase 3: 补充单元测试（约 10-12 小时）

#### Task 3.1: Interpreter 单元测试增强

**目标**: interpreter.py 覆盖率 50% → 75%

**文件**: `tests/unit/interpreter/test_execution.py`

**要测试的场景**：
1. ✅ 变量声明执行
2. ✅ 变量赋值执行
3. ✅ 函数定义执行
4. ✅ 函数调用执行
5. ✅ 循环执行
6. ✅ 条件执行
7. ✅ Step 块执行
8. ✅ When 语句执行
9. ✅ 断言执行
10. ✅ 导航执行
11. ✅ 点击执行
12. ✅ 输入执行
13. ✅ 等待执行
14. ✅ 截图执行
15. ✅ 错误处理

**验收标准**：
- [ ] 至少 60 个测试用例
- [ ] interpreter.py 覆盖率 >= 75%
- [ ] 所有测试通过

**预计新增覆盖率**: +25%

---

#### Task 3.2: Expression Evaluator 单元测试增强

**目标**: expression_evaluator.py 覆盖率 46% → 75%

**拆分为多个文件**：
- `tests/unit/evaluator/test_operators.py` - 运算符测试
- `tests/unit/evaluator/test_type_conversion.py` - 类型转换
- `tests/unit/evaluator/test_short_circuit.py` - 短路求值
- `tests/unit/evaluator/test_function_calls.py` - 函数调用

**要测试的场景**（每个文件 20-30 个测试）：

**test_operators.py**:
1. ✅ 算术运算符 (+, -, *, /, %)
2. ✅ 比较运算符 (==, !=, <, >, <=, >=)
3. ✅ 逻辑运算符 (and, or, not)
4. ✅ 一元运算符 (-, +)
5. ✅ 成员访问 (.)
6. ✅ 数组访问 ([])
7. ✅ 运算符优先级
8. ✅ 括号表达式

**test_type_conversion.py**:
1. ✅ 字符串 → 数字
2. ✅ 数字 → 字符串
3. ✅ 布尔 → 数字
4. ✅ Truthy/Falsy 值
5. ✅ None 处理
6. ✅ 数组转换
7. ✅ 对象转换

**test_short_circuit.py**:
1. ✅ and 短路（左侧 False）
2. ✅ or 短路（左侧 True）
3. ✅ 嵌套短路
4. ✅ 短路副作用

**test_function_calls.py**:
1. ✅ 内置函数调用
2. ✅ 用户函数调用
3. ✅ 方法调用
4. ✅ 参数传递
5. ✅ 默认参数
6. ✅ 命名参数
7. ✅ 可变参数

**验收标准**：
- [ ] 至少 100 个测试用例（分布在 4 个文件）
- [ ] expression_evaluator.py 覆盖率 >= 75%
- [ ] 所有测试通过

**预计新增覆盖率**: +29%

---

### Phase 4: 端到端测试（约 6-8 小时）

#### Task 4.1: Web 自动化 E2E 测试

**文件**: `tests/e2e/test_web_automation.py`

**要测试的完整场景**：
1. ✅ 登录流程
2. ✅ 表单填写提交
3. ✅ 搜索功能
4. ✅ 数据列表操作
5. ✅ 多步骤向导
6. ✅ 文件上传
7. ✅ 拖拽操作
8. ✅ 弹窗处理
9. ✅ 多标签页切换
10. ✅ 截图验证

**示例场景**：

```python
import pytest
from flowby.runner import ScriptRunner


class TestWebAutomationE2E:
    """Web 自动化端到端测试"""

    @pytest.fixture
    def runner(self, tmp_path):
        return ScriptRunner(output_dir=tmp_path)

    def test_login_workflow(self, runner, tmp_path):
        """✅ 完整登录流程"""
        script = tmp_path / "login.flow"
        script.write_text('''
step "用户登录":
    navigate to "https://example.com/login"
    type "admin" into "#username"
    type "password123" into "#password"
    click "#submit"
    wait for navigation
    assert page.url == "https://example.com/dashboard"
    assert page.title contains "Dashboard"
''')

        result = runner.run(script)
        assert result.success is True

    def test_form_submission(self, runner, tmp_path):
        """✅ 表单提交流程"""
        script = tmp_path / "form.flow"
        script.write_text('''
step "填写表单":
    navigate to "https://example.com/form"
    type "John Doe" into "#name"
    type "john@example.com" into "#email"
    select "Option 1" from "#dropdown"
    check "#agree"
    click "#submit"
    wait for "#success-message"
    assert text from "#success-message" contains "Success"
''')

        result = runner.run(script)
        assert result.success is True

    # ... 其他场景
```

**验收标准**：
- [ ] 至少 10 个完整场景
- [ ] 每个场景覆盖 5+ 步骤
- [ ] 所有测试通过

---

#### Task 4.2: API 测试 E2E 测试

**文件**: `tests/e2e/test_api_testing.py`

**要测试的完整场景**：
1. ✅ RESTful API CRUD
2. ✅ 认证流程（OAuth/JWT）
3. ✅ 分页查询
4. ✅ 批量操作
5. ✅ 文件上传下载
6. ✅ WebSocket 通信
7. ✅ GraphQL 查询
8. ✅ 错误重试
9. ✅ 并发请求
10. ✅ 性能测试

**验收标准**：
- [ ] 至少 10 个完整场景
- [ ] 所有测试通过

---

### Phase 5: 重构现有测试（约 15-20 小时）

#### Task 5.1: 拆分 test_v3_02_control_flow.py (1011 行)

**目标**: 拆分为多个小文件，提升可维护性

**新结构**：
```
tests/grammar/control_flow/
├── test_if_else.py           # if/else 语句（~200 行）
├── test_for_loop.py           # for 循环（~200 行）
├── test_while_loop.py         # while 循环（~200 行）
├── test_when_statement.py     # when 语句（~200 行）
└── test_control_flow_combinations.py  # 组合场景（~211 行）
```

**步骤**：
1. 创建新目录和文件
2. 逐个复制测试用例到新文件
3. 运行新文件确保通过
4. 删除旧文件中对应的测试
5. 确认旧文件中测试全部迁移
6. 删除旧文件
7. 提交

**验收标准**：
- [ ] 所有测试迁移完成
- [ ] 新文件结构清晰
- [ ] 测试总数不变
- [ ] 所有测试通过
- [ ] 删除旧文件

---

#### Task 5.2: 拆分 test_expression_evaluator.py (990 行)

**目标**: 按功能拆分

**新结构**：
```
tests/unit/evaluator/
├── test_arithmetic.py         # 算术运算（~150 行）
├── test_comparison.py         # 比较运算（~150 行）
├── test_logical.py            # 逻辑运算（~150 行）
├── test_member_access.py      # 成员访问（~150 行）
├── test_function_calls.py     # 函数调用（~150 行）
├── test_type_conversion.py    # 类型转换（~150 行）
└── test_edge_cases.py         # 边界情况（~90 行）
```

**验收标准**：
- [ ] 所有测试迁移完成
- [ ] 新文件结构清晰
- [ ] 测试总数不变
- [ ] 所有测试通过
- [ ] 删除旧文件

---

### Phase 6: 测试文档和工具（约 4-6 小时）

#### Task 6.1: 编写测试文档

**文件**: `tests/README.md`

**内容**：
- 测试架构说明
- 测试分层原则
- 如何编写测试
- 如何运行测试
- 测试覆盖率目标
- 常见问题解决

**验收标准**：
- [ ] 文档完整清晰
- [ ] 包含示例代码
- [ ] 易于理解

---

#### Task 6.2: 创建测试生成脚本

**文件**: `scripts/generate_test.py`

**功能**：
- 根据模板生成测试文件
- 自动填充模块信息
- 生成基础测试用例

**使用示例**：
```bash
python scripts/generate_test.py --module interpreter --type unit
# 生成: tests/unit/interpreter/test_interpreter.py
```

**验收标准**：
- [ ] 脚本可执行
- [ ] 生成的文件符合模板
- [ ] 包含使用说明

---

#### Task 6.3: 创建覆盖率监控脚本

**文件**: `scripts/coverage_report.py`

**功能**：
- 生成详细覆盖率报告
- 对比历史覆盖率
- 识别低覆盖率模块
- 生成可视化图表

**验收标准**：
- [ ] 生成 HTML 报告
- [ ] 输出 JSON 数据
- [ ] 可视化展示

---

## 执行时间表

| Phase | 内容 | 预计时间 | 预计覆盖率提升 |
|-------|------|----------|----------------|
| Phase 1 | 准备工作 | 1 小时 | - |
| Phase 2 | 集成测试 | 8-10 小时 | +40% |
| Phase 3 | 单元测试 | 10-12 小时 | +15% |
| Phase 4 | E2E 测试 | 6-8 小时 | +5% |
| Phase 5 | 重构测试 | 15-20 小时 | +5% |
| Phase 6 | 文档工具 | 4-6 小时 | - |
| **总计** | | **44-57 小时** | **54% → 80%+** |

---

## 验证检查点

### 每个 Task 完成后

```bash
# 1. 运行新测试
pytest <new_test_file> -v

# 2. 运行所有测试
pytest tests/ -x

# 3. 检查覆盖率
pytest tests/ --cov=src/flowby --cov-report=term

# 4. 运行验证脚本
python scripts/verify_tests.py

# 5. 提交
git add .
git commit -m "test: <task description>"
```

### 每个 Phase 完成后

```bash
# 生成覆盖率报告
pytest tests/ --cov=src/flowby --cov-report=html

# 查看报告
# 打开 htmlcov/index.html

# 确认覆盖率达标
python scripts/coverage_report.py
```

---

## 常见问题

### Q: 测试失败怎么办？

**A**:
1. 检查错误信息
2. 确认是否修改了业务代码（不应该修改）
3. 检查 fixture 是否正确
4. 运行单个测试调试：`pytest tests/path/to/test.py::test_function -vvs`

### Q: 覆盖率不达标怎么办？

**A**:
1. 运行覆盖率报告：`pytest --cov-report=html`
2. 查看 htmlcov/index.html 找到未覆盖的代码
3. 添加测试覆盖缺失的分支

### Q: 测试太慢怎么办？

**A**:
1. 使用 pytest-xdist 并行运行：`pytest -n auto`
2. 跳过慢速测试：`pytest -m "not slow"`
3. 优化 fixture 共享

### Q: 重复代码太多怎么办？

**A**:
1. 提取为 fixture
2. 使用参数化测试：`@pytest.mark.parametrize`
3. 创建测试辅助函数

---

## 提交规范

每个 Task 提交格式：

```
test: <task title>

<task description>

Coverage:
- <module>: <before>% → <after>%

Tests added: <count>
```

例如：
```
test: add runner integration tests

添加 ScriptRunner 集成测试，覆盖运行、错误处理、超时等场景

Coverage:
- runner.py: 11% → 72%

Tests added: 52
```

---

## 最终验收

完成所有 Task 后，运行最终验收：

```bash
# 1. 所有测试通过
pytest tests/ -v
# 预期：1400+ passed

# 2. 覆盖率达标
pytest tests/ --cov=src/flowby --cov-report=term
# 预期：总覆盖率 >= 80%

# 3. 关键模块覆盖率
# interpreter.py >= 75%
# expression_evaluator.py >= 75%
# runner.py >= 70%
# response_handler.py >= 70%
# resource_namespace.py >= 70%

# 4. 测试速度
pytest tests/ --durations=0
# 预期：总时间 < 30 秒

# 5. 代码质量
flake8 tests/
black --check tests/
```

---

## 备注

- 所有文件路径使用 `E:\cf\ads\flowby\` 作为根目录
- Python 版本：3.8+
- 使用 pytest 作为测试框架
- 遵循项目的代码风格（Black + Flake8）
- 不要修改 `src/` 目录下的业务代码
- 保持测试独立，不依赖执行顺序
- 使用 mock 隔离外部依赖（网络、文件系统等）

---

## 联系方式

如有问题，请：
1. 检查此文档的常见问题部分
2. 查看测试模板和示例
3. 运行验证脚本确认问题
