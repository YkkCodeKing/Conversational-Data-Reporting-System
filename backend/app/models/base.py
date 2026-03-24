from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """全局声明式基类：用于所有模块内的 SQLAlchemy模型集成"""
    pass
