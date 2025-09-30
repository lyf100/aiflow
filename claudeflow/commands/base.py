"""
命令处理器基类

提供命令处理的通用接口和工具函数
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional


class BaseCommandHandler(ABC):
    """命令处理器基类"""

    def __init__(self, project_path: str, options: Dict[str, Any]):
        self.project_path = Path(project_path)
        self.options = options
        self.config = options.get('config', {})
        self.use_color = self.config.get('output', {}).get('colorful', True)

    @abstractmethod
    def execute(self, args: list) -> Dict[str, Any]:
        """
        执行命令

        Args:
            args: 命令参数列表

        Returns:
            执行结果字典
        """
        pass

    def print_progress(self, message: str, step: int = 0, total: int = 0):
        """打印进度信息"""
        if step and total:
            progress_text = f"[{step}/{total}]"
            if self.use_color:
                progress_text = self.colored(progress_text, 'cyan', 'bright')
            print(f"  {progress_text} {message}")
        else:
            bullet = self.colored("•", 'blue') if self.use_color else "•"
            print(f"  {bullet} {message}")

    def colored(self, text: str, color: str = None, style: str = None) -> str:
        """为文本添加颜色"""
        if not self.use_color:
            return text

        try:
            from colorama import Fore, Style
        except ImportError:
            return text

        result = ""
        if style == 'bright':
            result += Style.BRIGHT
        elif style == 'dim':
            result += Style.DIM

        if color:
            color_map = {
                'red': Fore.RED,
                'green': Fore.GREEN,
                'yellow': Fore.YELLOW,
                'blue': Fore.BLUE,
                'magenta': Fore.MAGENTA,
                'cyan': Fore.CYAN,
                'white': Fore.WHITE,
            }
            result += color_map.get(color, '')

        return result + text + Style.RESET_ALL

    def format_output_path(self, output_file: Path) -> tuple:
        """格式化输出路径"""
        try:
            rel_path = output_file.relative_to(self.project_path)
        except ValueError:
            rel_path = output_file

        return str(rel_path), str(output_file.absolute())

    def confirm_operation(self, operation: str, warning: str = None) -> bool:
        """确认操作"""
        print(f"⚠️  即将执行: {operation}")
        if warning:
            print(f"   {warning}")
        print()

        response = input("确认继续? (y/N): ")
        return response.lower() == 'y'