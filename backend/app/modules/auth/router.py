from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.core.security import get_current_user, get_current_active_admin
from app.modules.auth.models import User
from app.modules.auth.schemas import UserCreate, UserLogin, UserResponse, TokenResponse, UserRoleUpdate
from app.modules.auth.service import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册接口"""
    return await auth_service.register(db, data)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录接口，返回 JWT 令牌"""
    return await auth_service.login(db, data)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserResponse.model_validate(current_user)


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin)
):
    """【管理员】获取系统所有用户的列表"""
    return await auth_service.list_users(db, limit=limit, offset=skip)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user_status(
    user_id: int,
    data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin)
):
    """【管理员】修改目标用户的属性（角色提权或封禁）"""
    return await auth_service.update_user(db, user_id=user_id, role=data.role, is_active=data.is_active)
