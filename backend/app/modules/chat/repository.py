from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.shared.database.repository import BaseRepository
from app.modules.chat.models import Conversation, Message

class ChatRepository(BaseRepository[Conversation]):
    def __init__(self):
        super().__init__(Conversation)
        
    async def get_or_create_conversation(self, db: AsyncSession, conversation_id: Optional[int] = None) -> Conversation:
        if conversation_id:
            db_conv = await self.get(db, conversation_id)
            if db_conv:
                return db_conv
        
        # 不存在或未提供时创建新 Conversation
        db_conv = Conversation(title="New Conversation")
        db.add(db_conv)
        await db.commit()
        await db.refresh(db_conv)
        return db_conv

    async def create_message(self, db: AsyncSession, conversation_id: int, role: str, content: str) -> Message:
        db_msg = Message(conversation_id=conversation_id, role=role, content=content)
        db.add(db_msg)
        await db.commit()
        await db.refresh(db_msg)
        return db_msg

    async def get_conversation_context(self, db: AsyncSession, conversation_id: int, limit: int = 20) -> List[Message]:
        stmt = (
            select(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        messages = result.scalars().all()
        # 让最新的消息在最后，方便拼装 Prompt 上下文
        return list(reversed(messages))

chat_repo = ChatRepository()
