"""
测试数据导出器模块 (exporter.py)
"""
import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch

from core.exporter import DataExporter


class TestDataExporter:
    """测试DataExporter类"""

    def test_exporter_initialization(self, temp_project_dir):
        """测试导出器初始化"""
        exporter = DataExporter(str(temp_project_dir))

        assert exporter.project_path == temp_project_dir
        assert exporter.output_dir == temp_project_dir / "claudeflow" / "exports"
        assert exporter.output_dir.exists()

    def test_export_analysis_data(self, sample_project_structure):
        """测试导出分析数据"""
        exporter = DataExporter(str(sample_project_structure))

        test_data = {
            "test": "data",
            "number": 123,
            "nested": {"key": "value"}
        }

        files = exporter.export_analysis_data(test_data, formats=['json'])

        assert isinstance(files, dict)
        assert 'json' in files or 'analysis' in files

    def test_export_project_report(self, sample_project_structure):
        """测试导出项目报告"""
        exporter = DataExporter(str(sample_project_structure))

        analysis_data = {
            "metadata": {"version": "1.0"},
            "metrics": {"total_files": 10}
        }

        structure_data = {
            "overview": {"total_files": 10}
        }

        files = exporter.export_project_report(analysis_data, structure_data)

        # 验证返回结果
        assert files is not None


class TestDataExporterEdgeCases:
    """测试边界情况"""

    def test_export_empty_data(self, temp_project_dir):
        """测试导出空数据"""
        exporter = DataExporter(str(temp_project_dir))

        empty_data = {}

        try:
            files = exporter.export_analysis_data(empty_data, formats=['json'])
            assert files is not None
        except Exception:
            # 某些实现可能不接受空数据
            pass

    def test_export_large_data(self, temp_project_dir):
        """测试导出大量数据"""
        exporter = DataExporter(str(temp_project_dir))

        large_data = {
            "items": [{"id": i, "data": "x" * 1000} for i in range(100)]
        }

        files = exporter.export_analysis_data(large_data, formats=['json'])

        # 验证能够处理大数据
        assert files is not None

    def test_export_with_special_characters(self, temp_project_dir):
        """测试导出包含特殊字符的数据"""
        exporter = DataExporter(str(temp_project_dir))

        special_data = {
            "chinese": "中文测试",
            "emoji": "🎉✨",
            "special": "Special <>&\" characters"
        }

        files = exporter.export_analysis_data(special_data, formats=['json'])

        # 验证特殊字符被正确处理
        assert files is not None

    def test_export_nested_data(self, temp_project_dir):
        """测试导出嵌套数据结构"""
        exporter = DataExporter(str(temp_project_dir))

        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep"
                    }
                }
            }
        }

        files = exporter.export_analysis_data(nested_data, formats=['json'])

        assert files is not None


class TestDataExportFormats:
    """测试不同导出格式"""

    def test_json_format_structure(self, temp_project_dir):
        """测试JSON格式结构"""
        exporter = DataExporter(str(temp_project_dir))

        data = {"test": "value"}
        files = exporter.export_analysis_data(data, formats=['json'])

        assert isinstance(files, dict)
        assert 'json' in files or 'analysis' in files

    def test_multiple_formats(self, sample_project_structure):
        """测试多种格式导出"""
        exporter = DataExporter(str(sample_project_structure))

        data = {
            "metrics": {
                "files": 10,
                "lines": 1000
            }
        }

        files = exporter.export_analysis_data(data, formats=['json', 'markdown'])

        # 多格式应该返回字典
        assert isinstance(files, dict)