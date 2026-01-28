"""
交易记录路由模块

本模块提供交易记录管理的 API 端点，包括交易的创建、查询、更新、
平仓和删除功能，以及交易截图上传。

API 端点
--------

- GET /api/trades/portfolio/{portfolio_id} - 获取投资组合的交易列表
- POST /api/trades - 创建新交易
- GET /api/trades/{trade_id} - 获取指定交易
- PATCH /api/trades/{trade_id} - 更新交易
- POST /api/trades/{trade_id}/close - 平仓交易
- POST /api/trades/{trade_id}/screenshot - 上传交易截图
- DELETE /api/trades/{trade_id} - 删除交易

权限说明
--------

- 所有端点都需要用户认证
- 用户只能操作自己投资组合中的交易
- 通过投资组合所有权验证来确保权限
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pathlib import Path
import shutil
from datetime import datetime
from app.database import get_db
from app.schemas.trade import Trade, TradeCreate, TradeUpdate, TradeClose
from app.models.trade import TradeStatus
from app.crud import trade as trade_crud
from app.crud import portfolio as portfolio_crud
from app.auth.dependencies import get_current_active_user
from app.models import User

# 创建路由器
router = APIRouter(prefix="/trades", tags=["trades"])

# 截图上传目录
# 如果目录不存在则创建
UPLOAD_DIR = Path("uploads/screenshots")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def verify_portfolio_ownership(portfolio_id: int, user_id: int, db: AsyncSession):
    """验证用户对投资组合的所有权

    在操作交易记录前，验证用户是否拥有对应的投资组合。

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


@router.get("/portfolio/{portfolio_id}", response_model=List[Trade])
async def get_portfolio_trades(
    portfolio_id: int,
    status: Optional[TradeStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取投资组合的交易列表

    获取指定投资组合中的所有交易记录，支持按状态筛选。

    Args:
        portfolio_id: 投资组合 ID
        status: 交易状态筛选（可选，open=持仓中, closed=已平仓）
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        List[Trade]: 交易记录列表，按入场时间降序排列
    """
    await verify_portfolio_ownership(portfolio_id, current_user.id, db)
    trades = await trade_crud.get_portfolio_trades(db, portfolio_id=portfolio_id, status=status)
    return trades


@router.post("/", response_model=Trade, status_code=status.HTTP_201_CREATED)
async def create_trade(
    trade: TradeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建新交易

    在指定投资组合中创建一笔新的交易记录。
    创建的交易默认状态为"持仓中"（OPEN）。

    Args:
        trade: 交易创建数据
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        Trade: 创建的交易记录
    """
    await verify_portfolio_ownership(trade.portfolio_id, current_user.id, db)
    return await trade_crud.create_trade(db, trade=trade)


@router.get("/{trade_id}", response_model=Trade)
async def get_trade(
    trade_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取指定交易

    根据交易 ID 获取交易详情。

    Args:
        trade_id: 交易 ID
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        Trade: 交易记录详情

    Raises:
        HTTPException: 404 - 交易不存在
    """
    trade = await trade_crud.get_trade_by_id(db, trade_id=trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )

    # 通过投资组合验证所有权
    await verify_portfolio_ownership(trade.portfolio_id, current_user.id, db)
    return trade


@router.patch("/{trade_id}", response_model=Trade)
async def update_trade(
    trade_id: int,
    trade_update: TradeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新交易

    更新指定交易的信息。如果更新了出场价格，会自动重新计算盈亏。

    Args:
        trade_id: 交易 ID
        trade_update: 更新数据
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        Trade: 更新后的交易记录

    Raises:
        HTTPException: 404 - 交易不存在
    """
    trade = await trade_crud.get_trade_by_id(db, trade_id=trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )

    # 通过投资组合验证所有权
    await verify_portfolio_ownership(trade.portfolio_id, current_user.id, db)

    updated_trade = await trade_crud.update_trade(db, trade_id=trade_id, trade_update=trade_update)
    return updated_trade


@router.post("/{trade_id}/close", response_model=Trade)
async def close_trade(
    trade_id: int,
    trade_close: TradeClose,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """平仓交易

    关闭一笔交易，设置出场价格和时间，自动计算盈亏。

    盈亏计算
    --------

    - 做多盈亏 = (出场价 - 入场价) × 数量
    - 做空盈亏 = (入场价 - 出场价) × 数量

    Args:
        trade_id: 交易 ID
        trade_close: 平仓数据（出场价格和时间）
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        Trade: 平仓后的交易记录（包含盈亏数据）

    Raises:
        HTTPException: 404 - 交易不存在
        HTTPException: 400 - 交易已经平仓
    """
    trade = await trade_crud.get_trade_by_id(db, trade_id=trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )

    # 通过投资组合验证所有权
    await verify_portfolio_ownership(trade.portfolio_id, current_user.id, db)

    # 检查交易是否已经平仓
    if trade.status == TradeStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trade is already closed"
        )

    closed_trade = await trade_crud.close_trade(db, trade_id=trade_id, trade_close=trade_close)
    return closed_trade


@router.post("/{trade_id}/screenshot")
async def upload_screenshot(
    trade_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """上传交易截图

    为交易上传一张截图（如交易图表、入场点位等）。

    Args:
        trade_id: 交易 ID
        file: 上传的图片文件
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        dict: 包含文件名和保存路径的字典

    Raises:
        HTTPException: 404 - 交易不存在
        HTTPException: 400 - 文件类型不支持

    Note:
        支持的图片格式：JPEG、PNG、WebP
    """
    trade = await trade_crud.get_trade_by_id(db, trade_id=trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )

    # 通过投资组合验证所有权
    await verify_portfolio_ownership(trade.portfolio_id, current_user.id, db)

    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files (JPEG, PNG, WebP) are allowed"
        )

    # 创建唯一文件名（包含交易 ID 和时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(file.filename).suffix
    filename = f"trade_{trade_id}_{timestamp}{file_extension}"
    file_path = UPLOAD_DIR / filename

    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 更新交易的截图路径
    from app.schemas.trade import TradeUpdate
    trade_update = TradeUpdate(screenshot_path=str(file_path))
    await trade_crud.update_trade(db, trade_id=trade_id, trade_update=trade_update)

    return {"filename": filename, "path": str(file_path)}


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trade(
    trade_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除交易

    删除指定的交易记录。

    Args:
        trade_id: 交易 ID
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        None: 成功删除返回空响应

    Raises:
        HTTPException: 404 - 交易不存在
    """
    trade = await trade_crud.get_trade_by_id(db, trade_id=trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )

    # 通过投资组合验证所有权
    await verify_portfolio_ownership(trade.portfolio_id, current_user.id, db)

    await trade_crud.delete_trade(db, trade_id=trade_id)
    return None
