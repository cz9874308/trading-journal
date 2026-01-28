"""
Pydantic 数据模式模块

本模块定义了 API 请求和响应的数据验证模式，使用 Pydantic 
实现自动数据验证和序列化。

核心组件
--------

- **user**: 用户相关数据模式
- **portfolio**: 投资组合数据模式
- **trade**: 交易记录数据模式

模式类型
--------

- **Base**: 基础模式，定义通用字段
- **Create**: 创建操作的输入模式
- **Update**: 更新操作的输入模式（字段可选）
- **Response**: API 响应模式，包含完整字段

使用示例
--------

::

    from app.schemas.user import UserCreate, User
    
    # 验证输入数据
    user_data = UserCreate(email="test@example.com", ...)
    
    # 序列化响应
    return User.model_validate(db_user)
"""
