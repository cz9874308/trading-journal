"""
投资组合数据模型

本模块定义了投资组合（Portfolio）的数据库模型，用于存储用户的
投资组合信息。

表结构
------

portfolios 表包含以下字段：

- id: 主键，自增整数
- name: 组合名称
- description: 组合描述（可选）
- initial_balance: 初始资金（印度卢比）
- user_id: 所属用户 ID（外键）
- created_at: 创建时间
- updated_at: 更新时间

关系
----

- owner: 多对一关系，所属用户
- trades: 一对多关系，组合内的交易记录
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Portfolio(Base):
    """投资组合模型

    表示用户创建的一个投资组合，用于分组管理交易记录。

    Attributes:
        id: 组合唯一标识符
        name: 组合名称（如"长期投资"、"日内交易"等）
        description: 组合描述说明
        initial_balance: 初始资金金额（INR）
        user_id: 所属用户的 ID
        created_at: 组合创建时间
        updated_at: 最后更新时间
        owner: 组合所属的用户对象
        trades: 组合内的所有交易记录
    """
    __tablename__ = "portfolios"

    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 组合信息
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    initial_balance = Column(Float, default=0.0)  # 初始资金（INR）
    
    # 外键：所属用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系：所属用户
    owner = relationship("User", back_populates="portfolios")
    
    # 关系：组合内的交易记录
    # cascade="all, delete-orphan": 删除组合时同时删除其所有交易
    trades = relationship("Trade", back_populates="portfolio", cascade="all, delete-orphan")
