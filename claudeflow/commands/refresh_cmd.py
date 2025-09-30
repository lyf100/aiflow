"""
刷新命令处理器
"""
from pathlib import Path
from typing import Dict, Any, List

from .base import BaseCommandHandler
from core.analyzer import CodeAnalyzer
from core.mapper import ProjectMapper


class RefreshCommandHandler(BaseCommandHandler):
    """refresh命令处理器"""

    def execute(self, args: List[str]) -> Dict[str, Any]:
        """执行刷新命令"""
        if not self.options.get('force'):
            if not self.confirm_operation(
                "刷新项目分析数据",
                "此操作会重新分析整个项目并覆盖现有数据，大型项目可能需要较长时间"
            ):
                print("❌ 操作已取消")
                return {"cancelled": True}

        print("╔══════════════════════════════════════════════════════╗")
        print("║  正在刷新项目分析数据...                             ║")
        print("╚══════════════════════════════════════════════════════╝")
        print()

        analyzer = CodeAnalyzer(str(self.project_path))

        # 重新分析项目
        self.print_progress("重新扫描项目文件", 1, 3)
        analysis_result = analyzer.analyze_project()
        print("✅ 项目分析完成")

        # 保存分析结果
        self.print_progress("保存分析结果", 2, 3)
        output_file = analyzer.save_analysis()
        rel_path, full_path = self.format_output_path(Path(output_file))
        print(f"✅ 分析结果已保存: {rel_path}")

        # 更新映射
        self.print_progress("更新项目映射", 3, 3)
        mapper = ProjectMapper(str(self.project_path))
        mapper.save_maps()
        print("✅ 项目映射已更新")

        print()
        print("💡 刷新完成，所有分析数据已更新为最新状态")

        return {
            "analysis_result": analysis_result,
            "output_file": output_file
        }