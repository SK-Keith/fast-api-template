#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：fast-api-template
@File    ：default_router.py
@Author  ：Keith007
@Date    ：2023/11/13 18:45 
"""
from datetime import datetime

from fastapi import APIRouter

router = APIRouter(tags=["默认路由"])


@router.get("/")
async def index():
    """
    默认访问链接
    """
    return {
        "code": 200,
        "msg": "Hello World!",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
