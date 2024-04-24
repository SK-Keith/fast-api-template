#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：fast-api-template
@File    ：main.py
@Author  ：Keith007
@Date    ：2023/11/13 17:44 
"""

import uvicorn
from fastapi import FastAPI

from app import bootstrap
from app.config import globalAppSettings
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware


if __name__ == "__main__":
    print("打印项目配置:", globalAppSettings)
    # 实例化
    server = FastAPI(redoc_url=None, docs_url="/apidoc", title=globalAppSettings.app_name)
    # 添加 CORS 中间件到 server 实例
    server.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许的客户端地址
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],  # 允许的 HTTP 方法
        allow_headers=["*"]
    )
    # 初始化项目
    bootstrap.Init(server)
    # 使用 python main.py 启动服务
    # uvicorn.run(app='main:app', host="0.0.0.0", port=36100, reload=True)
    uvicorn.run(server, host=globalAppSettings.app_host, port=globalAppSettings.app_port)


