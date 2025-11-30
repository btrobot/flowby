"""
诊断模块

提供断言失败时的错误诊断信息收集和报告生成功能。

模块:
    - config: 诊断级别和配置定义
    - collectors: 各类信息收集器
    - listeners: 事件监听器
    - manager: 诊断管理器
    - report: 报告生成器
    - cleanup: 自动清理
"""

from .config import DiagnosisLevel, DiagnosisConfig, DEFAULT_DIAGNOSIS_CONFIG
from .manager import DiagnosisManager
from .cleanup import DiagnosisCleanup

__all__ = [
    'DiagnosisLevel',
    'DiagnosisConfig',
    'DEFAULT_DIAGNOSIS_CONFIG',
    'DiagnosisManager',
    'DiagnosisCleanup',
]
