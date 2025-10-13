"""
AIFlow - AI分析指挥与可视化平台
AI Analysis Command and Visualization Platform

Core package initialization
"""

__version__ = "0.1.0"
__author__ = "AIFlow Team"

from .protocol.entities import *
from .protocol.validator import ProtocolValidator, validate_analysis_result
from .protocol.serializer import ProtocolSerializer, serialize_to_file, deserialize_from_file

from .adapters.base import BaseAIAdapter, AIProvider, AIModelConfig, AIResponse, TokenUsage
from .adapters.claude import ClaudeAdapter, create_claude_adapter

from .prompts.manager import PromptTemplateManager, load_prompt_template
from .prompts.renderer import PromptRenderer, render_prompt

from .analysis.engine import AnalysisEngine, AnalysisJob, AnalysisStage, AnalysisStatus
from .analysis.queue import TaskQueue, TaskPriority, get_global_queue

__all__ = [
    # Version
    "__version__",
    "__author__",

    # Protocol
    "ProtocolValidator",
    "validate_analysis_result",
    "ProtocolSerializer",
    "serialize_to_file",
    "deserialize_from_file",

    # Adapters
    "BaseAIAdapter",
    "AIProvider",
    "AIModelConfig",
    "AIResponse",
    "TokenUsage",
    "ClaudeAdapter",
    "create_claude_adapter",

    # Prompts
    "PromptTemplateManager",
    "load_prompt_template",
    "PromptRenderer",
    "render_prompt",

    # Analysis
    "AnalysisEngine",
    "AnalysisJob",
    "AnalysisStage",
    "AnalysisStatus",
    "TaskQueue",
    "TaskPriority",
    "get_global_queue",
]
