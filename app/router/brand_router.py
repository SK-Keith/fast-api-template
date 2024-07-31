#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：fast-api-template
@File    ：default_router.py
@Author  ：Keith007
@Date    ：2023/11/13 18:45 
"""
from fastapi import APIRouter, Depends
from app.types import request
import requests
import uvicorn
import json
import time
import os

router = APIRouter(prefix="/router", tags=["远程"])

# 路由装饰器，处理 POST 请求
@router.post("/save")
async def post_data(item: request.Item):  # 使用 Pydantic 模型自动解析请求体
    # 打印接收到的数据
    print('Received POST data:', item.data)

    # 保存数据到本地文件
    # 使用当前时间戳创建文件名
    timestamp = int(time.time())
    file_name = f"res-{timestamp}.json"
    with open(file_name, 'w', encoding='utf-8') as f:
        # 因为 data 是字符串，我们可能需要先将其转换为字典，如果是JSON字符串的话
        try:
            data_dict = json.loads(item.data)
        except json.JSONDecodeError:
            data_dict = {"data": item.data}  # 如果不是有效的 JSON 字符串，则直接保存

        json.dump(data_dict, f)

    # 返回成功响应
    return {"code": 200, "message": "Received data successfully"}


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


@router.get("/xxgk")
async def xxgk():
    for i in range(10, 101):
        url = "https://www.szgm.gov.cn/xxgk/xqgwhxxgkml/gzgg/index_" + str(i) + ".html"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Cookie": "Path=/; bm_uuid=42022042; ft_szgov=0; arialoadData=false; laravel_session=eyJpdiI6IktcL09iQW1Fa3JQMWsyUDdFS0diRU1nPT0iLCJ2YWx1ZSI6InVRQW0xU2gxYTBRSitVUWh0UG93cWVxYlNkNEhWdk4yV0Y1M0FiOEs1VE9ZWHpuSEMxSHNMV1h5Q3IzOTQwNVAiLCJtYWMiOiJlMjkyZWU3ZjNhMjEwNThhZTQ5MzM1ZGQ1Y2JiYWVlYTUyNWZjN2EzNWNjNmJmNzYxNTdiMDEwOTA3ZjNhYWI1In0%3D; front_uc_session=eyJpdiI6IkRUaHJWNjEydHM4VmdFZFFxUmFuWUE9PSIsInZhbHVlIjoiMFlSc3dIeUM2NHJoWWZ6RkJHXC9FZldSZ0NqZDBwM0ZLMGJZeld4RkNxelBaWno4UWNKOFNoaTlIUVRwTlFrMU4iLCJtYWMiOiJkMjI1N2ExNzQzYzczZDBmMGY0ODNiYzdlNGNhMmJmYzgwNDIyNTJiNGZiMmNlZGJkMDhiY2YxMjI2YmUwZTdjIn0%3D",
            "Pragma": "no-cache",
            "Referer": "https://www.szgm.gov.cn/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        print(response)