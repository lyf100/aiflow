"""
项目映射器

生成项目的结构地图和代码地图
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 导入缓存模块
from .cache import get_cached_rglob, get_cached_hash, get_cached_line_count


class ProjectMapper:
    """项目映射器 - 生成项目结构和代码地图"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.output_dir = self.project_path / "code2claude"
        self.maps_dir = self.output_dir / "maps"
        self.maps_dir.mkdir(parents=True, exist_ok=True)

    def map_project_structure(self) -> Dict[str, Any]:
        """
        映射项目结构

        Returns:
            项目结构映射字典
        """
        structure_map = {
            "metadata": {
                "project_name": self.project_path.name,
                "project_path": str(self.project_path),
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            },
            "overview": {
                "total_files": 0,
                "total_directories": 0,
                "file_types": {},
                "largest_files": [],
                "deepest_path": ""
            },
            "directory_tree": {},
            "file_index": {},
            "patterns": {
                "config_files": [],
                "test_files": [],
                "documentation": [],
                "assets": [],
                "source_code": {}
            }
        }

        # 构建目录树和文件索引
        structure_map["directory_tree"] = self._build_enhanced_tree()
        structure_map["file_index"] = self._build_file_index()
        structure_map["overview"] = self._calculate_overview_stats()
        structure_map["patterns"] = self._identify_file_patterns()

        return structure_map

    def map_code_structure(self, analysis_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        映射代码结构

        Args:
            analysis_data: 从 CodeAnalyzer 获取的分析数据

        Returns:
            代码结构映射字典
        """
        code_map = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "analysis_source": "provided" if analysis_data else "internal"
            },
            "modules": {},
            "functions": {},
            "classes": {},
            "interfaces": {},
            "namespaces": {},
            "entry_points": [],
            "exports": [],
            "imports": {}
        }

        if analysis_data:
            code_map.update(self._extract_code_elements(analysis_data))
        else:
            # 执行基本的代码结构分析
            code_map.update(self._analyze_code_structure())

        return code_map

    def generate_interactive_map(self) -> str:
        """
        生成交互式项目地图 (HTML)

        Returns:
            生成的 HTML 文件路径
        """
        structure_data = self.map_project_structure()

        html_content = self._create_interactive_html(structure_data)

        output_file = self.maps_dir / "interactive_map.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file)

    def _build_enhanced_tree(self, path: Path = None, level: int = 0) -> Dict[str, Any]:
        """构建增强的目录树"""
        if path is None:
            path = self.project_path

        if level > 10:  # 防止过深递归
            return {"name": path.name, "type": "directory", "truncated": True}

        node = {
            "name": path.name,
            "path": str(path.relative_to(self.project_path)),
            "type": "directory",
            "level": level,
            "children": [],
            "stats": {
                "file_count": 0,
                "dir_count": 0,
                "total_size": 0
            }
        }

        try:
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))

            for item in items:
                # 跳过特定的隐藏文件和目录
                if self._should_skip_item(item):
                    continue

                if item.is_dir():
                    child_node = self._build_enhanced_tree(item, level + 1)
                    node["children"].append(child_node)
                    node["stats"]["dir_count"] += 1
                    # 只有目录节点才有 stats
                    if "stats" in child_node:
                        node["stats"]["file_count"] += child_node["stats"]["file_count"]
                        node["stats"]["total_size"] += child_node["stats"]["total_size"]
                else:
                    file_info = self._get_file_info(item)
                    node["children"].append(file_info)
                    node["stats"]["file_count"] += 1
                    node["stats"]["total_size"] += file_info.get("size", 0)

        except PermissionError:
            node["error"] = "Permission denied"

        return node

    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """获取文件详细信息"""
        try:
            stat = file_path.stat()
            info = {
                "name": file_path.name,
                "path": str(file_path.relative_to(self.project_path)),
                "type": "file",
                "extension": file_path.suffix.lower(),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "hash": self._calculate_file_hash(file_path)
            }

            # 添加文件类型特定信息
            if file_path.suffix.lower() in ['.py', '.js', '.ts', '.dart', '.java']:
                info["language"] = self._detect_file_language(file_path)
                info["lines"] = self._count_lines(file_path)

            return info

        except (IOError, OSError) as e:
            logging.error(f"文件访问错误 {file_path}: {e}")
            return {
                "name": file_path.name,
                "path": str(file_path.relative_to(self.project_path)),
                "type": "file",
                "error": f"File access error: {e}"
            }
        except PermissionError as e:
            logging.error(f"文件权限不足 {file_path}: {e}")
            return {
                "name": file_path.name,
                "path": str(file_path.relative_to(self.project_path)),
                "type": "file",
                "error": f"Permission denied: {e}"
            }
        except Exception as e:
            logging.error(f"获取文件信息时发生未知错误 {file_path}: {type(e).__name__}: {e}")
            return {
                "name": file_path.name,
                "path": str(file_path.relative_to(self.project_path)),
                "type": "file",
                "error": f"Unknown error: {type(e).__name__}: {e}"
            }

    def _build_file_index(self) -> Dict[str, Any]:
        """构建文件索引"""
        index = {
            "by_extension": {},
            "by_size": [],
            "by_name": {},
            "duplicates": []
        }

        file_hashes = {}

        for file_path in get_cached_rglob(self.project_path, "*"):
            if file_path.is_file() and not self._should_skip_item(file_path):
                rel_path = str(file_path.relative_to(self.project_path))
                ext = file_path.suffix.lower()

                # 按扩展名索引
                if ext not in index["by_extension"]:
                    index["by_extension"][ext] = []
                index["by_extension"][ext].append(rel_path)

                # 按名称索引
                name = file_path.name
                if name not in index["by_name"]:
                    index["by_name"][name] = []
                index["by_name"][name].append(rel_path)

                # 按大小索引
                try:
                    size = file_path.stat().st_size
                    index["by_size"].append({
                        "path": rel_path,
                        "size": size,
                        "name": file_path.name
                    })

                    # 检测重复文件
                    file_hash = self._calculate_file_hash(file_path)
                    if file_hash in file_hashes:
                        # 找到重复文件
                        duplicate_group = next(
                            (group for group in index["duplicates"] if group["hash"] == file_hash),
                            None
                        )
                        if duplicate_group:
                            duplicate_group["files"].append(rel_path)
                        else:
                            index["duplicates"].append({
                                "hash": file_hash,
                                "files": [file_hashes[file_hash], rel_path]
                            })
                    else:
                        file_hashes[file_hash] = rel_path

                except (IOError, OSError):
                    # 文件访问错误,跳过
                    continue
                except PermissionError:
                    # 权限错误,跳过
                    continue

        # 排序大小索引
        index["by_size"].sort(key=lambda x: x["size"], reverse=True)

        return index

    def _identify_file_patterns(self) -> Dict[str, Any]:
        """识别文件模式"""
        patterns = {
            "config_files": [],
            "test_files": [],
            "documentation": [],
            "assets": [],
            "source_code": {},
            "build_files": [],
            "data_files": []
        }

        config_patterns = [
            '*.json', '*.yaml', '*.yml', '*.toml', '*.ini', '*.cfg',
            '.env*', 'config.*', '*.config.*', 'settings.*'
        ]

        test_patterns = [
            'test_*.py', '*_test.py', '*.test.js', '*.spec.js',
            'test/*.py', 'tests/*.py', '__tests__/*'
        ]

        doc_patterns = [
            '*.md', '*.rst', '*.txt', 'README*', 'CHANGELOG*',
            'LICENSE*', 'CONTRIBUTORS*', 'docs/*'
        ]

        asset_patterns = [
            '*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg', '*.ico',
            '*.css', '*.scss', '*.sass', '*.less'
        ]

        build_patterns = [
            'Makefile', '*.gradle', 'build.xml', 'pom.xml',
            'Dockerfile*', 'docker-compose*'
        ]

        data_patterns = [
            '*.csv', '*.json', '*.xml', '*.sqlite', '*.db'
        ]

        source_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.dart': 'Dart',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.go': 'Go',
            '.rs': 'Rust'
        }

        for file_path in get_cached_rglob(self.project_path, "*"):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(self.project_path))

                # 检查各种模式
                if self._matches_patterns(file_path, config_patterns):
                    patterns["config_files"].append(rel_path)
                elif self._matches_patterns(file_path, test_patterns):
                    patterns["test_files"].append(rel_path)
                elif self._matches_patterns(file_path, doc_patterns):
                    patterns["documentation"].append(rel_path)
                elif self._matches_patterns(file_path, asset_patterns):
                    patterns["assets"].append(rel_path)
                elif self._matches_patterns(file_path, build_patterns):
                    patterns["build_files"].append(rel_path)
                elif self._matches_patterns(file_path, data_patterns):
                    patterns["data_files"].append(rel_path)

                # 源代码分类
                ext = file_path.suffix.lower()
                if ext in source_extensions:
                    lang = source_extensions[ext]
                    if lang not in patterns["source_code"]:
                        patterns["source_code"][lang] = []
                    patterns["source_code"][lang].append(rel_path)

        return patterns

    def _calculate_overview_stats(self) -> Dict[str, Any]:
        """计算项目概览统计"""
        stats = {
            "total_files": 0,
            "total_directories": 0,
            "file_types": {},
            "largest_files": [],
            "deepest_path": "",
            "total_size": 0
        }

        max_depth = 0
        deepest_path = ""

        for item in get_cached_rglob(self.project_path, "*"):
            if self._should_skip_item(item):
                continue

            depth = len(item.relative_to(self.project_path).parts)
            if depth > max_depth:
                max_depth = depth
                deepest_path = str(item.relative_to(self.project_path))

            if item.is_file():
                stats["total_files"] += 1
                ext = item.suffix.lower()
                stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1

                try:
                    size = item.stat().st_size
                    stats["total_size"] += size
                    stats["largest_files"].append({
                        "path": str(item.relative_to(self.project_path)),
                        "size": size,
                        "name": item.name
                    })
                except (IOError, OSError):
                    # 文件访问错误,跳过
                    continue
                except PermissionError:
                    # 权限错误,跳过
                    continue
            else:
                stats["total_directories"] += 1

        # 保留最大的文件
        stats["largest_files"].sort(key=lambda x: x["size"], reverse=True)
        stats["largest_files"] = stats["largest_files"][:10]
        stats["deepest_path"] = deepest_path

        return stats

    def _extract_code_elements(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """从分析数据中提取代码元素"""
        elements = {
            "modules": {},
            "functions": {},
            "classes": {},
            "entry_points": [],
            "imports": {}
        }

        languages = analysis_data.get("languages", {})
        for lang, lang_data in languages.items():
            # 提取函数
            for func in lang_data.get("functions", []):
                func_key = f"{func['file']}::{func['name']}"
                elements["functions"][func_key] = {
                    "name": func["name"],
                    "file": func["file"],
                    "line": func.get("line", 0),
                    "language": lang,
                    "calls": func.get("calls", [])
                }

            # 提取类
            for cls in lang_data.get("classes", []):
                cls_key = f"{cls['file']}::{cls['name']}"
                elements["classes"][cls_key] = {
                    "name": cls["name"],
                    "file": cls["file"],
                    "line": cls.get("line", 0),
                    "language": lang,
                    "methods": cls.get("methods", [])
                }

        return elements

    def _analyze_code_structure(self) -> Dict[str, Any]:
        """基本的代码结构分析（不依赖外部分析）"""
        return {
            "modules": {},
            "functions": {},
            "classes": {},
            "note": "Basic analysis - detailed code analysis requires external analyzer"
        }

    def _create_interactive_html(self, structure_data: Dict[str, Any]) -> str:
        """创建交互式 HTML 地图"""
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>项目地图 - {project_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 20px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .tree {{
            padding: 20px;
            font-family: monospace;
        }}
        .tree-node {{
            margin-left: 20px;
            padding: 2px 0;
            cursor: pointer;
        }}
        .tree-node:hover {{
            background-color: #e3f2fd;
        }}
        .directory {{
            color: #1976d2;
            font-weight: bold;
        }}
        .file {{
            color: #424242;
        }}
        .toggle {{
            color: #666;
            margin-right: 5px;
        }}
        .file-type {{
            display: inline-block;
            padding: 2px 6px;
            background: #e0e0e0;
            border-radius: 3px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        .size {{
            color: #666;
            font-size: 0.9em;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📁 项目地图</h1>
            <h2>{project_name}</h2>
            <p>生成时间: {timestamp}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>📊 项目统计</h3>
                <p>总文件数: {total_files}</p>
                <p>总目录数: {total_directories}</p>
                <p>总大小: {total_size_mb:.2f} MB</p>
            </div>
            <div class="stat-card">
                <h3>📄 文件类型</h3>
                {file_types_html}
            </div>
            <div class="stat-card">
                <h3>🔍 最大文件</h3>
                {largest_files_html}
            </div>
        </div>

        <div class="tree">
            <h3>🌳 项目结构</h3>
            <div id="projectTree">
                {tree_html}
            </div>
        </div>
    </div>

    <script>
        // 简单的树状图交互
        document.addEventListener('DOMContentLoaded', function() {{
            const nodes = document.querySelectorAll('.tree-node');
            nodes.forEach(node => {{
                node.addEventListener('click', function(e) {{
                    e.stopPropagation();
                    const children = this.nextElementSibling;
                    if (children && children.classList.contains('children')) {{
                        children.style.display = children.style.display === 'none' ? 'block' : 'none';
                        const toggle = this.querySelector('.toggle');
                        toggle.textContent = children.style.display === 'none' ? '📁' : '📂';
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>
        """

        # 准备数据
        overview = structure_data.get("overview", {})
        project_name = structure_data["metadata"]["project_name"]
        timestamp = structure_data["metadata"]["timestamp"]

        # 格式化文件类型
        file_types_html = ""
        for ext, count in overview.get("file_types", {}).items():
            file_types_html += f"<p>{ext or 'no ext'}: {count}</p>"

        # 格式化最大文件
        largest_files_html = ""
        for file_info in overview.get("largest_files", [])[:5]:
            size_kb = file_info["size"] / 1024
            largest_files_html += f"<p>{file_info['name']}: {size_kb:.1f} KB</p>"

        # 生成树状 HTML
        tree_html = self._generate_tree_html(structure_data.get("directory_tree", {}))

        return html_template.format(
            project_name=project_name,
            timestamp=timestamp,
            total_files=overview.get("total_files", 0),
            total_directories=overview.get("total_directories", 0),
            total_size_mb=overview.get("total_size", 0) / (1024 * 1024),
            file_types_html=file_types_html,
            largest_files_html=largest_files_html,
            tree_html=tree_html
        )

    def _generate_tree_html(self, tree_node: Dict[str, Any], level: int = 0) -> str:
        """生成树状 HTML"""
        if not tree_node:
            return ""

        html = ""
        name = tree_node.get("name", "")
        node_type = tree_node.get("type", "file")

        if node_type == "directory":
            children = tree_node.get("children", [])
            has_children = len(children) > 0
            toggle = "📁" if has_children else "📁"

            html += f'<div class="tree-node directory" style="margin-left: {level * 20}px;">'
            html += f'<span class="toggle">{toggle}</span>{name}'
            if "stats" in tree_node:
                stats = tree_node["stats"]
                html += f'<span class="size">({stats["file_count"]} files)</span>'
            html += '</div>'

            if has_children:
                html += '<div class="children">'
                for child in children:
                    html += self._generate_tree_html(child, level + 1)
                html += '</div>'
        else:
            # 文件
            ext = tree_node.get("extension", "")
            size = tree_node.get("size", 0)
            html += f'<div class="file" style="margin-left: {level * 20}px;">'
            html += f'📄 {name}'
            if ext:
                html += f'<span class="file-type">{ext}</span>'
            if size > 0:
                html += f'<span class="size">{size // 1024:.0f} KB</span>'
            html += '</div>'

        return html

    def _should_skip_item(self, path: Path) -> bool:
        """判断是否应该跳过某个文件或目录"""
        skip_patterns = {
            '.git', '.svn', '.hg', '.bzr',
            '__pycache__', '.pytest_cache', 'node_modules',
            '.vscode', '.idea', '.vs',
            '*.pyc', '*.pyo', '*.pyd', '.DS_Store',
            'Thumbs.db', '*.tmp', '*.log'
        }

        name = path.name

        # 检查精确匹配
        if name in skip_patterns:
            return True

        # 检查模式匹配
        for pattern in skip_patterns:
            if '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(name, pattern):
                    return True

        return False

    def _matches_patterns(self, file_path: Path, patterns: List[str]) -> bool:
        """检查文件是否匹配某些模式"""
        import fnmatch

        name = file_path.name
        rel_path = str(file_path.relative_to(self.project_path))

        for pattern in patterns:
            if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel_path, pattern):
                return True
        return False

    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值 (使用缓存)"""
        return get_cached_hash(file_path)

    def _detect_file_language(self, file_path: Path) -> str:
        """检测文件语言"""
        ext_mapping = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.dart': 'Dart',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.rb': 'Ruby',
            '.php': 'PHP'
        }
        return ext_mapping.get(file_path.suffix.lower(), 'Unknown')

    def _count_lines(self, file_path: Path) -> int:
        """统计文件行数 (使用缓存)"""
        return get_cached_line_count(file_path)

    def save_maps(self) -> Dict[str, str]:
        """保存所有地图到文件"""
        saved_files = {}

        # 保存结构地图
        structure_map = self.map_project_structure()
        structure_file = self.maps_dir / "structure_map.json"
        with open(structure_file, 'w', encoding='utf-8') as f:
            json.dump(structure_map, f, indent=2, ensure_ascii=False)
        saved_files["structure"] = str(structure_file)

        # 保存代码地图
        code_map = self.map_code_structure()
        code_file = self.maps_dir / "code_map.json"
        with open(code_file, 'w', encoding='utf-8') as f:
            json.dump(code_map, f, indent=2, ensure_ascii=False)
        saved_files["code"] = str(code_file)

        # 生成交互式地图
        interactive_file = self.generate_interactive_map()
        saved_files["interactive"] = interactive_file

        return saved_files