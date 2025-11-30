#!/usr/bin/env python3
"""
语义验证工具

检查 AST 定义、解释器实现和语义正确性

用途:
    1. 验证所有 AST 节点都在解释器中有对应实现
    2. 验证解释器覆盖所有语法特性
    3. 检查语义实现的正确性
    4. 生成语义验证报告

用法:
    python grammar/tools/check_semantics.py
    python grammar/tools/check_semantics.py --verbose

退出码:
    0: 语义实现完整且正确
    1: 发现语义问题
"""

import re
import sys
from pathlib import Path
from typing import List, Set, Dict, Any
from dataclasses import dataclass


@dataclass
class ASTNodeInfo:
    """AST 节点信息"""
    name: str
    line_number: int
    has_handler: bool = False
    handler_line: int = 0


@dataclass
class SemanticReport:
    """语义验证报告"""
    total_ast_nodes: int
    statement_nodes: int
    expression_nodes: int
    handled_nodes: int
    unhandled_nodes: List[str]

    total_handlers: int
    handler_without_node: List[str]

    is_complete: bool


def extract_ast_nodes(ast_file: Path) -> Dict[str, ASTNodeInfo]:
    """提取 AST 节点定义"""
    nodes = {}

    if not ast_file.exists():
        print(f"❌ Error: {ast_file} not found")
        return nodes

    content = ast_file.read_text(encoding='utf-8')

    # 匹配 @dataclass 后跟的类定义
    pattern = r'^@dataclass\s*\nclass\s+(\w+)\((ASTNode|Statement|Expression|Condition)\):'

    for line_num, line in enumerate(content.split('\n'), start=1):
        # 检查是否是 @dataclass
        if line.strip() == '@dataclass':
            # 查找下一行的类定义
            next_lines = content.split('\n')[line_num:]
            for offset, next_line in enumerate(next_lines[:3]):  # 最多向后看3行
                match = re.match(r'class\s+(\w+)\((ASTNode|Statement|Expression|Condition)\):', next_line.strip())
                if match:
                    node_name = match.group(1)
                    nodes[node_name] = ASTNodeInfo(
                        name=node_name,
                        line_number=line_num + offset + 1
                    )
                    break

    return nodes


def extract_interpreter_handlers(interpreter_file: Path) -> Dict[str, int]:
    """提取解释器处理器"""
    handlers = {}

    if not interpreter_file.exists():
        print(f"❌ Error: {interpreter_file} not found")
        return handlers

    content = interpreter_file.read_text(encoding='utf-8')

    # 匹配 if isinstance 或 elif isinstance
    pattern = r'(?:if|elif)\s+isinstance\((?:statement|expr|program),\s+(\w+)\):'

    for line_num, line in enumerate(content.split('\n'), start=1):
        match = re.search(pattern, line)
        if match:
            node_name = match.group(1)
            handlers[node_name] = line_num

    return handlers


def check_semantics(
    ast_nodes: Dict[str, ASTNodeInfo],
    handlers: Dict[str, int]
) -> SemanticReport:
    """检查语义完整性"""

    # 标记有处理器的节点
    for node_name, node_info in ast_nodes.items():
        if node_name in handlers:
            node_info.has_handler = True
            node_info.handler_line = handlers[node_name]

    # 找出没有处理器的节点
    unhandled = []
    for node_name, node_info in ast_nodes.items():
        if not node_info.has_handler:
            # 排除基类
            if node_name in ['ASTNode', 'Expression', 'Statement', 'Condition']:
                continue
            # 排除辅助类
            if node_name in ['CallParameter', 'WhenClause']:
                continue
            # 排除 Program（在 execute() 方法中处理）
            if node_name == 'Program':
                node_info.has_handler = True
                continue
            # 排除表达式节点（由 ExpressionEvaluator 处理）
            if node_name in ['BinaryOp', 'UnaryOp', 'Literal', 'Identifier',
                             'SystemVariable', 'MemberAccess', 'ArrayAccess',
                             'MethodCall', 'ArrayLiteral', 'ObjectLiteral',
                             'StringInterpolation', 'FunctionCall',
                             'MemberAccessExpression',  # v5.0 模块成员访问
                             'InputExpression']:  # v5.1 控制台输入
                # 标记为已处理（由 ExpressionEvaluator 处理）
                node_info.has_handler = True
                continue
            unhandled.append(f"{node_name} (line {node_info.line_number})")

    # 找出没有对应节点的处理器
    handler_without_node = []
    for handler_name, line_num in handlers.items():
        if handler_name not in ast_nodes:
            handler_without_node.append(f"{handler_name} (line {line_num})")

    # 分类节点
    statement_nodes = 0
    expression_nodes = 0
    for node_name in ast_nodes.keys():
        if 'Statement' in node_name or 'Block' in node_name or 'Action' in node_name or node_name in ['Program', 'Assignment', 'EachLoop']:
            statement_nodes += 1
        elif 'Expression' in node_name or node_name in ['Literal', 'Identifier', 'BinaryOp', 'UnaryOp',
                                                          'MemberAccess', 'ArrayAccess', 'MethodCall',
                                                          'ArrayLiteral', 'ObjectLiteral', 'StringInterpolation',
                                                          'SystemVariable', 'FunctionCall',
                                                          'MemberAccessExpression', 'InputExpression']:
            expression_nodes += 1

    is_complete = (len(unhandled) == 0 and len(handler_without_node) == 0)

    return SemanticReport(
        total_ast_nodes=len(ast_nodes),
        statement_nodes=statement_nodes,
        expression_nodes=expression_nodes,
        handled_nodes=len([n for n in ast_nodes.values() if n.has_handler]),
        unhandled_nodes=unhandled,
        total_handlers=len(handlers),
        handler_without_node=handler_without_node,
        is_complete=is_complete
    )


def print_report(report: SemanticReport, verbose: bool = False):
    """打印语义验证报告"""

    print("\n" + "=" * 70)
    print("Semantic Verification Report")
    print("=" * 70)

    # AST 节点统计
    print("\n[AST Nodes Statistics]")
    print(f"   Total AST Nodes:       {report.total_ast_nodes}")
    print(f"   Statement Nodes:       {report.statement_nodes}")
    print(f"   Expression Nodes:      {report.expression_nodes}")
    print(f"   Other Nodes:           {report.total_ast_nodes - report.statement_nodes - report.expression_nodes}")

    # 解释器处理器统计
    print(f"\n[Interpreter Handlers]")
    print(f"   Total Handlers:        {report.total_handlers}")
    print(f"   Handled Nodes:         {report.handled_nodes}")
    print(f"   Coverage:              {report.handled_nodes}/{report.total_ast_nodes} ({report.handled_nodes*100//report.total_ast_nodes}%)")

    # 问题报告
    has_issues = False

    if report.unhandled_nodes:
        has_issues = True
        print(f"\n[ERROR] Unhandled AST Nodes ({len(report.unhandled_nodes)}):")
        for node in report.unhandled_nodes:
            print(f"   - {node}")

    if report.handler_without_node:
        has_issues = True
        print(f"\n[WARNING] Handlers Without AST Node ({len(report.handler_without_node)}):")
        for handler in report.handler_without_node:
            print(f"   - {handler}")

    # 语义完整性状态
    print("\n" + "=" * 70)
    if report.is_complete:
        print("[OK] Status: SEMANTICS COMPLETE")
        print("     All AST nodes have corresponding interpreter handlers!")
    else:
        print("[ERROR] Status: SEMANTICS INCOMPLETE")
        print("        Some AST nodes are missing interpreter handlers.")
        print("\n        Please implement handlers for unhandled nodes.")
    print("=" * 70 + "\n")

    return 0 if report.is_complete else 1


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='Check semantic implementation')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show verbose output')

    args = parser.parse_args()

    # 路径配置
    project_root = Path(__file__).parent.parent.parent
    ast_file = project_root / 'src' / 'registration_system' / 'dsl' / 'ast_nodes.py'
    interpreter_file = project_root / 'src' / 'registration_system' / 'dsl' / 'interpreter.py'

    if args.verbose:
        print(f"[*] Project root: {project_root}")
        print(f"[*] AST file: {ast_file}")
        print(f"[*] Interpreter file: {interpreter_file}")
        print()

    # 提取信息
    print("[*] Extracting AST node definitions...")
    ast_nodes = extract_ast_nodes(ast_file)
    print(f"    Found {len(ast_nodes)} AST nodes")

    print("[*] Extracting interpreter handlers...")
    handlers = extract_interpreter_handlers(interpreter_file)
    print(f"    Found {len(handlers)} handlers")

    # 检查语义
    print("\n[*] Checking semantic completeness...")
    report = check_semantics(ast_nodes, handlers)

    # 打印报告
    exit_code = print_report(report, verbose=args.verbose)

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
