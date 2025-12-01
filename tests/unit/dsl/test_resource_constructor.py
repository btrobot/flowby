"""
Resource() 构造函数单元测试 (v6.0)

测试 Resource() 内置函数的所有功能：
- 基本用法
- 参数验证
- 错误处理
- 配置选项
"""

import pytest

from flowby.lexer import Lexer
from flowby.parser import Parser
from flowby.interpreter import Interpreter
from flowby.context import ExecutionContext
from flowby.errors import ExecutionError
from flowby.builtin_functions import Resource


class TestResourceConstructorBasic:
    """测试 Resource() 构造函数的基本功能"""

    def test_resource_function_exists_in_builtins(self):
        """测试 Resource 函数在 BUILTIN_FUNCTIONS 中注册"""
        from flowby.builtin_functions import BUILTIN_FUNCTIONS

        assert "Resource" in BUILTIN_FUNCTIONS
        assert BUILTIN_FUNCTIONS["Resource"] == Resource

    def test_resource_constructor_with_valid_spec(self, tmp_path):
        """测试使用有效 OpenAPI 规范创建 Resource"""
        # 创建测试 OpenAPI 规范
        spec_file = tmp_path / "test_api.yml"
        spec_file.write_text(
            """
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths:
  /users:
    get:
      operationId: getUsers
      responses:
        '200':
          description: OK
"""
        )

        # 创建执行上下文
        context = ExecutionContext(task_id="test_123")
        context.script_path = str(tmp_path)

        # 调用 Resource()
        api = Resource(str(spec_file), context=context)

        # 验证返回的是 ResourceNamespace
        from flowby.resource_namespace import ResourceNamespace

        assert isinstance(api, ResourceNamespace)
        assert api.name == f"Resource({spec_file})"

    def test_resource_constructor_dsl_syntax(self, tmp_path):
        """测试通过 DSL 语法调用 Resource()"""
        # 创建测试 OpenAPI 规范
        spec_file = tmp_path / "api.yml"
        spec_file.write_text(
            """
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths:
  /test:
    get:
      operationId: test
      responses:
        '200':
          description: OK
"""
        )

        # DSL 代码 - 使用 POSIX 路径避免 Windows 反斜杠问题
        spec_path = spec_file.as_posix()
        source = f"""
let api = Resource("{spec_path}")
log "Resource created"
"""

        # 执行
        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        context = ExecutionContext(task_id="test")
        context.script_path = str(tmp_path)
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        # 验证变量已定义
        from flowby.resource_namespace import ResourceNamespace

        api = interpreter.symbol_table.get("api", line_number=0)
        assert isinstance(api, ResourceNamespace)


class TestResourceConstructorParameters:
    """测试 Resource() 构造函数的参数"""

    def test_resource_with_base_url(self, tmp_path):
        """测试带 base_url 参数"""
        spec_file = tmp_path / "api.yml"
        spec_file.write_text(
            """
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths: {}
"""
        )

        spec_path = spec_file.as_posix()
        source = f"""
let api = Resource("{spec_path}", base_url = "https://api.example.com")
"""

        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        context = ExecutionContext(task_id="test")
        context.script_path = str(tmp_path)
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        api = interpreter.symbol_table.get("api", line_number=0)
        assert api.base_url == "https://api.example.com"

    def test_resource_with_timeout(self, tmp_path):
        """测试带 timeout 参数"""
        spec_file = tmp_path / "api.yml"
        spec_file.write_text(
            """
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths: {}
"""
        )

        spec_path = spec_file.as_posix()
        source = f"""
let api = Resource("{spec_path}", timeout = 60)
"""

        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        context = ExecutionContext(task_id="test")
        context.script_path = str(tmp_path)
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        api = interpreter.symbol_table.get("api", line_number=0)
        assert api.timeout == 60

    def test_resource_with_auth(self, tmp_path):
        """测试带 auth 参数"""
        spec_file = tmp_path / "api.yml"
        spec_file.write_text(
            """
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths: {}
"""
        )

        spec_path = spec_file.as_posix()
        source = f"""
let api = Resource("{spec_path}",
    auth = {{type: "bearer", token: "test_token"}}
)
"""

        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        context = ExecutionContext(task_id="test")
        context.script_path = str(tmp_path)
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        api = interpreter.symbol_table.get("api", line_number=0)
        # ResourceNamespace 创建成功即可，参数已内部配置
        from flowby.resource_namespace import ResourceNamespace

        assert isinstance(api, ResourceNamespace)

    def test_resource_with_multiple_params(self, tmp_path):
        """测试带多个参数"""
        spec_file = tmp_path / "api.yml"
        spec_file.write_text(
            """
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths: {}
"""
        )

        spec_path = spec_file.as_posix()
        source = f"""
let api = Resource("{spec_path}",
    base_url = "https://api.example.com",
    timeout = 60,
    headers = {{"X-Client": "test"}}
)
"""

        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        context = ExecutionContext(task_id="test")
        context.script_path = str(tmp_path)
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        api = interpreter.symbol_table.get("api", line_number=0)
        # ResourceNamespace 创建成功，验证 base_url 和 timeout 传递正确
        assert api.base_url == "https://api.example.com"
        assert api.timeout == 60
        # headers 是内部配置，不直接暴露为属性，创建成功即可
        from flowby.resource_namespace import ResourceNamespace

        assert isinstance(api, ResourceNamespace)


class TestResourceConstructorValidation:
    """测试 Resource() 构造函数的参数验证"""

    def test_resource_without_spec_file_raises_error(self):
        """测试缺少 spec_file 参数抛出错误"""
        context = ExecutionContext(task_id="test")

        with pytest.raises(ExecutionError) as exc_info:
            Resource("", context=context)

        assert "spec_file 必须是非空字符串" in str(exc_info.value)

    def test_resource_with_invalid_spec_file_type(self):
        """测试 spec_file 参数类型错误"""
        context = ExecutionContext(task_id="test")

        with pytest.raises(ExecutionError) as exc_info:
            Resource(123, context=context)

        assert "spec_file 必须是非空字符串" in str(exc_info.value)

    def test_resource_with_none_spec_file(self):
        """测试 spec_file 为 None"""
        context = ExecutionContext(task_id="test")

        with pytest.raises(ExecutionError) as exc_info:
            Resource(None, context=context)

        assert "spec_file 必须是非空字符串" in str(exc_info.value)

    def test_resource_without_context_raises_error(self):
        """测试缺少 context 参数抛出错误"""
        with pytest.raises(ExecutionError) as exc_info:
            Resource("test.yml", context=None)

        assert "Resource() 函数需要执行上下文" in str(exc_info.value)

    def test_resource_with_nonexistent_file(self, tmp_path):
        """测试文件不存在抛出错误"""
        context = ExecutionContext(task_id="test")
        context.script_path = str(tmp_path)
        nonexistent_file = tmp_path / "nonexistent.yml"

        with pytest.raises(ExecutionError) as exc_info:
            Resource(str(nonexistent_file), context=context)

        assert "OpenAPI 规范文件未找到" in str(exc_info.value)


class TestResourceConstructorErrorHandling:
    """测试 Resource() 构造函数的错误处理"""

    def test_resource_with_invalid_yaml_format(self, tmp_path):
        """测试无效的 YAML 格式"""
        spec_file = tmp_path / "invalid.yml"
        spec_file.write_text("invalid: yaml: syntax:")

        context = ExecutionContext(task_id="test")
        context.script_path = str(tmp_path)

        with pytest.raises(ExecutionError) as exc_info:
            Resource(str(spec_file), context=context)

        assert "创建 Resource 失败" in str(exc_info.value)

    def test_resource_dsl_error_handling(self, tmp_path):
        """测试 DSL 中的错误处理"""
        # 不存在的文件
        source = """
let api = Resource("nonexistent.yml")
"""

        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        context = ExecutionContext(task_id="test")
        context.script_path = str(tmp_path)
        interpreter = Interpreter(context)

        with pytest.raises(ExecutionError) as exc_info:
            interpreter.execute(ast)

        assert "OpenAPI 规范文件未找到" in str(exc_info.value)


class TestResourceConstructorDynamicUsage:
    """测试 Resource() 构造函数的动态使用场景"""

    def test_resource_with_dynamic_token(self, tmp_path):
        """测试使用动态 token"""
        spec_file = tmp_path / "api.yml"
        spec_file.write_text(
            """
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths: {}
"""
        )

        spec_path = spec_file.as_posix()
        source = f"""
let token = "dynamic_token_123"
let api = Resource("{spec_path}",
    auth = {{type: "bearer", token: token}}
)
"""

        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        context = ExecutionContext(task_id="test")
        context.script_path = str(tmp_path)
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        api = interpreter.symbol_table.get("api", line_number=0)
        # ResourceNamespace 创建成功，动态 token 已传递
        from flowby.resource_namespace import ResourceNamespace

        assert isinstance(api, ResourceNamespace)

    def test_resource_in_conditional(self, tmp_path):
        """测试在条件语句中创建 Resource"""
        spec_file = tmp_path / "api.yml"
        spec_file.write_text(
            """
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths: {}
"""
        )

        spec_path = spec_file.as_posix()
        # 修改：在 if 块外声明变量
        source = f"""
let is_prod = True
let api = None
if is_prod:
    api = Resource("{spec_path}", base_url = "https://prod.example.com")
else:
    api = Resource("{spec_path}", base_url = "https://dev.example.com")
"""

        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        context = ExecutionContext(task_id="test")
        context.script_path = str(tmp_path)
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        api = interpreter.symbol_table.get("api", line_number=0)
        assert api.base_url == "https://prod.example.com"

    def test_resource_multiple_instances(self, tmp_path):
        """测试创建多个 Resource 实例"""
        spec_file = tmp_path / "api.yml"
        spec_file.write_text(
            """
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths: {}
"""
        )

        spec_path = spec_file.as_posix()
        source = f"""
let dev_api = Resource("{spec_path}", base_url = "https://dev.example.com")
let prod_api = Resource("{spec_path}", base_url = "https://prod.example.com")
"""

        tokens = Lexer().tokenize(source)
        ast = Parser().parse(tokens)
        context = ExecutionContext(task_id="test")
        context.script_path = str(tmp_path)
        interpreter = Interpreter(context)
        interpreter.execute(ast)

        dev_api = interpreter.symbol_table.get("dev_api", line_number=0)
        prod_api = interpreter.symbol_table.get("prod_api", line_number=0)

        assert dev_api.base_url == "https://dev.example.com"
        assert prod_api.base_url == "https://prod.example.com"
        assert dev_api is not prod_api  # 不同的实例
