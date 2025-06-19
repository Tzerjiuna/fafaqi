import pymysql

# 数据库连接
conn = pymysql.connect(
    host='103.30.79.57',
    user='fafaqishop',
    password='fafaqishop',
    database='fafaqishop'
)
cursor = conn.cursor()

# 读取保存的路径列表文件
with open("updated_image_paths.txt", "r") as file:
    image_urls = file.readlines()

# 去除文件中的换行符
image_urls = [url.strip() for url in image_urls]

# 遍历图片路径并删除数据库中相应的记录
for url in image_urls:
    # 从 URL 中去掉前缀，得到图片路径
    image_path = url.replace("https://farfetch.tzkun.cc/media/", "")

    # 执行 SQL 查询，找到与该图片路径匹配的 ProductImage 记录
    cursor.execute("SELECT id, image FROM core_productimage WHERE image LIKE %s", ('%' + image_path + '%',))
    results = cursor.fetchall()

    # 如果找到了匹配的记录，则删除
    if results:
        for row in results:
            product_image_id = row[0]
            # 删除该记录
            cursor.execute("DELETE FROM core_productimage WHERE id = %s", (product_image_id,))
            print(f"Deleted ProductImage record with ID {product_image_id} for image {image_path}")
    else:
        print(f"No matching record found for image {image_path}")

# 提交删除操作
conn.commit()

# 关闭数据库连接
cursor.close()
conn.close()

print("删除操作完成。")
import pymysql

# 数据库连接
conn = pymysql.connect(
    host='103.30.79.57',
    user='fafaqishop',
    password='fafaqishop',
    database='fafaqishop'
)
cursor = conn.cursor()

# 读取保存的路径列表文件
with open("updated_image_paths.txt", "r") as file:
    image_urls = file.readlines()

# 去除文件中的换行符
image_urls = [url.strip() for url in image_urls]

# 遍历图片路径并删除数据库中相应的记录
for url in image_urls:
    # 从 URL 中去掉前缀，得到图片路径
    image_path = url.replace("https://farfetch.tzkun.cc/media/", "")

    # 执行 SQL 查询，找到与该图片路径匹配的 ProductImage 记录
    cursor.execute("SELECT id, image FROM core_productimage WHERE image LIKE %s", ('%' + image_path + '%',))
    results = cursor.fetchall()

    # 如果找到了匹配的记录，则删除
    if results:
        for row in results:
            product_image_id = row[0]
            # 删除该记录
            cursor.execute("DELETE FROM core_productimage WHERE id = %s", (product_image_id,))
            print(f"Deleted ProductImage record with ID {product_image_id} for image {image_path}")
    else:
        print(f"No matching record found for image {image_path}")

# 提交删除操作
conn.commit()

# 关闭数据库连接
cursor.close()
conn.close()

print("删除操作完成。")
