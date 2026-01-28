"""
应用配置模块

本模块使用 Pydantic Settings 管理应用配置，支持从环境变量
和 .env 文件加载配置项。

配置项说明
----------

- **SECRET_KEY**: JWT 签名密钥，必须设置且保密
- **ALGORITHM**: JWT 加密算法，默认 HS256
- **ACCESS_TOKEN_EXPIRE_MINUTES**: 令牌过期时间（分钟）
- **DATABASE_URL**: 数据库连接字符串

使用方式
--------

::

    from app.config import get_settings
    
    settings = get_settings()
    print(settings.SECRET_KEY)

注意事项
--------

- 生产环境必须修改默认的 SECRET_KEY
- 配置使用 lru_cache 缓存，避免重复加载
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类

    从环境变量或 .env 文件加载配置项，使用 Pydantic 进行验证。

    Attributes:
        SECRET_KEY: JWT 签名密钥
        ALGORITHM: JWT 加密算法
        ACCESS_TOKEN_EXPIRE_MINUTES: 访问令牌过期时间（分钟）
        DATABASE_URL: 数据库连接 URL
    """
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str

    class Config:
        """Pydantic 配置"""
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """获取应用配置实例

    使用 lru_cache 装饰器缓存配置实例，确保整个应用
    使用同一个配置对象，避免重复读取环境变量。

    Returns:
        Settings: 配置实例

    Example:
        >>> settings = get_settings()
        >>> print(settings.DATABASE_URL)
    """
    return Settings()
