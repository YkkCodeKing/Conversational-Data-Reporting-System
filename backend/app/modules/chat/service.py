import json
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.modules.chat.repository import chat_repo
from app.shared.ai.llm_client import llm_client

class ChatService:
    @staticmethod
    async def process_message(db: AsyncSession, conversation_id: int, user_message: str) -> str:
        """非流式对话服务：保存记录、请求模型、保存回复并返回"""
        # 保存用户消息
        await chat_repo.create_message(db, conversation_id, "user", user_message)
        
        # 组装上下文
        history = await chat_repo.get_conversation_context(db, conversation_id)
        messages = [{"role": msg.role, "content": msg.content} for msg in history]
        
        # 调用大模型生成（此处可后续加入 NLPService 或 QueryService 处理报表数据）
        response_text = await llm_client.generate(messages)
        
        # 保存模型回复
        await chat_repo.create_message(db, conversation_id, "assistant", response_text)
        
        return response_text

    @staticmethod
    async def stream_message(db: AsyncSession, conversation_id: int, user_message: str) -> AsyncGenerator[str, None]:
        """流式对话服务：支持 Server-Sent Events"""
        # 保存用户消息
        await chat_repo.create_message(db, conversation_id, "user", user_message)
        
        history = await chat_repo.get_conversation_context(db, conversation_id)
        messages = [{"role": msg.role, "content": msg.content} for msg in history]
        
        full_response = ""
        try:
            async for chunk in llm_client.stream_generate(messages):
                full_response += chunk
                # 按照 SSE 数据格式 yield
                yield f"data: {json.dumps({'content': chunk})}\n\n"
        except Exception as e:
            logger.error(f"Error in stream_generate: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
        yield "data: [DONE]\n\n"
        
        # 将完整的模型回复保存入库
        if full_response:
            await chat_repo.create_message(db, conversation_id, "assistant", full_response)

chat_service = ChatService()
