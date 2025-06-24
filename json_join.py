import json

# JSON 파일 열기
with open('/Users/jinwoo/Desktop/restaurants.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(len(data))
# id 기준 중복 제거
unique_data = {entry['id']: entry for entry in data}
deduped_list = list(unique_data.values())
print(len(deduped_list))

# 파일 덮어쓰기
with open('/Users/jinwoo/Desktop/restaurants.json', 'w', encoding='utf-8') as f:
    json.dump(deduped_list, f, ensure_ascii=False, indent=2)