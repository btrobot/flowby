#!/usr/bin/env python3
"""
v2.0 to v3.0 语法迁移工具

自动将 v2.0 语法（使用 end 关键字）转换为 v3.0 语法（纯缩进）

使用方法：
    python tools/migrate_v2_to_v3.py <file.flow>
    python tools/migrate_v2_to_v3.py --all  # 转换所有示例文件
"""

import re
import sys
from pathlib import Path
from typing import List


def migrate_file_content(content: str) -> str:
    """
    转换文件内容从 v2.0 到 v3.0

    主要变更：
    1. 移除 end if/step/for/while/when/function
    2. 替换 false/true/null 为 False/True/None
    3. 替换 $context 为 context (移除 $)
    4. 保持缩进结构不变
    """
    lines = content.split('\n')
    result_lines = []

    for line in lines:
        # 检查是否是 end 语句（忽略行内注释后的 end）
        stripped = line.lstrip()

        # 如果整行就是 end 关键字（可能带缩进），跳过
        if re.match(r'^(end\s+(if|step|for|while|when|function))(\s*#.*)?$', stripped):
            continue

        # v3.0 语法修复：布尔值和空值
        # false -> False, true -> True, null -> None
        # 但要避免在字符串中替换
        line = re.sub(r'\bfalse\b', 'False', line)
        line = re.sub(r'\btrue\b', 'True', line)
        line = re.sub(r'\bnull\b', 'None', line)

        # 移除 $ 前缀（系统变量）
        # $context -> context, $page -> page, $env -> env
        line = re.sub(r'\$context\b', 'context', line)
        line = re.sub(r'\$page\b', 'page', line)
        line = re.sub(r'\$env\b', 'env', line)

        # 否则保留这行
        result_lines.append(line)

    return '\n'.join(result_lines)


def migrate_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    迁移单个文件

    Args:
        file_path: 文件路径
        dry_run: 只检查不修改

    Returns:
        是否有变更
    """
    if not file_path.exists():
        print(f"[ERROR] File not found: {file_path}")
        return False

    # 读取原始内容
    original_content = file_path.read_text(encoding='utf-8')

    # 检查是否包含 v2.0 语法
    has_v2_syntax = (
        bool(re.search(r'\bend\s+(if|step|for|while|when|function)\b', original_content)) or
        bool(re.search(r'\b(false|true|null)\b', original_content)) or
        bool(re.search(r'\$context|\$page|\$env', original_content))
    )

    if not has_v2_syntax:
        print(f"[SKIP] Already v3.0: {file_path}")
        return False

    # 转换内容
    migrated_content = migrate_file_content(original_content)

    if dry_run:
        print(f"[CHECK] Need migration: {file_path}")
        # 显示变更统计
        removed_lines = original_content.count('\n') - migrated_content.count('\n')
        print(f"   Will remove {removed_lines} end statements")
        return True

    # 写回文件
    file_path.write_text(migrated_content, encoding='utf-8')
    print(f"[OK] Migrated: {file_path}")

    # 显示变更统计
    removed_lines = original_content.count('\n') - migrated_content.count('\n')
    print(f"   Removed {removed_lines} end statements")

    return True


def find_v2_files(directory: Path) -> List[Path]:
    """查找所有使用 v2.0 语法的 .flow 文件"""
    v2_files = []

    for flow_file in directory.rglob('*.flow'):
        content = flow_file.read_text(encoding='utf-8')
        if re.search(r'\bend\s+(if|step|for|while|when|function)\b', content):
            v2_files.append(flow_file)

    return v2_files


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    examples_dir = project_root / 'examples'

    if sys.argv[1] == '--all':
        # 批量转换
        print("[SCAN] Scanning examples/ directory...")
        v2_files = find_v2_files(examples_dir)

        if not v2_files:
            print("[OK] All files are already v3.0 syntax")
            return

        print(f"\nFound {len(v2_files)} files to migrate:")
        for f in v2_files:
            print(f"  - {f.relative_to(project_root)}")

        # 询问确认
        response = input("\nConfirm migration? [y/N] ")
        if response.lower() != 'y':
            print("Migration cancelled")
            return

        # 执行迁移
        print("\nStarting migration...")
        success_count = 0
        for file_path in v2_files:
            if migrate_file(file_path):
                success_count += 1

        print(f"\n[SUCCESS] Migrated {success_count}/{len(v2_files)} files")

    elif sys.argv[1] == '--dry-run':
        # 只检查不修改
        print("[DRY-RUN] Check only, no modifications")
        v2_files = find_v2_files(examples_dir)

        if not v2_files:
            print("[OK] All files are already v3.0 syntax")
            return

        print(f"\nNeed to migrate {len(v2_files)} files:")
        for file_path in v2_files:
            migrate_file(file_path, dry_run=True)

    else:
        # 单个文件迁移
        file_path = Path(sys.argv[1])
        migrate_file(file_path)


if __name__ == '__main__':
    main()
