"""
用户数据验证模式

本模块定义了用户相关 API 的请求和响应数据验证模式，
使用 Pydantic 实现自动数据验证和序列化。

模式类说明
----------

- **UserBase**: 用户基础模式，定义通用字段
- **UserCreate**: 用户注册请求模式
- **UserUpdate**: 用户更新请求模式（所有字段可选）
- **UserInDB**: 数据库用户模式（包含完整字段）
- **User**: API 响应模式
- **Token**: JWT 令牌响应模式
- **TokenData**: 令牌载荷数据模式
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模式

    定义用户的通用字段，作为其他用户模式的基类。

    Attributes:
        email: 用户邮箱地址
        username: 用户名
        full_name: 用户全名（可选）
    """
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """用户注册请求模式

    用于用户注册接口的输入验证。

    Attributes:
        password: 用户密码（明文，存储前会进行哈希处理）
    """
    password: str


class UserUpdate(BaseModel):
    """用户更新请求模式

    用于更新用户信息，所有字段都是可选的，
    只更新提供的字段。

    Attributes:
        email: 新邮箱地址
        username: 新用户名
        full_name: 新全名
        is_active: 账户激活状态
        is_admin: 管理员权限（仅管理员可修改）
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserInDB(UserBase):
    """数据库用户模式

    包含数据库中存储的完整用户信息（不含密码）。

    Attributes:
        id: 用户 ID
        is_active: 账户是否激活
        is_admin: 是否为管理员
        created_at: 账户创建时间
        updated_at: 最后更新时间
    """
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic 配置"""
        from_attributes = True  # 允许从 ORM 模型创建


class User(UserInDB):
    """用户 API 响应模式

    用于 API 响应的用户数据模式，继承自 UserInDB。
    """
    pass


class Token(BaseModel):
    """JWT 令牌响应模式

    登录成功后返回的令牌信息。

    Attributes:
        access_token: JWT 访问令牌
        token_type: 令牌类型（固定为 "bearer"）
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌载荷数据模式

    JWT 令牌解码后的数据结构。

    Attributes:
        user_id: 用户 ID
    """
    user_id: Optional[int] = None
