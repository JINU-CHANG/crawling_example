import json
import re
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

driver.get("https://map.naver.com/p/search/충무로%20음식점?c=15.00,0,0,0,dh")
time.sleep(1)

WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))

def crawling_restaurants(driver):
    restaurants = []

    print("[스크롤 시작]")

    scroll_container = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".place_on_pcmap #app-root .Ryr1F")))
    scroll(scroll_container)

    restaurant_elements = driver.find_elements(By.CSS_SELECTOR,".place_on_pcmap #app-root .XUrfU .place_bluelink.N_KDL")
    restaurants.extend(restaurant_elements)
    return restaurants

def scroll(scroll_container):
    last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
    while True:
        driver.execute_script("arguments[0].scrollTop += 300", scroll_container)
        time.sleep(0.5)
        current_height = driver.execute_script("return arguments[0].scrollTop", scroll_container)
        if current_height == last_height:
            break
        last_height = current_height

def extract_restaurant_info(driver, store_elements):
    restaurant_info = []
    except_keywords = ["카페", "디저트", "베이커리"]

    for idx, store in enumerate(store_elements, start=0):
        try:
            # 식당 이름 찾기
            store_name = store.find_element(By.CSS_SELECTOR, ".TYaxT").text.strip()
            category = store.find_element(By.CSS_SELECTOR, ".KCMnt").text.strip()
            
            if not store_name:
                continue
            if any(keyword in category for keyword in except_keywords):
                continue

            # 가게 클릭
            driver.execute_script("arguments[0].click();", store)
            time.sleep(1)

            # iframe으로 이동
            driver.switch_to.default_content()
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="entryIframe"]')))
            iframe = driver.find_element(By.XPATH, '//*[@id="entryIframe"]')
            iframe_src = iframe.get_attribute("src")
            driver.switch_to.frame(iframe)

            # 고유 ID 추출
            place_id = re.search(r"/place/(\d+)", iframe_src).group(1)
            
            # 주소 찾기
            try:
                address_elements = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".place_section_content .vV_z_"))
                )
                address = address_elements.find_element(By.CSS_SELECTOR, "span.LDgIH").text
            except Exception as e:
                print(store_name + " 주소 에러 발생 : " + str(e)) 
            
            # 가게 사진
            try:
                images = []
                image_elements = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".CB8aP .uDR4i")))
                img_elements = image_elements.find_elements(By.TAG_NAME, "img")
                images = [img.get_attribute("src") for img in img_elements if img.get_attribute("src")]
            except Exception as e:
                 print(store_name + " 가게 이미지 에러 발생 : " + str(e)) 

            # 영업 시간
            try:
                more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".gKP9i.RMgN0"))  # '영업시간 더보기' 버튼의 클래스
                )
                driver.execute_script("arguments[0].click();", more_button)

                opening_hours_elements = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((
                        By.XPATH,
                        "//div[@class='w9QyJ' or @class='w9QyJ undefined']"
                    ))
                )

                opening_hours = []
                for opening in opening_hours_elements:
                    day = None
                    hours = []
                    try:
                        day = opening.find_element(By.CSS_SELECTOR, "span.i8cJw").text.strip()
                    except Exception as e:
                        day = None
                    try:
                        hours_list = opening.find_element(By.CSS_SELECTOR, ".H3ua4").text.strip()
                    except Exception as e:
                        hours = None
                    if day and hours:
                        opening_hours.append({"dayOfWeek": day, "hours": hours})
            except Exception as e:
                print(store_name + " 영업시간 에러 발생 : " + str(e))
            
            # 메뉴 가져오기
            a_elements = driver.find_elements(By.CSS_SELECTOR, ".flicking-camera a")
            menu_link = next((a for a in a_elements if "menu" in a.get_attribute("href")), None)
            driver.execute_script("arguments[0].click();", menu_link)

            driver.switch_to.default_content()
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "entryIframe")))
            driver.switch_to.frame(driver.find_element(By.ID, "entryIframe"))

            # 메뉴 항목 로드 기다리기
            menu_elements = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".place_section_content .E2jtL"))
            )
            
            menu = []
            for m in menu_elements:
                try:
                    is_main = bool(m.find_elements(By.CSS_SELECTOR, "span.place_blind"))
                except:
                    is_main = False

                try:
                    name = m.find_element(By.CSS_SELECTOR, "span.lPzHi").text.strip()
                except:
                    name = None

                try:
                    introduce = m.find_element(By.CSS_SELECTOR, ".kPogF").text.strip()
                except:
                    introduce = None

                try:
                    price = m.find_element(By.CSS_SELECTOR, ".GXS1X em").text.strip()
                except:
                    price = None

                try:
                    img_el = m.find_element(By.CSS_SELECTOR, ".place_thumb img")
                    img_src = img_el.get_attribute("src").strip()
                except:
                    img_src = None

                menu.append({
                    "isMain": is_main,
                    "name": name,
                    "introduce": introduce,
                    "price": price,
                    "imgUrl": img_src
                })

            restaurant_info.append({
                "id" : place_id,
                "name" : store_name,
                "category" : category,
                "address" : address,
                "images" : images,
                "openingHours": opening_hours,
                "menu" : menu
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
restaurants = crawling_restaurants(driver)
#restaurants_info = extract_restaurant_info(driver, restaurants)

end = datetime.now()

print("[크롤링 결과]")
print(f"\n 최종 수집 식당 수: {len(restaurants)}개")
#print(json.dumps(restaurants_info, ensure_ascii=False, indent=2))
print("소요 시간 : ", (end - now).total_seconds())

driver.quit()
