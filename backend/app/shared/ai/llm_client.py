from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List, Optional

from openai import AsyncOpenAI
from loguru import logger

from app.core.config import settings


class BaseLLMClient(ABC):
    """LLM 客户端的抽象基类，规范标准与流式生成接口"""

    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """普通生成完整文本"""
        pass

    @abstractmethod
    async def stream_generate(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """流式生成文本（用于 SSE）"""
        pass


class DeepSeekClient(BaseLLMClient):
    """
    DeepSeek 客户端实现：使用 OpenAI 兼容接口。
    通过自定义 base_url 指向 DeepSeek 的 API 端点。
    """
    def __init__(self):
        if not settings.DEEPSEEK_API_KEY:
            logger.warning("DeepSeek API Key 未配置，DeepSeekClient 调用将失败。")
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
        self.default_model = settings.DEEPSEEK_MODEL

    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """非流式调用 DeepSeek 生成完整文本"""
        model = kwargs.get("model", self.default_model)
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content or ""

    async def stream_generate(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """流式调用 DeepSeek（用于 SSE 推送）"""
        model = kwargs.get("model", self.default_model)
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content


class GPTClient(BaseLLMClient):
    """OpenAI/GPT 客户端实现，作为备用"""

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API Key 未配置，GPTClient 调用将失败。")
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


def _create_llm_client() -> BaseLLMClient:
    """根据配置自动选择最佳可用的 LLM 客户端"""
    if settings.DEEPSEEK_API_KEY:
        logger.info("LLM 引擎: DeepSeek (deepseek-chat)")
        return DeepSeekClient()
    elif settings.OPENAI_API_KEY:
        logger.info("LLM 引擎: OpenAI (GPT)")
        return GPTClient()
    else:
        logger.warning("未检测到任何 LLM API Key，默认使用 DeepSeek 客户端（调用时会报错）。")
        return DeepSeekClient()


# 全局单例：根据 .env 配置自动选择引擎
llm_client = _create_llm_client()
