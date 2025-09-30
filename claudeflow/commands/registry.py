"""
命令注册表

集中管理所有命令处理器的注册和路由
"""
from typing import Dict, Type

from .base import BaseCommandHandler
from .structure_cmd import StructureCommandHandler
from .refresh_cmd import RefreshCommandHandler
from .hotspot_cmd import HotspotCommandHandler
from .graph_cmd import GraphCommandHandler, AIContextCommandHandler


# 命令处理器注册表
COMMAND_HANDLERS: Dict[str, Type[BaseCommandHandler]] = {
    'structure': StructureCommandHandler,
    'refresh': RefreshCommandHandler,
    'hotspot': HotspotCommandHandler,
    'graph': GraphCommandHandler,
    'ai-context': AIContextCommandHandler,
}


def get_command_handler(command: str, project_path: str, options: dict) -> BaseCommandHandler:
    """
    获取命令处理器实例

    Args:
        command: 命令名称
        project_path: 项目路径
        options: 选项字典

    Returns:
        命令处理器实例

    Raises:
        ValueError: 未知命令
    """
    handler_class = COMMAND_HANDLERS.get(command)

    if handler_class is None:
        raise ValueError(f"Unknown command: {command}")

    return handler_class(project_path, options)


__all__ = [
    'BaseCommandHandler',
    'StructureCommandHandler',
    'RefreshCommandHandler',
    'HotspotCommandHandler',
    'GraphCommandHandler',
    'AIContextCommandHandler',
    'COMMAND_HANDLERS',
    'get_command_handler',
]