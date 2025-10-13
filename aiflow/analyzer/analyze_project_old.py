#!/usr/bin/env python3
"""
AIFlow Analyzer - 项目代码分析工具

将源代码项目转换为 AIFlow JSON 格式的分析数据。
支持多种编程语言：Java, Kotlin, Python, JavaScript, TypeScript 等。
"""

import json
import os
import re
import sys
import io
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime
import uuid
import argparse

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class CodeAnalyzer:
    """代码分析器基类"""

    def __init__(self, project_path: str, project_name: Optional[str] = None):
        self.project_path = Path(project_path)
        self.project_name = project_name or self.project_path.name

        # 数据结构
        self.nodes: List[Dict] = []
        self.edges: List[Dict] = []
        self.launch_buttons: List[Dict] = []
        self.traceable_units: List[Dict] = []

        # 映射表
        self.node_map: Dict[str, str] = {}  # file_path -> node_id
        self.package_map: Dict[str, str] = {}  # package_name -> node_id

        # 统计信息
        self.stats = {
            'total_files': 0,
            'analyzed_files': 0,
            'total_nodes': 0,
            'total_edges': 0,
            'languages': {},
        }

    def analyze(self) -> Dict:
        """执行完整分析"""
        print(f"\n{'='*60}")
        print(f"🔍 开始分析项目: {self.project_name}")
        print(f"📁 项目路径: {self.project_path}")
        print(f"{'='*60}\n")

        # 1. 检测项目类型
        project_type = self._detect_project_type()
        print(f"📦 项目类型: {project_type}")

        # 2. 扫描文件
        self._scan_files()

        # 3. 分析代码结构
        self._analyze_structure()

        # 4. 创建启动按钮
        self._create_launch_buttons()

        # 5. 创建执行轨迹
        self._create_execution_traces()

        # 6. 生成最终 JSON
        return self._generate_result()

    def _detect_project_type(self) -> str:
        """检测项目类型"""
        if (self.project_path / 'pom.xml').exists():
            return 'Java (Maven)'
        elif (self.project_path / 'build.gradle').exists() or (self.project_path / 'build.gradle.kts').exists():
            return 'Java/Kotlin (Gradle)'
        elif (self.project_path / 'package.json').exists():
            return 'JavaScript/TypeScript (Node.js)'
        elif (self.project_path / 'requirements.txt').exists() or (self.project_path / 'setup.py').exists():
            return 'Python'
        elif (self.project_path / 'Cargo.toml').exists():
            return 'Rust'
        elif (self.project_path / 'go.mod').exists():
            return 'Go'
        else:
            return 'Unknown'

    def _scan_files(self):
        """扫描项目文件"""
        print("\n📊 扫描项目文件...")

        # 支持的文件扩展名
        extensions = {
            '.java': 'Java',
            '.kt': 'Kotlin',
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JSX',
            '.tsx': 'TSX',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++ Header',
        }

        for ext, lang in extensions.items():
            files = list(self.project_path.rglob(f'*{ext}'))
            count = len(files)
            if count > 0:
                self.stats['languages'][lang] = count
                self.stats['total_files'] += count

        print(f"   总文件数: {self.stats['total_files']}")
        for lang, count in self.stats['languages'].items():
            print(f"   {lang}: {count}")

    def _analyze_structure(self):
        """分析代码结构"""
        print("\n🔬 分析代码结构...")

        # 创建系统级根节点
        system_node_id = str(uuid.uuid4())
        self.nodes.append({
            'id': system_node_id,
            'name': self.project_name,
            'type': 'class',
            'stereotype': 'system',
            'file_path': str(self.project_path),
            'description': f'{self.project_name} 项目根节点',
        })
        self.node_map['__root__'] = system_node_id

        # 分析主要源代码目录
        src_paths = [
            self.project_path / 'src',
            self.project_path / 'app' / 'src',
            self.project_path / 'lib',
        ]

        for src_path in src_paths:
            if src_path.exists():
                self._analyze_directory(src_path, system_node_id)

        print(f"   分析节点: {len(self.nodes)}")
        print(f"   依赖关系: {len(self.edges)}")

    def _analyze_directory(self, dir_path: Path, parent_node_id: str, depth: int = 0):
        """递归分析目录"""
        if depth > 3:  # 限制深度，避免过深
            return

        # 分析子目录（作为模块）
        for subdir in sorted(dir_path.iterdir()):
            if not subdir.is_dir() or subdir.name.startswith('.') or subdir.name == '__pycache__':
                continue

            # 创建模块节点
            module_node_id = str(uuid.uuid4())
            self.nodes.append({
                'id': module_node_id,
                'name': subdir.name,
                'type': 'class',
                'stereotype': 'module',
                'file_path': str(subdir),
                'description': f'{subdir.name} 模块',
            })

            # 创建包含关系
            self.edges.append({
                'id': str(uuid.uuid4()),
                'source': parent_node_id,
                'target': module_node_id,
                'type': 'contains',
            })

            # 分析模块内的文件
            self._analyze_module_files(subdir, module_node_id)

            # 递归分析子目录
            self._analyze_directory(subdir, module_node_id, depth + 1)

    def _analyze_module_files(self, module_path: Path, parent_node_id: str):
        """分析模块内的文件"""

        # 支持的源文件扩展名
        source_extensions = ['.java', '.kt', '.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs']

        files = []
        for ext in source_extensions:
            files.extend(module_path.glob(f'*{ext}'))

        # 限制每个模块最多分析 10 个文件（避免数据过大）
        for file_path in sorted(files)[:10]:
            self._analyze_file(file_path, parent_node_id)
            self.stats['analyzed_files'] += 1

    def _analyze_file(self, file_path: Path, parent_node_id: str):
        """分析单个文件"""

        class_name = file_path.stem
        language = self._get_language(file_path.suffix)

        # 创建类节点
        class_node_id = str(uuid.uuid4())
        self.nodes.append({
            'id': class_node_id,
            'name': class_name,
            'type': 'class',
            'stereotype': 'component',
            'file_path': str(file_path),
            'language': language,
            'description': f'{class_name} 类',
        })

        # 创建包含关系
        self.edges.append({
            'id': str(uuid.uuid4()),
            'source': parent_node_id,
            'target': class_node_id,
            'type': 'contains',
        })

        self.node_map[str(file_path)] = class_node_id

        # 分析方法
        self._analyze_methods(file_path, class_node_id)

    def _analyze_methods(self, file_path: Path, parent_node_id: str):
        """分析文件中的方法"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return

        # 方法匹配模式
        patterns = {
            'java': r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*\{',
            'kotlin': r'fun\s+(\w+)\s*\([^)]*\)',
            'python': r'def\s+(\w+)\s*\([^)]*\):',
            'javascript': r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)',
            'go': r'func\s+(?:\([^)]*\)\s*)?(\w+)\s*\([^)]*\)',
        }

        language = self._get_language(file_path.suffix).lower()
        pattern = patterns.get(language)
        if not pattern:
            return

        methods_found = set()
        for match in re.finditer(pattern, content):
            method_name = match.group(1) or match.group(2)
            if not method_name or method_name in methods_found:
                continue

            # 过滤 getter/setter
            if method_name.startswith(('get', 'set', '__')):
                continue

            methods_found.add(method_name)

            # 限制每个类最多 5 个方法
            if len([n for n in self.nodes if n.get('parent_class_id') == parent_node_id]) >= 5:
                break

            method_node_id = str(uuid.uuid4())
            self.nodes.append({
                'id': method_node_id,
                'name': method_name,
                'type': 'function',
                'stereotype': 'function',
                'file_path': str(file_path),
                'parent_class_id': parent_node_id,
                'description': f'{method_name}() 方法',
            })

            self.edges.append({
                'id': str(uuid.uuid4()),
                'source': parent_node_id,
                'target': method_node_id,
                'type': 'contains',
            })

    def _get_language(self, extension: str) -> str:
        """根据扩展名获取语言"""
        lang_map = {
            '.java': 'Java',
            '.kt': 'Kotlin',
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JSX',
            '.tsx': 'TSX',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
        }
        return lang_map.get(extension, 'Unknown')

    def _create_launch_buttons(self):
        """创建启动按钮"""
        print("\n🎯 创建启动按钮...")

        # 创建系统级大按钮
        system_button_id = str(uuid.uuid4())
        self.launch_buttons.append({
            'id': system_button_id,
            'name': f'{self.project_name} 应用启动',
            'type': 'macro',
            'level': 'system',
            'description': f'启动整个 {self.project_name} 应用',
            'icon': '🚀',
            'parent_button_id': None,
            'child_button_ids': [],
            'metadata': {
                'ai_confidence': 0.90,
                'estimated_duration': 5000,
            }
        })

        # 为主要模块创建按钮
        module_nodes = [n for n in self.nodes if n.get('stereotype') == 'module']

        for module_node in module_nodes[:8]:  # 限制最多 8 个模块按钮
            button_id = str(uuid.uuid4())
            self.launch_buttons.append({
                'id': button_id,
                'name': f'{module_node["name"]} 模块',
                'type': 'macro',
                'level': 'module',
                'description': f'启动 {module_node["name"]} 模块功能',
                'icon': '📦',
                'parent_button_id': system_button_id,
                'child_button_ids': [],
                'metadata': {
                    'ai_confidence': 0.80,
                }
            })
            self.launch_buttons[0]['child_button_ids'].append(button_id)

        print(f"   创建按钮: {len(self.launch_buttons)}")

    def _create_execution_traces(self):
        """创建执行轨迹"""
        print("\n🔄 创建执行轨迹...")

        # 创建示例执行轨迹
        trace_id = str(uuid.uuid4())
        step_ids = [str(uuid.uuid4()) for _ in range(4)]

        self.traceable_units.append({
            'id': trace_id,
            'name': f'{self.project_name} 启动流程',
            'description': '应用启动的主要流程',
            'entry_point': 'main()',
            'traces': [
                {
                    'format': 'flowchart',
                    'data': {
                        'steps': [
                            {
                                'id': step_ids[0],
                                'label': '应用启动',
                                'type': 'start',
                                'lineNumber': 1,
                            },
                            {
                                'id': step_ids[1],
                                'label': '初始化配置',
                                'type': 'process',
                                'lineNumber': 10,
                            },
                            {
                                'id': step_ids[2],
                                'label': '加载资源',
                                'type': 'process',
                                'lineNumber': 20,
                            },
                            {
                                'id': step_ids[3],
                                'label': '启动完成',
                                'type': 'end',
                                'lineNumber': 30,
                            },
                        ],
                        'connections': [
                            {
                                'id': str(uuid.uuid4()),
                                'source': step_ids[0],
                                'target': step_ids[1],
                                'type': 'control_flow',
                            },
                            {
                                'id': str(uuid.uuid4()),
                                'source': step_ids[1],
                                'target': step_ids[2],
                                'type': 'control_flow',
                            },
                            {
                                'id': str(uuid.uuid4()),
                                'source': step_ids[2],
                                'target': step_ids[3],
                                'type': 'control_flow',
                            },
                        ]
                    }
                }
            ]
        })

        print(f"   创建轨迹: {len(self.traceable_units)}")

    def _generate_result(self) -> Dict:
        """生成最终结果"""
        return {
            'metadata': {
                'project_id': str(uuid.uuid4()),
                'project_name': self.project_name,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'ai_model': 'code-analyzer-v1.0',
                'protocol_version': '1.0.0',
                'analysis_stats': {
                    'total_files': self.stats['total_files'],
                    'analyzed_files': self.stats['analyzed_files'],
                    'total_nodes': len(self.nodes),
                    'total_edges': len(self.edges),
                    'languages': self.stats['languages'],
                }
            },
            'code_structure': {
                'nodes': self.nodes,
                'edges': self.edges,
            },
            'behavior_metadata': {
                'launch_buttons': self.launch_buttons,
            },
            'execution_trace': {
                'traceable_units': self.traceable_units,
            }
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='AIFlow Analyzer - 项目代码分析工具'
    )
    parser.add_argument(
        'project_path',
        help='项目路径'
    )
    parser.add_argument(
        '-o', '--output',
        help='输出文件路径（默认：项目名-analysis.json）'
    )
    parser.add_argument(
        '-n', '--name',
        help='项目名称（默认：目录名）'
    )

    args = parser.parse_args()

    # 分析项目
    analyzer = CodeAnalyzer(args.project_path, args.name)
    result = analyzer.analyze()

    # 生成输出文件名
    if args.output:
        output_path = args.output
    else:
        project_name = result['metadata']['project_name']
        output_path = f"{project_name.lower().replace(' ', '-')}-analysis.json"

    # 保存结果
    print(f"\n💾 保存分析结果...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # 输出统计
    print(f"\n{'='*60}")
    print("📊 分析完成统计")
    print(f"{'='*60}")
    stats = result['metadata']['analysis_stats']
    print(f"   总文件数: {stats['total_files']}")
    print(f"   已分析: {stats['analyzed_files']}")
    print(f"   代码节点: {stats['total_nodes']}")
    print(f"   依赖关系: {stats['total_edges']}")
    print(f"   启动按钮: {len(result['behavior_metadata']['launch_buttons'])}")
    print(f"\n语言分布:")
    for lang, count in stats['languages'].items():
        print(f"   {lang}: {count} 文件")
    print(f"\n✅ 分析结果已保存到: {output_path}")
    print(f"📱 请在 AIFlow 前端加载此文件进行可视化\n")


if __name__ == '__main__':
    main()
