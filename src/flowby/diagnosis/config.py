"""
诊断配置定义

定义诊断级别和默认配置
"""

from enum import IntEnum
from dataclasses import dataclass, field
from typing import Dict, List


class DiagnosisLevel(IntEnum):
    """诊断级别枚举"""

    NONE = 0  # 不输出诊断信息
    MINIMAL = 1  # 最小: 截图 + URL
    BASIC = 2  # 基本: + HTML源码 + 元素信息
    STANDARD = 3  # 标准: + 控制台日志 + 执行上下文 (默认)
    DETAILED = 4  # 详细: + 网络请求
    FULL = 5  # 完整: + 性能指标 + 视口信息

    @classmethod
    def from_string(cls, name: str) -> "DiagnosisLevel":
        """从字符串解析诊断级别"""
        name_upper = name.upper()
        if hasattr(cls, name_upper):
            return cls[name_upper]
        raise ValueError(f"未知的诊断级别: {name}")


@dataclass
class CleanupConfig:
    """清理配置"""

    enabled: bool = True
    max_age_days: int = 7  # 保留天数
    max_count: int = 100  # 最大诊断包数量
    max_size_mb: int = 500  # 最大总大小 (MB)


@dataclass
class NetworkFilterConfig:
    """网络日志过滤配置"""

    include_assets: bool = False  # 是否包含静态资源 (js, css, images)
    only_failed: bool = False  # 只记录失败请求
    exclude_patterns: List[str] = field(
        default_factory=lambda: [
            r".*\.(png|jpg|jpeg|gif|svg|ico)$",
            r".*\.(css|woff|woff2|ttf|eot)$",
        ]
    )


@dataclass
class ConsoleFilterConfig:
    """控制台日志过滤配置"""

    levels: List[str] = field(default_factory=lambda: ["error", "warning", "log"])
    max_entries: int = 100


@dataclass
class DiagnosisConfig:
    """诊断配置"""

    # 默认诊断级别
    default_level: DiagnosisLevel = DiagnosisLevel.STANDARD

    # 自动清理配置
    cleanup: CleanupConfig = field(default_factory=CleanupConfig)

    # 各错误类型的默认级别
    error_levels: Dict[str, DiagnosisLevel] = field(
        default_factory=lambda: {
            "ASSERTION_FAILED": DiagnosisLevel.STANDARD,
            "ELEMENT_NOT_FOUND": DiagnosisLevel.BASIC,
            "TIMEOUT": DiagnosisLevel.DETAILED,
            "NAVIGATION_FAILED": DiagnosisLevel.DETAILED,
        }
    )

    # 网络日志过滤
    network_filter: NetworkFilterConfig = field(default_factory=NetworkFilterConfig)

    # 控制台日志过滤
    console_filter: ConsoleFilterConfig = field(default_factory=ConsoleFilterConfig)

    # 诊断输出目录名
    diagnosis_dir_name: str = "error_diagnosis"

    def get_level_for_error(self, error_type: str) -> DiagnosisLevel:
        """获取特定错误类型的诊断级别"""
        return self.error_levels.get(error_type, self.default_level)


# 默认配置实例
DEFAULT_DIAGNOSIS_CONFIG = DiagnosisConfig()


# 诊断级别对应的收集器映射
LEVEL_COLLECTORS = {
    DiagnosisLevel.MINIMAL: [
        "screenshot",
        "page_info",
    ],
    DiagnosisLevel.BASIC: [
        "screenshot",
        "page_info",
        "html_source",
        "element_info",
    ],
    DiagnosisLevel.STANDARD: [
        "screenshot",
        "page_info",
        "html_source",
        "element_info",
        "console_logs",
        "context_snapshot",
    ],
    DiagnosisLevel.DETAILED: [
        "screenshot",
        "page_info",
        "html_source",
        "element_info",
        "console_logs",
        "context_snapshot",
        "network_logs",
    ],
    DiagnosisLevel.FULL: [
        "screenshot",
        "page_info",
        "html_source",
        "element_info",
        "console_logs",
        "context_snapshot",
        "network_logs",
        "performance_metrics",
        "viewport_info",
    ],
}


def get_collectors_for_level(level: DiagnosisLevel) -> List[str]:
    """获取指定级别需要的收集器列表"""
    if level == DiagnosisLevel.NONE:
        return []
    return LEVEL_COLLECTORS.get(level, LEVEL_COLLECTORS[DiagnosisLevel.STANDARD])
