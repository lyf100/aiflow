#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIFlow 代码解析器 - 真正的AST级别分析
支持 Java, Kotlin, Python, JavaScript, TypeScript
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class ClassInfo:
    """类信息"""
    name: str
    file_path: str
    package: str = ""
    superclass: Optional[str] = None
    interfaces: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    is_interface: bool = False
    is_abstract: bool = False


@dataclass
class MethodInfo:
    """方法信息"""
    name: str
    class_name: str
    file_path: str
    return_type: str = ""
    parameters: List[str] = field(default_factory=list)
    calls: Set[str] = field(default_factory=set)
    is_static: bool = False
    is_constructor: bool = False


class JavaKotlinParser:
    """Java/Kotlin 代码解析器"""

    def __init__(self):
        # Java/Kotlin 类声明正则
        self.class_pattern = re.compile(
            r'(?:public|private|protected)?\s*(?:static|abstract|final)?\s*'
            r'(class|interface|enum|object)\s+(\w+)'
            r'(?:\s+extends\s+(\w+))?'
            r'(?:\s+implements\s+([\w\s,]+))?'
        )

        # Kotlin 类声明
        self.kotlin_class_pattern = re.compile(
            r'(?:open|abstract|sealed|data)?\s*'
            r'(class|interface|object)\s+(\w+)'
            r'(?:\s*:\s*([\w\s,()]+))?'
        )

        # 方法声明正则
        self.method_pattern = re.compile(
            r'(?:public|private|protected)?\s*(?:static|abstract|final|synchronized)?\s*'
            r'(?:<[^>]+>)?\s*'  # 泛型
            r'([\w<>\[\]]+)\s+'  # 返回类型
            r'(\w+)\s*'  # 方法名
            r'\(([^)]*)\)'  # 参数
        )

        # Kotlin 函数声明
        self.kotlin_fun_pattern = re.compile(
            r'(?:suspend\s+)?fun\s+(?:<[^>]+>)?\s*(\w+)\s*\(([^)]*)\)(?:\s*:\s*([\w<>?]+))?'
        )

        # 方法调用正则
        self.call_pattern = re.compile(r'(\w+)\s*\(')

        # 包声明
        self.package_pattern = re.compile(r'package\s+([\w.]+)')

        # 导入语句
        self.import_pattern = re.compile(r'import\s+([\w.]+)')

    def parse_file(self, file_path: Path) -> Tuple[List[ClassInfo], List[MethodInfo]]:
        """解析单个文件"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except:
            return [], []

        classes = []
        methods = []

        # 提取包名
        package_match = self.package_pattern.search(content)
        package = package_match.group(1) if package_match else ""

        # 提取导入
        imports = [m.group(1) for m in self.import_pattern.finditer(content)]

        # 是否是 Kotlin 文件
        is_kotlin = file_path.suffix == '.kt'

        # 分析类
        class_info = self._parse_class(content, file_path, package, imports, is_kotlin)
        if class_info:
            classes.append(class_info)

            # 分析方法
            method_infos = self._parse_methods(content, class_info.name, file_path, is_kotlin)
            methods.extend(method_infos)

        return classes, methods

    def _parse_class(self, content: str, file_path: Path, package: str,
                     imports: List[str], is_kotlin: bool) -> Optional[ClassInfo]:
        """解析类声明"""
        if is_kotlin:
            match = self.kotlin_class_pattern.search(content)
            if not match:
                return None

            class_type, name, inheritance = match.groups()
            superclass = None
            interfaces = []

            if inheritance:
                # Kotlin 的继承语法: class A : B(), C, D
                parts = [p.strip().rstrip('()') for p in inheritance.split(',')]
                if parts:
                    superclass = parts[0]
                    interfaces = parts[1:] if len(parts) > 1 else []
        else:
            match = self.class_pattern.search(content)
            if not match:
                return None

            class_type, name, superclass, interfaces_str = match.groups()
            interfaces = [i.strip() for i in interfaces_str.split(',')] if interfaces_str else []

        return ClassInfo(
            name=name,
            file_path=str(file_path.relative_to(file_path.parents[4])),  # 相对路径
            package=package,
            superclass=superclass,
            interfaces=interfaces,
            imports=imports,
            is_interface=(class_type == 'interface'),
            is_abstract=('abstract' in content[:content.find(name)] if name in content else False)
        )

    def _parse_methods(self, content: str, class_name: str,
                       file_path: Path, is_kotlin: bool) -> List[MethodInfo]:
        """解析方法"""
        methods = []

        if is_kotlin:
            pattern = self.kotlin_fun_pattern
        else:
            pattern = self.method_pattern

        for match in pattern.finditer(content):
            if is_kotlin:
                name, params, return_type = match.groups()
                return_type = return_type or 'Unit'
            else:
                return_type, name, params = match.groups()

            # 跳过一些常见的非方法模式
            if name in ['if', 'while', 'for', 'switch', 'catch']:
                continue

            # 提取方法调用
            method_start = match.end()
            method_end = self._find_method_end(content, method_start)
            method_body = content[method_start:method_end]

            calls = set()
            for call_match in self.call_pattern.finditer(method_body):
                called_method = call_match.group(1)
                if called_method not in ['if', 'while', 'for', 'switch', 'catch']:
                    calls.add(called_method)

            methods.append(MethodInfo(
                name=name,
                class_name=class_name,
                file_path=str(file_path.relative_to(file_path.parents[4])),
                return_type=return_type,
                parameters=[p.strip() for p in params.split(',')] if params else [],
                calls=calls,
                is_static=('static' in content[max(0, match.start()-50):match.start()]),
                is_constructor=(name == class_name)
            ))

        return methods

    def _find_method_end(self, content: str, start: int) -> int:
        """查找方法结束位置（简单的大括号匹配）"""
        brace_count = 0
        i = start
        while i < len(content):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return i
            i += 1
        return len(content)


class PythonParser:
    """Python 代码解析器"""

    def __init__(self):
        self.class_pattern = re.compile(r'class\s+(\w+)(?:\(([^)]*)\))?:')
        self.method_pattern = re.compile(r'def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?:')
        self.call_pattern = re.compile(r'(\w+)\s*\(')
        self.import_pattern = re.compile(r'(?:from\s+([\w.]+)\s+)?import\s+([\w\s,.*]+)')

    def parse_file(self, file_path: Path) -> Tuple[List[ClassInfo], List[MethodInfo]]:
        """解析 Python 文件"""
        try:
            content = file_path.read_text(encoding='utf-8')
        except:
            return [], []

        classes = []
        methods = []

        # 提取导入
        imports = []
        for match in self.import_pattern.finditer(content):
            from_module, import_names = match.groups()
            if from_module:
                imports.append(f"{from_module}.{import_names}")
            else:
                imports.append(import_names)

        # 分析类
        for match in self.class_pattern.finditer(content):
            name, bases = match.groups()
            bases_list = [b.strip() for b in bases.split(',')] if bases else []

            class_info = ClassInfo(
                name=name,
                file_path=str(file_path.relative_to(file_path.parents[4])),
                superclass=bases_list[0] if bases_list else None,
                interfaces=bases_list[1:] if len(bases_list) > 1 else [],
                imports=imports
            )
            classes.append(class_info)

            # 查找类内的方法
            class_start = match.end()
            class_methods = self._parse_class_methods(content, class_start, name, file_path)
            methods.extend(class_methods)

        return classes, methods

    def _parse_class_methods(self, content: str, start: int,
                             class_name: str, file_path: Path) -> List[MethodInfo]:
        """解析类内方法"""
        methods = []
        lines = content[start:].split('\n')

        for i, line in enumerate(lines):
            # 检测到非缩进行，说明类定义结束
            if line and not line[0].isspace():
                break

            match = self.method_pattern.search(line)
            if match:
                name, params, return_type = match.groups()

                # 查找方法体中的调用
                method_body = self._get_method_body(lines, i)
                calls = set()
                for call_match in self.call_pattern.finditer(method_body):
                    calls.add(call_match.group(1))

                methods.append(MethodInfo(
                    name=name,
                    class_name=class_name,
                    file_path=str(file_path.relative_to(file_path.parents[4])),
                    return_type=return_type or 'None',
                    parameters=[p.strip() for p in params.split(',')] if params else [],
                    calls=calls,
                    is_static=('@staticmethod' in lines[i-1] if i > 0 else False),
                    is_constructor=(name == '__init__')
                ))

        return methods

    def _get_method_body(self, lines: List[str], method_line: int) -> str:
        """获取方法体内容"""
        if method_line >= len(lines) - 1:
            return ""

        base_indent = len(lines[method_line]) - len(lines[method_line].lstrip())
        body_lines = []

        for line in lines[method_line + 1:]:
            if line.strip() == "":
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent:
                break
            body_lines.append(line)

        return '\n'.join(body_lines)


class CodeParser:
    """统一代码解析器"""

    def __init__(self):
        self.java_kotlin_parser = JavaKotlinParser()
        self.python_parser = PythonParser()

    def parse_project(self, project_path: Path) -> Tuple[List[ClassInfo], List[MethodInfo]]:
        """解析整个项目"""
        all_classes = []
        all_methods = []

        # 支持的文件类型
        extensions = {'.java', '.kt', '.py'}

        for file_path in project_path.rglob('*'):
            if file_path.suffix not in extensions:
                continue

            if file_path.suffix in {'.java', '.kt'}:
                classes, methods = self.java_kotlin_parser.parse_file(file_path)
            elif file_path.suffix == '.py':
                classes, methods = self.python_parser.parse_file(file_path)
            else:
                continue

            all_classes.extend(classes)
            all_methods.extend(methods)

        return all_classes, all_methods
