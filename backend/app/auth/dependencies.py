"""
认证依赖注入模块

本模块提供 FastAPI 依赖注入函数，用于在 API 端点中获取当前用户信息
和进行权限验证。

依赖函数
--------

- **get_current_user**: 从 JWT 令牌获取当前用户
- **get_current_active_user**: 获取当前激活状态的用户
- **get_current_admin_user**: 获取当前管理员用户

使用方式
--------

在路由函数中使用 Depends 注入::

    @router.get("/me")
    async def get_me(current_user: User = Depends(get_current_active_user)):
        return current_user

认证流程
--------

1. 客户端在请求头中携带 Authorization: Bearer <token>
2. oauth2_scheme 提取令牌
3. get_current_user 验证令牌并返回用户对象
4. 可选的进一步验证（激活状态、管理员权限）
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.auth.utils import verify_token
from app.schemas.user import TokenData

# OAuth2 密码模式，指定令牌获取端点
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前登录用户

    从请求头的 JWT 令牌中解析用户身份，并从数据库获取用户对象。

    工作流程
    --------

    1. 从请求头提取 Bearer 令牌
    2. 验证并解码 JWT 令牌
    3. 从令牌载荷中获取用户 ID
    4. 查询数据库获取用户对象

    Args:
        token: JWT 访问令牌（由 oauth2_scheme 自动提取）
        db: 数据库会话（依赖注入）

    Returns:
        User: 当前登录的用户对象

    Raises:
        HTTPException: 401 - 令牌无效或用户不存在
    """
    # 定义认证失败异常
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 验证令牌
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    # 从载荷中获取用户 ID
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    # 转换用户 ID 为整数
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise credentials_exception

    # 从数据库查询用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前激活状态的用户

    在 get_current_user 基础上，额外验证用户账户是否处于激活状态。

    Args:
        current_user: 当前用户（由 get_current_user 注入）

    Returns:
        User: 激活状态的用户对象

    Raises:
        HTTPException: 400 - 用户账户未激活
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """获取当前管理员用户

    在 get_current_active_user 基础上，额外验证用户是否具有管理员权限。
    仅用于需要管理员权限的 API 端点。

    Args:
        current_user: 当前激活用户（由 get_current_active_user 注入）

    Returns:
        User: 具有管理员权限的用户对象

    Raises:
        HTTPException: 403 - 用户没有管理员权限
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
