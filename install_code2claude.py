#!/usr/bin/env python3
"""
Code2Claude 安装脚本

自动安装和配置 Code2Claude 分析系统
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def install_code2claude():
    """安装 Code2Claude 系统"""
    print("开始安装 Code2Claude 分析系统...")

    # 检查 Python 版本
    if sys.version_info < (3, 7):
        print("错误: 需要 Python 3.7 或更高版本")
        sys.exit(1)

    # 获取当前目录
    current_dir = Path(__file__).parent.absolute()

    # 创建可执行脚本
    create_executable_scripts(current_dir)

    # 安装依赖
    install_dependencies()

    print("Code2Claude 安装完成!")
    print("\n可用命令:")
    print("  code2claude /cc:map           # 映射项目结构")
    print("  code2claude /cc:sync          # 同步项目变化")
    print("  code2claude /cc:context       # 生成Claude上下文")
    print("  code2claude /cc:graph         # 生成依赖关系图")
    print("  code2claude /cc:hotspot       # 识别代码热点")
    print("  code2claude /cc:impact <file> # 影响分析")
    print("  code2claude /cc:trace <func>  # 追踪函数调用")
    print("  code2claude /cc:snapshot      # 创建项目快照")
    print("  code2claude /cc:diff s1 s2    # 对比快照差异")
    print("  code2claude /cc:export        # 导出分析数据")


def create_executable_scripts(base_dir):
    """创建可执行脚本"""
    print("创建可执行脚本...")

    # 创建主启动脚本
    launcher_content = f'''#!/usr/bin/env python3
"""Code2Claude 启动器"""
import sys
import os
sys.path.insert(0, r"{base_dir}")

from code2claude.cli import main

if __name__ == "__main__":
    main()
'''

    # Windows 批处理文件
    bat_content = f'''@echo off
python "{base_dir / "code2claude" / "__main__.py"}" %*
'''

    # PowerShell 脚本
    ps1_content = f'''#!/usr/bin/env pwsh
python "{base_dir / "code2claude" / "__main__.py"}" @args
'''

    # 保存脚本文件
    launcher_file = base_dir / "code2claude_launcher.py"
    with open(launcher_file, 'w', encoding='utf-8') as f:
        f.write(launcher_content)

    bat_file = base_dir / "code2claude.bat"
    with open(bat_file, 'w', encoding='utf-8') as f:
        f.write(bat_content)

    ps1_file = base_dir / "code2claude.ps1"
    with open(ps1_file, 'w', encoding='utf-8') as f:
        f.write(ps1_content)

    # 使脚本可执行 (Unix/Linux)
    if os.name != 'nt':
        os.chmod(launcher_file, 0o755)
        os.chmod(ps1_file, 0o755)

    print(f"脚本已创建:")
    print(f"   Windows: {bat_file}")
    print(f"   PowerShell: {ps1_file}")
    print(f"   Python: {launcher_file}")


def install_dependencies():
    """安装必要的依赖"""
    print("检查和安装依赖...")

    # 基础依赖列表
    dependencies = [
        # 没有额外的 Python 包依赖，主要使用标准库
    ]

    # 检查可选依赖
    optional_deps = {
        'graphviz': '用于生成更好的图形输出',
        'matplotlib': '用于生成图表',
        'networkx': '用于复杂网络分析'
    }

    print("检查可选依赖...")
    for dep, description in optional_deps.items():
        try:
            __import__(dep)
            print(f"   {dep}: 已安装")
        except ImportError:
            print(f"   {dep}: 未安装 ({description})")


if __name__ == "__main__":
    install_code2claude()