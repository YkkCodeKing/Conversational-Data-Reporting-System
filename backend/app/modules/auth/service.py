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


auth_service = AuthService()
