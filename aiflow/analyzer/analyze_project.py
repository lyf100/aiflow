#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIFlow 项目分析器 v2.0 - 真正的代码结构分析
"""

import sys
import io
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

# Windows 控制台编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from code_parser import CodeParser, ClassInfo, MethodInfo


class ProjectAnalyzer:
    """项目分析器"""

    def __init__(self, project_path: str, project_name: Optional[str] = None):
        self.project_path = Path(project_path)
        self.project_name = project_name or self.project_path.name

        self.parser = CodeParser()

        # 分析结果
        self.classes: List[ClassInfo] = []
        self.methods: List[MethodInfo] = []

        # JSON 输出结构
        self.nodes: List[Dict] = []
        self.edges: List[Dict] = []
        self.launch_buttons: List[Dict] = []
        self.traceable_units: List[Dict] = []

        # ID 生成器
        self.node_id_counter = 0
        self.edge_id_counter = 0
        self.button_id_counter = 0
        self.unit_id_counter = 0

        # 类名到节点ID的映射
        self.class_to_node_id: Dict[str, str] = {}
        self.method_to_node_id: Dict[str, str] = {}

    def analyze(self) -> Dict:
        """执行分析"""
        print(f"🔍 分析项目: {self.project_name}")
        print(f"📂 路径: {self.project_path}")
        print()

        # 1. 解析代码
        print("⏳ 解析代码文件...")
        self.classes, self.methods = self.parser.parse_project(self.project_path)
        print(f"✅ 找到 {len(self.classes)} 个类，{len(self.methods)} 个方法")
        print()

        # 2. 构建代码结构图
        print("⏳ 构建代码结构...")
        self._build_code_structure()
        print(f"✅ 生成 {len(self.nodes)} 个节点，{len(self.edges)} 条关系")
        print()

        # 3. 生成启动按钮
        print("⏳ 生成启动按钮...")
        self._generate_launch_buttons()
        print(f"✅ 生成 {len(self.launch_buttons)} 个启动按钮")
        print()

        # 4. 生成可追踪单元
        print("⏳ 生成可追踪单元...")
        self._generate_traceable_units()
        print(f"✅ 生成 {len(self.traceable_units)} 个可追踪单元")
        print()

        # 5. 生成项目类型
        project_type = self._detect_project_type()
        print(f"📦 项目类型: {project_type}")
        print()

        # 构建输出 JSON
        result = {
            "metadata": {
                "project_name": self.project_name,
                "project_type": project_type,
                "analysis_timestamp": datetime.now().isoformat(),
                "protocol_version": "1.0.0",
                "analyzer_version": "2.0.0"
            },
            "code_structure": {
                "nodes": self.nodes,
                "edges": self.edges
            },
            "behavior_metadata": {
                "launch_buttons": self.launch_buttons
            },
            "execution_trace": {
                "traceable_units": self.traceable_units
            }
        }

        return result

    def _build_code_structure(self):
        """构建代码结构图"""
        # 1. 创建系统级节点（整个项目）
        system_node_id = self._gen_node_id()
        self.nodes.append({
            "id": system_node_id,
            "name": self.project_name,
            "type": "class",
            "stereotype": "system",
            "file_path": str(self.project_path)
        })

        # 2. 按包分组类（模块级）
        packages = defaultdict(list)
        for cls in self.classes:
            package = cls.package or "default"
            packages[package].append(cls)

        # 为每个包创建模块节点
        package_to_node_id = {}
        for package, classes_in_package in packages.items():
            if len(classes_in_package) > 0:
                module_node_id = self._gen_node_id()
                self.nodes.append({
                    "id": module_node_id,
                    "name": package,
                    "type": "class",
                    "stereotype": "module",
                    "file_path": package.replace('.', '/')
                })
                package_to_node_id[package] = module_node_id

                # 模块 contains 系统
                self.edges.append({
                    "id": self._gen_edge_id(),
                    "source": system_node_id,
                    "target": module_node_id,
                    "type": "contains"
                })

        # 3. 创建类节点（组件级）
        for cls in self.classes:
            class_node_id = self._gen_node_id()
            self.class_to_node_id[cls.name] = class_node_id

            self.nodes.append({
                "id": class_node_id,
                "name": cls.name,
                "type": "class",
                "stereotype": "component",
                "file_path": cls.file_path
            })

            # 类属于模块
            package = cls.package or "default"
            if package in package_to_node_id:
                self.edges.append({
                    "id": self._gen_edge_id(),
                    "source": package_to_node_id[package],
                    "target": class_node_id,
                    "type": "contains"
                })

            # 继承关系
            if cls.superclass:
                superclass_id = self.class_to_node_id.get(cls.superclass)
                if superclass_id:
                    self.edges.append({
                        "id": self._gen_edge_id(),
                        "source": class_node_id,
                        "target": superclass_id,
                        "type": "inherits"
                    })

            # 接口实现关系
            for interface in cls.interfaces:
                interface_id = self.class_to_node_id.get(interface)
                if interface_id:
                    self.edges.append({
                        "id": self._gen_edge_id(),
                        "source": class_node_id,
                        "target": interface_id,
                        "type": "implements"
                    })

        # 4. 创建方法节点（函数级）
        for method in self.methods:
            method_key = f"{method.class_name}.{method.name}"
            method_node_id = self._gen_node_id()
            self.method_to_node_id[method_key] = method_node_id

            self.nodes.append({
                "id": method_node_id,
                "name": method.name,
                "type": "function",
                "stereotype": "function",
                "file_path": method.file_path,
                "parent_class_id": self.class_to_node_id.get(method.class_name)
            })

            # 方法属于类
            class_id = self.class_to_node_id.get(method.class_name)
            if class_id:
                self.edges.append({
                    "id": self._gen_edge_id(),
                    "source": class_id,
                    "target": method_node_id,
                    "type": "contains"
                })

        # 5. 创建方法调用关系
        for method in self.methods:
            method_key = f"{method.class_name}.{method.name}"
            source_id = self.method_to_node_id.get(method_key)

            if not source_id:
                continue

            for called_method in method.calls:
                # 尝试在当前类中查找
                target_key = f"{method.class_name}.{called_method}"
                target_id = self.method_to_node_id.get(target_key)

                # 如果找不到，尝试在所有类中查找
                if not target_id:
                    for other_method in self.methods:
                        if other_method.name == called_method:
                            target_key = f"{other_method.class_name}.{other_method.name}"
                            target_id = self.method_to_node_id.get(target_key)
                            if target_id:
                                break

                if target_id and source_id != target_id:
                    self.edges.append({
                        "id": self._gen_edge_id(),
                        "source": source_id,
                        "target": target_id,
                        "type": "calls"
                    })

    def _generate_launch_buttons(self):
        """生成启动按钮"""
        # 为每个包生成一个 macro 按钮
        packages = set(cls.package for cls in self.classes if cls.package)

        for package in sorted(packages):
            button_id = self._gen_button_id()
            self.launch_buttons.append({
                "id": button_id,
                "name": f"分析 {package} 模块",
                "type": "macro",
                "level": "module",
                "description": f"分析 {package} 包中的所有类和方法调用",
                "parent_button_id": None,
                "child_button_ids": [],
                "traceable_unit_id": None,
                "ai_confidence": 0.85,
                "estimated_duration_seconds": 30
            })

        # 为主要的类生成 micro 按钮
        main_classes = [cls for cls in self.classes if not cls.is_interface][:10]
        for cls in main_classes:
            button_id = self._gen_button_id()
            self.launch_buttons.append({
                "id": button_id,
                "name": f"执行 {cls.name}",
                "type": "micro",
                "level": "component",
                "description": f"追踪 {cls.name} 类的执行流程",
                "parent_button_id": None,
                "child_button_ids": [],
                "traceable_unit_id": None,
                "ai_confidence": 0.75,
                "estimated_duration_seconds": 15
            })

    def _generate_traceable_units(self):
        """生成可追踪单元"""
        # 为每个方法生成一个可追踪单元
        for method in self.methods[:20]:  # 限制数量
            unit_id = self._gen_unit_id()
            self.traceable_units.append({
                "id": unit_id,
                "name": f"{method.class_name}.{method.name}",
                "type": "function",
                "entry_point_node_id": self.method_to_node_id.get(f"{method.class_name}.{method.name}"),
                "execution_steps": []
            })

    def _detect_project_type(self) -> str:
        """检测项目类型"""
        if (self.project_path / 'build.gradle').exists() or (self.project_path / 'build.gradle.kts').exists():
            return 'Java/Kotlin (Gradle)'
        elif (self.project_path / 'pom.xml').exists():
            return 'Java (Maven)'
        elif (self.project_path / 'setup.py').exists() or (self.project_path / 'pyproject.toml').exists():
            return 'Python'
        elif (self.project_path / 'package.json').exists():
            return 'JavaScript/TypeScript (Node.js)'
        else:
            return 'Unknown'

    def _gen_node_id(self) -> str:
        self.node_id_counter += 1
        return f"node_{self.node_id_counter}"

    def _gen_edge_id(self) -> str:
        self.edge_id_counter += 1
        return f"edge_{self.edge_id_counter}"

    def _gen_button_id(self) -> str:
        self.button_id_counter += 1
        return f"btn_{self.button_id_counter}"

    def _gen_unit_id(self) -> str:
        self.unit_id_counter += 1
        return f"unit_{self.unit_id_counter}"


def main():
    if len(sys.argv) < 2:
        print("用法: python analyze_project.py <项目路径> [项目名称]")
        sys.exit(1)

    project_path = sys.argv[1]
    project_name = sys.argv[2] if len(sys.argv) > 2 else None

    analyzer = ProjectAnalyzer(project_path, project_name)
    result = analyzer.analyze()

    # 输出 JSON
    output_file = Path(__file__).parent / f"{analyzer.project_name.lower()}-analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 分析完成！输出文件: {output_file}")
    print(f"📊 统计:")
    print(f"   - 类: {len(analyzer.classes)}")
    print(f"   - 方法: {len(analyzer.methods)}")
    print(f"   - 节点: {len(analyzer.nodes)}")
    print(f"   - 关系: {len(analyzer.edges)}")
    print(f"   - 按钮: {len(analyzer.launch_buttons)}")


if __name__ == '__main__':
    main()
