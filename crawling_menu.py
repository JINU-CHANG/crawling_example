import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def crawling_menu(driver):
    print("[메뉴 정보 크롤링 시작]")
    menus = []
    a_elements = driver.find_elements(By.CSS_SELECTOR, ".place_fixed_maintab a")
    menu_link = next((a for a in a_elements if "menu" in a.get_attribute("href")), None)

    if menu_link is None:
        return menus
    
    driver.execute_script("arguments[0].click();", menu_link)
    time.sleep(0.1)
    if driver.find_elements(By.CSS_SELECTOR, ".smart_category.slick-slider.general_place"):
        return menus

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
            price = int(price.replace(",", ""))
        except:
            price = None

        try:
            img_el = m.find_element(By.CSS_SELECTOR, ".place_thumb img")
            img_src = img_el.get_attribute("src").strip()
        except:
            img_src = None

        menus.append({
            "isMain": is_main,
            "name": name,
            "introduce": introduce,
            "price": price,
            "imgUrl": img_src
        })
    return menus

def calculate_menu_average(menus):
    main_prices = [menu["price"] for menu in menus
               if menu.get("isMain") and isinstance(menu.get("price"), int)]

    if not main_prices:
        main_prices = [menu["price"] for menu in menus
                if isinstance(menu.get("price"), int)]
    
    return sum(main_prices) / len(main_prices)