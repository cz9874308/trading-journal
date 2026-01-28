"""
数据库连接与会话管理模块

本模块配置 SQLAlchemy 异步数据库引擎，提供数据库会话管理
和表初始化功能。

核心组件
--------

- **engine**: 异步数据库引擎
- **AsyncSessionLocal**: 异步会话工厂
- **Base**: ORM 模型基类

使用方式
--------

在 FastAPI 依赖注入中使用 `get_db` 获取数据库会话::

    @router.get("/users")
    async def get_users(db: AsyncSession = Depends(get_db)):
        ...

技术细节
--------

- 使用 aiosqlite 驱动实现 SQLite 异步访问
- 会话配置 `expire_on_commit=False` 避免访问已提交对象时的额外查询
- 数据库表在应用启动时自动创建（如不存在）
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import get_settings

# 获取应用配置
settings = get_settings()

# 创建异步数据库引擎
# - echo=True: 开发模式下打印 SQL 语句
# - future=True: 使用 SQLAlchemy 2.0 风格
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

# 创建异步会话工厂
# - expire_on_commit=False: 提交后不自动过期对象，避免延迟加载问题
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ORM 模型基类
# 所有数据模型都应继承此基类
Base = declarative_base()


async def get_db():
    """获取数据库会话（依赖注入）

    作为 FastAPI 依赖项使用，自动管理会话的创建和关闭。

    Yields:
        AsyncSession: 异步数据库会话

    Example:
        >>> @router.get("/items")
        >>> async def get_items(db: AsyncSession = Depends(get_db)):
        >>>     result = await db.execute(select(Item))
        >>>     return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库

    创建所有已定义的数据库表（如果不存在）。
    此函数在应用启动时调用。

    注意事项
    --------

    - 仅创建不存在的表，不会修改已有表结构
    - 生产环境建议使用 Alembic 进行数据库迁移
    """
    async with engine.begin() as conn:
        # 同步执行表创建操作
        await conn.run_sync(Base.metadata.create_all)
