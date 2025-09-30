"""
ClaudeFlow 包初始化

基于 code2flow 的增强代码分析系统
"""

__version__ = "1.0.0"
__author__ = "ClaudeFlow Team"
__description__ = "Enhanced code analysis system based on code2flow"

# 导出主要类和函数
from .core.analyzer import CodeAnalyzer
from .core.mapper import ProjectMapper
from .core.grapher import DependencyGrapher
from .core.tracker import ChangeTracker
from .core.exporter import DataExporter

__all__ = [
    'CodeAnalyzer',
    'ProjectMapper',
    'DependencyGrapher',
    'ChangeTracker',
    'DataExporter'
]