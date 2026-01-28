"""
CSRF 保护中间件模块

本模块实现了 CSRF（跨站请求伪造）保护机制，使用 Double Submit Cookie
模式防止 CSRF 攻击。

工作原理
--------

Double Submit Cookie 模式的核心思想：

1. 服务器在响应中设置一个 CSRF 令牌到 Cookie
2. 客户端在后续请求中，同时在请求头和 Cookie 中发送该令牌
3. 服务器验证两个令牌是否匹配

攻击者无法读取用户浏览器中的 Cookie 值，因此无法在请求头中
发送正确的令牌，从而防止了 CSRF 攻击。

配置说明
--------

通过环境变量配置：

- **SECRET_KEY**: 令牌签名密钥
- **CSRF_TOKEN_EXPIRE_SECONDS**: 令牌过期时间（秒），默认 3600
- **CSRF_COOKIE_SECURE**: 是否仅 HTTPS 传输，默认 true
- **CSRF_COOKIE_SAMESITE**: SameSite 策略，默认 lax

豁免路径
--------

以下路径不需要 CSRF 验证：

- /api/auth/login - 登录接口
- /api/auth/register - 注册接口
- /docs - API 文档
- /health - 健康检查
- / - 根路径
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from itsdangerous import URLSafeTimedSerializer, BadSignature
import os
from typing import Optional

# ========== CSRF 配置 ==========
# 从环境变量加载配置

# CSRF 令牌签名密钥（使用与 JWT 相同的密钥）
CSRF_SECRET = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")

# 令牌过期时间（秒）
CSRF_TOKEN_EXPIRE_SECONDS = int(os.getenv("CSRF_TOKEN_EXPIRE_SECONDS", "3600"))

# Cookie 安全设置
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "true").lower() == "true"
CSRF_COOKIE_SAMESITE = os.getenv("CSRF_COOKIE_SAMESITE", "lax")

# 令牌名称配置
CSRF_TOKEN_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_COOKIE_NAME = "csrf_token"

# 需要 CSRF 保护的 HTTP 方法（状态变更操作）
CSRF_PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# 豁免 CSRF 验证的路径
CSRF_EXEMPT_PATHS = {
    "/api/auth/login",     # 登录接口（尚未获取令牌）
    "/api/auth/register",  # 注册接口（尚未获取令牌）
    "/docs",               # Swagger 文档
    "/openapi.json",       # OpenAPI 规范
    "/health",             # 健康检查
    "/"                    # 根路径
}

# 创建令牌序列化器
serializer = URLSafeTimedSerializer(CSRF_SECRET)


def generate_csrf_token() -> str:
    """生成新的 CSRF 令牌

    使用 secrets 模块生成安全的随机字符串，然后使用
    itsdangerous 进行签名，确保令牌不可伪造。

    Returns:
        str: 签名后的 CSRF 令牌
    """
    import secrets
    # 生成 32 字节的安全随机字符串
    token_data = secrets.token_urlsafe(32)
    # 使用密钥签名
    return serializer.dumps(token_data)


def validate_csrf_token(token: str) -> bool:
    """验证 CSRF 令牌

    检查令牌的签名有效性和是否过期。

    Args:
        token: 要验证的 CSRF 令牌

    Returns:
        bool: 令牌有效返回 True，否则返回 False
    """
    try:
        # 验证签名并检查过期时间
        serializer.loads(token, max_age=CSRF_TOKEN_EXPIRE_SECONDS)
        return True
    except (BadSignature, Exception):
        # 签名无效或令牌过期
        return False


class CSRFProtectMiddleware(BaseHTTPMiddleware):
    """CSRF 保护中间件

    实现 Double Submit Cookie 模式：

    1. 在成功响应中设置 CSRF 令牌到 Cookie
    2. 对于状态变更请求，验证请求头中的令牌与 Cookie 中的令牌是否匹配
    3. 验证令牌签名和过期时间

    使用示例
    --------

    在 FastAPI 应用中添加中间件::

        app.add_middleware(CSRFProtectMiddleware)

    客户端需要：
    1. 从响应头 X-CSRF-Token 获取令牌
    2. 在后续 POST/PUT/PATCH/DELETE 请求中，将令牌放入 X-CSRF-Token 请求头
    """

    async def dispatch(self, request: Request, call_next):
        """处理请求

        中间件的核心处理逻辑。

        Args:
            request: 请求对象
            call_next: 下一个处理函数

        Returns:
            Response: 响应对象
        """
        # 检查路径是否豁免 CSRF 验证
        if self._is_exempt_path(request.url.path):
            response = await call_next(request)
            
            # 登录/注册成功后设置 CSRF 令牌
            # 让客户端获取令牌用于后续请求
            if request.method == "POST" and request.url.path in ["/api/auth/login", "/api/auth/register"]:
                csrf_token = generate_csrf_token()
                response.set_cookie(
                    key=CSRF_COOKIE_NAME,
                    value=csrf_token,
                    httponly=True,                    # 禁止 JavaScript 访问
                    secure=CSRF_COOKIE_SECURE,        # 仅 HTTPS 传输
                    samesite=CSRF_COOKIE_SAMESITE,    # SameSite 策略
                    max_age=CSRF_TOKEN_EXPIRE_SECONDS # 过期时间
                )
                # 同时在响应头中返回令牌，方便客户端读取
                response.headers[CSRF_HEADER_NAME] = csrf_token
            return response

        # 对于需要 CSRF 保护的方法，进行令牌验证
        if request.method in CSRF_PROTECTED_METHODS:
            # 从请求头获取 CSRF 令牌
            csrf_header_token = request.headers.get(CSRF_HEADER_NAME)

            # 从 Cookie 获取 CSRF 令牌
            csrf_cookie_token = request.cookies.get(CSRF_COOKIE_NAME)

            # 验证：两个令牌都必须存在
            if not csrf_header_token or not csrf_cookie_token:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF token missing"
                )

            # 验证：两个令牌必须匹配（Double Submit 核心逻辑）
            if csrf_header_token != csrf_cookie_token:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF token mismatch"
                )

            # 验证：令牌签名有效且未过期
            if not validate_csrf_token(csrf_header_token):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF token invalid or expired"
                )

        # 处理请求
        response = await call_next(request)

        # 成功响应后刷新 CSRF 令牌
        # 每次请求后更新令牌，提高安全性
        if response.status_code < 400:
            csrf_token = generate_csrf_token()
            response.set_cookie(
                key=CSRF_COOKIE_NAME,
                value=csrf_token,
                httponly=True,
                secure=CSRF_COOKIE_SECURE,
                samesite=CSRF_COOKIE_SAMESITE,
                max_age=CSRF_TOKEN_EXPIRE_SECONDS
            )
            # 在响应头中返回新令牌
            response.headers[CSRF_HEADER_NAME] = csrf_token

        return response

    def _is_exempt_path(self, path: str) -> bool:
        """检查路径是否豁免 CSRF 验证

        Args:
            path: 请求路径

        Returns:
            bool: 如果路径豁免验证返回 True
        """
        # 精确匹配
        if path in CSRF_EXEMPT_PATHS:
            return True

        # 前缀匹配（文档和静态资源）
        exempt_prefixes = ("/docs", "/redoc", "/openapi", "/static")
        if any(path.startswith(prefix) for prefix in exempt_prefixes):
            return True

        # GET 请求不需要 CSRF 保护（不会改变状态）
        return False
