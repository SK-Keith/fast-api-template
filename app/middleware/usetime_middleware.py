#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：fast-api-template
@File    ：usetime_middleware.py
@Author  ：Keith007
@Date    ：2023/12/12 7:25 PM
"""
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.utils.log import logger


class UseTimeMiddleware(BaseHTTPMiddleware):
    """ 计算耗时中间件"""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host
        logger.info(f"Client IP: {client_ip}")
        """ 请求耗时 """
        start_time = time.time()
        print("调用-中间件-UseTimeMiddleware---before")
        # 调用下一个中间件或路由处理函数
        result = await call_next(request)
        process_time = time.time() - start_time
        result.headers["X-Process-Time"] = str(process_time)
        print("调用-中间件-UseTimeMiddleware---after")
        return result
