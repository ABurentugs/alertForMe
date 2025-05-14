from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import time
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


# Settings
DRIVER_PATH = 'C:/Users/ariun/Desktop/chromedriver-win64/chromedriver-win64/chromedriver.exe'
TOKYO_URL = "https://www.keishicho-gto.metro.tokyo.lg.jp/keishicho-u/reserve/offerList_detail?tempSeq=363&accessFrom=offerList"  
KANAGAWA_URL = "https://dshinsei.e-kanagawa.lg.jp/140007-u/reserve/offerList_detail?tempSeq=50909&accessFrom=offerList"
check_interval = 50  # seconds
TABLE_ID = "TBL"

service = Service(executable_path = DRIVER_PATH)
driver = webdriver.Chrome(service=service)

def main():
    global driver, KANAGAWA_URL, check_interval

    try:
        # change_date_button = date_parent_element.find_element(By.XPATH, '//input[@value="2週後>"]')
        # latest_week_element = driver.find_element(By.XPATH, '//')
        date_parent_element = None
        change_date_button = None

        while True:
        # get website

            driver.get(KANAGAWA_URL)
            driver.implicitly_wait(15)
        # click on button until latest date on table.
            date_parent_element = driver.find_element(By.CLASS_NAME, 'calender_pager_right')

            while True:
                try:
                    # date_parent_element = driver.find_element(By.CLASS_NAME, 'calender_pager_right')
                    change_date_button = driver.find_element(By.XPATH, '//input[@value="2週後＞"]')
                    if not change_date_button.is_enabled():
                        break
                    driver.execute_script("arguments[0].scrollIntoView(true);", change_date_button)
                    time.sleep(1)
                    change_date_button.click()
                    logger.info(f"CLICKED BUTTON\n\n\n\n\n\n")
                    # time.sleep(5)
                except:
                    break

        
        # search for latest available dates. Get latest availabel datess

        # send available dates via email to me if any new.s



            time.sleep(check_interval)
    finally:
        driver.quit()

if __name__ == "__main__":
    logger.info(f"started main")
    main()
    logger.info(f"ended main")

