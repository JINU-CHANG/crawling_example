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

# 네이버 맛집 검색
driver.get("https://map.naver.com/p/search/충무로%20음식점?c=15.00,0,0,0,dh")
time.sleep(1)

# iframe 안으로 진입
WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))

# 스크롤 가능한 div 가져오기
scrollable_div = driver.find_element(By.CSS_SELECTOR, ".Ryr1F") # 음식점 리스트

def scroll_and_collect_restaurants(driver, scrollable_div, scroll_pause_time=2.5, max_scroll=30):
    restaurants = []
    scroll_count = 0

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
            restaurants.extend(elements_after)
            print("\n[스크롤 종료]")
            break

        scroll_count += 1

    print(f"\n[전체 스크롤 완료] 최종 수집 식당 수: {len(restaurants)}개")
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
            address_elements = driver.find_element(By.CSS_SELECTOR, ".place_section_content .vV_z_")
            address = address_elements.find_element(By.CSS_SELECTOR, "span.LDgIH").text

            print(f"가게명: {store_name}, 주소: {address}")

            restaurant_info.append({
                "name": store_name,
                "address": address
            })

            # 다시 검색 프레임으로 복귀
            driver.switch_to.default_content()
            WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))

        except Exception as e:
            print(f"에러 발생: {e}")
            driver.switch_to.default_content()
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))
            continue

    return restaurant_info
    
# 식당 이름 모으기
restaurants = scroll_and_collect_restaurants(driver, scrollable_div, scroll_pause_time=1.5, max_scroll=30)
extract_restaurant_info(driver, restaurants)

end = datetime.now()
print("소요 시간 : ", (end - now).total_seconds())

driver.quit()
