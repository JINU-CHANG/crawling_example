import json
from datetime import datetime
from crawling_restaurants import crawling_restaurants, crawling_restaurant_info
from driver import get_driver, go_to_search_page

driver = get_driver()
go_to_search_page(driver, "https://map.naver.com/p/search/충무로%20음식점?c=15.00,0,0,0,dh") 
restaurants = crawling_restaurants(driver)
restaurants_info = crawling_restaurant_info(driver, restaurants)

print("[크롤링 결과]")
print(f"\n 최종 수집 식당 수: {len(restaurants)}개")
print(json.dumps(restaurants_info, ensure_ascii=False, indent=2))

end = datetime.now()
driver.quit()