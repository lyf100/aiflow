"""
AIFlow AI Adapter Base Interface
AI 适配器基础接口 - 统一的 AI 模型调用抽象层

核心功能:
1. 定义统一的 AI 调用接口
2. 支持多种 AI 模型 (Claude, GPT-4, Gemini, etc.)
3. 流式响应支持
4. Token 使用统计
5. 错误处理和重试机制
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncIterator, Dict, List, Optional
from datetime import datetime


class AIProvider(Enum):
    """AI 提供商枚举"""
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"
    CUSTOM = "custom"


@dataclass
class AIModelConfig:
    """AI 模型配置"""
    provider: AIProvider
    model_name: str
    api_key: str
    api_base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 120  # 秒
    max_retries: int = 3
    retry_delay: float = 1.0  # 秒
    extra_params: Optional[Dict[str, Any]] = None


@dataclass
class TokenUsage:
    """Token 使用统计"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    @property
    def cost_estimate(self) -> float:
        """
        成本估算（美元）
        注: 实际成本需要根据具体模型定价计算
        """
        # 粗略估算: $0.01 / 1K tokens
        return self.total_tokens * 0.01 / 1000


@dataclass
class AIResponse:
    """AI 响应"""
    content: str
    model: str
    usage: TokenUsage
    finish_reason: str  # "stop", "length", "error"
    response_time: float  # 秒
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class AIAdapterError(Exception):
    """AI 适配器错误基类"""
    pass


class RateLimitError(AIAdapterError):
    """速率限制错误"""
    pass


class AuthenticationError(AIAdapterError):
    """认证错误"""
    pass


class InvalidRequestError(AIAdapterError):
    """无效请求错误"""
    pass


class ModelNotFoundError(AIAdapterError):
    """模型未找到错误"""
    pass


class BaseAIAdapter(ABC):
    """
    AI 适配器基类

    所有 AI 模型适配器必须继承此类并实现抽象方法
    """

    def __init__(self, config: AIModelConfig):
        """
        初始化适配器

        Args:
            config: AI 模型配置
        """
        self.config = config
        self._validate_config()

    def _validate_config(self) -> None:
        """验证配置"""
        if not self.config.api_key:
            raise ValueError("API key is required")

        if self.config.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        if not (0.0 <= self.config.temperature <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AIResponse:
        """
        生成响应（非流式）

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词 (可选)
            max_tokens: 最大生成 Token 数 (可选，使用配置默认值)
            temperature: 温度参数 (可选，使用配置默认值)
            stop_sequences: 停止序列 (可选)
            **kwargs: 额外参数

        Returns:
            AIResponse: AI 响应

        Raises:
            AIAdapterError: 调用失败
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """
        生成响应（流式）

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词 (可选)
            max_tokens: 最大生成 Token 数 (可选)
            temperature: 温度参数 (可选)
            stop_sequences: 停止序列 (可选)
            **kwargs: 额外参数

        Yields:
            str: 流式响应片段

        Raises:
            AIAdapterError: 调用失败
        """
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """
        验证连接是否可用

        Returns:
            bool: 连接是否有效
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            Dict[str, Any]: 模型信息 (名称、版本、能力等)
        """
        pass

    def get_provider(self) -> AIProvider:
        """获取提供商"""
        return self.config.provider

    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.config.model_name

    async def generate_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AIResponse:
        """
        带重试的生成

        Args:
            同 generate()

        Returns:
            AIResponse: AI 响应

        Raises:
            AIAdapterError: 重试耗尽后仍失败
        """
        import asyncio

        last_error: Optional[Exception] = None

        for attempt in range(self.config.max_retries):
            try:
                return await self.generate(
                    prompt,
                    system_prompt,
                    max_tokens,
                    temperature,
                    stop_sequences,
                    **kwargs
                )
            except RateLimitError as e:
                # 速率限制：指数退避
                last_error = e
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                raise
            except (AuthenticationError, InvalidRequestError, ModelNotFoundError):
                # 这些错误不应重试
                raise
            except AIAdapterError as e:
                # 其他错误：重试
                last_error = e
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay)
                    continue
                raise

        # 重试耗尽
        raise AIAdapterError(
            f"Failed after {self.config.max_retries} retries"
        ) from last_error


# 工具函数

def create_adapter(
    provider: AIProvider,
    model_name: str,
    api_key: str,
    **kwargs: Any
) -> BaseAIAdapter:
    """
    工厂函数：创建 AI 适配器实例

    Args:
        provider: AI 提供商
        model_name: 模型名称
        api_key: API 密钥
        **kwargs: 额外配置参数

    Returns:
        BaseAIAdapter: 适配器实例

    Raises:
        ValueError: 不支持的提供商
    """
    from .claude import ClaudeAdapter
    # from .openai import OpenAIAdapter  # 待实现
    # from .gemini import GeminiAdapter  # 待实现

    config = AIModelConfig(
        provider=provider,
        model_name=model_name,
        api_key=api_key,
        **kwargs
    )

    if provider == AIProvider.CLAUDE:
        return ClaudeAdapter(config)
    # elif provider == AIProvider.OPENAI:
    #     return OpenAIAdapter(config)
    # elif provider == AIProvider.GEMINI:
    #     return GeminiAdapter(config)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


async def test_adapter(adapter: BaseAIAdapter) -> Dict[str, Any]:
    """
    测试适配器连接和基本功能

    Args:
        adapter: AI 适配器实例

    Returns:
        Dict[str, Any]: 测试结果
    """
    result = {
        "provider": adapter.get_provider().value,
        "model": adapter.get_model_name(),
        "connection_valid": False,
        "generation_test": False,
        "error": None
    }

    try:
        # 测试连接
        result["connection_valid"] = await adapter.validate_connection()

        # 测试生成
        if result["connection_valid"]:
            response = await adapter.generate(
                prompt="Hello, please respond with 'OK'.",
                max_tokens=10
            )
            result["generation_test"] = "OK" in response.content.upper()
            result["response_time"] = response.response_time
            result["tokens_used"] = response.usage.total_tokens

    except Exception as e:
        result["error"] = str(e)

    return result
