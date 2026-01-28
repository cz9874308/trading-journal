"""
交易记录数据验证模式

本模块定义了交易记录相关 API 的请求和响应数据验证模式。

模式类说明
----------

- **TradeBase**: 交易基础模式
- **TradeCreate**: 创建交易请求模式
- **TradeUpdate**: 更新交易请求模式
- **TradeClose**: 平仓请求模式
- **Trade**: API 响应模式
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.trade import TradeType, TradeStatus


class TradeBase(BaseModel):
    """交易基础模式

    定义交易记录的通用字段。

    Attributes:
        symbol: 交易标的代码（如 RELIANCE, TCS, INFY）
        trade_type: 交易类型（做多/做空）
        entry_price: 入场价格（INR）
        entry_date: 入场日期时间
        quantity: 交易数量（股数）
        notes: 交易笔记（可选）
        tags: 标签（可选，逗号分隔）
    """
    symbol: str
    trade_type: TradeType
    entry_price: float
    entry_date: datetime
    quantity: float
    notes: Optional[str] = None
    tags: Optional[str] = None


class TradeCreate(TradeBase):
    """创建交易请求模式

    用于创建新交易记录的输入验证。

    Attributes:
        portfolio_id: 所属投资组合 ID
    """
    portfolio_id: int


class TradeUpdate(BaseModel):
    """更新交易请求模式

    用于更新交易记录，所有字段都是可选的。

    Attributes:
        symbol: 交易标的代码
        trade_type: 交易类型
        entry_price: 入场价格
        entry_date: 入场日期时间
        quantity: 交易数量
        exit_price: 出场价格
        exit_date: 出场日期时间
        status: 交易状态
        notes: 交易笔记
        tags: 标签
    """
    symbol: Optional[str] = None
    trade_type: Optional[TradeType] = None
    entry_price: Optional[float] = None
    entry_date: Optional[datetime] = None
    quantity: Optional[float] = None
    exit_price: Optional[float] = None
    exit_date: Optional[datetime] = None
    status: Optional[TradeStatus] = None
    notes: Optional[str] = None
    tags: Optional[str] = None


class TradeClose(BaseModel):
    """平仓请求模式

    用于平仓（关闭）交易的输入验证。

    Attributes:
        exit_price: 出场价格（INR）
        exit_date: 出场日期时间

    Note:
        提交此请求后，系统会自动计算盈亏并更新交易状态为已平仓。
    """
    exit_price: float
    exit_date: datetime


class Trade(TradeBase):
    """交易记录 API 响应模式

    用于 API 响应的完整交易数据模式。

    Attributes:
        id: 交易 ID
        portfolio_id: 所属投资组合 ID
        status: 交易状态
        exit_price: 出场价格（平仓后有值）
        exit_date: 出场日期（平仓后有值）
        profit_loss: 盈亏金额（INR，平仓后计算）
        profit_loss_percentage: 盈亏百分比（平仓后计算）
        screenshot_path: 交易截图路径
        created_at: 记录创建时间
        updated_at: 记录更新时间
    """
    id: int
    portfolio_id: int
    status: TradeStatus
    exit_price: Optional[float] = None
    exit_date: Optional[datetime] = None
    profit_loss: Optional[float] = None
    profit_loss_percentage: Optional[float] = None
    screenshot_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic 配置"""
        from_attributes = True  # 允许从 ORM 模型创建
