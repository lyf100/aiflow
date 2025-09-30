"""
依赖关系图生成器

基于 code2flow 的增强依赖关系分析和可视化
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import sys

# 导入缓存模块
from .cache import get_cached_rglob

# 添加 code2flow 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "code2flow-master"))

try:
    from code2flow.engine import code2flow, map_it, write_file
    from code2flow.model import Group, Node, Edge
except ImportError:
    code2flow = None


class DependencyGrapher:
    """依赖关系图生成器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.output_dir = self.project_path / "claudeflow" / "graphs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_call_graph(self, target_language: str = None,
                           target_function: str = None) -> str:
        """
        生成调用关系图

        Args:
            target_language: 目标语言（py, js, rb, php）
            target_function: 目标函数（生成以此函数为中心的子图）

        Returns:
            生成的图文件路径
        """
        if not code2flow:
            return self._generate_basic_graph()

        # 检测语言
        if not target_language:
            target_language = self._detect_primary_language()

        if not target_language:
            raise ValueError("无法检测项目主要语言")

        # 获取源文件
        source_files = self._get_source_files(target_language)
        if not source_files:
            raise ValueError(f"未找到 {target_language} 源文件")

        # 生成输出文件名
        suffix = f"_{target_function}" if target_function else ""
        output_file = self.output_dir / f"call_graph_{target_language}{suffix}.png"

        try:
            # 配置参数
            kwargs = {
                'raw_source_paths': source_files,
                'output_file': str(output_file),
                'language': target_language,
                'hide_legend': False,
                'no_grouping': False,
                'no_trimming': False,
                'skip_parse_errors': True
            }

            # 如果指定了目标函数，添加子集参数
            if target_function:
                kwargs.update({
                    'subset_params': self._create_subset_params(target_function)
                })

            # 调用 code2flow
            code2flow(**kwargs)

            return str(output_file)

        except ImportError as e:
            logging.error(f"code2flow模块导入失败: {e}")
            print(f"生成调用图失败: code2flow未正确安装")
            return self._generate_basic_graph()
        except (IOError, OSError) as e:
            logging.error(f"生成调用图时文件操作错误: {e}")
            print(f"生成调用图失败: 文件操作错误")
            return self._generate_basic_graph()
        except Exception as e:
            logging.error(f"生成调用图时发生未知错误: {type(e).__name__}: {e}")
            print(f"生成调用图失败: {e}")
            return self._generate_basic_graph()

    def generate_dependency_graph(self, graph_type: str = "module") -> str:
        """
        生成依赖关系图

        Args:
            graph_type: 图类型 ("module", "class", "function")

        Returns:
            生成的图文件路径
        """
        graph_data = self._analyze_dependencies(graph_type)
        output_file = self.output_dir / f"dependency_graph_{graph_type}.html"

        html_content = self._create_dependency_html(graph_data, graph_type)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file)

    def generate_class_hierarchy(self) -> str:
        """
        生成类层次结构图

        Returns:
            生成的图文件路径
        """
        hierarchy_data = self._analyze_class_hierarchy()
        output_file = self.output_dir / "class_hierarchy.html"

        html_content = self._create_hierarchy_html(hierarchy_data)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file)

    def generate_module_map(self) -> str:
        """
        生成模块地图

        Returns:
            生成的图文件路径
        """
        module_data = self._analyze_modules()
        output_file = self.output_dir / "module_map.html"

        html_content = self._create_module_map_html(module_data)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file)

    def _detect_primary_language(self) -> Optional[str]:
        """检测项目主要语言"""
        language_counts = {}

        extensions = {
            'py': '*.py',
            'js': '*.js',
            'rb': '*.rb',
            'php': '*.php'
        }

        for lang, pattern in extensions.items():
            files = list(get_cached_rglob(self.project_path, pattern))
            if files:
                language_counts[lang] = len(files)

        if not language_counts:
            return None

        return max(language_counts, key=language_counts.get)

    def _get_source_files(self, language: str) -> List[str]:
        """获取指定语言的源文件"""
        extensions = {
            'py': '*.py',
            'js': '*.js',
            'rb': '*.rb',
            'php': '*.php'
        }

        pattern = extensions.get(language)
        if not pattern:
            return []

        files = list(get_cached_rglob(self.project_path, pattern))
        return [str(f) for f in files]

    def _create_subset_params(self, target_function: str):
        """创建子集参数"""
        try:
            from code2flow.engine import SubsetParams
            return SubsetParams.generate(
                target_function=target_function,
                upstream_depth=2,
                downstream_depth=2
            )
        except ImportError as e:
            logging.warning(f"SubsetParams导入失败: {e}")
            return None
        except Exception as e:
            logging.warning(f"创建子集参数失败: {type(e).__name__}: {e}")
            return None

    def _analyze_dependencies(self, graph_type: str) -> Dict[str, Any]:
        """分析依赖关系"""
        dependencies = {
            "nodes": [],
            "edges": [],
            "metadata": {
                "type": graph_type,
                "timestamp": self._get_timestamp()
            }
        }

        if graph_type == "module":
            dependencies.update(self._analyze_module_dependencies())
        elif graph_type == "class":
            dependencies.update(self._analyze_class_dependencies())
        elif graph_type == "function":
            dependencies.update(self._analyze_function_dependencies())

        return dependencies

    def _analyze_module_dependencies(self) -> Dict[str, Any]:
        """分析模块级依赖"""
        nodes = []
        edges = []

        # 分析不同语言的模块依赖
        python_modules = self._analyze_python_imports()
        js_modules = self._analyze_js_imports()

        nodes.extend(python_modules.get("nodes", []))
        edges.extend(python_modules.get("edges", []))
        nodes.extend(js_modules.get("nodes", []))
        edges.extend(js_modules.get("edges", []))

        return {"nodes": nodes, "edges": edges}

    def _analyze_python_imports(self) -> Dict[str, Any]:
        """分析 Python 导入依赖"""
        nodes = []
        edges = []
        modules = set()

        for py_file in get_cached_rglob(self.project_path, "*.py"):
            if py_file.name.startswith('.'):
                continue

            module_name = str(py_file.relative_to(self.project_path)).replace('/', '.').replace('.py', '')
            modules.add(module_name)

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 简单的导入分析
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        imported = self._parse_python_import(line)
                        for imp in imported:
                            edges.append({
                                "from": module_name,
                                "to": imp,
                                "type": "import"
                            })

            except (IOError, OSError):
                # 文件访问错误,跳过
                continue
            except PermissionError:
                # 权限错误,跳过
                continue
            except UnicodeDecodeError:
                # 编码错误,跳过
                continue

        # 创建节点
        for module in modules:
            nodes.append({
                "id": module,
                "label": module,
                "type": "module",
                "language": "python"
            })

        return {"nodes": nodes, "edges": edges}

    def _parse_python_import(self, line: str) -> List[str]:
        """解析 Python 导入语句"""
        imports = []

        if line.startswith('import '):
            # import module1, module2
            modules = line[7:].split(',')
            for module in modules:
                module = module.strip().split(' as ')[0]
                imports.append(module)

        elif line.startswith('from '):
            # from module import something
            parts = line.split(' import ')
            if len(parts) == 2:
                module = parts[0][5:].strip()
                imports.append(module)

        return imports

    def _analyze_js_imports(self) -> Dict[str, Any]:
        """分析 JavaScript 导入依赖"""
        nodes = []
        edges = []
        modules = set()

        for js_file in get_cached_rglob(self.project_path, "*.js"):
            if js_file.name.startswith('.'):
                continue

            module_name = str(js_file.relative_to(self.project_path))
            modules.add(module_name)

            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 简单的导入分析
                for line in content.split('\n'):
                    line = line.strip()
                    if 'require(' in line or 'import ' in line:
                        imported = self._parse_js_import(line)
                        for imp in imported:
                            edges.append({
                                "from": module_name,
                                "to": imp,
                                "type": "import"
                            })

            except (IOError, OSError):
                # 文件访问错误,跳过
                continue
            except PermissionError:
                # 权限错误,跳过
                continue
            except UnicodeDecodeError:
                # 编码错误,跳过
                continue

        # 创建节点
        for module in modules:
            nodes.append({
                "id": module,
                "label": module,
                "type": "module",
                "language": "javascript"
            })

        return {"nodes": nodes, "edges": edges}

    def _parse_js_import(self, line: str) -> List[str]:
        """解析 JavaScript 导入语句"""
        imports = []

        # require('module')
        if 'require(' in line:
            start = line.find("require('")
            if start != -1:
                start += 9
                end = line.find("')", start)
                if end != -1:
                    imports.append(line[start:end])

        # import ... from 'module'
        if 'import ' in line and ' from ' in line:
            from_pos = line.find(' from ')
            if from_pos != -1:
                module_part = line[from_pos + 6:].strip()
                if module_part.startswith("'") and module_part.endswith("'"):
                    imports.append(module_part[1:-1])

        return imports

    def _analyze_class_dependencies(self) -> Dict[str, Any]:
        """分析类级依赖"""
        # 基础实现，可以扩展
        return {"nodes": [], "edges": []}

    def _analyze_function_dependencies(self) -> Dict[str, Any]:
        """分析函数级依赖"""
        # 基础实现，可以扩展
        return {"nodes": [], "edges": []}

    def _analyze_class_hierarchy(self) -> Dict[str, Any]:
        """分析类层次结构"""
        hierarchy = {
            "classes": [],
            "inheritance": [],
            "metadata": {
                "timestamp": self._get_timestamp()
            }
        }

        # 分析 Python 类
        python_classes = self._analyze_python_classes()
        hierarchy["classes"].extend(python_classes.get("classes", []))
        hierarchy["inheritance"].extend(python_classes.get("inheritance", []))

        return hierarchy

    def _analyze_python_classes(self) -> Dict[str, Any]:
        """分析 Python 类"""
        classes = []
        inheritance = []

        for py_file in get_cached_rglob(self.project_path, "*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 简单的类分析
                for line_num, line in enumerate(content.split('\n'), 1):
                    line = line.strip()
                    if line.startswith('class '):
                        class_info = self._parse_python_class(line, py_file, line_num)
                        if class_info:
                            classes.append(class_info["class"])
                            inheritance.extend(class_info["inheritance"])

            except (IOError, OSError):
                # 文件访问错误,跳过
                continue
            except PermissionError:
                # 权限错误,跳过
                continue
            except UnicodeDecodeError:
                # 编码错误,跳过
                continue

        return {"classes": classes, "inheritance": inheritance}

    def _parse_python_class(self, line: str, file_path: Path, line_num: int) -> Optional[Dict[str, Any]]:
        """解析 Python 类定义"""
        # class ClassName(BaseClass):
        if not line.startswith('class '):
            return None

        # 提取类名和基类
        class_part = line[6:].split(':')[0].strip()

        if '(' in class_part:
            class_name = class_part.split('(')[0].strip()
            base_classes = class_part.split('(')[1].rstrip(')').split(',')
            base_classes = [bc.strip() for bc in base_classes if bc.strip()]
        else:
            class_name = class_part
            base_classes = []

        class_info = {
            "id": f"{file_path.name}::{class_name}",
            "name": class_name,
            "file": str(file_path.relative_to(self.project_path)),
            "line": line_num,
            "language": "python"
        }

        inheritance = []
        for base_class in base_classes:
            inheritance.append({
                "child": class_info["id"],
                "parent": base_class,
                "type": "inheritance"
            })

        return {
            "class": class_info,
            "inheritance": inheritance
        }

    def _analyze_modules(self) -> Dict[str, Any]:
        """分析模块结构"""
        modules = {
            "modules": [],
            "packages": [],
            "relationships": [],
            "metadata": {
                "timestamp": self._get_timestamp()
            }
        }

        # 分析 Python 包结构
        python_modules = self._analyze_python_packages()
        modules.update(python_modules)

        return modules

    def _analyze_python_packages(self) -> Dict[str, Any]:
        """分析 Python 包结构"""
        modules = []
        packages = []
        relationships = []

        # 找到所有 Python 文件和包
        for py_file in get_cached_rglob(self.project_path, "*.py"):
            rel_path = py_file.relative_to(self.project_path)
            module_path = str(rel_path).replace('/', '.').replace('.py', '')

            modules.append({
                "id": module_path,
                "name": py_file.name,
                "path": str(rel_path),
                "type": "module",
                "language": "python"
            })

        # 找到包目录
        for init_file in get_cached_rglob(self.project_path, "__init__.py"):
            package_dir = init_file.parent
            rel_path = package_dir.relative_to(self.project_path)
            package_path = str(rel_path).replace('/', '.')

            packages.append({
                "id": package_path,
                "name": package_dir.name,
                "path": str(rel_path),
                "type": "package",
                "language": "python"
            })

        return {
            "modules": modules,
            "packages": packages,
            "relationships": relationships
        }

    def _create_dependency_html(self, graph_data: Dict[str, Any], graph_type: str) -> str:
        """创建依赖图 HTML"""
        template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>依赖关系图 - {graph_type}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
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
        #graph {{
            width: 100%;
            height: 600px;
        }}
        .node {{
            fill: #69b3a2;
            stroke: #fff;
            stroke-width: 2px;
        }}
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 2px;
        }}
        .node text {{
            font: 12px sans-serif;
            text-anchor: middle;
            fill: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔗 依赖关系图</h1>
            <h2>{graph_type} 级别</h2>
            <p>节点数: {node_count} | 连接数: {edge_count}</p>
        </div>
        <div id="graph"></div>
    </div>

    <script>
        const data = {graph_data_json};

        const width = 1200;
        const height = 600;

        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.edges).id(d => d.id))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const link = svg.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(data.edges)
            .enter().append("line")
            .attr("class", "link");

        const node = svg.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(data.nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", 8)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        const labels = svg.append("g")
            .attr("class", "labels")
            .selectAll("text")
            .data(data.nodes)
            .enter().append("text")
            .text(d => d.label)
            .style("font-size", "12px")
            .style("text-anchor", "middle");

        simulation
            .on("tick", () => {{
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);

                node
                    .attr("cx", d => d.x)
                    .attr("cy", d => d.y);

                labels
                    .attr("x", d => d.x)
                    .attr("y", d => d.y + 4);
            }});

        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}

        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}

        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>
        """

        return template.format(
            graph_type=graph_type,
            node_count=len(graph_data.get("nodes", [])),
            edge_count=len(graph_data.get("edges", [])),
            graph_data_json=json.dumps(graph_data)
        )

    def _create_hierarchy_html(self, hierarchy_data: Dict[str, Any]) -> str:
        """创建类层次结构 HTML"""
        # 简化的层次结构可视化
        template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>类层次结构</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .class {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .inheritance {{ margin-left: 20px; }}
    </style>
</head>
<body>
    <h1>🏗️ 类层次结构</h1>
    <div id="hierarchy">
        {hierarchy_content}
    </div>
</body>
</html>
        """

        hierarchy_content = ""
        for cls in hierarchy_data.get("classes", []):
            hierarchy_content += f"<div class='class'><strong>{cls['name']}</strong> ({cls['file']}:{cls['line']})</div>"

        return template.format(hierarchy_content=hierarchy_content)

    def _create_module_map_html(self, module_data: Dict[str, Any]) -> str:
        """创建模块地图 HTML"""
        template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>模块地图</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .module {{ margin: 5px 0; padding: 8px; background: #f0f0f0; border-radius: 3px; }}
        .package {{ margin: 10px 0; padding: 10px; background: #e0e0e0; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>📦 模块地图</h1>

    <h2>📋 包</h2>
    <div id="packages">
        {packages_content}
    </div>

    <h2>📄 模块</h2>
    <div id="modules">
        {modules_content}
    </div>
</body>
</html>
        """

        packages_content = ""
        for pkg in module_data.get("packages", []):
            packages_content += f"<div class='package'><strong>{pkg['name']}</strong> - {pkg['path']}</div>"

        modules_content = ""
        for mod in module_data.get("modules", []):
            modules_content += f"<div class='module'>{mod['name']} - {mod['path']}</div>"

        return template.format(
            packages_content=packages_content,
            modules_content=modules_content
        )

    def _generate_basic_graph(self) -> str:
        """生成基础图（当 code2flow 不可用时）"""
        output_file = self.output_dir / "basic_graph.html"

        html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>基础项目图</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; text-align: center; }
        .message { background: #fffbf0; border: 1px solid #ddd; padding: 20px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="message">
        <h1>⚠️ 基础图模式</h1>
        <p>Code2flow 模块不可用，无法生成详细的调用图。</p>
        <p>请确保 code2flow 依赖已正确安装。</p>
    </div>
</body>
</html>
        """

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file)

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()

    def generate_all_graphs(self) -> Dict[str, str]:
        """生成所有类型的图"""
        results = {}

        try:
            # 生成调用图
            call_graph = self.generate_call_graph()
            results["call_graph"] = call_graph
        except ImportError as e:
            logging.error(f"生成调用图失败: code2flow未安装: {e}")
            print(f"生成调用图失败: code2flow未正确安装")
        except (IOError, OSError) as e:
            logging.error(f"生成调用图失败: 文件操作错误: {e}")
            print(f"生成调用图失败: 文件操作错误")
        except Exception as e:
            logging.error(f"生成调用图失败: {type(e).__name__}: {e}")
            print(f"生成调用图失败: {e}")

        try:
            # 生成依赖图
            dep_graph = self.generate_dependency_graph("module")
            results["dependency_graph"] = dep_graph
        except (IOError, OSError) as e:
            logging.error(f"生成依赖图失败: 文件操作错误: {e}")
            print(f"生成依赖图失败: 文件操作错误")
        except Exception as e:
            logging.error(f"生成依赖图失败: {type(e).__name__}: {e}")
            print(f"生成依赖图失败: {e}")

        try:
            # 生成类层次图
            class_hierarchy = self.generate_class_hierarchy()
            results["class_hierarchy"] = class_hierarchy
        except (IOError, OSError) as e:
            logging.error(f"生成类层次图失败: 文件操作错误: {e}")
            print(f"生成类层次图失败: 文件操作错误")
        except Exception as e:
            logging.error(f"生成类层次图失败: {type(e).__name__}: {e}")
            print(f"生成类层次图失败: {e}")

        try:
            # 生成模块地图
            module_map = self.generate_module_map()
            results["module_map"] = module_map
        except (IOError, OSError) as e:
            logging.error(f"生成模块地图失败: 文件操作错误: {e}")
            print(f"生成模块地图失败: 文件操作错误")
        except Exception as e:
            logging.error(f"生成模块地图失败: {type(e).__name__}: {e}")
            print(f"生成模块地图失败: {e}")

        return results