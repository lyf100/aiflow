"""
ClaudeFlow 命令行接口 (重构版)

基于 code2flow 的增强代码分析命令
使用命令处理器模式，简化代码结构
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from colorama import init as colorama_init
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

# 导入命令处理器
from commands.registry import get_command_handler, COMMAND_HANDLERS


# 初始化colorama(如果可用)
if COLORAMA_AVAILABLE:
    colorama_init(autoreset=True)


# 命令别名映射
COMMAND_ALIASES = {
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
                        config = merge_config(config, user_config)
                        print(f"ℹ️  已加载配置文件: {config_file.name}")
                        break
            except yaml.YAMLError as e:
                print(f"⚠️  配置文件格式错误: {config_file.name}")
                print(f"   YAML语法错误: {e}")
            except (IOError, OSError) as e:
                print(f"⚠️  无法读取配置文件: {config_file.name}")

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
  claudeflow help impact            # 查看impact命令帮助

🔧 常用选项:

  -p, --project-path <path>   指定项目路径 (默认: 当前目录)
  --format <format>           输出格式 (json/markdown/html/csv)
  --days <n>                  热点分析天数 (默认: 30)
  -v, --verbose               详细输出模式
  --force                     跳过确认提示
"""
    print(help_text)


def print_workflow():
    """打印推荐的工作流程"""
    workflow_text = """
╔══════════════════════════════════════════════════════╗
║           推荐工作流程                               ║
╚══════════════════════════════════════════════════════╝

🔄 标准分析流程:

  1️⃣  初始化分析
      claudeflow structure

  2️⃣  生成可视化
      claudeflow graph

  3️⃣  识别问题区域
      claudeflow hotspot

  4️⃣  深入分析
      claudeflow impact <file>
      claudeflow trace <function>

  5️⃣  生成AI上下文
      claudeflow ai-context

📊 持续维护流程:

  • 代码修改后:
    claudeflow refresh
    claudeflow hotspot

  • 重大重构前:
    claudeflow snapshot pre-refactor
    claudeflow snapshot post-refactor
    claudeflow diff pre-refactor post-refactor
"""
    print(workflow_text)


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="ClaudeFlow - 基于 code2flow 的增强代码分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
        epilog="运行 'claudeflow help' 查看详细帮助信息"
    )

    parser.add_argument('command', help='要执行的命令')
    parser.add_argument('args', nargs='*', help='命令参数')
    parser.add_argument('-p', '--project-path', default='.', help='项目路径 (默认: 当前目录)')
    parser.add_argument('--format', choices=['json', 'markdown', 'html', 'csv'], default='json', help='输出格式')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--language', choices=['py', 'js', 'rb', 'php'], help='指定分析的编程语言')
    parser.add_argument('--depth', type=int, default=3, help='分析深度 (默认: 3)')
    parser.add_argument('--days', type=int, default=30, help='热点分析的天数范围 (默认: 30)')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--force', action='store_true', help='跳过确认提示，强制执行')

    return parser


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
            return False

    return True


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()

    # 处理help命令
    command = args.command.lower()
    if command in ALIAS_TO_COMMAND.get('help', ['help']):
        if args.args:
            # TODO: 显示特定命令帮助
            pass
        else:
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
        sys.exit(1)

    # 加载配置文件
    config = load_config(project_path)

    # 准备选项字典
    options = {
        'format': args.format if args.format != 'json' else config.get('output', {}).get('format', 'json'),
        'output': args.output,
        'language': args.language if args.language else config.get('project', {}).get('language'),
        'depth': args.depth if args.depth != 3 else config.get('analysis', {}).get('depth', 3),
        'days': args.days if args.days != 30 else config.get('hotspot', {}).get('days', 30),
        'verbose': args.verbose or config.get('output', {}).get('verbose', False),
        'force': getattr(args, 'force', False),
        'config': config
    }

    # 解析命令别名
    canonical_command = ALIAS_TO_COMMAND.get(command, command)
    command_args = args.args

    # 检查先决条件
    if not check_prerequisites(project_path, canonical_command):
        # 执行structure命令
        try:
            handler = get_command_handler('structure', str(project_path), options)
            handler.execute([])
            print()
            print("✅ 结构映射完成，继续执行原命令...")
            print()
        except Exception as e:
            print(f"❌ 执行structure命令失败: {e}")
            sys.exit(1)

    try:
        # 获取并执行命令处理器
        handler = get_command_handler(canonical_command, str(project_path), options)
        result = handler.execute(command_args)

        if options['verbose'] and result:
            print("\n" + "="*54)
            print("详细结果:")
            print("="*54)
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    except ValueError as e:
        # 未知命令
        print(f"❌ 错误: {e}")
        print()
        print("💡 运行 'claudeflow help' 查看所有可用命令")
        sys.exit(1)

    except KeyboardInterrupt:
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