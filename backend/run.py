"""
应用启动脚本

本脚本用于在开发环境中启动 FastAPI 应用服务器。

使用方式
--------

直接运行此脚本启动开发服务器::

    python run.py

服务将在 http://0.0.0.0:8000 启动，支持热重载。

生产部署
--------

生产环境建议使用 Docker 或直接运行::

    uvicorn app.main:app --host 0.0.0.0 --port 8000

注意事项
--------

- 开发模式启用了 `reload=True`，文件变更会自动重启
- 生产环境应禁用热重载以提高性能
"""

import uvicorn

if __name__ == "__main__":
    # 启动 Uvicorn ASGI 服务器
    # - app.main:app: 指向 FastAPI 应用实例
    # - host: 监听所有网络接口
    # - port: 服务端口
    # - reload: 开发模式下启用热重载
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
