"""
交易记录数据模型

本模块定义了交易记录（Trade）的数据库模型，用于存储用户的
每一笔交易详情，包括入场、出场信息和盈亏计算。

表结构
------

trades 表包含以下字段：

- id: 主键，自增整数
- portfolio_id: 所属投资组合 ID（外键）
- symbol: 交易标的代码（如 RELIANCE, TCS）
- trade_type: 交易类型（做多/做空）
- status: 交易状态（持仓中/已平仓）
- entry_price: 入场价格
- entry_date: 入场时间
- quantity: 交易数量
- exit_price: 出场价格（平仓时填写）
- exit_date: 出场时间（平仓时填写）
- profit_loss: 盈亏金额（自动计算）
- profit_loss_percentage: 盈亏百分比（自动计算）
- notes: 交易笔记
- tags: 标签（逗号分隔）
- screenshot_path: 截图文件路径

枚举类型
--------

- TradeType: 交易类型（long=做多, short=做空）
- TradeStatus: 交易状态（open=持仓中, closed=已平仓）
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class TradeType(str, enum.Enum):
    """交易类型枚举

    Attributes:
        LONG: 做多（买入后等待上涨卖出）
        SHORT: 做空（借入卖出后等待下跌买回）
    """
    LONG = "long"
    SHORT = "short"


class TradeStatus(str, enum.Enum):
    """交易状态枚举

    Attributes:
        OPEN: 持仓中（尚未平仓）
        CLOSED: 已平仓（交易已结束）
    """
    OPEN = "open"
    CLOSED = "closed"


class Trade(Base):
    """交易记录模型

    存储单笔交易的完整信息，包括入场、出场和盈亏数据。

    盈亏计算公式
    ------------

    - 做多盈亏 = (出场价 - 入场价) × 数量
    - 做空盈亏 = (入场价 - 出场价) × 数量
    - 盈亏百分比 = 盈亏金额 / (入场价 × 数量) × 100

    Attributes:
        id: 交易唯一标识符
        portfolio_id: 所属投资组合 ID
        symbol: 交易标的代码（NSE/BSE 股票代码）
        trade_type: 交易类型（做多/做空）
        status: 交易状态
        entry_price: 入场价格（INR）
        entry_date: 入场日期时间
        quantity: 交易数量（股数）
        exit_price: 出场价格（平仓时设置）
        exit_date: 出场日期时间（平仓时设置）
        profit_loss: 盈亏金额（INR）
        profit_loss_percentage: 盈亏百分比
        notes: 交易笔记和策略说明
        tags: 标签，用于分类（逗号分隔）
        screenshot_path: 交易截图文件路径
        created_at: 记录创建时间
        updated_at: 记录更新时间
        portfolio: 所属投资组合对象
    """
    __tablename__ = "trades"

    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 外键：所属投资组合
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)

    # 交易基本信息
    symbol = Column(String, nullable=False, index=True)  # 股票代码，建立索引以加速查询
    trade_type = Column(Enum(TradeType), nullable=False)  # 做多/做空
    status = Column(Enum(TradeStatus), default=TradeStatus.OPEN)  # 默认为持仓中

    # 入场信息
    entry_price = Column(Float, nullable=False)  # 入场价格
    entry_date = Column(DateTime(timezone=True), nullable=False)  # 入场时间
    quantity = Column(Float, nullable=False)  # 交易数量

    # 出场信息（持仓中时为空）
    exit_price = Column(Float, nullable=True)  # 出场价格
    exit_date = Column(DateTime(timezone=True), nullable=True)  # 出场时间

    # 盈亏数据（平仓时自动计算）
    profit_loss = Column(Float, nullable=True)  # 盈亏金额（INR）
    profit_loss_percentage = Column(Float, nullable=True)  # 盈亏百分比

    # 附加信息
    notes = Column(Text, nullable=True)  # 交易笔记
    tags = Column(String, nullable=True)  # 标签（逗号分隔，如"突破,趋势"）
    screenshot_path = Column(String, nullable=True)  # 截图文件路径

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系：所属投资组合
    portfolio = relationship("Portfolio", back_populates="trades")
