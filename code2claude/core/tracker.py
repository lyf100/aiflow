"""
变更跟踪器

跟踪项目文件变更、热点识别和影响分析
"""

import os
import json
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta

# 导入缓存模块
from .cache import get_cached_rglob, get_cached_hash, get_cached_line_count


class ChangeTracker:
    """变更跟踪器 - 识别代码热点和影响分析"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.output_dir = self.project_path / "claudeflow" / "tracking"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir = self.output_dir / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def create_snapshot(self, name: str = None) -> str:
        """
        创建项目结构快照

        Args:
            name: 快照名称，默认使用时间戳

        Returns:
            快照文件路径
        """
        if not name:
            name = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        snapshot_data = {
            "metadata": {
                "name": name,
                "timestamp": datetime.now().isoformat(),
                "project_path": str(self.project_path),
                "version": "1.0.0"
            },
            "files": {},
            "structure": {},
            "git_info": self._get_git_info()
        }

        # 收集文件信息
        snapshot_data["files"] = self._collect_file_info()
        snapshot_data["structure"] = self._collect_structure_info()

        # 保存快照
        snapshot_file = self.snapshots_dir / f"{name}.json"
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot_data, f, indent=2, ensure_ascii=False)

        return str(snapshot_file)

    def compare_snapshots(self, snapshot1_path: str, snapshot2_path: str) -> Dict[str, Any]:
        """
        比较两个快照的差异

        Args:
            snapshot1_path: 第一个快照路径
            snapshot2_path: 第二个快照路径

        Returns:
            差异比较结果
        """
        # 加载快照数据
        with open(snapshot1_path, 'r', encoding='utf-8') as f:
            snapshot1 = json.load(f)

        with open(snapshot2_path, 'r', encoding='utf-8') as f:
            snapshot2 = json.load(f)

        comparison = {
            "metadata": {
                "snapshot1": snapshot1["metadata"],
                "snapshot2": snapshot2["metadata"],
                "comparison_time": datetime.now().isoformat()
            },
            "file_changes": {
                "added": [],
                "deleted": [],
                "modified": [],
                "renamed": []
            },
            "structure_changes": {
                "directories_added": [],
                "directories_removed": [],
                "moved_files": []
            },
            "summary": {
                "total_changes": 0,
                "change_types": {}
            }
        }

        # 比较文件变化
        files1 = snapshot1.get("files", {})
        files2 = snapshot2.get("files", {})

        all_files = set(files1.keys()) | set(files2.keys())

        for file_path in all_files:
            if file_path not in files1:
                # 新增文件
                comparison["file_changes"]["added"].append({
                    "path": file_path,
                    "info": files2[file_path]
                })
            elif file_path not in files2:
                # 删除文件
                comparison["file_changes"]["deleted"].append({
                    "path": file_path,
                    "info": files1[file_path]
                })
            else:
                # 检查修改
                if files1[file_path].get("hash") != files2[file_path].get("hash"):
                    comparison["file_changes"]["modified"].append({
                        "path": file_path,
                        "before": files1[file_path],
                        "after": files2[file_path],
                        "size_change": files2[file_path].get("size", 0) - files1[file_path].get("size", 0)
                    })

        # 统计摘要
        comparison["summary"]["total_changes"] = (
            len(comparison["file_changes"]["added"]) +
            len(comparison["file_changes"]["deleted"]) +
            len(comparison["file_changes"]["modified"])
        )

        comparison["summary"]["change_types"] = {
            "added": len(comparison["file_changes"]["added"]),
            "deleted": len(comparison["file_changes"]["deleted"]),
            "modified": len(comparison["file_changes"]["modified"])
        }

        return comparison

    def identify_hotspots(self, days: int = 30) -> Dict[str, Any]:
        """
        识别代码热点

        Args:
            days: 分析的天数范围

        Returns:
            热点分析结果
        """
        hotspots = {
            "metadata": {
                "analysis_period_days": days,
                "timestamp": datetime.now().isoformat()
            },
            "frequency_hotspots": [],
            "complexity_hotspots": [],
            "size_hotspots": [],
            "error_prone_files": [],
            "recommendations": []
        }

        # 使用 Git 分析变更频率
        if self._is_git_repo():
            hotspots["frequency_hotspots"] = self._analyze_git_hotspots(days)

        # 分析复杂度热点
        hotspots["complexity_hotspots"] = self._analyze_complexity_hotspots()

        # 分析大小热点
        hotspots["size_hotspots"] = self._analyze_size_hotspots()

        # 生成建议
        hotspots["recommendations"] = self._generate_hotspot_recommendations(hotspots)

        return hotspots

    def analyze_impact(self, file_path: str, analysis_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        分析修改某文件会影响哪些模块

        Args:
            file_path: 要分析的文件路径
            analysis_data: 可选的分析数据

        Returns:
            影响分析结果
        """
        target_file = Path(file_path)
        if not target_file.exists():
            target_file = self.project_path / file_path

        impact_analysis = {
            "metadata": {
                "target_file": str(target_file.relative_to(self.project_path)),
                "timestamp": datetime.now().isoformat()
            },
            "direct_dependencies": [],
            "indirect_dependencies": [],
            "dependent_files": [],
            "impact_score": 0.0,
            "risk_level": "low"
        }

        # 直接依赖分析
        impact_analysis["direct_dependencies"] = self._find_direct_dependencies(target_file)

        # 反向依赖分析（谁依赖这个文件）
        impact_analysis["dependent_files"] = self._find_dependent_files(target_file)

        # 间接影响分析
        impact_analysis["indirect_dependencies"] = self._find_indirect_dependencies(
            target_file, analysis_data
        )

        # 计算影响分数
        impact_analysis["impact_score"] = self._calculate_impact_score(impact_analysis)
        impact_analysis["risk_level"] = self._determine_risk_level(impact_analysis["impact_score"])

        return impact_analysis

    def trace_function_calls(self, function_name: str, file_path: str = None) -> Dict[str, Any]:
        """
        追踪函数调用链

        Args:
            function_name: 函数名
            file_path: 文件路径（可选）

        Returns:
            调用链分析结果
        """
        trace_result = {
            "metadata": {
                "function_name": function_name,
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            },
            "call_chain": [],
            "callers": [],
            "callees": [],
            "complexity": {
                "depth": 0,
                "breadth": 0,
                "total_functions": 0
            }
        }

        # 查找函数定义
        function_locations = self._find_function_definitions(function_name, file_path)

        for location in function_locations:
            # 分析调用链
            chain = self._analyze_call_chain(function_name, location)
            trace_result["call_chain"].extend(chain)

        # 分析调用者和被调用者
        trace_result["callers"] = self._find_function_callers(function_name)
        trace_result["callees"] = self._find_function_callees(function_name, file_path)

        # 计算复杂度
        trace_result["complexity"] = self._calculate_call_complexity(trace_result)

        return trace_result

    def _collect_file_info(self) -> Dict[str, Any]:
        """收集文件信息"""
        file_info = {}

        for file_path in get_cached_rglob(self.project_path, "*"):
            if file_path.is_file() and not self._should_skip_file(file_path):
                rel_path = str(file_path.relative_to(self.project_path))

                try:
                    stat = file_path.stat()
                    file_info[rel_path] = {
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "hash": self._calculate_file_hash(file_path),
                        "extension": file_path.suffix.lower(),
                        "lines": self._count_lines(file_path) if self._is_text_file(file_path) else 0
                    }
                except (IOError, OSError) as e:
                    logging.warning(f"文件访问错误 {rel_path}: {e}")
                    file_info[rel_path] = {"error": f"File access error: {e}"}
                except PermissionError as e:
                    logging.warning(f"文件权限不足 {rel_path}: {e}")
                    file_info[rel_path] = {"error": f"Permission denied: {e}"}

        return file_info

    def _collect_structure_info(self) -> Dict[str, Any]:
        """收集结构信息"""
        structure = {
            "directories": [],
            "total_files": 0,
            "total_size": 0,
            "file_types": {}
        }

        for item in get_cached_rglob(self.project_path, "*"):
            if item.is_dir():
                rel_path = str(item.relative_to(self.project_path))
                structure["directories"].append(rel_path)
            elif item.is_file() and not self._should_skip_file(item):
                structure["total_files"] += 1
                try:
                    size = item.stat().st_size
                    structure["total_size"] += size

                    ext = item.suffix.lower()
                    structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1
                except (IOError, OSError):
                    # 文件访问错误,跳过
                    continue
                except PermissionError:
                    # 权限错误,跳过
                    continue

        return structure

    def _get_git_info(self) -> Dict[str, Any]:
        """获取 Git 信息"""
        if not self._is_git_repo():
            return {"available": False}

        try:
            # 获取当前分支
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.project_path,
                universal_newlines=True
            ).strip()

            # 获取最新提交
            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_path,
                universal_newlines=True
            ).strip()

            # 获取提交信息
            commit_info = subprocess.check_output(
                ["git", "log", "-1", "--pretty=format:%H|%an|%ad|%s"],
                cwd=self.project_path,
                universal_newlines=True
            ).strip()

            parts = commit_info.split('|')
            if len(parts) >= 4:
                return {
                    "available": True,
                    "branch": branch,
                    "commit": commit,
                    "author": parts[1],
                    "date": parts[2],
                    "message": parts[3]
                }

        except subprocess.CalledProcessError as e:
            logging.warning(f"Git命令执行失败: {e}")
            return {"available": False, "error": f"Git command failed: {e}"}
        except FileNotFoundError:
            logging.info("Git未安装或不在PATH中")
            return {"available": False, "error": "Git not found"}
        except Exception as e:
            logging.error(f"获取Git信息时发生未知错误: {type(e).__name__}: {e}")
            return {"available": False, "error": f"Unknown error: {type(e).__name__}: {e}"}

        return {"available": False}

    def _analyze_git_hotspots(self, days: int) -> List[Dict[str, Any]]:
        """使用 Git 分析变更热点"""
        hotspots = []

        try:
            # 获取指定天数内的变更统计
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            cmd = [
                "git", "log", f"--since={since_date}",
                "--name-only", "--pretty=format:", "--"
            ]

            output = subprocess.check_output(
                cmd, cwd=self.project_path, universal_newlines=True
            )

            # 统计文件变更频率
            file_changes = {}
            for line in output.split('\n'):
                if line.strip() and not line.startswith(' '):
                    file_changes[line.strip()] = file_changes.get(line.strip(), 0) + 1

            # 创建热点列表
            for file_path, change_count in sorted(
                file_changes.items(), key=lambda x: x[1], reverse=True
            ):
                if change_count > 1:  # 至少修改过2次
                    hotspots.append({
                        "file": file_path,
                        "change_count": change_count,
                        "score": change_count / days  # 平均每天变更次数
                    })

        except subprocess.CalledProcessError as e:
            logging.warning(f"Git热点分析失败: {e}")
        except FileNotFoundError:
            logging.info("Git未安装,跳过热点分析")
        except Exception as e:
            logging.error(f"Git热点分析时发生未知错误: {type(e).__name__}: {e}")

        return hotspots[:20]  # 返回前20个热点

    def _analyze_complexity_hotspots(self) -> List[Dict[str, Any]]:
        """分析复杂度热点"""
        hotspots = []

        # 简单的复杂度分析：基于文件大小和嵌套深度
        for file_path in get_cached_rglob(self.project_path, "*.py"):
            if self._should_skip_file(file_path):
                continue

            try:
                complexity_score = self._calculate_file_complexity(file_path)
                if complexity_score > 5:  # 复杂度阈值
                    hotspots.append({
                        "file": str(file_path.relative_to(self.project_path)),
                        "complexity_score": complexity_score,
                        "size": file_path.stat().st_size,
                        "lines": self._count_lines(file_path)
                    })
            except (IOError, OSError):
                # 文件访问错误,跳过
                continue
            except PermissionError:
                # 权限错误,跳过
                continue

        return sorted(hotspots, key=lambda x: x["complexity_score"], reverse=True)[:10]

    def _analyze_size_hotspots(self) -> List[Dict[str, Any]]:
        """分析大小热点"""
        hotspots = []

        for file_path in get_cached_rglob(self.project_path, "*"):
            if file_path.is_file() and not self._should_skip_file(file_path):
                try:
                    size = file_path.stat().st_size
                    if size > 50000:  # 大于50KB的文件
                        hotspots.append({
                            "file": str(file_path.relative_to(self.project_path)),
                            "size": size,
                            "lines": self._count_lines(file_path) if self._is_text_file(file_path) else 0
                        })
                except (IOError, OSError):
                    # 文件访问错误,跳过
                    continue
                except PermissionError:
                    # 权限错误,跳过
                    continue

        return sorted(hotspots, key=lambda x: x["size"], reverse=True)[:10]

    def _find_direct_dependencies(self, target_file: Path) -> List[str]:
        """查找直接依赖"""
        dependencies = []

        if not target_file.exists() or not self._is_text_file(target_file):
            return dependencies

        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 分析不同语言的导入语句
            if target_file.suffix == '.py':
                dependencies.extend(self._parse_python_imports(content))
            elif target_file.suffix in ['.js', '.ts']:
                dependencies.extend(self._parse_js_imports(content))

        except (IOError, OSError) as e:
            logging.warning(f"读取文件失败 {target_file}: {e}")
        except PermissionError as e:
            logging.warning(f"文件权限不足 {target_file}: {e}")
        except UnicodeDecodeError as e:
            logging.warning(f"文件编码错误 {target_file}: {e}")

        return dependencies

    def _find_dependent_files(self, target_file: Path) -> List[str]:
        """查找依赖于目标文件的文件"""
        dependents = []
        target_module = self._file_to_module_name(target_file)

        # 搜索项目中引用此模块的文件
        for file_path in get_cached_rglob(self.project_path, "*"):
            if (file_path.is_file() and
                file_path != target_file and
                self._is_text_file(file_path)):

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if self._file_references_module(content, target_module, file_path.suffix):
                        dependents.append(str(file_path.relative_to(self.project_path)))

                except (IOError, OSError):
                    # 文件访问错误,跳过
                    continue
                except PermissionError:
                    # 权限错误,跳过
                    continue
                except UnicodeDecodeError:
                    # 编码错误,跳过二进制文件
                    continue

        return dependents

    def _find_indirect_dependencies(self, target_file: Path, analysis_data: Dict[str, Any] = None) -> List[str]:
        """查找间接依赖"""
        # 基础实现，可以基于分析数据进行增强
        return []

    def _calculate_impact_score(self, impact_analysis: Dict[str, Any]) -> float:
        """计算影响分数"""
        direct_count = len(impact_analysis.get("direct_dependencies", []))
        dependent_count = len(impact_analysis.get("dependent_files", []))
        indirect_count = len(impact_analysis.get("indirect_dependencies", []))

        # 简单的加权计算
        score = (direct_count * 0.3) + (dependent_count * 0.5) + (indirect_count * 0.2)
        return round(score, 2)

    def _determine_risk_level(self, impact_score: float) -> str:
        """确定风险级别"""
        if impact_score >= 10:
            return "high"
        elif impact_score >= 5:
            return "medium"
        else:
            return "low"

    def _find_function_definitions(self, function_name: str, file_path: str = None) -> List[Dict[str, Any]]:
        """查找函数定义"""
        definitions = []

        search_files = [Path(file_path)] if file_path else get_cached_rglob(self.project_path, "*.py")

        for py_file in search_files:
            if not py_file.is_file():
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for line_num, line in enumerate(content.split('\n'), 1):
                    if f"def {function_name}(" in line:
                        definitions.append({
                            "file": str(py_file.relative_to(self.project_path)),
                            "line": line_num,
                            "definition": line.strip()
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

        return definitions

    def _find_function_callers(self, function_name: str) -> List[Dict[str, Any]]:
        """查找函数调用者"""
        callers = []

        for py_file in get_cached_rglob(self.project_path, "*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for line_num, line in enumerate(content.split('\n'), 1):
                    if f"{function_name}(" in line and not line.strip().startswith("def "):
                        callers.append({
                            "file": str(py_file.relative_to(self.project_path)),
                            "line": line_num,
                            "context": line.strip()
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

        return callers

    def _find_function_callees(self, function_name: str, file_path: str = None) -> List[str]:
        """查找函数调用的其他函数"""
        # 基础实现
        return []

    def _analyze_call_chain(self, function_name: str, location: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析调用链"""
        # 基础实现
        return [{"function": function_name, "location": location}]

    def _calculate_call_complexity(self, trace_result: Dict[str, Any]) -> Dict[str, Any]:
        """计算调用复杂度"""
        return {
            "depth": len(trace_result.get("call_chain", [])),
            "breadth": len(trace_result.get("callers", [])) + len(trace_result.get("callees", [])),
            "total_functions": len(set(
                [item.get("function", "") for item in trace_result.get("call_chain", [])]
            ))
        }

    def _calculate_file_complexity(self, file_path: Path) -> float:
        """计算文件复杂度（简单实现）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 简单的复杂度指标
            lines = content.split('\n')
            complexity = 0

            for line in lines:
                line = line.strip()
                # 增加复杂度的语句
                if any(keyword in line for keyword in ['if ', 'elif ', 'for ', 'while ', 'try:', 'except']):
                    complexity += 1
                # 嵌套增加复杂度
                if line.count('    ') > 2:  # 深度嵌套
                    complexity += 0.5

            return complexity

        except (IOError, OSError) as e:
            logging.warning(f"读取文件失败 {file_path}: {e}")
            return 0
        except PermissionError as e:
            logging.warning(f"文件权限不足 {file_path}: {e}")
            return 0
        except UnicodeDecodeError as e:
            logging.warning(f"文件编码错误 {file_path}: {e}")
            return 0

    def _parse_python_imports(self, content: str) -> List[str]:
        """解析 Python 导入"""
        imports = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                # 简化的导入解析
                if line.startswith('import '):
                    module = line[7:].split(' as ')[0].split(',')[0].strip()
                    imports.append(module)
                elif line.startswith('from '):
                    parts = line.split(' import ')
                    if len(parts) >= 2:
                        module = parts[0][5:].strip()
                        imports.append(module)
        return imports

    def _parse_js_imports(self, content: str) -> List[str]:
        """解析 JavaScript 导入"""
        imports = []
        for line in content.split('\n'):
            line = line.strip()
            if 'require(' in line or ('import ' in line and ' from ' in line):
                # 简化的导入解析
                # TODO: 更完整的 JS 导入解析
                pass
        return imports

    def _file_to_module_name(self, file_path: Path) -> str:
        """文件路径转模块名"""
        rel_path = file_path.relative_to(self.project_path)
        return str(rel_path).replace('/', '.').replace('.py', '')

    def _file_references_module(self, content: str, module_name: str, file_ext: str) -> bool:
        """检查文件是否引用了模块"""
        if file_ext == '.py':
            patterns = [
                f"import {module_name}",
                f"from {module_name}",
                f"import {module_name.split('.')[-1]}"
            ]
            return any(pattern in content for pattern in patterns)
        return False

    def _generate_hotspot_recommendations(self, hotspots: Dict[str, Any]) -> List[str]:
        """生成热点建议"""
        recommendations = []

        # 基于频率热点的建议
        freq_hotspots = hotspots.get("frequency_hotspots", [])
        if freq_hotspots:
            recommendations.append(
                f"考虑重构经常变更的文件：{', '.join([h['file'] for h in freq_hotspots[:3]])}"
            )

        # 基于复杂度热点的建议
        complex_hotspots = hotspots.get("complexity_hotspots", [])
        if complex_hotspots:
            recommendations.append(
                f"简化复杂文件：{', '.join([h['file'] for h in complex_hotspots[:3]])}"
            )

        # 基于大小热点的建议
        size_hotspots = hotspots.get("size_hotspots", [])
        if size_hotspots:
            recommendations.append(
                f"拆分大文件：{', '.join([h['file'] for h in size_hotspots[:3]])}"
            )

        return recommendations

    def _is_git_repo(self) -> bool:
        """检查是否为 Git 仓库"""
        return (self.project_path / ".git").exists()

    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = {
            '.git', '__pycache__', 'node_modules', '.pytest_cache',
            '.vscode', '.idea', '.DS_Store', 'Thumbs.db'
        }

        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)

    def _is_text_file(self, file_path: Path) -> bool:
        """判断是否为文本文件"""
        text_extensions = {
            '.py', '.js', '.ts', '.dart', '.java', '.cpp', '.c', '.cs',
            '.rb', '.php', '.go', '.rs', '.html', '.css', '.scss',
            '.md', '.txt', '.json', '.yaml', '.yml', '.xml'
        }
        return file_path.suffix.lower() in text_extensions

    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希 (使用缓存)"""
        return get_cached_hash(file_path)

    def _count_lines(self, file_path: Path) -> int:
        """统计文件行数 (使用缓存)"""
        return get_cached_line_count(file_path)