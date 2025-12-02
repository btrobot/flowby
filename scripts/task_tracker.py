#!/usr/bin/env python
"""
任务跟踪系统

用于跟踪测试重建进度和质量
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

TASK_FILE = Path(__file__).parent.parent / "docs" / "task_progress.json"


class TaskTracker:
    """任务跟踪器"""

    def __init__(self):
        self.tasks = self.load_tasks()

    def load_tasks(self) -> Dict:
        """加载任务进度"""
        if TASK_FILE.exists():
            with open(TASK_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.create_initial_tasks()

    def create_initial_tasks(self) -> Dict:
        """创建初始任务列表"""
        return {
            "metadata": {
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "total_tasks": 18,
                "completed_tasks": 0,
                "target_coverage": 80.0,
                "current_coverage": 54.0
            },
            "phases": {
                "phase_1": {
                    "name": "准备工作",
                    "tasks": {
                        "1.1": {
                            "title": "创建单元测试模板",
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        },
                        "1.2": {
                            "title": "创建集成测试模板",
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        },
                        "1.3": {
                            "title": "创建验证脚本",
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        }
                    }
                },
                "phase_2": {
                    "name": "补充集成测试",
                    "tasks": {
                        "2.1": {
                            "title": "Runner 集成测试",
                            "target_coverage": 70,
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        },
                        "2.2": {
                            "title": "Response Handler 集成测试",
                            "target_coverage": 70,
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        },
                        "2.3": {
                            "title": "Resource Integration 测试",
                            "target_coverage": 70,
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        },
                        "2.4": {
                            "title": "Resilience 集成测试",
                            "target_coverage": 70,
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        }
                    }
                },
                "phase_3": {
                    "name": "补充单元测试",
                    "tasks": {
                        "3.1": {
                            "title": "Interpreter 单元测试增强",
                            "target_coverage": 75,
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        },
                        "3.2": {
                            "title": "Expression Evaluator 单元测试增强",
                            "target_coverage": 75,
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        }
                    }
                },
                "phase_4": {
                    "name": "端到端测试",
                    "tasks": {
                        "4.1": {
                            "title": "Web 自动化 E2E 测试",
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        },
                        "4.2": {
                            "title": "API 测试 E2E",
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        }
                    }
                },
                "phase_5": {
                    "name": "重构现有测试",
                    "tasks": {
                        "5.1": {
                            "title": "拆分 test_v3_02_control_flow.py",
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        },
                        "5.2": {
                            "title": "拆分 test_expression_evaluator.py",
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        }
                    }
                },
                "phase_6": {
                    "name": "测试文档和工具",
                    "tasks": {
                        "6.1": {
                            "title": "编写测试文档",
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        },
                        "6.2": {
                            "title": "创建测试生成脚本",
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        },
                        "6.3": {
                            "title": "创建覆盖率监控脚本",
                            "status": "pending",
                            "coverage_delta": 0,
                            "tests_added": 0,
                            "completed_at": None
                        }
                    }
                }
            }
        }

    def save_tasks(self):
        """保存任务进度"""
        self.tasks["metadata"]["updated"] = datetime.now().isoformat()
        with open(TASK_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)

    def complete_task(self, task_id: str, coverage_delta: float, tests_added: int):
        """标记任务完成"""
        phase_id, task_num = task_id.split('.')
        phase_key = f"phase_{phase_id}"

        if phase_key in self.tasks["phases"]:
            task_key = f"{phase_id}.{task_num}"
            if task_key in self.tasks["phases"][phase_key]["tasks"]:
                task = self.tasks["phases"][phase_key]["tasks"][task_key]
                task["status"] = "completed"
                task["coverage_delta"] = coverage_delta
                task["tests_added"] = tests_added
                task["completed_at"] = datetime.now().isoformat()

                # 更新元数据
                self.tasks["metadata"]["completed_tasks"] += 1
                self.tasks["metadata"]["current_coverage"] += coverage_delta

                self.save_tasks()
                return True
        return False

    def get_status(self) -> str:
        """获取当前状态"""
        meta = self.tasks["metadata"]
        completed = meta["completed_tasks"]
        total = meta["total_tasks"]
        current_coverage = meta["current_coverage"]
        target_coverage = meta["target_coverage"]

        status = f"""
{'='*60}
测试重建进度
{'='*60}
任务进度: {completed}/{total} ({completed/total*100:.1f}%)
覆盖率:   {current_coverage:.1f}% / {target_coverage:.1f}%
{'='*60}

阶段进度:
"""
        for phase_key, phase_data in self.tasks["phases"].items():
            phase_name = phase_data["name"]
            tasks = phase_data["tasks"]
            completed_tasks = sum(1 for t in tasks.values() if t["status"] == "completed")
            total_tasks = len(tasks)

            status += f"\n{phase_name}: {completed_tasks}/{total_tasks}"

            for task_id, task in tasks.items():
                status_icon = "✅" if task["status"] == "completed" else "⏳"
                status += f"\n  {status_icon} {task_id}: {task['title']}"
                if task["status"] == "completed":
                    status += f" (+{task['coverage_delta']:.1f}%, {task['tests_added']} tests)"

        return status


def main():
    """主函数"""
    import sys

    tracker = TaskTracker()

    if len(sys.argv) < 2:
        print(tracker.get_status())
        return

    command = sys.argv[1]

    if command == "complete":
        if len(sys.argv) < 5:
            print("Usage: python task_tracker.py complete <task_id> <coverage_delta> <tests_added>")
            print("Example: python task_tracker.py complete 2.1 59.0 52")
            sys.exit(1)

        task_id = sys.argv[2]
        coverage_delta = float(sys.argv[3])
        tests_added = int(sys.argv[4])

        if tracker.complete_task(task_id, coverage_delta, tests_added):
            print(f"✅ Task {task_id} marked as completed")
            print(tracker.get_status())
        else:
            print(f"❌ Task {task_id} not found")
            sys.exit(1)

    elif command == "status":
        print(tracker.get_status())

    else:
        print(f"Unknown command: {command}")
        print("Available commands: status, complete")
        sys.exit(1)


if __name__ == "__main__":
    main()
