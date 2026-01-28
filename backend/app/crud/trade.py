"""
交易记录数据操作模块

本模块封装了交易记录（Trade）相关的所有数据库操作，包括查询、
创建、更新、平仓和删除功能，以及盈亏计算逻辑。

函数列表
--------

- calculate_profit_loss: 计算交易盈亏
- get_trade_by_id: 根据 ID 查询交易
- get_portfolio_trades: 获取投资组合的交易列表
- create_trade: 创建新交易
- update_trade: 更新交易信息
- close_trade: 平仓交易
- delete_trade: 删除交易

盈亏计算
--------

- 做多盈亏 = (出场价 - 入场价) × 数量
- 做空盈亏 = (入场价 - 出场价) × 数量
- 盈亏百分比 = 盈亏金额 / (入场价 × 数量) × 100
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import Trade
from app.models.trade import TradeStatus
from app.schemas.trade import TradeCreate, TradeUpdate, TradeClose
from typing import Optional, List


def calculate_profit_loss(trade: Trade) -> tuple[float, float]:
    """计算交易的盈亏金额和百分比

    根据交易类型（做多/做空）计算盈亏：
    - 做多: 盈亏 = (出场价 - 入场价) × 数量
    - 做空: 盈亏 = (入场价 - 出场价) × 数量

    Args:
        trade: 交易记录对象

    Returns:
        tuple[float, float]: (盈亏金额, 盈亏百分比)
            如果没有出场价格，返回 (0.0, 0.0)
    """
    if trade.exit_price is None:
        return 0.0, 0.0

    # 根据交易类型计算盈亏
    if trade.trade_type == "long":
        # 做多：价格上涨盈利
        pl = (trade.exit_price - trade.entry_price) * trade.quantity
    else:
        # 做空：价格下跌盈利
        pl = (trade.entry_price - trade.exit_price) * trade.quantity

    # 计算盈亏百分比
    pl_percentage = (pl / (trade.entry_price * trade.quantity)) * 100
    return pl, pl_percentage


async def get_trade_by_id(db: AsyncSession, trade_id: int) -> Optional[Trade]:
    """根据 ID 查询交易记录

    Args:
        db: 数据库会话
        trade_id: 交易 ID

    Returns:
        Trade: 交易记录对象，如果不存在返回 None
    """
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    return result.scalar_one_or_none()


async def get_portfolio_trades(
    db: AsyncSession,
    portfolio_id: int,
    status: Optional[TradeStatus] = None
) -> List[Trade]:
    """获取投资组合的交易列表

    支持按交易状态筛选，结果按入场时间降序排列。

    Args:
        db: 数据库会话
        portfolio_id: 投资组合 ID
        status: 交易状态筛选（可选）

    Returns:
        List[Trade]: 交易记录列表，按入场时间降序排列
    """
    query = select(Trade).where(Trade.portfolio_id == portfolio_id)
    
    # 如果指定了状态，添加筛选条件
    if status:
        query = query.where(Trade.status == status)
    
    # 按入场时间降序排列（最新的在前）
    result = await db.execute(query.order_by(Trade.entry_date.desc()))
    return list(result.scalars().all())


async def create_trade(db: AsyncSession, trade: TradeCreate) -> Trade:
    """创建新交易记录

    创建的交易默认状态为"持仓中"（OPEN）。

    Args:
        db: 数据库会话
        trade: 交易创建数据

    Returns:
        Trade: 创建的交易记录对象
    """
    db_trade = Trade(**trade.model_dump())
    db.add(db_trade)
    await db.commit()
    await db.refresh(db_trade)
    return db_trade


async def update_trade(
    db: AsyncSession,
    trade_id: int,
    trade_update: TradeUpdate
) -> Optional[Trade]:
    """更新交易记录

    只更新提供的字段，如果更新了出场价格，会自动重新计算盈亏。

    Args:
        db: 数据库会话
        trade_id: 要更新的交易 ID
        trade_update: 更新数据

    Returns:
        Trade: 更新后的交易记录对象，如果不存在返回 None
    """
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    db_trade = result.scalar_one_or_none()

    if db_trade is None:
        return None

    # 只更新提供的字段
    update_data = trade_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_trade, field, value)

    # 如果有出场价格，重新计算盈亏
    if db_trade.exit_price is not None:
        pl, pl_pct = calculate_profit_loss(db_trade)
        db_trade.profit_loss = pl
        db_trade.profit_loss_percentage = pl_pct

    await db.commit()
    await db.refresh(db_trade)
    return db_trade


async def close_trade(db: AsyncSession, trade_id: int, trade_close: TradeClose) -> Optional[Trade]:
    """平仓交易

    设置出场价格和时间，将交易状态更改为"已平仓"，并自动计算盈亏。

    Args:
        db: 数据库会话
        trade_id: 要平仓的交易 ID
        trade_close: 平仓数据（出场价格和时间）

    Returns:
        Trade: 平仓后的交易记录对象，如果交易不存在返回 None
    """
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    db_trade = result.scalar_one_or_none()

    if db_trade is None:
        return None

    # 设置出场信息
    db_trade.exit_price = trade_close.exit_price
    db_trade.exit_date = trade_close.exit_date
    db_trade.status = TradeStatus.CLOSED

    # 计算盈亏
    pl, pl_pct = calculate_profit_loss(db_trade)
    db_trade.profit_loss = pl
    db_trade.profit_loss_percentage = pl_pct

    await db.commit()
    await db.refresh(db_trade)
    return db_trade


async def delete_trade(db: AsyncSession, trade_id: int) -> bool:
    """删除交易记录

    Args:
        db: 数据库会话
        trade_id: 要删除的交易 ID

    Returns:
        bool: 删除成功返回 True，交易不存在返回 False
    """
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    db_trade = result.scalar_one_or_none()

    if db_trade is None:
        return False

    await db.delete(db_trade)
    await db.commit()
    return True
