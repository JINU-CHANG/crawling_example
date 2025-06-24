from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

from crawling_menu import calculate_menu_average, crawling_menu

except_keywords = ["카페", "디저트", "베이커리"]

def crawling_restaurant_info(driver, restaurant_elements):
    restaurant_info = []
    print(f"[{len(restaurant_elements)}개의 가게 디테일 정보 크롤링 시작]")
    
    for idx, restaurant in enumerate(restaurant_elements, start = 0):
        try:
            store_name = restaurant.find_element(By.CSS_SELECTOR, ".TYaxT").text.strip()
            category = restaurant.find_element(By.CSS_SELECTOR, ".KCMnt").text.strip()
            
            if not store_name:
                continue
            if any(keyword in category for keyword in except_keywords):
                continue

            driver.execute_script("arguments[0].click();", restaurant)

            driver.switch_to.default_content()
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="entryIframe"]')))
            
            entryIframe = driver.find_element(By.XPATH, '//*[@id="entryIframe"]')
            entryIframe_src = entryIframe.get_attribute("src")
            place_id = re.search(r"/place/(\d+)", entryIframe_src).group(1)
        
            driver.switch_to.frame(entryIframe)
        
            print(f"{idx} 가게명 : ", store_name)
            address = crawling_address(driver)
            images = crawling_img(driver)
            opening_hours = crawling_openingHours(driver)
            menu = crawling_menu(driver)

            restaurant_info.append({
                "id" : place_id,
                "name" : store_name,
                "category" : category,
                "address" : address,
                "images" : images,
                "openingHours": opening_hours,
                "menus" : menu,
                "menu_average" : int(calculate_menu_average(menu))
            })

            switch_iframe(driver, "searchIframe")
        except Exception :
            switch_iframe(driver, "searchIframe")
            continue
            
    return restaurant_info

def switch_iframe(driver, name):
    driver.switch_to.default_content()
    WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it((By.ID, name)))

def crawling_address(driver):
    print("[주소 정보 크롤링 시작]")
    try:
        address_elements = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".place_section_content .vV_z_")))
        address = address_elements.find_element(By.CSS_SELECTOR, "span.LDgIH").text.strip()
    except Exception as e:
        print("주소 에러 발생 : " + str(e)) 
    return address

def crawling_img(driver):
    print("[이미지 정보 크롤링 시작]")
    try:
        images = []
        image_elements = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".CB8aP .uDR4i")))
        img_elements = image_elements.find_elements(By.TAG_NAME, "img")
        images = [img.get_attribute("src") for img in img_elements if img.get_attribute("src")]
    except Exception as e:
        print("가게 이미지 에러 발생 : " + str(e))
    return images

def crawling_openingHours(driver):
    print("[영업 시간 정보 크롤링 시작]")
    try:
        if driver.find_elements(By.CSS_SELECTOR, ".O8qbU.J1zN9 span.LDgIH"):
            return []
        
        button_element = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".gKP9i.RMgN0")))
        driver.execute_script("arguments[0].click();", button_element)

        opening_hours_elements = WebDriverWait(driver, 60).until(
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
                hours = parse_hours(opening.find_element(By.CSS_SELECTOR, ".H3ua4").text.strip())
            except Exception as e:
                hours = None
            if day and hours:
                opening_hours.append({"dayOfWeek": day, "hours": hours})
    except Exception as e:
        print(" 영업시간 에러 발생 : " + str(e))
    return opening_hours

def parse_hours(hours):
    lines = hours.strip().split('\n')

    result = {
        "startTime": None,
        "endTime": None,
        "breakStartTime": None,
        "breakEndTime": None,
        "lastOrderTime": None
    }

    for line in lines:
        line = line.strip()

        if "브레이크" in line:
            parts = line.split(' - ')
            result["breakStartTime"] = clean_time_string(parts[0])
            result["breakEndTime"] = clean_time_string(parts[1].split()[0])
        elif "라스트오더" in line:
            result["lastOrderTime"] = clean_time_string(line.split()[0])
        elif " - " in line:
            start, end = line.split(' - ')
            result["startTime"] = clean_time_string(start)
            result["endTime"] = clean_time_string(end)

    return result

def clean_time_string(t: str) -> str:
    t = t.strip().replace(",", "")
    return "00:00" if t == "24:00" else t