from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, get_password_hash, create_access_token
from app.modules.auth.repository import auth_repo
from app.modules.auth.schemas import UserCreate, UserLogin, TokenResponse, UserResponse


class AuthService:
    """认证业务服务：注册、登录、令牌签发"""

    @staticmethod
    async def register(db: AsyncSession, data: UserCreate) -> UserResponse:
        """用户注册：校验唯一性 → 哈希密码 → 创建账户"""
        # 校验邮箱是否已注册
        existing = await auth_repo.get_user_by_email(db, data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该邮箱已被注册")

        # 校验用户名是否已占用
        existing = await auth_repo.get_user_by_username(db, data.username)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该用户名已存在")

        hashed_pw = get_password_hash(data.password)
        user = await auth_repo.create_user(db, data.username, data.email, hashed_pw)
        return UserResponse.model_validate(user)

    @staticmethod
    async def login(db: AsyncSession, data: UserLogin) -> TokenResponse:
        """用户登录：校验密码 → 签发 JWT"""
        user = await auth_repo.get_user_by_email(db, data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账户已被禁用")

        token = create_access_token(data={"sub": str(user.id)})
        return TokenResponse(access_token=token)

    @staticmethod
    async def list_users(db: AsyncSession, limit: int = 50, offset: int = 0) -> List[UserResponse]:
        """管理员：分页列出系统内所有用户"""
        users = await auth_repo.get_users(db, limit=limit, offset=offset)
        return [UserResponse.model_validate(user) for user in users]

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, role: Optional[str], is_active: Optional[bool]) -> UserResponse:
        """管理员：更改目标用户的权限和状态"""
        user = await auth_repo.get(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目标用户不存在")
        
        updated_user = await auth_repo.update_user_role_status(db, user, role, is_active)
        return UserResponse.model_validate(updated_user)


auth_service = AuthService()
