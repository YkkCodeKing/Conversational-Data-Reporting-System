from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DataSourceCreate(BaseModel):
    """创建数据源请求体"""
    name: str = Field(..., max_length=100, description="数据源名称")
    db_type: str = Field(..., description="数据库类型: postgresql / mysql / sqlite")
    connection_string: str = Field(..., description="数据库连接字符串")
    description: Optional[str] = Field(None, max_length=500, description="数据源描述")


class DataSourceResponse(BaseModel):
    """数据源响应体"""
    id: int
    name: str
    db_type: str
    connection_string: str
    description: Optional[str] = None
    is_active: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ConnectionTestResult(BaseModel):
    """连接测试结果"""
    success: bool
    message: str
    tables: list[str] = []
