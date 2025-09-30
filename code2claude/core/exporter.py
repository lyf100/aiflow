"""
数据导出器

导出分析数据到不同格式 (JSON/Markdown/HTML/CSV)
"""

import os
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class DataExporter:
    """数据导出器 - 支持多种格式导出"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.output_dir = self.project_path / "claudeflow" / "exports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_analysis_data(self, data: Dict[str, Any],
                           formats: List[str] = ['json', 'markdown']) -> Dict[str, str]:
        """
        导出分析数据到多种格式

        Args:
            data: 要导出的数据
            formats: 导出格式列表 ['json', 'markdown', 'html', 'csv']

        Returns:
            导出文件路径字典
        """
        exported_files = {}

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        for format_type in formats:
            if format_type == 'json':
                file_path = self._export_to_json(data, f"analysis_{timestamp}.json")
                exported_files['json'] = file_path

            elif format_type == 'markdown':
                file_path = self._export_to_markdown(data, f"analysis_{timestamp}.md")
                exported_files['markdown'] = file_path

            elif format_type == 'html':
                file_path = self._export_to_html(data, f"analysis_{timestamp}.html")
                exported_files['html'] = file_path

            elif format_type == 'csv':
                file_path = self._export_to_csv(data, f"analysis_{timestamp}.csv")
                exported_files['csv'] = file_path

        return exported_files

    def export_project_report(self, analysis_data: Dict[str, Any],
                            map_data: Dict[str, Any] = None,
                            graph_data: Dict[str, Any] = None,
                            tracking_data: Dict[str, Any] = None) -> str:
        """
        导出综合项目报告

        Args:
            analysis_data: 分析数据
            map_data: 映射数据
            graph_data: 图表数据
            tracking_data: 跟踪数据

        Returns:
            报告文件路径
        """
        report_data = {
            "metadata": {
                "project": analysis_data.get("metadata", {}).get("project_path", "Unknown"),
                "generated": datetime.now().isoformat(),
                "report_type": "comprehensive"
            },
            "executive_summary": self._generate_executive_summary(
                analysis_data, map_data, graph_data, tracking_data
            ),
            "analysis": analysis_data,
            "mapping": map_data,
            "graphs": graph_data,
            "tracking": tracking_data
        }

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 导出为 HTML 报告
        html_file = self._export_comprehensive_html_report(
            report_data, f"project_report_{timestamp}.html"
        )

        # 同时导出为 JSON
        json_file = self._export_to_json(
            report_data, f"project_report_{timestamp}.json"
        )

        return html_file

    def _export_to_json(self, data: Dict[str, Any], filename: str) -> str:
        """导出为 JSON 格式"""
        output_file = self.output_dir / filename

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        return str(output_file)

    def _export_to_markdown(self, data: Dict[str, Any], filename: str) -> str:
        """导出为 Markdown 格式"""
        output_file = self.output_dir / filename

        markdown_content = self._generate_markdown_content(data)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return str(output_file)

    def _export_to_html(self, data: Dict[str, Any], filename: str) -> str:
        """导出为 HTML 格式"""
        output_file = self.output_dir / filename

        html_content = self._generate_html_content(data)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file)

    def _export_to_csv(self, data: Dict[str, Any], filename: str) -> str:
        """导出为 CSV 格式"""
        output_file = self.output_dir / filename

        # 提取可以制表的数据
        csv_data = self._extract_tabular_data(data)

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if csv_data:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)
            else:
                # 如果没有表格数据，创建简单的摘要
                writer = csv.writer(f)
                writer.writerow(['Key', 'Value'])
                writer.writerow(['Project', data.get('metadata', {}).get('project_path', 'Unknown')])
                writer.writerow(['Generated', data.get('metadata', {}).get('timestamp', 'Unknown')])

        return str(output_file)

    def _generate_markdown_content(self, data: Dict[str, Any]) -> str:
        """生成 Markdown 内容"""
        metadata = data.get('metadata', {})

        content = f"""# 项目分析报告

## 基本信息

- **项目路径**: {metadata.get('project_path', 'Unknown')}
- **生成时间**: {metadata.get('timestamp', 'Unknown')}
- **版本**: {metadata.get('version', '1.0.0')}

## 项目概览

"""

        # 添加语言统计
        languages = data.get('languages', {})
        if languages:
            content += "### 编程语言\n\n"
            for lang, lang_data in languages.items():
                metrics = lang_data.get('metrics', {})
                content += f"- **{lang.upper()}**: {metrics.get('file_count', 0)} 文件, "
                content += f"{metrics.get('function_count', 0)} 函数, "
                content += f"{metrics.get('call_count', 0)} 调用\n"
            content += "\n"

        # 添加项目结构
        structure = data.get('structure', {})
        if structure:
            content += "### 项目结构\n\n"
            tree = structure.get('tree', {})
            if tree:
                content += self._tree_to_markdown(tree)
            content += "\n"

        # 添加依赖关系
        dependencies = data.get('dependencies', {})
        if dependencies:
            content += "### 依赖关系\n\n"
            external_deps = dependencies.get('external', {})
            for lang, deps in external_deps.items():
                if deps:
                    content += f"#### {lang.capitalize()} 依赖\n\n"
                    for dep in deps[:10]:  # 只显示前10个
                        content += f"- {dep}\n"
                    content += "\n"

        # 添加热点分析
        hotspots = data.get('hotspots', {})
        if hotspots:
            content += "### 代码热点\n\n"
            large_files = hotspots.get('large_files', [])
            if large_files:
                content += "#### 大文件\n\n"
                for file_info in large_files[:5]:
                    content += f"- **{file_info['path']}**: {file_info['size']} bytes, {file_info['lines']} 行\n"
                content += "\n"

        # 添加指标
        metrics = data.get('metrics', {})
        if metrics:
            content += "### 项目指标\n\n"
            content += f"- **总文件数**: {metrics.get('total_files', 0)}\n"
            content += f"- **代码行数**: {metrics.get('code_lines', 0)}\n"
            content += f"- **支持语言**: {metrics.get('languages', 0)}\n"

            file_counts = metrics.get('file_counts', {})
            if file_counts:
                content += "\n#### 文件类型分布\n\n"
                for ext, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    content += f"- **{ext or '无扩展名'}**: {count} 个文件\n"

        content += "\n---\n\n*报告由 ClaudeFlow 自动生成*\n"

        return content

    def _tree_to_markdown(self, tree: Dict[str, Any], level: int = 0) -> str:
        """将目录树转换为 Markdown"""
        content = ""
        indent = "  " * level

        if tree.get('type') == 'directory':
            content += f"{indent}- 📁 **{tree.get('name', 'Unknown')}**\n"
            for child in tree.get('children', [])[:10]:  # 限制显示数量
                content += self._tree_to_markdown(child, level + 1)
        else:
            name = tree.get('name', 'Unknown')
            size = tree.get('size', 0)
            content += f"{indent}- 📄 {name}"
            if size > 0:
                content += f" ({size // 1024:.0f} KB)"
            content += "\n"

        return content

    def _generate_html_content(self, data: Dict[str, Any]) -> str:
        """生成 HTML 内容"""
        metadata = data.get('metadata', {})

        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>项目分析报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .section {{
            padding: 20px 30px;
            border-bottom: 1px solid #eee;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .file-list {{
            max-height: 300px;
            overflow-y: auto;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
        }}
        .file-item {{
            padding: 5px 0;
            border-bottom: 1px solid #ddd;
        }}
        .file-item:last-child {{
            border-bottom: none;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            background: #e9ecef;
            border-radius: 4px;
            font-size: 0.9em;
            margin-left: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 项目分析报告</h1>
            <p><strong>项目:</strong> {project_name}</p>
            <p><strong>生成时间:</strong> {timestamp}</p>
        </div>

        {content_sections}
    </div>
</body>
</html>
        """

        # 生成内容部分
        content_sections = ""

        # 项目概览
        content_sections += self._generate_overview_section(data)

        # 语言统计
        if data.get('languages'):
            content_sections += self._generate_languages_section(data['languages'])

        # 项目指标
        if data.get('metrics'):
            content_sections += self._generate_metrics_section(data['metrics'])

        # 热点分析
        if data.get('hotspots'):
            content_sections += self._generate_hotspots_section(data['hotspots'])

        return html_template.format(
            project_name=metadata.get('project_path', 'Unknown'),
            timestamp=metadata.get('timestamp', 'Unknown'),
            content_sections=content_sections
        )

    def _generate_overview_section(self, data: Dict[str, Any]) -> str:
        """生成概览部分"""
        overview = data.get('metrics', {})

        return f"""
        <div class="section">
            <h2>📈 项目概览</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>总文件数</h3>
                    <div class="stat-value">{overview.get('total_files', 0)}</div>
                </div>
                <div class="stat-card">
                    <h3>代码行数</h3>
                    <div class="stat-value">{overview.get('code_lines', 0):,}</div>
                </div>
                <div class="stat-card">
                    <h3>编程语言</h3>
                    <div class="stat-value">{overview.get('languages', 0)}</div>
                </div>
            </div>
        </div>
        """

    def _generate_languages_section(self, languages: Dict[str, Any]) -> str:
        """生成语言部分"""
        content = """
        <div class="section">
            <h2>💻 编程语言</h2>
            <table>
                <tr>
                    <th>语言</th>
                    <th>文件数</th>
                    <th>函数数</th>
                    <th>调用数</th>
                </tr>
        """

        for lang, lang_data in languages.items():
            metrics = lang_data.get('metrics', {})
            content += f"""
                <tr>
                    <td><strong>{lang.upper()}</strong></td>
                    <td>{metrics.get('file_count', 0)}</td>
                    <td>{metrics.get('function_count', 0)}</td>
                    <td>{metrics.get('call_count', 0)}</td>
                </tr>
            """

        content += """
            </table>
        </div>
        """

        return content

    def _generate_metrics_section(self, metrics: Dict[str, Any]) -> str:
        """生成指标部分"""
        file_counts = metrics.get('file_counts', {})

        content = """
        <div class="section">
            <h2>📊 文件类型分布</h2>
            <div class="file-list">
        """

        for ext, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
            content += f"""
                <div class="file-item">
                    <strong>{ext or '无扩展名'}</strong>
                    <span class="badge">{count} 个文件</span>
                </div>
            """

        content += """
            </div>
        </div>
        """

        return content

    def _generate_hotspots_section(self, hotspots: Dict[str, Any]) -> str:
        """生成热点部分"""
        large_files = hotspots.get('large_files', [])

        content = """
        <div class="section">
            <h2>🔥 代码热点</h2>
            <h3>大文件 (>10KB)</h3>
            <table>
                <tr>
                    <th>文件路径</th>
                    <th>大小</th>
                    <th>行数</th>
                </tr>
        """

        for file_info in large_files[:10]:
            size_kb = file_info['size'] / 1024
            content += f"""
                <tr>
                    <td>{file_info['path']}</td>
                    <td>{size_kb:.1f} KB</td>
                    <td>{file_info['lines']}</td>
                </tr>
            """

        content += """
            </table>
        </div>
        """

        return content

    def _export_comprehensive_html_report(self, report_data: Dict[str, Any],
                                        filename: str) -> str:
        """导出综合 HTML 报告"""
        output_file = self.output_dir / filename

        html_content = self._generate_comprehensive_html(report_data)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file)

    def _generate_comprehensive_html(self, report_data: Dict[str, Any]) -> str:
        """生成综合 HTML 报告"""
        metadata = report_data.get('metadata', {})

        template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>项目综合报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        .nav {{
            background: white;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .nav ul {{
            list-style: none;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
        }}
        .nav li {{
            margin: 0 15px;
        }}
        .nav a {{
            text-decoration: none;
            color: #667eea;
            font-weight: bold;
            padding: 10px 15px;
            border-radius: 5px;
            transition: background-color 0.3s;
        }}
        .nav a:hover {{
            background-color: #f0f0f0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .section {{
            background: white;
            margin: 20px 0;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 25px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 25px 0;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #667eea;
        }}
        .summary-card h3 {{
            margin: 0 0 15px 0;
            color: #333;
        }}
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .summary-card .description {{
            color: #666;
            font-size: 0.9em;
        }}
        .footer {{
            text-align: center;
            padding: 40px 20px;
            background: #333;
            color: white;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 项目综合分析报告</h1>
        <p><strong>项目:</strong> {project_name}</p>
        <p><strong>生成时间:</strong> {generated_time}</p>
    </div>

    <nav class="nav">
        <ul>
            <li><a href="#summary">执行摘要</a></li>
            <li><a href="#analysis">代码分析</a></li>
            <li><a href="#mapping">项目映射</a></li>
            <li><a href="#graphs">依赖图表</a></li>
            <li><a href="#tracking">变更跟踪</a></li>
        </ul>
    </nav>

    <div class="container">
        {content_sections}
    </div>

    <div class="footer">
        <p>📊 报告由 ClaudeFlow 综合分析系统生成</p>
        <p>基于 code2flow 引擎的增强代码分析平台</p>
    </div>
</body>
</html>
        """

        # 生成各个部分的内容
        content_sections = ""

        # 执行摘要
        exec_summary = report_data.get('executive_summary', {})
        if exec_summary:
            content_sections += f"""
            <div id="summary" class="section">
                <h2>📋 执行摘要</h2>
                <div class="summary-grid">
                    <div class="summary-card">
                        <h3>项目规模</h3>
                        <div class="value">{exec_summary.get('total_files', 0)}</div>
                        <div class="description">总文件数</div>
                    </div>
                    <div class="summary-card">
                        <h3>代码质量</h3>
                        <div class="value">{exec_summary.get('quality_score', 0):.1f}</div>
                        <div class="description">质量评分 (1-10)</div>
                    </div>
                    <div class="summary-card">
                        <h3>技术债务</h3>
                        <div class="value">{exec_summary.get('tech_debt', 0)}</div>
                        <div class="description">需要重构的文件数</div>
                    </div>
                    <div class="summary-card">
                        <h3>维护指数</h3>
                        <div class="value">{exec_summary.get('maintainability', 'Good')}</div>
                        <div class="description">可维护性评级</div>
                    </div>
                </div>
                <p><strong>主要发现:</strong></p>
                <ul>
                    {''.join(f'<li>{finding}</li>' for finding in exec_summary.get('key_findings', []))}
                </ul>
            </div>
            """

        # 其他部分的内容...
        analysis = report_data.get('analysis', {})
        if analysis:
            content_sections += f"""
            <div id="analysis" class="section">
                <h2>🔍 代码分析</h2>
                <p>分析了 {len(analysis.get('languages', {}))} 种编程语言的代码结构和依赖关系。</p>
                {self._generate_languages_section(analysis.get('languages', {}))}
            </div>
            """

        # 添加其他部分...
        content_sections += """
        <div id="mapping" class="section">
            <h2>🗺️ 项目映射</h2>
            <p>项目结构映射和代码地图已生成，详细信息请查看相关的映射文件。</p>
        </div>

        <div id="graphs" class="section">
            <h2>📊 依赖图表</h2>
            <p>依赖关系图和调用图已生成，详细图表请查看 graphs 目录。</p>
        </div>

        <div id="tracking" class="section">
            <h2>📈 变更跟踪</h2>
            <p>代码热点和变更历史分析已完成，详细跟踪数据请查看 tracking 目录。</p>
        </div>
        """

        return template.format(
            project_name=metadata.get('project', 'Unknown'),
            generated_time=metadata.get('generated', 'Unknown'),
            content_sections=content_sections
        )

    def _extract_tabular_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取可以制表的数据"""
        tabular_data = []

        # 提取语言统计数据
        languages = data.get('languages', {})
        for lang, lang_data in languages.items():
            metrics = lang_data.get('metrics', {})
            tabular_data.append({
                'Type': 'Language',
                'Name': lang.upper(),
                'Files': metrics.get('file_count', 0),
                'Functions': metrics.get('function_count', 0),
                'Calls': metrics.get('call_count', 0)
            })

        # 提取大文件数据
        hotspots = data.get('hotspots', {})
        large_files = hotspots.get('large_files', [])
        for file_info in large_files[:20]:  # 限制数量
            tabular_data.append({
                'Type': 'Large File',
                'Name': file_info['path'],
                'Size_KB': round(file_info['size'] / 1024, 1),
                'Lines': file_info['lines'],
                'Extension': Path(file_info['path']).suffix
            })

        return tabular_data

    def _generate_executive_summary(self, analysis_data: Dict[str, Any],
                                   map_data: Dict[str, Any] = None,
                                   graph_data: Dict[str, Any] = None,
                                   tracking_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成执行摘要"""
        summary = {
            "total_files": 0,
            "quality_score": 7.5,  # 默认评分
            "tech_debt": 0,
            "maintainability": "Good",
            "key_findings": []
        }

        # 从分析数据提取信息
        if analysis_data:
            metrics = analysis_data.get('metrics', {})
            summary["total_files"] = metrics.get('total_files', 0)

            # 简单的质量评分算法
            languages_count = metrics.get('languages', 0)
            if languages_count > 3:
                summary["quality_score"] -= 0.5

            hotspots = analysis_data.get('hotspots', {})
            large_files = hotspots.get('large_files', [])
            summary["tech_debt"] = len(large_files)

            if len(large_files) > 10:
                summary["maintainability"] = "Needs Attention"
                summary["key_findings"].append("发现多个大文件，建议进行重构")

            if languages_count > 1:
                summary["key_findings"].append(f"项目使用了 {languages_count} 种编程语言")

        # 默认发现
        if not summary["key_findings"]:
            summary["key_findings"] = [
                "项目结构分析完成",
                "代码质量评估已生成",
                "建议定期进行代码审查"
            ]

        return summary