#!/usr/bin/env python
"""
提交前检查脚本（跨平台兼容）

使用方法：
    python scripts/pre_commit.py

或者在 git commit 前手动运行：
    python scripts/pre_commit.py && git commit -m "message"
"""

import subprocess
import sys
from pathlib import Path
from typing import List

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent


def run_command(name: str, cmd: List[str], description: str) -> bool:
    """运行命令并返回是否成功"""
    print(f"\n{'='*60}")
    print(f">> {name}: {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # 显示输出
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
        print(f"[ERROR] Running {name}: {e}")
        return False


def main():
    """运行所有检查"""
    print("\n" + "="*60)
    print(">> Pre-commit Checks")
    print("="*60)

    # 注意：根据用户反馈，设备性能有限，完整测试很慢
    # 可以通过环境变量 SKIP_TESTS=1 跳过测试
    skip_tests = sys.argv[1:] and sys.argv[1] == "--skip-tests"

    checks = [
        (
            "Black formatting",
            ["black", "--check", "src/", "tests/"],
            "Check code formatting"
        ),
        (
            "Flake8 linting",
            ["flake8", "src/", "tests/", "--max-line-length=100", "--extend-ignore=E203,W503"],
            "Check code style"
        ),
    ]

    # 可选：类型检查（可能较慢）
    if not skip_tests:
        checks.append((
            "MyPy type check",
            ["mypy", "src/", "--ignore-missing-imports"],
            "Check type annotations"
        ))

    # 可选：快速单元测试（可跳过以节省时间）
    if not skip_tests:
        checks.append((
            "Unit tests (quick)",
            ["pytest", "tests/unit/", "-x", "--tb=short", "-q", "--maxfail=3"],
            "Run unit tests (max 3 failures)"
        ))

    failed = []

    for name, cmd, desc in checks:
        if not run_command(name, cmd, desc):
            failed.append(name)

    print("\n" + "="*60)
    if failed:
        print(f"[FAIL] Failed checks: {', '.join(failed)}")
        print("="*60)
        print("\nTips:")
        print("  - Black formatting: Run 'black src/ tests/' to auto-fix")
        print("  - Flake8 errors: Fix manually or check detailed output")
        print("  - MyPy errors: Check type annotations")
        print("  - Tests failed: Fix code or tests")
        print("\nSkip tests for faster checks:")
        print("  python scripts/pre_commit.py --skip-tests")
        sys.exit(1)
    else:
        print("[PASS] All checks passed! Safe to commit.")
        print("="*60)
        sys.exit(0)


if __name__ == "__main__":
    main()
