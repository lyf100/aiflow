"""
AIFlow Prompt Template Validator
Prompt 模板格式验证器 - 验证模板文件格式和内容

核心功能:
1. 验证 YAML 格式
2. 验证 metadata 字段完整性
3. 验证 Jinja2 模板语法
4. 验证 input_schema 和 output_schema
5. 验证示例 (examples)
"""

import re
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from jinja2 import Environment, TemplateSyntaxError
except ImportError:
    raise ImportError("jinja2 is required. Install with: pip install jinja2")

try:
    from jsonschema import Draft7Validator, SchemaError
except ImportError:
    raise ImportError("jsonschema is required. Install with: pip install jsonschema")


class ValidationResult:
    """验证结果"""

    def __init__(self):
        self.is_valid: bool = True
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_error(self, message: str) -> None:
        """添加错误"""
        self.is_valid = False
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """添加警告"""
        self.warnings.append(message)

    def __str__(self) -> str:
        if self.is_valid:
            return f"✅ Validation passed ({len(self.warnings)} warnings)"
        return f"❌ Validation failed ({len(self.errors)} errors, {len(self.warnings)} warnings)"


class PromptTemplateValidator:
    """Prompt 模板验证器"""

    # 必需的 metadata 字段
    REQUIRED_METADATA_FIELDS = {
        "id", "version", "stage", "target_language", "created_at",
        "author", "description", "estimated_tokens"
    }

    # 有效的 stage 值
    VALID_STAGES = {
        "project_understanding",
        "structure_recognition",
        "semantic_analysis",
        "execution_inference",
        "concurrency_detection"
    }

    def __init__(self):
        self.jinja_env = Environment()

    def validate_file(self, file_path: Path) -> ValidationResult:
        """
        验证 Prompt 模板文件

        Args:
            file_path: 模板文件路径

        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult()

        # 1. 检查文件是否存在
        if not file_path.exists():
            result.add_error(f"File not found: {file_path}")
            return result

        # 2. 验证 YAML 格式
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                template_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            result.add_error(f"Invalid YAML format: {e}")
            return result

        if not isinstance(template_data, dict):
            result.add_error("Template data must be a dictionary")
            return result

        # 3. 验证 metadata
        self._validate_metadata(template_data, result)

        # 4. 验证 template 字段
        self._validate_template(template_data, result)

        # 5. 验证 input_schema
        self._validate_input_schema(template_data, result)

        # 6. 验证 output_schema
        self._validate_output_schema(template_data, result)

        # 7. 验证 examples (可选)
        if "examples" in template_data:
            self._validate_examples(template_data, result)

        return result

    def _validate_metadata(
        self,
        template_data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """验证 metadata 字段"""
        if "metadata" not in template_data:
            result.add_error("Missing 'metadata' field")
            return

        metadata = template_data["metadata"]
        if not isinstance(metadata, dict):
            result.add_error("'metadata' must be a dictionary")
            return

        # 检查必需字段
        missing_fields = self.REQUIRED_METADATA_FIELDS - set(metadata.keys())
        if missing_fields:
            result.add_error(f"Missing required metadata fields: {', '.join(missing_fields)}")

        # 验证 version 格式 (语义化版本)
        if "version" in metadata:
            version = metadata["version"]
            if not re.match(r"^\d+\.\d+\.\d+$", version):
                result.add_error(f"Invalid version format: {version} (expected: X.Y.Z)")

        # 验证 stage
        if "stage" in metadata:
            stage = metadata["stage"]
            if stage not in self.VALID_STAGES:
                result.add_error(f"Invalid stage: {stage} (expected one of: {', '.join(self.VALID_STAGES)})")

        # 验证 estimated_tokens
        if "estimated_tokens" in metadata:
            tokens = metadata["estimated_tokens"]
            if not isinstance(tokens, int) or tokens <= 0:
                result.add_error(f"Invalid estimated_tokens: {tokens} (must be positive integer)")

        # 验证 created_at 格式 (YYYY-MM-DD)
        if "created_at" in metadata:
            created_at = metadata["created_at"]
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", created_at):
                result.add_warning(f"created_at format should be YYYY-MM-DD: {created_at}")

    def _validate_template(
        self,
        template_data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """验证 template 字段和 Jinja2 语法"""
        if "template" not in template_data:
            result.add_error("Missing 'template' field")
            return

        template_str = template_data["template"]
        if not isinstance(template_str, str):
            result.add_error("'template' must be a string")
            return

        if len(template_str.strip()) == 0:
            result.add_error("'template' cannot be empty")
            return

        # 验证 Jinja2 语法
        try:
            self.jinja_env.parse(template_str)
        except TemplateSyntaxError as e:
            result.add_error(f"Jinja2 template syntax error: {e}")

    def _validate_input_schema(
        self,
        template_data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """验证 input_schema"""
        if "input_schema" not in template_data:
            result.add_warning("Missing 'input_schema' field")
            return

        input_schema = template_data["input_schema"]
        if not isinstance(input_schema, dict):
            result.add_error("'input_schema' must be a dictionary")
            return

        # 验证 JSON Schema 格式
        try:
            Draft7Validator.check_schema(input_schema)
        except SchemaError as e:
            result.add_error(f"Invalid input_schema JSON Schema: {e}")

        # 检查是否定义了 required 字段
        if "required" not in input_schema:
            result.add_warning("input_schema should define 'required' fields")

    def _validate_output_schema(
        self,
        template_data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """验证 output_schema"""
        if "output_schema" not in template_data:
            result.add_warning("Missing 'output_schema' field")
            return

        output_schema = template_data["output_schema"]
        if not isinstance(output_schema, dict):
            result.add_error("'output_schema' must be a dictionary")
            return

        # 检查是否为 $ref 引用
        if "$ref" in output_schema:
            ref = output_schema["$ref"]
            if not isinstance(ref, str):
                result.add_error("output_schema.$ref must be a string")
            elif not ref.startswith("https://aiflow.dev/schemas/"):
                result.add_warning(f"output_schema.$ref should reference aiflow.dev schemas: {ref}")
        else:
            # 验证 JSON Schema 格式
            try:
                Draft7Validator.check_schema(output_schema)
            except SchemaError as e:
                result.add_error(f"Invalid output_schema JSON Schema: {e}")

    def _validate_examples(
        self,
        template_data: Dict[str, Any],
        result: ValidationResult
    ) -> None:
        """验证 examples 字段"""
        examples = template_data["examples"]
        if not isinstance(examples, list):
            result.add_error("'examples' must be a list")
            return

        for idx, example in enumerate(examples):
            if not isinstance(example, dict):
                result.add_error(f"examples[{idx}] must be a dictionary")
                continue

            # 检查 name 字段
            if "name" not in example:
                result.add_warning(f"examples[{idx}] missing 'name' field")

            # 检查示例内容
            if "input_summary" not in example and "input" not in example:
                result.add_warning(f"examples[{idx}] should have 'input' or 'input_summary'")

            if "expected_output_summary" not in example and "expected_output" not in example:
                result.add_warning(f"examples[{idx}] should have 'expected_output' or 'expected_output_summary'")


def validate_prompt_template(file_path: Path) -> ValidationResult:
    """
    便捷函数：验证 Prompt 模板文件

    Args:
        file_path: 模板文件路径

    Returns:
        ValidationResult: 验证结果
    """
    validator = PromptTemplateValidator()
    return validator.validate_file(file_path)


# CLI 入口（用于测试）
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python validator.py <template.yaml> [template2.yaml ...]")
        sys.exit(1)

    validator = PromptTemplateValidator()
    all_valid = True

    for template_file in sys.argv[1:]:
        file_path = Path(template_file)
        print(f"\nValidating: {file_path}")
        print("=" * 60)

        result = validator.validate_file(file_path)
        print(result)

        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  ❌ {error}")

        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  ⚠️  {warning}")

        if not result.is_valid:
            all_valid = False

    sys.exit(0 if all_valid else 1)
