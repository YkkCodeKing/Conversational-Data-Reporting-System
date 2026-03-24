from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class QueryRequest(BaseModel):
    """自然语言查询请求体"""
    datasource_id: int = Field(..., description="目标数据源 ID")
    question: str = Field(..., description="用户的自然语言问题")


class QueryResponse(BaseModel):
    """查询结果响应体"""
    id: int
    datasource_id: int
    natural_language: str
    generated_sql: Optional[str] = None
    result_summary: Optional[str] = None
    result_data: Optional[Any] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class QueryHistoryResponse(BaseModel):
    """查询历史记录响应体"""
    id: int
    datasource_id: int
    natural_language: str
    generated_sql: Optional[str] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
