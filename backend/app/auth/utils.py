"""
认证工具模块

本模块提供用户认证相关的工具函数，包括密码哈希处理和 JWT 令牌操作。

核心功能
--------

- **密码处理**: 使用 bcrypt 算法进行密码哈希和验证
- **JWT 令牌**: 创建和验证 JSON Web Token

安全说明
--------

- 密码使用 bcrypt 算法哈希，具有自动加盐功能
- JWT 使用 HS256 算法签名
- 令牌包含过期时间，默认 30 分钟
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

# 获取应用配置
settings = get_settings()

# 密码哈希上下文
# 使用 bcrypt 算法，deprecated="auto" 会自动处理旧算法迁移
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码

    比较明文密码与哈希密码是否匹配。

    Args:
        plain_password: 用户输入的明文密码
        hashed_password: 数据库中存储的哈希密码

    Returns:
        bool: 密码匹配返回 True，否则返回 False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希

    使用 bcrypt 算法对密码进行哈希处理。

    Args:
        password: 明文密码

    Returns:
        str: bcrypt 哈希后的密码字符串
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT 访问令牌

    生成包含用户信息和过期时间的 JWT 令牌。

    Args:
        data: 要编码到令牌中的数据（通常包含 "sub": user_id）
        expires_delta: 自定义过期时间间隔，默认使用配置中的值

    Returns:
        str: 编码后的 JWT 令牌字符串

    Example:
        >>> token = create_access_token({"sub": "123"})
        >>> # 返回类似 "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." 的字符串
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # 添加过期时间到载荷
    to_encode.update({"exp": expire})
    
    # 使用密钥和算法编码 JWT
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """验证 JWT 令牌

    解码并验证 JWT 令牌的有效性，包括签名和过期时间。

    Args:
        token: JWT 令牌字符串

    Returns:
        dict: 解码后的令牌载荷，如果验证失败返回 None

    Note:
        验证失败的情况包括：签名无效、令牌过期、格式错误等。
    """
    try:
        # 解码并验证令牌
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        # JWT 相关错误（签名无效、过期等）
        return None
    except Exception:
        # 其他意外错误
        return None
