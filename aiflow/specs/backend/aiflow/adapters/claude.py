"""
AIFlow Claude AI Adapter
Claude API 适配器实现

支持功能:
1. Claude 3.5 Sonnet / Claude 3 Opus / Claude 3 Haiku
2. 流式和非流式响应
3. 系统提示词支持
4. Token 统计
5. 错误处理和重试
"""

import asyncio
import time
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

try:
    import anthropic
    from anthropic import AsyncAnthropic, APIError, APIStatusError, RateLimitError as AnthropicRateLimitError
except ImportError:
    raise ImportError(
        "anthropic SDK is required. Install with: pip install anthropic"
    )

from .base import (
    AIAdapterError,
    AIProvider,
    AIResponse,
    AuthenticationError,
    BaseAIAdapter,
    InvalidRequestError,
    ModelNotFoundError,
    RateLimitError,
    TokenUsage,
)


class ClaudeAdapter(BaseAIAdapter):
    """Claude API 适配器"""

    # 支持的模型列表
    SUPPORTED_MODELS = {
        # Claude 4.5 (最新)
        "claude-sonnet-4-5-20250929": {"max_tokens": 8192, "context_window": 200000},
        # Claude 3.5 系列
        "claude-3-5-sonnet-20241022": {"max_tokens": 200000, "context_window": 200000},
        "claude-3-5-sonnet-20240620": {"max_tokens": 8192, "context_window": 200000},
        # Claude 3 系列
        "claude-3-opus-20240229": {"max_tokens": 4096, "context_window": 200000},
        "claude-3-sonnet-20240229": {"max_tokens": 4096, "context_window": 200000},
        "claude-3-haiku-20240307": {"max_tokens": 4096, "context_window": 200000},
    }

    def __init__(self, config):
        """初始化 Claude 适配器"""
        super().__init__(config)

        # 创建 Anthropic 客户端
        self.client = AsyncAnthropic(
            api_key=config.api_key,
            base_url=config.api_base_url,
            timeout=config.timeout,
        )

        # 验证模型
        if config.model_name not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported Claude model: {config.model_name}. "
                f"Supported models: {', '.join(self.SUPPORTED_MODELS.keys())}"
            )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AIResponse:
        """生成响应（非流式）"""
        start_time = time.time()

        # 参数准备
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature if temperature is not None else self.config.temperature

        # 构建消息
        messages = [{"role": "user", "content": prompt}]

        # 构建请求参数
        request_params = {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system_prompt:
            request_params["system"] = system_prompt

        if stop_sequences:
            request_params["stop_sequences"] = stop_sequences

        # 添加额外参数
        if self.config.extra_params:
            request_params.update(self.config.extra_params)

        # 添加自定义参数
        request_params.update(kwargs)

        try:
            # 调用 Claude API
            response = await self.client.messages.create(**request_params)

            # 计算响应时间
            response_time = time.time() - start_time

            # 提取内容
            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text

            # 构建响应
            return AIResponse(
                content=content,
                model=response.model,
                usage=TokenUsage(
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                    total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                ),
                finish_reason=response.stop_reason or "stop",
                response_time=response_time,
                created_at=datetime.now(),
                metadata={
                    "id": response.id,
                    "stop_reason": response.stop_reason,
                    "role": response.role,
                }
            )

        except AnthropicRateLimitError as e:
            raise RateLimitError(f"Claude rate limit exceeded: {e}") from e
        except APIStatusError as e:
            if e.status_code == 401:
                raise AuthenticationError(f"Invalid API key: {e}") from e
            elif e.status_code == 404:
                raise ModelNotFoundError(f"Model not found: {e}") from e
            elif e.status_code == 400:
                raise InvalidRequestError(f"Invalid request: {e}") from e
            else:
                raise AIAdapterError(f"Claude API error: {e}") from e
        except APIError as e:
            raise AIAdapterError(f"Claude API error: {e}") from e
        except Exception as e:
            raise AIAdapterError(f"Unexpected error: {e}") from e

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """生成响应（流式）"""
        # 参数准备
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature if temperature is not None else self.config.temperature

        # 构建消息
        messages = [{"role": "user", "content": prompt}]

        # 构建请求参数
        request_params = {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system_prompt:
            request_params["system"] = system_prompt

        if stop_sequences:
            request_params["stop_sequences"] = stop_sequences

        # 添加额外参数
        if self.config.extra_params:
            request_params.update(self.config.extra_params)

        # 添加自定义参数
        request_params.update(kwargs)

        try:
            # 调用 Claude API (流式)
            async with self.client.messages.stream(**request_params) as stream:
                async for text in stream.text_stream:
                    yield text

        except AnthropicRateLimitError as e:
            raise RateLimitError(f"Claude rate limit exceeded: {e}") from e
        except APIStatusError as e:
            if e.status_code == 401:
                raise AuthenticationError(f"Invalid API key: {e}") from e
            elif e.status_code == 404:
                raise ModelNotFoundError(f"Model not found: {e}") from e
            elif e.status_code == 400:
                raise InvalidRequestError(f"Invalid request: {e}") from e
            else:
                raise AIAdapterError(f"Claude API error: {e}") from e
        except APIError as e:
            raise AIAdapterError(f"Claude API error: {e}") from e
        except Exception as e:
            raise AIAdapterError(f"Unexpected error: {e}") from e

    async def validate_connection(self) -> bool:
        """验证连接是否可用"""
        try:
            # 发送一个简单的测试请求
            response = await self.client.messages.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
            )
            return True
        except Exception:
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        model_spec = self.SUPPORTED_MODELS.get(self.config.model_name, {})

        return {
            "provider": AIProvider.CLAUDE.value,
            "model_name": self.config.model_name,
            "max_tokens": model_spec.get("max_tokens", self.config.max_tokens),
            "context_window": model_spec.get("context_window", 200000),
            "supports_streaming": True,
            "supports_system_prompt": True,
            "supports_function_calling": False,  # Claude 不直接支持 function calling
            "sdk_version": anthropic.__version__,
        }


# 便捷函数

async def create_claude_adapter(
    model_name: str = "claude-sonnet-4-5-20250929",
    api_key: Optional[str] = None,
    **kwargs: Any
) -> ClaudeAdapter:
    """
    便捷函数：创建 Claude 适配器

    Args:
        model_name: 模型名称 (默认: claude-sonnet-4-5-20250929, 即 Claude 4.5 Sonnet)
        api_key: API 密钥 (可选，从环境变量读取)
        **kwargs: 额外配置参数

    Returns:
        ClaudeAdapter: Claude 适配器实例
    """
    import os

    if api_key is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "API key is required. Provide via parameter or ANTHROPIC_API_KEY environment variable."
            )

    from .base import AIModelConfig, AIProvider

    config = AIModelConfig(
        provider=AIProvider.CLAUDE,
        model_name=model_name,
        api_key=api_key,
        **kwargs
    )

    return ClaudeAdapter(config)


# CLI 测试入口
if __name__ == "__main__":
    import sys

    async def main():
        if len(sys.argv) < 2:
            print("Usage: python claude.py <prompt>")
            sys.exit(1)

        prompt = " ".join(sys.argv[1:])

        # 创建适配器
        adapter = await create_claude_adapter()

        # 测试连接
        print("Testing connection...")
        if not await adapter.validate_connection():
            print("❌ Connection failed")
            sys.exit(1)
        print("✅ Connection successful")

        # 测试生成
        print(f"\nPrompt: {prompt}")
        print("\nResponse:")
        print("-" * 60)

        response = await adapter.generate(prompt)
        print(response.content)

        print("-" * 60)
        print(f"\nModel: {response.model}")
        print(f"Tokens: {response.usage.total_tokens} (prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens})")
        print(f"Cost estimate: ${response.usage.cost_estimate:.4f}")
        print(f"Response time: {response.response_time:.2f}s")

    asyncio.run(main())
