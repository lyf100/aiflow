#!/usr/bin/env python3
"""
Code2Claude MCP 一键安装脚本

自动安装依赖、配置 Claude Desktop，无需手动操作
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @staticmethod
    def print_success(msg: str):
        print(f"{Colors.GREEN}✓{Colors.END} {msg}")

    @staticmethod
    def print_warning(msg: str):
        print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

    @staticmethod
    def print_error(msg: str):
        print(f"{Colors.RED}✗{Colors.END} {msg}")

    @staticmethod
    def print_info(msg: str):
        print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

    @staticmethod
    def print_header(msg: str):
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{msg}{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")


class MCPInstaller:
    """MCP 服务器安装器"""

    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.config_paths = self._get_config_paths()
        self.backup_suffix = ".backup"

    def _get_config_paths(self) -> Dict[str, Path]:
        """获取 Claude Desktop 配置文件路径"""
        system = sys.platform

        if system == "win32":
            base = Path(os.environ.get("APPDATA", "")) / "Claude"
        elif system == "darwin":
            base = Path.home() / "Library" / "Application Support" / "Claude"
        else:  # Linux
            base = Path.home() / ".config" / "Claude"

        return {
            "config": base / "claude_desktop_config.json",
            "logs": base / "logs",
            "backup_dir": base / "backups"
        }

    def check_python_version(self) -> bool:
        """检查 Python 版本"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            Colors.print_error(f"Python 版本过低: {version.major}.{version.minor}")
            Colors.print_error("需要 Python 3.8 或更高版本")
            return False

        Colors.print_success(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
        return True

    def install_dependencies(self) -> bool:
        """安装依赖包"""
        Colors.print_info("正在安装依赖包...")

        requirements_file = self.script_dir / "requirements.txt"
        if not requirements_file.exists():
            Colors.print_error("requirements.txt 文件不存在")
            return False

        try:
            # 升级 pip
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                check=True,
                capture_output=True
            )

            # 安装依赖
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                check=True,
                capture_output=True,
                text=True
            )

            Colors.print_success("依赖安装完成")
            return True

        except subprocess.CalledProcessError as e:
            Colors.print_error(f"依赖安装失败: {e.stderr}")
            return False

    def verify_mcp_sdk(self) -> bool:
        """验证 MCP SDK 安装"""
        Colors.print_info("验证 MCP SDK...")

        try:
            import mcp
            Colors.print_success("MCP SDK 已安装")
            return True
        except ImportError:
            Colors.print_error("MCP SDK 未安装")
            Colors.print_info("尝试单独安装 MCP SDK...")

            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "mcp[cli]>=1.4.0"],
                    check=True,
                    capture_output=True
                )
                Colors.print_success("MCP SDK 安装成功")
                return True
            except subprocess.CalledProcessError:
                Colors.print_error("MCP SDK 安装失败")
                return False

    def backup_config(self, config_path: Path) -> Optional[Path]:
        """备份现有配置"""
        if not config_path.exists():
            return None

        # 创建备份目录
        backup_dir = self.config_paths["backup_dir"]
        backup_dir.mkdir(parents=True, exist_ok=True)

        # 生成备份文件名
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"claude_desktop_config_{timestamp}.json"

        try:
            shutil.copy2(config_path, backup_file)
            Colors.print_success(f"配置已备份到: {backup_file}")
            return backup_file
        except Exception as e:
            Colors.print_warning(f"备份失败: {e}")
            return None

    def update_config(self) -> bool:
        """更新 Claude Desktop 配置"""
        Colors.print_info("配置 Claude Desktop...")

        config_path = self.config_paths["config"]

        # 确保配置目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # 备份现有配置
        if config_path.exists():
            self.backup_config(config_path)

        # 读取或创建配置
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                Colors.print_warning("现有配置文件格式错误，将创建新配置")
                config = {}
        else:
            config = {}

        # 确保 mcpServers 存在
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # 添加 Code2Claude 配置
        config["mcpServers"]["code2claude"] = {
            "command": sys.executable,
            "args": ["-m", "code2claude.mcp_server"],
            "env": {},
            "description": "Code2Claude - AI-powered code analysis and project mapping"
        }

        # 写入配置
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            Colors.print_success(f"配置已更新: {config_path}")
            return True

        except Exception as e:
            Colors.print_error(f"配置更新失败: {e}")
            return False

    def verify_installation(self) -> bool:
        """验证安装"""
        Colors.print_info("验证安装...")

        # 检查配置文件
        config_path = self.config_paths["config"]
        if not config_path.exists():
            Colors.print_error("配置文件不存在")
            return False

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            if "mcpServers" not in config or "code2claude" not in config["mcpServers"]:
                Colors.print_error("配置文件中未找到 Code2Claude")
                return False

            Colors.print_success("配置验证通过")

        except Exception as e:
            Colors.print_error(f"配置验证失败: {e}")
            return False

        # 检查核心模块
        try:
            from core.analyzer import CodeAnalyzer
            from core.mapper import ProjectMapper
            Colors.print_success("核心模块验证通过")
        except ImportError as e:
            Colors.print_error(f"核心模块导入失败: {e}")
            return False

        return True

    def print_next_steps(self):
        """打印后续步骤"""
        Colors.print_header("安装完成！")

        print(f"{Colors.GREEN}✓{Colors.END} MCP 服务器已配置完成\n")

        print(f"{Colors.BOLD}下一步操作:{Colors.END}\n")
        print("1. 重启 Claude Desktop")
        print("   - 完全退出 Claude Desktop (任务管理器确认进程已关闭)")
        print("   - 重新启动 Claude Desktop\n")

        print("2. 验证 MCP 服务器")
        print("   - 打开 Claude Code")
        print("   - 在聊天中输入: \"请使用 analyze_project 工具分析当前项目\"\n")

        print(f"{Colors.BOLD}可用工具:{Colors.END}")
        tools = [
            "analyze_project - 项目代码分析",
            "map_project_structure - 项目结构映射",
            "generate_dependency_graph - 依赖关系图",
            "identify_code_hotspots - 代码热点识别",
            "analyze_file_impact - 文件影响分析",
            "trace_function_calls - 函数调用追踪",
            "create_project_snapshot - 创建项目快照",
            "compare_snapshots - 快照对比",
            "export_analysis_data - 导出分析数据"
        ]
        for tool in tools:
            print(f"  • {tool}")

        print(f"\n{Colors.BOLD}配置文件位置:{Colors.END}")
        print(f"  {self.config_paths['config']}")

        print(f"\n{Colors.BOLD}查看详细文档:{Colors.END}")
        print(f"  {self.script_dir / 'MCP_SETUP.md'}")

    def run(self) -> int:
        """运行安装流程"""
        Colors.print_header("Code2Claude MCP 服务器一键安装")

        # 步骤 1: 检查 Python 版本
        if not self.check_python_version():
            return 1

        # 步骤 2: 安装依赖
        if not self.install_dependencies():
            Colors.print_error("\n安装失败: 无法安装依赖包")
            return 1

        # 步骤 3: 验证 MCP SDK
        if not self.verify_mcp_sdk():
            Colors.print_error("\n安装失败: MCP SDK 未正确安装")
            return 1

        # 步骤 4: 更新配置
        if not self.update_config():
            Colors.print_error("\n安装失败: 配置更新失败")
            return 1

        # 步骤 5: 验证安装
        if not self.verify_installation():
            Colors.print_error("\n安装失败: 验证未通过")
            return 1

        # 安装成功
        self.print_next_steps()
        return 0


def main():
    """主函数"""
    installer = MCPInstaller()
    return installer.run()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n安装已取消")
        sys.exit(1)
    except Exception as e:
        Colors.print_error(f"\n安装过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)