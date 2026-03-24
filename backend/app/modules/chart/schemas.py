from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class ChartGenerateRequest(BaseModel):
    """图表生成请求体"""
    query_id: Optional[int] = Field(None, description="关联查询记录 ID")
    data: Any = Field(..., description="待可视化的数据（列表或字典）")
    title: Optional[str] = Field(None, description="图表标题（可由 LLM 自动生成）")
    preferred_type: Optional[str] = Field(None, description="偏好图表类型，留空则由 LLM 推荐")


class ChartConfigResponse(BaseModel):
    """图表配置响应体"""
    id: int
    query_id: Optional[int] = None
    chart_type: str
    title: Optional[str] = None
    config_json: Any
    created_by: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}
