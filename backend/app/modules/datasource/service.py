from typing import List, Optional
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.modules.datasource.repository import datasource_repo
from app.modules.datasource.schemas import DataSourceCreate, DataSourceResponse, ConnectionTestResult


class DataSourceService:
    """数据源业务服务：仅负责管理操作与连通性测试"""

    @staticmethod
    async def create(db: AsyncSession, data: DataSourceCreate, user_id: Optional[int] = None) -> DataSourceResponse:
        """创建新数据源"""
        ds = await datasource_repo.create_datasource(
            db, data.name, data.db_type, data.connection_string, data.description, user_id,
        )
        return DataSourceResponse.model_validate(ds)

    @staticmethod
    async def list_all(db: AsyncSession) -> List[DataSourceResponse]:
        """获取所有活跃数据源列表"""
        items = await datasource_repo.list_datasources(db)
        return [DataSourceResponse.model_validate(ds) for ds in items]

    @staticmethod
    async def get_by_id(db: AsyncSession, datasource_id: int) -> Optional[DataSourceResponse]:
        """根据 ID 获取数据源详情"""
        ds = await datasource_repo.get(db, datasource_id)
        if not ds:
            return None
        return DataSourceResponse.model_validate(ds)

    @staticmethod
    async def delete(db: AsyncSession, datasource_id: int) -> bool:
        """软删除数据源"""
        return await datasource_repo.delete_datasource(db, datasource_id)

    @staticmethod
    def test_connection(connection_string: str) -> ConnectionTestResult:
        """
        同步测试数据库连接是否可用，
        并返回目标库所有的表名列表。
        """
        try:
            engine = create_engine(connection_string, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            engine.dispose()
            return ConnectionTestResult(success=True, message="连接成功", tables=tables)
        except Exception as e:
            logger.warning(f"数据源连接测试失败: {e}")
            return ConnectionTestResult(success=False, message=str(e))

    @staticmethod
    def get_schema_info(connection_string: str) -> dict:
        """
        获取目标数据库的 schema 元信息（表名 → 列信息）,
        用于为 NL2SQL 提供上下文。
        """
        try:
            engine = create_engine(connection_string, pool_pre_ping=True)
            inspector = inspect(engine)
            schema_info = {}
            for table_name in inspector.get_table_names():
                columns = []
                for col in inspector.get_columns(table_name):
                    columns.append({"name": col["name"], "type": str(col["type"])})
                schema_info[table_name] = columns
            engine.dispose()
            return schema_info
        except Exception as e:
            logger.error(f"获取 schema 元信息失败: {e}")
            return {}


datasource_service = DataSourceService()
