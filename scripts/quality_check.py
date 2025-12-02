#!/usr/bin/env python
"""
测试质量检查脚本

用于检查 AI 生成的测试代码质量

使用方法：
    python scripts/quality_check.py <test_file_path>
"""

import subprocess
import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict

ROOT_DIR = Path(__file__).parent.parent


class QualityChecker:
    """测试质量检查器"""

    def __init__(self, test_file: Path):
        self.test_file = test_file
        self.issues = []
        self.warnings = []
        self.score = 100.0

    def run_all_checks(self) -> Tuple[bool, float, List[str]]:
        """运行所有检查"""
        print(f"\n{'='*60}")
        print(f"质量检查: {self.test_file.relative_to(ROOT_DIR)}")
        print(f"{'='*60}\n")

        # 检查项
        checks = [
            ("文件存在性", self.check_file_exists),
            ("代码格式 (Black)", self.check_black_formatting),
            ("代码风格 (Flake8)", self.check_flake8),
            ("测试可执行性", self.check_tests_executable),
            ("测试命名规范", self.check_test_naming),
            ("文档完整性", self.check_documentation),
            ("Fixture 使用", self.check_fixtures),
            ("断言质量", self.check_assertions),
            ("覆盖率贡献", self.check_coverage_contribution),
            ("无重复代码", self.check_duplication),
        ]

        for name, check_func in checks:
            self._run_check(name, check_func)

        # 计算最终分数
        final_score = max(0, self.score)

        # 输出结果
        self._print_results(final_score)

        # 通过标准：分数 >= 80
        passed = final_score >= 80.0 and len(self.issues) == 0

        return passed, final_score, self.issues

    def _run_check(self, name: str, check_func):
        """运行单个检查"""
        print(f"[检查] {name}...", end=" ")
        try:
            check_func()
            print("✅ 通过")
        except Exception as e:
            print(f"❌ 失败: {e}")
            self.issues.append(f"{name}: {e}")

    def check_file_exists(self):
        """检查文件存在"""
        if not self.test_file.exists():
            raise ValueError("文件不存在")

    def check_black_formatting(self):
        """检查 Black 格式化"""
        result = subprocess.run(
            ["black", "--check", str(self.test_file)],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            self.score -= 10
            raise ValueError("代码格式不符合 Black 标准，运行 'black <file>' 修复")

    def check_flake8(self):
        """检查 Flake8"""
        result = subprocess.run(
            ["flake8", str(self.test_file), "--max-line-length=100"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            self.score -= 10
            errors = result.stdout.strip()
            raise ValueError(f"Flake8 检查失败:\n{errors}")

    def check_tests_executable(self):
        """检查测试可执行"""
        result = subprocess.run(
            ["pytest", str(self.test_file), "-v"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode != 0:
            self.score -= 30
            raise ValueError(f"测试执行失败:\n{result.stdout[-500:]}")

        # 统计测试数量
        match = re.search(r'(\d+) passed', result.stdout)
        if match:
            test_count = int(match.group(1))
            if test_count == 0:
                self.score -= 20
                raise ValueError("没有测试用例")
            print(f"({test_count} 个测试)", end=" ")

    def check_test_naming(self):
        """检查测试命名规范"""
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查测试函数命名
        test_functions = re.findall(r'def (test_\w+)', content)
        if not test_functions:
            self.score -= 20
            raise ValueError("没有找到测试函数（应以 test_ 开头）")

        # 检查命名规范
        bad_names = []
        for func_name in test_functions:
            # 应该是 test_<function>_<scenario>_<expected> 格式
            if len(func_name.split('_')) < 3:
                bad_names.append(func_name)

        if bad_names:
            self.score -= 5
            self.warnings.append(f"命名不够描述性: {', '.join(bad_names[:3])}")

    def check_documentation(self):
        """检查文档完整性"""
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查文件级文档字符串
        if not content.strip().startswith('"""'):
            self.score -= 5
            self.warnings.append("缺少文件级文档字符串")

        # 检查类文档字符串
        class_pattern = r'class Test\w+:\s*\n\s*"""'
        if not re.search(class_pattern, content):
            self.score -= 5
            self.warnings.append("测试类缺少文档字符串")

    def check_fixtures(self):
        """检查 Fixture 使用"""
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否使用 fixture
        has_fixtures = '@pytest.fixture' in content

        # 检查是否有重复的 setup 代码
        test_functions = re.findall(r'def test_\w+\([^)]*\):\s*\n(.*?)(?=\n    def |\Z)', content, re.DOTALL)

        if len(test_functions) > 3:
            # 检查重复的初始化代码
            setup_lines = []
            for func_body in test_functions[:5]:
                first_lines = func_body.split('\n')[:3]
                setup_lines.append('\n'.join(first_lines))

            # 简单的重复检测
            if len(set(setup_lines)) < len(setup_lines) * 0.7:
                if not has_fixtures:
                    self.score -= 10
                    self.warnings.append("存在重复的 setup 代码，建议使用 fixture")

    def check_assertions(self):
        """检查断言质量"""
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 统计断言
        assertions = re.findall(r'\n\s+(assert\s+)', content)
        test_functions = re.findall(r'def test_\w+', content)

        if test_functions:
            avg_assertions = len(assertions) / len(test_functions)

            if avg_assertions < 1:
                self.score -= 15
                raise ValueError(f"平均每个测试只有 {avg_assertions:.1f} 个断言，太少了")
            elif avg_assertions < 2:
                self.score -= 5
                self.warnings.append(f"平均每个测试只有 {avg_assertions:.1f} 个断言，建议增加")

        # 检查断言消息
        assertions_with_msg = re.findall(r'assert\s+.*,\s*["\']', content)
        if len(assertions_with_msg) / max(len(assertions), 1) < 0.3:
            self.score -= 5
            self.warnings.append("建议为重要断言添加错误消息")

    def check_coverage_contribution(self):
        """检查覆盖率贡献"""
        # 运行覆盖率检查
        result = subprocess.run(
            ["pytest", str(self.test_file), "--cov=src/flowby", "--cov-report=json", "-q"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            self.warnings.append("无法计算覆盖率贡献")
            return

        # 读取覆盖率
        coverage_file = ROOT_DIR / "coverage.json"
        if coverage_file.exists():
            import json
            with open(coverage_file) as f:
                data = json.load(f)

            # 检查覆盖率
            total_coverage = data['totals']['percent_covered']
            if total_coverage < 54:
                self.warnings.append(f"覆盖率下降到 {total_coverage:.1f}%")

    def check_duplication(self):
        """检查重复代码"""
        with open(self.test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 简单的重复检测：检查相似的代码块
        code_blocks = []
        for i in range(0, len(lines) - 5, 5):
            block = ''.join(lines[i:i+5]).strip()
            if block and not block.startswith('#'):
                code_blocks.append(block)

        unique_blocks = set(code_blocks)
        duplication_ratio = 1 - (len(unique_blocks) / max(len(code_blocks), 1))

        if duplication_ratio > 0.5:
            self.score -= 10
            self.warnings.append(f"代码重复率 {duplication_ratio*100:.1f}%，建议重构")
        elif duplication_ratio > 0.3:
            self.score -= 5
            self.warnings.append(f"代码重复率 {duplication_ratio*100:.1f}%")

    def _print_results(self, final_score: float):
        """打印检查结果"""
        print(f"\n{'='*60}")
        print("检查结果")
        print(f"{'='*60}")

        # 分数
        if final_score >= 90:
            grade = "优秀"
            emoji = "🌟"
        elif final_score >= 80:
            grade = "良好"
            emoji = "✅"
        elif final_score >= 60:
            grade = "及格"
            emoji = "⚠️"
        else:
            grade = "不合格"
            emoji = "❌"

        print(f"\n{emoji} 质量分数: {final_score:.1f}/100 ({grade})")

        # 问题
        if self.issues:
            print(f"\n❌ 严重问题 ({len(self.issues)}):")
            for issue in self.issues:
                print(f"  - {issue}")

        # 警告
        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")

        # 建议
        print(f"\n{'='*60}")
        if final_score >= 80:
            print("✅ 测试质量合格，可以提交")
        else:
            print("❌ 测试质量不合格，需要改进")
            print("\n改进建议:")
            if final_score < 60:
                print("  1. 修复所有严重问题")
                print("  2. 确保所有测试通过")
                print("  3. 运行 black 和 flake8 修复代码风格")
            print("  4. 增加断言数量和质量")
            print("  5. 减少重复代码，使用 fixture")
            print("  6. 改进测试命名和文档")

        print(f"{'='*60}\n")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python scripts/quality_check.py <test_file>")
        print("Example: python scripts/quality_check.py tests/integration/test_runner.py")
        sys.exit(1)

    test_file = Path(sys.argv[1])
    if not test_file.is_absolute():
        test_file = ROOT_DIR / test_file

    checker = QualityChecker(test_file)
    passed, score, issues = checker.run_all_checks()

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
