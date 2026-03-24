from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}

class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(ConversationBase):
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[MessageResponse] = []
    
    model_config = {"from_attributes": True}

class ChatCompletionRequest(BaseModel):
    conversation_id: Optional[int] = Field(None, description="提供以继续现有会话，否则新建")
    message: str = Field(..., description="用户发出的对话内容")

class ChatCompletionResponse(BaseModel):
    conversation_id: int
    response: str
