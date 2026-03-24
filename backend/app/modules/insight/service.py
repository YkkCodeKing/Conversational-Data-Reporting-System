import json
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.shared.ai.llm_client import llm_client
from app.modules.insight.repository import insight_repo
from app.modules.insight.schemas import InsightGenerateRequest, InsightResponse

# 数据洞察的系统提示词
INSIGHT_SYSTEM_PROMPT = """你是一位资深数据分析师。根据用户提供的数据，进行深度分析并生成洞察报告。

你必须返回严格的 JSON 格式，结构如下：
{
  "summary": "数据的总体概述（2-3句话）",
  "key_findings": [
    "关键发现1：...",
    "关键发现2：...",
    "关键发现3：..."
  ],
  "suggestions": [
    "建议1：...",
    "建议2：..."
  ]
}

分析维度：
1. 数据趋势与规律
2. 异常值或离群点
3. 数据分布特征
4. 核心指标的业务含义
5. 可行的行动建议

不要在 JSON 外添加任何文字说明。
"""


class InsightService:
    """智能数据洞察业务服务：调用 LLM 对数据进行深度分析"""

    @staticmethod
    async def generate_insight(db: AsyncSession, data: InsightGenerateRequest,
                               user_id: Optional[int] = None) -> InsightResponse:
        """对提供的数据进行智能分析并生成洞察"""
        try:
            user_content = f"请分析以下数据:\n{json.dumps(data.data, ensure_ascii=False, default=str)}"
            if data.context:
                user_content += f"\n\n业务背景: {data.context}"

            messages = [
                {"role": "system", "content": INSIGHT_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ]

            raw_response = await llm_client.generate(messages)
            result = json.loads(raw_response)

            summary = result.get("summary", "数据分析完成")
            key_findings = result.get("key_findings", [])
            suggestions = result.get("suggestions", [])

            insight = await insight_repo.create_insight(
                db, summary, key_findings, suggestions, data.query_id, user_id,
            )
            return InsightResponse.model_validate(insight)

        except json.JSONDecodeError as e:
            logger.error(f"LLM 返回的洞察结果不是合法 JSON: {e}")
            # 降级：将原始文本作为 summary 保存
            insight = await insight_repo.create_insight(
                db, raw_response, [], [], data.query_id, user_id,
            )
            return InsightResponse.model_validate(insight)

    @staticmethod
    async def get_insight(db: AsyncSession, insight_id: int) -> Optional[InsightResponse]:
        """根据 ID 获取洞察详情"""
        insight = await insight_repo.get(db, insight_id)
        if not insight:
            return None
        return InsightResponse.model_validate(insight)

    @staticmethod
    async def list_all(db: AsyncSession) -> list[InsightResponse]:
        """列出所有洞察记录"""
        insights = await insight_repo.list_insights(db)
        return [InsightResponse.model_validate(i) for i in insights]


insight_service = InsightService()
