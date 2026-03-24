from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class InsightGenerateRequest(BaseModel):
    """洞察生成请求体"""
    query_id: Optional[int] = Field(None, description="关联查询记录 ID")
    data: Any = Field(..., description="待分析的数据")
    context: Optional[str] = Field(None, description="额外的业务背景信息")


class InsightResponse(BaseModel):
    """洞察结果响应体"""
    id: int
    query_id: Optional[int] = None
    summary: str
    key_findings: Optional[list] = None
    suggestions: Optional[list] = None
    created_by: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}
