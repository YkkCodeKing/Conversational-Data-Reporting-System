from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import datetime


class ReportItemCreate(BaseModel):
    """报表组件项创建请求体"""
    item_type: str = Field(..., description="组件类型: chart / insight / text")
    reference_id: Optional[int] = Field(None, description="引用的图表或洞察 ID")
    position: int = Field(0, description="排列顺序")
    config_json: Optional[Any] = Field(None, description="组件自定义配置")


class ReportItemResponse(BaseModel):
    """报表组件项响应体"""
    id: int
    report_id: int
    item_type: str
    reference_id: Optional[int] = None
    position: int
    config_json: Optional[Any] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportCreate(BaseModel):
    """报表创建请求体"""
    title: str = Field(..., max_length=255, description="报表标题")
    description: Optional[str] = Field(None, description="报表描述")
    layout_config: Optional[Any] = Field(None, description="仪表盘布局配置")


class ReportUpdate(BaseModel):
    """报表更新请求体"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    layout_config: Optional[Any] = None


class ReportResponse(BaseModel):
    """报表响应体（含组件列表）"""
    id: int
    title: str
    description: Optional[str] = None
    layout_config: Optional[Any] = None
    is_published: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[ReportItemResponse] = []

    model_config = {"from_attributes": True}
