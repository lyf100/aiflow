#!/usr/bin/env python3
"""
Code2Claude MCP 卸载脚本

自动卸载 MCP 服务器配置，恢复原始状态
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional


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


class MCPUninstaller:
    """MCP 服务器卸载器"""

    def __init__(self):
        self.config_path = self._get_config_path()

    def _get_config_path(self) -> Path:
        """获取 Claude Desktop 配置文件路径"""
        system = sys.platform

        if system == "win32":
            base = Path(os.environ.get("APPDATA", "")) / "Claude"
        elif system == "darwin":
            base = Path.home() / "Library" / "Application Support" / "Claude"
        else:  # Linux
            base = Path.home() / ".config" / "Claude"

        return base / "claude_desktop_config.json"

    def remove_from_config(self) -> bool:
        """从配置中移除 Code2Claude"""
        Colors.print_info("正在移除 Code2Claude 配置...")

        if not self.config_path.exists():
            Colors.print_warning("配置文件不存在，无需卸载")
            return True

        try:
            # 读取配置
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 检查是否存在 Code2Claude
            if "mcpServers" not in config or "code2claude" not in config["mcpServers"]:
                Colors.print_warning("配置中未找到 Code2Claude，无需卸载")
                return True

            # 移除 Code2Claude
            del config["mcpServers"]["code2claude"]
            Colors.print_success("已从配置中移除 Code2Claude")

            # 如果 mcpServers 为空，也可以选择删除整个键
            if not config["mcpServers"]:
                Colors.print_info("mcpServers 为空，保留空配置")

            # 写回配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            Colors.print_success(f"配置已更新: {self.config_path}")
            return True

        except Exception as e:
            Colors.print_error(f"配置更新失败: {e}")
            return False

    def uninstall_dependencies(self, keep_dependencies: bool = True) -> bool:
        """卸载依赖（可选）"""
        if keep_dependencies:
            Colors.print_info("保留依赖包（可手动运行: pip uninstall mcp pyyaml colorama）")
            return True

        Colors.print_info("正在卸载依赖包...")

        packages = ["mcp", "pyyaml", "colorama"]

        try:
            for package in packages:
                subprocess.run(
                    [sys.executable, "-m", "pip", "uninstall", "-y", package],
                    capture_output=True
                )

            Colors.print_success("依赖包已卸载")
            return True

        except Exception as e:
            Colors.print_warning(f"依赖包卸载失败: {e}")
            return False

    def print_completion_message(self):
        """打印完成信息"""
        Colors.print_header("卸载完成")

        print(f"{Colors.GREEN}✓{Colors.END} Code2Claude MCP 服务器已卸载\n")

        print(f"{Colors.BOLD}后续操作:{Colors.END}\n")
        print("1. 重启 Claude Desktop 使配置生效")
        print("2. 如需完全卸载，可手动删除项目目录")
        print("3. 如需卸载依赖包，运行:")
        print("   pip uninstall mcp pyyaml colorama\n")

    def run(self, keep_dependencies: bool = True) -> int:
        """运行卸载流程"""
        Colors.print_header("Code2Claude MCP 服务器卸载")

        # 确认卸载
        response = input(f"{Colors.YELLOW}确认卸载 Code2Claude MCP 服务器? (y/N): {Colors.END}")
        if response.lower() not in ['y', 'yes']:
            Colors.print_info("卸载已取消")
            return 0

        # 步骤 1: 从配置中移除
        if not self.remove_from_config():
            Colors.print_error("\n卸载失败: 无法更新配置")
            return 1

        # 步骤 2: 卸载依赖（可选）
        self.uninstall_dependencies(keep_dependencies)

        # 卸载成功
        self.print_completion_message()
        return 0


def main():
    """主函数"""
    # 解析参数
    keep_deps = True
    if len(sys.argv) > 1 and sys.argv[1] == "--remove-deps":
        keep_deps = False

    uninstaller = MCPUninstaller()
    return uninstaller.run(keep_dependencies=keep_deps)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n卸载已取消")
        sys.exit(1)
    except Exception as e:
        Colors.print_error(f"\n卸载过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)