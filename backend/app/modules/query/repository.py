from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.shared.database.repository import BaseRepository
from app.modules.query.models import QueryRecord


class QueryRepository(BaseRepository[QueryRecord]):
    """查询记录仓储"""

    def __init__(self):
        super().__init__(QueryRecord)

    async def create_query_record(self, db: AsyncSession, datasource_id: int,
                                  natural_language: str, created_by: Optional[int] = None) -> QueryRecord:
        """创建一条查询记录（初始状态为 pending）"""
        record = QueryRecord(
            datasource_id=datasource_id,
            natural_language=natural_language,
            created_by=created_by,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record

    async def update_query_result(self, db: AsyncSession, record: QueryRecord,
                                  generated_sql: str, result_summary: str, status: str) -> QueryRecord:
        """更新查询记录的 SQL、结果摘要和状态"""
        record.generated_sql = generated_sql
        record.result_summary = result_summary
        record.status = status
        await db.commit()
        await db.refresh(record)
        return record

    async def list_query_history(self, db: AsyncSession, limit: int = 50) -> List[QueryRecord]:
        """列出最近的查询历史"""
        stmt = select(QueryRecord).order_by(QueryRecord.created_at.desc()).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())


query_repo = QueryRepository()
