from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.modules.report.schemas import (
    ReportCreate, ReportUpdate, ReportResponse,
    ReportItemCreate, ReportItemResponse,
)
from app.modules.report.service import report_service

router = APIRouter(prefix="/report", tags=["Report"])


@router.post("/", response_model=ReportResponse)
async def create_report(data: ReportCreate, db: AsyncSession = Depends(get_db)):
    """创建新报表"""
    return await report_service.create_report(db, data)


@router.get("/", response_model=List[ReportResponse])
async def list_reports(db: AsyncSession = Depends(get_db)):
    """列出所有报表"""
    return await report_service.list_reports(db)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """获取报表详情（含组件列表）"""
    return await report_service.get_report(db, report_id)


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(report_id: int, data: ReportUpdate, db: AsyncSession = Depends(get_db)):
    """更新报表基础信息"""
    return await report_service.update_report(db, report_id, data)


@router.delete("/{report_id}")
async def delete_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """删除报表"""
    await report_service.delete_report(db, report_id)
    return {"detail": "删除成功"}


@router.post("/{report_id}/items", response_model=ReportItemResponse)
async def add_report_item(report_id: int, data: ReportItemCreate, db: AsyncSession = Depends(get_db)):
    """向报表中添加组件项"""
    return await report_service.add_item(db, report_id, data)


@router.post("/{report_id}/publish", response_model=ReportResponse)
async def publish_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """发布报表"""
    return await report_service.publish_report(db, report_id, publish=True)


@router.post("/{report_id}/unpublish", response_model=ReportResponse)
async def unpublish_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """取消发布报表"""
    return await report_service.publish_report(db, report_id, publish=False)
