from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.modules.chart.schemas import ChartGenerateRequest, ChartConfigResponse
from app.modules.chart.service import chart_service

router = APIRouter(prefix="/chart", tags=["Chart"])


@router.post("/generate", response_model=ChartConfigResponse)
async def generate_chart(data: ChartGenerateRequest, db: AsyncSession = Depends(get_db)):
    """根据数据自动生成图表可视化配置"""
    return await chart_service.generate_chart(db, data)


@router.get("/{chart_id}", response_model=ChartConfigResponse)
async def get_chart(chart_id: int, db: AsyncSession = Depends(get_db)):
    """根据 ID 获取图表配置"""
    chart = await chart_service.get_chart(db, chart_id)
    if not chart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图表配置不存在")
    return chart


@router.get("/", response_model=List[ChartConfigResponse])
async def list_charts(db: AsyncSession = Depends(get_db)):
    """列出所有图表配置"""
    return await chart_service.list_charts(db)
