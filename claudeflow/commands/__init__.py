"""
命令处理器模块

将cli.py中的命令执行逻辑拆分为独立的命令处理器
"""

from .base import BaseCommandHandler
from .structure_cmd import StructureCommandHandler
from .refresh_cmd import RefreshCommandHandler
from .hotspot_cmd import HotspotCommandHandler
from .graph_cmd import GraphCommandHandler, AIContextCommandHandler
from .registry import get_command_handler, COMMAND_HANDLERS

__all__ = [
    'BaseCommandHandler',
    'StructureCommandHandler',
    'RefreshCommandHandler',
    'HotspotCommandHandler',
    'GraphCommandHandler',
    'AIContextCommandHandler',
    'get_command_handler',
    'COMMAND_HANDLERS',
]