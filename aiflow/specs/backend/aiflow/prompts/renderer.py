"""
AIFlow Prompt Template Renderer
Jinja2 模板渲染器 - 渲染 Prompt 模板

核心功能:
1. 加载 Prompt 模板
2. 使用 Jinja2 渲染模板
3. 验证输入参数（基于 input_schema）
4. 处理模板变量和过滤器
5. 返回渲染后的文本
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from jinja2 import Environment, StrictUndefined, Template, TemplateSyntaxError
except ImportError:
    raise ImportError("jinja2 is required. Install with: pip install jinja2")

try:
    from jsonschema import Draft7Validator, ValidationError
except ImportError:
    raise ImportError("jsonschema is required. Install with: pip install jsonschema")

from .manager import PromptTemplateManager, PromptTemplateNotFoundError


class RenderError(Exception):
    """渲染错误"""
    pass


class InputValidationError(Exception):
    """输入验证错误"""
    pass


class PromptRenderer:
    """Prompt 模板渲染器"""

    def __init__(
        self,
        manager: Optional[PromptTemplateManager] = None,
        strict_mode: bool = True
    ):
        """
        初始化渲染器

        Args:
            manager: Prompt 模板管理器 (None 时自动创建)
            strict_mode: 严格模式 (未定义变量会抛出错误，默认 True)
        """
        self.manager = manager or PromptTemplateManager()
        self.strict_mode = strict_mode

        # 创建 Jinja2 环境
        self.jinja_env = Environment(
            undefined=StrictUndefined if strict_mode else None,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # 注册自定义过滤器
        self._register_filters()

    def _register_filters(self) -> None:
        """注册自定义 Jinja2 过滤器"""
        # 日期时间格式化
        def format_datetime(value: str, format: str = "%Y-%m-%d %H:%M:%S") -> str:
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt.strftime(format)
            except Exception:
                return value

        # JSON 格式化
        def to_json(value: Any, indent: Optional[int] = 2) -> str:
            return json.dumps(value, indent=indent, ensure_ascii=False)

        # 截断字符串
        def truncate(value: str, length: int = 100, suffix: str = "...") -> str:
            if len(value) <= length:
                return value
            return value[:length - len(suffix)] + suffix

        # 注册过滤器
        self.jinja_env.filters["format_datetime"] = format_datetime
        self.jinja_env.filters["to_json"] = to_json
        self.jinja_env.filters["truncate"] = truncate

    def _validate_input(
        self,
        input_data: Dict[str, Any],
        input_schema: Dict[str, Any]
    ) -> None:
        """
        验证输入数据是否符合 input_schema

        Args:
            input_data: 输入数据
            input_schema: JSON Schema 定义

        Raises:
            InputValidationError: 验证失败
        """
        validator = Draft7Validator(input_schema)
        errors = list(validator.iter_errors(input_data))

        if errors:
            error_messages = []
            for error in errors:
                path = " -> ".join(str(p) for p in error.path) if error.path else "root"
                error_messages.append(f"{path}: {error.message}")

            raise InputValidationError(
                f"Input validation failed with {len(errors)} errors:\n" +
                "\n".join(error_messages)
            )

    def render(
        self,
        language: str,
        stage: str,
        input_data: Dict[str, Any],
        version: Optional[str] = None,
        validate_input: bool = True
    ) -> str:
        """
        渲染 Prompt 模板

        Args:
            language: 编程语言
            stage: 分析阶段
            input_data: 输入数据
            version: 版本号 (None 表示 latest)
            validate_input: 是否验证输入 (默认 True)

        Returns:
            str: 渲染后的 Prompt 文本

        Raises:
            PromptTemplateNotFoundError: 模板未找到
            InputValidationError: 输入验证失败
            RenderError: 渲染失败
        """
        # 加载模板
        template_data = self.manager.load_template(language, stage, version)

        # 验证输入
        if validate_input and "input_schema" in template_data:
            self._validate_input(input_data, template_data["input_schema"])

        # 渲染模板
        try:
            template_str = template_data.get("template", "")
            template = self.jinja_env.from_string(template_str)
            rendered = template.render(**input_data)
            return rendered

        except TemplateSyntaxError as e:
            raise RenderError(f"Template syntax error: {e}") from e
        except Exception as e:
            raise RenderError(f"Render failed: {e}") from e

    def render_by_id(
        self,
        template_id: str,
        input_data: Dict[str, Any],
        validate_input: bool = True
    ) -> str:
        """
        通过模板 ID 渲染

        Args:
            template_id: 模板 ID
            input_data: 输入数据
            validate_input: 是否验证输入

        Returns:
            str: 渲染后的 Prompt 文本
        """
        # 加载模板
        template_data = self.manager.get_template_by_id(template_id)

        # 验证输入
        if validate_input and "input_schema" in template_data:
            self._validate_input(input_data, template_data["input_schema"])

        # 渲染模板
        try:
            template_str = template_data.get("template", "")
            template = self.jinja_env.from_string(template_str)
            rendered = template.render(**input_data)
            return rendered

        except TemplateSyntaxError as e:
            raise RenderError(f"Template syntax error: {e}") from e
        except Exception as e:
            raise RenderError(f"Render failed: {e}") from e

    def render_template_string(
        self,
        template_str: str,
        input_data: Dict[str, Any]
    ) -> str:
        """
        直接渲染模板字符串（不通过文件）

        Args:
            template_str: 模板字符串
            input_data: 输入数据

        Returns:
            str: 渲染后的文本

        Raises:
            RenderError: 渲染失败
        """
        try:
            template = self.jinja_env.from_string(template_str)
            return template.render(**input_data)
        except TemplateSyntaxError as e:
            raise RenderError(f"Template syntax error: {e}") from e
        except Exception as e:
            raise RenderError(f"Render failed: {e}") from e


# 便捷函数

def render_prompt(
    language: str,
    stage: str,
    input_data: Dict[str, Any],
    version: Optional[str] = None,
    validate_input: bool = True
) -> str:
    """
    便捷函数：渲染 Prompt 模板

    Args:
        language: 编程语言
        stage: 分析阶段
        input_data: 输入数据
        version: 版本号 (None 表示 latest)
        validate_input: 是否验证输入

    Returns:
        str: 渲染后的 Prompt 文本
    """
    renderer = PromptRenderer()
    return renderer.render(language, stage, input_data, version, validate_input)


# CLI 入口（用于测试）
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage:")
        print("  python renderer.py <language> <stage> <input.json> [version]")
        print()
        print("Example:")
        print("  python renderer.py python project_understanding input.json")
        sys.exit(1)

    language = sys.argv[1]
    stage = sys.argv[2]
    input_file = Path(sys.argv[3])
    version = sys.argv[4] if len(sys.argv) > 4 else None

    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    # 加载输入数据
    with open(input_file, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    # 渲染
    try:
        renderer = PromptRenderer()
        rendered = renderer.render(language, stage, input_data, version, validate_input=True)
        print(rendered)
    except (PromptTemplateNotFoundError, InputValidationError, RenderError) as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
