from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

def crawling_restaurant_info(driver, restaurant_elements):
    restaurant_info = []
    except_keywords = ["카페", "디저트", "베이커리"]
    print(f"[{len(restaurant_elements)}개의 가게 디테일 정보 크롤링 시작]")
    for idx, restaurant in enumerate(restaurant_elements, start=0):
        try:
            store_name = restaurant.find_element(By.CSS_SELECTOR, ".TYaxT").text.strip()
            category = restaurant.find_element(By.CSS_SELECTOR, ".KCMnt").text.strip()
            
            if not store_name:
                continue
            if any(keyword in category for keyword in except_keywords):
                continue

            driver.execute_script("arguments[0].click();", restaurant)
            time.sleep(1)

            driver.switch_to.default_content()
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="entryIframe"]')))

            iframe = driver.find_element(By.XPATH, '//*[@id="entryIframe"]')
            iframe_src = iframe.get_attribute("src")
            driver.switch_to.frame(iframe)

            place_id = re.search(r"/place/(\d+)", iframe_src).group(1)
            print(f"{idx} 가게명 : ", store_name)
            print("[주소 정보 크롤링 시작]")
            address = crawling_address(driver)
            print("[이미지 정보 크롤링 시작]")
            images = crawling_img(driver)
            print("[영업 시간 정보 크롤링 시작]")
            opening_hours = crawling_openingHours(driver)
            print("[메뉴 정보 크롤링 시작]")
            menu = crawling_menu(driver)

            restaurant_info.append({
                "id" : place_id,
                "name" : store_name,
                "category" : category,
                "address" : address,
                "images" : images,
                "openingHours": opening_hours,
                "menu" : menu
            })

            driver.switch_to.default_content()
            WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))

        except Exception as e:
            driver.switch_to.default_content()
            WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))
            continue

    return restaurant_info

def crawling_address(driver):
    try:
        address_elements = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".place_section_content .vV_z_")))
        address = address_elements.find_element(By.CSS_SELECTOR, "span.LDgIH").text.strip()
    except Exception as e:
        print("주소 에러 발생 : " + str(e)) 
    return address

def crawling_img(driver):
    try:
        images = []
        image_elements = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".CB8aP .uDR4i")))
        img_elements = image_elements.find_elements(By.TAG_NAME, "img")
        images = [img.get_attribute("src") for img in img_elements if img.get_attribute("src")]
    except Exception as e:
        print("가게 이미지 에러 발생 : " + str(e))
    return images

def crawling_openingHours(driver):
    try:
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
            result["breakStartTime"] = parts[0]
            result["breakEndTime"] = parts[1].split()[0]
        elif "라스트오더" in line:
            result["lastOrderTime"] = line.split()[0]
        elif " - " in line:
            # 영업시간은 첫 번째 라인이라고 가정
            start, end = line.split(' - ')
            result["startTime"] = start
            result["endTime"] = end

    return result

def crawling_menu(driver):
    try:
        menu = []
        a_elements = driver.find_elements(By.CSS_SELECTOR, ".flicking-camera a")
        menu_link = next((a for a in a_elements if "menu" in a.get_attribute("href")), None)

        if menu_link is None:
            return menu
        
        driver.execute_script("arguments[0].click();", menu_link)

        driver.switch_to.default_content()
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "entryIframe")))
        driver.switch_to.frame(driver.find_element(By.ID, "entryIframe"))

        menu_elements = WebDriverWait(driver, 60).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".place_section_content .E2jtL")))
    
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
    except Exception as e:
         print(" 메뉴 에러 발생 : " + str(e))
    return menu
