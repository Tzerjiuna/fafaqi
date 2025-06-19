from bs4 import BeautifulSoup
import json
import os

def guess_category(text):
    text = text.lower()
    if any(k in text for k in ['hoodie', 'shirt', 'jacket', 't-shirt', 'sweater', 'pants', 'track']):
        return 'clothing'
    elif any(k in text for k in ['sneakers', 'shoes', 'boots']):
        return 'shoes'
    elif any(k in text for k in ['bag', 'backpack', 'tote']):
        return 'bags'
    elif any(k in text for k in ['hat', 'scarf', 'ring', 'bracelet', 'belt']):
        return 'accessories'
    return 'others'

def extract_product_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = []

    for card in soup.select('[data-testid="productCard"]'):
        try:
            link = card.select_one('a')
            href = link.get('href')
            slug_base = href.strip('/').split('/')[-1]
            gender = 'men' if '/men/' in href else 'women' if '/women/' in href else 'unisex'

            brand = card.select_one('[data-component="ProductCardBrandName"]').text.strip()
            description = card.select_one('[data-component="ProductCardDescription"]').text.strip()
            title = f"{brand} {description}"

            image_url = card.select_one('img').get('src')
            image_filename = os.path.basename(image_url.split('?')[0])
            image_path = f"products/{image_filename}"

            price_text = card.select_one('[data-component="PriceFinal"]').text.strip().replace('$', '').replace(',', '')
            price = float(price_text)

            discount_price = None  # 如有折扣逻辑，可拓展

            category = guess_category(description)
            slug = f"{slug_base} ({gender}, {brand}, {category})"

            results.append({
                'title': title,
                'slug': slug,
                'description': description,
                'price': price,
                'discount_price': discount_price,
                'image': image_url,
                'image_path': image_path,
                'brand': brand
            })
        except Exception as e:
            print(f"跳过一个产品，错误：{e}")
            continue

    return results

# 从本地文件读取 HTML
with open('products.aspx', 'r', encoding='utf-8') as f:
    html_content = f.read()

data = extract_product_data(html_content)

# 保存到 JSON
with open('products.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("提取完成，保存为 products.json")
