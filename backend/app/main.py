"""
FastAPI 应用入口模块

本模块是 Vibe Journal 交易日记系统的主入口，负责初始化 FastAPI 应用、
配置中间件、注册路由以及定义应用生命周期事件。

核心功能
--------

- 应用生命周期管理（启动时初始化数据库）
- CORS 跨域资源共享配置
- CSRF 跨站请求伪造保护
- API 路由注册

API 文档
--------

启动服务后，可通过以下地址访问 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

环境配置
--------

应用依赖以下环境变量（通过 .env 文件配置）：

- SECRET_KEY: JWT 签名密钥
- DATABASE_URL: 数据库连接字符串
- ACCESS_TOKEN_EXPIRE_MINUTES: 令牌过期时间
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.routers import auth, users, portfolios, trades, analytics
from app.middleware.csrf import CSRFProtectMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理器

    管理 FastAPI 应用的启动和关闭事件。

    启动时执行
    ----------
    - 初始化数据库连接
    - 创建数据库表（如果不存在）

    关闭时执行
    ----------
    - 清理资源（预留扩展）

    Args:
        app: FastAPI 应用实例

    Yields:
        None: 应用运行期间保持上下文
    """
    # 启动：初始化数据库
    await init_db()
    yield
    # 关闭：清理资源（如需要）


# 创建 FastAPI 应用实例
app = FastAPI(
    title="Trade Journal API",
    description="API for managing trading portfolios and journals",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 中间件配置
# 允许前端应用跨域访问 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # 本地开发环境
        "http://127.0.0.1:3000",      # 本地开发环境（备用）
        "https://vibe.marketcalls.in", # 生产环境
        "http://vibe.marketcalls.in"   # 生产环境（HTTP）
    ],
    allow_credentials=True,  # 允许携带凭据（Cookie）
    allow_methods=["*"],     # 允许所有 HTTP 方法
    allow_headers=["*"],     # 允许所有请求头
    expose_headers=["X-CSRF-Token"],  # 暴露 CSRF 令牌头部
)

# CSRF 保护中间件
# 防止跨站请求伪造攻击
app.add_middleware(CSRFProtectMiddleware)

# 注册 API 路由
# 所有路由统一使用 /api 前缀
app.include_router(auth.router, prefix="/api")       # 认证路由
app.include_router(users.router, prefix="/api")      # 用户管理路由
app.include_router(portfolios.router, prefix="/api") # 投资组合路由
app.include_router(trades.router, prefix="/api")     # 交易记录路由
app.include_router(analytics.router, prefix="/api")  # 数据分析路由


@app.get("/")
async def root():
    """API 根端点

    返回 API 基本信息，用于验证服务是否正常运行。

    Returns:
        dict: 包含 API 名称、版本和文档地址的字典
    """
    return {
        "message": "Trade Journal API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查端点

    用于负载均衡器或监控系统检查服务健康状态。

    Returns:
        dict: 包含健康状态的字典
    """
    return {"status": "healthy"}
