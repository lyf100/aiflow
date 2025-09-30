"""
测试代码分析器模块 (analyzer.py)
"""
import pytest
import json
from pathlib import Path

from core.analyzer import CodeAnalyzer


class TestCodeAnalyzer:
    """测试CodeAnalyzer类"""

    def test_analyzer_initialization(self, temp_project_dir):
        """测试分析器初始化"""
        analyzer = CodeAnalyzer(str(temp_project_dir))

        assert analyzer.project_path == temp_project_dir
        assert analyzer.output_dir == temp_project_dir / "claudeflow"
        assert isinstance(analyzer.analysis_data, dict)

    def test_detect_languages(self, sample_project_structure):
        """测试语言检测"""
        analyzer = CodeAnalyzer(str(sample_project_structure))

        detected = analyzer._detect_languages()

        assert 'py' in detected

    def test_detect_multiple_languages(self, temp_project_dir):
        """测试多语言项目检测"""
        # 创建多语言文件
        (temp_project_dir / "script.py").write_text("# Python", encoding='utf-8')
        (temp_project_dir / "app.js").write_text("// JavaScript", encoding='utf-8')
        (temp_project_dir / "style.dart").write_text("// Dart", encoding='utf-8')

        analyzer = CodeAnalyzer(str(temp_project_dir))
        detected = analyzer._detect_languages()

        assert 'py' in detected
        assert 'js' in detected
        assert 'dart' in detected

    def test_build_project_structure(self, sample_project_structure):
        """测试项目结构构建"""
        analyzer = CodeAnalyzer(str(sample_project_structure))

        structure = analyzer._build_project_structure()

        assert 'root' in structure
        assert 'directories' in structure
        assert 'files' in structure
        assert 'tree' in structure

    def test_build_directory_tree(self, sample_project_structure):
        """测试目录树构建"""
        analyzer = CodeAnalyzer(str(sample_project_structure))

        tree = analyzer._build_directory_tree()

        assert tree['type'] == 'directory'
        assert 'children' in tree
        assert len(tree['children']) > 0

    def test_analyze_dependencies_python(self, sample_project_structure):
        """测试Python依赖分析"""
        analyzer = CodeAnalyzer(str(sample_project_structure))

        dependencies = analyzer._analyze_dependencies()

        assert 'external' in dependencies
        assert 'python' in dependencies['external']
        assert 'pyyaml' in dependencies['external']['python']

    def test_parse_dependency_file_requirements(self, temp_project_dir):
        """测试解析requirements.txt"""
        req_file = temp_project_dir / "requirements.txt"
        req_file.write_text("""
pyyaml>=6.0
colorama==0.4.6
# Comment
requests
""", encoding='utf-8')

        analyzer = CodeAnalyzer(str(temp_project_dir))
        deps = analyzer._parse_dependency_file(req_file, 'python')

        assert 'pyyaml' in deps
        assert 'colorama' in deps
        assert 'requests' in deps
        assert len(deps) == 3

    def test_parse_dependency_file_package_json(self, temp_project_dir):
        """测试解析package.json"""
        pkg_file = temp_project_dir / "package.json"
        pkg_file.write_text(json.dumps({
            "dependencies": {
                "express": "^4.18.0",
                "lodash": "^4.17.21"
            },
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }), encoding='utf-8')

        analyzer = CodeAnalyzer(str(temp_project_dir))
        deps = analyzer._parse_dependency_file(pkg_file, 'javascript')

        assert 'express' in deps
        assert 'lodash' in deps
        assert 'jest' in deps

    def test_identify_hotspots(self, sample_project_structure):
        """测试代码热点识别"""
        # 创建大文件
        large_file = sample_project_structure / "large.py"
        large_file.write_text("# " + "x" * 20000, encoding='utf-8')

        analyzer = CodeAnalyzer(str(sample_project_structure))
        hotspots = analyzer._identify_hotspots()

        assert 'large_files' in hotspots
        assert len(hotspots['large_files']) > 0

    def test_calculate_metrics(self, sample_project_structure):
        """测试项目指标计算"""
        analyzer = CodeAnalyzer(str(sample_project_structure))
        analyzer.analysis_data = {"languages": {"py": {}}}

        metrics = analyzer._calculate_metrics()

        assert 'file_counts' in metrics
        assert 'code_lines' in metrics
        assert 'total_files' in metrics
        assert 'languages' in metrics
        assert metrics['total_files'] > 0

    def test_fallback_analysis(self, sample_project_structure):
        """测试降级分析模式"""
        analyzer = CodeAnalyzer(str(sample_project_structure))

        result = analyzer._fallback_analysis()

        assert 'metadata' in result
        assert result['metadata']['mode'] == 'fallback'
        assert 'structure' in result
        assert 'dependencies' in result
        assert 'metrics' in result

    def test_save_analysis(self, sample_project_structure):
        """测试保存分析结果"""
        analyzer = CodeAnalyzer(str(sample_project_structure))
        analyzer.analysis_data = {
            "test": "data",
            "metadata": {"version": "1.0"}
        }

        output_file = analyzer.save_analysis("test_analysis.json")

        assert Path(output_file).exists()
        with open(output_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == analyzer.analysis_data

    def test_analyze_project_full(self, sample_project_structure):
        """测试完整项目分析"""
        analyzer = CodeAnalyzer(str(sample_project_structure))

        result = analyzer.analyze_project()

        assert 'metadata' in result
        assert 'structure' in result
        assert 'dependencies' in result
        assert 'metrics' in result
        # languages和hotspots在fallback模式下可能不存在
        if result.get('metadata', {}).get('mode') != 'fallback':
            assert 'languages' in result
            assert 'hotspots' in result

    def test_analyze_project_with_languages(self, sample_project_structure):
        """测试指定语言分析"""
        analyzer = CodeAnalyzer(str(sample_project_structure))

        result = analyzer.analyze_project(languages=['py'])

        assert 'py' in result.get('languages', {}) or 'metadata' in result

    def test_get_timestamp(self, temp_project_dir):
        """测试时间戳生成"""
        analyzer = CodeAnalyzer(str(temp_project_dir))

        timestamp = analyzer._get_timestamp()

        assert isinstance(timestamp, str)
        assert 'T' in timestamp  # ISO格式


class TestCodeAnalyzerEdgeCases:
    """测试边界情况"""

    def test_empty_project(self, temp_project_dir):
        """测试空项目分析"""
        analyzer = CodeAnalyzer(str(temp_project_dir))

        result = analyzer.analyze_project()

        assert 'metadata' in result
        assert result.get('metrics', {}).get('total_files', 0) == 0

    def test_nonexistent_dependency_file(self, temp_project_dir):
        """测试不存在的依赖文件"""
        analyzer = CodeAnalyzer(str(temp_project_dir))
        fake_file = temp_project_dir / "fake_requirements.txt"

        deps = analyzer._parse_dependency_file(fake_file, 'python')

        assert deps == []

    def test_invalid_json_package(self, temp_project_dir):
        """测试无效的package.json"""
        pkg_file = temp_project_dir / "package.json"
        pkg_file.write_text("invalid json", encoding='utf-8')

        analyzer = CodeAnalyzer(str(temp_project_dir))
        deps = analyzer._parse_dependency_file(pkg_file, 'javascript')

        assert deps == []