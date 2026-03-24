from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func

from app.models.base import Base


class Insight(Base):
    """数据洞察实体表：存储对查询结果的智能分析"""
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("query_records.id"), nullable=True)
    summary = Column(Text, nullable=False)
    key_findings = Column(JSON, nullable=True)    # 关键发现列表
    suggestions = Column(JSON, nullable=True)     # 建议与行动项列表
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
