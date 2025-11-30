#!/usr/bin/env python3
"""
Grammar Sync Checker

自动检查 GRAMMAR-MASTER.md 与实际代码实现的同步状态

用途:
    1. 验证 GRAMMAR-MASTER.md 中所有 ✅ 特性都有对应的 parser 方法
    2. 验证所有 parser 方法都在 GRAMMAR-MASTER.md 中文档化
    3. 检查测试覆盖情况
    4. 生成同步状态报告

用法:
    python scripts/check_grammar_sync.py
    python scripts/check_grammar_sync.py --verbose
    python scripts/check_grammar_sync.py --fix-status

退出码:
    0: 完全同步
    1: 发现不同步问题
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    """特性状态"""
    IMPLEMENTED = "✅"
    NEEDS_TESTS = "⚠️"
    PARTIAL = "🚧"
    NOT_IMPLEMENTED = "❌"
    DEPRECATED = "🗑️"


@dataclass
class Feature:
    """语法特性"""
    id: str  # 如 "1.1"
    name: str
    syntax: str
    status: Status
    parser_method: str
    tests: str
    notes: str


@dataclass
class ParserMethod:
    """Parser 方法"""
    name: str
    line_number: int
    documented: bool = False


@dataclass
class SyncReport:
    """同步报告"""
    total_features: int
    implemented_features: int
    needs_tests_features: int
    partial_features: int
    not_implemented_features: int
    deprecated_features: int

    total_parser_methods: int
    documented_methods: int
    undocumented_methods: List[str]

    missing_parser_methods: List[str]  # 文档有但代码没有
    missing_tests: List[str]  # 有代码但缺测试

    is_synced: bool


def parse_grammar_master(filepath: Path) -> List[Feature]:
    """解析 GRAMMAR-MASTER.md"""
    features = []

    if not filepath.exists():
        print(f"[ERROR] {filepath} not found")
        return features

    content = filepath.read_text(encoding='utf-8')

    # 匹配主语句特性表格: | 1.1 | Let Declaration | `let VAR = expr` | ✅ | v1.0 | `_parse_let_statement()` | ✅ | ... |
    # 注意：语法列可能包含 \| (转义的竖线)
    # 新格式包含 Since 列，支持多版本格式 (v1.0/v3.0, v1.0, v4.3+)
    pattern1 = r'\|\s*(\d+\.\d+)\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|\s*([✅⚠️🚧❌🗑️])\s*\|\s*v?(\d+\.\d+(?:[/,]\s*v?\d+\.\d+\+?)*)\s*\|\s*`?([^|`]+?)`?\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|'

    for match in re.finditer(pattern1, content):
        feature_id = match.group(1).strip()
        name = match.group(2).strip()
        syntax = match.group(3).strip()
        status_icon = match.group(4).strip()
        since_version = match.group(5).strip()
        parser_method = match.group(6).strip()
        tests = match.group(7).strip()
        notes = match.group(8).strip()

        # 转换状态
        status = Status.IMPLEMENTED
        for s in Status:
            if s.value == status_icon:
                status = s
                break

        features.append(Feature(
            id=feature_id,
            name=name,
            syntax=syntax,
            status=status,
            parser_method=parser_method,
            tests=tests,
            notes=notes
        ))

    # 匹配表达式系统表格: | 1 (Low) | `or` | Left | v1.0 | `_parse_logical_or()` |
    # 支持多版本格式 (v1.0/v3.0, v1.0, v4.3+)
    pattern2 = r'\|\s*(\d+)\s*(?:\([^)]+\))?\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*v?(\d+\.\d+(?:[/,]\s*v?\d+\.\d+\+?)*)\s*\|\s*`?([^|`]+?)`?\s*\|'

    for match in re.finditer(pattern2, content):
        level = match.group(1).strip()
        operators = match.group(2).strip()
        associativity = match.group(3).strip()
        since_version = match.group(4).strip()
        parser_method = match.group(5).strip()

        if parser_method and parser_method.startswith('_parse_'):
            features.append(Feature(
                id=f"expr.{level}",
                name=f"Expression Level {level}",
                syntax=operators,
                status=Status.IMPLEMENTED,
                parser_method=parser_method,
                tests="✅",
                notes=f"Precedence {level}"
            ))

    # 匹配数据类型表格: | String | `"text"`, `'text'` | `"Hello"` | v1.0 | `_parse_primary()` |
    # 支持多词类型名，如 "String Interpolation"
    # 支持多版本格式 (v1.0/v3.0, v1.0, v4.3+)
    pattern3 = r'\|\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*v?(\d+\.\d+(?:[/,]\s*v?\d+\.\d+\+?)*)\s*\|\s*`?([^|`]+?)`?\s*\|'

    in_data_types_section = False
    for line in content.split('\n'):
        if '## 🎨 Data Types' in line or '## Data Types' in line:
            in_data_types_section = True
            continue
        if in_data_types_section and line.startswith('##'):
            in_data_types_section = False
            continue

        if in_data_types_section:
            match = re.match(pattern3, line)
            if match:
                type_name = match.group(1).strip()
                syntax = match.group(2).strip()
                examples = match.group(3).strip()
                since_version = match.group(4).strip()
                parser_method = match.group(5).strip()

                if parser_method and parser_method.startswith('_parse_'):
                    features.append(Feature(
                        id=f"type.{type_name.lower()}",
                        name=f"{type_name} Type",
                        syntax=syntax,
                        status=Status.IMPLEMENTED,
                        parser_method=parser_method,
                        tests="✅",
                        notes=f"Data type parsing"
                    ))

    return features


def parse_parser_methods(filepath: Path) -> List[ParserMethod]:
    """解析 parser.py 中的所有 _parse_* 方法"""
    methods = []

    if not filepath.exists():
        print(f"❌ Error: {filepath} not found")
        return methods

    content = filepath.read_text(encoding='utf-8')

    # 匹配方法定义: def _parse_xxx(...)
    pattern = r'^\s*def\s+(_parse_\w+)\s*\('

    for line_num, line in enumerate(content.split('\n'), start=1):
        match = re.match(pattern, line)
        if match:
            method_name = match.group(1)
            methods.append(ParserMethod(
                name=method_name,
                line_number=line_num
            ))

    return methods


def check_sync(
    features: List[Feature],
    parser_methods: List[ParserMethod]
) -> SyncReport:
    """检查同步状态"""

    # 统计特性状态
    status_count = {
        Status.IMPLEMENTED: 0,
        Status.NEEDS_TESTS: 0,
        Status.PARTIAL: 0,
        Status.NOT_IMPLEMENTED: 0,
        Status.DEPRECATED: 0
    }

    for feature in features:
        status_count[feature.status] += 1

    # 提取文档中的 parser 方法
    documented_methods = set()
    for feature in features:
        if feature.parser_method and feature.parser_method != '-':
            # 清理方法名: _parse_let_statement() -> _parse_let_statement
            method_name = feature.parser_method.strip('`()').strip()
            documented_methods.add(method_name)

    # 提取代码中的 parser 方法
    code_methods = {m.name for m in parser_methods}

    # 标记文档化的方法
    for method in parser_methods:
        if method.name in documented_methods:
            method.documented = True

    # 找出未文档化的方法
    undocumented = []
    for method in parser_methods:
        if not method.documented:
            # 排除一些辅助方法
            if method.name in ['_parse_statement', '_parse_expression',
                               '_parse_variable_name', '_parse_attribute_name',
                               '_parse_where_clause', '_parse_call_parameters',
                               '_parse_call_parameter', '_parse_number_value',
                               '_parse_object_pair', '_parse_time_value',
                               '_parse_string_with_interpolation',
                               '_parse_array_literal', '_parse_object_literal',
                               '_parse_string_interpolation',
                               '_parse_method_arguments']:
                continue
            undocumented.append(f"{method.name} (line {method.line_number})")

    # 找出缺失的 parser 方法（文档有但代码没有）
    missing_parser = []
    for feature in features:
        if feature.status == Status.IMPLEMENTED or feature.status == Status.NEEDS_TESTS:
            method_name = feature.parser_method.strip('`()').strip()
            if method_name and method_name != '-' and method_name not in code_methods:
                missing_parser.append(f"Feature {feature.id} ({feature.name}) expects {method_name}")

    # 找出缺失测试的特性
    missing_tests = []
    for feature in features:
        if feature.status == Status.NEEDS_TESTS:
            missing_tests.append(f"Feature {feature.id} ({feature.name})")
        elif feature.status == Status.IMPLEMENTED and feature.tests.strip() != '✅':
            missing_tests.append(f"Feature {feature.id} ({feature.name}) - marked as implemented but tests not ✅")

    # 判断是否同步
    is_synced = (
        len(undocumented) == 0 and
        len(missing_parser) == 0 and
        len(missing_tests) == 0 and
        status_count[Status.NEEDS_TESTS] == 0 and
        status_count[Status.PARTIAL] == 0
    )

    return SyncReport(
        total_features=len(features),
        implemented_features=status_count[Status.IMPLEMENTED],
        needs_tests_features=status_count[Status.NEEDS_TESTS],
        partial_features=status_count[Status.PARTIAL],
        not_implemented_features=status_count[Status.NOT_IMPLEMENTED],
        deprecated_features=status_count[Status.DEPRECATED],
        total_parser_methods=len(parser_methods),
        documented_methods=len(documented_methods),
        undocumented_methods=undocumented,
        missing_parser_methods=missing_parser,
        missing_tests=missing_tests,
        is_synced=is_synced
    )


def print_report(report: SyncReport, verbose: bool = False):
    """打印同步报告"""

    print("\n" + "=" * 70)
    print("Grammar Sync Report")
    print("=" * 70)

    # 特性统计
    print("\n[Feature Statistics]")
    print(f"   Total Features:        {report.total_features}")
    print(f"   [OK] Implemented:      {report.implemented_features}")
    print(f"   [!]  Needs Tests:      {report.needs_tests_features}")
    print(f"   [~]  Partial:          {report.partial_features}")
    print(f"   [X]  Not Implemented:  {report.not_implemented_features}")
    print(f"   [-]  Deprecated:       {report.deprecated_features}")

    # Parser 方法统计
    print(f"\n[Parser Methods]")
    print(f"   Total Methods:         {report.total_parser_methods}")
    print(f"   Documented:            {report.documented_methods}")
    print(f"   Undocumented:          {len(report.undocumented_methods)}")

    # 问题报告
    has_issues = False

    if report.undocumented_methods:
        has_issues = True
        print(f"\n[ERROR] Undocumented Parser Methods ({len(report.undocumented_methods)}):")
        for method in report.undocumented_methods:
            print(f"   - {method}")

    if report.missing_parser_methods:
        has_issues = True
        print(f"\n[ERROR] Missing Parser Methods ({len(report.missing_parser_methods)}):")
        for issue in report.missing_parser_methods:
            print(f"   - {issue}")

    if report.missing_tests:
        has_issues = True
        print(f"\n[WARN] Missing or Incomplete Tests ({len(report.missing_tests)}):")
        for issue in report.missing_tests:
            print(f"   - {issue}")

    # 同步状态
    print("\n" + "=" * 70)
    if report.is_synced:
        print("[OK] Status: SYNCED")
        print("     Grammar and implementation are in sync!")
    else:
        print("[ERROR] Status: OUT OF SYNC")
        print("        Grammar and implementation have inconsistencies.")
        print("\n        Please fix the issues above before merging.")
    print("=" * 70 + "\n")

    return 0 if report.is_synced else 1


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='Check grammar sync status')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show verbose output')
    parser.add_argument('--fix-status', action='store_true',
                       help='Suggest fixes for status issues')

    args = parser.parse_args()

    # 路径配置
    # 工具位于: grammar/tools/check_sync.py
    # 项目根目录: ../../
    project_root = Path(__file__).parent.parent.parent
    grammar_master_path = project_root / 'grammar' / 'MASTER.md'
    parser_path = project_root / 'src' / 'registration_system' / 'dsl' / 'parser.py'

    if args.verbose:
        print(f"[*] Project root: {project_root}")
        print(f"[*] Grammar master: {grammar_master_path}")
        print(f"[*] Parser file: {parser_path}")
        print()

    # 解析文件
    print("[*] Parsing grammar/MASTER.md...")
    features = parse_grammar_master(grammar_master_path)
    print(f"    Found {len(features)} features")

    print("[*] Parsing parser.py...")
    parser_methods = parse_parser_methods(parser_path)
    print(f"    Found {len(parser_methods)} parser methods")

    # 检查同步
    print("\n[*] Checking sync status...")
    report = check_sync(features, parser_methods)

    # 打印报告
    exit_code = print_report(report, verbose=args.verbose)

    # 建议修复
    if args.fix_status and not report.is_synced:
        print("\n[SUGGESTIONS] Suggested Fixes:")
        print("=" * 70)

        if report.undocumented_methods:
            print("\n1. Add undocumented methods to GRAMMAR-MASTER.md:")
            print("   - Review each method and add it to the appropriate section")
            print("   - Or mark them as helper methods (comment in code)")

        if report.missing_parser_methods:
            print("\n2. Implement missing parser methods:")
            print("   - Add the methods to parser.py")
            print("   - Or update GRAMMAR-MASTER.md if feature is not actually implemented")

        if report.missing_tests:
            print("\n3. Add missing tests:")
            print("   - Create test cases in tests/ directory")
            print("   - Update GRAMMAR-MASTER.md test status to ✅")

        if report.needs_tests_features > 0:
            print("\n4. Fix features with ⚠️ status:")
            print("   - Add comprehensive test coverage")
            print("   - Update status to ✅ in GRAMMAR-MASTER.md")

        if report.partial_features > 0:
            print("\n5. Complete partial features (🚧):")
            print("   - Finish implementation")
            print("   - Add tests")
            print("   - Update status to ✅")

        print("=" * 70 + "\n")

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
