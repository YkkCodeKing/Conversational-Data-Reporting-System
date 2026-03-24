from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.modules.insight.schemas import InsightGenerateRequest, InsightResponse
from app.modules.insight.service import insight_service

router = APIRouter(prefix="/insight", tags=["Insight"])


@router.post("/generate", response_model=InsightResponse)
async def generate_insight(data: InsightGenerateRequest, db: AsyncSession = Depends(get_db)):
    """对数据进行智能分析，生成洞察报告"""
    return await insight_service.generate_insight(db, data)


@router.get("/{insight_id}", response_model=InsightResponse)
async def get_insight(insight_id: int, db: AsyncSession = Depends(get_db)):
    """根据 ID 获取洞察详情"""
    insight = await insight_service.get_insight(db, insight_id)
    if not insight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="洞察记录不存在")
    return insight


@router.get("/", response_model=List[InsightResponse])
async def list_insights(db: AsyncSession = Depends(get_db)):
    """列出所有洞察记录"""
    return await insight_service.list_all(db)
