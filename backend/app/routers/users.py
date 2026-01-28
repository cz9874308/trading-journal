"""
用户管理路由模块

本模块提供用户管理相关的 API 端点，仅限管理员访问。

API 端点
--------

- GET /api/users - 获取所有用户列表
- GET /api/users/{user_id} - 获取指定用户信息
- PATCH /api/users/{user_id} - 更新用户信息
- DELETE /api/users/{user_id} - 删除用户

权限说明
--------

所有端点都需要管理员权限。管理员可以：

- 查看所有用户
- 修改用户信息（包括激活状态和管理员权限）
- 删除其他用户（不能删除自己）
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.user import User, UserUpdate
from app.crud import user as user_crud
from app.auth.dependencies import get_current_admin_user
from app.models import User as UserModel

# 创建路由器
router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[User])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """获取所有用户列表（仅管理员）

    分页获取系统中的所有用户。

    Args:
        skip: 跳过的记录数（用于分页）
        limit: 返回的最大记录数
        db: 数据库会话
        current_user: 当前管理员用户

    Returns:
        List[User]: 用户列表
    """
    users = await user_crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """获取指定用户信息（仅管理员）

    根据用户 ID 获取用户详细信息。

    Args:
        user_id: 用户 ID
        db: 数据库会话
        current_user: 当前管理员用户

    Returns:
        User: 用户信息

    Raises:
        HTTPException: 404 - 用户不存在
    """
    user = await user_crud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """更新用户信息（仅管理员）

    管理员可以更新用户的以下信息：

    - 邮箱、用户名、全名
    - 激活状态（is_active）
    - 管理员权限（is_admin）

    Args:
        user_id: 要更新的用户 ID
        user_update: 更新数据
        db: 数据库会话
        current_user: 当前管理员用户

    Returns:
        User: 更新后的用户信息

    Raises:
        HTTPException: 404 - 用户不存在
    """
    user = await user_crud.update_user(db, user_id=user_id, user_update=user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """删除用户（仅管理员）

    删除指定用户及其所有投资组合和交易记录。
    管理员不能删除自己的账户。

    Args:
        user_id: 要删除的用户 ID
        db: 数据库会话
        current_user: 当前管理员用户

    Returns:
        None: 成功删除返回空响应

    Raises:
        HTTPException: 400 - 不能删除自己的账户
        HTTPException: 404 - 用户不存在
    """
    # 防止管理员删除自己的账户
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    success = await user_crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None
