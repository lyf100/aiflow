"""
AIFlow Protocol Serializer
分析结果序列化/反序列化模块

核心功能:
1. 序列化分析结果为 JSON 文件
2. 反序列化 JSON 文件为 Python 数据结构
3. 支持 gzip 压缩 (可选)
4. 序列化前自动验证
5. 支持增量更新 (部分数据)
"""

import gzip
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .validator import ProtocolValidator, ValidationResult, validate_analysis_result


class SerializationError(Exception):
    """序列化错误"""
    pass


class DeserializationError(Exception):
    """反序列化错误"""
    pass


class ProtocolSerializer:
    """协议序列化器"""

    def __init__(
        self,
        validate_on_serialize: bool = True,
        schema_path: Optional[Path] = None
    ):
        """
        初始化序列化器

        Args:
            validate_on_serialize: 序列化前是否自动验证 (默认 True)
            schema_path: JSON Schema 文件路径 (可选)
        """
        self.validate_on_serialize = validate_on_serialize
        self.validator = ProtocolValidator(schema_path) if validate_on_serialize else None

    def serialize(
        self,
        data: Dict[str, Any],
        output_path: Union[str, Path],
        compress: bool = False,
        indent: Optional[int] = 2,
        validate: Optional[bool] = None
    ) -> ValidationResult:
        """
        序列化分析结果到文件

        Args:
            data: 分析结果数据
            output_path: 输出文件路径
            compress: 是否 gzip 压缩 (默认 False)
            indent: JSON 缩进 (None 为紧凑格式, 默认 2)
            validate: 是否验证 (None 时使用初始化参数)

        Returns:
            ValidationResult: 验证结果 (如果启用验证)

        Raises:
            SerializationError: 序列化失败
        """
        output_path = Path(output_path)

        # 验证
        validation_result = ValidationResult()
        if validate is None:
            validate = self.validate_on_serialize

        if validate:
            validation_result = self.validator.validate_complete(data)
            if not validation_result.is_valid:
                raise SerializationError(
                    f"Validation failed with {len(validation_result.errors)} errors"
                )

        # 序列化
        try:
            json_str = json.dumps(data, indent=indent, ensure_ascii=False)

            # 写入文件
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if compress:
                # gzip 压缩
                with gzip.open(output_path, "wt", encoding="utf-8") as f:
                    f.write(json_str)
            else:
                # 直接写入
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(json_str)

        except Exception as e:
            raise SerializationError(f"Failed to serialize data: {e}") from e

        return validation_result

    def deserialize(
        self,
        input_path: Union[str, Path],
        validate: bool = False
    ) -> Dict[str, Any]:
        """
        反序列化 JSON 文件

        Args:
            input_path: 输入文件路径
            validate: 是否验证反序列化后的数据 (默认 False)

        Returns:
            Dict[str, Any]: 分析结果数据

        Raises:
            DeserializationError: 反序列化失败
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise DeserializationError(f"File not found: {input_path}")

        try:
            # 尝试 gzip 解压
            try:
                with gzip.open(input_path, "rt", encoding="utf-8") as f:
                    data = json.load(f)
            except (gzip.BadGzipFile, OSError):
                # 不是 gzip 文件，直接读取
                with open(input_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

        except json.JSONDecodeError as e:
            raise DeserializationError(f"Invalid JSON format: {e}") from e
        except Exception as e:
            raise DeserializationError(f"Failed to deserialize data: {e}") from e

        # 验证
        if validate:
            validation_result = validate_analysis_result(data)
            if not validation_result.is_valid:
                raise DeserializationError(
                    f"Validation failed with {len(validation_result.errors)} errors:\n" +
                    "\n".join(validation_result.errors)
                )

        return data

    def update_partial(
        self,
        file_path: Union[str, Path],
        updates: Dict[str, Any],
        validate: bool = True
    ) -> ValidationResult:
        """
        增量更新：读取 → 更新部分数据 → 验证 → 写回

        Args:
            file_path: 文件路径
            updates: 要更新的字段 (支持嵌套字典)
            validate: 是否验证更新后的数据 (默认 True)

        Returns:
            ValidationResult: 验证结果

        Example:
            serializer.update_partial(
                "analysis.json",
                {
                    "project_metadata": {"total_lines": 5000},
                    "concurrency_info": {"flows": [...]}
                }
            )
        """
        file_path = Path(file_path)

        # 读取现有数据
        existing_data = self.deserialize(file_path, validate=False)

        # 递归更新
        def deep_update(base: Dict, updates: Dict) -> None:
            for key, value in updates.items():
                if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                    deep_update(base[key], value)
                else:
                    base[key] = value

        deep_update(existing_data, updates)

        # 写回
        return self.serialize(
            existing_data,
            file_path,
            compress=str(file_path).endswith(".gz"),
            validate=validate
        )


# 便捷函数

def serialize_to_file(
    data: Dict[str, Any],
    output_path: Union[str, Path],
    compress: bool = False,
    validate: bool = True
) -> ValidationResult:
    """
    便捷函数：序列化分析结果到文件

    Args:
        data: 分析结果数据
        output_path: 输出文件路径
        compress: 是否 gzip 压缩 (默认 False)
        validate: 是否验证 (默认 True)

    Returns:
        ValidationResult: 验证结果
    """
    serializer = ProtocolSerializer(validate_on_serialize=validate)
    return serializer.serialize(data, output_path, compress=compress)


def deserialize_from_file(
    input_path: Union[str, Path],
    validate: bool = False
) -> Dict[str, Any]:
    """
    便捷函数：反序列化 JSON 文件

    Args:
        input_path: 输入文件路径
        validate: 是否验证 (默认 False)

    Returns:
        Dict[str, Any]: 分析结果数据
    """
    serializer = ProtocolSerializer(validate_on_serialize=False)
    return serializer.deserialize(input_path, validate=validate)


# CLI 入口（用于测试）
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage:")
        print("  Validate and compress:   python serializer.py validate <input.json> <output.json.gz>")
        print("  Decompress and validate: python serializer.py validate <input.json.gz> <output.json>")
        print("  Simple copy:             python serializer.py copy <input.json> <output.json>")
        sys.exit(1)

    command = sys.argv[1]
    input_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    if command == "validate":
        # 读取 → 验证 → 写入
        data = deserialize_from_file(input_file, validate=False)
        if output_file:
            compress = str(output_file).endswith(".gz")
            result = serialize_to_file(data, output_file, compress=compress, validate=True)
            print(result)
            if result.is_valid:
                print(f"✅ Serialized to {output_file}")
            else:
                print("❌ Validation failed")
                for error in result.errors:
                    print(f"  - {error}")
        else:
            # 只验证
            result = validate_analysis_result(data)
            print(result)
            if not result.is_valid:
                for error in result.errors:
                    print(f"  - {error}")

    elif command == "copy":
        # 简单复制（不验证）
        data = deserialize_from_file(input_file, validate=False)
        if output_file:
            serializer = ProtocolSerializer(validate_on_serialize=False)
            serializer.serialize(data, output_file, compress=str(output_file).endswith(".gz"))
            print(f"✅ Copied to {output_file}")
        else:
            print("Error: Output file required for copy command")
            sys.exit(1)

    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)
