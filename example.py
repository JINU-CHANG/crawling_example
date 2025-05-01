import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

now = datetime.now()

options = Options()
driver = webdriver.Chrome(options=options)

address = ["https://map.naver.com/p/search/%EC%9D%8C%EC%8B%9D%EC%A0%90?c=16.82,0,0,0,dh", 
        "https://map.naver.com/p/search/충무로%20음식점?c=15.00,0,0,0,dh"]

# 네이버 맛집 검색
driver.get("https://map.naver.com/p/search/충무로%20음식점?c=15.00,0,0,0,dh")
time.sleep(1)

# iframe 안으로 진입
WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))

# 스크롤 가능한 div 가져오기
scrollable_div = scrollable_div = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".Ryr1F"))
)

def scroll_and_collect_restaurants(driver, scrollable_div, scroll_pause_time=2.5, max_scroll=30):
    restaurants = []
    scroll_count = 0
    before_count = 0
    after_count = 0

    while scroll_count < max_scroll:

        print(f"\n[스크롤 {scroll_count + 1}회차 시작]")

        # 가게 리스트 수집
        store_elements = driver.find_elements(By.CSS_SELECTOR,
            ".place_on_pcmap #app-root .XUrfU .place_bluelink.N_KDL"
        )
        before_count = len(store_elements)

        # 천천히 스크롤
        total_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        current_scroll = driver.execute_script("return arguments[0].scrollTop", scrollable_div)
        last_scroll = -1
        while current_scroll < total_height:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollTop + 300", scrollable_div)
            time.sleep(0.5)
            current_scroll = driver.execute_script("return arguments[0].scrollTop", scrollable_div)
            if last_scroll == current_scroll:
                break
            last_scroll = current_scroll

        time.sleep(scroll_pause_time)

        # 스크롤 후 가게 리스트 다시 수집
        elements_after = driver.find_elements(
            By.CSS_SELECTOR,
            ".place_on_pcmap #app-root .XUrfU .place_bluelink.N_KDL"
        )
        after_count = len(elements_after)

        if after_count == before_count:
            print("\n[스크롤 종료]")
            break

        scroll_count += 1
    restaurants.extend(elements_after)
    return restaurants

def extract_restaurant_info(driver, store_elements):
    restaurant_info = []

    for idx, store in enumerate(store_elements, start=0):
        try:
            # 식당 이름 찾기
            name_element = store.find_element(By.CSS_SELECTOR, ".TYaxT")
            store_name = name_element.text.strip()

            if not store_name:
                continue

            # 가게 클릭
            driver.execute_script("arguments[0].click();", store)
            time.sleep(1)

            # iframe으로 이동
            driver.switch_to.default_content()
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="entryIframe"]')))
            driver.switch_to.frame(driver.find_element(By.XPATH, '//*[@id="entryIframe"]'))

            # 주소 찾기
            try:
                address_elements = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".place_section_content .vV_z_"))
                )
                address = address_elements.find_element(By.CSS_SELECTOR, "span.LDgIH").text
            except Exception as e:
                print(store_name + " 주소 에러 발생 : " + str(e)) 

            # 영업 시간
            try:
                more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".gKP9i.RMgN0"))  # '영업시간 더보기' 버튼의 클래스
                )
                driver.execute_script("arguments[0].click();", more_button)

                opening_hours_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((
                        By.XPATH,
                        "//div[@class='w9QyJ' or @class='w9QyJ undefined']"
                    ))
                )

                opening_hours = []
                for opening in opening_hours_elements:
                    day = None
                    hours = None
                    try:
                        day = opening.find_element(By.CSS_SELECTOR, "span.i8cJw").text.strip()
                    except Exception as e:
                        day = None
                    try:
                        hours = opening.find_element(By.CSS_SELECTOR, ".H3ua4").text.strip()
                    except Exception as e:
                        hours = None
                    if day and hours:
                        opening_hours.append({"day": day, "hours": hours})
            except Exception as e:
                print(store_name + " 영업시간 에러 발생 : " + str(e))
            
            restaurant_info.append({
                "name": store_name,
                "address": address,
                "opening_hours": opening_hours
            })

            print("가게명 : ", store_name, " address : ", address)

            # 다시 검색 프레임으로 복귀
            driver.switch_to.default_content()
            WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))

        except Exception as e:
            driver.switch_to.default_content()
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))
            continue

    return restaurant_info
    
# 식당 이름 모으기
restaurants = scroll_and_collect_restaurants(driver, scrollable_div, scroll_pause_time=1.5, max_scroll=1)
restaurants_info = extract_restaurant_info(driver, restaurants)

end = datetime.now()

print("[크롤링 결과]")
print(f"\n 최종 수집 식당 수: {len(restaurants)}개")
print(json.dumps(restaurants_info, ensure_ascii=False, indent=2))
print("소요 시간 : ", (end - now).total_seconds())

driver.quit()
