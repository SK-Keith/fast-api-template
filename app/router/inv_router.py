import csv
import mysql.connector
from datetime import datetime

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'mydb'
}

# 连接到数据库
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# 准备插入语句
insert_query = """
INSERT INTO inv_order (shop, sku, purchase_date, asin, quantity, state, price)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

# 读取 inv.txt 文件
with open('inv.txt', 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file, delimiter='\t')
    next(csv_reader)  # 跳过表头

    for row in csv_reader:
        if len(row) >= 15:  # 确保行有足够的列
            shop = 'go'  # 假设所有订单属于同一个店铺，您可能需要根据实际情况修改
            purchase_date = datetime.strptime(row[2], '%Y-%m-%dT%H:%M:%S%z').date()
            sku = row[11]
            asin = row[12]
            quantity = int(row[14])
            state = row[4] if len(row) > 4 else None  # 假设第7列是state

            if state in ['Pending', 'Shipped']:
                price = float(row[16]) if len(row) > 16 and row[16] else 0  # 如果state为Pending或Shipped，尝试获取价格
            else:
                price = 0  # 如果state不是Pending或Shipped，价格默认为0

            # 准备数据
            data = (shop, sku, purchase_date, asin, quantity, state, price)

            try:
                # 执行插入操作
                cursor.execute(insert_query, data)
            except mysql.connector.Error as err:
                print(f"数据插入错误: {err}")

# 提交事务
conn.commit()

# 关闭游标和连接
cursor.close()
conn.close()

print("数据导入完成")
