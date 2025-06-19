'''
import os
import json
from bs4 import BeautifulSoup

def guess_category(text):
    text = text.lower()
    if any(x in text for x in ['hoodie', 'shirt', 'jacket', 't-shirt', 'pants', 'sweater', 'trousers']):
        return 'clothing'
    if any(x in text for x in ['sneakers', 'shoes', 'boots']):
        return 'shoes'
    if any(x in text for x in ['bag', 'backpack', 'tote']):
        return 'bags'
    if any(x in text for x in ['hat', 'scarf', 'ring', 'bracelet', 'belt']):
        return 'accessories'
    return 'others'

def extract_product_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    product_cards = soup.select('[data-testid="productCard"]')

    for card in product_cards:
        try:
            link = card.select_one('a')
            href = link.get('href') if link else None
            if not href:
                continue
            slug = href.strip('/').split('/')[-1]
            gender = 'men' if '/men/' in href else 'women' if '/women/' in href else 'unisex'

            brand_elem = card.select_one('[data-component="ProductCardBrandName"]')
            description_elem = card.select_one('[data-component="ProductCardDescription"]')
            price_elem = card.select_one('[data-component="PriceFinal"]')
            img_elem = card.select_one('img')

            if not all([brand_elem, description_elem, price_elem, img_elem]):
                continue

            brand = brand_elem.text.strip()
            description = description_elem.text.strip()
            title = f"{brand} {description}"
            price = float(price_elem.text.strip().replace('$', '').replace(',', ''))
            discount_price = None

            image_url = img_elem.get('src')
            image_name = os.path.basename(image_url).split('?')[0]
            image = f"products/{image_name}"

            category = guess_category(description)

            results.append({
                'title': description,
                'slug': slug,
                'gender': gender,
                'brand': brand,
                'description': title,
                'category': category,
                'price': price,
                'discount_price': discount_price,
                'image': image
            })
        except Exception as e:
            print(f"跳过一个产品，错误：{e}")
            continue

    return results

# 🔍 遍历文件夹
base_folder = '更新商品/网页/'
all_data = []

for root, dirs, files in os.walk(base_folder):
    for filename in files:
        if filename.endswith('.aspx'):
            filepath = os.path.join(root, filename)
            print(f'正在处理文件：{filepath}')
            with open(filepath, 'r', encoding='utf-8') as f:
                html = f.read()
                data = extract_product_data(html)  # 你已有的提取函数
                all_data.extend(data)

# ✏️ 保存到 JSON 文件
with open('products.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"完成提取，总商品数：{len(all_data)}，保存为 products.json")
'''

import json
import pymysql

# 数据库连接信息
conn = pymysql.connect(
    host='103.30.79.57',
    user='fafaqishop',
    password='fafaqishop',
    database='fafaqishop',
    charset='utf8mb4'
)

# 读取 products.json
with open('products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

try:
    with conn.cursor() as cursor:
        for product in products:
            image = product.get('image')
            description = product.get('description')
            if image and description:
                # 按 image 匹配，更新 description
                sql = "UPDATE core_product SET description=%s WHERE image=%s"
                cursor.execute(sql, (description, image))
        conn.commit()
    print("数据库 core_product 表已根据 products.json 更新 description 字段。")
finally:
    conn.close()