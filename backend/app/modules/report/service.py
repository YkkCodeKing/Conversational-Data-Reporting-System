from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.modules.report.repository import report_repo
from app.modules.report.schemas import (
    ReportCreate, ReportUpdate, ReportResponse,
    ReportItemCreate, ReportItemResponse,
)


class ReportService:
    """报表/仪表盘业务服务：组装、编排、发布"""

    @staticmethod
    async def create_report(db: AsyncSession, data: ReportCreate,
                            user_id: Optional[int] = None) -> ReportResponse:
        """创建新报表"""
        report = await report_repo.create_report(
            db, data.title, data.description, data.layout_config, user_id,
        )
        return ReportResponse.model_validate(report)

    @staticmethod
    async def get_report(db: AsyncSession, report_id: int) -> ReportResponse:
        """获取报表详情（含所有组件项）"""
        report = await report_repo.get_report_with_items(db, report_id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报表不存在")
        return ReportResponse.model_validate(report)

    @staticmethod
    async def list_reports(db: AsyncSession) -> List[ReportResponse]:
        """列出所有报表"""
        reports = await report_repo.list_reports(db)
        return [ReportResponse.model_validate(r) for r in reports]

    @staticmethod
    async def update_report(db: AsyncSession, report_id: int, data: ReportUpdate) -> ReportResponse:
        """更新报表基础信息"""
        report = await report_repo.get_report_with_items(db, report_id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报表不存在")
        updated = await report_repo.update_report(db, report, data.title, data.description, data.layout_config)
        return ReportResponse.model_validate(updated)

    @staticmethod
    async def delete_report(db: AsyncSession, report_id: int) -> bool:
        """删除报表"""
        success = await report_repo.delete_report(db, report_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报表不存在")
        return True

    @staticmethod
    async def add_item(db: AsyncSession, report_id: int, data: ReportItemCreate) -> ReportItemResponse:
        """向报表添加组件项"""
        # 先校验报表是否存在
        report = await report_repo.get(db, report_id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报表不存在")
        item = await report_repo.add_report_item(
            db, report_id, data.item_type, data.reference_id, data.position, data.config_json,
        )
        return ReportItemResponse.model_validate(item)

    @staticmethod
    async def publish_report(db: AsyncSession, report_id: int, publish: bool = True) -> ReportResponse:
        """发布或取消发布报表"""
        report = await report_repo.get_report_with_items(db, report_id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报表不存在")
        report.is_published = publish
        await db.commit()
        await db.refresh(report)
        return ReportResponse.model_validate(report)


report_service = ReportService()
