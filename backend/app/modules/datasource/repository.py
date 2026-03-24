from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.shared.database.repository import BaseRepository
from app.modules.datasource.models import DataSource


class DataSourceRepository(BaseRepository[DataSource]):
    """数据源仓储：封装与 datasources 表的交互"""

    def __init__(self):
        super().__init__(DataSource)

    async def create_datasource(self, db: AsyncSession, name: str, db_type: str,
                                connection_string: str, description: Optional[str] = None,
                                created_by: Optional[int] = None) -> DataSource:
        """创建新数据源记录"""
        ds = DataSource(
            name=name, db_type=db_type, connection_string=connection_string,
            description=description, created_by=created_by,
        )
        db.add(ds)
        await db.commit()
        await db.refresh(ds)
        return ds

    async def list_datasources(self, db: AsyncSession) -> List[DataSource]:
        """列出所有活跃数据源"""
        result = await db.execute(select(DataSource).filter(DataSource.is_active == True))
        return list(result.scalars().all())

    async def delete_datasource(self, db: AsyncSession, datasource_id: int) -> bool:
        """软删除数据源（标记为非活跃）"""
        ds = await self.get(db, datasource_id)
        if not ds:
            return False
        ds.is_active = False
        await db.commit()
        return True


datasource_repo = DataSourceRepository()
