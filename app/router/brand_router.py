#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：fast-api-template
@File    ：default_router.py
@Author  ：Keith007
@Date    ：2023/11/13 18:45 
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.types import request
import requests
import uvicorn
import json
import time
import os
import mysql.connector
from mysql.connector import pooling
from datetime import datetime, date
import logging
from typing import List, Tuple

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# 创建数据库连接池
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "mydb",
    "pool_name": "mypool",
    "pool_size": 5
}

connection_pool = pooling.MySQLConnectionPool(**db_config)

# 辅助函数，用于获取数据库连接
def get_db_connection():
    return connection_pool.get_connection()


@router.post("/inv/save")
async def save_inventory(item: request.Item):
    try:
        # 解析 JSON 数据
        data_dict = json.loads(item.data)
        
        # 打印整个对象
        logger.info(f"接收到的数据: {json.dumps(data_dict, ensure_ascii=False, indent=2)}")
        
        # 检查数据结构
        if 'data' not in data_dict:
            logger.error("数据格式不匹配：缺少 'data' 属性")
            return {"code": 400, "message": "数据格式不匹配：缺少 'data' 属性"}
        
        if 'listings' not in data_dict['data']:
            logger.error("数据格式不匹配：缺少 'listings' 属性")
            return {"code": 400, "message": "数据格式不匹配：缺少 'listings' 属性"}
        
        if 'listings' not in data_dict['data']['listings']:
            logger.error("数据格式不匹配：缺少 'listings' 数组")
            return {"code": 400, "message": "数据格式不匹配：缺少 'listings' 数组"}
        
        # 从连接池获取连接
        db_connection = get_db_connection()
        cursor = db_connection.cursor()

        # 准备更新旧记录的语句
        update_old_query = '''
        UPDATE inv_stock SET is_deleted = 1
        WHERE sku = %s AND is_deleted = 0
        '''

        # 准备插入新记录的语句
        insert_query = '''
        INSERT INTO inv_stock (
            sku, fnsku, asin, quantity, available, unfulfillable, 
            inbound, reserved, state, price
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''

        # 添加这个辅助函数在文件的适当位置
        def safe_int(value):
            try:
                return int(value) if value is not None else 0
            except ValueError:
                logger.warning(f"无法转换为整数: {value}")
                return 0

        # 遍历 listings 数组
        for listing in data_dict['data']['listings']['listings']:
            sku = listing['id']['sku']
            fnsku = listing['id']['fnSku']
            asin = listing['id']['asin']
            available = safe_int(listing['inventory'].get('available'))
            unfulfillable = safe_int(listing['inventory'].get('unfulfillable'))
            inbound = safe_int(listing['inventory'].get('inbound'))
            reserved = safe_int(listing['inventory'].get('reserved'))
            state = listing['state']
            
            # 计算 quantity
            quantity = available + unfulfillable + inbound + reserved
            
             # 获取价格 (如果有的话)
            price = None
            try:
                if listing['offers'] and len(listing['offers']) > 0:
                    price = float(listing['offers'][0]['buyBoxPrice']['price']['amount'])
            except (KeyError, ValueError, TypeError, IndexError) as e:
                logger.warning(f"无法获取 SKU {sku} 的价格或价格格式不正确: {str(e)}")

            # 首先更新旧记录
            logger.info(f"执行更新旧记录的 SQL: {update_old_query}")
            logger.info(f"参数值: {(sku,)}")
            cursor.execute(update_old_query, (sku,))

            # 然后插入新记录
            values = (
                sku, fnsku, asin, quantity, available, unfulfillable,
                inbound, reserved, state, price
            )
            logger.info(f"执行插入新记录的 SQL: {insert_query}")
            logger.info(f"参数值: {values}")
            cursor.execute(insert_query, values)

        # 提交事务
        db_connection.commit()

        # 关闭游标和连接（返回到连接池）
        cursor.close()
        db_connection.close()

        return {"code": 200, "message": "库存数据保存成功"}

    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析错误: {e}")
        return {"code": 400, "message": f"无效的 JSON 数据: {str(e)}"}
    except KeyError as e:
        logger.error(f"数据结构错误: 缺少键 {e}")
        return {"code": 400, "message": f"数据结构错误: 缺少键 {e}"}
    except mysql.connector.Error as err:
        logger.error(f"数据库错误: {err}")
        logger.error(f"最后执行的 SQL: {cursor._last_executed}")
        return {"code": 500, "message": f"数据库错误: {str(err)}"}
    except Exception as e:
        logger.error(f"未预期的错误: {e}")
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'db_connection' in locals() and db_connection is not None:
            db_connection.close()
        return {"code": 500, "message": f"发生错误: {str(e)}"}

@router.post("/ad/save")
async def post_data(item: request.Item):
    try:
        # 解析 JSON 数据
        data_dict = json.loads(item.data)
        param_dict = json.loads(item.param)
        
        # 从 param 中提取 startDate 和 endDate
        start_date = datetime.strptime(param_dict.get('startDate'), '%Y-%m-%d').date()
        end_date = datetime.strptime(param_dict.get('endDate'), '%Y-%m-%d').date()
        
        # 从连接池获取连接
        db_connection = get_db_connection()
        cursor = db_connection.cursor()

        # 初始化计数器
        updated_count = 0
        inserted_count = 0

        # 准备插入语句
        insert_query = '''
        INSERT INTO ad_campaign_group (
            buyer_search_term, keyword, target_bid, clicks, spend, 
            orders, sales, ACOS, state, match_type, campaign_id, 
            ad_group_id, keyword_id, ad_name, data_info, ad_date,
            start_date, end_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''

        # 获取当前日期
        current_date = date.today()

        # 用于收集需要更新的记录
        records_to_update: List[Tuple[str, str, date, date]] = []
        records_to_insert: List[Tuple] = []

        # 遍历 adEntities 数组
        for ad_entity in data_dict.get('adEntities', []):
            settings = ad_entity.get('settings', {})
            targeting = ad_entity.get('targeting', {}).get('data', {})
            summary = ad_entity.get('intervalData', {}).get('SUMMARY', [{}])[0]

            # 确定 ad_name 的值
            ad_group_id = targeting.get('adGroupId')
            ad_name_mapping = {
                "A00051522ZWDV3F32YWOC": "7736 CZ 10.30 0729",
                "A04712132DBEEF7OR2KIV": "7735 GF CZ 0818",
                "A08564912UYIPP0TPQ4O2": "7642 B0CZJC1LGV A",
                "A00468352LR543XWBDMA4": "7636SS CZ 219",
                "A045628113PWNV4RBIYTS": "TR AA 240924",
                "A05783271YA96L8R77MLZ": "7735 AB 0822",
                "A0224609KQSDXLUN258X": "7642 AUTO JMKF 0610",
                "A0959437348PY6CGZSFET": "JJ CZ 0924"
            }
            ad_name = ad_name_mapping.get(ad_group_id)
            logger.info(f"ad_name: {ad_name}")

            # 收集需要更新的记录
            records_to_update.append((ad_name, ad_group_id, start_date, end_date))

            values = (
                settings.get('CUSTOMER_SEARCH_TERM'),
                settings.get('TARGETINGCLAUSE'),
                safe_float(targeting.get('bid')),
                int(summary.get('CLICKS') or 0),
                safe_float(summary.get('SPEND'), 100000),
                int(summary.get('ORDERS') or 0),
                safe_float(summary.get('SALES'), 100000),
                safe_float(summary.get('ACOS')),
                targeting.get('state'),
                targeting.get('matchType'),
                targeting.get('campaignId'),
                ad_group_id,
                targeting.get('keywordId'),
                ad_name,
                json.dumps(ad_entity),  # 将整个 ad_entity 作为 JSON 存储在 data_info 字段
                current_date,
                start_date,
                end_date
            )
            records_to_insert.append(values)

        # 批量标记重复数据为已删除
        if records_to_update:
            update_query = '''
            UPDATE ad_campaign_group
            SET is_deleted = 1
            WHERE (ad_name, ad_group_id, start_date, end_date) IN (%s) AND is_deleted = 0
            '''
            placeholders = ', '.join(['(%s, %s, %s, %s)'] * len(records_to_update))
            update_query = update_query % placeholders
            update_values = [item for sublist in records_to_update for item in sublist]
            
            try:
                cursor.execute(update_query, update_values)
                updated_count = cursor.rowcount
                logger.info(f"Marked {updated_count} record(s) as deleted")
                db_connection.commit()
            except mysql.connector.Error as err:
                logger.error(f"Error marking duplicate data as deleted: {err}")
                db_connection.rollback()
                raise

        # 批量插入新数据
        if records_to_insert:
            try:
                cursor.executemany(insert_query, records_to_insert)
                inserted_count = cursor.rowcount
                logger.info(f"Inserted {inserted_count} new record(s)")
                db_connection.commit()
            except mysql.connector.Error as err:
                logger.error(f"Error inserting data: {err}")
                db_connection.rollback()
                raise

        # 关闭游标和连接（返回到连接池）
        cursor.close()
        db_connection.close()

        return {"code": 200, "message": f"成功更新 {updated_count} 条记录，插入 {inserted_count} 条新记录"}

    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析错误: {e}")
        return {"code": 400, "message": f"无效的 JSON 数据: {str(e)}"}
    except mysql.connector.Error as err:
        logger.error(f"数据库错误: {err}")
        return {"code": 500, "message": f"数据库错误: {str(err)}"}
    except Exception as e:
        logger.error(f"未预期的错误: {e}")
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'db_connection' in locals() and db_connection is not None:
            db_connection.close()
        return {"code": 500, "message": f"发生错误: {str(e)}"}

# 定义响应模型
class AdCampaignGroup(BaseModel):
    id: int
    buyer_search_term: Optional[str]
    keyword: Optional[str]
    target_bid: Optional[float]
    clicks: Optional[int]
    spend: Optional[float]
    orders: Optional[int]
    sales: Optional[float]
    ACOS: Optional[float]
    state: Optional[str]
    match_type: Optional[str]
    campaign_id: Optional[str]
    ad_group_id: Optional[str]
    keyword_id: Optional[str]
    ad_name: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    created_time: datetime

class PageResponse(BaseModel):
    total: int
    items: List[AdCampaignGroup]

@router.get("/ad/page", response_model=PageResponse)
async def get_ad_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    ad_name: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    sort_field: str = Query("id", description="排序字段"),
    sort_order: str = Query("desc", description="排序顺序 (asc 或 desc)")
):
    try:
        db_connection = get_db_connection()
        cursor = db_connection.cursor(dictionary=True)

        where_clause = "WHERE is_deleted = 0"
        params = []

        if ad_name:
            where_clause += " AND ad_name LIKE %s"
            params.append(f"%{ad_name}%")

        if start_date and end_date:
            where_clause += " AND (start_date = %s AND end_date = %s)"
            params.extend([end_date, start_date])
        elif start_date:
            where_clause += " AND end_date >= %s"
            params.append(start_date)
        elif end_date:
            where_clause += " AND start_date <= %s"
            params.append(end_date)

        valid_sort_fields = ["id", "buyer_search_term", "keyword", "target_bid", "clicks", "spend", "orders", "sales", "ACOS", "state", "match_type", "ad_name", "start_date", "end_date"]
        if sort_field not in valid_sort_fields:
            raise HTTPException(status_code=400, detail=f"无效的排序字段: {sort_field}")
        if sort_order.lower() not in ["asc", "desc"]:
            raise HTTPException(status_code=400, detail=f"无效的排序顺序: {sort_order}")
        
        order_clause = f"ORDER BY {sort_field} {sort_order.upper()}"

        count_query = f"SELECT COUNT(*) as total FROM ad_campaign_group {where_clause}"
        logger.info(f"Count Query: {count_query}")
        logger.info(f"Count Query Params: {params}")
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']

        offset = (page - 1) * page_size
        query = f"""
        SELECT id, buyer_search_term, keyword, target_bid, clicks, spend, 
               orders, sales, ACOS, state, match_type, campaign_id, 
               ad_group_id, keyword_id, ad_name, start_date, end_date, created_time
        FROM ad_campaign_group
        {where_clause}
        {order_clause}
        LIMIT %s OFFSET %s
        """
        logger.info(f"Data Query: {query}")
        logger.info(f"Data Query Params: {params + [page_size, offset]}")
        cursor.execute(query, params + [page_size, offset])
        results = cursor.fetchall()

        # 关闭游标和连接（返回到连接池）
        cursor.close()
        db_connection.close()

        # 构造响应
        items = [AdCampaignGroup(**result) for result in results]
        return PageResponse(total=total, items=items)

    except mysql.connector.Error as err:
        logger.error(f"数据库错误: {err}")
        raise HTTPException(status_code=500, detail=f"数据库错误: {str(err)}")
    except Exception as e:
        logger.error(f"未预期的错误: {e}")
        raise HTTPException(status_code=500, detail=f"发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"发生错误: {str(e)}")

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
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJsb2dpblR5cGUiOiJsb2dpbiIsImxvZ2luSWQiOjE2LCJyblN0ciI6IjB6T2RrVkh2TkZOa241ZFQ3b3Qxek9hM0Y4YnVwWXBRIiwibG9naW5fdXNlciI6eyJ1c2VySWQiOjE2LCJ1c2VybmFtZSI6InlteSIsIm5pY2tOYW1lIjoi5aea5qOJ6LSkIiwibG9naW5UaW1lIjoxNzIxMTkzOTk1NzMzLCJpcGFkZHIiOiI1OC4yNTEuMTQ3LjE5NCIsImlzQWxsRGF0YVNjb3BlIjp0cnVlfX0.fzUW4JdMWC67W6qIguTm3y0I1xUmH3DZYUX7S-lQPkc"  # 添加Bearer Token，替换为您的实际Token
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

def safe_float(value, divisor=1, decimal_places=2):
    try:
        return round(float(value) / divisor, decimal_places)
    except (ValueError, TypeError):
        logger.warning(f"无法转换为浮点数: {value}")
        return None

# 添加这个辅助函数在文件的适当位置
def safe_int(value):
    try:
        return int(value) if value is not None else 0
    except ValueError:
        logger.warning(f"无法转换为整数: {value}")
        return 0
