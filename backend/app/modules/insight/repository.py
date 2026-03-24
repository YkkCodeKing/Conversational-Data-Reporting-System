from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.shared.database.repository import BaseRepository
from app.modules.insight.models import Insight


class InsightRepository(BaseRepository[Insight]):
    """数据洞察仓储"""

    def __init__(self):
        super().__init__(Insight)

    async def create_insight(self, db: AsyncSession, summary: str,
                             key_findings: Optional[list] = None,
                             suggestions: Optional[list] = None,
                             query_id: Optional[int] = None,
                             created_by: Optional[int] = None) -> Insight:
        """创建一条洞察记录"""
        insight = Insight(
            query_id=query_id, summary=summary,
            key_findings=key_findings, suggestions=suggestions,
            created_by=created_by,
        )
        db.add(insight)
        await db.commit()
        await db.refresh(insight)
        return insight

    async def list_insights(self, db: AsyncSession, limit: int = 50) -> List[Insight]:
        """列出最近的洞察记录"""
        stmt = select(Insight).order_by(Insight.created_at.desc()).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())


insight_repo = InsightRepository()
