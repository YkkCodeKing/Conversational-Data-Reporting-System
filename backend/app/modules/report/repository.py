from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.shared.database.repository import BaseRepository
from app.modules.report.models import Report, ReportItem


class ReportRepository(BaseRepository[Report]):
    """报表仓储"""

    def __init__(self):
        super().__init__(Report)

    async def create_report(self, db: AsyncSession, title: str,
                            description: Optional[str] = None,
                            layout_config: Optional[Any] = None,
                            created_by: Optional[int] = None) -> Report:
        """创建新报表"""
        report = Report(
            title=title, description=description,
            layout_config=layout_config, created_by=created_by,
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)
        return report

    async def add_report_item(self, db: AsyncSession, report_id: int,
                              item_type: str, reference_id: Optional[int] = None,
                              position: int = 0, config_json: Optional[Any] = None) -> ReportItem:
        """向报表中添加一个组件项"""
        item = ReportItem(
            report_id=report_id, item_type=item_type,
            reference_id=reference_id, position=position, config_json=config_json,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    async def get_report_with_items(self, db: AsyncSession, report_id: int) -> Optional[Report]:
        """获取报表及其所有组件项（预加载）"""
        stmt = (
            select(Report)
            .options(selectinload(Report.items))
            .filter(Report.id == report_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def list_reports(self, db: AsyncSession) -> List[Report]:
        """列出所有报表"""
        stmt = select(Report).order_by(Report.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update_report(self, db: AsyncSession, report: Report,
                            title: Optional[str] = None,
                            description: Optional[str] = None,
                            layout_config: Optional[Any] = None) -> Report:
        """更新报表基础信息"""
        if title is not None:
            report.title = title
        if description is not None:
            report.description = description
        if layout_config is not None:
            report.layout_config = layout_config
        await db.commit()
        await db.refresh(report)
        return report

    async def delete_report(self, db: AsyncSession, report_id: int) -> bool:
        """删除报表及其所有组件项（级联删除）"""
        report = await self.get_report_with_items(db, report_id)
        if not report:
            return False
        await db.delete(report)
        await db.commit()
        return True


report_repo = ReportRepository()
