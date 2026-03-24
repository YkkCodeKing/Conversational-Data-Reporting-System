from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Report(Base):
    """报表/仪表盘实体表"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    layout_config = Column(JSON, nullable=True)  # 仪表盘的布局配置
    is_published = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    items = relationship("ReportItem", back_populates="report", cascade="all, delete-orphan")


class ReportItem(Base):
    """报表组件项实体表：一个报表由多个组件（图表/洞察/文本）组合而成"""
    __tablename__ = "report_items"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    item_type = Column(String(50), nullable=False)  # chart / insight / text
    reference_id = Column(Integer, nullable=True)     # 引用的图表或洞察 ID
    position = Column(Integer, default=0)             # 组件排列顺序
    config_json = Column(JSON, nullable=True)         # 组件级别的自定义配置
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    report = relationship("Report", back_populates="items")
