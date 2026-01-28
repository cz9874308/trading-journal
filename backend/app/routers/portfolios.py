"""
投资组合路由模块

本模块提供投资组合管理的 API 端点。

API 端点
--------

- GET /api/portfolios - 获取当前用户的所有投资组合
- POST /api/portfolios - 创建新投资组合
- GET /api/portfolios/{portfolio_id} - 获取指定投资组合
- PATCH /api/portfolios/{portfolio_id} - 更新投资组合
- DELETE /api/portfolios/{portfolio_id} - 删除投资组合

权限说明
--------

- 所有端点都需要用户认证
- 用户只能访问自己创建的投资组合
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.portfolio import Portfolio, PortfolioCreate, PortfolioUpdate
from app.crud import portfolio as portfolio_crud
from app.auth.dependencies import get_current_active_user
from app.models import User

# 创建路由器
router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.get("", response_model=List[Portfolio])
async def get_my_portfolios(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的所有投资组合

    返回当前登录用户创建的所有投资组合列表。

    Args:
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        List[Portfolio]: 投资组合列表
    """
    portfolios = await portfolio_crud.get_user_portfolios(db, user_id=current_user.id)
    return portfolios


@router.post("", response_model=Portfolio, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建新投资组合

    为当前用户创建一个新的投资组合。

    Args:
        portfolio: 投资组合创建数据
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        Portfolio: 创建的投资组合信息
    """
    return await portfolio_crud.create_portfolio(db, portfolio=portfolio, user_id=current_user.id)


@router.get("/{portfolio_id}", response_model=Portfolio)
async def get_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取指定投资组合

    根据 ID 获取投资组合详情。用户只能访问自己的投资组合。

    Args:
        portfolio_id: 投资组合 ID
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        Portfolio: 投资组合信息

    Raises:
        HTTPException: 404 - 投资组合不存在
        HTTPException: 403 - 无权访问该投资组合
    """
    portfolio = await portfolio_crud.get_portfolio_by_id(db, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )

    # 验证用户是否拥有该投资组合
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this portfolio"
        )

    return portfolio


@router.patch("/{portfolio_id}", response_model=Portfolio)
async def update_portfolio(
    portfolio_id: int,
    portfolio_update: PortfolioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新投资组合

    更新指定投资组合的信息。用户只能更新自己的投资组合。

    Args:
        portfolio_id: 投资组合 ID
        portfolio_update: 更新数据
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        Portfolio: 更新后的投资组合信息

    Raises:
        HTTPException: 404 - 投资组合不存在
        HTTPException: 403 - 无权修改该投资组合
    """
    portfolio = await portfolio_crud.get_portfolio_by_id(db, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )

    # 验证用户是否拥有该投资组合
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this portfolio"
        )

    updated_portfolio = await portfolio_crud.update_portfolio(
        db, portfolio_id=portfolio_id, portfolio_update=portfolio_update
    )
    return updated_portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除投资组合

    删除指定的投资组合及其所有交易记录。用户只能删除自己的投资组合。

    Args:
        portfolio_id: 投资组合 ID
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        None: 成功删除返回空响应

    Raises:
        HTTPException: 404 - 投资组合不存在
        HTTPException: 403 - 无权删除该投资组合

    Note:
        删除投资组合会级联删除该组合下的所有交易记录。
    """
    portfolio = await portfolio_crud.get_portfolio_by_id(db, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )

    # 验证用户是否拥有该投资组合
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this portfolio"
        )

    await portfolio_crud.delete_portfolio(db, portfolio_id=portfolio_id)
    return None
