"""
数据库 CRUD 操作模块

本模块封装了所有数据库的创建(Create)、读取(Read)、更新(Update)、
删除(Delete)操作，提供统一的数据访问接口。

核心组件
--------

- **user**: 用户数据操作
- **portfolio**: 投资组合数据操作
- **trade**: 交易记录数据操作

设计原则
--------

- 所有操作均为异步函数，支持高并发
- 使用 SQLAlchemy 异步会话进行数据库操作
- 返回值为 ORM 模型实例或 None
- 统一的错误处理和事务管理

使用示例
--------

::

    from app.crud import user as user_crud
    
    # 获取用户
    user = await user_crud.get_user_by_id(db, user_id=1)
    
    # 创建用户
    new_user = await user_crud.create_user(db, user=user_data)
"""
