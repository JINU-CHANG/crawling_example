import json
from datetime import datetime
from crawling_restaurants import crawling_restaurants
from crawling_restaurnats_detail import crawling_restaurant_info
from driver import get_driver

driver = get_driver()
restaurants = crawling_restaurants(driver, "https://map.naver.com/p/search/충무로%20음식점?c=15.00,0,0,0,dh")
restaurants_info = crawling_restaurant_info(driver, restaurants)

print("[크롤링 결과]")
print(f"\n 최종 수집 식당 수: {len(restaurants)}개")
print(json.dumps(restaurants_info, ensure_ascii=False, indent=2))

end = datetime.now()
driver.quit()
