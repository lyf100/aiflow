"""
结构映射命令处理器
"""
from pathlib import Path
from typing import Dict, Any, List

from .base import BaseCommandHandler
from core.mapper import ProjectMapper


class StructureCommandHandler(BaseCommandHandler):
    """structure命令处理器"""

    def execute(self, args: List[str]) -> Dict[str, Any]:
        """执行结构映射命令"""
        print("╔══════════════════════════════════════════════════════╗")
        print("║  正在映射项目结构...                                 ║")
        print("╚══════════════════════════════════════════════════════╝")
        print()

        mapper = ProjectMapper(str(self.project_path))

        # 生成结构映射
        self.print_progress("扫描项目目录结构", 1, 4)
        structure_map = mapper.map_project_structure()
        success_msg = f"✅ 项目结构映射完成 ({structure_map['overview']['total_files']} 个文件)"
        print(self.colored(success_msg, 'green'))

        # 生成代码映射
        self.print_progress("分析代码结构", 2, 4)
        code_map = mapper.map_code_structure()
        print(self.colored("✅ 代码结构映射完成", 'green'))

        # 生成交互式地图
        self.print_progress("生成交互式地图", 3, 4)
        interactive_map = mapper.generate_interactive_map()
        print(self.colored("✅ 交互式地图已生成", 'green'))

        # 保存映射文件
        self.print_progress("保存映射文件", 4, 4)
        saved_files = mapper.save_maps()

        print()
        print(self.colored("📁 映射文件已保存:", 'blue'))
        for map_type, file_path in saved_files.items():
            rel_path, full_path = self.format_output_path(Path(file_path))
            print(f"   • {map_type:<12} {self.colored(rel_path, 'cyan')}")

        # 如果是HTML文件，提供打开提示
        if 'interactive' in saved_files:
            html_file = Path(saved_files['interactive'])
            print()
            hint = f"💡 在浏览器中查看: file://{html_file.absolute()}"
            print(self.colored(hint, 'yellow'))

        # 下一步建议
        print()
        print(self.colored("💡 下一步建议:", 'yellow'))
        print("   • claudeflow graph       - 生成依赖关系可视化")
        print("   • claudeflow hotspot     - 识别代码热点")
        print("   • claudeflow ai-context  - 生成AI分析上下文")

        return {
            "structure_map": structure_map,
            "code_map": code_map,
            "saved_files": saved_files
        }