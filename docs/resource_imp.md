
   Resource 语法详解

   1. 用途

   resource 语句是 Flowby DSL v4.2 引入的核心特性，用于将 OpenAPI 规范转换为可直接调用的 API 客户端。它解决了以下问题：

   传统方式         │ resource 方式
   -------------+--------------------------------
   手动构建 HTTP 请求 │ 自动从 OpenAPI 生成方法
   手动处理认证       │ 内置多种认证方式
   手动处理错误重试     │ 内置弹性处理（retry + circuit breaker）
   测试时需要真实 API  │ 内置 Mock 模式

   2. 语法形式

   简单形式

   dsl
     resource user_api from "openapi/user-service.yml"

   完整形式（带配置）

   dsl
     resource user_api:
         spec: "openapi/user-service.yml"
         base_url: "https://api.example.com/v1"
         auth: {type: "bearer", token: env.API_TOKEN}
         timeout: 30
         headers: {"X-Client-ID": "flowby"}

   3. 实现架构

     ┌─────────────────┐
     │  DSL 脚本       │   resource user_api from "api.yml"
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │  Parser         │   _parse_resource() → ResourceStatement AST
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │  Interpreter    │   _execute_resource()
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │  OpenAPISpec    │   加载并解析 OpenAPI YAML/JSON
     │  (openapi_      │   提取 operationId → {path, method, params}
     │   loader.py)    │
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │ResourceNamespace│   动态生成每个 operationId 对应的方法
     │  (resource_     │   user_api.getUser(userId=123)
     │   namespace.py) │   user_api.createUser(name="Alice")
     └────────┬────────┘
              │
              ▼
     ┌─────────────────┐
     │  HTTP 请求      │   requests.get/post/put/delete
     │  + 认证处理     │   AuthHandler (Bearer/APIKey/Basic/OAuth2)
     │  + 弹性处理     │   ResilienceHandler (retry/circuit breaker)
     │  + Mock 处理    │   MockHandler (测试模式)
     └─────────────────┘

   4. 核心组件

   组件                    │ 文件                      │ 职责
   ----------------------+-------------------------+------------------------------------
   **ResourceStatement** │ `ast_nodes.py`          │ AST 节点，存储 name, spec_file, auth 等配置
   **OpenAPISpec**       │ `openapi_loader.py`     │ 加载/解析 OpenAPI 规范，提取 operations
   **ResourceNamespace** │ `resource_namespace.py` │ 动态生成 API 方法，执行 HTTP 请求
   **AuthHandler**       │ `auth_handler.py`       │ 处理 Bearer/APIKey/Basic/OAuth2 认证
   **ResilienceHandler** │ `resilience_handler.py` │ 处理重试和断路器
   **MockHandler**       │ `mock_handler.py`       │ 测试时返回模拟数据

   5. 使用示例

   dsl
     # 定义资源
     resource user_api from "openapi/user-service.yml"

     step "用户管理":
         # 调用 API（方法名 = OpenAPI 的 operationId）
         let user = user_api.getUser(userId=123)
         log f"用户: {user.name}"

         # POST 请求
         let new_user = user_api.createUser(
             name="Alice",
             email="alice@example.com"
         )

         # 断言
         assert new_user.id > 0

   6. OpenAPI 要求

   OpenAPI 规范必须包含 operationId：

   yaml
     openapi: 3.0.0
     info:
       title: User Service
       version: 1.0.0
     paths:
       /users/{userId}:
         get:
           operationId: getUser  # ← 必须！成为方法名
           parameters:
             - name: userId
               in: path
               required: true
           responses:
             '200':
               description: Success

   7. 五阶段实现

   Phase       │ 功能                             │ 状态
   ------------+--------------------------------+-------
   **Phase 1** │ 基础 OpenAPI 支持                  │ ✅ 已实现
   **Phase 2** │ 认证（Bearer/APIKey/Basic/OAuth2） │ ✅ 已实现
   **Phase 3** │ 响应映射与验证                        │ ✅ 已实现
   **Phase 4** │ 弹性处理（重试+断路器）                   │ ✅ 已实现
   **Phase 5** │ Mock 模式（测试支持）                  │ ✅ 已实现

   ──────────────────────────────────────────

   这是一个设计良好的 API 集成方案，将复杂的 HTTP 请求处理抽象为简单的方法调用，同时保持了类型安全（基于 OpenAPI
   规范）和可测试性（Mock 模式）。

