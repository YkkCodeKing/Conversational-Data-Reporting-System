from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.shared.database.repository import BaseRepository
from app.modules.auth.models import User


class AuthRepository(BaseRepository[User]):
    """用户仓储：封装与 users 表的交互"""

    def __init__(self):
        super().__init__(User)

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱查询用户"""
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def get_user_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名查询用户"""
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, username: str, email: str, hashed_password: str) -> User:
        """创建新用户"""
        user = User(username=username, email=email, hashed_password=hashed_password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def get_users(self, db: AsyncSession, limit: int = 50, offset: int = 0) -> List[User]:
        """管理员：分页获取所有用户"""
        result = await db.execute(select(User).order_by(User.id.desc()).limit(limit).offset(offset))
        return list(result.scalars().all())

    async def update_user_role_status(self, db: AsyncSession, user: User, role: Optional[str], is_active: Optional[bool]) -> User:
        """管理员：更新用户的角色与状态"""
        if role is not None:
            user.role = role
        if is_active is not None:
            user.is_active = is_active
        await db.commit()
        await db.refresh(user)
        return user


auth_repo = AuthRepository()
