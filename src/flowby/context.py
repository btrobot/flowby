"""
执行上下文

ExecutionContext 是 DSL 解释器执行的核心，包含了执行过程中的所有状态。

关键设计原则:
    1. 实例隔离 - 每个任务创建独立的 ExecutionContext 实例
    2. 无全局状态 - 所有状态存储在实例中
    3. 线程安全 - 多个实例可以并发执行互不干扰
"""

import logging
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from playwright.sync_api import Page, Locator

from .settings import Settings
from .errors import ExecutionError
from .diagnosis import DiagnosisManager, DiagnosisConfig, DEFAULT_DIAGNOSIS_CONFIG
from .diagnosis.listeners import DiagnosisListeners
from .diagnosis.cleanup import DiagnosisCleanup
from .config.schema import ServicesConfig


class ExecutionStatus(Enum):
    """
    执行状态枚举

    表示执行上下文的当前状态
    """
    PENDING = "pending"      # 等待开始
    RUNNING = "running"      # 正在执行
    COMPLETED = "completed"  # 执行完成
    FAILED = "failed"        # 执行失败
    CANCELLED = "cancelled"  # 已取消


@dataclass
class ExecutionRecord:
    """
    执行记录

    记录单个语句的执行信息

    Attributes:
        timestamp: 执行时间戳
        type: 记录类型（statement, step_start, step_end, error）
        content: 记录内容
        duration: 执行耗时（秒，可选）
        success: 是否成功（可选）
    """
    timestamp: float
    type: str
    content: str
    duration: Optional[float] = None
    success: Optional[bool] = None


class ScreenshotManager:
    """
    截图管理器（按日期和任务组织）

    为每个任务提供截图功能，截图按日期-任务目录组织

    目录结构：screenshots/YYYY-MM-DD/task-{task_id_short}-{timestamp}/

    Attributes:
        task_id: 任务 ID
        script_name: 脚本名称
        screenshot_dir: 截图目录（任务专属目录）
        screenshots: 已捕获的截图列表
    """

    def __init__(self, task_id: str, script_name: str = 'unnamed'):
        """
        初始化截图管理器

        Args:
            task_id: 唯一任务 ID
            script_name: 脚本名称（用于文件命名）
        """
        self.task_id = task_id
        self.script_name = script_name

        # 按日期和任务组织：screenshots/YYYY-MM-DD/task-{task_id_short}-{timestamp}/
        from datetime import datetime
        now = datetime.now()
        date_dir = Settings.SCREENSHOTS_DIR / now.strftime("%Y-%m-%d")

        # 创建任务专属子目录：task-{task_id_short}-{timestamp}
        short_id = task_id[:8]
        timestamp = now.strftime("%H%M%S")
        task_dir = date_dir / f"task-{short_id}-{timestamp}"
        task_dir.mkdir(parents=True, exist_ok=True)

        self.screenshot_dir = task_dir

        self.screenshots: List[str] = []

    def capture(self, page: Page, name: str, fullpage: bool = False) -> str:
        """
        捕获截图

        Args:
            page: Playwright Page 对象
            name: 截图描述
            fullpage: 是否全页面截图

        Returns:
            截图文件的完整路径
        """
        from datetime import datetime

        # 文件名格式: scriptname_HHMMSS_shortid_description.png
        timestamp = datetime.now().strftime("%H%M%S")
        short_id = self.task_id[:8]
        filename = f"{self.script_name}_{timestamp}_{short_id}_{name}.png"
        filepath = self.screenshot_dir / filename

        # 捕获截图
        page.screenshot(path=str(filepath), full_page=fullpage, type='png')

        # 记录
        self.screenshots.append(str(filepath))

        return str(filepath)

    def capture_on_error(self, page: Page, error_type: str, line: int) -> str:
        """
        捕获错误时的截图

        Args:
            page: Playwright Page 对象
            error_type: 错误类型
            line: 错误发生的行号

        Returns:
            截图文件的完整路径
        """
        name = f"error_{error_type}_line_{line}"
        return self.capture(page, name, fullpage=True)


class ExecutionContext:
    """
    执行上下文

    包含 DSL 解释器执行过程中的所有状态

    关键原则:
        - 每个任务创建独立的实例
        - 所有状态存储在实例中（无全局变量）
        - 支持并发执行（多个实例互不干扰）

    Attributes:
        task_id: 唯一任务 ID
        status: 执行状态（PENDING/RUNNING/COMPLETED/FAILED/CANCELLED）
        is_interactive: 是否交互模式（v5.1，默认 True）
        variables: 变量存储
        page: Playwright Page 对象
        playwright_wrapper: Playwright 包装器
        browser_name: 浏览器名称 (chromium/firefox/webkit)
        current_element: 当前选中的元素
        execution_history: 执行历史记录
        screenshots: 截图列表
        current_step: 当前步骤名称
        logger: 任务专用日志器
        screenshot_manager: 截图管理器
    """

    def __init__(
        self,
        task_id: str,
        variables: Optional[Dict[str, Any]] = None,
        services_config: Optional[ServicesConfig] = None,
        browser_name: str = 'chromium',
        script_name: str = 'unnamed',
        script_path: Optional[str] = None,
        is_interactive: bool = True
    ):
        """
        初始化执行上下文

        Args:
            task_id: 唯一任务 ID（建议使用 UUID）
            variables: 初始变量字典（将被深拷贝）
            services_config: 服务配置（可选）
            browser_name: 浏览器名称 (chromium/firefox/webkit，默认 chromium)
            script_name: 脚本名称（用于日志文件命名，默认 "unnamed"）
            script_path: 脚本文件路径（用于确定 .env 位置，v4.2.1）
            is_interactive: 是否交互模式（v5.1，默认 True，CI/CD 应设为 False）
        """
        # === 任务标识 ===
        self.task_id = task_id
        self.script_name = script_name
        self.script_path = script_path

        # === 加载环境变量（v4.2.1）===
        self._load_env_files(script_path)

        # === 执行状态 ===
        self.status: ExecutionStatus = ExecutionStatus.PENDING
        self.is_interactive: bool = is_interactive  # v5.1: 交互模式标志

        # === 变量存储（深拷贝，避免共享） ===
        self.variables: Dict[str, Any] = self._deep_copy_dict(variables or {})

        # === 浏览器相关（每个任务独立） ===
        self.browser_name = browser_name  # 浏览器名称
        self.page: Optional[Page] = None
        self.playwright_wrapper: Optional[Any] = None  # AdsPowerPlaywright 实例
        self.current_element: Optional[Locator] = None

        # === 执行追踪（每个任务独立） ===
        self.execution_history: List[ExecutionRecord] = []
        self.screenshots: List[str] = []
        self.current_step: Optional[str] = None

        # === 日志器（独立的日志文件） ===
        self.logger = self._create_logger(task_id, script_name)

        # === 截图管理器（按日期-任务目录组织） ===
        self.screenshot_manager = ScreenshotManager(task_id, script_name)

        # === 诊断管理器 ===
        self.diagnosis_config = DEFAULT_DIAGNOSIS_CONFIG
        self.diagnosis_manager = DiagnosisManager(
            config=self.diagnosis_config,
            base_dir=str(Settings.SCREENSHOTS_DIR)
        )
        self.diagnosis_listeners: Optional[DiagnosisListeners] = None

        # === 服务注册中心 ===
        self.service_registry = None
        if services_config:
            from .services import ServiceRegistry
            self.service_registry = ServiceRegistry(services_config)
            self.service_registry.initialize()

    def _load_env_files(self, script_path: Optional[str] = None):
        """
        加载环境变量文件（v4.2.1）

        支持多环境配置：
        1. .env（默认配置）
        2. .env.local（本地配置，覆盖 .env）
        3. .env.{ENV}（特定环境，如 .env.production）
        4. 系统环境变量（最高优先级，不会被覆盖）

        Args:
            script_path: 脚本文件路径（用于确定 .env 位置）
        """
        try:
            from .env_loader import EnvLoader

            # 使用多环境加载策略
            # 注意：此时 logger 还未创建，不传递 logger 参数
            EnvLoader.load_with_environments(script_path=script_path, logger=None)

        except ImportError:
            # python-dotenv 未安装，跳过
            pass
        except Exception as e:
            # 环境变量加载失败不应阻止脚本执行
            import sys
            print(f"[警告] 加载环境变量失败: {e}", file=sys.stderr)

    def _deep_copy_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """
        深拷贝字典（避免引用共享）

        Args:
            d: 原始字典

        Returns:
            深拷贝后的字典
        """
        import copy
        return copy.deepcopy(d)

    def _create_logger(self, task_id: str, script_name: str = 'unnamed') -> logging.Logger:
        """
        创建任务专用日志器（按日期组织）

        日志文件路径: logs/YYYY-MM-DD/scriptname_HHMMSS_shortid.log

        Args:
            task_id: 任务 ID
            script_name: 脚本名称（用于文件命名）

        Returns:
            配置好的日志器
        """
        from datetime import datetime

        logger = logging.getLogger(f"dsl.task.{task_id}")

        # 避免重复添加 handler
        if logger.handlers:
            return logger

        logger.setLevel(logging.INFO)
        logger.propagate = False  # 不传播到父 logger

        # 控制台 handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            f'[{task_id[:8]}] [%(levelname)s] %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # 文件 handler（按日期组织）
        now = datetime.now()
        date_dir = Settings.LOGS_DIR / now.strftime("%Y-%m-%d")
        date_dir.mkdir(parents=True, exist_ok=True)

        # 文件名: scriptname_HHMMSS_shortid.log
        timestamp = now.strftime("%H%M%S")
        short_id = task_id[:8]
        log_filename = f"{script_name}_{timestamp}_{short_id}.log"
        log_file = date_dir / log_filename

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        return logger

    def set_variable(self, name: str, value: Any) -> None:
        """
        设置变量值（支持点号路径）

        Args:
            name: 变量名（如 "user.email" 或 "code"）
            value: 变量值
        """
        parts = name.split('.')

        if len(parts) == 1:
            self.variables[name] = value
        else:
            # 嵌套设置
            current = self.variables
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value

    def get_variable(self, name: str) -> Any:
        """
        获取变量值（支持点号路径）

        Args:
            name: 变量名（如 "user.email" 或 "code"）

        Returns:
            变量值

        Raises:
            ExecutionError: 变量不存在
        """
        parts = name.split('.')
        current = self.variables

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise ExecutionError(
                    line=0,
                    statement=f"get_variable({name!r})",
                    error_type=ExecutionError.VARIABLE_NOT_FOUND,
                    message=f"变量不存在: {name}"
                )

        return current

    def call_service(self, service_path: str, **kwargs) -> Any:
        """
        调用服务

        Args:
            service_path: 服务路径 "provider.method"
            **kwargs: 方法参数

        Returns:
            服务返回值

        Raises:
            ExecutionError: 服务调用失败
        """
        if not self.service_registry:
            raise ExecutionError(
                line=0,
                statement=f"call {service_path}",
                error_type=ExecutionError.SERVICE_ERROR,
                message="服务注册中心未初始化，请配置 services_config"
            )

        try:
            return self.service_registry.call(service_path, **kwargs)
        except Exception as e:
            raise ExecutionError(
                line=0,
                statement=f"call {service_path}",
                error_type=ExecutionError.SERVICE_ERROR,
                message=str(e)
            )

    def resolve_variables(self, text: str) -> str:
        """
        解析文本中的变量引用

        支持点号访问嵌套属性: {user.email} → user['email']

        Args:
            text: 可能包含变量引用的文本

        Returns:
            解析后的文本

        Raises:
            ExecutionError: 如果变量未定义

        Examples:
            >>> ctx = ExecutionContext("test", {"user": {"email": "test@example.com"}})
            >>> ctx.resolve_variables("{user.email}")
            'test@example.com'
            >>> ctx.resolve_variables("Hello {user.email}!")
            'Hello test@example.com!'
        """
        # 查找所有变量引用 {xxx.yyy.zzz}
        pattern = r'\{([^}]+)\}'

        def replace_var(match):
            var_path = match.group(1)  # "user.email"
            parts = var_path.split('.')  # ["user", "email"]

            # 逐层访问
            value = self.variables
            for part in parts:
                if not isinstance(value, dict):
                    raise ExecutionError(
                        line=0,
                        statement=f"resolve_variables({text!r})",
                        error_type=ExecutionError.VARIABLE_NOT_FOUND,
                        message=f"变量 '{var_path}' 不是字典类型，无法访问属性 '{part}'"
                    )

                if part not in value:
                    raise ExecutionError(
                        line=0,
                        statement=f"resolve_variables({text!r})",
                        error_type=ExecutionError.VARIABLE_NOT_FOUND,
                        message=f"变量未定义: {var_path}"
                    )

                value = value[part]

            return str(value)

        try:
            return re.sub(pattern, replace_var, text)
        except ExecutionError:
            raise
        except Exception as e:
            raise ExecutionError(
                line=0,
                statement=f"resolve_variables({text!r})",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"变量解析失败: {e}"
            )

    def add_execution_record(
        self,
        record_type: str,
        content: str,
        duration: Optional[float] = None,
        success: Optional[bool] = None
    ):
        """
        添加执行记录

        Args:
            record_type: 记录类型（statement, step_start, step_end, error）
            content: 记录内容
            duration: 执行耗时（秒）
            success: 是否成功
        """
        import time

        record = ExecutionRecord(
            timestamp=time.time(),
            type=record_type,
            content=content,
            duration=duration,
            success=success
        )
        self.execution_history.append(record)

    def get_page(self) -> Page:
        """
        获取当前页面对象（动态获取，避免失效）

        Returns:
            Playwright Page 对象

        Raises:
            ExecutionError: 如果页面未初始化
        """
        if self.playwright_wrapper is None:
            raise ExecutionError(
                line=0,
                statement="get_page()",
                error_type=ExecutionError.INVALID_STATE,
                message="浏览器未初始化，请先连接浏览器"
            )

        # 动态获取页面对象（避免失效）
        self.page = self.playwright_wrapper.get_page()

        if self.page is None:
            raise ExecutionError(
                line=0,
                statement="get_page()",
                error_type=ExecutionError.INVALID_STATE,
                message="无法获取页面对象"
            )

        return self.page

    def set_playwright_wrapper(self, wrapper: Any):
        """
        设置 Playwright 包装器

        Args:
            wrapper: Playwright 包装器实例 (ADSPowerWrapper 或 PlaywrightWrapper)
        """
        self.playwright_wrapper = wrapper

    def set_page(self, page: Page):
        """
        设置当前页面对象

        Args:
            page: Playwright Page 对象
        """
        self.page = page

    def init_diagnosis_listeners(self):
        """
        初始化诊断监听器

        应该在获取 page 之后调用
        """
        if self.page is None:
            return

        self.diagnosis_listeners = DiagnosisListeners(
            page=self.page,
            config=self.diagnosis_config
        )

    def cleanup_diagnosis_listeners(self):
        """清理诊断监听器"""
        if self.diagnosis_listeners:
            self.diagnosis_listeners.detach()
            self.diagnosis_listeners = None

    def set_diagnosis_config(self, config: DiagnosisConfig):
        """
        设置诊断配置

        Args:
            config: 诊断配置
        """
        self.diagnosis_config = config
        self.diagnosis_manager = DiagnosisManager(
            config=config,
            base_dir=str(Settings.SCREENSHOTS_DIR)
        )

    def clear_current_element(self):
        """清空当前选中的元素"""
        self.current_element = None

    def set_current_element(self, element: Locator):
        """
        设置当前选中的元素

        Args:
            element: Playwright Locator 对象
        """
        self.current_element = element

    def get_current_element(self) -> Locator:
        """
        获取当前选中的元素

        Returns:
            Playwright Locator 对象

        Raises:
            ExecutionError: 如果没有选中元素
        """
        if self.current_element is None:
            raise ExecutionError(
                line=0,
                statement="get_current_element()",
                error_type=ExecutionError.INVALID_STATE,
                message="没有选中元素，请先使用 select 语句选择元素"
            )

        return self.current_element

    def get_summary(self) -> Dict[str, Any]:
        """
        获取执行摘要

        Returns:
            包含执行统计信息的字典
        """
        total_records = len(self.execution_history)
        successful_records = sum(
            1 for r in self.execution_history
            if r.success is True
        )
        failed_records = sum(
            1 for r in self.execution_history
            if r.success is False
        )

        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "total_records": total_records,
            "successful_records": successful_records,
            "failed_records": failed_records,
            "screenshots_count": len(self.screenshots),
            "current_step": self.current_step,
        }

    def __repr__(self) -> str:
        """返回上下文的字符串表示"""
        return (
            f"ExecutionContext(task_id={self.task_id!r}, "
            f"status={self.status.value}, "
            f"variables={list(self.variables.keys())}, "
            f"has_page={self.page is not None}, "
            f"current_element={self.current_element is not None})"
        )
