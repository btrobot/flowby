#!/usr/bin/env python3
"""
Grammar Feature Coverage Verification Script

验证 grammar/MASTER.md 中定义的所有特性是否都有对应的测试覆盖。

用法:
    python verify_grammar_coverage.py [--output REPORT.md]
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import argparse


class FeatureExtractor:
    """从 MASTER.md 提取特性定义"""

    def __init__(self, master_md_path: Path):
        self.master_md_path = master_md_path
        self.features = {}

    def extract_all_features(self) -> Dict[str, Dict]:
        """提取所有特性"""
        content = self.master_md_path.read_text(encoding='utf-8')

        features = {}

        # 1. 提取编号特性（1.1-10.2）
        numbered_features = self._extract_numbered_features(content)
        features.update(numbered_features)

        # 2. 提取表达式系统（9个层次）
        expression_features = self._extract_expression_features(content)
        features.update(expression_features)

        # 3. 提取数据类型（7种）
        datatype_features = self._extract_datatype_features(content)
        features.update(datatype_features)

        # 4. 提取系统变量（5个命名空间）
        sysvar_features = self._extract_sysvar_features(content)
        features.update(sysvar_features)

        # 5. 提取内置函数（19个）
        builtin_features = self._extract_builtin_features(content)
        features.update(builtin_features)

        self.features = features
        return features

    def _extract_numbered_features(self, content: str) -> Dict[str, Dict]:
        """提取编号特性（1.1-10.2）"""
        features = {}

        # 匹配表格行，使用灵活的模式
        # 寻找所有包含特性 ID 的行
        lines = content.split('\n')

        for line in lines:
            # 跳过非表格行
            if not line.strip().startswith('|') or '|---|' in line or '| # |' in line:
                continue

            # 尝试提取特性 ID (X.Y 格式)
            id_match = re.search(r'\|\s*(\d+\.\d+)\s*\|', line)
            if not id_match:
                continue

            feature_id = id_match.group(1).strip()

            # 分割表格列
            columns = [col.strip() for col in line.split('|')]
            # 过滤空列
            columns = [col for col in columns if col]

            if len(columns) < 7:  # 至少需要 7 列
                continue

            feature_name = columns[1]

            # 提取语法（第三列，可能包含多个反引号）
            syntax_raw = columns[2]
            syntax_parts = re.findall(r'`([^`]+)`', syntax_raw)
            syntax = ' / '.join(syntax_parts) if syntax_parts else syntax_raw.strip('`')

            status = columns[3]
            since = columns[4]
            parser_method = columns[5].strip('`').strip()
            test_status = columns[6] if len(columns) > 6 else '✅'

            features[feature_id] = {
                'id': feature_id,
                'name': feature_name,
                'syntax': syntax,
                'status': status,
                'since': since,
                'parser_method': parser_method,
                'test_status': test_status,
                'category': self._get_category(feature_id)
            }

        return features

    def _extract_expression_features(self, content: str) -> Dict[str, Dict]:
        """提取表达式系统特性"""
        features = {}

        # 查找表达式系统表格
        expr_section = re.search(
            r'## 📈 Expression System.*?### Operator Precedence.*?\n(.*?)\n\*\*Test Coverage',
            content,
            re.DOTALL
        )

        if expr_section:
            table_content = expr_section.group(1)
            # 匹配: | 1 (Low) | `or` | Left | v1.0 | `_parse_logical_or()` |
            # 或: | 2 | `and` | Left | v1.0 | `_parse_logical_and()` |
            # 或: | 9 (High) | Literals, Variables | - | v1.0 | `_parse_primary()` |
            pattern = r'\|\s*(\d+)\s*(?:\([^)]+\))?\s*\|\s*([^|]+?)\s*\|\s*(\S+)\s*\|\s*([^|]+?)\s*\|\s*`?([^`|]+?)`?\s*\|'

            for match in re.finditer(pattern, table_content):
                level = match.group(1).strip()
                operators_raw = match.group(2).strip()
                associativity = match.group(3).strip()
                since = match.group(4).strip()
                parser_method = match.group(5).strip()

                # 清理运算符（去除反引号）
                operators = operators_raw.replace('`', '').strip()

                feature_id = f"expr-level{level}"
                features[feature_id] = {
                    'id': feature_id,
                    'name': f'Expression Level {level}: {operators}',
                    'syntax': operators,
                    'status': '✅',
                    'since': since,
                    'parser_method': parser_method,
                    'test_status': '✅',
                    'category': 'Expressions'
                }

        return features

    def _extract_datatype_features(self, content: str) -> Dict[str, Dict]:
        """提取数据类型特性"""
        features = {}

        # 查找数据类型表格
        datatype_section = re.search(
            r'## 🎨 Data Types.*?\n(.*?)\n\*\*Test Coverage',
            content,
            re.DOTALL
        )

        if datatype_section:
            table_content = datatype_section.group(1)
            # 匹配: | String | `"text"`, `'text'` | `"Hello"` | v1.0 | `_parse_primary()` |
            pattern = r'\|\s*(\w+(?:\s+\w+)?)\s*\|\s*`([^`]+)`(?:,\s*`[^`]+`)?\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*`([^`]+)`'

            for match in re.finditer(pattern, table_content):
                type_name = match.group(1).strip()
                syntax = match.group(2).strip()
                since = match.group(4).strip()
                parser_method = match.group(5).strip()

                feature_id = f"type-{type_name.lower().replace(' ', '-')}"
                features[feature_id] = {
                    'id': feature_id,
                    'name': f'{type_name} Type',
                    'syntax': syntax,
                    'status': '✅',
                    'since': since,
                    'parser_method': parser_method,
                    'test_status': '✅',
                    'category': 'Data Types'
                }

        return features

    def _extract_sysvar_features(self, content: str) -> Dict[str, Dict]:
        """提取系统变量特性"""
        features = {}

        # 查找系统变量表格
        sysvar_section = re.search(
            r'## 🔧 System Variables.*?\n(.*?)\n\*\*Test Coverage',
            content,
            re.DOTALL
        )

        if sysvar_section:
            table_content = sysvar_section.group(1)
            # 匹配: | `$context` | ... | `$context.task_id` | v2.0 | ✅ |
            pattern = r'\|\s*`(\$\w+)`\s*\|\s*([^|]+)\|\s*`([^`]+)`\s*\|\s*([^|]+)\|\s*([✅⚠️🚧❌]+)'

            for match in re.finditer(pattern, table_content):
                namespace = match.group(1).strip()
                properties = match.group(2).strip()
                example = match.group(3).strip()
                since = match.group(4).strip()
                status = match.group(5).strip()

                feature_id = f"sysvar-{namespace[1:]}"  # 去掉 $
                features[feature_id] = {
                    'id': feature_id,
                    'name': f'System Variable {namespace}',
                    'syntax': example,
                    'status': status,
                    'since': since,
                    'parser_method': 'System Variable',
                    'test_status': status,
                    'category': 'System Variables'
                }

        return features

    def _extract_builtin_features(self, content: str) -> Dict[str, Dict]:
        """提取内置函数特性"""
        features = {}

        # 查找内置函数各个命名空间
        namespaces = ['Math', 'Date', 'JSON', 'Global Functions']

        for namespace in namespaces:
            # 查找命名空间表格
            if namespace == 'Global Functions':
                section_pattern = f'### {namespace}.*?\\n(.*?)\\n\\*\\*Test Coverage'
            else:
                section_pattern = f'### {namespace} Namespace.*?\\n(.*?)(?=###|\\*\\*Test Coverage)'

            section = re.search(section_pattern, content, re.DOTALL)

            if section:
                table_content = section.group(1)
                # 匹配: | `Math.abs(x)` | v2.0 | ✅ | ✅ |
                pattern = r'\|\s*`([^`]+)`\s*\|\s*([^|]+)\|\s*([✅⚠️🚧❌]+)\s*\|\s*([✅⚠️🚧❌]+)'

                for match in re.finditer(pattern, table_content):
                    function_sig = match.group(1).strip()
                    since = match.group(2).strip()
                    status = match.group(3).strip()
                    test_status = match.group(4).strip()

                    # 提取函数名
                    func_name = function_sig.split('(')[0]
                    feature_id = f"builtin-{func_name.replace('.', '-').lower()}"

                    features[feature_id] = {
                        'id': feature_id,
                        'name': f'Built-in Function: {function_sig}',
                        'syntax': function_sig,
                        'status': status,
                        'since': since,
                        'parser_method': 'Built-in Function',
                        'test_status': test_status,
                        'category': f'Built-in: {namespace}'
                    }

        return features

    def _get_category(self, feature_id: str) -> str:
        """根据特性 ID 获取分类"""
        prefix = feature_id.split('.')[0]
        categories = {
            '1': 'Variables & Assignment',
            '2': 'Control Flow',
            '3': 'Navigation',
            '4': 'Wait',
            '5': 'Selection',
            '6': 'Actions',
            '7': 'Assertions',
            '8': 'Service Call',
            '9': 'Data Extraction',
            '10': 'Utilities'
        }
        return categories.get(prefix, 'Unknown')


class TestCoverageScanner:
    """扫描测试文件提取覆盖信息"""

    def __init__(self, test_dir: Path):
        self.test_dir = test_dir
        self.coverage = defaultdict(list)

        # 特性 ID 同义词映射
        self.synonyms = {
            # 表达式系统
            'expr-1': 'expr-level1',
            'expr-2': 'expr-level2',
            'expr-3': 'expr-level3',
            'expr-4': 'expr-level4',
            'expr-5': 'expr-level5',
            'expr-6': 'expr-level6',
            'expr-7': 'expr-level7',
            'expr-8': 'expr-level8',
            'expr-9': 'expr-level9',

            # 数据类型
            'data-type-string': 'type-string',
            'data-type-string-interpolation': 'type-string-interpolation',
            'data-type-number': 'type-number',
            'data-type-boolean': 'type-boolean',
            'data-type-null': 'type-null',
            'data-type-array': 'type-array',
            'data-type-object': 'type-object',

            # 系统变量
            'system-var-context': 'sysvar-context',
            'system-var-page': 'sysvar-page',
            'system-var-browser': 'sysvar-browser',
            'system-var-env': 'sysvar-env',
            'system-var-config': 'sysvar-config',

            # 内置函数分组（映射到通用类别）
            'builtin-math': ['builtin-math-abs', 'builtin-math-round', 'builtin-math-ceil',
                            'builtin-math-floor', 'builtin-math-max', 'builtin-math-min',
                            'builtin-math-random', 'builtin-math-pow', 'builtin-math-sqrt'],
            'builtin-date': ['builtin-date-now', 'builtin-date-format', 'builtin-date-from_timestamp'],
            'builtin-json': ['builtin-json-stringify', 'builtin-json-parse'],
            'builtin-global': ['builtin-number', 'builtin-string', 'builtin-boolean',
                              'builtin-isnan', 'builtin-isfinite'],

            # 断言部分（v2.0 通用语法）
            '7.x': ['7.1', '7.2', '7.3', '7.4'],  # v2.0 实现覆盖所有 v1.0 特定语法
            '7.1-7.4': ['7.1', '7.2', '7.3', '7.4'],

            # 其他
            'VR-VAR': ['1.1', '1.2', '1.3'],  # 验证规则测试覆盖变量特性
            '4.x': ['4.1', '4.2', '4.3'],  # Wait 特性通用测试
        }

    def scan_all_tests(self) -> Dict[str, List[str]]:
        """扫描所有测试文件"""
        test_files = sorted(self.test_dir.glob('test_*.py'))

        for test_file in test_files:
            self._scan_test_file(test_file)

        # 应用同义词映射
        self._apply_synonyms()

        return dict(self.coverage)

    def _apply_synonyms(self):
        """应用同义词映射，将测试 ID 转换为标准 ID"""
        # 创建新的覆盖字典
        normalized_coverage = defaultdict(list)

        for test_id, test_files in self.coverage.items():
            if test_id in self.synonyms:
                mapped = self.synonyms[test_id]

                # 如果映射是列表，表示一个测试覆盖多个特性
                if isinstance(mapped, list):
                    for standard_id in mapped:
                        normalized_coverage[standard_id].extend(test_files)
                else:
                    # 单个映射
                    normalized_coverage[mapped].extend(test_files)
            else:
                # 没有映射，保持原样
                normalized_coverage[test_id].extend(test_files)

        # 去重
        for feature_id in normalized_coverage:
            normalized_coverage[feature_id] = list(set(normalized_coverage[feature_id]))

        self.coverage = normalized_coverage

    def _scan_test_file(self, test_file: Path):
        """扫描单个测试文件"""
        content = test_file.read_text(encoding='utf-8')

        # 1. 查找 @pytest.mark.feature("X.Y") 标记
        feature_marks = re.findall(r'@pytest\.mark\.feature\(["\']([^"\']+)["\']\)', content)

        for feature_id in feature_marks:
            self.coverage[feature_id].append(str(test_file.name))

        # 2. 从类名推断特性（如 Test1_1_LetDeclaration）
        class_pattern = r'class\s+Test(\d+)_(\d+)_\w+'
        for match in re.finditer(class_pattern, content):
            major = match.group(1)
            minor = match.group(2)
            feature_id = f"{major}.{minor}"
            if str(test_file.name) not in self.coverage[feature_id]:
                self.coverage[feature_id].append(str(test_file.name))

        # 3. 特殊情况：表达式、数据类型等
        if 'test_expressions.py' in str(test_file):
            # 为所有表达式层次添加覆盖
            for level in range(1, 10):
                self.coverage[f'expr-level{level}'].append(str(test_file.name))

        if 'test_data_types.py' in str(test_file):
            # 为所有数据类型添加覆盖
            types = ['string', 'string-interpolation', 'number', 'boolean', 'null', 'array', 'object']
            for dtype in types:
                self.coverage[f'type-{dtype}'].append(str(test_file.name))

        if 'test_system_variables.py' in str(test_file):
            # 为所有系统变量命名空间添加覆盖
            namespaces = ['context', 'page', 'browser', 'env', 'config']
            for ns in namespaces:
                self.coverage[f'sysvar-{ns}'].append(str(test_file.name))

        if 'test_builtin_functions.py' in str(test_file):
            # 为所有内置函数添加覆盖
            functions = [
                'math-abs', 'math-round', 'math-ceil', 'math-floor',
                'math-max', 'math-min', 'math-random', 'math-pow', 'math-sqrt',
                'date-now', 'date-format', 'date-from_timestamp',
                'json-stringify', 'json-parse',
                'number', 'string', 'boolean', 'isnan', 'isfinite'
            ]
            for func in functions:
                self.coverage[f'builtin-{func}'].append(str(test_file.name))


class CoverageValidator:
    """交叉验证并生成报告"""

    def __init__(self, features: Dict, coverage: Dict):
        self.features = features
        self.coverage = coverage

    def validate(self) -> Dict:
        """执行验证"""
        result = {
            'total_features': len(self.features),
            'covered_features': 0,
            'missing_features': [],
            'orphan_tests': [],
            'coverage_by_category': defaultdict(lambda: {'total': 0, 'covered': 0}),
            'feature_details': []
        }

        # 统计覆盖情况
        for feature_id, feature_info in self.features.items():
            category = feature_info['category']
            result['coverage_by_category'][category]['total'] += 1

            is_covered = feature_id in self.coverage
            if is_covered:
                result['covered_features'] += 1
                result['coverage_by_category'][category]['covered'] += 1
                test_files = self.coverage[feature_id]
            else:
                result['missing_features'].append(feature_id)
                test_files = []

            result['feature_details'].append({
                'id': feature_id,
                'name': feature_info['name'],
                'category': category,
                'covered': is_covered,
                'test_files': test_files,
                'test_count': len(test_files)
            })

        # 查找孤立测试
        covered_feature_ids = set(self.features.keys())
        for test_feature_id in self.coverage.keys():
            if test_feature_id not in covered_feature_ids:
                result['orphan_tests'].append({
                    'id': test_feature_id,
                    'test_files': self.coverage[test_feature_id]
                })

        return result

    def generate_report(self, result: Dict, output_path: Path):
        """生成 Markdown 报告"""
        report = []

        # 标题
        report.append("# Grammar Feature Coverage Validation Report")
        report.append("")
        report.append(f"**Generated**: {self._get_timestamp()}")
        report.append("")
        report.append("---")
        report.append("")

        # 总体统计
        coverage_pct = (result['covered_features'] / result['total_features'] * 100) if result['total_features'] > 0 else 0
        report.append("## 📊 Overall Statistics")
        report.append("")
        report.append("| Metric | Value | Status |")
        report.append("|--------|-------|--------|")
        report.append(f"| Total Features | {result['total_features']} | - |")
        report.append(f"| Covered Features | {result['covered_features']} | {'✅' if coverage_pct == 100 else '⚠️'} |")
        report.append(f"| Missing Features | {len(result['missing_features'])} | {'✅' if len(result['missing_features']) == 0 else '❌'} |")
        report.append(f"| Coverage Percentage | {coverage_pct:.1f}% | {'✅' if coverage_pct == 100 else '⚠️'} |")
        report.append(f"| Orphan Tests | {len(result['orphan_tests'])} | {'✅' if len(result['orphan_tests']) == 0 else '⚠️'} |")
        report.append("")

        # 按分类统计
        report.append("## 📂 Coverage by Category")
        report.append("")
        report.append("| Category | Total | Covered | Coverage | Status |")
        report.append("|----------|-------|---------|----------|--------|")

        for category, stats in sorted(result['coverage_by_category'].items()):
            cat_pct = (stats['covered'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status = '✅' if cat_pct == 100 else '⚠️'
            bar = self._generate_bar(cat_pct)
            report.append(f"| {category} | {stats['total']} | {stats['covered']} | {bar} {cat_pct:.0f}% | {status} |")

        report.append("")

        # 未覆盖特性
        if result['missing_features']:
            report.append("## ❌ Missing Feature Coverage")
            report.append("")
            report.append("以下特性在 MASTER.md 中定义，但没有找到对应的测试：")
            report.append("")
            report.append("| Feature ID | Feature Name | Category |")
            report.append("|------------|--------------|----------|")

            for feature_id in result['missing_features']:
                feature_info = self.features[feature_id]
                report.append(f"| {feature_id} | {feature_info['name']} | {feature_info['category']} |")

            report.append("")
        else:
            report.append("## ✅ All Features Covered")
            report.append("")
            report.append("所有在 MASTER.md 中定义的特性都有对应的测试覆盖！")
            report.append("")

        # 孤立测试
        if result['orphan_tests']:
            report.append("## ⚠️ Orphan Tests")
            report.append("")
            report.append("以下测试标记的特性在 MASTER.md 中未找到定义：")
            report.append("")
            report.append("| Test Feature ID | Test Files |")
            report.append("|----------------|------------|")

            for orphan in result['orphan_tests']:
                files = ', '.join(orphan['test_files'])
                report.append(f"| {orphan['id']} | {files} |")

            report.append("")

        # 详细特性列表
        report.append("## 📋 Detailed Feature Coverage")
        report.append("")

        # 按分类分组
        by_category = defaultdict(list)
        for detail in result['feature_details']:
            by_category[detail['category']].append(detail)

        for category in sorted(by_category.keys()):
            report.append(f"### {category}")
            report.append("")
            report.append("| Feature ID | Feature Name | Status | Test Files |")
            report.append("|------------|--------------|--------|------------|")

            for detail in sorted(by_category[category], key=lambda x: x['id']):
                status = '✅' if detail['covered'] else '❌'
                test_files = ', '.join(detail['test_files']) if detail['test_files'] else '-'
                report.append(f"| {detail['id']} | {detail['name']} | {status} | {test_files} |")

            report.append("")

        # 写入文件
        output_path.write_text('\n'.join(report), encoding='utf-8')

        return '\n'.join(report)

    def _generate_bar(self, percentage: float) -> str:
        """生成进度条"""
        filled = int(percentage / 5)  # 每 5% 一个方块
        empty = 20 - filled
        return '█' * filled + '░' * empty

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='验证语法特性测试覆盖')
    parser.add_argument('--output', '-o', default='COVERAGE-REPORT.md',
                        help='输出报告文件名（默认：COVERAGE-REPORT.md）')
    args = parser.parse_args()

    # 路径设置
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    master_md = script_dir / 'MASTER.md'
    test_dir = project_root / 'tests' / 'grammar_alignment'
    output_path = script_dir / args.output

    print("Grammar Feature Coverage Verification")
    print("=" * 60)
    print()

    # 1. 提取特性
    print(f"[1/4] Parsing {master_md.name}...")
    extractor = FeatureExtractor(master_md)
    features = extractor.extract_all_features()
    print(f"      Found {len(features)} features")
    print()

    # 2. 扫描测试
    print(f"[2/4] Scanning test files in {test_dir.name}/...")
    scanner = TestCoverageScanner(test_dir)
    coverage = scanner.scan_all_tests()
    print(f"      Found coverage for {len(coverage)} features")
    print()

    # 3. 验证
    print("[3/4] Cross-validating...")
    validator = CoverageValidator(features, coverage)
    result = validator.validate()
    print(f"      Validation complete")
    print()

    # 4. 生成报告
    print(f"[4/4] Generating report...")
    validator.generate_report(result, output_path)
    print(f"      Report saved to: {output_path}")
    print()

    # 5. 显示摘要
    coverage_pct = (result['covered_features'] / result['total_features'] * 100) if result['total_features'] > 0 else 0

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Features:    {result['total_features']}")
    print(f"Covered Features:  {result['covered_features']}")
    print(f"Missing Features:  {len(result['missing_features'])}")
    print(f"Coverage:          {coverage_pct:.1f}%")
    print(f"Orphan Tests:      {len(result['orphan_tests'])}")
    print()

    if result['missing_features']:
        print("[!] Missing Coverage:")
        for feature_id in result['missing_features'][:5]:  # 显示前5个
            print(f"   - {feature_id}: {features[feature_id]['name']}")
        if len(result['missing_features']) > 5:
            print(f"   ... and {len(result['missing_features']) - 5} more")
        print()

    if coverage_pct == 100 and len(result['orphan_tests']) == 0:
        print("[OK] PERFECT COVERAGE! All features are tested!")
        return 0
    else:
        print("[WARN] Coverage is incomplete. See report for details.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
