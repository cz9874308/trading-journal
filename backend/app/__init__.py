"""
交易日记应用核心模块

本模块是 Vibe Journal 交易日记系统的核心应用包，提供完整的交易记录、
投资组合管理和数据分析功能。

核心子模块
----------

- **auth**: 用户认证与授权，包括 JWT 令牌管理
- **crud**: 数据库 CRUD 操作封装
- **middleware**: 中间件，包括 CSRF 保护
- **models**: SQLAlchemy 数据模型定义
- **routers**: FastAPI 路由端点
- **schemas**: Pydantic 数据验证模式

使用方式
--------

通过 FastAPI 应用入口 `main.py` 启动服务::

    uvicorn app.main:app --reload

依赖关系
--------

本模块依赖 FastAPI、SQLAlchemy、Pydantic 等核心库，
详见 requirements.txt 文件。
"""
