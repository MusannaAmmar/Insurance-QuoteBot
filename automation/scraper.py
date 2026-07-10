from typing import List
from selenium.webdriver.common.by import By
from automation.utils import*
import time

from selenium.webdriver.common.keys import Keys




# ================================================================
#  4. UNIVERSAL ELEMENT FINDER (Enhanced for React/MUI)
# ================================================================
def find_elements_by_keywords(driver, keywords: List[str], 
                               element_types: List[str] = None,
                               timeout: int = 5) -> List:
    """Find elements containing any keyword in text, aria-label, placeholder, etc."""
    if element_types is None:
        element_types = [
            "button", "a", "div[role='button']", "span[role='button']",
            "input", "select", "textarea",
            # Material-UI and React specific
            "button[class*='MuiButton']", "button[class*='Button']",
            "div[class*='button']", "span[class*='button']"
        ]
    
    found_elements = []
    
    for elem_type in element_types:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, elem_type)
            for elem in elements:
                if not elem.is_displayed():
                    continue
                
                # Get text from element and all children (for nested spans)
                text = elem.text.strip()
                
                # Also check inner spans/children text
                try:
                    inner_text = driver.execute_script(
                        "return arguments[0].innerText || arguments[0].textContent || '';", 
                        elem
                    ).strip()
                    text = text or inner_text
                except:
                    pass
                
                # Check attributes
                try:
                    aria_label = elem.get_attribute("aria-label") or ""
                    placeholder = elem.get_attribute("placeholder") or ""
                    title = elem.get_attribute("title") or ""
                    value = elem.get_attribute("value") or ""
                    name = elem.get_attribute("name") or ""
                    id_attr = elem.get_attribute("id") or ""
                    data_testid = elem.get_attribute("data-testid") or ""
                    
                    combined_text = f"{text} {aria_label} {placeholder} {title} {value} {name} {id_attr} {data_testid}"
                    
                    if fuzzy_match(combined_text, keywords):
                        # For buttons, prefer the actual button element over spans
                        if elem.tag_name == "span" and "button" in elem_type.lower():
                            try:
                                parent = elem.find_element(By.XPATH, "./..")
                                if parent.tag_name == "button":
                                    if parent not   in found_elements:
                                        found_elements.append(parent)
                                        print(f"    Found: button (via span) with text '{text[:30]}...'")
                                else:
                                    found_elements.append(elem)
                                    print(f"    Found: {elem_type} with text '{text[:30]}...'")
                            except:
                                found_elements.append(elem)
                        else:
                            found_elements.append(elem)
                            print(f"    Found: {elem_type} with text '{text[:30]}...'")
                except Exception as e:
                    pass
        except Exception as e:
            continue
    
    return found_elements

# ================================================================
#  5. SMART LANDING PAGE HANDLER
# ================================================================
def handle_landing_page(driver, profile: Dict) -> bool:
    """Handle initial landing page - find and click car insurance option"""
    print("\n🔍 Analyzing landing page...")
    
    # Strategy 1: Look for car/auto/motor insurance buttons
    car_keywords = [
        "car insurance", "auto insurance", "vehicle insurance", "motor insurance",
        "car", "auto", "vehicle", "motor", "drive", "driving",
    ]
    
    car_elements = find_elements_by_keywords(
        driver, car_keywords, 
        element_types=["button", "a", "div[role='button']", "span[onclick]"]
    )
    
    if car_elements:
        print(f"  ✓ Found {len(car_elements)} car insurance options")
        for elem in car_elements[:3]:  # Try first 3 matches
            try:
                elem_text = elem.text.strip()[:50]
                print(f"    Clicking: '{elem_text}...'")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", elem)
                time.sleep(3)
                
                # Check if page changed
                if driver.find_elements(By.CSS_SELECTOR, "input, select, button[type='submit']"):
                    print("  ✓ Form loaded successfully")
                    return True
            except Exception as e:
                print(f"    Failed to click: {e}")
                continue
    
    # Strategy 2: Look for quick quote forms
    print("  Checking for quick quote form...")
    quick_inputs = driver.find_elements(By.CSS_SELECTOR, 
        "input[type='text'], input[type='email'], input[type='tel'], input.MuiInputBase-input, input[class*='input']")
    
    # Filter for visible inputs
    visible_inputs = [inp for inp in quick_inputs if inp.is_displayed()]
    
    if len(visible_inputs) >= 1:  # Even 1 input might be a quick quote (like just ZIP)
        print(f"  ✓ Found quick quote form with {len(visible_inputs)} fields")
        return fill_quick_quote(driver, profile, visible_inputs)
    
    print("  ℹ No specific action needed - proceeding to main form")
    return False

def fill_quick_quote(driver, profile: Dict, inputs: List) -> bool:
    """Fill and submit a quick quote form"""
    filled = 0
    for inp in inputs:
        try:
            if not inp.is_displayed():
                continue
            
            # Scroll into view and click
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
            time.sleep(0.3)
            inp.click()
            time.sleep(0.2)
                
            name = (inp.get_attribute("name") or "").lower()
            placeholder = (inp.get_attribute("placeholder") or "").lower()
            id_attr = (inp.get_attribute("id") or "").lower()
            aria_label = (inp.get_attribute("aria-label") or "").lower()
            combined = f"{name} {placeholder} {id_attr} {aria_label}"
            
            value = None
            if any(x in combined for x in ["zip", "postal", "zipcode", "code"]):
                value = profile.get("zip")
            elif any(x in combined for x in ["email", "e-mail"]):
                value = profile.get("email")
            elif any(x in combined for x in ["phone", "tel", "mobile"]):
                value = profile.get("phone")
            elif any(x in combined for x in ["address", "street"]):
                value = profile.get("address")
            elif any(x in combined for x in ["first", "fname"]):
                value = profile.get("first_name")
            elif any(x in combined for x in ["last", "lname"]):
                value = profile.get("last_name")
            
            if value:
                # Clear and fill
                inp.clear()
                inp.send_keys(Keys.CONTROL + "a")
                inp.send_keys(Keys.BACKSPACE)
                inp.send_keys(str(value))
                
                # Trigger events for React
                driver.execute_script("""
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
                """, inp)
                
                filled += 1
                print(f"    Filled: {combined[:30]} = {value}")
                time.sleep(0.5)
        except Exception as e:
            print(f"    Error filling field: {e}")
            continue
    
    if filled > 0:
        # Give validation a moment
        time.sleep(1)
        
        # Find and click submit
        submit_keywords = ["get quote", "start", "continue", "submit", "next", "get started"]
        submit_buttons = find_elements_by_keywords(driver, submit_keywords, 
                                                   ["button", "input[type='submit']", "a[role='button']"])
        
        if submit_buttons:
            try:
                btn = submit_buttons[0]
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(0.5)
                btn.click()
                print("  ✓ Submitted quick quote")
                time.sleep(5)
                return True
            except Exception as e:
                print(f"  ✗ Failed to click submit: {e}")
                pass
    
    return False