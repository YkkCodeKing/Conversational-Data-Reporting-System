from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from loguru import logger

from app.core.config import settings

class BaseLLMClient(ABC):
    """
    LLM 客户端的抽象基类，规范标准与流式生成接口
    """
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """普通生成完整文本"""
        pass

    @abstractmethod
    async def stream_generate(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """流式生成文本（用于 SSE）"""
        pass


class ClaudeClient(BaseLLMClient):
    """
    Claude API 客户端实现基于 anthropic SDK
    """
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("Anthropic API Key is missing. ClaudeClient may fail.")
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.default_model = "claude-3-5-sonnet-20241022"

    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        model = kwargs.get("model", self.default_model)
        max_tokens = kwargs.get("max_tokens", 4096)
        
        # 转换 system message
        system_prompt = next((m["content"] for m in messages if m["role"] == "system"), None)
        chat_messages = [m for m in messages if m["role"] != "system"]

        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=chat_messages,
            system=system_prompt if system_prompt else "",
        )
        return response.content[0].text

    async def stream_generate(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        model = kwargs.get("model", self.default_model)
        max_tokens = kwargs.get("max_tokens", 4096)
        
        system_prompt = next((m["content"] for m in messages if m["role"] == "system"), None)
        chat_messages = [m for m in messages if m["role"] != "system"]

        async with self.client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            messages=chat_messages,
            system=system_prompt if system_prompt else "",
        ) as stream:
            async for text in stream.text_stream:
                yield text


class GPTClient(BaseLLMClient):
    """
    OpenAI/GPT 客户端实现，作为备用或比对
    """
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API Key is missing. GPTClient may fail.")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.default_model = "gpt-4o"

    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        model = kwargs.get("model", self.default_model)
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content or ""

    async def stream_generate(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        model = kwargs.get("model", self.default_model)
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

# 默认提供一个以 Claude 为主的 Client 实例
llm_client = ClaudeClient()
