import json

# JSON 파일 열기
with open('/Users/jinwoo/Desktop/restaurants.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# category만 추출해서 set에 담기
categories = {item['category'] for item in data if 'category' in item}

print(categories)
