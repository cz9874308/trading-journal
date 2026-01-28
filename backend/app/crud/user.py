"""
用户数据操作模块

本模块封装了用户（User）相关的所有数据库操作，包括查询、创建、
更新和删除功能。

函数列表
--------

- get_user_by_email: 根据邮箱查询用户
- get_user_by_username: 根据用户名查询用户
- get_user_by_id: 根据 ID 查询用户
- get_users: 分页获取用户列表
- get_user_count: 获取用户总数
- create_user: 创建新用户
- update_user: 更新用户信息
- delete_user: 删除用户

注意事项
--------

- 所有函数均为异步函数
- 密码在创建用户时自动进行哈希处理
- 删除用户会级联删除其所有投资组合和交易
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.auth.utils import get_password_hash
from typing import Optional, List


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """根据邮箱查询用户

    Args:
        db: 数据库会话
        email: 用户邮箱地址

    Returns:
        User: 用户对象，如果不存在返回 None
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """根据用户名查询用户

    Args:
        db: 数据库会话
        username: 用户名

    Returns:
        User: 用户对象，如果不存在返回 None
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """根据 ID 查询用户

    Args:
        db: 数据库会话
        user_id: 用户 ID

    Returns:
        User: 用户对象，如果不存在返回 None
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """分页获取用户列表

    Args:
        db: 数据库会话
        skip: 跳过的记录数（用于分页）
        limit: 返回的最大记录数

    Returns:
        List[User]: 用户列表
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_user_count(db: AsyncSession) -> int:
    """获取用户总数

    用于判断是否为首个注册用户（首个用户自动成为管理员）。

    Args:
        db: 数据库会话

    Returns:
        int: 用户总数
    """
    result = await db.execute(select(func.count(User.id)))
    return result.scalar_one()


async def create_user(db: AsyncSession, user: UserCreate, is_admin: bool = False) -> User:
    """创建新用户

    密码会自动进行 bcrypt 哈希处理后存储。

    Args:
        db: 数据库会话
        user: 用户创建数据
        is_admin: 是否设置为管理员

    Returns:
        User: 创建的用户对象
    """
    # 对密码进行哈希处理
    hashed_password = get_password_hash(user.password)
    
    # 创建用户对象
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_admin=is_admin
    )
    
    # 保存到数据库
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """更新用户信息

    只更新提供的字段，未提供的字段保持不变。

    Args:
        db: 数据库会话
        user_id: 要更新的用户 ID
        user_update: 更新数据

    Returns:
        User: 更新后的用户对象，如果用户不存在返回 None
    """
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()

    if db_user is None:
        return None

    # 只更新提供的字段
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """删除用户

    删除用户会级联删除其所有投资组合和交易记录。

    Args:
        db: 数据库会话
        user_id: 要删除的用户 ID

    Returns:
        bool: 删除成功返回 True，用户不存在返回 False
    """
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()

    if db_user is None:
        return False

    await db.delete(db_user)
    await db.commit()
    return True
