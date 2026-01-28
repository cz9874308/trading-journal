"""
投资组合数据操作模块

本模块封装了投资组合（Portfolio）相关的所有数据库操作，
包括查询、创建、更新和删除功能。

函数列表
--------

- get_portfolio_by_id: 根据 ID 查询投资组合
- get_user_portfolios: 获取用户的所有投资组合
- create_portfolio: 创建新投资组合
- update_portfolio: 更新投资组合信息
- delete_portfolio: 删除投资组合

注意事项
--------

- 所有函数均为异步函数
- 删除投资组合会级联删除其所有交易记录
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Portfolio
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate
from typing import Optional, List


async def get_portfolio_by_id(db: AsyncSession, portfolio_id: int) -> Optional[Portfolio]:
    """根据 ID 查询投资组合

    Args:
        db: 数据库会话
        portfolio_id: 投资组合 ID

    Returns:
        Portfolio: 投资组合对象，如果不存在返回 None
    """
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    return result.scalar_one_or_none()


async def get_user_portfolios(db: AsyncSession, user_id: int) -> List[Portfolio]:
    """获取用户的所有投资组合

    Args:
        db: 数据库会话
        user_id: 用户 ID

    Returns:
        List[Portfolio]: 投资组合列表
    """
    result = await db.execute(select(Portfolio).where(Portfolio.user_id == user_id))
    return list(result.scalars().all())


async def create_portfolio(db: AsyncSession, portfolio: PortfolioCreate, user_id: int) -> Portfolio:
    """创建新投资组合

    Args:
        db: 数据库会话
        portfolio: 投资组合创建数据
        user_id: 所属用户 ID

    Returns:
        Portfolio: 创建的投资组合对象
    """
    db_portfolio = Portfolio(
        **portfolio.model_dump(),
        user_id=user_id
    )
    db.add(db_portfolio)
    await db.commit()
    await db.refresh(db_portfolio)
    return db_portfolio


async def update_portfolio(
    db: AsyncSession,
    portfolio_id: int,
    portfolio_update: PortfolioUpdate
) -> Optional[Portfolio]:
    """更新投资组合信息

    只更新提供的字段，未提供的字段保持不变。

    Args:
        db: 数据库会话
        portfolio_id: 要更新的投资组合 ID
        portfolio_update: 更新数据

    Returns:
        Portfolio: 更新后的投资组合对象，如果不存在返回 None
    """
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    db_portfolio = result.scalar_one_or_none()

    if db_portfolio is None:
        return None

    # 只更新提供的字段
    update_data = portfolio_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_portfolio, field, value)

    await db.commit()
    await db.refresh(db_portfolio)
    return db_portfolio


async def delete_portfolio(db: AsyncSession, portfolio_id: int) -> bool:
    """删除投资组合

    删除投资组合会级联删除其所有交易记录。

    Args:
        db: 数据库会话
        portfolio_id: 要删除的投资组合 ID

    Returns:
        bool: 删除成功返回 True，投资组合不存在返回 False
    """
    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
    db_portfolio = result.scalar_one_or_none()

    if db_portfolio is None:
        return False

    await db.delete(db_portfolio)
    await db.commit()
    return True
