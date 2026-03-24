from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.modules.query.schemas import QueryRequest, QueryResponse, QueryHistoryResponse
from app.modules.query.service import query_service
from app.modules.query.repository import query_repo

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/execute", response_model=QueryResponse)
async def execute_query(data: QueryRequest, db: AsyncSession = Depends(get_db)):
    """自然语言查询执行接口：NL → SQL → 结果"""
    result = await query_service.execute_query(db, data.datasource_id, data.question)
    return result


@router.get("/history", response_model=List[QueryHistoryResponse])
async def get_query_history(db: AsyncSession = Depends(get_db)):
    """获取查询历史记录"""
    records = await query_repo.list_query_history(db)
    return [QueryHistoryResponse.model_validate(r) for r in records]
