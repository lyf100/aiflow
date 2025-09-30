"""
测试项目映射器模块 (mapper.py)
"""
import pytest
import json
from pathlib import Path

from core.mapper import ProjectMapper


class TestProjectMapper:
    """测试ProjectMapper类"""

    def test_mapper_initialization(self, temp_project_dir):
        """测试映射器初始化"""
        mapper = ProjectMapper(str(temp_project_dir))

        assert mapper.project_path == temp_project_dir
        assert mapper.output_dir == temp_project_dir / "claudeflow"
        assert mapper.maps_dir == temp_project_dir / "claudeflow" / "maps"
        assert mapper.maps_dir.exists()

    def test_map_project_structure(self, sample_project_structure):
        """测试项目结构映射"""
        mapper = ProjectMapper(str(sample_project_structure))

        structure_map = mapper.map_project_structure()

        assert 'metadata' in structure_map
        assert 'overview' in structure_map
        assert 'directory_tree' in structure_map
        assert 'file_index' in structure_map
        assert 'patterns' in structure_map

    def test_structure_metadata(self, sample_project_structure):
        """测试结构元数据"""
        mapper = ProjectMapper(str(sample_project_structure))

        structure_map = mapper.map_project_structure()
        metadata = structure_map['metadata']

        assert 'project_name' in metadata
        assert 'project_path' in metadata
        assert 'timestamp' in metadata
        assert metadata['project_name'] == sample_project_structure.name

    def test_overview_statistics(self, sample_project_structure):
        """测试概览统计"""
        mapper = ProjectMapper(str(sample_project_structure))

        structure_map = mapper.map_project_structure()
        overview = structure_map['overview']

        assert 'total_files' in overview
        assert 'total_directories' in overview
        assert 'file_types' in overview
        assert overview['total_files'] > 0

    def test_directory_tree_structure(self, sample_project_structure):
        """测试目录树结构"""
        mapper = ProjectMapper(str(sample_project_structure))

        structure_map = mapper.map_project_structure()
        tree = structure_map['directory_tree']

        assert 'name' in tree
        assert 'type' in tree
        assert tree['type'] == 'directory'

    def test_file_patterns_identification(self, sample_project_structure):
        """测试文件模式识别"""
        mapper = ProjectMapper(str(sample_project_structure))

        structure_map = mapper.map_project_structure()
        patterns = structure_map['patterns']

        assert 'config_files' in patterns
        assert 'test_files' in patterns
        assert 'documentation' in patterns
        assert 'source_code' in patterns

    def test_map_code_structure(self, sample_project_structure):
        """测试代码结构映射"""
        mapper = ProjectMapper(str(sample_project_structure))

        code_map = mapper.map_code_structure()

        assert 'metadata' in code_map
        assert 'modules' in code_map
        assert 'functions' in code_map
        assert 'classes' in code_map

    def test_generate_interactive_map(self, sample_project_structure):
        """测试生成交互式地图"""
        mapper = ProjectMapper(str(sample_project_structure))

        html_file = mapper.generate_interactive_map()

        assert Path(html_file).exists()
        assert html_file.endswith('.html')

        # 验证HTML内容
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '<html' in content.lower()
        assert '</html>' in content.lower()

    def test_save_maps(self, sample_project_structure):
        """测试保存映射文件"""
        mapper = ProjectMapper(str(sample_project_structure))

        # 先生成映射
        mapper.map_project_structure()
        mapper.map_code_structure()

        # 保存
        saved_files = mapper.save_maps()

        assert isinstance(saved_files, dict)
        for file_path in saved_files.values():
            assert Path(file_path).exists()


class TestProjectMapperEdgeCases:
    """测试边界情况"""

    def test_empty_project_mapping(self, temp_project_dir):
        """测试空项目映射"""
        mapper = ProjectMapper(str(temp_project_dir))

        structure_map = mapper.map_project_structure()

        assert structure_map['overview']['total_files'] == 0

    def test_deep_directory_nesting(self, temp_project_dir):
        """测试深层目录嵌套"""
        # 创建12层深的目录
        deep_path = temp_project_dir
        for i in range(12):
            deep_path = deep_path / f"level{i}"
            deep_path.mkdir()

        (deep_path / "deep_file.txt").write_text("deep", encoding='utf-8')

        mapper = ProjectMapper(str(temp_project_dir))
        structure_map = mapper.map_project_structure()

        # 应该有截断处理
        assert 'directory_tree' in structure_map

    def test_special_characters_in_filenames(self, temp_project_dir):
        """测试文件名包含特殊字符"""
        special_file = temp_project_dir / "测试-文件 (1).txt"
        special_file.write_text("content", encoding='utf-8')

        mapper = ProjectMapper(str(temp_project_dir))
        structure_map = mapper.map_project_structure()

        assert structure_map['overview']['total_files'] > 0

    def test_permission_denied_handling(self, temp_project_dir, monkeypatch):
        """测试权限拒绝处理"""
        def mock_iterdir(self):
            raise PermissionError("Access denied")

        monkeypatch.setattr(Path, 'iterdir', mock_iterdir)

        mapper = ProjectMapper(str(temp_project_dir))

        # 应该优雅处理权限错误
        structure_map = mapper.map_project_structure()
        assert 'metadata' in structure_map