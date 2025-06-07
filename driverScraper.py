from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options 
from selenium.webdriver.common.by import By

import glob

import smtplib
from email.message import EmailMessage
import ssl
import os
from dotenv import load_dotenv
load_dotenv()

import time, datetime
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

# Email settings
EMAIL_SENDER = os.getenv("EMAIL_SENDER") 
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


# URL settings
DRIVER_PATH = '/snap/bin/geckodriver'
TOKYO_URL = "https://www.keishicho-gto.metro.tokyo.lg.jp/keishicho-u/reserve/offerList_detail?tempSeq=363&accessFrom=offerList"  
KANAGAWA_URL = "https://dshinsei.e-kanagawa.lg.jp/140007-u/reserve/offerList_detail?tempSeq=50909&accessFrom=offerList"
check_interval = 50# seconds
TABLE_ID = "TBL"
LAST_DATES_FILE = "./last_dates.txt"

service = Service(executable_path = DRIVER_PATH)
options = Options()
options.headless = True
driver = webdriver.Firefox(service=service, options=options)

def send_email_with_attachment(subject, body, attachment_path):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg.set_content(body)

    # Attach image
    with open(attachment_path, "rb") as file:
        file_data = file.read()
        file_name = os.path.basename(file.name)
    msg.add_attachment(file_data, maintype="image", subtype="png", filename=file_name)

    # send email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
            logger.info(f"Email sent successfully")
    except Exception as e:
        logger.error(f"Could not send email: {e}")

def test_email():
    msg = EmailMessage()
    msg["Subject"] = "Test Email - App Password"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg.set_content("This is a test email to verify the Gmail App Password setup.")

    logger.info(f"sender: {EMAIL_SENDER}, receiver: {EMAIL_RECEIVER}")
    # Send the email
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Email sent successfully.")
    except smtplib.SMTPAuthenticationError as e:
        print("❌ Authentication failed. Check your app password and email settings.")
        print("Error:", e)
    except Exception as e:
        print("❌ An error occurred.")
        print("Error:", e)

def run_scraper():
    global driver, KANAGAWA_URL, check_interval

    try:
        # change_date_button = date_parent_element.find_element(By.XPATH, '//input[@value="2週後>"]')
        # latest_week_element = driver.find_element(By.XPATH, '//')
        date_parent_element = None
        change_date_button = None
        time_stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # while True:
        # # get website

        driver.get(KANAGAWA_URL)
        og_url = driver.current_url
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

        
        table_element = driver.find_element(By.ID, "TBL")

        # get dates from table
        current_dates = get_dates_from_table(table_element)
        last_dates = load_last_dates()
        new_dates = [d for d in current_dates if d not in last_dates]
        logger.info(f"new dates: {new_dates}\n\n\n")
        logger.info(f"last dates: {last_dates}\n\n\n")
        logger.info(f"current dates: {current_dates}\n\n\n")

        if new_dates:

        # take screenshot of latest page, copy link of latest page
            screenshot_path = f"./screenshots/screenshot_{time_stamp}.png"
            table_element.screenshot(screenshot_path)

            # send available dates via email to me if any new.
            body = f"Latest URL: {og_url}"
            # logger.info(f"{body}")
            send_email_with_attachment("Page update", body, screenshot_path)
            save_last_dates(current_dates)
            delete_old_photos()
    finally:
        driver.quit()

def load_last_dates():
    if not os.path.exists(LAST_DATES_FILE):
        return []
    with open(LAST_DATES_FILE, "r", encoding='utf-8') as f:
        return [line.strip().strip(',') for line in f.readlines()]

def save_last_dates(dates):
    logger.info(f"{dates}, {type(dates)}")
    with open(LAST_DATES_FILE, "w", encoding='utf-8') as f:
        for date in dates:
            logger.info(f"date: {str(date)}")
            f.write(str(date) + ',' + '\n')

def delete_old_photos(folder_path="./screenshots", pattern="*.png"):     
    files = glob.glob(os.path.join(folder_path, pattern))
    for pic in files:
        try:
            os.remove(pic)
        except Exception as e:
            logger.error(f"could not delete old photos: {e}")
            pass


def get_dates_from_table(table_element):
    rows = table_element.find_element(By.XPATH, "//tr[@id='height_auto_普通車ＡＭ']")
    cols = rows.find_elements(By.XPATH, "//*[contains(text(), '普通車ＡＭは')]")
    dates = []

    for col in cols:
        # cols = row.find_elements(By.TAG_NAME, "td")
        if not col:
            continue
        date_text = col.text.strip()
        dates.append(date_text)

    return dates

if __name__ == "__main__":
    logger.info(f"started main")
    run_scraper()
    # test_email()
    logger.info(f"ended main")

