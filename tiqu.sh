#!/bin/bash

mkdir -p media/products

for file in 更新商品/shoes.json; do
  echo "📄 正在处理: $file"

  jq -r '.[].images[]' "$file" | while read -r url; do
    filename=$(basename "$url")
    target="media/products/$filename"

    if [[ -f "$target" ]]; then
      echo "✅ 已存在: $filename"
      continue
    fi

    echo "⬇️ 下载: $filename"
    wget -c --header="User-Agent: Mozilla/5.0" "$url" -O "$target"
  done
done

echo "🎉 所有图片下载完成"
