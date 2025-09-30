"""
ClaudeFlow 命令行接口

基于 code2flow 的增强代码分析命令
"""

import argparse
import sys
import json
import time
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from colorama import Fore, Back, Style, init as colorama_init
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

from .core.analyzer import CodeAnalyzer
from .core.mapper import ProjectMapper
from .core.grapher import DependencyGrapher
from .core.tracker import ChangeTracker
from .core.exporter import DataExporter


# 初始化colorama(如果可用)
if COLORAMA_AVAILABLE:
    colorama_init(autoreset=True)


# 颜色辅助函数
def colored(text: str, color: str = None, style: str = None, enabled: bool = True) -> str:
    """为文本添加颜色(如果启用且可用)"""
    if not enabled or not COLORAMA_AVAILABLE:
        return text

    result = ""
    if style == 'bright':
        result += Style.BRIGHT
    elif style == 'dim':
        result += Style.DIM

    if color:
        color_map = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE,
        }
        result += color_map.get(color, '')

    return result + text + Style.RESET_ALL


# 命令别名映射
COMMAND_ALIASES = {
    # 新命令名 -> [别名列表]
    'structure': ['map', '/cc:map', '/cc:structure'],
    'refresh': ['sync', '/cc:sync', '/cc:refresh', '/cc:update'],
    'ai-context': ['context', '/cc:context', '/cc:ai-context'],
    'graph': ['graph', '/cc:graph'],
    'hotspot': ['hotspot', '/cc:hotspot'],
    'impact': ['impact', '/cc:impact'],
    'trace': ['trace', '/cc:trace'],
    'snapshot': ['snapshot', '/cc:snapshot'],
    'diff': ['diff', '/cc:diff'],
    'export': ['export', '/cc:export'],
    'help': ['help', '/cc:help', '--help', '-h'],
    'workflow': ['workflow', '/cc:workflow'],
}

# 反向映射: 别名 -> 标准命令名
ALIAS_TO_COMMAND = {}
for cmd, aliases in COMMAND_ALIASES.items():
    for alias in aliases:
        ALIAS_TO_COMMAND[alias.lower()] = cmd


# 默认配置
DEFAULT_CONFIG = {
    "project": {
        "exclude": ["*.pyc", "__pycache__", ".git", "node_modules", "venv", ".venv", "dist", "build"]
    },
    "analysis": {
        "depth": 3,
        "include_comments": True,
        "include_tests": True,
    },
    "hotspot": {
        "days": 30,
    },
    "output": {
        "format": "json",
        "colorful": True,
        "verbose": False,
        "show_progress": True,
    },
    "commands": {}
}


def load_config(project_path: Path) -> Dict[str, Any]:
    """加载配置文件"""
    config = DEFAULT_CONFIG.copy()

    # 查找配置文件
    config_files = [
        project_path / ".claudeflow.yml",
        project_path / ".claudeflow.yaml",
        project_path / "claudeflow.yml",
        project_path / "claudeflow.yaml",
    ]

    for config_file in config_files:
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        # 深度合并配置
                        config = merge_config(config, user_config)
                        print(f"ℹ️  已加载配置文件: {config_file.name}")
                        break
            except yaml.YAMLError as e:
                print(f"⚠️  配置文件格式错误: {config_file.name}")
                print(f"   YAML语法错误: {e}")
            except (IOError, OSError) as e:
                print(f"⚠️  无法读取配置文件: {config_file.name}")
                print(f"   文件访问错误: {e}")
            except PermissionError as e:
                print(f"⚠️  配置文件权限不足: {config_file.name}")
                print(f"   权限错误: {e}")

    return config


def merge_config(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """深度合并配置字典"""
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_config(result[key], value)
        else:
            result[key] = value

    return result


def print_help_message():
    """打印帮助信息"""
    help_text = """
╔══════════════════════════════════════════════════════╗
║         ClaudeFlow - 代码分析工具 v1.0              ║
╚══════════════════════════════════════════════════════╝

📚 核心命令:

  structure (map)         映射项目结构和代码组织
  refresh (sync)          刷新分析数据，同步最新变化
  ai-context (context)    生成AI友好的结构化上下文
  graph                   生成依赖关系可视化图表
  hotspot                 识别代码热点（复杂度、变更频率）

📊 分析命令:

  impact <file>           分析修改文件的影响范围
  trace <function>        追踪函数调用链和依赖关系

📸 版本控制:

  snapshot [name]         创建项目结构快照
  diff <snap1> <snap2>    对比两个快照的差异

📤 导出命令:

  export                  导出分析数据（支持多种格式）

❓ 帮助命令:

  help [command]          显示帮助信息
  workflow                显示推荐的工作流程

💡 使用示例:

  claudeflow structure              # 映射项目结构
  claudeflow refresh                # 刷新分析数据
  claudeflow impact core/cli.py     # 分析文件影响
  claudeflow trace main             # 追踪main函数
  claudeflow help impact            # 查看impact命令帮助

🔧 常用选项:

  -p, --project-path <path>   指定项目路径 (默认: 当前目录)
  --format <format>           输出格式 (json/markdown/html/csv)
  --days <n>                  热点分析天数 (默认: 30)
  -v, --verbose               详细输出模式
  --force                     跳过确认提示

📖 获取更多帮助:
  claudeflow help <command>  查看特定命令的详细帮助
  claudeflow workflow        查看推荐的使用流程
"""
    print(help_text)


def print_command_help(command: str):
    """打印特定命令的帮助"""
    help_messages = {
        'structure': """
╔══════════════════════════════════════════════════════╗
║  structure (map) - 项目结构映射                      ║
╚══════════════════════════════════════════════════════╝

📋 功能:
  生成项目的完整结构映射，包括目录树、文件索引和代码组织

🎯 用途:
  • 理解项目整体结构
  • 生成可视化项目地图
  • 为后续分析提供基础数据

💻 用法:
  claudeflow structure
  claudeflow structure -p /path/to/project

📤 输出:
  • claudeflow/maps/structure_map.json    结构数据
  • claudeflow/maps/code_map.json         代码映射
  • claudeflow/maps/interactive_map.html  交互式地图

💡 建议:
  这通常是第一个执行的命令，为后续分析打基础
""",
        'refresh': """
╔══════════════════════════════════════════════════════╗
║  refresh (sync) - 刷新分析数据                       ║
╚══════════════════════════════════════════════════════╝

📋 功能:
  重新分析项目，更新所有缓存的分析数据

🎯 用途:
  • 代码有重大修改后同步数据
  • 确保分析结果是最新的
  • 更新项目映射和依赖关系

💻 用法:
  claudeflow refresh
  claudeflow refresh --force  # 跳过确认

⚠️  注意:
  此操作会覆盖现有分析数据，大型项目可能需要较长时间

📤 输出:
  • claudeflow/analysis.json              分析结果
  • claudeflow/maps/structure_map.json    更新的映射
""",
        'impact': """
╔══════════════════════════════════════════════════════╗
║  impact - 文件影响分析                               ║
╚══════════════════════════════════════════════════════╝

📋 功能:
  分析修改某个文件会影响哪些模块和文件

🎯 用途:
  • 评估修改风险
  • 确定测试范围
  • 理解模块依赖关系

💻 用法:
  claudeflow impact <文件路径>
  claudeflow impact core/analyzer.py
  claudeflow impact src/utils/helper.py

📊 分析内容:
  • 直接依赖列表
  • 反向依赖（谁依赖此文件）
  • 影响范围评分
  • 风险级别评估

📤 输出:
  • 控制台显示摘要信息
  • claudeflow/tracking/impact_*.json  详细分析结果
""",
        'trace': """
╔══════════════════════════════════════════════════════╗
║  trace - 函数调用链追踪                              ║
╚══════════════════════════════════════════════════════╝

📋 功能:
  追踪函数的调用链和被调用关系

🎯 用途:
  • 理解函数执行流程
  • 识别函数依赖关系
  • 调试复杂调用链

💻 用法:
  claudeflow trace <函数名>
  claudeflow trace main
  claudeflow trace process_data

📊 分析内容:
  • 函数定义位置
  • 调用者列表（谁调用了此函数）
  • 被调用者列表（此函数调用了谁）
  • 调用链深度和广度

📤 输出:
  • 控制台显示调用关系摘要
  • claudeflow/tracking/trace_*.json  详细调用链
""",
        'hotspot': """
╔══════════════════════════════════════════════════════╗
║  hotspot - 代码热点识别                              ║
╚══════════════════════════════════════════════════════╝

📋 功能:
  识别需要关注的代码热点（高频修改、高复杂度、大文件）

🎯 用途:
  • 识别重构目标
  • 发现潜在问题区域
  • 优化代码质量

💻 用法:
  claudeflow hotspot
  claudeflow hotspot --days 60  # 分析最近60天

📊 分析维度:
  • 频率热点: 经常修改的文件（需要Git仓库）
  • 复杂度热点: 高复杂度文件
  • 大小热点: 过大的文件（>50KB）

📤 输出:
  • 分类热点列表和统计
  • 重构建议
  • claudeflow/tracking/hotspots.json  详细分析
"""
    }

    if command in help_messages:
        print(help_messages[command])
    else:
        print(f"❌ 未找到命令 '{command}' 的帮助信息")
        print(f"💡 运行 'claudeflow help' 查看所有可用命令")


def print_workflow():
    """打印推荐的工作流程"""
    workflow_text = """
╔══════════════════════════════════════════════════════╗
║           推荐工作流程                               ║
╚══════════════════════════════════════════════════════╝

🔄 标准分析流程:

  1️⃣  初始化分析
      claudeflow structure
      └─ 生成项目结构映射，创建基础数据

  2️⃣  生成可视化
      claudeflow graph
      └─ 创建依赖关系图，直观理解项目

  3️⃣  识别问题区域
      claudeflow hotspot
      └─ 找出需要关注的代码热点

  4️⃣  深入分析
      claudeflow impact <file>    # 分析修改影响
      claudeflow trace <function>  # 追踪调用链

  5️⃣  生成AI上下文
      claudeflow ai-context
      └─ 为AI工具生成结构化项目信息

📊 持续维护流程:

  • 代码修改后:
    claudeflow refresh            # 刷新分析数据
    claudeflow hotspot            # 重新识别热点

  • 重大重构前:
    claudeflow snapshot pre-refactor     # 创建快照
    ... 进行重构 ...
    claudeflow snapshot post-refactor    # 创建新快照
    claudeflow diff pre-refactor post-refactor  # 对比变化

🎯 特定场景:

  • 新接手项目:
    structure → graph → ai-context → hotspot

  • 重构规划:
    hotspot → impact <files> → snapshot

  • 代码审查:
    trace <function> → impact <file> → graph

💡 提示:
  - 大型项目首次分析可能需要几分钟
  - 建议定期执行 refresh 保持数据最新
  - 善用 snapshot 和 diff 追踪项目演进
"""
    print(workflow_text)


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="ClaudeFlow - 基于 code2flow 的增强代码分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,  # 使用自定义help
        epilog="""
运行 'claudeflow help' 查看详细帮助信息
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

    parser.add_argument(
        '--force',
        action='store_true',
        help='跳过确认提示，强制执行'
    )

    return parser


def print_progress(message: str, step: int = 0, total: int = 0, use_color: bool = True):
    """打印进度信息"""
    if step and total:
        progress_text = f"[{step}/{total}]"
        if use_color:
            progress_text = colored(progress_text, 'cyan', 'bright')
        print(f"  {progress_text} {message}")
    else:
        bullet = colored("•", 'blue') if use_color else "•"
        print(f"  {bullet} {message}")


def format_output_path(project_path: Path, output_file: Path) -> tuple:
    """格式化输出路径"""
    try:
        rel_path = output_file.relative_to(project_path)
    except ValueError:
        rel_path = output_file

    return str(rel_path), str(output_file.absolute())


def check_prerequisites(project_path: Path, command: str) -> bool:
    """检查命令执行的先决条件"""
    claudeflow_dir = project_path / "claudeflow"
    maps_dir = claudeflow_dir / "maps"

    needs_structure = ['ai-context', 'graph']

    if command in needs_structure and not maps_dir.exists():
        print("⚠️  建议先运行 structure 命令生成项目映射")
        print("   这将提供更完整和准确的分析结果")
        print()

        response = input("是否现在运行 structure 命令? (Y/n): ")
        if response.lower() != 'n':
            return False  # 需要先执行structure

    return True


def confirm_operation(operation: str, warning: str = None) -> bool:
    """确认操作"""
    print(f"⚠️  即将执行: {operation}")
    if warning:
        print(f"   {warning}")
    print()

    response = input("确认继续? (y/N): ")
    return response.lower() == 'y'


def execute_map_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行映射命令"""
    use_color = options.get('config', {}).get('output', {}).get('colorful', True)

    print("╔══════════════════════════════════════════════════════╗")
    print("║  正在映射项目结构...                                 ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    mapper = ProjectMapper(project_path)
    project_path_obj = Path(project_path)

    # 生成结构映射
    print_progress("扫描项目目录结构", 1, 4, use_color)
    structure_map = mapper.map_project_structure()
    success_msg = f"✅ 项目结构映射完成 ({structure_map['overview']['total_files']} 个文件)"
    print(colored(success_msg, 'green', enabled=use_color))

    # 生成代码映射
    print_progress("分析代码结构", 2, 4, use_color)
    code_map = mapper.map_code_structure()
    print(colored("✅ 代码结构映射完成", 'green', enabled=use_color))

    # 生成交互式地图
    print_progress("生成交互式地图", 3, 4, use_color)
    interactive_map = mapper.generate_interactive_map()
    print(colored("✅ 交互式地图已生成", 'green', enabled=use_color))

    # 保存映射文件
    print_progress("保存映射文件", 4, 4, use_color)
    saved_files = mapper.save_maps()

    print()
    print(colored("📁 映射文件已保存:", 'blue', enabled=use_color))
    for map_type, file_path in saved_files.items():
        rel_path, full_path = format_output_path(project_path_obj, Path(file_path))
        print(f"   • {map_type:<12} {colored(rel_path, 'cyan', enabled=use_color)}")

    # 如果是HTML文件，提供打开提示
    if 'interactive' in saved_files:
        html_file = Path(saved_files['interactive'])
        print()
        hint = f"💡 在浏览器中查看: file://{html_file.absolute()}"
        print(colored(hint, 'yellow', enabled=use_color))

    # 下一步建议
    print()
    print(colored("💡 下一步建议:", 'yellow', enabled=use_color))
    print("   • claudeflow graph       - 生成依赖关系可视化")
    print("   • claudeflow hotspot     - 识别代码热点")
    print("   • claudeflow ai-context  - 生成AI分析上下文")

    return {
        "structure_map": structure_map,
        "code_map": code_map,
        "saved_files": saved_files
    }


def execute_sync_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行同步命令"""
    if not options.get('force'):
        if not confirm_operation(
            "刷新项目分析数据",
            "此操作会重新分析整个项目并覆盖现有数据，大型项目可能需要较长时间"
        ):
            print("❌ 操作已取消")
            return {"cancelled": True}

    print("╔══════════════════════════════════════════════════════╗")
    print("║  正在刷新项目分析数据...                             ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    analyzer = CodeAnalyzer(project_path)
    project_path_obj = Path(project_path)

    # 重新分析项目
    print_progress("重新扫描项目文件", 1, 3)
    analysis_result = analyzer.analyze_project()
    print("✅ 项目分析完成")

    # 保存分析结果
    print_progress("保存分析结果", 2, 3)
    output_file = analyzer.save_analysis()
    rel_path, full_path = format_output_path(project_path_obj, Path(output_file))
    print(f"✅ 分析结果已保存: {rel_path}")

    # 更新映射
    print_progress("更新项目映射", 3, 3)
    mapper = ProjectMapper(project_path)
    mapper.save_maps()
    print("✅ 项目映射已更新")

    print()
    print("💡 刷新完成，所有分析数据已更新为最新状态")

    return {
        "analysis_result": analysis_result,
        "output_file": output_file
    }


def execute_impact_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行影响分析命令"""
    if not args:
        print("❌ 错误: 缺少必需参数")
        print()
        print("💻 用法:")
        print("   claudeflow impact <文件路径>")
        print()
        print("📖 示例:")
        print("   claudeflow impact core/analyzer.py")
        print("   claudeflow impact src/utils/helper.py")
        print()
        print("❓ 运行 'claudeflow help impact' 查看详细帮助")
        return {"error": "Missing file path"}

    file_path = args[0]
    print(f"🎯 正在分析文件影响: {file_path}")
    print()

    tracker = ChangeTracker(project_path)
    project_path_obj = Path(project_path)

    # 执行影响分析
    impact_analysis = tracker.analyze_impact(file_path)

    # 格式化输出
    print("╔══════════════════════════════════════════════════════╗")
    print("║           影响分析结果                               ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    print(f"📊 影响评估:")
    print(f"   • 风险级别: {impact_analysis['risk_level'].upper()}")
    print(f"   • 影响分数: {impact_analysis['impact_score']}")
    print()
    print(f"🔗 依赖关系:")
    print(f"   • 直接依赖: {len(impact_analysis['direct_dependencies'])} 个模块")
    print(f"   • 被依赖: {len(impact_analysis['dependent_files'])} 个文件")

    # 显示关键依赖
    if impact_analysis['dependent_files']:
        print()
        print("⚠️  修改此文件将影响以下文件:")
        for dep_file in impact_analysis['dependent_files'][:5]:
            print(f"   • {dep_file}")
        if len(impact_analysis['dependent_files']) > 5:
            print(f"   ... 以及其他 {len(impact_analysis['dependent_files']) - 5} 个文件")

    # 保存结果
    safe_filename = file_path.replace('/', '_').replace('\\', '_').replace('.', '_')
    output_file = Path(project_path) / "claudeflow" / "tracking" / f"impact_{safe_filename}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(impact_analysis, f, indent=2, ensure_ascii=False)

    print()
    rel_path, full_path = format_output_path(project_path_obj, output_file)
    print(f"📁 详细分析结果: {rel_path}")

    return {
        "impact_analysis": impact_analysis,
        "output_file": str(output_file)
    }


def execute_trace_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行函数追踪命令"""
    if not args:
        print("❌ 错误: 缺少必需参数")
        print()
        print("💻 用法:")
        print("   claudeflow trace <函数名> [文件路径]")
        print()
        print("📖 示例:")
        print("   claudeflow trace main")
        print("   claudeflow trace process_data")
        print("   claudeflow trace calculate src/utils.py")
        print()
        print("❓ 运行 'claudeflow help trace' 查看详细帮助")
        return {"error": "Missing function name"}

    function_name = args[0]
    file_path = args[1] if len(args) > 1 else None

    print(f"🔍 正在追踪函数调用: {function_name}")
    if file_path:
        print(f"   限定文件: {file_path}")
    print()

    tracker = ChangeTracker(project_path)
    project_path_obj = Path(project_path)

    # 执行函数追踪
    trace_result = tracker.trace_function_calls(function_name, file_path)

    # 格式化输出
    print("╔══════════════════════════════════════════════════════╗")
    print("║           函数调用链分析                             ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    print(f"📊 调用复杂度:")
    print(f"   • 调用链深度: {trace_result['complexity']['depth']}")
    print(f"   • 调用广度: {trace_result['complexity']['breadth']}")
    print(f"   • 涉及函数: {trace_result['complexity']['total_functions']} 个")

    # 显示调用者
    if trace_result['callers']:
        print()
        print(f"📞 被以下位置调用 ({len(trace_result['callers'])} 处):")
        for caller in trace_result['callers'][:5]:
            print(f"   • {caller['file']}:{caller['line']}")
        if len(trace_result['callers']) > 5:
            print(f"   ... 以及其他 {len(trace_result['callers']) - 5} 处")

    # 保存结果
    output_file = Path(project_path) / "claudeflow" / "tracking" / f"trace_{function_name}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(trace_result, f, indent=2, ensure_ascii=False)

    print()
    rel_path, full_path = format_output_path(project_path_obj, output_file)
    print(f"📁 详细追踪结果: {rel_path}")

    return {
        "trace_result": trace_result,
        "output_file": str(output_file)
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
    output_dir = Path(project_path) / "claudeflow"
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
    print("╔══════════════════════════════════════════════════════╗")
    print("║  正在识别代码热点...                                 ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    tracker = ChangeTracker(project_path)
    project_path_obj = Path(project_path)
    days = options.get('days', 30)

    # 识别热点
    print(f"📊 分析周期: 最近 {days} 天")
    hotspots = tracker.identify_hotspots(days)

    # 格式化输出
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║           🔥 代码热点分析报告                        ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    # 频率热点
    freq_hotspots = hotspots.get("frequency_hotspots", [])
    if freq_hotspots:
        print(f"┌─ 频率热点 (Top {min(5, len(freq_hotspots))})")
        for i, hotspot in enumerate(freq_hotspots[:5], 1):
            changes = hotspot.get('change_count', 0)
            warning = "  ⚠️ 高频修改" if changes > 10 else ""
            print(f"│  {i}. {hotspot['file']:<40} ({changes}次变更){warning}")
        print()

    # 复杂度热点
    complex_hotspots = hotspots.get("complexity_hotspots", [])
    if complex_hotspots:
        print(f"┌─ 复杂度热点 (Top {min(3, len(complex_hotspots))})")
        for i, hotspot in enumerate(complex_hotspots[:3], 1):
            score = hotspot.get('complexity_score', 0)
            warning = "  ⚠️ 需重构" if score > 8 else ""
            print(f"│  {i}. {hotspot['file']:<40} (复杂度: {score:.1f}){warning}")
        print()

    # 大小热点
    size_hotspots = hotspots.get("size_hotspots", [])
    if size_hotspots:
        print(f"┌─ 大小热点 (Top {min(3, len(size_hotspots))})")
        for i, hotspot in enumerate(size_hotspots[:3], 1):
            size_kb = hotspot['size'] / 1024
            lines = hotspot.get('lines', 0)
            print(f"│  {i}. {hotspot['file']:<40} ({size_kb:.1f}KB, {lines}行)")
        print()

    # 建议
    recommendations = hotspots.get("recommendations", [])
    if recommendations:
        print("💡 建议:")
        for rec in recommendations:
            print(f"   • {rec}")
        print()

    # 保存结果
    output_file = Path(project_path) / "claudeflow" / "tracking" / "hotspots.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hotspots, f, indent=2, ensure_ascii=False)

    rel_path, full_path = format_output_path(project_path_obj, output_file)
    print(f"📁 详细报告: {rel_path}")

    return {
        "hotspots": hotspots,
        "output_file": str(output_file)
    }


def execute_graph_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行图表生成命令"""
    print("╔══════════════════════════════════════════════════════╗")
    print("║  正在生成依赖关系图...                               ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    grapher = DependencyGrapher(project_path)
    project_path_obj = Path(project_path)

    # 生成所有类型的图
    print_progress("生成调用关系图", 1, 4)
    print_progress("分析模块依赖", 2, 4)
    print_progress("生成类层次图", 3, 4)
    print_progress("生成模块地图", 4, 4)

    generated_graphs = grapher.generate_all_graphs()

    print()
    print("✅ 依赖关系图生成完成")
    print()
    print("📊 生成的图表:")
    for graph_type, file_path in generated_graphs.items():
        rel_path, full_path = format_output_path(project_path_obj, Path(file_path))

        # 为HTML文件添加浏览器打开提示
        if file_path.endswith('.html'):
            print(f"   • {graph_type:<20} {rel_path}")
            print(f"     💡 在浏览器中查看: file://{Path(file_path).absolute()}")
        else:
            print(f"   • {graph_type:<20} {rel_path}")

    print()
    print("💡 下一步建议:")
    print("   • 在浏览器中打开HTML文件查看交互式图表")
    print("   • claudeflow hotspot  - 识别需要重构的区域")

    return {
        "generated_graphs": generated_graphs
    }


def execute_context_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行上下文生成命令"""
    print("╔══════════════════════════════════════════════════════╗")
    print("║  正在生成AI上下文...                                 ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    analyzer = CodeAnalyzer(project_path)
    project_path_obj = Path(project_path)

    print_progress("分析项目结构", 1, 3)
    analysis_result = analyzer.analyze_project()

    print_progress("提取关键组件", 2, 3)

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

    print_progress("生成上下文文件", 3, 3)

    # 保存上下文文件
    output_dir = Path(project_path) / "claudeflow"
    output_dir.mkdir(exist_ok=True)
    context_file = output_dir / "context.json"

    with open(context_file, 'w', encoding='utf-8') as f:
        json.dump(context_data, f, indent=2, ensure_ascii=False)

    print()
    print("✅ AI上下文生成完成")
    print()
    rel_path, full_path = format_output_path(project_path_obj, context_file)
    print(f"📁 上下文文件: {rel_path}")
    print()
    print(f"📊 项目概况:")
    print(f"   • 项目类型: {context_data['context_for_claude']['project_type']}")
    print(f"   • 主要语言: {', '.join(context_data['context_for_claude']['main_languages'])}")
    print(f"   • 复杂度级别: {context_data['context_for_claude']['complexity_level']}")
    print(f"   • 关键组件: {len(context_data['key_components'])} 个")

    return {
        "context_data": context_data,
        "context_file": str(context_file)
    }


def execute_snapshot_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行快照创建命令"""
    snapshot_name = args[0] if args else None

    print("╔══════════════════════════════════════════════════════╗")
    print("║  正在创建项目快照...                                 ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    tracker = ChangeTracker(project_path)
    project_path_obj = Path(project_path)

    print_progress("扫描项目文件", 1, 2)
    # 创建快照
    snapshot_file = tracker.create_snapshot(snapshot_name)

    print_progress("保存快照数据", 2, 2)

    print()
    print("✅ 项目快照创建完成")
    print()
    rel_path, full_path = format_output_path(project_path_obj, Path(snapshot_file))
    print(f"📁 快照文件: {rel_path}")
    if snapshot_name:
        print(f"   快照名称: {snapshot_name}")

    print()
    print("💡 下一步建议:")
    print("   • claudeflow snapshot <另一个名称>  - 创建另一个快照用于对比")
    print("   • claudeflow diff <快照1> <快照2>   - 对比两个快照的差异")

    return {
        "snapshot_file": snapshot_file
    }


def execute_diff_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行快照对比命令"""
    if len(args) < 2:
        print("❌ 错误: 缺少必需参数")
        print()
        print("💻 用法:")
        print("   claudeflow diff <快照1> <快照2>")
        print()
        print("📖 示例:")
        print("   claudeflow diff v1.0 v1.1")
        print("   claudeflow diff pre-refactor post-refactor")
        print()
        print("❓ 运行 'claudeflow help diff' 查看详细帮助")
        return {"error": "Missing snapshot files"}

    snapshot1 = args[0]
    snapshot2 = args[1]

    print("╔══════════════════════════════════════════════════════╗")
    print("║  正在对比快照...                                     ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    print(f"🔍 对比: {snapshot1} ↔ {snapshot2}")
    print()

    tracker = ChangeTracker(project_path)
    project_path_obj = Path(project_path)

    print_progress("加载快照数据", 1, 3)
    print_progress("分析变更", 2, 3)

    # 对比快照
    comparison = tracker.compare_snapshots(snapshot1, snapshot2)

    print_progress("生成对比报告", 3, 3)

    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║           快照对比结果                               ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    print(f"📊 变更统计:")
    print(f"   • 总变更数: {comparison['summary']['total_changes']}")
    print(f"   • 新增文件: {len(comparison['file_changes']['added'])} 个")
    print(f"   • 删除文件: {len(comparison['file_changes']['deleted'])} 个")
    print(f"   • 修改文件: {len(comparison['file_changes']['modified'])} 个")

    # 保存对比结果
    output_file = Path(project_path) / "claudeflow" / "tracking" / "comparison.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)

    print()
    rel_path, full_path = format_output_path(project_path_obj, output_file)
    print(f"📁 详细对比报告: {rel_path}")

    return {
        "comparison": comparison,
        "output_file": str(output_file)
    }


def execute_export_command(project_path: str, args: list, options: Dict[str, Any]) -> Dict[str, Any]:
    """执行数据导出命令"""
    export_format = options.get('format', 'json')

    print("╔══════════════════════════════════════════════════════╗")
    print("║  正在导出分析数据...                                 ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    print(f"📤 导出格式: {export_format}")
    print()

    project_path_obj = Path(project_path)

    print_progress("获取分析数据", 1, 3)
    # 获取最新的分析数据
    analyzer = CodeAnalyzer(project_path)
    analysis_data = analyzer.analyze_project()

    print_progress("导出数据", 2, 3)
    # 导出数据
    exporter = DataExporter(project_path)
    exported_files = exporter.export_analysis_data(analysis_data, [export_format])

    print_progress("生成报告", 3, 3)

    print()
    print("✅ 数据导出完成")
    print()
    print("📊 导出的文件:")
    for format_type, file_path in exported_files.items():
        rel_path, full_path = format_output_path(project_path_obj, Path(file_path))
        print(f"   • {format_type:<10} {rel_path}")

    # 如果导出为 HTML，还生成综合报告
    if export_format == 'html':
        print()
        print_progress("生成综合HTML报告", 1, 1)

        mapper = ProjectMapper(project_path)
        map_data = mapper.map_project_structure()

        grapher = DependencyGrapher(project_path)
        graph_data = grapher.generate_all_graphs()

        report_file = exporter.export_project_report(
            analysis_data, map_data, graph_data
        )

        rel_path, full_path = format_output_path(project_path_obj, Path(report_file))
        print(f"   • 综合报告    {rel_path}")
        print()
        print(f"💡 在浏览器中查看: file://{Path(report_file).absolute()}")

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

    # 处理help命令
    command = args.command.lower()
    if command in ALIAS_TO_COMMAND.get('help', ['help']):
        if args.args:
            # 显示特定命令帮助
            target_cmd = args.args[0].lower()
            # 解析命令别名
            canonical_cmd = ALIAS_TO_COMMAND.get(target_cmd, target_cmd)
            print_command_help(canonical_cmd)
        else:
            # 显示总帮助
            print_help_message()
        sys.exit(0)

    # 处理workflow命令
    if command in ['workflow', '/cc:workflow']:
        print_workflow()
        sys.exit(0)

    # 验证项目路径
    project_path = Path(args.project_path).resolve()

    if not project_path.exists():
        print("❌ 错误: 找不到项目路径")
        print(f"📁 指定路径: {project_path}")
        print()
        print("💡 提示:")
        print("   • 检查路径是否正确")
        print("   • 使用 -p 参数指定项目路径")
        print(f"   • 示例: claudeflow {command} -p /path/to/project")
        sys.exit(1)

    # 加载配置文件
    config = load_config(project_path)

    # 准备选项字典 - 命令行参数优先于配置文件
    options = {
        'format': args.format if args.format != 'json' else config.get('output', {}).get('format', 'json'),
        'output': args.output,
        'language': args.language if args.language else config.get('project', {}).get('language'),
        'depth': args.depth if args.depth != 3 else config.get('analysis', {}).get('depth', 3),
        'days': args.days if args.days != 30 else config.get('hotspot', {}).get('days', 30),
        'verbose': args.verbose or config.get('output', {}).get('verbose', False),
        'force': getattr(args, 'force', False),
        'config': config  # 传递完整配置供命令使用
    }

    # 解析命令别名
    canonical_command = ALIAS_TO_COMMAND.get(command, command)
    command_args = args.args

    # 检查先决条件
    if not check_prerequisites(project_path, canonical_command):
        # 用户选择先执行structure
        result = execute_map_command(str(project_path), [], options)
        print()
        print("✅ 结构映射完成，继续执行原命令...")
        print()

    try:
        # 执行命令
        if canonical_command == 'structure':
            result = execute_map_command(str(project_path), command_args, options)
        elif canonical_command == 'refresh':
            result = execute_sync_command(str(project_path), command_args, options)
        elif canonical_command == 'ai-context':
            result = execute_context_command(str(project_path), command_args, options)
        elif canonical_command == 'graph':
            result = execute_graph_command(str(project_path), command_args, options)
        elif canonical_command == 'hotspot':
            result = execute_hotspot_command(str(project_path), command_args, options)
        elif canonical_command == 'impact':
            result = execute_impact_command(str(project_path), command_args, options)
        elif canonical_command == 'trace':
            result = execute_trace_command(str(project_path), command_args, options)
        elif canonical_command == 'snapshot':
            result = execute_snapshot_command(str(project_path), command_args, options)
        elif canonical_command == 'diff':
            result = execute_diff_command(str(project_path), command_args, options)
        elif canonical_command == 'export':
            result = execute_export_command(str(project_path), command_args, options)
        else:
            print(f"❌ 错误: 未知命令 '{command}'")
            print()
            print("💡 运行 'claudeflow help' 查看所有可用命令")
            print("   或运行 'claudeflow workflow' 查看使用流程")
            sys.exit(1)

        if options['verbose'] and result:
            print("\n" + "="*54)
            print("详细结果:")
            print("="*54)
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    except KeyboardInterrupt:
        print()
        print("\n⚠️  操作已被用户中断")
        sys.exit(130)
    except Exception as e:
        print()
        print(f"❌ 执行命令时出错: {e}")
        if options['verbose']:
            print()
            print("详细错误信息:")
            import traceback
            traceback.print_exc()
        else:
            print()
            print("💡 使用 -v 参数查看详细错误信息")
        sys.exit(1)


if __name__ == '__main__':
    main()