"""
DSL CLI 运行器

提供命令行接口来执行 DSL 脚本
"""

import sys
import argparse
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter
from .context import ExecutionContext
from .errors import DSLError, LexerError, ParserError, ExecutionError
from .config.loader import ConfigLoader
from .config.errors import ConfigError



class DSLRunner:
    """DSL 脚本运行器"""

    def __init__(
        self,
        task_id: str,
        variables: Optional[Dict[str, Any]] = None,
        headless: bool = False,
        browser_id: Optional[str] = None,
        browser_type: str = "adspower",
        services_config_path: Optional[str] = None
    ):
        """
        初始化运行器

        Args:
            task_id: 任务标识符
            variables: 初始变量
            headless: 是否无头模式
            browser_id: ADSPower 浏览器 ID (when browser_type=adspower)
            browser_type: 浏览器类型 (adspower, playwright, chromium, firefox, webkit)
            services_config_path: 服务配置文件路径（可选，默认在脚本目录查找 services.yaml）
        """
        self.task_id = task_id
        self.variables = variables or {}
        self.headless = headless
        self.browser_id = browser_id
        self.browser_type = browser_type
        self.services_config_path = services_config_path
        self.services_config = None

        # 组件
        self.lexer = Lexer()
        self.parser = Parser()
        self.interpreter = None
        self.context = None  # Will be initialized when running


    def run_file(self, file_path: str) -> bool:
        """
        执行 DSL 脚本文件

        Args:
            file_path: 脚本文件路径

        Returns:
            执行是否成功
        """
        path = Path(file_path)

        if not path.exists():
            print(f"错误: 文件不存在: {file_path}")
            return False

        if not path.suffix == ".flow":
            print(f"警告: 建议使用 .flow 扩展名")

        # 如果没有指定 services_config_path，尝试在脚本目录查找 services.yaml
        if not self.services_config_path:
            script_dir = path.parent
            services_yaml = script_dir / "services.yaml"
            if services_yaml.exists():
                self.services_config_path = str(services_yaml)
                print(f"[{self.task_id}] 找到服务配置: {services_yaml}")

        try:
            source = path.read_text(encoding="utf-8")
            return self.run_source(source, str(path))
        except Exception as e:
            print(f"错误: 读取文件失败: {e}")
            return False

    def run_source(self, source: str, source_name: str = "<source>") -> bool:
        """
        执行 DSL 源代码

        Args:
            source: DSL 源代码
            source_name: 源名称（用于错误报告）

        Returns:
            执行是否成功
        """
        start_time = time.time()

        try:
            # 加载服务配置（如果有）
            if self.services_config_path:
                try:
                    config_path = Path(self.services_config_path)
                    loader = ConfigLoader(config_dir=str(config_path.parent))
                    self.services_config = loader.load_services(path=config_path.name)
                    print(f"[{self.task_id}] 服务配置已加载: {self.services_config_path}")
                except ConfigError as e:
                    print(f"[{self.task_id}] 警告: 服务配置加载失败: {e}")
                    print(f"[{self.task_id}] 将继续执行，但服务调用将不可用")
                except Exception as e:
                    print(f"[{self.task_id}] 警告: 服务配置加载异常: {e}")
                    print(f"[{self.task_id}] 将继续执行，但服务调用将不可用")

            # 创建执行上下文
            self.context = ExecutionContext(
                task_id=self.task_id,
                variables=self.variables,
                services_config=self.services_config,
                script_path=source_name if source_name != "<source>" else None
            )

            # 词法分析
            print(f"[{self.task_id}] 词法分析中...")
            tokens = self.lexer.tokenize(source)

            # 语法分析
            print(f"[{self.task_id}] 语法分析中...")
            program = self.parser.parse(tokens)
            print(f"[{self.task_id}] 解析完成: {len(program.statements)} 条语句")

            # 初始化浏览器
            if self.browser_type in ("playwright", "chromium", "firefox", "webkit"):
                self._init_playwright_browser()
            elif self.browser_id:
                self._init_adspower_browser()
            else:
                print(f"[{self.task_id}] 警告: 未指定浏览器，将跳过浏览器操作")

            # 执行
            print(f"[{self.task_id}] 开始执行...")

            self.interpreter = Interpreter(self.context)
            self.interpreter.execute(program)

            # 成功
            elapsed = time.time() - start_time
            print(f"\n[{self.task_id}] 执行成功! 耗时: {elapsed:.2f}s")

            # 输出执行摘要
            self._print_summary()

            return True

        except LexerError as e:
            print(f"\n词法错误: {e}")
            return False

        except ParserError as e:
            print(f"\n语法错误: {e}")
            return False

        except ExecutionError as e:
            print(f"\n执行错误: {e}")
            if e.screenshot_path:
                print(f"截图已保存: {e.screenshot_path}")
            return False

        except Exception as e:
            print(f"\n未知错误: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            # 清理资源
            self._cleanup()

    def _init_playwright_browser(self):
        """初始化 Playwright 浏览器"""
        try:
            from .browser.playwright_wrapper import PlaywrightWrapper

            print(f"[{self.task_id}] 启动 Playwright 浏览器: {self.browser_type}")

            # 创建包装器
            wrapper = PlaywrightWrapper()

            # 确定浏览器类型
            browser_type = self.browser_type
            if browser_type == "playwright":
                browser_type = "chromium"  # 默认使用 chromium

            # 启动浏览器
            page = wrapper.launch(
                browser_type=browser_type,
                headless=self.headless
            )

            # 设置到上下文
            self.context.set_playwright_wrapper(wrapper)
            self.context.set_page(page)

            print(f"[{self.task_id}] Playwright 浏览器启动成功")

        except ImportError as e:
            print(f"[{self.task_id}] 错误: Playwright 不可用")
            print(f"请安装: pip install playwright")
            print(f"然后运行: playwright install")
            raise ExecutionError(
                line=0,
                statement="init browser",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"Playwright 不可用: {e}"
            )
        except Exception as e:
            raise ExecutionError(
                line=0,
                statement="init browser",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"Playwright 浏览器初始化失败: {e}"
            )

    def _init_adspower_browser(self):
        """初始化 ADSPower 浏览器"""
        try:
            from ..browser.adspower_wrapper import ADSPowerWrapper

            print(f"[{self.task_id}] 连接 ADSPower 浏览器: {self.browser_id}")

            # 创建包装器
            wrapper = ADSPowerWrapper()

            # 连接到浏览器 (browser_id 可以是 profile_id 或 profile_no)
            page = wrapper.connect_to_browser(
                profile_id=self.browser_id,
                headless=self.headless
            )

            # 设置到上下文
            self.context.set_playwright_wrapper(wrapper)
            self.context.set_page(page)

            print(f"[{self.task_id}] ADSPower 浏览器连接成功")

        except ImportError as e:
            print(f"[{self.task_id}] 错误: ADSPowerWrapper 不可用")
            print(f"请确保 adspower_client.py 在正确的位置")
            raise ExecutionError(
                line=0,
                statement="init browser",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"ADSPowerWrapper 不可用: {e}"
            )
        except Exception as e:
            raise ExecutionError(
                line=0,
                statement="init browser",
                error_type=ExecutionError.RUNTIME_ERROR,
                message=f"ADSPower 浏览器初始化失败: {e}"
            )

    def _cleanup(self):
        """清理资源"""
        try:
            wrapper = self.context.playwright_wrapper
            if wrapper:
                wrapper.close()
        except:
            pass

    def _print_summary(self):
        """打印执行摘要"""
        history = self.context.execution_history
        screenshots = self.context.screenshots

        print(f"\n--- 执行摘要 ---")
        print(f"总操作数: {len(history)}")
        print(f"截图数: {len(screenshots)}")

        # 统计操作类型
        type_counts = {}
        for record in history:
            t = record.type  # Fixed: was record.record_type
            type_counts[t] = type_counts.get(t, 0) + 1

        if type_counts:
            print("操作统计:")
            for t, count in sorted(type_counts.items()):
                print(f"  - {t}: {count}")


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="DSL 脚本运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "script",
        help="DSL 脚本文件路径 (.flow)"
    )

    parser.add_argument(
        "--task-id",
        default=None,
        help="任务标识符（默认自动生成）"
    )

    parser.add_argument(
        "--browser",
        default="playwright",
        help="浏览器类型或 ADSPower 浏览器 ID。支持: playwright, chromium, firefox, webkit, 或 ADSPower ID (默认: playwright)"
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="无头模式运行"
    )

    parser.add_argument(
        "--variables",
        default=None,
        help="变量 JSON 文件路径"
    )

    parser.add_argument(
        "--var",
        action="append",
        default=[],
        help="设置单个变量 (格式: key=value)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry-Run 模式：只检查脚本语法和语义，不执行操作"
    )

    args = parser.parse_args()

    # 生成任务 ID
    if args.task_id:
        task_id = args.task_id
    else:
        import uuid
        task_id = f"task_{uuid.uuid4().hex[:8]}"

    # 加载变量
    variables = {}

    # 从 JSON 文件加载
    if args.variables:
        try:
            with open(args.variables, 'r', encoding='utf-8') as f:
                variables = json.load(f)
        except Exception as e:
            print(f"警告: 加载变量文件失败: {e}")

    # 从命令行参数加载
    for var in args.var:
        if '=' in var:
            key, value = var.split('=', 1)
            # 支持嵌套键 (user.email)
            keys = key.split('.')
            current = variables
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value

    # 检测浏览器类型
    browser_type = "adspower"  # 默认
    browser_id = None

    if args.browser:
        # 如果是已知浏览器类型关键字
        if args.browser.lower() in ("playwright", "chromium", "firefox", "webkit"):
            browser_type = args.browser.lower()
        else:
            # 否则视为 ADSPower 浏览器 ID
            browser_type = "adspower"
            browser_id = args.browser

    # 创建运行器
    runner = DSLRunner(
        task_id=task_id,
        variables=variables,
        headless=args.headless,
        browser_id=browser_id,
        browser_type=browser_type,
        dry_run=args.dry_run
    )

    # 执行脚本
    success = runner.run_file(args.script)

    # 返回状态码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
