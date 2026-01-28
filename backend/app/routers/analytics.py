"""
数据分析路由模块

本模块提供投资组合的数据分析和统计功能，帮助用户了解交易表现。

API 端点
--------

- GET /api/analytics/portfolio/{portfolio_id} - 获取投资组合综合分析
- GET /api/analytics/portfolio/{portfolio_id}/by-symbol - 按股票代码分组分析

分析指标
--------

综合分析提供以下指标：

- **total_trades**: 已平仓交易总数
- **total_profit_loss**: 总盈亏金额（INR）
- **win_rate**: 胜率（百分比）
- **average_profit_loss**: 平均盈亏
- **best_trade / worst_trade**: 最佳/最差交易
- **average_win / average_loss**: 平均盈利/亏损
- **profit_factor**: 盈利因子（总盈利/总亏损）

注意事项
--------

- 所有分析仅基于已平仓交易
- 持仓中的交易不计入统计
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Dict, Any
from app.database import get_db
from app.models import Trade, Portfolio
from app.models.trade import TradeStatus
from app.crud import portfolio as portfolio_crud
from app.auth.dependencies import get_current_active_user
from app.models import User

# 创建路由器
router = APIRouter(prefix="/analytics", tags=["analytics"])


async def verify_portfolio_ownership(portfolio_id: int, user_id: int, db: AsyncSession):
    """验证用户对投资组合的所有权

    在进行数据分析前，验证用户是否拥有对应的投资组合。

    Args:
        portfolio_id: 投资组合 ID
        user_id: 当前用户 ID
        db: 数据库会话

    Returns:
        Portfolio: 投资组合对象

    Raises:
        HTTPException: 404 - 投资组合不存在
        HTTPException: 403 - 用户无权访问该投资组合
    """
    portfolio = await portfolio_crud.get_portfolio_by_id(db, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    if portfolio.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this portfolio"
        )
    return portfolio


@router.get("/portfolio/{portfolio_id}", response_model=Dict[str, Any])
async def get_portfolio_analytics(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取投资组合综合分析

    计算并返回投资组合的综合交易统计数据。

    分析指标说明
    ------------

    - **total_trades**: 已平仓交易总数
    - **total_profit_loss**: 总盈亏金额（INR）
    - **win_rate**: 胜率 = 盈利交易数 / 总交易数 × 100
    - **average_profit_loss**: 平均每笔交易盈亏
    - **best_trade**: 盈利最多的交易
    - **worst_trade**: 亏损最多的交易
    - **total_wins / total_losses**: 盈利/亏损交易数
    - **average_win / average_loss**: 平均盈利/平均亏损
    - **profit_factor**: 盈利因子 = 总盈利 / |总亏损|

    Args:
        portfolio_id: 投资组合 ID
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        Dict: 包含各项分析指标的字典

    Note:
        - 仅统计已平仓（CLOSED）的交易
        - 如果没有已平仓交易，所有指标返回 0 或 None
    """
    portfolio = await verify_portfolio_ownership(portfolio_id, current_user.id, db)

    # 查询所有已平仓交易
    result = await db.execute(
        select(Trade).where(
            and_(
                Trade.portfolio_id == portfolio_id,
                Trade.status == TradeStatus.CLOSED
            )
        )
    )
    closed_trades = list(result.scalars().all())

    # 计算统计数据
    total_trades = len(closed_trades)
    
    # 如果没有已平仓交易，返回零值
    if total_trades == 0:
        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "total_trades": 0,
            "total_profit_loss": 0.0,
            "win_rate": 0.0,
            "average_profit_loss": 0.0,
            "best_trade": None,
            "worst_trade": None,
            "total_wins": 0,
            "total_losses": 0,
            "average_win": 0.0,
            "average_loss": 0.0,
            "profit_factor": 0.0,
        }

    # 计算总盈亏
    total_pl = sum(t.profit_loss or 0 for t in closed_trades)
    
    # 分类盈利和亏损交易
    winning_trades = [t for t in closed_trades if (t.profit_loss or 0) > 0]
    losing_trades = [t for t in closed_trades if (t.profit_loss or 0) <= 0]

    total_wins = len(winning_trades)
    total_losses = len(losing_trades)
    
    # 计算胜率
    win_rate = (total_wins / total_trades) * 100 if total_trades > 0 else 0

    # 计算平均值
    avg_pl = total_pl / total_trades if total_trades > 0 else 0
    avg_win = sum(t.profit_loss for t in winning_trades) / total_wins if total_wins > 0 else 0
    avg_loss = sum(t.profit_loss for t in losing_trades) / total_losses if total_losses > 0 else 0

    # 计算盈利因子（Profit Factor）
    # 盈利因子 = 总盈利 / |总亏损|
    # 盈利因子 > 1 表示整体盈利
    total_win_amount = sum(t.profit_loss for t in winning_trades)
    total_loss_amount = abs(sum(t.profit_loss for t in losing_trades))
    profit_factor = total_win_amount / total_loss_amount if total_loss_amount > 0 else 0

    # 找出最佳和最差交易
    best_trade = max(closed_trades, key=lambda t: t.profit_loss or 0)
    worst_trade = min(closed_trades, key=lambda t: t.profit_loss or 0)

    return {
        "portfolio_id": portfolio_id,
        "portfolio_name": portfolio.name,
        "total_trades": total_trades,
        "total_profit_loss": round(total_pl, 2),
        "win_rate": round(win_rate, 2),
        "average_profit_loss": round(avg_pl, 2),
        "best_trade": {
            "id": best_trade.id,
            "symbol": best_trade.symbol,
            "profit_loss": round(best_trade.profit_loss or 0, 2),
        },
        "worst_trade": {
            "id": worst_trade.id,
            "symbol": worst_trade.symbol,
            "profit_loss": round(worst_trade.profit_loss or 0, 2),
        },
        "total_wins": total_wins,
        "total_losses": total_losses,
        "average_win": round(avg_win, 2),
        "average_loss": round(avg_loss, 2),
        "profit_factor": round(profit_factor, 2),
    }


@router.get("/portfolio/{portfolio_id}/by-symbol", response_model=Dict[str, Any])
async def get_analytics_by_symbol(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """按股票代码分组分析

    将投资组合的交易按股票代码分组，计算每个股票的交易统计。

    返回数据结构
    ------------

    每个股票的统计包含：

    - **symbol**: 股票代码
    - **total_trades**: 该股票的交易总数
    - **total_profit_loss**: 该股票的总盈亏
    - **wins / losses**: 盈利/亏损交易数
    - **win_rate**: 该股票的胜率

    Args:
        portfolio_id: 投资组合 ID
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        Dict: 包含各股票统计数据的字典

    Example:
        >>> # 返回示例
        >>> {
        >>>     "symbols": [
        >>>         {"symbol": "RELIANCE", "total_trades": 10, "win_rate": 60.0, ...},
        >>>         {"symbol": "TCS", "total_trades": 5, "win_rate": 80.0, ...}
        >>>     ]
        >>> }
    """
    await verify_portfolio_ownership(portfolio_id, current_user.id, db)

    # 查询所有已平仓交易
    result = await db.execute(
        select(Trade).where(
            and_(
                Trade.portfolio_id == portfolio_id,
                Trade.status == TradeStatus.CLOSED
            )
        )
    )
    closed_trades = list(result.scalars().all())

    # 按股票代码分组统计
    symbol_stats = {}
    for trade in closed_trades:
        symbol = trade.symbol
        
        # 初始化股票统计
        if symbol not in symbol_stats:
            symbol_stats[symbol] = {
                "symbol": symbol,
                "total_trades": 0,
                "total_profit_loss": 0.0,
                "wins": 0,
                "losses": 0,
            }

        # 更新统计数据
        symbol_stats[symbol]["total_trades"] += 1
        symbol_stats[symbol]["total_profit_loss"] += trade.profit_loss or 0
        
        # 统计盈亏次数
        if (trade.profit_loss or 0) > 0:
            symbol_stats[symbol]["wins"] += 1
        else:
            symbol_stats[symbol]["losses"] += 1

    # 计算各股票的胜率
    for symbol in symbol_stats:
        total = symbol_stats[symbol]["total_trades"]
        wins = symbol_stats[symbol]["wins"]
        symbol_stats[symbol]["win_rate"] = round((wins / total) * 100, 2) if total > 0 else 0
        symbol_stats[symbol]["total_profit_loss"] = round(symbol_stats[symbol]["total_profit_loss"], 2)

    return {"symbols": list(symbol_stats.values())}
