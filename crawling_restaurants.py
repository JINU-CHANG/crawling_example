from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def crawling_restaurants(driver, url):
    driver.get(url)
    time.sleep(1)

    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))
    print("[스크롤 시작]")
    
    scroll_container = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".place_on_pcmap #app-root .Ryr1F")))
    scroll(driver, scroll_container, 300)

    restaurant_elements = driver.find_elements(By.CSS_SELECTOR,".place_on_pcmap #app-root .XUrfU .place_bluelink.N_KDL")
    return restaurant_elements

def scroll(driver, scroll_container, px):
    last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
    while True:
        driver.execute_script("arguments[0].scrollTop += arguments[1]", scroll_container, px)
        time.sleep(0.5)
        current_height = driver.execute_script("return arguments[0].scrollTop", scroll_container)
        if current_height == last_height:
            break
        last_height = current_height
