from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.shared.database.repository import BaseRepository
from app.modules.chart.models import ChartConfig


class ChartRepository(BaseRepository[ChartConfig]):
    """图表配置仓储"""

    def __init__(self):
        super().__init__(ChartConfig)

    async def create_chart_config(self, db: AsyncSession, chart_type: str,
                                  config_json: Any, query_id: Optional[int] = None,
                                  title: Optional[str] = None,
                                  created_by: Optional[int] = None) -> ChartConfig:
        """创建一条图表配置记录"""
        chart = ChartConfig(
            query_id=query_id, chart_type=chart_type, title=title,
            config_json=config_json, created_by=created_by,
        )
        db.add(chart)
        await db.commit()
        await db.refresh(chart)
        return chart

    async def list_chart_configs(self, db: AsyncSession, limit: int = 50) -> List[ChartConfig]:
        """列出最近创建的图表配置"""
        stmt = select(ChartConfig).order_by(ChartConfig.created_at.desc()).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())


chart_repo = ChartRepository()
