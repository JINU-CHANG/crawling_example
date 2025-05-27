from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from crawling_restaurnats_detail import crawling_restaurant_info
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def get_driver():
    options = Options()
    #options.add_argument("--headless=new")
    #options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def crawling_restaurants(url):
    restaurants_info = []

    driver = get_driver()
    driver.get(url)
    WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".place_on_pcmap #app-root .zRM9F")))
    divs = driver.find_elements(By.XPATH, "//a[contains(@class, 'mBN2s')]")
        
    for page in range(1):
        print(f"{page + 1}페이지 [가게 크롤링 시작]")
        driver.execute_script("arguments[0].click();", divs[page])
        scroll_container = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".place_on_pcmap #app-root .Ryr1F")))
        scroll(driver, scroll_container, 300)
        restaurant_elements = driver.find_elements(By.CSS_SELECTOR,".place_on_pcmap #app-root .XUrfU .place_bluelink.N_KDL")
        restaurants_info.extend(crawling_restaurant_info(driver, restaurant_elements))
    return restaurants_info

def scroll(driver, scroll_container, px, timeout=5):
    print("[스크롤 시작]")
    last_height = driver.execute_script("return arguments[0].scrollTop", scroll_container)

    def scroll_condition(driver):
        current_height = driver.execute_script("return arguments[0].scrollTop", scroll_container)
        return current_height > last_height

    while True:
        driver.execute_script("arguments[0].scrollTop += arguments[1]", scroll_container, px)
        try:
            WebDriverWait(driver, timeout).until(scroll_condition)
        except:
            break
        last_height = driver.execute_script("return arguments[0].scrollTop", scroll_container)

    print("[스크롤 완료]")