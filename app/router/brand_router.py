#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：fast-api-template
@File    ：default_router.py
@Author  ：Keith007
@Date    ：2023/11/13 18:45 
"""
from fastapi import APIRouter, Depends
import requests

router = APIRouter(prefix="/router", tags=["远程"])


@router.get("/brand")
async def brand():
    # 构造POST请求的数据载荷
    payload = {
        "pageNum": 1,
        "pageSize": 10,
        "countryCodeList": [
            "CN"
        ],
        "nodeCode": "100"
    }

    # 发起POST请求
    url = "https://dev-admin.wincomply.cn/admin-api/compliance/sys/brand/page"
    headers = {
        "Content-Type": "application/json",  # 请求内容类型为JSON
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpblR5cGUiOiJsb2dpbiIsImxvZ2luSWQiOjE2LCJyblN0ciI6IjB6T2RrVkh2TkZOa241ZFQ3b3Qxek9hM0Y4YnVwWXBRIiwibG9naW5fdXNlciI6eyJ1c2VySWQiOjE2LCJ1c2VybmFtZSI6InlteCIsIm5pY2tOYW1lIjoi5aea5qOJ6LSkIiwibG9naW5UaW1lIjoxNzIxMTkzOTk1NzMzLCJpcGFkZHIiOiI1OC4yNTEuMTQ3LjE5NCIsImlzQWxsRGF0YVNjb3BlIjp0cnVlfX0.fzUW4JdMWC67W6qIguTm3y0I1xUmH3DZYUX7S-lQPkc"  # 添加Bearer Token，替换为您的实际Token
    }

    response = requests.post(url, json=payload, headers=headers)

    # 解析响应内容
    response_data = response.json()

    # 检查响应是否成功
    if response_data["code"] == 200:
        # 获取data中的rows数据
        rows = response_data["data"]["page"]["rows"]

        # 遍历rows，找出符合条件的productName并汇总到列表中
        product_names = []
        for row in rows:
            if row.get("productName") == "中国商标注册":
                product_names.append(row["serviceNo"])

        # 打印汇总的productName列表
        print(product_names)
    else:
        print("请求失败:", response_data["msg"])
