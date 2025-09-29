"""
代码分析器

基于 code2flow 引擎的增强代码分析功能
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys

# 添加 code2flow 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "code2flow-master"))

try:
    from code2flow.engine import code2flow, get_sources_and_language, map_it
    from code2flow.model import Group, Node, Edge
except ImportError as e:
    logging.warning(f"Code2flow 模块导入失败: {e}")
    # 提供降级功能
    code2flow = None


class CodeAnalyzer:
    """代码分析器 - 基于 code2flow 的增强版本"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.output_dir = self.project_path / "code2claude"
        self.analysis_data = {}

    def analyze_project(self, languages: List[str] = None) -> Dict[str, Any]:
        """
        分析整个项目

        Args:
            languages: 要分析的语言列表，默认自动检测

        Returns:
            分析结果字典
        """
        if not code2flow:
            return self._fallback_analysis()

        analysis_result = {
            "metadata": {
                "project_path": str(self.project_path),
                "timestamp": self._get_timestamp(),
                "version": "1.0.0"
            },
            "languages": {},
            "structure": {},
            "dependencies": {},
            "hotspots": {},
            "metrics": {}
        }

        # 检测项目中的语言
        detected_languages = self._detect_languages()
        target_languages = languages or detected_languages

        for lang in target_languages:
            lang_analysis = self._analyze_language(lang)
            if lang_analysis:
                analysis_result["languages"][lang] = lang_analysis

        # 合并跨语言分析结果
        analysis_result["structure"] = self._build_project_structure()
        analysis_result["dependencies"] = self._analyze_dependencies()
        analysis_result["hotspots"] = self._identify_hotspots()
        analysis_result["metrics"] = self._calculate_metrics()

        self.analysis_data = analysis_result
        return analysis_result

    def _detect_languages(self) -> List[str]:
        """检测项目中使用的编程语言"""
        language_extensions = {
            'py': ['*.py'],
            'js': ['*.js', '*.mjs', '*.jsx'],
            'rb': ['*.rb'],
            'php': ['*.php'],
            'ts': ['*.ts', '*.tsx'],
            'dart': ['*.dart'],
            'java': ['*.java'],
            'cpp': ['*.cpp', '*.cc', '*.cxx'],
            'c': ['*.c'],
            'cs': ['*.cs']
        }

        detected = []
        for lang, patterns in language_extensions.items():
            for pattern in patterns:
                if list(self.project_path.rglob(pattern)):
                    detected.append(lang)
                    break

        return detected

    def _analyze_language(self, language: str) -> Optional[Dict[str, Any]]:
        """分析特定语言的代码"""
        # 支持的 code2flow 语言
        supported_langs = ['py', 'js', 'rb', 'php']

        if language not in supported_langs:
            return self._analyze_unsupported_language(language)

        try:
            # 获取该语言的源文件
            pattern = f"*.{language}"
            source_files = list(self.project_path.rglob(pattern))

            if not source_files:
                return None

            # 使用 code2flow 分析
            sources = [str(f) for f in source_files]

            # 创建临时输出文件
            temp_output = self.output_dir / f"temp_{language}.json"
            temp_output.parent.mkdir(parents=True, exist_ok=True)

            # 调用 code2flow 分析
            file_groups, all_nodes, edges = map_it(
                sources=sources,
                extension=language,
                no_trimming=False,
                exclude_namespaces=[],
                exclude_functions=[],
                include_only_namespaces=[],
                include_only_functions=[],
                skip_parse_errors=True,
                lang_params=None
            )

            # 转换结果为我们的格式
            return {
                "files": [str(f) for f in source_files],
                "functions": [self._node_to_dict(node) for node in all_nodes],
                "classes": [self._group_to_dict(group) for group in file_groups if group.group_type.CLASS],
                "call_graph": [self._edge_to_dict(edge) for edge in edges],
                "metrics": {
                    "file_count": len(source_files),
                    "function_count": len(all_nodes),
                    "call_count": len(edges)
                }
            }

        except Exception as e:
            logging.error(f"分析 {language} 代码时出错: {e}")
            return None

    def _analyze_unsupported_language(self, language: str) -> Dict[str, Any]:
        """分析不被 code2flow 直接支持的语言"""
        pattern = f"*.{language}"
        source_files = list(self.project_path.rglob(pattern))

        return {
            "files": [str(f) for f in source_files],
            "functions": [],  # 需要其他工具分析
            "classes": [],
            "call_graph": [],
            "metrics": {
                "file_count": len(source_files),
                "function_count": 0,
                "call_count": 0
            },
            "note": f"Language {language} requires additional analysis tools"
        }

    def _build_project_structure(self) -> Dict[str, Any]:
        """构建项目结构树"""
        structure = {
            "root": str(self.project_path),
            "directories": {},
            "files": {},
            "tree": self._build_directory_tree()
        }
        return structure

    def _build_directory_tree(self, path: Path = None) -> Dict[str, Any]:
        """递归构建目录树"""
        if path is None:
            path = self.project_path

        tree = {
            "name": path.name,
            "type": "directory",
            "children": []
        }

        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith('.') and item.name not in ['.gitignore', '.env']:
                    continue

                if item.is_dir():
                    tree["children"].append(self._build_directory_tree(item))
                else:
                    tree["children"].append({
                        "name": item.name,
                        "type": "file",
                        "size": item.stat().st_size,
                        "extension": item.suffix
                    })
        except PermissionError:
            tree["error"] = "Permission denied"

        return tree

    def _analyze_dependencies(self) -> Dict[str, Any]:
        """分析项目依赖关系"""
        dependencies = {
            "internal": {},  # 内部模块依赖
            "external": {},  # 外部库依赖
            "graph": []      # 依赖图数据
        }

        # 分析不同类型的依赖文件
        dep_files = {
            'requirements.txt': 'python',
            'package.json': 'javascript',
            'Gemfile': 'ruby',
            'composer.json': 'php',
            'pubspec.yaml': 'dart',
            'pom.xml': 'java',
            'Cargo.toml': 'rust'
        }

        for filename, lang in dep_files.items():
            dep_file = self.project_path / filename
            if dep_file.exists():
                dependencies["external"][lang] = self._parse_dependency_file(dep_file, lang)

        return dependencies

    def _parse_dependency_file(self, file_path: Path, lang: str) -> List[str]:
        """解析依赖文件"""
        try:
            content = file_path.read_text(encoding='utf-8')

            if lang == 'python' and file_path.name == 'requirements.txt':
                return [line.strip().split('==')[0].split('>=')[0].split('<=')[0]
                       for line in content.split('\n')
                       if line.strip() and not line.startswith('#')]

            elif lang == 'javascript' and file_path.name == 'package.json':
                import json
                data = json.loads(content)
                deps = []
                deps.extend(data.get('dependencies', {}).keys())
                deps.extend(data.get('devDependencies', {}).keys())
                return deps

            elif lang == 'dart' and file_path.name == 'pubspec.yaml':
                # 简单的 YAML 解析
                lines = content.split('\n')
                deps = []
                in_deps = False
                for line in lines:
                    if line.strip() == 'dependencies:':
                        in_deps = True
                        continue
                    if in_deps and line.startswith('  ') and ':' in line:
                        dep_name = line.strip().split(':')[0]
                        if not dep_name.startswith('#'):
                            deps.append(dep_name)
                    elif in_deps and not line.startswith('  '):
                        break
                return deps

        except Exception as e:
            logging.error(f"解析依赖文件 {file_path} 失败: {e}")

        return []

    def _identify_hotspots(self) -> Dict[str, Any]:
        """识别代码热点（复杂度、变更频率等）"""
        hotspots = {
            "complexity": [],
            "large_files": [],
            "frequent_changes": []
        }

        # 识别大文件
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                try:
                    size = file_path.stat().st_size
                    if size > 10000:  # 大于10KB的文件
                        hotspots["large_files"].append({
                            "path": str(file_path.relative_to(self.project_path)),
                            "size": size,
                            "lines": len(file_path.read_text(encoding='utf-8', errors='ignore').split('\n'))
                        })
                except Exception:
                    continue

        # 按大小排序
        hotspots["large_files"].sort(key=lambda x: x["size"], reverse=True)

        return hotspots

    def _calculate_metrics(self) -> Dict[str, Any]:
        """计算项目指标"""
        metrics = {
            "file_counts": {},
            "code_lines": 0,
            "total_files": 0,
            "languages": len(self.analysis_data.get("languages", {}))
        }

        # 统计文件类型
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file():
                metrics["total_files"] += 1
                ext = file_path.suffix.lower()
                metrics["file_counts"][ext] = metrics["file_counts"].get(ext, 0) + 1

                # 统计代码行数（常见代码文件）
                code_extensions = {'.py', '.js', '.ts', '.dart', '.java', '.cpp', '.c', '.cs', '.rb', '.php'}
                if ext in code_extensions:
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        metrics["code_lines"] += len([line for line in content.split('\n') if line.strip()])
                    except Exception:
                        continue

        return metrics

    def _fallback_analysis(self) -> Dict[str, Any]:
        """当 code2flow 不可用时的降级分析"""
        return {
            "metadata": {
                "project_path": str(self.project_path),
                "timestamp": self._get_timestamp(),
                "version": "1.0.0",
                "mode": "fallback"
            },
            "structure": self._build_project_structure(),
            "dependencies": self._analyze_dependencies(),
            "metrics": self._calculate_metrics(),
            "note": "Limited analysis due to missing code2flow dependency"
        }

    def _node_to_dict(self, node: 'Node') -> Dict[str, Any]:
        """将 code2flow Node 转换为字典"""
        return {
            "name": node.token,
            "file": node.file_group().token if hasattr(node, 'file_group') else "",
            "line": node.line_number,
            "is_constructor": getattr(node, 'is_constructor', False),
            "calls": [call.to_string() for call in getattr(node, 'calls', [])]
        }

    def _group_to_dict(self, group: 'Group') -> Dict[str, Any]:
        """将 code2flow Group 转换为字典"""
        return {
            "name": group.token,
            "type": str(group.group_type),
            "file": group.filename() if hasattr(group, 'filename') else "",
            "line": group.line_number,
            "methods": [node.token for node in getattr(group, 'nodes', [])]
        }

    def _edge_to_dict(self, edge: 'Edge') -> Dict[str, Any]:
        """将 code2flow Edge 转换为字典"""
        return {
            "from": edge.node0.token,
            "to": edge.node1.token,
            "from_file": edge.node0.file_group().token if hasattr(edge.node0, 'file_group') else "",
            "to_file": edge.node1.file_group().token if hasattr(edge.node1, 'file_group') else ""
        }

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()

    def save_analysis(self, filename: str = "analysis.json") -> str:
        """保存分析结果到文件"""
        output_file = self.output_dir / filename
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_data, f, indent=2, ensure_ascii=False)

        return str(output_file)