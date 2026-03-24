from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.modules.chat.schemas import ChatCompletionRequest, ChatCompletionResponse
from app.modules.chat.repository import chat_repo
from app.modules.chat.service import chat_service

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    非流式对话补全接口：
    传入对话ID与新消息，返回完整的AI回答片段。
    """
    conv = await chat_repo.get_or_create_conversation(db, request.conversation_id)
    response_text = await chat_service.process_message(db, conv.id, request.message)
    return ChatCompletionResponse(conversation_id=conv.id, response=response_text)

@router.post("/completions/stream")
async def chat_completions_stream(
    request: ChatCompletionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    SSE 流式对话补全接口：
    传入对话ID与新消息，按块返回AI回答片段。
    """
    conv = await chat_repo.get_or_create_conversation(db, request.conversation_id)
    return StreamingResponse(
        chat_service.stream_message(db, conv.id, request.message),
        media_type="text/event-stream"
    )
