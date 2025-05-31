import json
import os
from datetime import datetime
from crawling_restaurants import crawling_restaurants

start_time = datetime.now()

save_dir = "/Users/jinwoo/Desktop"
filename = "restaurants_page.json"
file_path = os.path.join(save_dir, filename)

# 충무로 음식점 "https://map.naver.com/p/search/%EC%B6%A9%EB%AC%B4%EB%A1%9C%20%EC%9D%8C%EC%8B%9D%EC%A0%90?c=15.00,0,0,0,dh"
# 동대입구 음식점 "https://map.naver.com/p/search/%EC%9D%8C%EC%8B%9D%EC%A0%90?c=14138202.1256454%2C4517460.9622469%2C16.34%2C0%2C0%2C0%2Cdh"
# 충무로 확대 버전 "https://map.naver.com/p/search/%EC%9D%8C%EC%8B%9D%EC%A0%90?c=14137233.3095541%2C4517585.4963101%2C17.13%2C0%2C0%2C0%2Cdh"
restaurants_info = crawling_restaurants("https://map.naver.com/p/search/%EC%9D%8C%EC%8B%9D%EC%A0%90?c=14138202.1256454%2C4517460.9622469%2C16.34%2C0%2C0%2C0%2Cdh")

print("[크롤링 결과]")
print(f"\n 최종 수집 식당 수: {len(restaurants_info)}개")

restaurants_json = json.dumps(restaurants_info, ensure_ascii=False, indent=2)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(restaurants_json)

end_time = datetime.now()
elapsed = end_time - start_time
print(f"저장완료 : {file_path}")
print(f"총 소요 시간: {elapsed.seconds}초 ({elapsed})")
