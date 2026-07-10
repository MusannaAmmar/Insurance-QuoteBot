
from automation.browser_driver import*
from automation.form_filer import*




def fill_form(driver, site_url: str, form_data: Dict = None) -> bool:
    global PAGE_FINGERPRINT_SEEN
    PAGE_FINGERPRINT_SEEN = set()
    
    try:
        profile = form_data or temp_user_profile()
        print(f"\n{'='*60}\n🌐 Navigating to: {site_url}\n{'='*60}")
        driver.get(site_url)
        time.sleep(5)
        
        # Handle landing page
        handle_landing_page(driver, profile)
        time.sleep(2)
        
        # Fill form steps
        step = 1
        max_steps = 30
        
        while step <= max_steps:
            print(f"\n--- STEP {step} ---")
            
            if not fill_current_step(driver, profile):
                print(f"  ⏹ No more steps or reached final page")
                break
            
            step += 1
            time.sleep(1.5)
        
        print(f"\n✅ Form process completed ({step-1} steps)")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        traceback.print_exc()
        return False

# ================================================================
#  12. MULTI-SITE RUNNER
# ================================================================
def run_quote_comparison(sites: List[str] = None):
    """Run form filling across multiple insurance sites"""
    
    if not sites:
        sites = [
            "https://www.bindright.com/",
            # 'https://www.statefarm.com/'
            # 'https://smartchoice.pk/'
            # Add more sites as needed
        ]
    
    driver = create_browser(headless=False)
    click_cookie_accept(driver)
    print('Accepted cookies',driver)
    profile = temp_user_profile()
    
    results = []
    
    for site_url in sites:
        try:
            success = fill_form(driver, site_url, profile)
            
            # Take screenshot
            screenshot_path = f"data/screenshot_{len(results)+1}.png"
            os.makedirs("data", exist_ok=True)
            driver.save_screenshot(screenshot_path)
            
            result = {
                "site": site_url,
                "status": "success" if success else "failed",
                "screenshot": screenshot_path,
                "final_url": driver.current_url
            }
            
            results.append(result)
            print(f"\n{'='*60}\n✅ Completed: {site_url}\n{'='*60}")
            
            time.sleep(10)  # View results
            
        except Exception as e:
            print(f"\n❌ Failed {site_url}: {e}")
            results.append({
                "site": site_url,
                "status": "error",
                "error": str(e)
            })
    
    driver.quit()
    
    # Save results
    with open("data/results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}\n📊 FINAL SUMMARY\n{'='*60}")
    print(json.dumps(results, indent=2))
    print(f"\n✅ Processed {len(results)} sites")
    
    return results

# ================================================================
#  13. ENTRY POINT
# ================================================================
if __name__ == "__main__":
    # Test with single site
    # driver = create_browser(headless=False)
    # fill_form(driver, "https://www.theunitedinsurance.com/")
    # time.sleep(30)
    # driver.quit()
    
    # Or run multiple sites
    run_quote_comparison()







    


# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from langchain_community.document_loaders import SeleniumURLLoader
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support import expected_conditions as EC

# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import time
# from selenium.webdriver.support.ui import WebDriverWait,Select



# def web_driver(url,headless=False):

#     options=Options()
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
#     driver.get(url)
#     return driver



# desired_selection={
#     'make':'Suzuki',
#     'model':'Alto X',
#     'year':'2020',
# }



# def handle_clikcable_options(url):

#     driver=web_driver(url)

#     WebDriverWait(driver, 15).until(
#         EC.presence_of_element_located((By.TAG_NAME, "body"))
#     )

#     try:
#         for key,value in desired_selection.items():
#             print(f"Looking for {key} select elements...")
#             selectors = [
#                     f"//select[contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{key.lower()}')]",
#                     f"//select[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{key.lower()}')]",
#                     f"//select[contains(@class, '{key.lower()}')]",
#                     f"//select[contains(@placeholder, '{key}')]",
#                     "//select"  # Get all selects as fallback
#                 ]
#             select_elements = []
#             for selector in selectors:
#                 elements = driver.find_elements(By.XPATH, selector)
#                 if elements:
#                     select_elements = elements
#                     print(f"Found {len(elements)} select elements with selector: {selector}")
#                     break
#             for sel in select_elements:
#                 try:
#                     if sel.is_displayed() and sel.is_enabled():
#                         select = Select(sel)
                        
#                         # Print available options for debugging
#                         options = [opt.text for opt in select.options]
#                         print(f"Available options: {options}")
                        
#                         # Try exact match first, then partial match
#                         try:
#                             select.select_by_visible_text(value)
#                             print(f"Selected '{value}' for {key}")
#                             time.sleep(1)
#                             break
#                         except:
#                             print('Not results')
#                 except:
#                     print('Code didnt executed')
#     except:     
#         print('Not found')

#     try:
#         forms=driver.find_elements(By.TAG_NAME,'input')    
#         for form in forms:
#             if form:

#                 form.get_attribute('type')
#                 form.send_keys('10003')
#         clickable_options=[
#             "button",          
#             ".button",       
#             "div button",      
#             "div[role='button']",
#             "[onclick]",  
#         ]
#     except:
#         print('Not found')

#     try:
#         relation_urls=driver.find_elements(By.XPATH,f"//ul//div[@class='text']/ancestor::a")
#         for rel in relation_urls:
#             text=rel.text.lower().strip()
#             if 'car' in text:
#                 rel.click()
#     except:
#         print('No found')
        
#     try:
#         for clickable in clickable_options:
#             elements=driver.find_elements(By.CSS_SELECTOR,clickable)
#             if elements:
#                 print(f'found {len(elements)} for {clickable}')

#                 for el in elements:
#                     el.click()
#                     print(f'Clicked element {el.tag_name}')
#     except:
#         print('Not Found')
  
#     return 



# # def handle_clikcable_options(url):
# #     driver = web_driver(url)

# #     WebDriverWait(driver, 15).until(
# #         EC.presence_of_element_located((By.TAG_NAME, "body"))
# #     )
    
# #     time.sleep(3)  # Allow page to fully load

# #     # Try multiple strategies to find select elements
# #     try:
# #         for key, value in desired_selection.items():
# #             print(f"Looking for {key} select elements...")
            
# #             # Multiple XPath strategies
# #             selectors = [
# #                 f"//select[contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{key.lower()}')]",
# #                 f"//select[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{key.lower()}')]",
# #                 f"//select[contains(@class, '{key.lower()}')]",
# #                 f"//select[contains(@placeholder, '{key}')]",
# #                 "//select"  # Get all selects as fallback
# #             ]
            
# #             select_elements = []
# #             for selector in selectors:
# #                 elements = driver.find_elements(By.XPATH, selector)
# #                 if elements:
# #                     select_elements = elements
# #                     print(f"Found {len(elements)} select elements with selector: {selector}")
# #                     break
            
# #             if not select_elements:
# #                 print(f'No select elements found for {key}')
# #                 continue
                
# #             for sel in select_elements:
# #                 try:
# #                     if sel.is_displayed() and sel.is_enabled():
# #                         select = Select(sel)
                        
# #                         # Print available options for debugging
# #                         options = [opt.text for opt in select.options]
# #                         print(f"Available options: {options}")
                        
# #                         # Try exact match first, then partial match
# #                         try:
# #                             select.select_by_visible_text(value)
# #                             print(f"Selected '{value}' for {key}")
# #                             time.sleep(1)
# #                             break
# #                         except:
# #                             # Try partial match
# #                             for option in select.options:
# #                                 if value.lower() in option.text.lower():
# #                                     select.select_by_visible_text(option.text)
# #                                     print(f"Selected '{option.text}' (partial match) for {key}")
# #                                     time.sleep(1)
# #                                     break
# #                 except Exception as e:
# #                     print(f"Error with select element: {e}")
                    
# #     except Exception as e:
# #         print(f'Error finding select elements: {e}')

# #     # Handle input fields
# #     try:
# #         input_elements = driver.find_elements(By.TAG_NAME, 'input')
# #         print(f"Found {len(input_elements)} input elements")
        
# #         for form in input_elements:
# #             if form.is_displayed() and form.is_enabled():
# #                 input_type = form.get_attribute('type')
# #                 placeholder = form.get_attribute('placeholder') or ""
# #                 name = form.get_attribute('name') or ""
                
# #                 print(f"Input type: {input_type}, placeholder: {placeholder}, name: {name}")
                
# #                 # Handle different input types
# #                 if input_type in ['text', 'number'] and any(keyword in (placeholder + name).lower() 
# #                                                           for keyword in ['phone', 'mobile', 'contact']):
# #                     form.clear()
# #                     form.send_keys('03001234567')
# #                     print("Entered phone number")
# #                 elif input_type in ['text', 'number'] and 'engine' in (placeholder + name).lower():
# #                     form.clear()
# #                     form.send_keys('1000')
# #                     print("Entered engine capacity")
                    
# #         time.sleep(2)
# #     except Exception as e:
# #         print(f'Error with input fields: {e}')

# #     # Handle clickable elements for car insurance
# #     try:
# #         # Look for car insurance related links/buttons
# #         car_related_selectors = [
# #             "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'car')]",
# #             "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'car')]",
# #             "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'vehicle')]",
# #             "//a[contains(@href, 'car') or contains(@href, 'vehicle')]"
# #         ]
        
# #         for selector in car_related_selectors:
# #             elements = driver.find_elements(By.XPATH, selector)
# #             if elements:
# #                 print(f"Found {len(elements)} car-related elements")
# #                 for el in elements:
# #                     if el.is_displayed() and el.is_enabled():
# #                         print(f"Clicking: {el.text}")
# #                         driver.execute_script("arguments[0].click();", el)
# #                         time.sleep(2)
# #                         break
# #                 break
                        
# #     except Exception as e:
# #         print(f'Error with car-related elements: {e}')

# #     # Handle general buttons
# #     try:
# #         clickable_selectors = [
# #             "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'get') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'quote')]",
# #             "//button[@type='submit']",
# #             "//input[@type='submit']"
# #         ]
        
# #         for selector in clickable_selectors:
# #             elements = driver.find_elements(By.XPATH, selector)
# #             if elements:
# #                 print(f"Found {len(elements)} clickable elements with selector")
# #                 for el in elements:
# #                     if el.is_displayed() and el.is_enabled():
# #                         print(f"Clicking button: {el.text or el.get_attribute('value')}")
# #                         driver.execute_script("arguments[0].click();", el)
# #                         time.sleep(3)
# #                         break
# #                 break
                        
# #     except Exception as e:
# #         print(f'Error with buttons: {e}')
    
# #     # Wait to see results
# #     time.sleep(10)
    
# #     # Take screenshot for debugging
# #     # try:
# #     #     driver.save_screenshot(f"debug_screenshot_{int(time.time())}.png")
# #     #     print("Screenshot saved")
# #     # except:
# #     #     pass
    
# #     driver.quit()
# #     return

    
            


# # # # handle_clikcable_options('https://www.bindright.com/')
# # # handle_clikcable_options('https://smartchoice.pk/')





# # def handle_clikcable_options(url):
# #     driver = web_driver(url)

# #     WebDriverWait(driver, 15).until(
# #         EC.presence_of_element_located((By.TAG_NAME, "body"))
# #     )
    
# #     time.sleep(5)  # Increased wait time

# #     # First, let's see what's actually on the page
# #     print("=== PAGE ANALYSIS ===")
# #     try:
# #         # Get all form elements
# #         all_selects = driver.find_elements(By.TAG_NAME, 'select')
# #         all_inputs = driver.find_elements(By.TAG_NAME, 'input')
# #         all_buttons = driver.find_elements(By.TAG_NAME, 'button')
        
# #         print(f"Total selects on page: {len(all_selects)}")
# #         print(f"Total inputs on page: {len(all_inputs)}")
# #         print(f"Total buttons on page: {len(all_buttons)}")
        
# #         # Debug select elements
# #         for i, sel in enumerate(all_selects):
# #             try:
# #                 id_attr = sel.get_attribute('id') or 'N/A'
# #                 name_attr = sel.get_attribute('name') or 'N/A'
# #                 class_attr = sel.get_attribute('class') or 'N/A'
# #                 print(f"Select {i}: id='{id_attr}', name='{name_attr}', class='{class_attr}'")
                
# #                 if sel.is_displayed():
# #                     select_obj = Select(sel)
# #                     options = [opt.text.strip() for opt in select_obj.options if opt.text.strip()]
# #                     print(f"  Options: {options[:5]}...")  # Show first 5 options
                    
# #             except Exception as e:
# #                 print(f"  Error analyzing select {i}: {e}")
        
# #         # Debug input elements
# #         for i, inp in enumerate(all_inputs):
# #             try:
# #                 input_type = inp.get_attribute('type') or 'text'
# #                 id_attr = inp.get_attribute('id') or 'N/A'
# #                 name_attr = inp.get_attribute('name') or 'N/A'
# #                 placeholder = inp.get_attribute('placeholder') or 'N/A'
# #                 if inp.is_displayed():
# #                     print(f"Input {i}: type='{input_type}', id='{id_attr}', name='{name_attr}', placeholder='{placeholder}'")
# #             except Exception as e:
# #                 print(f"  Error analyzing input {i}: {e}")
                
# #     except Exception as e:
# #         print(f"Error in page analysis: {e}")

# #     # Handle car-related clicking first (as this might load the form)
# #     print("\n=== CLICKING CAR-RELATED ELEMENTS ===")
# #     try:
# #         car_related_selectors = [
# #             "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'car')]",
# #             "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'car')]",
# #             "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'vehicle')]",
# #             "//a[contains(@href, 'car') or contains(@href, 'vehicle')]"
# #         ]
        
# #         clicked = False
# #         for selector in car_related_selectors:
# #             if clicked:
# #                 break
# #             elements = driver.find_elements(By.XPATH, selector)
# #             if elements:
# #                 print(f"Found {len(elements)} car-related elements")
# #                 for el in elements:
# #                     if el.is_displayed() and el.is_enabled():
# #                         print(f"Clicking: '{el.text.strip()}'")
# #                         driver.execute_script("arguments[0].click();", el)
# #                         time.sleep(3)  # Wait for page to load
# #                         clicked = True
# #                         break
                        
# #         if clicked:
# #             print("Waiting for new content to load...")
# #             time.sleep(5)
            
# #     except Exception as e:
# #         print(f'Error with car-related elements: {e}')

# #     # Now try to find form elements again after clicking
# #     print("\n=== FORM FILLING AFTER CLICK ===")
# #     try:
# #         for key, value in desired_selection.items():
# #             print(f"\nLooking for {key} select elements...")
            
# #             # More comprehensive selectors
# #             selectors = [
# #                 f"//select[contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{key.lower()}')]",
# #                 f"//select[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{key.lower()}')]",
# #                 f"//select[contains(@class, '{key.lower()}')]",
# #                 f"//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{key.lower()}')]/following-sibling::select",
# #                 f"//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{key.lower()}')]/..//select",
# #                 "//select"  # Get all selects as fallback
# #             ]
            
# #             select_elements = []
# #             for selector in selectors:
# #                 elements = driver.find_elements(By.XPATH, selector)
# #                 if elements:
# #                     select_elements = elements
# #                     print(f"Found {len(elements)} select elements with selector: {selector}")
# #                     break
            
# #             if not select_elements:
# #                 print(f'No select elements found for {key}')
# #                 continue
                
# #             for sel in select_elements:
# #                 try:
# #                     if sel.is_displayed() and sel.is_enabled():
# #                         select = Select(sel)
                        
# #                         # Print available options for debugging
# #                         options = [opt.text.strip() for opt in select.options]
# #                         print(f"Available options: {options}")
                        
# #                         # Try different matching strategies
# #                         found_match = False
                        
# #                         # Exact match
# #                         try:
# #                             select.select_by_visible_text(value)
# #                             print(f"Selected '{value}' for {key} (exact match)")
# #                             time.sleep(1)
# #                             found_match = True
# #                             break
# #                         except:
# #                             pass
                            
# #                         # Partial match
# #                         if not found_match:
# #                             for option in select.options:
# #                                 option_text = option.text.strip()
# #                                 if value.lower() in option_text.lower():
# #                                     select.select_by_visible_text(option_text)
# #                                     print(f"Selected '{option_text}' (partial match) for {key}")
# #                                     time.sleep(1)
# #                                     found_match = True
# #                                     break
                        
# #                         # Value-based selection
# #                         if not found_match:
# #                             try:
# #                                 select.select_by_value(value.lower())
# #                                 print(f"Selected by value '{value.lower()}' for {key}")
# #                                 found_match = True
# #                             except:
# #                                 pass
                                
# #                         if found_match:
# #                             break
                            
# #                 except Exception as e:
# #                     print(f"Error with select element: {e}")
                    
# #     except Exception as e:
# #         print(f'Error finding select elements: {e}')

# #     # Handle input fields with better detection
# #     print("\n=== INPUT FIELD HANDLING ===")
# #     try:
# #         input_elements = driver.find_elements(By.TAG_NAME, 'input')
# #         print(f"Found {len(input_elements)} input elements")
        
# #         for i, form in enumerate(input_elements):
# #             if form.is_displayed() and form.is_enabled():
# #                 input_type = form.get_attribute('type') or 'text'
# #                 placeholder = (form.get_attribute('placeholder') or "").lower()
# #                 name = (form.get_attribute('name') or "").lower()
# #                 id_attr = (form.get_attribute('id') or "").lower()
                
# #                 print(f"Input {i}: type='{input_type}', placeholder='{placeholder}', name='{name}', id='{id_attr}'")
                
# #                 # Handle different input types
# #                 if input_type in ['text', 'tel', 'number']:
# #                     if any(keyword in (placeholder + name + id_attr) for keyword in ['phone', 'mobile', 'contact', 'cell']):
# #                         form.clear()
# #                         form.send_keys('03001234567')
# #                         print("  → Entered phone number")
# #                     elif any(keyword in (placeholder + name + id_attr) for keyword in ['engine', 'cc', 'capacity']):
# #                         form.clear()
# #                         form.send_keys('1000')
# #                         print("  → Entered engine capacity")
# #                     elif any(keyword in (placeholder + name + id_attr) for keyword in ['name', 'first', 'last']):
# #                         form.clear()
# #                         form.send_keys('John Doe')
# #                         print("  → Entered name")
# #                     elif any(keyword in (placeholder + name + id_attr) for keyword in ['email']):
# #                         form.clear()
# #                         form.send_keys('test@example.com')
# #                         print("  → Entered email")
                        
# #         time.sleep(2)
# #     except Exception as e:
# #         print(f'Error with input fields: {e}')

# #     # Handle submit buttons
# #     print("\n=== BUTTON CLICKING ===")
# #     try:
# #         clickable_selectors = [
# #             "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'get') and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'quote')]",
# #             "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]",
# #             "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]",
# #             "//button[@type='submit']",
# #             "//input[@type='submit']"
# #         ]
        
# #         for selector in clickable_selectors:
# #             elements = driver.find_elements(By.XPATH, selector)
# #             if elements:
# #                 print(f"Found {len(elements)} clickable elements with selector")
# #                 for el in elements:
# #                     if el.is_displayed() and el.is_enabled():
# #                         button_text = el.text or el.get_attribute('value') or 'unnamed button'
# #                         print(f"Clicking button: '{button_text}'")
# #                         driver.execute_script("arguments[0].click();", el)
# #                         time.sleep(3)
# #                         break
# #                 break
                        
# #     except Exception as e:
# #         print(f'Error with buttons: {e}')
    
# #     # Wait to see results
# #     print("\n=== FINAL WAIT ===")
# #     time.sleep(10)
    
# #     print(f"Final URL: {driver.current_url}")
    
# #     driver.quit()
# #     return


# # handle_clikcable_options('https://smartchoice.pk/')
# handle_clikcable_options('https://www.bindright.com/')