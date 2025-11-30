"""
Response Handler - v4.2 Phase 3

响应数据映射和验证处理器。

功能:
- 根据 OpenAPI schema 验证响应数据
- 自动类型转换和格式化
- 字段映射和重命名
- 嵌套对象和数组处理
- 数据验证（类型、必填、格式、范围）
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import re


class ValidationError(Exception):
    """验证错误"""

    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"字段 '{field}' 验证失败: {message}")


class ResponseValidator:
    """
    响应数据验证器

    根据 OpenAPI schema 定义验证响应数据的合法性。
    """

    @staticmethod
    def validate(data: Any, schema: Dict[str, Any], field_path: str = "root") -> None:
        """
        验证数据是否符合 schema 定义

        Args:
            data: 要验证的数据
            schema: OpenAPI schema 定义
            field_path: 字段路径（用于错误提示）

        Raises:
            ValidationError: 验证失败时抛出
        """
        if not schema:
            return

        schema_type = schema.get('type')

        # 处理 nullable
        if data is None:
            if schema.get('nullable', False):
                return
            raise ValidationError(field_path, "不能为 null", data)

        # 类型验证
        if schema_type == 'object':
            ResponseValidator._validate_object(data, schema, field_path)
        elif schema_type == 'array':
            ResponseValidator._validate_array(data, schema, field_path)
        elif schema_type == 'string':
            ResponseValidator._validate_string(data, schema, field_path)
        elif schema_type == 'integer':
            ResponseValidator._validate_integer(data, schema, field_path)
        elif schema_type == 'number':
            ResponseValidator._validate_number(data, schema, field_path)
        elif schema_type == 'boolean':
            ResponseValidator._validate_boolean(data, schema, field_path)

    @staticmethod
    def _validate_object(data: Any, schema: Dict[str, Any], field_path: str) -> None:
        """验证对象类型"""
        if not isinstance(data, dict):
            raise ValidationError(field_path, f"期望类型为 object，实际为 {type(data).__name__}", data)

        properties = schema.get('properties', {})
        required = schema.get('required', [])

        # 验证必填字段
        for field_name in required:
            if field_name not in data:
                raise ValidationError(f"{field_path}.{field_name}", "必填字段缺失")

        # 验证每个字段
        for field_name, field_value in data.items():
            if field_name in properties:
                field_schema = properties[field_name]
                ResponseValidator.validate(
                    field_value,
                    field_schema,
                    f"{field_path}.{field_name}"
                )

    @staticmethod
    def _validate_array(data: Any, schema: Dict[str, Any], field_path: str) -> None:
        """验证数组类型"""
        if not isinstance(data, list):
            raise ValidationError(field_path, f"期望类型为 array，实际为 {type(data).__name__}", data)

        # 验证数组长度
        min_items = schema.get('minItems')
        max_items = schema.get('maxItems')

        if min_items is not None and len(data) < min_items:
            raise ValidationError(field_path, f"数组长度不能少于 {min_items}，当前为 {len(data)}", data)

        if max_items is not None and len(data) > max_items:
            raise ValidationError(field_path, f"数组长度不能超过 {max_items}，当前为 {len(data)}", data)

        # 验证数组元素
        items_schema = schema.get('items')
        if items_schema:
            for i, item in enumerate(data):
                ResponseValidator.validate(
                    item,
                    items_schema,
                    f"{field_path}[{i}]"
                )

    @staticmethod
    def _validate_string(data: Any, schema: Dict[str, Any], field_path: str) -> None:
        """验证字符串类型"""
        if not isinstance(data, str):
            raise ValidationError(field_path, f"期望类型为 string，实际为 {type(data).__name__}", data)

        # 长度验证
        min_length = schema.get('minLength')
        max_length = schema.get('maxLength')

        if min_length is not None and len(data) < min_length:
            raise ValidationError(field_path, f"字符串长度不能少于 {min_length}，当前为 {len(data)}", data)

        if max_length is not None and len(data) > max_length:
            raise ValidationError(field_path, f"字符串长度不能超过 {max_length}，当前为 {len(data)}", data)

        # 格式验证
        format_type = schema.get('format')
        if format_type:
            ResponseValidator._validate_string_format(data, format_type, field_path)

        # 模式验证
        pattern = schema.get('pattern')
        if pattern and not re.match(pattern, data):
            raise ValidationError(field_path, f"不符合正则表达式: {pattern}", data)

        # 枚举验证
        enum = schema.get('enum')
        if enum and data not in enum:
            raise ValidationError(field_path, f"必须是以下值之一: {enum}，当前为 {data}", data)

    @staticmethod
    def _validate_string_format(data: str, format_type: str, field_path: str) -> None:
        """验证字符串格式"""
        if format_type == 'email':
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data):
                raise ValidationError(field_path, f"不是有效的 email 格式", data)

        elif format_type == 'uri' or format_type == 'url':
            url_pattern = r'^https?://.+'
            if not re.match(url_pattern, data):
                raise ValidationError(field_path, f"不是有效的 URL 格式", data)

        elif format_type == 'date':
            # ISO 8601 date: YYYY-MM-DD
            date_pattern = r'^\d{4}-\d{2}-\d{2}$'
            if not re.match(date_pattern, data):
                raise ValidationError(field_path, f"不是有效的日期格式 (YYYY-MM-DD)", data)

        elif format_type == 'date-time':
            # ISO 8601 datetime
            try:
                datetime.fromisoformat(data.replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError(field_path, f"不是有效的日期时间格式 (ISO 8601)", data)

    @staticmethod
    def _validate_integer(data: Any, schema: Dict[str, Any], field_path: str) -> None:
        """验证整数类型"""
        if not isinstance(data, int) or isinstance(data, bool):
            raise ValidationError(field_path, f"期望类型为 integer，实际为 {type(data).__name__}", data)

        # 范围验证
        minimum = schema.get('minimum')
        maximum = schema.get('maximum')

        if minimum is not None and data < minimum:
            raise ValidationError(field_path, f"不能小于 {minimum}，当前为 {data}", data)

        if maximum is not None and data > maximum:
            raise ValidationError(field_path, f"不能大于 {maximum}，当前为 {data}", data)

    @staticmethod
    def _validate_number(data: Any, schema: Dict[str, Any], field_path: str) -> None:
        """验证数字类型（包括整数和浮点数）"""
        if not isinstance(data, (int, float)) or isinstance(data, bool):
            raise ValidationError(field_path, f"期望类型为 number，实际为 {type(data).__name__}", data)

        # 范围验证
        minimum = schema.get('minimum')
        maximum = schema.get('maximum')

        if minimum is not None and data < minimum:
            raise ValidationError(field_path, f"不能小于 {minimum}，当前为 {data}", data)

        if maximum is not None and data > maximum:
            raise ValidationError(field_path, f"不能大于 {maximum}，当前为 {data}", data)

    @staticmethod
    def _validate_boolean(data: Any, schema: Dict[str, Any], field_path: str) -> None:
        """验证布尔类型"""
        if not isinstance(data, bool):
            raise ValidationError(field_path, f"期望类型为 boolean，实际为 {type(data).__name__}", data)


class ResponseMapper:
    """
    响应数据映射器

    将 API 响应数据映射为结构化对象，支持字段重命名和类型转换。
    """

    def __init__(self, mapping_config: Optional[Dict[str, Any]] = None):
        """
        初始化响应映射器

        Args:
            mapping_config: 映射配置字典

        映射配置示例:
            {
                "field_mapping": {
                    "userId": "user_id",        # 重命名字段
                    "createdAt": "created_at"
                },
                "exclude_fields": ["internal_field"],  # 排除字段
                "include_only": ["id", "name"],        # 仅包含指定字段
                "default_values": {                    # 默认值
                    "status": "active"
                }
            }
        """
        self.mapping_config = mapping_config or {}
        self.field_mapping = self.mapping_config.get('field_mapping', {})
        self.exclude_fields = set(self.mapping_config.get('exclude_fields', []))
        self.include_only = self.mapping_config.get('include_only')
        self.default_values = self.mapping_config.get('default_values', {})

    def map(self, data: Any) -> Any:
        """
        映射响应数据

        Args:
            data: 原始响应数据

        Returns:
            映射后的数据
        """
        if isinstance(data, dict):
            return self._map_object(data)
        elif isinstance(data, list):
            return [self.map(item) for item in data]
        else:
            return data

    def _map_object(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """映射对象"""
        result = {}

        # 应用默认值
        for key, value in self.default_values.items():
            if key not in data:
                result[key] = value

        # 映射字段
        for key, value in data.items():
            # 检查是否排除
            if key in self.exclude_fields:
                continue

            # 检查是否仅包含特定字段
            if self.include_only and key not in self.include_only:
                continue

            # 字段重命名
            mapped_key = self.field_mapping.get(key, key)

            # 递归映射嵌套对象
            if isinstance(value, dict):
                result[mapped_key] = self._map_object(value)
            elif isinstance(value, list):
                result[mapped_key] = [
                    self._map_object(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[mapped_key] = value

        return result


class ResponseHandler:
    """
    响应处理器

    整合验证和映射功能，处理 API 响应。
    """

    def __init__(
        self,
        response_schema: Optional[Dict[str, Any]] = None,
        mapping_config: Optional[Dict[str, Any]] = None,
        validate: bool = True
    ):
        """
        初始化响应处理器

        Args:
            response_schema: OpenAPI response schema
            mapping_config: 映射配置
            validate: 是否启用验证（默认 True）
        """
        self.response_schema = response_schema
        self.mapping_config = mapping_config
        self.validate_enabled = validate
        self.mapper = ResponseMapper(mapping_config) if mapping_config else None

    def process(self, data: Any) -> Any:
        """
        处理响应数据

        Args:
            data: 原始响应数据

        Returns:
            处理后的数据

        Raises:
            ValidationError: 验证失败时抛出
        """
        # 1. 数据验证
        if self.validate_enabled and self.response_schema:
            ResponseValidator.validate(data, self.response_schema)

        # 2. 数据映射
        if self.mapper:
            data = self.mapper.map(data)

        return data


def create_response_handler(
    operation: Dict[str, Any],
    mapping_config: Optional[Dict[str, Any]] = None,
    validate: bool = True
) -> Optional[ResponseHandler]:
    """
    根据 OpenAPI 操作定义创建响应处理器

    Args:
        operation: OpenAPI 操作定义
        mapping_config: 映射配置
        validate: 是否启用验证

    Returns:
        ResponseHandler 实例，如果没有响应定义则返回 None
    """
    # 从操作中提取 200 响应的 schema
    responses = operation.get('responses', {})
    success_response = responses.get('200') or responses.get('201')

    if not success_response:
        return None

    # 提取 schema
    content = success_response.get('content', {})
    json_content = content.get('application/json', {})
    schema = json_content.get('schema')

    if not schema:
        return None

    return ResponseHandler(
        response_schema=schema,
        mapping_config=mapping_config,
        validate=validate
    )
