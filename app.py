import json
import os
from datetime import datetime
from crawling_restaurants import crawling_restaurants

start_time = datetime.now()

save_dir = "/Users/jinwoo/Desktop"
filename = "restaurants_page.json"
file_path = os.path.join(save_dir, filename)

restaurants_info = crawling_restaurants("https://map.naver.com/p/search/충무로&음식점?c=15.00,0,0,0,dh")

print("[크롤링 결과]")
print(f"\n 최종 수집 식당 수: {len(restaurants_info)}개")

restaurants_json = json.dumps(restaurants_info, ensure_ascii=False, indent=2)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(restaurants_json)

end_time = datetime.now()
elapsed = end_time - start_time
print(f"저장완료 : {file_path}")
print(f"총 소요 시간: {elapsed.seconds}초 ({elapsed})")
