"""
用户认证路由模块

本模块提供用户认证相关的 API 端点，包括注册、登录和获取当前用户信息。

API 端点
--------

- POST /api/auth/register - 用户注册
- POST /api/auth/login - 用户登录
- GET /api/auth/me - 获取当前用户信息

认证说明
--------

- 登录和注册接口无需认证
- /me 接口需要有效的 JWT 令牌
- 首个注册的用户自动成为管理员
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate, User, Token
from app.crud import user as user_crud
from app.auth.utils import verify_password, create_access_token
from app.auth.dependencies import get_current_active_user
from app.config import get_settings

# 获取应用配置
settings = get_settings()

# 创建路由器
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册

    创建新用户账户。首个注册的用户将自动成为管理员。

    注册流程
    --------

    1. 检查是否为首个用户（用于确定管理员权限）
    2. 验证邮箱是否已被注册
    3. 验证用户名是否已被使用
    4. 创建用户账户

    Args:
        user: 用户注册信息
        db: 数据库会话

    Returns:
        User: 创建的用户信息（不含密码）

    Raises:
        HTTPException: 400 - 邮箱已注册或用户名已被使用
    """
    # 检查是否为首个用户（首个用户将成为管理员）
    user_count = await user_crud.get_user_count(db)
    is_first_user = user_count == 0

    # 检查邮箱是否已存在
    db_user = await user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 检查用户名是否已存在
    db_user = await user_crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # 创建用户（首个用户自动成为管理员）
    return await user_crud.create_user(db, user=user, is_admin=is_first_user)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """用户登录

    验证用户凭据并返回 JWT 访问令牌。

    登录流程
    --------

    1. 尝试通过用户名查找用户
    2. 如果未找到，尝试通过邮箱查找用户
    3. 验证密码
    4. 检查账户是否激活
    5. 生成并返回 JWT 令牌

    Args:
        form_data: OAuth2 登录表单（username 和 password）
        db: 数据库会话

    Returns:
        Token: 包含 access_token 和 token_type 的对象

    Raises:
        HTTPException: 401 - 用户名或密码错误
        HTTPException: 400 - 用户账户未激活

    Note:
        username 字段可以填写用户名或邮箱。
    """
    # 尝试通过用户名或邮箱查找用户
    user = await user_crud.get_user_by_username(db, username=form_data.username)
    if not user:
        user = await user_crud.get_user_by_email(db, email=form_data.username)

    # 验证密码
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查账户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息

    返回当前登录用户的详细信息。

    Args:
        current_user: 当前登录用户（通过依赖注入获取）

    Returns:
        User: 当前用户的详细信息

    Note:
        此接口需要有效的 JWT 令牌。
    """
    return current_user
