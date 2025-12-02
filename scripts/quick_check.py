#!/usr/bin/env python
"""
快速检查脚本（仅检查代码格式）

使用方法：
    python scripts/quick_check.py

说明：
    只运行 black 和 flake8，用于日常快速检查
"""

import subprocess
import sys
from pathlib import Path
from typing import List

ROOT_DIR = Path(__file__).parent.parent


def run_check(name: str, cmd: List[str]) -> bool:
    """运行检查命令"""
    print(f"\n{'='*50}")
    print(f">> {name}")
    print(f"{'='*50}")

    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode != 0:
            print(f"[FAIL] {name}")
            return False

        print(f"[PASS] {name}")
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def main():
    """运行快速检查"""
    print(">> Quick Check (Formatting + Code Style)")

    checks = [
        ("Black formatting", ["black", "--check", "src/", "tests/"]),
        ("Flake8 linting", ["flake8", "src/", "tests/", "--max-line-length=100"]),
    ]

    failed = []
    for name, cmd in checks:
        if not run_check(name, cmd):
            failed.append(name)

    print(f"\n{'='*50}")
    if failed:
        print(f"[FAIL] Failed: {', '.join(failed)}")
        print("\nFix:")
        print("   black src/ tests/  # Auto-format")
        sys.exit(1)
    else:
        print("[PASS] All checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
