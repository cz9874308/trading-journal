"""
数据模型模块

本模块定义了所有 SQLAlchemy ORM 数据模型，用于映射数据库表结构。

数据模型
--------

- **User**: 用户模型，存储用户账户信息
- **Portfolio**: 投资组合模型，存储用户的投资组合
- **Trade**: 交易记录模型，存储具体的交易信息

枚举类型
--------

- **TradeType**: 交易类型（做多/做空）
- **TradeStatus**: 交易状态（持仓中/已平仓）

关系说明
--------

- User -> Portfolio: 一对多（一个用户可以有多个投资组合）
- Portfolio -> Trade: 一对多（一个投资组合可以有多笔交易）
"""

from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.trade import Trade, TradeType, TradeStatus

__all__ = ["User", "Portfolio", "Trade", "TradeType", "TradeStatus"]
