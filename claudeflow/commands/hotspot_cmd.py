"""
热点识别命令处理器
"""
import json
from pathlib import Path
from typing import Dict, Any, List

from .base import BaseCommandHandler
from core.tracker import ChangeTracker


class HotspotCommandHandler(BaseCommandHandler):
    """hotspot命令处理器"""

    def execute(self, args: List[str]) -> Dict[str, Any]:
        """执行热点识别命令"""
        print("╔══════════════════════════════════════════════════════╗")
        print("║  正在识别代码热点...                                 ║")
        print("╚══════════════════════════════════════════════════════╝")
        print()

        tracker = ChangeTracker(str(self.project_path))
        days = self.options.get('days', 30)

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
        output_file = self.project_path / "claudeflow" / "tracking" / "hotspots.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(hotspots, f, indent=2, ensure_ascii=False)

        rel_path, full_path = self.format_output_path(output_file)
        print(f"📁 详细报告: {rel_path}")

        return {
            "hotspots": hotspots,
            "output_file": str(output_file)
        }