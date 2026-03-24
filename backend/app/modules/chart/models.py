from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func

from app.models.base import Base


class ChartConfig(Base):
    """图表配置实体表：存储查询结果对应的可视化配置"""
    __tablename__ = "chart_configs"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("query_records.id"), nullable=True)
    chart_type = Column(String(50), nullable=False)  # bar / line / pie / scatter / table
    title = Column(String(255), nullable=True)
    config_json = Column(JSON, nullable=False)  # ECharts 兼容的完整配置项
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
