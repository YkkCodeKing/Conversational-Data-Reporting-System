import json
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.shared.ai.llm_client import llm_client
from app.modules.chart.repository import chart_repo
from app.modules.chart.schemas import ChartGenerateRequest, ChartConfigResponse

# 图表推荐与配置生成的系统提示词
CHART_SYSTEM_PROMPT = """你是一个数据可视化专家。根据用户提供的数据，完成以下任务：
1. 推荐最适合的图表类型（bar / line / pie / scatter / table）。
2. 生成一份兼容 ECharts 的完整 JSON 配置项。

返回格式必须是严格的 JSON，结构如下：
{
  "chart_type": "推荐的图表类型",
  "title": "自动生成的图表标题",
  "config": { ... ECharts option 配置对象 ... }
}

注意事项：
- 数据应映射到 ECharts 的 xAxis/yAxis/series 等字段。
- 色彩方案使用现代商务风格。
- 不要在 JSON 外添加任何文字说明。
"""


class ChartService:
    """图表可视化业务服务：调用 LLM 推荐图表类型并生成 ECharts 配置"""

    @staticmethod
    async def generate_chart(db: AsyncSession, data: ChartGenerateRequest,
                             user_id: Optional[int] = None) -> ChartConfigResponse:
        """根据数据生成图表配置"""
        try:
            # 组装 LLM 请求
            user_content = f"数据内容: {json.dumps(data.data, ensure_ascii=False, default=str)}"
            if data.preferred_type:
                user_content += f"\n用户偏好图表类型: {data.preferred_type}"
            if data.title:
                user_content += f"\n图表标题建议: {data.title}"

            messages = [
                {"role": "system", "content": CHART_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ]

            raw_response = await llm_client.generate(messages)
            result = json.loads(raw_response)

            chart_type = data.preferred_type or result.get("chart_type", "bar")
            title = data.title or result.get("title", "数据图表")
            config_json = result.get("config", result)

            # 持久化
            chart = await chart_repo.create_chart_config(
                db, chart_type, config_json, data.query_id, title, user_id,
            )
            return ChartConfigResponse.model_validate(chart)

        except json.JSONDecodeError as e:
            logger.error(f"LLM 返回的图表配置不是合法 JSON: {e}")
            # 降级方案：创建一个基础配置
            fallback_config = {"title": {"text": data.title or "数据图表"}, "series": [{"type": "bar", "data": []}]}
            chart = await chart_repo.create_chart_config(
                db, "bar", fallback_config, data.query_id, data.title, user_id,
            )
            return ChartConfigResponse.model_validate(chart)

    @staticmethod
    async def get_chart(db: AsyncSession, chart_id: int) -> Optional[ChartConfigResponse]:
        """根据 ID 获取图表配置"""
        chart = await chart_repo.get(db, chart_id)
        if not chart:
            return None
        return ChartConfigResponse.model_validate(chart)

    @staticmethod
    async def list_charts(db: AsyncSession) -> list[ChartConfigResponse]:
        """列出所有图表配置"""
        charts = await chart_repo.list_chart_configs(db)
        return [ChartConfigResponse.model_validate(c) for c in charts]


chart_service = ChartService()
