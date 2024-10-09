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
import mysql.connector
from datetime import datetime

router = APIRouter(prefix="/router", tags=["远程"])

# 路由装饰器，处理 POST 请求
@router.post("/save")
async def post_data(item: request.Item):  # 使用 Pydantic 模型自动解析请求体
    # 打印接收到的数据
    # print('Received POST data:', item.data)

    # 保存数据到本地文件
    # 使用当前时间戳创建文件名
    timestamp = int(time.time())
    file_name = f"res-{timestamp}.json"
    with open(file_name, 'w', encoding='utf-8') as f:
        # 因为 data 是字符串，我们可能需要先将其转换为字典，如果是JSON字符串的话
        try:
            data_dict = json.loads(item.data)
            param_dict = json.loads(item.param)
            regServiceNo = param_dict['regServiceNo']
            print("regServiceNo", regServiceNo)
        except json.JSONDecodeError:
            data_dict = {"data": item.data}  # 如果不是有效的 JSON 字符串，则直接保存
        try:
            extracted_list = extract_data(data_dict)
            insert_into_database(extracted_list)
            # print(extracted_list)
        except Exception as e:  # 捕获所有异常的基类
            print(f'extract_data or insert_into_database fail，An error occurred: {e}')  # 打印异常信息
            pass
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


# 辅助函数，检查None值并将其转换为字符串形式
def to_str(value):
    return f'{value}' if value is not None else 'null'

def to_default_if_empty(value, default=0):
    return value if value is not None and value != '' else default

def to_left5(value):
    try:
        if value is not None:
            # Convert value to float, if possible
            numeric_value = float(value)
            return numeric_value / 100000
        else:
            # Handle the case where value is None
            return None
    except ValueError:
        # Handle the case where value cannot be converted to float
        raise ValueError(f"Invalid input: {value}. Must be a number or convertible to float.")

def extract_data(data_dict):

    # with open(file_name, 'r', encoding='utf-8-sig') as file:
    #     json_data = file.read()
    # 解析JSON数据
    # data = json.loads(json_data)

    # 用于存储提取数据的列表
    extracted_list = []

    # 遍历数据中的每条记录
    for record in data_dict.get('data', []):
        extracted_data = {
            'id': to_str(record['id']),
            'campaignName': to_str(record['campaign']['name']),
            'keyword': to_str(record['keyword']),
            'state': to_str(record['state']),
            'dailyBudget': to_default_if_empty(record['campaign']['dailyBudget']),
            'matchType': to_str(record['matchType']),
            'SPEND': to_default_if_empty(to_left5(record['performance']['SPEND'])),
            'CPC': to_default_if_empty(to_left5(record['performance']['CPC'])),
            'ROAS': to_default_if_empty(record['performance']['ROAS']),
            'SALES': to_default_if_empty(to_left5(record['performance']['SALES'])),
            'CLICKS': to_default_if_empty(record['performance']['CLICKS'])
        }
        extracted_list.append(extracted_data)

    return extracted_list

def insert_into_database(extracted_data):
    # 连接数据库
    db_connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='mydb'
    )
    cursor = db_connection.cursor()

    # 构建插入SQL语句
    insert_query = '''
    INSERT INTO gg_daily (campaign_name, keyword, state, daily_budget, match_type,spend, CPC, ROAS, sales, clicks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''

    # 准备要插入的数据
    current_date = datetime.now().date()  # 获取当前日期
    for data in extracted_data:
        values = (
            data['campaignName'],
            data['keyword'],
            data['state'],
            data['dailyBudget'],
            data['matchType'],
            data['SPEND'],
            data['CPC'],
            data['ROAS'],
            data['SALES'],
            data['CLICKS']
        )

        # 执行插入操作
        try:
            cursor.execute(insert_query, values)
            db_connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            db_connection.rollback()

    # 关闭游标和数据库连接
    cursor.close()
    db_connection.close()