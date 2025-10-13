"""
AIFlow Prompt Template Manager
Prompt 模板管理器 - 加载、查找、版本管理

核心功能:
1. 加载 registry.yaml 注册表
2. 查找和加载 Prompt 模板
3. 版本管理 (latest, 特定版本)
4. 缓存机制
5. 列出所有可用模板
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class PromptTemplateInfo:
    """Prompt 模板信息"""
    id: str
    version: str
    file_path: Path
    description: str
    target_language: str
    stage: str
    target_ai_models: List[str]
    estimated_tokens: int


class PromptTemplateNotFoundError(Exception):
    """模板未找到错误"""
    pass


class PromptTemplateManager:
    """Prompt 模板管理器"""

    def __init__(self, prompts_dir: Optional[Path] = None):
        """
        初始化管理器

        Args:
            prompts_dir: Prompt 模板根目录 (默认: backend/prompts/)
        """
        if prompts_dir is None:
            # 默认路径: backend/prompts/
            prompts_dir = Path(__file__).parent.parent.parent / "prompts"

        self.prompts_dir = prompts_dir
        self.registry_path = prompts_dir / "registry.yaml"

        # 缓存
        self._registry: Optional[Dict[str, Any]] = None
        self._template_cache: Dict[str, Dict[str, Any]] = {}

    def _load_registry(self) -> Dict[str, Any]:
        """加载 registry.yaml"""
        if self._registry is not None:
            return self._registry

        if not self.registry_path.exists():
            raise FileNotFoundError(f"Registry not found: {self.registry_path}")

        with open(self.registry_path, "r", encoding="utf-8") as f:
            self._registry = yaml.safe_load(f)

        return self._registry

    def list_languages(self) -> List[str]:
        """列出所有支持的编程语言"""
        registry = self._load_registry()
        return list(registry.keys() - {"version"})  # 排除 version 字段

    def list_stages(self, language: str) -> List[str]:
        """
        列出指定语言的所有分析阶段

        Args:
            language: 编程语言 (如 "python", "javascript")

        Returns:
            List[str]: 阶段列表
        """
        registry = self._load_registry()
        if language not in registry:
            raise ValueError(f"Language not found: {language}")

        return list(registry[language].keys())

    def get_template_info(
        self,
        language: str,
        stage: str,
        version: Optional[str] = None
    ) -> PromptTemplateInfo:
        """
        获取 Prompt 模板信息

        Args:
            language: 编程语言
            stage: 分析阶段
            version: 版本号 (None 表示 latest)

        Returns:
            PromptTemplateInfo: 模板信息

        Raises:
            PromptTemplateNotFoundError: 模板未找到
        """
        registry = self._load_registry()

        # 检查语言
        if language not in registry:
            raise PromptTemplateNotFoundError(f"Language not found: {language}")

        # 检查阶段
        if stage not in registry[language]:
            raise PromptTemplateNotFoundError(
                f"Stage '{stage}' not found for language '{language}'"
            )

        stage_info = registry[language][stage]

        # 获取版本
        if version is None:
            version = stage_info.get("latest")
            if version is None:
                raise PromptTemplateNotFoundError(
                    f"No latest version for {language}/{stage}"
                )

        # 查找模板
        templates = stage_info.get("templates", [])
        for template in templates:
            if template["version"] == version:
                file_path = self.prompts_dir / template["file_path"]
                return PromptTemplateInfo(
                    id=template["id"],
                    version=template["version"],
                    file_path=file_path,
                    description=template.get("description", ""),
                    target_language=language,
                    stage=stage,
                    target_ai_models=template.get("target_ai_models", []),
                    estimated_tokens=template.get("estimated_tokens", 0),
                )

        raise PromptTemplateNotFoundError(
            f"Template not found: {language}/{stage} version {version}"
        )

    def load_template(
        self,
        language: str,
        stage: str,
        version: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        加载 Prompt 模板

        Args:
            language: 编程语言
            stage: 分析阶段
            version: 版本号 (None 表示 latest)
            use_cache: 是否使用缓存 (默认 True)

        Returns:
            Dict[str, Any]: 模板内容 (包含 metadata, template, input_schema, output_schema 等)

        Raises:
            PromptTemplateNotFoundError: 模板未找到
        """
        # 获取模板信息
        template_info = self.get_template_info(language, stage, version)

        # 检查缓存
        cache_key = str(template_info.file_path)
        if use_cache and cache_key in self._template_cache:
            return self._template_cache[cache_key]

        # 加载模板文件
        if not template_info.file_path.exists():
            raise PromptTemplateNotFoundError(
                f"Template file not found: {template_info.file_path}"
            )

        with open(template_info.file_path, "r", encoding="utf-8") as f:
            template_data = yaml.safe_load(f)

        # 缓存
        if use_cache:
            self._template_cache[cache_key] = template_data

        return template_data

    def get_template_by_id(
        self,
        template_id: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        通过 ID 加载 Prompt 模板

        Args:
            template_id: 模板 ID (如 "python-project-understanding-v1.0.0")
            use_cache: 是否使用缓存

        Returns:
            Dict[str, Any]: 模板内容

        Raises:
            PromptTemplateNotFoundError: 模板未找到
        """
        registry = self._load_registry()

        # 遍历所有语言和阶段
        for language in self.list_languages():
            for stage in self.list_stages(language):
                stage_info = registry[language][stage]
                for template in stage_info.get("templates", []):
                    if template["id"] == template_id:
                        return self.load_template(
                            language,
                            stage,
                            template["version"],
                            use_cache=use_cache
                        )

        raise PromptTemplateNotFoundError(f"Template ID not found: {template_id}")

    def list_all_templates(self) -> List[PromptTemplateInfo]:
        """
        列出所有可用的 Prompt 模板

        Returns:
            List[PromptTemplateInfo]: 所有模板信息列表
        """
        templates = []

        for language in self.list_languages():
            for stage in self.list_stages(language):
                try:
                    # 获取 latest 版本
                    template_info = self.get_template_info(language, stage, version=None)
                    templates.append(template_info)
                except PromptTemplateNotFoundError:
                    # 跳过没有 latest 版本的阶段
                    continue

        return templates

    def clear_cache(self) -> None:
        """清空模板缓存"""
        self._template_cache.clear()
        self._registry = None


# 便捷函数

def get_prompt_manager(prompts_dir: Optional[Path] = None) -> PromptTemplateManager:
    """
    获取全局 Prompt 模板管理器实例

    Args:
        prompts_dir: Prompt 模板根目录 (可选)

    Returns:
        PromptTemplateManager: 管理器实例
    """
    return PromptTemplateManager(prompts_dir)


def load_prompt_template(
    language: str,
    stage: str,
    version: Optional[str] = None
) -> Dict[str, Any]:
    """
    便捷函数：加载 Prompt 模板

    Args:
        language: 编程语言
        stage: 分析阶段
        version: 版本号 (None 表示 latest)

    Returns:
        Dict[str, Any]: 模板内容
    """
    manager = get_prompt_manager()
    return manager.load_template(language, stage, version)


# CLI 入口（用于测试）
if __name__ == "__main__":
    import sys

    manager = PromptTemplateManager()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  List languages:  python manager.py list")
        print("  List stages:     python manager.py list <language>")
        print("  Load template:   python manager.py load <language> <stage> [version]")
        print("  Show template:   python manager.py show <template_id>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        if len(sys.argv) == 2:
            # 列出所有语言
            print("Supported languages:")
            for lang in manager.list_languages():
                print(f"  - {lang}")
        else:
            # 列出指定语言的所有阶段
            language = sys.argv[2]
            print(f"Stages for {language}:")
            for stage in manager.list_stages(language):
                print(f"  - {stage}")

    elif command == "load":
        if len(sys.argv) < 4:
            print("Usage: python manager.py load <language> <stage> [version]")
            sys.exit(1)

        language = sys.argv[2]
        stage = sys.argv[3]
        version = sys.argv[4] if len(sys.argv) > 4 else None

        try:
            template = manager.load_template(language, stage, version)
            print(f"✅ Loaded: {template['metadata']['id']}")
            print(f"Description: {template['metadata']['description']}")
            print(f"Estimated tokens: {template['metadata']['estimated_tokens']}")
        except PromptTemplateNotFoundError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: python manager.py show <template_id>")
            sys.exit(1)

        template_id = sys.argv[2]
        try:
            template = manager.get_template_by_id(template_id)
            print(yaml.dump(template, allow_unicode=True, default_flow_style=False))
        except PromptTemplateNotFoundError as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    else:
        print(f"Error: Unknown command '{command}'")
        sys.exit(1)
