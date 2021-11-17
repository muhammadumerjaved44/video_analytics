import os
import re
import time
import pyautogui

import wget
from bs4 import BeautifulSoup
from decouple import config
# from selenium import webdriver
from seleniumwire import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains, DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from fastapi import HTTPException
from fake_useragent import UserAgent

try:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
except:
    pass

def load_browser() -> object:

    """This fucntion load the chrome browser

    Args:
        isHeadless (bool): if Ture headless is applied otherwise not

    Returns:
        object: returns the browser object
    """

    # mobile_emulation = { "deviceName": "Nexus 5" }
    caps = DesiredCapabilities.CHROME
    ua = UserAgent()
    user_agent = ua.random
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    option = Options()

    option.add_argument(f'user-agent={user_agent}')
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    # option.add_experimental_option("mobileEmulation", mobile_emulation)
    # if isHeadless: option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    # option.add_argument("--disable-extensions")
    option.add_extension('chromedriver/extention/ZenMate-Free-VPN–Best-VPN-for-Chrome.crx')
    option.add_argument("--disable-popup-blocking")
    option.add_argument('--disable-dev-shm-usage')
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    print('loading local chrome driver...', os.path.realpath('chromedriver/chromedriver'))
    driver = webdriver.Chrome(executable_path=os.path.realpath('chromedriver/chromedriver'), options=option, desired_capabilities=caps)
    print('local driver is running')

    # driver.get('https://www.tiktok.com/?is_copy_url=1&is_from_webapp=v1')


    return driver


def open_vpn_service():
    import time
    pyautogui.click(x=1834, y=80, clicks=1, interval=1, button='left')
    time.sleep(5)
    pyautogui.click(x=1669, y=236, clicks=1, interval=1, button='left')
    time.sleep(5)
    pyautogui.click(x=1775, y=639, clicks=1, interval=1, button='left')
    time.sleep(5)
    pyautogui.click(x=1629, y=378, clicks=1, interval=1, button='left')
    
driver = load_browser()
time.sleep(10)
open_vpn_service()
time.sleep(2)
driver.get('https://www.tiktok.com')
