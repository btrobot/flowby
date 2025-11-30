# DSL v3.0 完整语法示例集（Python化版本）

"""
目标受众: Python程序员
展示所有73个语法特性的v3.0 Python风格示例
如果你会Python，这些代码应该看起来很熟悉！
"""

# ============================================================
# 1. 变量与赋值 (3 features)
# ============================================================

# 1.1 Let Declaration（DSL特有：显式声明）
let count = 0
let name = "Alice"
let score = 95.5
let active = True          # ✅ Python风格: True（首字母大写）
let items = [1, 2, 3]
let user = {name: "Bob", age: 30}

# 1.2 Const Declaration（DSL特有：真正的不可变）
const MAX_RETRY = 3
const API_URL = "https://api.example.com"
const TAX_RATE = 0.08

# 1.3 Assignment
count = count + 1
name = "Charlie"
score = score * 1.1

# ============================================================
# 2. 控制流 (4 features) - 完全Python化
# ============================================================

# 2.1 Step Block（删除 end step，像Python函数）
step "用户注册流程":
    navigate to "https://example.com/register"
    type "john@example.com" into "#email"
    type "SecurePass123" into "#password"
    click "#submit"
    wait for element "#success-message" to be visible
# ✅ 块结束由缩进决定，无需 end step

# 2.2 If-Else Block（删除 end if，完全像Python）
step "条件处理":
    if score >= 90:
        log "成绩优秀"
        const grade = "A"
    else if score >= 80:
        log "成绩良好"
        const grade = "B"
    else if score >= 70:
        log "成绩中等"
        const grade = "C"
    else:
        log "需要努力"
        const grade = "F"
    # ✅ 块结束由缩进决定，无需 end if

# 嵌套if示例
step "嵌套条件":
    if user.active:
        if user.role == "admin":
            navigate to "https://admin.example.com"
            log "管理员登录"
        else:
            navigate to "https://user.example.com"
            log "普通用户登录"
    else:
        log "账户未激活"

# 2.3 When-Otherwise Block（类似Python match/case，但更简洁）
step "状态处理":
    when order_status:
        "pending":
            log "订单待处理"
            click "#process-button"
        "processing":
            log "订单处理中"
            wait for element "#status-update"
        "completed":
            log "订单已完成"
            click "#download-invoice"
        "cancelled":
            log "订单已取消"
        otherwise:
            log "未知状态"
    # ✅ 块结束由缩进决定，无需 end when

# 2.4 For-Each Loop（完全像Python）
step "遍历处理":
    for item in items:
        log f"处理项目: {item}"    # ✅ f-string，像Python一样
        click item.selector
        wait 500ms
    # ✅ 块结束由缩进决定，无需 end for

# 复杂嵌套示例（5层嵌套，纯Python风格）
step "复杂嵌套控制流":
    for user in users:
        if user.active:
            when user.role:
                "admin":
                    log f"管理员: {user.name}"
                    navigate to user.admin_url
                "editor":
                    log f"编辑: {user.name}"
                    navigate to user.editor_url
                otherwise:
                    log f"访客: {user.name}"
        else:
            log f"跳过未激活用户: {user.name}"

# ============================================================
# 3. 导航 (3 features)
# ============================================================

# 3.1 Navigate To
step "页面导航":
    navigate to "https://example.com"
    navigate to "https://example.com/login"
    navigate to "https://example.com/dashboard" wait for networkidle
    navigate to config.base_url    # ✅ 无$前缀，像Python对象

# 3.2 Go Back/Forward
step "浏览器历史":
    navigate to "https://example.com/page1"
    navigate to "https://example.com/page2"
    go back
    go forward

# 3.3 Reload
step "页面刷新":
    navigate to "https://example.com"
    reload

# ============================================================
# 4. 等待 (3 features)
# ============================================================

# 4.1 Wait Duration
step "时间等待":
    wait 5s
    wait for 1000ms
    wait 2 seconds
    wait 500 milliseconds

# 4.2 Wait Element
step "元素等待":
    wait for element "#button"
    wait for element ".loading" to be hidden
    wait for element "#modal" to be visible
    wait for element "#item" to be attached
    wait for element "#deleted" to be detached
    wait for element "#delayed" timeout 10s

# 4.3 Wait Navigation
step "导航等待":
    click "#submit"
    wait for navigation
    wait for navigation wait for networkidle
    wait for navigation to "https://example.com/success"

# ============================================================
# 5. 选择 (2 features)
# ============================================================

# 5.1 Select Element
step "元素选择":
    select "input" where name equals "username"
    select "button" where text contains "Submit"
    select "a" where href contains "/admin"
    select "img" where src contains "logo"
    select "div" where class equals "active" and id contains "main"

# 5.2 Select Option
step "下拉选择":
    select option "China" from "#country"
    select option "English" from ".language-selector"
    select option country_code from "#country-select"

# ============================================================
# 6. 动作 (10 features)
# ============================================================

# 6.1 Type
step "文本输入":
    type "john@example.com" into "#email"
    type password into "#password"
    type "Hello World" slowly
    type "Quick text" fast

# 6.2 Click
step "点击操作":
    click
    click "#submit-button"
    click ".nav-item:first-child"

# 6.3 Double Click
step "双击操作":
    double click "#file-item"
    double click ".editable-field"

# 6.4 Right Click
step "右键操作":
    right click "#context-menu-trigger"
    right click ".file-item"

# 6.5 Hover
step "悬停操作":
    hover over "#menu-item"
    hover over ".tooltip-trigger"

# 6.6 Clear
step "清除输入":
    clear "#search-box"
    clear ".input-field"

# 6.7 Press
step "按键操作":
    press Enter
    press Tab
    press Escape
    press Space
    press ArrowDown
    press ArrowUp

# 6.8 Scroll
step "滚动操作":
    scroll to top
    scroll to bottom
    scroll to "#section"
    scroll to 500

# 6.9 Check/Uncheck
step "复选框操作":
    check "#agree-terms"
    uncheck "#newsletter"
    check ".option-checkbox"

# 6.10 Upload
step "文件上传":
    upload file "/path/to/file.pdf" to "#file-input"
    upload file avatar_path to ".avatar-upload"

# ============================================================
# 7. 断言 (通用表达式断言)
# ============================================================

step "断言验证":
    # 通用表达式断言（Python风格）
    assert page.url == "https://example.com/success"    # ✅ 无$前缀
    assert score >= 60, "分数不及格"
    assert user.name != None    # ✅ None（Python风格）
    assert items.length > 0

    # 复杂表达式断言
    assert (score >= 90 and attendance > 80) or extra_credit == True
    assert Math.abs(result - expected) < 0.01

# ============================================================
# 8. 服务调用 (1 feature)
# ============================================================

step "服务调用":
    # HTTP服务
    call "http.get" with url: "https://api.example.com/data" into response
    call "http.post" with url: api_url, body: {name: "Test"} into result

    # Random服务
    call "random.email" into test_email
    call "random.password" with length: 16 into password
    call "random.username" into username
    call "random.phone" into phone_number
    call "random.number" with min: 1, max: 100 into random_num
    call "random.uuid" into uuid

    # 使用服务返回值（f-string）
    log f"随机邮箱: {test_email}"    # ✅ f-string，像Python
    type test_email into "#email"

# ============================================================
# 9. 数据提取 (1 feature)
# ============================================================

step "数据提取":
    # 提取文本
    extract text from "#title" into page_title
    extract text from ".description" into desc

    # 提取值
    extract value from "#input-field" into input_value

    # 提取属性
    extract attr "href" from "#link" into link_url
    extract attr "src" from "img.logo" into logo_src
    extract attr "data-id" from ".item" into item_id

    # Pattern提取（正则表达式）
    extract text from "#code" pattern "\\d{6}" into verification_code

    # 使用提取的数据（f-string）
    log f"页面标题: {page_title}"
    assert page_title contains "Welcome"

# ============================================================
# 10. 工具 (2 features)
# ============================================================

# 10.1 Log（支持f-string）
step "日志输出":
    log "开始测试"
    log f"用户名: {username}"                   # ✅ f-string
    log f"分数: {score}, 等级: {grade}"
    log f"计算结果: {x + y * 2}"
    log f"当前时间: {Date.now()}"
    log f"环境: {env.ENVIRONMENT}"              # ✅ 无$前缀

# 10.2 Screenshot
step "截图操作":
    # 全屏截图
    screenshot
    screenshot fullpage

    # 指定名称
    screenshot as "homepage"
    screenshot as "login-page"

    # 元素截图
    screenshot of "#main-content"
    screenshot of ".modal" as "modal-view"

    # 全页面元素截图
    screenshot of "body" fullpage as "full-page"

    # 使用变量
    screenshot of selector as screenshot_name

# ============================================================
# 数据类型展示（Python对齐）
# ============================================================

step "数据类型示例":
    # 布尔值（Python风格：首字母大写）
    let bool1 = True     # ✅ 不是 true
    let bool2 = False    # ✅ 不是 false

    # None（Python风格）
    let nil = None       # ✅ 不是 null
    let maybe = None

    # 字符串与f-string
    let str1 = "普通字符串"
    let str2 = f"插值字符串: {count}"              # ✅ f前缀
    let str3 = f"表达式: {x + y}"
    let str4 = f"嵌套: {user.name} - {user.age}"
    let str5 = "字面量 {count}"                   # 不插值（无f）

    # 数字（与Python相同）
    let int1 = 42
    let float1 = 3.14
    let neg = -10

    # 数组（与Python列表相同）
    let arr1 = []
    let arr2 = [1, 2, 3]
    let arr3 = ["a", "b", "c"]
    let arr4 = [True, False, None]               # ✅ Python风格
    let arr5 = [1, "text", True, None]
    let nested = [[1, 2], [3, 4]]

    # 对象（类似Python dict，键可无引号）
    let obj1 = {}
    let obj2 = {name: "Alice"}                   # 键无引号（简洁）
    let obj3 = {name: "Bob", age: 30}
    let obj4 = {active: True, data: None}        # ✅ Python风格
    let obj5 = {"first-name": "Alice"}           # 特殊字符需引号
    let nested_obj = {user: {name: "Alice", verified: False}}

# ============================================================
# 系统变量（去掉$前缀，像Python内置对象）
# ============================================================

step "系统变量示例":
    # context命名空间（类似Python的上下文对象）
    log f"任务ID: {context.task_id}"             # ✅ 无$前缀
    log f"执行ID: {context.execution_id}"
    log f"开始时间: {context.start_time}"
    log f"步骤名称: {context.step_name}"
    log f"状态: {context.status}"

    # page命名空间（当前页面信息）
    log f"当前URL: {page.url}"                   # ✅ 无$前缀
    log f"页面标题: {page.title}"
    log f"页面来源: {page.origin}"
    assert page.url == "https://example.com/dashboard"

    # browser命名空间（浏览器信息）
    log f"浏览器: {browser.name}"                 # ✅ 无$前缀
    log f"版本: {browser.version}"
    if browser.name == "chromium":
        log "使用Chromium浏览器"

    # env命名空间（环境变量，类似os.environ）
    log f"API Key: {env.API_KEY}"                # ✅ 无$前缀
    log f"Database: {env.DATABASE_URL}"
    let api_key = env.API_KEY

    # config命名空间（配置）
    log f"Base URL: {config.base_url}"           # ✅ 无$前缀
    log f"Timeout: {config.timeout}"
    let base_url = config.base_url
    navigate to base_url

    # 组合使用
    log f"用户 {user.name} 在 {browser.name} 浏览器中访问 {page.url}"

# ============================================================
# 内置函数 (19个函数 - Python风格命名)
# ============================================================

step "内置函数示例":
    # Math命名空间（类似Python的math模块）
    let abs_val = Math.abs(-5)           # 5
    let rounded = Math.round(3.7)        # 4
    let ceiling = Math.ceil(3.2)         # 4
    let floor = Math.floor(3.8)          # 3
    let max_val = Math.max(1, 5, 3)     # 5
    let min_val = Math.min(1, 5, 3)     # 1
    let random = Math.random()           # 0.0-1.0
    let power = Math.pow(2, 3)           # 8
    let sqrt = Math.sqrt(16)             # 4

    # 嵌套使用
    let complex_calc = Math.abs(Math.min(-5, -10)) + Math.max(3, 7)

    # Date命名空间
    let now = Date.now()                 # 当前时间戳
    let formatted = Date.format("YYYY-MM-DD")
    let from_ts = Date.from_timestamp(1609459200)

    log f"当前时间戳: {now}"
    log f"格式化日期: {formatted}"

    # JSON命名空间（类似Python的json模块）
    let json_str = JSON.stringify({name: "Alice", age: 30})
    let json_obj = JSON.parse('{"key": "value"}')

    log f"JSON字符串: {json_str}"

    # 全局函数（类似Python的内置函数）
    let num = Number("42")               # 42（类似int()）
    let str = String(123)                # "123"（类似str()）
    let bool = Boolean(1)                # True（类似bool()）
    let is_nan = isNaN("abc")            # True
    let is_finite = isFinite(100)        # True

    # 条件中使用
    if isNaN(user_input):
        log "输入不是数字"

    # 类型转换工作流
    let user_age = Number(age_string)
    if isFinite(user_age) and user_age >= 18:
        log "成年用户"

# ============================================================
# 注释语法（Python风格）
# ============================================================

step "注释示例":
    # 这是行注释（与Python相同）
    let x = 1  # 行尾注释

    """
    这是块注释（三引号）
    跨越多行
    类似Python的docstring
    ✅ 不再使用 /* */ 风格
    """

    let y = 2

# ============================================================
# 复杂综合示例（展示Python风格一致性）
# ============================================================

step "用户登录与验证流程":
    """完整的登录流程示例"""

    # 导航到登录页
    navigate to config.login_url wait for networkidle

    # 验证页面
    assert page.url contains "/login"
    assert page.title == "用户登录"

    # 截图记录
    screenshot as "login-page-initial"

    # 生成测试数据
    call "random.email" into test_email
    call "random.password" with length: 16 into test_password

    log f"使用测试账号: {test_email}"    # ✅ f-string

    # 填写表单
    type test_email into "#email" slowly
    type test_password into "#password"
    check "#remember-me"

    # 提交表单
    click "#submit-button"
    wait for navigation wait for networkidle

    # 验证登录成功
    wait for element "#dashboard" to be visible timeout 10s
    assert page.url == config.base_url + "/dashboard"

    # 提取用户信息
    extract text from "#username" into display_name
    extract attr "src" from "#avatar" into avatar_url

    log f"登录成功: {display_name}"
    screenshot of "#user-panel" as "user-panel-logged-in"

    # 条件处理
    if display_name == "Admin":
        log "管理员登录"
        navigate to config.admin_url
    else:
        log "普通用户登录"

    # 数据验证
    call "http.get" with url: config.api_url + "/user/profile" into profile
    let profile_data = JSON.parse(profile)

    assert profile_data.email == test_email
    assert isFinite(profile_data.login_count)

    log "用户资料验证完成"

step "数据处理与分析（Python风格）":
    """展示DSL的Python相似性"""

    # 初始化数据
    let scores = [85, 92, 78, 95, 88]
    let students = [
        {name: "Alice", score: 85, active: True},
        {name: "Bob", score: 92, active: True},
        {name: "Charlie", score: 78, active: False}
    ]

    # 计算统计
    let sum = 0
    let count = 0

    for score in scores:
        sum = sum + score
        count = count + 1

    let average = sum / count
    let rounded_avg = Math.round(average)

    log f"平均分: {rounded_avg}"    # ✅ f-string

    # 分类统计
    let excellent = 0
    let good = 0
    let pass = 0

    for student in students:
        if student.active:    # ✅ 直接访问属性，像Python
            if student.score >= 90:
                excellent = excellent + 1
                log f"{student.name}: 优秀 ({student.score})"
            else if student.score >= 80:
                good = good + 1
                log f"{student.name}: 良好 ({student.score})"
            else if student.score >= 60:
                pass = pass + 1
                log f"{student.name}: 及格 ({student.score})"
            else:
                log f"{student.name}: 不及格 ({student.score})"
        else:
            log f"{student.name}: 未激活，跳过"

    # 生成报告
    let report = {
        total: count,
        average: rounded_avg,
        excellent: excellent,
        good: good,
        pass: pass,
        completed: True    # ✅ Python风格布尔值
    }

    let report_json = JSON.stringify(report)
    log f"统计报告: {report_json}"

    # 断言验证
    assert count == scores.length
    assert average >= 60
    assert excellent + good + pass <= count

# ============================================================
# v3.0 Python风格展示（5层嵌套）
# ============================================================

step "深度嵌套示例（纯Python风格）":
    """
    展示v3.0如何像Python一样处理深度嵌套
    无需任何end关键字，完全用缩进
    """

    log "开始深度嵌套处理"

    for user in users:
        log f"处理用户: {user.name}"

        if user.active:
            log "用户活跃"

            when user.status:
                "premium":
                    log "高级用户"

                    if user.credits > 100:
                        log "积分充足"
                        call "service.upgrade" into result
                    else:
                        log "积分不足"

                "standard":
                    log "标准用户"

                otherwise:
                    log "其他类型用户"

        else:
            log "用户不活跃"

    log "处理完成"

# ============================================================
# Python程序员对比示例
# ============================================================

"""
如果你是Python程序员，对比以下代码：
"""

step "Python vs DSL 对比":
    # Python代码会这样写：
    # if user["active"]:
    #     print(f"User: {user['name']}")

    # DSL代码（几乎相同）：
    if user.active:
        log f"User: {user.name}"

    # Python代码会这样写：
    # for item in items:
    #     if item > 0:
    #         print(f"Positive: {item}")

    # DSL代码（完全相同！）：
    for item in items:
        if item > 0:
            log f"Positive: {item}"

    # Python代码会这样写：
    # data = {"name": "Alice", "active": True}
    # if data["active"]:
    #     print(data["name"])

    # DSL代码（更简洁）：
    let data = {name: "Alice", active: True}    # 键无需引号
    if data.active:                              # 点号访问
        log data.name

# ============================================================
# 总结：DSL v3.0 的Python化程度
# ============================================================

"""
Python程序员5分钟上手总结：

✅ 完全相同（零学习成本）：
   - if/else/for 语法
   - True/False/None
   - f-string 插值
   - 缩进块（4空格）
   - and/or/not 运算符
   - 注释 # 和 三引号
   - 数组 [1, 2, 3]
   - 数学运算

⚠️ 小差异（5分钟学会）：
   - let x = 1（声明变量）
   - const MAX = 1（常量）
   - when x: "val":（模式匹配）
   - step "name":（步骤块）
   - page.url, env.API_KEY（内置对象）

📊 Python对齐度：93%+
如果你会Python，你已经会了DSL的90%！
"""

log "DSL v3.0 示例集完成"
log f"总计展示特性: 73个"
log "核心设计：为Python程序员设计，最小化学习成本"
