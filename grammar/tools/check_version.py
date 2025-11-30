#!/usr/bin/env python3
"""
Grammar Version Checker

检查 DSL 脚本与语法版本的兼容性

功能:
    1. 解析脚本中的 meta 块，获取 grammar-version
    2. 检查脚本使用的特性是否在指定版本中可用
    3. 检测废弃特性的使用
    4. 生成迁移建议

用法:
    # 检查单个脚本
    python scripts/check_grammar_version.py script.flow

    # 检查目录下所有脚本
    python scripts/check_grammar_version.py examples/flows/

    # 指定目标语法版本
    python scripts/check_grammar_version.py script.flow --target-version 2.0.0

    # 生成迁移报告
    python scripts/check_grammar_version.py script.flow --migration-report

退出码:
    0: 完全兼容
    1: 有警告（使用了废弃特性）
    2: 不兼容（使用了移除的特性或未来的特性）
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum


class CompatibilityStatus(Enum):
    """兼容性状态"""
    COMPATIBLE = "[OK]"
    WARNING = "[WARN]"
    INCOMPATIBLE = "[ERROR]"


@dataclass
class FeatureVersion:
    """特性版本信息"""
    feature_id: str
    feature_name: str
    added_in: str  # 添加的版本
    deprecated_in: Optional[str] = None  # 废弃的版本
    removed_in: Optional[str] = None  # 移除的版本
    replaced_by: Optional[str] = None  # 被什么替代


@dataclass
class CompatibilityIssue:
    """兼容性问题"""
    line_number: int
    feature: str
    issue_type: str  # "deprecated", "removed", "not_available"
    message: str
    suggestion: Optional[str] = None


@dataclass
class VersionCheckReport:
    """版本检查报告"""
    script_path: str
    declared_version: Optional[str]
    target_version: str
    current_version: str

    status: CompatibilityStatus
    issues: List[CompatibilityIssue]

    features_used: Set[str]
    deprecated_features_used: Set[str]
    removed_features_used: Set[str]


# 特性版本数据库
FEATURE_VERSIONS: Dict[str, FeatureVersion] = {
    # 变量与赋值
    "let": FeatureVersion("1.1", "Let Declaration", "1.0.0"),
    "const": FeatureVersion("1.2", "Const Declaration", "1.0.0"),
    "assignment": FeatureVersion("1.3", "Assignment", "1.0.0"),

    # 控制流
    "step": FeatureVersion("2.1", "Step Block", "1.0.0"),
    "if": FeatureVersion("2.2", "If-Else", "1.0.0"),
    "when": FeatureVersion("2.3", "When-Otherwise", "1.0.0"),
    "for": FeatureVersion("2.4", "For-Each Loop", "1.0.0"),

    # 导航
    "navigate": FeatureVersion("3.1", "Navigate To", "1.0.0"),
    "go": FeatureVersion("3.2", "Go Back/Forward", "1.0.0"),
    "reload": FeatureVersion("3.3", "Reload", "1.0.0"),

    # 等待
    "wait_duration": FeatureVersion("4.1", "Wait Duration", "1.0.0"),
    "wait_element": FeatureVersion("4.2", "Wait Element", "1.0.0"),
    "wait_navigation": FeatureVersion("4.3", "Wait Navigation", "1.0.0"),

    # 选择
    "select": FeatureVersion("5.1", "Select Element", "1.0.0"),
    "select_option": FeatureVersion("5.2", "Select Option", "1.0.0"),

    # 动作
    "type": FeatureVersion("6.1", "Type", "1.0.0"),
    "click": FeatureVersion("6.2", "Click", "1.0.0"),
    "double_click": FeatureVersion("6.3", "Double Click", "1.0.0"),
    "right_click": FeatureVersion("6.4", "Right Click", "1.0.0"),
    "hover": FeatureVersion("6.5", "Hover", "1.0.0"),
    "clear": FeatureVersion("6.6", "Clear", "1.0.0"),
    "press": FeatureVersion("6.7", "Press", "1.0.0"),
    "scroll": FeatureVersion("6.8", "Scroll", "1.0.0"),
    "check": FeatureVersion("6.9", "Check/Uncheck", "1.0.0"),
    "upload": FeatureVersion("6.10", "Upload", "1.0.0"),

    # 断言
    "assert": FeatureVersion("7.1", "Assert", "1.0.0"),

    # 服务调用
    "call": FeatureVersion("8.1", "Call Service", "1.0.0"),

    # 数据提取
    "extract": FeatureVersion("9.1", "Extract", "1.0.0"),

    # 工具
    "log": FeatureVersion("10.1", "Log", "1.0.0"),
    "screenshot": FeatureVersion("10.2", "Screenshot", "1.0.0"),

    # v2.0.0 新增
    "system_variables": FeatureVersion("var.1", "System Variables", "2.0.0"),
    "builtin_functions": FeatureVersion("func.1", "Built-in Functions", "2.0.0"),
    "string_interpolation": FeatureVersion("type.1", "String Interpolation", "2.0.0"),
}


def parse_version(version_str: str) -> tuple:
    """解析版本号"""
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version_str)
    if match:
        return (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return (0, 0, 0)


def compare_versions(v1: str, v2: str) -> int:
    """
    比较版本号

    返回:
        -1: v1 < v2
         0: v1 == v2
         1: v1 > v2
    """
    t1 = parse_version(v1)
    t2 = parse_version(v2)

    if t1 < t2:
        return -1
    elif t1 > t2:
        return 1
    else:
        return 0


def extract_declared_version(script_path: Path) -> Optional[str]:
    """从脚本的 meta 块中提取声明的语法版本"""
    if not script_path.exists():
        return None

    content = script_path.read_text(encoding='utf-8')

    # 匹配 meta 块中的 grammar-version
    # /**meta
    # grammar-version: 2.0.0
    # */
    match = re.search(r'/\*\*meta\s+.*?grammar-version:\s*([0-9.]+)', content, re.DOTALL)
    if match:
        return match.group(1)

    return None


def detect_features_used(script_path: Path) -> Set[str]:
    """检测脚本中使用的语法特性"""
    features = set()

    if not script_path.exists():
        return features

    content = script_path.read_text(encoding='utf-8')

    # 简单的关键字检测（实际应该使用 lexer/parser）
    keyword_to_feature = {
        r'\blet\s+': 'let',
        r'\bconst\s+': 'const',
        r'\bstep\s+': 'step',
        r'\bif\s+': 'if',
        r'\bwhen\s+': 'when',
        r'\bfor\s+\w+\s+in\s+': 'for',
        r'\bnavigate\s+to\s+': 'navigate',
        r'\bgo\s+(back|forward)': 'go',
        r'\breload\b': 'reload',
        r'\bwait\s+\d+': 'wait_duration',
        r'\bwait\s+for\s+element\s+': 'wait_element',
        r'\bwait\s+for\s+navigation': 'wait_navigation',
        r'\bselect\s+option\s+': 'select_option',
        r'\bselect\s+': 'select',
        r'\btype\s+': 'type',
        r'\bdouble\s+click\s+': 'double_click',
        r'\bright\s+click\s+': 'right_click',
        r'\bclick\s+': 'click',
        r'\bhover\s+': 'hover',
        r'\bclear\s+': 'clear',
        r'\bpress\s+': 'press',
        r'\bscroll\s+': 'scroll',
        r'\bcheck\s+': 'check',
        r'\buncheck\s+': 'check',
        r'\bupload\s+file\s+': 'upload',
        r'\bassert\s+': 'assert',
        r'\bcall\s+': 'call',
        r'\bextract\s+': 'extract',
        r'\blog\s+': 'log',
        r'\bscreenshot\b': 'screenshot',
    }

    for pattern, feature in keyword_to_feature.items():
        if re.search(pattern, content):
            features.add(feature)

    # 检测系统变量
    if re.search(r'\$context\.', content):
        features.add('system_variables')
    if re.search(r'\$page\.', content):
        features.add('system_variables')
    if re.search(r'\$browser\.', content):
        features.add('system_variables')
    if re.search(r'\$env\.', content):
        features.add('system_variables')
    if re.search(r'\$config\.', content):
        features.add('system_variables')

    # 检测内置函数
    if re.search(r'\bMath\.', content):
        features.add('builtin_functions')
    if re.search(r'\bDate\.', content):
        features.add('builtin_functions')
    if re.search(r'\bJSON\.', content):
        features.add('builtin_functions')

    # 检测字符串插值
    if re.search(r'"[^"]*\{[^}]+\}[^"]*"', content):
        features.add('string_interpolation')

    return features


def check_compatibility(
    script_path: Path,
    target_version: str,
    current_version: str
) -> VersionCheckReport:
    """检查脚本与目标版本的兼容性"""

    declared_version = extract_declared_version(script_path)
    features_used = detect_features_used(script_path)

    issues: List[CompatibilityIssue] = []
    deprecated_features = set()
    removed_features = set()

    # 检查每个使用的特性
    for feature_key in features_used:
        if feature_key not in FEATURE_VERSIONS:
            continue

        feature = FEATURE_VERSIONS[feature_key]

        # 检查特性是否在目标版本中可用
        if compare_versions(target_version, feature.added_in) < 0:
            issues.append(CompatibilityIssue(
                line_number=0,
                feature=feature.feature_name,
                issue_type="not_available",
                message=f"Feature '{feature.feature_name}' is not available in {target_version} (added in {feature.added_in})",
                suggestion=f"Upgrade to grammar version {feature.added_in} or higher"
            ))

        # 检查是否使用了废弃特性
        if feature.deprecated_in and compare_versions(target_version, feature.deprecated_in) >= 0:
            deprecated_features.add(feature_key)
            suggestion = f"Use '{feature.replaced_by}' instead" if feature.replaced_by else "Update your code"

            removal_msg = ""
            if feature.removed_in:
                removal_msg = f" (will be removed in {feature.removed_in})"

            issues.append(CompatibilityIssue(
                line_number=0,
                feature=feature.feature_name,
                issue_type="deprecated",
                message=f"Feature '{feature.feature_name}' is deprecated since {feature.deprecated_in}{removal_msg}",
                suggestion=suggestion
            ))

        # 检查是否使用了已移除的特性
        if feature.removed_in and compare_versions(target_version, feature.removed_in) >= 0:
            removed_features.add(feature_key)
            suggestion = f"Use '{feature.replaced_by}' instead" if feature.replaced_by else "Remove this feature"

            issues.append(CompatibilityIssue(
                line_number=0,
                feature=feature.feature_name,
                issue_type="removed",
                message=f"Feature '{feature.feature_name}' was removed in {feature.removed_in}",
                suggestion=suggestion
            ))

    # 判断兼容性状态
    status = CompatibilityStatus.COMPATIBLE
    if removed_features:
        status = CompatibilityStatus.INCOMPATIBLE
    elif deprecated_features:
        status = CompatibilityStatus.WARNING

    return VersionCheckReport(
        script_path=str(script_path),
        declared_version=declared_version,
        target_version=target_version,
        current_version=current_version,
        status=status,
        issues=issues,
        features_used=features_used,
        deprecated_features_used=deprecated_features,
        removed_features_used=removed_features
    )


def print_report(report: VersionCheckReport, show_features: bool = False):
    """打印兼容性报告"""

    print("\n" + "=" * 70)
    print("Grammar Version Compatibility Report")
    print("=" * 70)

    print(f"\n[Script Info]")
    print(f"   Script:            {report.script_path}")
    print(f"   Declared Version:  {report.declared_version or 'Not specified'}")
    print(f"   Target Version:    {report.target_version}")
    print(f"   Current Version:   {report.current_version}")

    if show_features:
        print(f"\n[Features Used]")
        print(f"   Total:             {len(report.features_used)}")
        for feature in sorted(report.features_used):
            if feature in FEATURE_VERSIONS:
                fv = FEATURE_VERSIONS[feature]
                print(f"   - {fv.feature_name} (since {fv.added_in})")

    print(f"\n[Compatibility Status]")

    if report.status == CompatibilityStatus.COMPATIBLE:
        print(f"   Status: {report.status.value} COMPATIBLE")
        print(f"   Message: Script is fully compatible with {report.target_version}")

    elif report.status == CompatibilityStatus.WARNING:
        print(f"   Status: {report.status.value} WARNING")
        print(f"   Message: Script uses {len(report.deprecated_features_used)} deprecated feature(s)")

    else:
        print(f"   Status: {report.status.value} INCOMPATIBLE")
        print(f"   Message: Script uses {len(report.removed_features_used)} removed feature(s)")

    # 显示问题
    if report.issues:
        print(f"\n[Issues Found] ({len(report.issues)})")

        deprecated_issues = [i for i in report.issues if i.issue_type == "deprecated"]
        removed_issues = [i for i in report.issues if i.issue_type == "removed"]
        not_available_issues = [i for i in report.issues if i.issue_type == "not_available"]

        if deprecated_issues:
            print(f"\n  [WARN] Deprecated Features ({len(deprecated_issues)}):")
            for issue in deprecated_issues:
                print(f"   - {issue.feature}")
                print(f"     {issue.message}")
                if issue.suggestion:
                    print(f"     Suggestion: {issue.suggestion}")

        if removed_issues:
            print(f"\n  [ERROR] Removed Features ({len(removed_issues)}):")
            for issue in removed_issues:
                print(f"   - {issue.feature}")
                print(f"     {issue.message}")
                if issue.suggestion:
                    print(f"     Suggestion: {issue.suggestion}")

        if not_available_issues:
            print(f"\n  [ERROR] Not Available Features ({len(not_available_issues)}):")
            for issue in not_available_issues:
                print(f"   - {issue.feature}")
                print(f"     {issue.message}")
                if issue.suggestion:
                    print(f"     Suggestion: {issue.suggestion}")

    print("\n" + "=" * 70 + "\n")

    # 返回退出码
    if report.status == CompatibilityStatus.COMPATIBLE:
        return 0
    elif report.status == CompatibilityStatus.WARNING:
        return 1
    else:
        return 2


def generate_migration_guide(report: VersionCheckReport):
    """生成迁移指南"""

    print("\n" + "=" * 70)
    print(f"Migration Guide: {report.declared_version or 'Unknown'} -> {report.target_version}")
    print("=" * 70)

    if not report.issues:
        print("\n[OK] No migration needed. Script is already compatible.")
        print("=" * 70 + "\n")
        return

    print("\n[Required Changes]")

    for issue in report.issues:
        print(f"\n{issue.issue_type.upper()}: {issue.feature}")
        print(f"   {issue.message}")
        if issue.suggestion:
            print(f"   Suggestion: {issue.suggestion}")

    print("\n" + "=" * 70 + "\n")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Check DSL script grammar version compatibility'
    )
    parser.add_argument('script', type=str,
                       help='Path to DSL script (.flow file)')
    parser.add_argument('--target-version', '-t', type=str, default='3.1.0',
                       help='Target grammar version (default: 3.1.0)')
    parser.add_argument('--current-version', '-c', type=str, default='3.1.0',
                       help='Current grammar version (default: 3.1.0)')
    parser.add_argument('--migration-report', '-m', action='store_true',
                       help='Generate migration guide')
    parser.add_argument('--show-features', '-f', action='store_true',
                       help='Show all features used in the script')

    args = parser.parse_args()

    script_path = Path(args.script)

    if not script_path.exists():
        print(f"[ERROR] Script not found: {script_path}")
        sys.exit(2)

    # 检查兼容性
    print(f"[*] Checking compatibility...")
    report = check_compatibility(script_path, args.target_version, args.current_version)

    # 打印报告
    exit_code = print_report(report, show_features=args.show_features)

    # 生成迁移指南
    if args.migration_report and report.issues:
        generate_migration_guide(report)

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
