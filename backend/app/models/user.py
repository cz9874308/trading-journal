"""
用户数据模型

本模块定义了用户（User）的数据库模型，用于存储用户账户信息。

表结构
------

users 表包含以下字段：

- id: 主键，自增整数
- email: 邮箱地址，唯一索引
- username: 用户名，唯一索引
- hashed_password: 哈希后的密码
- full_name: 用户全名（可选）
- is_active: 账户是否激活
- is_admin: 是否为管理员
- created_at: 创建时间
- updated_at: 更新时间

关系
----

- portfolios: 一对多关系，用户拥有的投资组合
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """用户模型

    存储用户账户信息，包括认证凭据和权限标识。

    Attributes:
        id: 用户唯一标识符
        email: 用户邮箱（用于登录和通知）
        username: 用户名（用于登录和显示）
        hashed_password: bcrypt 哈希后的密码
        full_name: 用户真实姓名
        is_active: 账户是否处于激活状态
        is_admin: 是否具有管理员权限
        created_at: 账户创建时间
        updated_at: 最后更新时间
        portfolios: 用户创建的投资组合列表
    """
    __tablename__ = "users"

    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 认证字段
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # 用户信息
    full_name = Column(String, nullable=True)
    
    # 状态和权限
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系：用户拥有的投资组合
    # cascade="all, delete-orphan": 删除用户时同时删除其所有投资组合
    portfolios = relationship("Portfolio", back_populates="owner", cascade="all, delete-orphan")
