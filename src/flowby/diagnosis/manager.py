"""
诊断管理器

负责协调信息收集和诊断包生成
"""

import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page
    from ..context import ExecutionContext

from .config import (
    DiagnosisLevel,
    DiagnosisConfig,
    DEFAULT_DIAGNOSIS_CONFIG,
    get_collectors_for_level,
)
from .collectors import get_collector
from .listeners import DiagnosisListeners
from .report import DiagnosisReportGenerator


class DiagnosisManager:
    """诊断管理器"""

    def __init__(self, config: DiagnosisConfig = None, base_dir: str = None):
        """
        初始化诊断管理器

        Args:
            config: 诊断配置
            base_dir: 诊断输出基础目录
        """
        self.config = config or DEFAULT_DIAGNOSIS_CONFIG
        self.base_dir = Path(base_dir) if base_dir else Path("screenshots")
        self.report_generator = DiagnosisReportGenerator()

    def capture_diagnosis(
        self,
        page: "Page",
        context: "ExecutionContext",
        error: Exception,
        error_type: str,
        level: DiagnosisLevel = None,
        statement: str = "",
        line: int = 0,
        selector: str = "",
        listeners: DiagnosisListeners = None,
    ) -> str:
        """
        捕获诊断信息

        Args:
            page: Playwright 页面对象
            context: 执行上下文
            error: 异常对象
            error_type: 错误类型
            level: 诊断级别 (None 则使用配置默认值)
            statement: 失败的语句
            line: 行号
            selector: 相关选择器
            listeners: 诊断监听器

        Returns:
            诊断包目录路径
        """
        # 确定诊断级别
        if level is None:
            level = self.config.get_level_for_error(error_type)

        # 如果级别为 NONE，不收集任何信息
        if level == DiagnosisLevel.NONE:
            return ""

        # 创建诊断目录
        diagnosis_dir = self._create_diagnosis_dir(context.task_id, error_type)

        # 获取需要的收集器
        collector_names = get_collectors_for_level(level)

        # 收集信息
        collected_data = {
            "error_info": {
                "type": error_type,
                "message": str(error),
                "statement": statement,
                "line": line,
                "level": level.name,
                "timestamp": datetime.now().isoformat(),
            },
            "files": {},
        }

        for collector_name in collector_names:
            collector = get_collector(collector_name)
            if not collector:
                continue

            try:
                # 收集数据
                data = collector.collect(
                    page=page,
                    context=context,
                    selector=selector,
                    listeners=listeners,
                )

                # 保存数据
                if collector_name == "screenshot":
                    # 截图需要特殊处理
                    filename = collector.save(data, diagnosis_dir, page)
                else:
                    filename = collector.save(data, diagnosis_dir)

                collected_data["files"][collector_name] = filename
                collected_data[collector_name] = data

            except Exception as e:
                collected_data["files"][collector_name] = f"收集失败: {e}"

        # 生成诊断报告
        try:
            report_content = self.report_generator.generate(collected_data)
            report_path = diagnosis_dir / "diagnosis_report.md"
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            collected_data["files"]["report"] = "diagnosis_report.md"
        except Exception as e:
            collected_data["files"]["report"] = f"报告生成失败: {e}"

        # 保存收集元数据
        meta_path = diagnosis_dir / "diagnosis_meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            # 移除大型数据，只保存元信息
            meta = {
                "error_info": collected_data["error_info"],
                "files": collected_data["files"],
            }
            json.dump(meta, f, ensure_ascii=False, indent=2)

        return str(diagnosis_dir)

    def _create_diagnosis_dir(self, task_id: str, error_type: str) -> Path:
        """
        创建诊断输出目录

        Args:
            task_id: 任务ID
            error_type: 错误类型

        Returns:
            诊断目录路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        dir_name = f"{timestamp}_{error_type}"

        # 构建路径: base_dir/task_id/error_diagnosis/timestamp_errortype/
        diagnosis_dir = self.base_dir / task_id / self.config.diagnosis_dir_name / dir_name

        diagnosis_dir.mkdir(parents=True, exist_ok=True)

        return diagnosis_dir

    def get_diagnosis_dirs(self, task_id: str = None) -> list:
        """
        获取诊断目录列表

        Args:
            task_id: 任务ID，None 则获取所有

        Returns:
            诊断目录路径列表
        """
        dirs = []

        if task_id:
            base = self.base_dir / task_id / self.config.diagnosis_dir_name
            if base.exists():
                dirs.extend([d for d in base.iterdir() if d.is_dir()])
        else:
            # 遍历所有任务目录
            if self.base_dir.exists():
                for task_dir in self.base_dir.iterdir():
                    if task_dir.is_dir():
                        diag_dir = task_dir / self.config.diagnosis_dir_name
                        if diag_dir.exists():
                            dirs.extend([d for d in diag_dir.iterdir() if d.is_dir()])

        return sorted(dirs, key=lambda x: x.name, reverse=True)
