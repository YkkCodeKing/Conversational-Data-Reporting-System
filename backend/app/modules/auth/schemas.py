from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """用户注册请求体"""
    username: str = Field(..., min_length=3, max_length=100, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, description="密码")


class UserLogin(BaseModel):
    """用户登录请求体"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """用户信息响应体"""
    id: int
    username: str
    email: str
    is_active: bool
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT 令牌响应体"""
    access_token: str
    token_type: str = "bearer"


class UserRoleUpdate(BaseModel):
    """管理员更新用户角色与状态的请求体"""
    role: Optional[str] = Field(None, description="用户角色: user / admin")
    is_active: Optional[bool] = Field(None, description="是否处于激活状态(true/false)")

