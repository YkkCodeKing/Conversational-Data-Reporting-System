import json
from typing import Optional, Any
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.shared.ai.llm_client import llm_client
from app.modules.query.repository import query_repo
from app.modules.datasource.repository import datasource_repo
from app.modules.datasource.service import datasource_service

# NL2SQL 的系统提示词模板
NL2SQL_SYSTEM_PROMPT = """你是一个精通 SQL 的数据库专家。根据用户的自然语言问题和目标数据库的 schema 信息，生成准确的 SQL 查询语句。

规则：
1. 仅生成 SELECT 查询，禁止任何写操作（INSERT/UPDATE/DELETE/DROP）。
2. 返回格式必须是纯 SQL，不要包含 markdown 代码块或额外说明。
3. 如果问题模糊，生成最合理的查询并使用 LIMIT 限制结果集大小。
4. 使用标准 SQL 语法，兼顾 PostgreSQL 和 MySQL。

以下是目标数据库的表结构信息：
{schema_info}
"""


class QueryService:
    """NL2SQL 核心业务服务：Schema组装 → LLM 生成SQL → 安全执行 → 返回结果"""

    @staticmethod
    async def execute_query(db: AsyncSession, datasource_id: int, question: str,
                            user_id: Optional[int] = None) -> dict:
        """
        完整的自然语言查询执行流水线：
        1. 获取目标数据源及其 schema 元信息
        2. 组装 NL2SQL 提示词，调用 LLM 生成 SQL
        3. 在目标数据库上安全执行 SQL
        4. 将结果保存到查询记录表
        """
        # 1. 获取数据源
        ds = await datasource_repo.get(db, datasource_id)
        if not ds:
            return {"error": "数据源不存在", "status": "error"}

        # 创建查询记录
        record = await query_repo.create_query_record(db, datasource_id, question, user_id)

        try:
            # 2. 获取目标库的 schema 信息
            schema_info = datasource_service.get_schema_info(ds.connection_string)
            schema_str = json.dumps(schema_info, ensure_ascii=False, indent=2)

            # 3. 调用 LLM 生成 SQL
            system_prompt = NL2SQL_SYSTEM_PROMPT.format(schema_info=schema_str)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ]
            generated_sql = await llm_client.generate(messages)
            generated_sql = generated_sql.strip().strip("`").strip()

            # 4. 安全执行 SQL（仅允许 SELECT）
            if not generated_sql.upper().lstrip().startswith("SELECT"):
                await query_repo.update_query_result(db, record, generated_sql, "SQL 不安全：非 SELECT 操作", "error")
                return {"error": "生成的 SQL 非法：仅允许 SELECT 查询", "generated_sql": generated_sql, "status": "error"}

            result_data = QueryService._execute_sql_on_datasource(ds.connection_string, generated_sql)

            # 5. 生成结果摘要
            summary = f"查询返回 {len(result_data)} 条记录"
            await query_repo.update_query_result(db, record, generated_sql, summary, "success")

            return {
                "id": record.id,
                "datasource_id": datasource_id,
                "natural_language": question,
                "generated_sql": generated_sql,
                "result_summary": summary,
                "result_data": result_data,
                "status": "success",
                "created_at": str(record.created_at),
            }

        except Exception as e:
            logger.error(f"NL2SQL 查询执行失败: {e}")
            await query_repo.update_query_result(db, record, "", str(e), "error")
            return {"error": str(e), "status": "error"}

    @staticmethod
    def _execute_sql_on_datasource(connection_string: str, sql: str) -> list[dict]:
        """在目标数据源上同步执行只读 SQL 并返回字典列表"""
        engine = create_engine(connection_string, pool_pre_ping=True)
        try:
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                columns = list(result.keys())
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                return rows
        finally:
            engine.dispose()


query_service = QueryService()
