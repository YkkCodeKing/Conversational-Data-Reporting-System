from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database.session import get_db
from app.modules.datasource.schemas import DataSourceCreate, DataSourceResponse, ConnectionTestResult
from app.modules.datasource.service import datasource_service

router = APIRouter(prefix="/datasource", tags=["DataSource"])


@router.post("/", response_model=DataSourceResponse)
async def create_datasource(data: DataSourceCreate, db: AsyncSession = Depends(get_db)):
    """创建新数据源"""
    return await datasource_service.create(db, data)


@router.get("/", response_model=List[DataSourceResponse])
async def list_datasources(db: AsyncSession = Depends(get_db)):
    """获取所有数据源列表"""
    return await datasource_service.list_all(db)


@router.get("/{datasource_id}", response_model=DataSourceResponse)
async def get_datasource(datasource_id: int, db: AsyncSession = Depends(get_db)):
    """根据 ID 获取数据源详情"""
    ds = await datasource_service.get_by_id(db, datasource_id)
    if not ds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="数据源不存在")
    return ds


@router.delete("/{datasource_id}")
async def delete_datasource(datasource_id: int, db: AsyncSession = Depends(get_db)):
    """软删除数据源"""
    success = await datasource_service.delete(db, datasource_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="数据源不存在")
    return {"detail": "删除成功"}


@router.post("/{datasource_id}/test", response_model=ConnectionTestResult)
async def test_datasource_connection(datasource_id: int, db: AsyncSession = Depends(get_db)):
    """测试数据源连接是否可用"""
    ds = await datasource_service.get_by_id(db, datasource_id)
    if not ds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="数据源不存在")
    return datasource_service.test_connection(ds.connection_string)
