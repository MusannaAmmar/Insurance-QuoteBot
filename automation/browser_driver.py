
# import re
# import time
# import json
# import os
# import traceback
# from typing import Dict, List, Tuple, Any, Optional
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait, Select
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from webdriver_manager.chrome import ChromeDriverManager

# # Global tracking
# PAGE_FINGERPRINT_SEEN = set()

# # ================================================================
# #  1. ENHANCED BROWSER SETUP
# # ================================================================
# def create_browser(headless: bool = False) -> webdriver.Chrome:
#     options = Options()
#     if headless:
#         options.add_argument("--headless=new")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
    
#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()),
#         options=options
#     )
#     driver.set_window_size(1400, 1000)
#     driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
#     return driver





# def click_cookie_accept(driver, timeout: int = 15):
#     """
#     Continuously check for a cookie consent banner and click 'Accept' if found.
#     Keeps running during page load.
#     """
#     start_time = time.time()
#     accepted = False

#     while time.time() - start_time < timeout:
#         try:
#             # Look for buttons or links with common consent text
#             buttons = driver.find_elements(
#                 By.XPATH,
#                 "//*["
#                 "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'accept') or "
#                 "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'agree') or "
#                 "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'allow') or "
#                 "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'consent') or "
#                 "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ok') or "
#                 "contains(translate(@id,'cookie')) or "
#                 "contains(translate(@class,'COOKIE','cookie'))"
#                 "]"
#             )

#             for btn in buttons:
#                 if btn.is_displayed():
#                     driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
#                     time.sleep(0.3)
#                     btn.click()
#                     print("🍪 Accepted cookie banner.")
#                     accepted = True
#                     break

#             if accepted:
#                 break
#         except Exception:
#             pass

#         # Wait a bit before retrying (banner might still be loading)
#         time.sleep(1)

#     if not accepted:
#         print("ℹ️ No cookie banner detected after waiting period.")
    
#     return driver




import re
import time
import json
import os
import traceback
from typing import Dict, List, Tuple, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Global tracking
PAGE_FINGERPRINT_SEEN = set()

# ================================================================
#  1. ENHANCED BROWSER SETUP
# ================================================================
def create_browser(headless: bool = False) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.set_window_size(1400, 1000)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def click_cookie_accept(driver, timeout: int = 15):
    """
    Continuously check for a cookie consent banner and click 'Accept' if found.
    Keeps running during page load.
    """
    start_time = time.time()
    accepted = False

    while time.time() - start_time < timeout:
        try:
            # Look for buttons or links with common consent text
            buttons = driver.find_elements(
                By.XPATH,
                "//*["
                "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'accept') or "
                "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'agree') or "
                "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'allow') or "
                "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'consent') or "
                "contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ok') or "
                "contains(translate(@id,'cookie')) or "
                "contains(translate(@class,'COOKIE','cookie'))"
                "]"
            )

            for btn in buttons:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                    time.sleep(0.3)
                    btn.click()
                    print("🍪 Accepted cookie banner.")
                    accepted = True
                    break

            if accepted:
                break
        except Exception:
            pass

        # Wait a bit before retrying (banner might still be loading)
        time.sleep(1)

    if not accepted:
        print("ℹ️ No cookie banner detected after waiting period.")
    
    return driver