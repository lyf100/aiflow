"""
Code2Claude MCP Server

基于 Model Context Protocol 的代码分析服务器
为 AI 工具提供标准化的项目分析能力
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.stdio import stdio_server
except ImportError:
    raise ImportError(
        "MCP SDK 未安装。请运行: pip install mcp[cli]>=1.4.0"
    )

from core.analyzer import CodeAnalyzer
from core.mapper import ProjectMapper
from core.grapher import DependencyGrapher
from core.tracker import ChangeTracker
from core.exporter import DataExporter

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 MCP 服务器实例
mcp = FastMCP("Code2Claude")


@mcp.tool()
def analyze_project(
    project_path: str,
    languages: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    分析项目代码结构

    Args:
        project_path: 项目根目录路径
        languages: 要分析的语言列表，如 ["py", "js"]，默认自动检测

    Returns:
        包含代码分析结果的字典，包括:
        - languages: 各语言的分析结果
        - structure: 项目结构信息
        - dependencies: 依赖关系
        - hotspots: 代码热点
        - metrics: 项目指标
    """
    try:
        analyzer = CodeAnalyzer(project_path)
        result = analyzer.analyze_project(languages)

        return {
            "success": True,
            "data": result,
            "message": f"Successfully analyzed project at {project_path}"
        }
    except Exception as e:
        logger.error(f"项目分析失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to analyze project: {e}"
        }


@mcp.tool()
def map_project_structure(project_path: str) -> Dict[str, Any]:
    """
    生成项目结构映射

    Args:
        project_path: 项目根目录路径

    Returns:
        项目结构映射，包括:
        - metadata: 项目元数据
        - overview: 统计概览
        - directory_tree: 目录树结构
        - file_index: 文件索引
        - patterns: 文件模式识别
    """
    try:
        mapper = ProjectMapper(project_path)
        result = mapper.map_project_structure()

        return {
            "success": True,
            "data": result,
            "message": f"Successfully mapped project structure at {project_path}"
        }
    except Exception as e:
        logger.error(f"项目结构映射失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to map project structure: {e}"
        }


@mcp.tool()
def generate_dependency_graph(
    project_path: str,
    graph_type: str = "module"
) -> Dict[str, Any]:
    """
    生成依赖关系图

    Args:
        project_path: 项目根目录路径
        graph_type: 图类型，可选 "module", "class", "function"

    Returns:
        依赖关系图数据和生成的文件路径
    """
    try:
        grapher = DependencyGrapher(project_path)
        graph_file = grapher.generate_dependency_graph(graph_type)

        return {
            "success": True,
            "data": {
                "graph_file": graph_file,
                "graph_type": graph_type
            },
            "message": f"Dependency graph generated at {graph_file}"
        }
    except Exception as e:
        logger.error(f"依赖图生成失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate dependency graph: {e}"
        }


@mcp.tool()
def identify_code_hotspots(project_path: str) -> Dict[str, Any]:
    """
    识别代码热点

    识别高频修改、高复杂度、过大的文件

    Args:
        project_path: 项目根目录路径

    Returns:
        代码热点列表，包括:
        - git_hotspots: Git高频修改文件
        - complexity_hotspots: 高复杂度文件
        - size_hotspots: 大文件列表
    """
    try:
        tracker = ChangeTracker(project_path)
        hotspots = tracker.identify_hotspots()

        return {
            "success": True,
            "data": hotspots,
            "message": f"Code hotspots identified for {project_path}"
        }
    except Exception as e:
        logger.error(f"热点识别失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to identify hotspots: {e}"
        }


@mcp.tool()
def analyze_file_impact(
    project_path: str,
    file_path: str
) -> Dict[str, Any]:
    """
    分析文件修改影响

    Args:
        project_path: 项目根目录路径
        file_path: 要分析的文件相对路径

    Returns:
        影响分析结果，包括:
        - file: 文件信息
        - direct_dependencies: 直接依赖
        - dependent_files: 依赖此文件的文件列表
        - impact_level: 影响级别 (high/medium/low)
    """
    try:
        tracker = ChangeTracker(project_path)
        impact = tracker.analyze_impact([file_path])

        return {
            "success": True,
            "data": impact,
            "message": f"Impact analysis completed for {file_path}"
        }
    except Exception as e:
        logger.error(f"影响分析失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to analyze impact: {e}"
        }


@mcp.tool()
def trace_function_calls(
    project_path: str,
    function_name: str,
    file_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    追踪函数调用链

    Args:
        project_path: 项目根目录路径
        function_name: 要追踪的函数名
        file_path: 可选的文件路径，限制搜索范围

    Returns:
        函数调用链信息，包括:
        - function: 函数名
        - definitions: 函数定义位置列表
        - callers: 调用者列表
        - call_chain: 调用链路径
    """
    try:
        tracker = ChangeTracker(project_path)
        trace = tracker.trace_function_calls(function_name, file_path)

        return {
            "success": True,
            "data": trace,
            "message": f"Function call trace completed for {function_name}"
        }
    except Exception as e:
        logger.error(f"函数追踪失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to trace function calls: {e}"
        }


@mcp.tool()
def create_project_snapshot(
    project_path: str,
    snapshot_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建项目快照

    Args:
        project_path: 项目根目录路径
        snapshot_name: 快照名称，默认使用时间戳

    Returns:
        快照文件路径和元数据
    """
    try:
        tracker = ChangeTracker(project_path)
        snapshot_file = tracker.create_snapshot(snapshot_name)

        return {
            "success": True,
            "data": {
                "snapshot_file": snapshot_file,
                "snapshot_name": snapshot_name or "auto"
            },
            "message": f"Project snapshot created at {snapshot_file}"
        }
    except Exception as e:
        logger.error(f"快照创建失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create snapshot: {e}"
        }


@mcp.tool()
def compare_snapshots(
    project_path: str,
    snapshot1: str,
    snapshot2: str
) -> Dict[str, Any]:
    """
    比较两个项目快照

    Args:
        project_path: 项目根目录路径
        snapshot1: 第一个快照名称
        snapshot2: 第二个快照名称

    Returns:
        快照差异信息，包括:
        - added_files: 新增文件
        - removed_files: 删除文件
        - modified_files: 修改文件
        - statistics: 变更统计
    """
    try:
        tracker = ChangeTracker(project_path)
        diff = tracker.compare_snapshots(snapshot1, snapshot2)

        return {
            "success": True,
            "data": diff,
            "message": f"Snapshot comparison completed: {snapshot1} vs {snapshot2}"
        }
    except Exception as e:
        logger.error(f"快照比较失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to compare snapshots: {e}"
        }


@mcp.tool()
def export_analysis_data(
    project_path: str,
    format: str = "json",
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    导出分析数据

    Args:
        project_path: 项目根目录路径
        format: 导出格式，可选 "json", "markdown", "html", "csv"
        output_path: 输出文件路径，默认在项目 code2claude 目录下

    Returns:
        导出文件的路径列表
    """
    try:
        # 先进行完整分析
        analyzer = CodeAnalyzer(project_path)
        mapper = ProjectMapper(project_path)
        tracker = ChangeTracker(project_path)

        analysis_data = analyzer.analyze_project()
        structure_data = mapper.map_project_structure()
        hotspots_data = tracker.identify_hotspots()

        # 导出数据
        exporter = DataExporter(project_path)

        if format == "json":
            files = exporter.export_to_json({
                "analysis": analysis_data,
                "structure": structure_data,
                "hotspots": hotspots_data
            })
        elif format == "markdown":
            files = exporter.export_to_markdown(
                analysis_data,
                structure_data,
                hotspots_data
            )
        elif format == "html":
            files = exporter.export_to_html(
                analysis_data,
                structure_data
            )
        else:
            raise ValueError(f"Unsupported format: {format}")

        return {
            "success": True,
            "data": {"files": files, "format": format},
            "message": f"Analysis data exported in {format} format"
        }
    except Exception as e:
        logger.error(f"数据导出失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to export data: {e}"
        }


# 服务器主入口
def main():
    """启动 MCP 服务器"""
    logger.info("Starting Code2Claude MCP Server...")

    # 使用 stdio transport 运行服务器
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()