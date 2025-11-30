"""
Mock Handler - v4.2 Phase 5

Mock 模式支持，用于测试环境。

功能:
- 静态 Mock 响应
- 动态 Mock 响应
- 文件加载 Mock
- 延迟模拟
- 错误模拟
- 调用记录
"""

import time
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from collections import defaultdict


class MockRecorder:
    """Mock 调用记录器"""

    def __init__(self):
        """初始化记录器"""
        self.calls = defaultdict(list)  # operation_id -> [calls]
        self.total_calls = 0

    def record(
        self,
        operation_id: str,
        kwargs: Dict[str, Any],
        response: Any
    ) -> None:
        """
        记录 Mock 调用

        Args:
            operation_id: 操作 ID
            kwargs: 调用参数
            response: Mock 响应
        """
        self.calls[operation_id].append({
            'timestamp': time.time(),
            'kwargs': kwargs,
            'response': response
        })
        self.total_calls += 1

    def get_calls(self, operation_id: str) -> List[Dict]:
        """
        获取指定操作的调用记录

        Args:
            operation_id: 操作 ID

        Returns:
            调用记录列表
        """
        return self.calls.get(operation_id, [])

    def get_call_count(self, operation_id: str) -> int:
        """
        获取指定操作的调用次数

        Args:
            operation_id: 操作 ID

        Returns:
            调用次数
        """
        return len(self.calls.get(operation_id, []))

    def get_last_call(self, operation_id: str) -> Optional[Dict]:
        """
        获取指定操作的最后一次调用

        Args:
            operation_id: 操作 ID

        Returns:
            最后一次调用记录，如果没有则返回 None
        """
        calls = self.calls.get(operation_id, [])
        return calls[-1] if calls else None

    def reset(self, operation_id: Optional[str] = None) -> None:
        """
        重置调用记录

        Args:
            operation_id: 操作 ID，如果为 None 则重置所有记录
        """
        if operation_id:
            self.calls[operation_id] = []
        else:
            self.calls.clear()
            self.total_calls = 0

    def get_all_calls(self) -> Dict[str, List[Dict]]:
        """获取所有调用记录"""
        return dict(self.calls)


class MockDataLoader:
    """Mock 数据加载器"""

    @staticmethod
    def load_from_file(file_path: str) -> Any:
        """
        从文件加载 Mock 数据

        Args:
            file_path: 文件路径

        Returns:
            加载的数据

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 不支持的文件格式
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Mock 数据文件不存在: {file_path}")

        # 根据文件扩展名选择加载器
        suffix = path.suffix.lower()

        if suffix == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif suffix in ['.yaml', '.yml']:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            raise ValueError(f"不支持的 Mock 数据文件格式: {suffix}")

    @staticmethod
    def apply_template(data: Any, variables: Dict[str, Any]) -> Any:
        """
        应用模板变量替换

        Args:
            data: 数据（支持字典、列表、字符串）
            variables: 变量字典

        Returns:
            替换后的数据
        """
        if isinstance(data, str):
            # 字符串模板替换
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                data = data.replace(placeholder, str(value))
            return data
        elif isinstance(data, dict):
            # 递归处理字典
            return {
                k: MockDataLoader.apply_template(v, variables)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            # 递归处理列表
            return [
                MockDataLoader.apply_template(item, variables)
                for item in data
            ]
        else:
            return data


class MockHandler:
    """
    Mock 处理器

    管理 Mock 配置和响应生成。
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 Mock 处理器

        Args:
            config: Mock 配置

        配置示例:
            {
                "enabled": True,
                "mode": "auto",  # auto, static, file
                "delay": 0.1,    # 模拟延迟（秒）
                "responses": {
                    "getUser": {
                        "status": 200,
                        "data": {"id": 1, "name": "Mock User"}
                    },
                    "createUser": {
                        "file": "mocks/create_user.json",
                        "status": 201
                    }
                },
                "errors": {
                    "getUser": {
                        "status": 404,
                        "message": "User not found"
                    }
                },
                "record_calls": True,
                "base_path": "mocks/"  # mock 文件基础路径
            }
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', False)
        self.mode = self.config.get('mode', 'auto')
        self.delay = self.config.get('delay', 0)
        self.responses = self.config.get('responses', {})
        self.errors = self.config.get('errors', {})
        self.record_calls = self.config.get('record_calls', False)
        self.base_path = self.config.get('base_path', '')

        # 调用记录器
        self.recorder = MockRecorder() if self.record_calls else None

    def is_enabled(self) -> bool:
        """检查 Mock 是否启用"""
        return self.enabled

    def has_mock(self, operation_id: str) -> bool:
        """
        检查指定操作是否有 Mock 配置

        Args:
            operation_id: 操作 ID

        Returns:
            是否有 Mock 配置
        """
        return operation_id in self.responses or operation_id in self.errors

    def get_mock_response(
        self,
        operation_id: str,
        kwargs: Dict[str, Any],
        logger: Optional[Any] = None
    ) -> Any:
        """
        获取 Mock 响应

        Args:
            operation_id: 操作 ID
            kwargs: 调用参数
            logger: 日志记录器

        Returns:
            Mock 响应数据

        Raises:
            ValueError: 没有 Mock 配置
        """
        # 模拟延迟
        if self.delay > 0:
            time.sleep(self.delay)

        # 优先检查是否有错误模拟
        if operation_id in self.errors:
            error_config = self.errors[operation_id]
            if logger:
                logger.warning(
                    f"[MOCK] Simulating error for {operation_id}: "
                    f"status={error_config.get('status', 500)}"
                )
            return self._build_error_response(error_config)

        # 获取正常响应
        if operation_id in self.responses:
            response_config = self.responses[operation_id]
            if logger:
                logger.info(f"[MOCK] Returning mock response for {operation_id}")
            return self._build_success_response(response_config, kwargs)

        raise ValueError(f"没有找到操作的 Mock 配置: {operation_id}")

    def _build_success_response(
        self,
        config: Dict[str, Any],
        kwargs: Dict[str, Any]
    ) -> Any:
        """
        构建成功响应

        Args:
            config: 响应配置
            kwargs: 调用参数

        Returns:
            Mock 响应数据
        """
        # 如果配置了文件，从文件加载
        if 'file' in config:
            file_path = config['file']
            # 如果是相对路径，加上基础路径
            if self.base_path and not Path(file_path).is_absolute():
                file_path = str(Path(self.base_path) / file_path)

            data = MockDataLoader.load_from_file(file_path)

            # 应用模板变量替换
            if kwargs:
                data = MockDataLoader.apply_template(data, kwargs)

            return data

        # 如果配置了 data，直接返回
        if 'data' in config:
            data = config['data']

            # 如果 data 是函数，调用它
            if callable(data):
                return data(**kwargs)

            # 应用模板变量替换
            if kwargs and isinstance(data, (dict, list, str)):
                data = MockDataLoader.apply_template(data, kwargs)

            return data

        # 如果配置了 factory，调用工厂函数
        if 'factory' in config:
            factory = config['factory']
            if callable(factory):
                return factory(**kwargs)

        # 默认返回空响应
        return {}

    def _build_error_response(self, config: Dict[str, Any]) -> Any:
        """
        构建错误响应

        Args:
            config: 错误配置

        Returns:
            错误响应数据（实际上会抛出异常）

        Raises:
            HTTPError: 模拟的 HTTP 错误
        """
        from requests.exceptions import HTTPError
        from requests.models import Response

        # 创建一个模拟的 Response 对象
        response = Response()
        response.status_code = config.get('status', 500)
        response._content = json.dumps({
            'error': config.get('message', 'Mock error'),
            'detail': config.get('detail', '')
        }).encode('utf-8')

        # 抛出 HTTPError
        raise HTTPError(response=response)

    def record_call(
        self,
        operation_id: str,
        kwargs: Dict[str, Any],
        response: Any
    ) -> None:
        """
        记录调用

        Args:
            operation_id: 操作 ID
            kwargs: 调用参数
            response: 响应数据
        """
        if self.recorder:
            self.recorder.record(operation_id, kwargs, response)

    def get_recorder(self) -> Optional[MockRecorder]:
        """获取调用记录器"""
        return self.recorder


def create_mock_handler(
    config: Optional[Dict[str, Any]] = None
) -> Optional[MockHandler]:
    """
    创建 Mock 处理器（工厂函数）

    Args:
        config: Mock 配置

    Returns:
        MockHandler 实例，如果配置为空或未启用则返回 None
    """
    if not config:
        return None

    if not config.get('enabled', False):
        return None

    return MockHandler(config)
