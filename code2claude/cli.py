"""
Code2Claude 命令行接口

基于 code2flow 的增强代码分析命令
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any

from .core.analyzer import CodeAnalyzer
from .core.mapper import ProjectMapper
from .core.grapher import DependencyGrapher
from .core.tracker import ChangeTracker
from .core.exporter import DataExporter


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Code2Claude - 基于 code2flow 的增强代码分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  code2claude /cc:map                    # 映射项目结构
  code2claude /cc:sync                   # 同步项目变化
  code2claude /cc:context                # 生成 Claude 上下文
  code2claude /cc:graph                  # 生成依赖关系图
  code2claude /cc:hotspot                # 识别代码热点
  code2claude /cc:impact file.py         # 影响分析
  code2claude /cc:trace function_name    # 追踪函数调用
  code2claude /cc:snapshot               # 创建项目快照
  code2claude /cc:diff snap1 snap2       # 对比快照差异
  code2claude /cc:export --format json  # 导出分析数据
        """
    )

    parser.add_argument(
        'command',
        help='要执行的命令'
    )

    parser.add_argument(
        'args',
        nargs='*',
        help='命令参数'
    )

    parser.add_argument(
        '-p', '--project-path',
        default='.',
        help='项目路径 (默认: 当前目录)'
    )

    parser.add_argument(
        '--format',
        choices=['json', 'markdown', 'html', 'csv'],
        default='json',
        help='输出格式'
    )

    parser.add_argument(
        '--output',
        help='输出文件路径'
    )

    parser.add_argument(
        '--language',
        choices=['py', 'js', 'rb', 'php'],
        help='指定分析的编程语言'
    )

    parser.add_argument(
        '--depth',
        type=int,
        default=3,
        help='分析深度 (默认: 3)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='热点分析的天数范围 (默认: 30)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='详细输出'
    )

    return parser


def execute_map_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行映射命令"""
    print("正在映射项目结构...")

    mapper = ProjectMapper(project_path)

    # 生成结构映射
    structure_map = mapper.map_project_structure()
    print(f"项目结构映射完成")

    # 生成代码映射
    code_map = mapper.map_code_structure()
    print(f"代码结构映射完成")

    # 生成交互式地图
    interactive_map = mapper.generate_interactive_map()
    print(f"交互式地图生成: {interactive_map}")

    # 保存映射文件
    saved_files = mapper.save_maps()
    print("映射文件已保存:")
    for map_type, file_path in saved_files.items():
        print(f"   {map_type}: {file_path}")

    return {
        "structure_map": structure_map,
        "code_map": code_map,
        "saved_files": saved_files
    }


def execute_sync_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行同步命令"""
    print("正在同步项目变化...")

    analyzer = CodeAnalyzer(project_path)

    # 重新分析项目
    analysis_result = analyzer.analyze_project()
    print(f"项目分析完成")

    # 保存分析结果
    output_file = analyzer.save_analysis()
    print(f"分析结果已保存: {output_file}")

    # 更新映射
    mapper = ProjectMapper(project_path)
    mapper.save_maps()
    print(f"项目映射已更新")

    return {
        "analysis_result": analysis_result,
        "output_file": output_file
    }


def execute_context_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行上下文生成命令"""
    print("📝 正在生成 Claude 上下文...")

    analyzer = CodeAnalyzer(project_path)
    analysis_result = analyzer.analyze_project()

    # 生成专门用于 Claude 的结构化上下文
    context_data = {
        "project_summary": {
            "name": Path(project_path).name,
            "languages": list(analysis_result.get("languages", {}).keys()),
            "total_files": analysis_result.get("metrics", {}).get("total_files", 0),
            "code_lines": analysis_result.get("metrics", {}).get("code_lines", 0)
        },
        "structure_overview": analysis_result.get("structure", {}),
        "key_components": [],
        "dependencies": analysis_result.get("dependencies", {}),
        "context_for_claude": {
            "project_type": _infer_project_type(analysis_result),
            "main_languages": list(analysis_result.get("languages", {}).keys())[:3],
            "complexity_level": _assess_complexity(analysis_result),
            "recommendations": _generate_context_recommendations(analysis_result)
        }
    }

    # 提取关键组件
    for lang, lang_data in analysis_result.get("languages", {}).items():
        functions = lang_data.get("functions", [])
        classes = lang_data.get("classes", [])

        # 添加重要的函数和类
        context_data["key_components"].extend([
            {"type": "function", "name": func["name"], "file": func["file"], "language": lang}
            for func in functions[:5]  # 前5个函数
        ])
        context_data["key_components"].extend([
            {"type": "class", "name": cls["name"], "file": cls["file"], "language": lang}
            for cls in classes[:5]  # 前5个类
        ])

    # 保存上下文文件
    output_dir = Path(project_path) / "code2claude"
    output_dir.mkdir(exist_ok=True)
    context_file = output_dir / "context.json"

    with open(context_file, 'w', encoding='utf-8') as f:
        json.dump(context_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Claude 上下文已生成: {context_file}")

    return {
        "context_data": context_data,
        "context_file": str(context_file)
    }


def execute_graph_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行图表生成命令"""
    print("📊 正在生成依赖关系图...")

    grapher = DependencyGrapher(project_path)

    # 生成所有类型的图
    generated_graphs = grapher.generate_all_graphs()

    print("✅ 依赖关系图生成完成:")
    for graph_type, file_path in generated_graphs.items():
        print(f"   {graph_type}: {file_path}")

    return {
        "generated_graphs": generated_graphs
    }


def execute_hotspot_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行热点识别命令"""
    print("🔥 正在识别代码热点...")

    tracker = ChangeTracker(project_path)
    days = options.get('days', 30)

    # 识别热点
    hotspots = tracker.identify_hotspots(days)

    print(f"✅ 代码热点识别完成 (分析了最近 {days} 天)")

    # 显示摘要
    freq_hotspots = hotspots.get("frequency_hotspots", [])
    if freq_hotspots:
        print(f"   频率热点: {len(freq_hotspots)} 个文件")

    complex_hotspots = hotspots.get("complexity_hotspots", [])
    if complex_hotspots:
        print(f"   复杂度热点: {len(complex_hotspots)} 个文件")

    size_hotspots = hotspots.get("size_hotspots", [])
    if size_hotspots:
        print(f"   大小热点: {len(size_hotspots)} 个文件")

    # 保存热点分析结果
    output_file = Path(project_path) / "code2claude" / "tracking" / "hotspots.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hotspots, f, indent=2, ensure_ascii=False)

    print(f"✅ 热点分析结果已保存: {output_file}")

    return {
        "hotspots": hotspots,
        "output_file": str(output_file)
    }


def execute_impact_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行影响分析命令"""
    if not args:
        print("❌ 错误: 请指定要分析的文件路径")
        return {"error": "Missing file path"}

    file_path = args[0]
    print(f"🎯 正在分析文件影响: {file_path}")

    tracker = ChangeTracker(project_path)

    # 执行影响分析
    impact_analysis = tracker.analyze_impact(file_path)

    print(f"✅ 影响分析完成")
    print(f"   风险级别: {impact_analysis['risk_level']}")
    print(f"   影响分数: {impact_analysis['impact_score']}")
    print(f"   直接依赖: {len(impact_analysis['direct_dependencies'])} 个")
    print(f"   依赖此文件: {len(impact_analysis['dependent_files'])} 个文件")

    # 保存影响分析结果
    safe_filename = file_path.replace('/', '_').replace('\\', '_').replace('.', '_')
    output_file = Path(project_path) / "code2claude" / "tracking" / f"impact_{safe_filename}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(impact_analysis, f, indent=2, ensure_ascii=False)

    print(f"✅ 影响分析结果已保存: {output_file}")

    return {
        "impact_analysis": impact_analysis,
        "output_file": str(output_file)
    }


def execute_trace_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行函数追踪命令"""
    if not args:
        print("❌ 错误: 请指定要追踪的函数名")
        return {"error": "Missing function name"}

    function_name = args[0]
    file_path = args[1] if len(args) > 1 else None

    print(f"🔍 正在追踪函数调用: {function_name}")

    tracker = ChangeTracker(project_path)

    # 执行函数追踪
    trace_result = tracker.trace_function_calls(function_name, file_path)

    print(f"✅ 函数追踪完成")
    print(f"   调用链深度: {trace_result['complexity']['depth']}")
    print(f"   调用广度: {trace_result['complexity']['breadth']}")
    print(f"   总函数数: {trace_result['complexity']['total_functions']}")

    # 保存追踪结果
    output_file = Path(project_path) / "code2claude" / "tracking" / f"trace_{function_name}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(trace_result, f, indent=2, ensure_ascii=False)

    print(f"✅ 追踪结果已保存: {output_file}")

    return {
        "trace_result": trace_result,
        "output_file": str(output_file)
    }


def execute_snapshot_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行快照创建命令"""
    snapshot_name = args[0] if args else None

    print("正在创建项目快照...")

    tracker = ChangeTracker(project_path)

    # 创建快照
    snapshot_file = tracker.create_snapshot(snapshot_name)

    print(f"项目快照已创建: {snapshot_file}")

    return {
        "snapshot_file": snapshot_file
    }


def execute_diff_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行快照对比命令"""
    if len(args) < 2:
        print("❌ 错误: 请指定两个快照文件进行对比")
        return {"error": "Missing snapshot files"}

    snapshot1 = args[0]
    snapshot2 = args[1]

    print(f"🔍 正在对比快照: {snapshot1} vs {snapshot2}")

    tracker = ChangeTracker(project_path)

    # 对比快照
    comparison = tracker.compare_snapshots(snapshot1, snapshot2)

    print(f"✅ 快照对比完成")
    print(f"   总变更数: {comparison['summary']['total_changes']}")
    print(f"   新增文件: {len(comparison['file_changes']['added'])}")
    print(f"   删除文件: {len(comparison['file_changes']['deleted'])}")
    print(f"   修改文件: {len(comparison['file_changes']['modified'])}")

    # 保存对比结果
    output_file = Path(project_path) / "code2claude" / "tracking" / "comparison.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    print(f"✅ 对比结果已保存: {output_file}")

    return {
        "comparison": comparison,
        "output_file": str(output_file)
    }


def execute_export_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行数据导出命令"""
    export_format = options.get('format', 'json')

    print(f"📤 正在导出数据 (格式: {export_format})...")

    # 获取最新的分析数据
    analyzer = CodeAnalyzer(project_path)
    analysis_data = analyzer.analyze_project()

    # 导出数据
    exporter = DataExporter(project_path)
    exported_files = exporter.export_analysis_data(analysis_data, [export_format])

    print(f"✅ 数据导出完成:")
    for format_type, file_path in exported_files.items():
        print(f"   {format_type}: {file_path}")

    # 如果导出为 HTML，还生成综合报告
    if export_format == 'html':
        mapper = ProjectMapper(project_path)
        map_data = mapper.map_project_structure()

        grapher = DependencyGrapher(project_path)
        graph_data = grapher.generate_all_graphs()

        report_file = exporter.export_project_report(
            analysis_data, map_data, graph_data
        )
        print(f"   综合报告: {report_file}")
        exported_files['comprehensive_report'] = report_file

    return {
        "exported_files": exported_files
    }


def _infer_project_type(analysis_result: Dict[str, Any]) -> str:
    """推断项目类型"""
    languages = analysis_result.get("languages", {})

    if "py" in languages:
        return "Python Project"
    elif "js" in languages:
        return "JavaScript Project"
    elif "dart" in languages:
        return "Flutter/Dart Project"
    elif "java" in languages:
        return "Java Project"
    else:
        return "Multi-language Project"


def _assess_complexity(analysis_result: Dict[str, Any]) -> str:
    """评估项目复杂度"""
    metrics = analysis_result.get("metrics", {})
    total_files = metrics.get("total_files", 0)
    languages = metrics.get("languages", 0)

    if total_files > 100 and languages > 2:
        return "High"
    elif total_files > 50 or languages > 1:
        return "Medium"
    else:
        return "Low"


def _generate_context_recommendations(analysis_result: Dict[str, Any]) -> list:
    """生成上下文建议"""
    recommendations = []

    languages = analysis_result.get("languages", {})
    if len(languages) > 1:
        recommendations.append("多语言项目，注意语言间的接口设计")

    hotspots = analysis_result.get("hotspots", {})
    large_files = hotspots.get("large_files", [])
    if len(large_files) > 5:
        recommendations.append("存在多个大文件，建议进行模块化重构")

    if not recommendations:
        recommendations.append("项目结构良好，继续保持代码质量")

    return recommendations


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()

    project_path = Path(args.project_path).resolve()

    if not project_path.exists():
        print(f"错误: 项目路径不存在: {project_path}")
        sys.exit(1)

    # 准备选项字典
    options = {
        'format': args.format,
        'output': args.output,
        'language': args.language,
        'depth': args.depth,
        'days': args.days,
        'verbose': args.verbose
    }

    # 执行命令
    command = args.command.lower()
    command_args = args.args

    try:
        if command in ['/cc:map', 'map']:
            result = execute_map_command(str(project_path), command_args, options)
        elif command in ['/cc:sync', 'sync']:
            result = execute_sync_command(str(project_path), command_args, options)
        elif command in ['/cc:context', 'context']:
            result = execute_context_command(str(project_path), command_args, options)
        elif command in ['/cc:graph', 'graph']:
            result = execute_graph_command(str(project_path), command_args, options)
        elif command in ['/cc:hotspot', 'hotspot']:
            result = execute_hotspot_command(str(project_path), command_args, options)
        elif command in ['/cc:impact', 'impact']:
            result = execute_impact_command(str(project_path), command_args, options)
        elif command in ['/cc:trace', 'trace']:
            result = execute_trace_command(str(project_path), command_args, options)
        elif command in ['/cc:snapshot', 'snapshot']:
            result = execute_snapshot_command(str(project_path), command_args, options)
        elif command in ['/cc:diff', 'diff']:
            result = execute_diff_command(str(project_path), command_args, options)
        elif command in ['/cc:export', 'export']:
            result = execute_export_command(str(project_path), command_args, options)
        else:
            print(f"错误: 未知命令: {command}")
            parser.print_help()
            sys.exit(1)

        if options['verbose'] and result:
            print("\n详细结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    except Exception as e:
        print(f"执行命令时出错: {e}")
        if options['verbose']:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()