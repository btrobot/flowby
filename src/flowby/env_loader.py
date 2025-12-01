"""
环境变量加载器 - v4.2.1

支持从多个位置加载 .env 文件，提供灵活的配置管理。

功能:
- 智能查找 .env 文件（脚本目录、项目根目录、当前目录）
- 支持多环境配置（.env.local, .env.production 等）
- 环境变量优先级管理
- 项目根目录自动识别

设计原则:
- 脚本所在目录优先（最直观）
- 项目根目录次之（标准做法）
- 系统环境变量最高优先级（不可覆盖）
"""

import os
from pathlib import Path
from typing import Optional, List


class EnvLoader:
    """
    环境变量加载器

    按优先级从多个位置查找并加载 .env 文件。

    查找顺序（优先级从低到高）：
    1. 当前工作目录的 .env
    2. 项目根目录的 .env
    3. 脚本所在目录的 .env
    4. DOTENV_PATH 环境变量指定的文件
    5. 系统环境变量（最高，不会被 .env 覆盖）
    """

    @staticmethod
    def load(script_path: Optional[str] = None, logger=None) -> Optional[Path]:
        """
        智能加载环境变量文件

        查找多个位置的 .env 文件并按优先级加载。

        Args:
            script_path: DSL 脚本文件路径（可选）
            logger: 日志记录器（可选）

        Returns:
            成功加载的主 .env 文件路径，如果未找到返回 None

        Examples:
            >>> EnvLoader.load("/path/to/script.flow")
            PosixPath('/path/to/.env')
        """
        try:
            from dotenv import load_dotenv
        except ImportError:
            if logger:
                logger.warning("python-dotenv 未安装，无法加载 .env 文件")
            return None

        candidates = EnvLoader._find_env_files(script_path)

        loaded_files = []

        # 按优先级加载（低优先级先加载，高优先级后加载会覆盖）
        for env_file in reversed(candidates):
            if env_file.exists():
                # override=False 确保系统环境变量不被覆盖
                load_dotenv(env_file, override=False)
                loaded_files.append(env_file)

                if logger:
                    logger.debug(f"✓ 加载环境变量文件: {env_file}")

        # 系统环境变量始终优先（不会被 .env 覆盖）
        if loaded_files:
            primary_file = loaded_files[-1]  # 最后加载的（优先级最高）
            if logger:
                logger.info(f"环境变量已加载（主文件: {primary_file.name}）")
            return primary_file
        else:
            if logger:
                logger.debug("未找到 .env 文件，使用系统环境变量")
            return None

    @staticmethod
    def _find_env_files(script_path: Optional[str] = None) -> List[Path]:
        """
        查找所有可能的 .env 文件位置

        Args:
            script_path: DSL 脚本文件路径（可选）

        Returns:
            按优先级排序的 .env 文件路径列表（优先级从低到高）
        """
        candidates = []

        # 1. 当前工作目录（最低优先级）
        cwd = Path.cwd()
        candidates.append(cwd / ".env")

        # 2. 项目根目录
        project_root = EnvLoader._find_project_root(script_path or str(cwd))
        if project_root and project_root != cwd:
            candidates.append(project_root / ".env")

        # 3. 脚本所在目录（如果提供了 script_path）
        if script_path:
            script_dir = Path(script_path).parent.resolve()
            if script_dir != cwd and script_dir != project_root:
                candidates.append(script_dir / ".env")

        # 4. DOTENV_PATH 环境变量指定的路径（最高优先级）
        dotenv_path = os.getenv("DOTENV_PATH")
        if dotenv_path:
            candidates.append(Path(dotenv_path))

        return candidates

    @staticmethod
    def _find_project_root(start_path: str) -> Optional[Path]:
        """
        向上查找项目根目录

        通过以下标志识别项目根目录：
        - pyproject.toml
        - setup.py
        - .git 目录
        - requirements.txt

        Args:
            start_path: 开始搜索的路径

        Returns:
            项目根目录路径，如果未找到返回 None

        Examples:
            >>> EnvLoader._find_project_root("/path/to/project/scripts")
            PosixPath('/path/to/project')
        """
        current = Path(start_path).resolve()

        # 如果 start_path 是文件，从其父目录开始
        if current.is_file():
            current = current.parent

        # 向上查找，最多查找 10 级
        for _ in range(10):
            # 检查是否存在项目标志文件
            markers = [
                current / "pyproject.toml",
                current / "setup.py",
                current / ".git",
                current / "requirements.txt",
            ]

            if any(marker.exists() for marker in markers):
                return current

            # 到达文件系统根目录
            if current.parent == current:
                break

            current = current.parent

        return None

    @staticmethod
    def load_with_environments(script_path: Optional[str] = None, logger=None) -> Optional[Path]:
        """
        加载环境变量，支持多环境配置

        加载顺序：
        1. .env（默认配置）
        2. .env.local（本地配置，覆盖 .env）
        3. .env.{ENV}（特定环境，如 .env.production）
        4. 系统环境变量（最高优先级，不会被覆盖）

        Args:
            script_path: DSL 脚本文件路径（可选）
            logger: 日志记录器（可选）

        Returns:
            主 .env 文件路径

        Examples:
            >>> # 设置环境
            >>> os.environ["ENV"] = "production"
            >>> EnvLoader.load_with_environments("/path/to/script.flow")
            # 加载：.env → .env.local → .env.production
        """
        try:
            from dotenv import load_dotenv
        except ImportError:
            if logger:
                logger.warning("python-dotenv 未安装，无法加载 .env 文件")
            return None

        # 1. 确定 .env 文件所在目录
        env_dir = EnvLoader._determine_env_directory(script_path)

        if logger:
            logger.debug(f"环境变量目录: {env_dir}")

        # 2. 加载 .env（基础配置）
        env_file = env_dir / ".env"
        if env_file.exists():
            load_dotenv(env_file, override=False)
            if logger:
                logger.debug(f"✓ 加载 .env: {env_file}")

        # 3. 加载 .env.local（本地配置）
        env_local = env_dir / ".env.local"
        if env_local.exists():
            load_dotenv(env_local, override=True)
            if logger:
                logger.debug(f"✓ 加载 .env.local: {env_local}")

        # 4. 加载特定环境配置
        env_type = os.getenv("ENV", os.getenv("NODE_ENV", "development"))
        env_specific = env_dir / f".env.{env_type}"
        if env_specific.exists():
            load_dotenv(env_specific, override=True)
            if logger:
                logger.info(f"✓ 加载环境配置 [{env_type}]: {env_specific}")

        # 5. 返回主配置文件路径
        return env_file if env_file.exists() else None

    @staticmethod
    def _determine_env_directory(script_path: Optional[str] = None) -> Path:
        """
        确定 .env 文件所在目录

        优先级：
        1. DOTENV_DIR 环境变量指定的目录
        2. 脚本所在目录
        3. 项目根目录
        4. 当前工作目录

        Args:
            script_path: DSL 脚本文件路径（可选）

        Returns:
            .env 文件所在目录
        """
        # 1. 环境变量指定
        dotenv_dir = os.getenv("DOTENV_DIR")
        if dotenv_dir:
            return Path(dotenv_dir)

        # 2. 脚本所在目录
        if script_path:
            return Path(script_path).parent.resolve()

        # 3. 项目根目录
        project_root = EnvLoader._find_project_root(str(Path.cwd()))
        if project_root:
            return project_root

        # 4. 当前工作目录
        return Path.cwd()
