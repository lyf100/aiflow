"""
图表生成命令处理器
"""
from pathlib import Path
from typing import Dict, Any, List

from .base import BaseCommandHandler
from core.grapher import DependencyGrapher


class GraphCommandHandler(BaseCommandHandler):
    """graph命令处理器"""

    def execute(self, args: List[str]) -> Dict[str, Any]:
        """执行图表生成命令"""
        print("╔══════════════════════════════════════════════════════╗")
        print("║  正在生成依赖关系图...                               ║")
        print("╚══════════════════════════════════════════════════════╝")
        print()

        grapher = DependencyGrapher(str(self.project_path))

        # 生成所有类型的图
        self.print_progress("生成调用关系图", 1, 4)
        self.print_progress("分析模块依赖", 2, 4)
        self.print_progress("生成类层次图", 3, 4)
        self.print_progress("生成模块地图", 4, 4)

        generated_graphs = grapher.generate_all_graphs()

        print()
        print("✅ 依赖关系图生成完成")
        print()
        print("📊 生成的图表:")
        for graph_type, file_path in generated_graphs.items():
            rel_path, full_path = self.format_output_path(Path(file_path))

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


class AIContextCommandHandler(BaseCommandHandler):
    """ai-context命令处理器"""

    def execute(self, args: List[str]) -> Dict[str, Any]:
        """执行AI上下文生成命令"""
        from core.analyzer import CodeAnalyzer
        import json

        print("╔══════════════════════════════════════════════════════╗")
        print("║  正在生成AI上下文...                                 ║")
        print("╚══════════════════════════════════════════════════════╝")
        print()

        analyzer = CodeAnalyzer(str(self.project_path))

        self.print_progress("分析项目结构", 1, 3)
        analysis_result = analyzer.analyze_project()

        self.print_progress("提取关键组件", 2, 3)

        # 生成专门用于 Claude 的结构化上下文
        context_data = {
            "project_summary": {
                "name": self.project_path.name,
                "languages": list(analysis_result.get("languages", {}).keys()),
                "total_files": analysis_result.get("metrics", {}).get("total_files", 0),
                "code_lines": analysis_result.get("metrics", {}).get("code_lines", 0)
            },
            "structure_overview": analysis_result.get("structure", {}),
            "key_components": [],
            "dependencies": analysis_result.get("dependencies", {}),
            "context_for_claude": {
                "project_type": self._infer_project_type(analysis_result),
                "main_languages": list(analysis_result.get("languages", {}).keys())[:3],
                "complexity_level": self._assess_complexity(analysis_result),
                "recommendations": self._generate_context_recommendations(analysis_result)
            }
        }

        # 提取关键组件
        for lang, lang_data in analysis_result.get("languages", {}).items():
            functions = lang_data.get("functions", [])
            classes = lang_data.get("classes", [])

            context_data["key_components"].extend([
                {"type": "function", "name": func["name"], "file": func["file"], "language": lang}
                for func in functions[:5]
            ])
            context_data["key_components"].extend([
                {"type": "class", "name": cls["name"], "file": cls["file"], "language": lang}
                for cls in classes[:5]
            ])

        self.print_progress("生成上下文文件", 3, 3)

        # 保存上下文文件
        output_dir = self.project_path / "claudeflow"
        output_dir.mkdir(exist_ok=True)
        context_file = output_dir / "context.json"

        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(context_data, f, indent=2, ensure_ascii=False)

        print()
        print("✅ AI上下文生成完成")
        print()
        rel_path, full_path = self.format_output_path(context_file)
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

    def _infer_project_type(self, analysis_result: Dict[str, Any]) -> str:
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

    def _assess_complexity(self, analysis_result: Dict[str, Any]) -> str:
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

    def _generate_context_recommendations(self, analysis_result: Dict[str, Any]) -> list:
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