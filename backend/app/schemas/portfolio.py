"""
投资组合数据验证模式

本模块定义了投资组合相关 API 的请求和响应数据验证模式。

模式类说明
----------

- **PortfolioBase**: 投资组合基础模式
- **PortfolioCreate**: 创建投资组合请求模式
- **PortfolioUpdate**: 更新投资组合请求模式
- **Portfolio**: API 响应模式
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PortfolioBase(BaseModel):
    """投资组合基础模式

    定义投资组合的通用字段。

    Attributes:
        name: 组合名称
        description: 组合描述（可选）
        initial_balance: 初始资金（INR），默认为 0
    """
    name: str
    description: Optional[str] = None
    initial_balance: float = 0.0


class PortfolioCreate(PortfolioBase):
    """创建投资组合请求模式

    用于创建投资组合接口的输入验证，继承基础模式的所有字段。
    """
    pass


class PortfolioUpdate(BaseModel):
    """更新投资组合请求模式

    用于更新投资组合，所有字段都是可选的。

    Attributes:
        name: 新的组合名称
        description: 新的组合描述
        initial_balance: 新的初始资金
    """
    name: Optional[str] = None
    description: Optional[str] = None
    initial_balance: Optional[float] = None


class Portfolio(PortfolioBase):
    """投资组合 API 响应模式

    用于 API 响应的投资组合数据模式。

    Attributes:
        id: 组合 ID
        user_id: 所属用户 ID
        created_at: 创建时间
        updated_at: 最后更新时间
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic 配置"""
        from_attributes = True  # 允许从 ORM 模型创建
