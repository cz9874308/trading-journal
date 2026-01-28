"""
API 路由模块

本模块包含所有 FastAPI 路由端点的定义，按功能模块组织。

路由结构
--------

- **/api/auth**: 用户认证（登录、注册）
- **/api/users**: 用户管理（仅管理员）
- **/api/portfolios**: 投资组合管理
- **/api/trades**: 交易记录管理
- **/api/analytics**: 数据分析与统计

路由注册
--------

所有路由在 `main.py` 中通过 `include_router()` 方法注册::

    app.include_router(auth.router, prefix="/api")
    app.include_router(portfolios.router, prefix="/api")

认证要求
--------

除了登录和注册接口外，所有接口都需要有效的 JWT 令牌。
用户管理接口额外需要管理员权限。
"""
