"""
测试命令处理器模块
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from commands.base import BaseCommandHandler
from commands.structure_cmd import StructureCommandHandler
from commands.refresh_cmd import RefreshCommandHandler
from commands.hotspot_cmd import HotspotCommandHandler
from commands.graph_cmd import GraphCommandHandler, AIContextCommandHandler
from commands.registry import get_command_handler, COMMAND_HANDLERS


class TestBaseCommandHandler:
    """测试基类命令处理器"""

    def test_initialization(self, temp_project_dir):
        """测试命令处理器初始化"""
        options = {
            'config': {
                'output': {'colorful': True}
            }
        }

        # 需要一个具体实现来测试抽象基类
        class ConcreteHandler(BaseCommandHandler):
            def execute(self, args):
                return {"success": True}

        handler = ConcreteHandler(str(temp_project_dir), options)

        assert handler.project_path == temp_project_dir
        assert handler.use_color == True
        assert handler.config == options['config']

    def test_colored_with_colorama(self, temp_project_dir):
        """测试彩色文本输出"""
        options = {'config': {'output': {'colorful': True}}}

        class ConcreteHandler(BaseCommandHandler):
            def execute(self, args):
                return {}

        handler = ConcreteHandler(str(temp_project_dir), options)

        # 测试彩色输出
        colored_text = handler.colored("test", "red", "bright")
        assert isinstance(colored_text, str)
        assert "test" in colored_text

    def test_colored_disabled(self, temp_project_dir):
        """测试禁用彩色输出"""
        options = {'config': {'output': {'colorful': False}}}

        class ConcreteHandler(BaseCommandHandler):
            def execute(self, args):
                return {}

        handler = ConcreteHandler(str(temp_project_dir), options)

        colored_text = handler.colored("test", "red")
        assert colored_text == "test"

    def test_format_output_path(self, temp_project_dir):
        """测试路径格式化"""
        options = {'config': {}}

        class ConcreteHandler(BaseCommandHandler):
            def execute(self, args):
                return {}

        handler = ConcreteHandler(str(temp_project_dir), options)

        test_file = temp_project_dir / "test.txt"
        rel_path, abs_path = handler.format_output_path(test_file)

        assert rel_path == "test.txt"
        assert abs_path == str(test_file.absolute())

    def test_confirm_operation(self, temp_project_dir, monkeypatch):
        """测试操作确认"""
        options = {'config': {}}

        class ConcreteHandler(BaseCommandHandler):
            def execute(self, args):
                return {}

        handler = ConcreteHandler(str(temp_project_dir), options)

        # 模拟用户输入 'y'
        monkeypatch.setattr('builtins.input', lambda _: 'y')
        assert handler.confirm_operation("test") == True

        # 模拟用户输入 'n'
        monkeypatch.setattr('builtins.input', lambda _: 'n')
        assert handler.confirm_operation("test") == False


class TestStructureCommandHandler:
    """测试structure命令处理器"""

    @patch('commands.structure_cmd.ProjectMapper')
    def test_execute_success(self, mock_mapper_class, sample_project_structure):
        """测试成功执行structure命令"""
        # 配置mock
        mock_mapper = Mock()
        mock_mapper_class.return_value = mock_mapper

        mock_mapper.map_project_structure.return_value = {
            'overview': {'total_files': 10}
        }
        mock_mapper.map_code_structure.return_value = {}
        mock_mapper.generate_interactive_map.return_value = "/path/map.html"
        mock_mapper.save_maps.return_value = {
            'structure': '/path/structure.json',
            'interactive': '/path/map.html'
        }

        options = {'config': {'output': {'colorful': False}}}
        handler = StructureCommandHandler(str(sample_project_structure), options)

        result = handler.execute([])

        assert 'structure_map' in result
        assert 'code_map' in result
        assert 'saved_files' in result
        assert mock_mapper.map_project_structure.called
        assert mock_mapper.map_code_structure.called


class TestRefreshCommandHandler:
    """测试refresh命令处理器"""

    @patch('commands.refresh_cmd.ProjectMapper')
    @patch('commands.refresh_cmd.CodeAnalyzer')
    def test_execute_with_force(self, mock_analyzer_class, mock_mapper_class,
                                sample_project_structure):
        """测试使用--force标志执行refresh命令"""
        # 配置mocks
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.analyze_project.return_value = {'test': 'data'}
        mock_analyzer.save_analysis.return_value = '/path/analysis.json'

        mock_mapper = Mock()
        mock_mapper_class.return_value = mock_mapper

        options = {
            'config': {'output': {'colorful': False}},
            'force': True
        }
        handler = RefreshCommandHandler(str(sample_project_structure), options)

        result = handler.execute([])

        assert 'analysis_result' in result
        assert 'output_file' in result
        assert not result.get('cancelled')

    def test_execute_cancelled(self, sample_project_structure, monkeypatch):
        """测试取消refresh命令"""
        # 模拟用户输入 'n'
        monkeypatch.setattr('builtins.input', lambda _: 'n')

        options = {
            'config': {'output': {'colorful': False}},
            'force': False
        }
        handler = RefreshCommandHandler(str(sample_project_structure), options)

        result = handler.execute([])

        assert result.get('cancelled') == True


class TestHotspotCommandHandler:
    """测试hotspot命令处理器"""

    @patch('commands.hotspot_cmd.ChangeTracker')
    def test_execute_success(self, mock_tracker_class, sample_project_structure):
        """测试成功执行hotspot命令"""
        # 配置mock
        mock_tracker = Mock()
        mock_tracker_class.return_value = mock_tracker

        mock_tracker.identify_hotspots.return_value = {
            'frequency_hotspots': [
                {'file': 'test.py', 'change_count': 15}
            ],
            'complexity_hotspots': [
                {'file': 'complex.py', 'complexity_score': 9.5}
            ],
            'size_hotspots': [
                {'file': 'large.py', 'size': 50000, 'lines': 1000}
            ],
            'recommendations': ['建议重构大文件']
        }

        options = {
            'config': {'output': {'colorful': False}},
            'days': 30
        }
        handler = HotspotCommandHandler(str(sample_project_structure), options)

        result = handler.execute([])

        assert 'hotspots' in result
        assert 'output_file' in result
        mock_tracker.identify_hotspots.assert_called_once_with(30)


class TestGraphCommandHandler:
    """测试graph命令处理器"""

    @patch('commands.graph_cmd.DependencyGrapher')
    def test_execute_success(self, mock_grapher_class, sample_project_structure):
        """测试成功执行graph命令"""
        # 配置mock
        mock_grapher = Mock()
        mock_grapher_class.return_value = mock_grapher

        mock_grapher.generate_all_graphs.return_value = {
            'call_graph': '/path/call.html',
            'dependency_graph': '/path/dep.html'
        }

        options = {'config': {'output': {'colorful': False}}}
        handler = GraphCommandHandler(str(sample_project_structure), options)

        result = handler.execute([])

        assert 'generated_graphs' in result
        assert len(result['generated_graphs']) > 0


class TestAIContextCommandHandler:
    """测试ai-context命令处理器"""

    @patch('core.analyzer.CodeAnalyzer')
    def test_execute_success(self, mock_analyzer_class, sample_project_structure):
        """测试成功执行ai-context命令"""
        # 配置mock
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer

        mock_analyzer.analyze_project.return_value = {
            'languages': {'py': {}},
            'metrics': {
                'total_files': 10,
                'code_lines': 500
            },
            'structure': {},
            'dependencies': {}
        }

        options = {'config': {'output': {'colorful': False}}}
        handler = AIContextCommandHandler(str(sample_project_structure), options)

        result = handler.execute([])

        assert 'context_data' in result
        assert 'context_file' in result
        assert 'project_summary' in result['context_data']

    def test_infer_project_type_python(self, sample_project_structure):
        """测试推断Python项目类型"""
        options = {'config': {}}
        handler = AIContextCommandHandler(str(sample_project_structure), options)

        analysis_result = {'languages': {'py': {}}}
        project_type = handler._infer_project_type(analysis_result)

        assert project_type == "Python Project"

    def test_assess_complexity_high(self, sample_project_structure):
        """测试评估高复杂度项目"""
        options = {'config': {}}
        handler = AIContextCommandHandler(str(sample_project_structure), options)

        analysis_result = {
            'metrics': {
                'total_files': 150,
                'languages': 3
            }
        }
        complexity = handler._assess_complexity(analysis_result)

        assert complexity == "High"


class TestCommandRegistry:
    """测试命令注册表"""

    def test_get_command_handler_valid(self, temp_project_dir):
        """测试获取有效的命令处理器"""
        options = {'config': {}}

        handler = get_command_handler('structure', str(temp_project_dir), options)

        assert isinstance(handler, StructureCommandHandler)

    def test_get_command_handler_invalid(self, temp_project_dir):
        """测试获取无效的命令处理器"""
        options = {'config': {}}

        with pytest.raises(ValueError, match="Unknown command"):
            get_command_handler('invalid_command', str(temp_project_dir), options)

    def test_all_handlers_registered(self):
        """测试所有命令处理器都已注册"""
        expected_commands = ['structure', 'refresh', 'hotspot', 'graph', 'ai-context']

        for cmd in expected_commands:
            assert cmd in COMMAND_HANDLERS
            assert COMMAND_HANDLERS[cmd] is not None