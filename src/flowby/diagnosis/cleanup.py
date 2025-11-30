"""
诊断清理模块

自动清理旧的诊断包
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

from .config import DiagnosisConfig, DEFAULT_DIAGNOSIS_CONFIG


class DiagnosisCleanup:
    """诊断清理器"""

    def __init__(self, base_dir: str = None, config: DiagnosisConfig = None):
        """
        初始化清理器

        Args:
            base_dir: 诊断输出基础目录
            config: 诊断配置
        """
        self.base_dir = Path(base_dir) if base_dir else Path("screenshots")
        self.config = config or DEFAULT_DIAGNOSIS_CONFIG

    def cleanup(self) -> dict:
        """
        执行清理

        Returns:
            清理统计信息
        """
        if not self.config.cleanup.enabled:
            return {"skipped": True, "reason": "清理已禁用"}

        stats = {
            "deleted_by_age": 0,
            "deleted_by_count": 0,
            "deleted_by_size": 0,
            "freed_bytes": 0,
        }

        # 获取所有诊断目录
        diagnosis_dirs = self._get_all_diagnosis_dirs()

        if not diagnosis_dirs:
            return stats

        # 按时间清理
        age_deleted, age_freed = self._cleanup_by_age(diagnosis_dirs)
        stats["deleted_by_age"] = age_deleted
        stats["freed_bytes"] += age_freed

        # 重新获取目录列表
        diagnosis_dirs = self._get_all_diagnosis_dirs()

        # 按数量清理
        count_deleted, count_freed = self._cleanup_by_count(diagnosis_dirs)
        stats["deleted_by_count"] = count_deleted
        stats["freed_bytes"] += count_freed

        # 重新获取目录列表
        diagnosis_dirs = self._get_all_diagnosis_dirs()

        # 按大小清理
        size_deleted, size_freed = self._cleanup_by_size(diagnosis_dirs)
        stats["deleted_by_size"] = size_deleted
        stats["freed_bytes"] += size_freed

        return stats

    def _get_all_diagnosis_dirs(self) -> List[Path]:
        """获取所有诊断目录"""
        dirs = []

        if not self.base_dir.exists():
            return dirs

        for task_dir in self.base_dir.iterdir():
            if not task_dir.is_dir():
                continue

            diag_dir = task_dir / self.config.diagnosis_dir_name
            if diag_dir.exists():
                for d in diag_dir.iterdir():
                    if d.is_dir():
                        dirs.append(d)

        # 按修改时间排序（最新的在前）
        dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return dirs

    def _cleanup_by_age(self, dirs: List[Path]) -> Tuple[int, int]:
        """按时间清理"""
        max_age = timedelta(days=self.config.cleanup.max_age_days)
        cutoff = datetime.now() - max_age

        deleted = 0
        freed = 0

        for d in dirs:
            try:
                mtime = datetime.fromtimestamp(d.stat().st_mtime)
                if mtime < cutoff:
                    size = self._get_dir_size(d)
                    shutil.rmtree(d)
                    deleted += 1
                    freed += size
            except Exception:
                pass

        return deleted, freed

    def _cleanup_by_count(self, dirs: List[Path]) -> Tuple[int, int]:
        """按数量清理"""
        max_count = self.config.cleanup.max_count

        if len(dirs) <= max_count:
            return 0, 0

        # 删除最旧的
        to_delete = dirs[max_count:]
        deleted = 0
        freed = 0

        for d in to_delete:
            try:
                size = self._get_dir_size(d)
                shutil.rmtree(d)
                deleted += 1
                freed += size
            except Exception:
                pass

        return deleted, freed

    def _cleanup_by_size(self, dirs: List[Path]) -> Tuple[int, int]:
        """按总大小清理"""
        max_size = self.config.cleanup.max_size_mb * 1024 * 1024  # 转换为字节

        # 计算当前总大小
        total_size = sum(self._get_dir_size(d) for d in dirs)

        if total_size <= max_size:
            return 0, 0

        # 从最旧的开始删除，直到总大小符合要求
        deleted = 0
        freed = 0

        for d in reversed(dirs):
            if total_size <= max_size:
                break

            try:
                size = self._get_dir_size(d)
                shutil.rmtree(d)
                deleted += 1
                freed += size
                total_size -= size
            except Exception:
                pass

        return deleted, freed

    def _get_dir_size(self, path: Path) -> int:
        """获取目录大小"""
        total = 0
        try:
            for entry in path.rglob("*"):
                if entry.is_file():
                    total += entry.stat().st_size
        except Exception:
            pass
        return total

    def get_stats(self) -> dict:
        """
        获取当前诊断包统计信息

        Returns:
            统计信息
        """
        dirs = self._get_all_diagnosis_dirs()

        total_size = sum(self._get_dir_size(d) for d in dirs)
        oldest = None
        newest = None

        if dirs:
            newest = datetime.fromtimestamp(dirs[0].stat().st_mtime)
            oldest = datetime.fromtimestamp(dirs[-1].stat().st_mtime)

        return {
            "count": len(dirs),
            "total_size_mb": total_size / 1024 / 1024,
            "oldest": oldest.isoformat() if oldest else None,
            "newest": newest.isoformat() if newest else None,
        }
