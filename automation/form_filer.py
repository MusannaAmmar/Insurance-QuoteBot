


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
from automation.utils import*
from automation.scraper import find_elements_by_keywords,handle_landing_page

from automation.browser_driver import PAGE_FINGERPRINT_SEEN


# def fill_select_field(driver, element, profile: Dict) -> bool:
#     """Fill a select dropdown intelligently"""
#     try:
#         if not element.is_displayed() or not element.is_enabled():
#             return False
        
#         name = (element.get_attribute("name") or "").lower()
#         id_attr = (element.get_attribute("id") or "").lower()
        
#         question = f"{name} {id_attr}"
#         answer = get_answer_from_profile(question, profile)
        
#         if answer:
#             select = Select(element)
#             options = select.options
            
#             # Try to match answer with options
#             for option in options:
#                 option_text = option.text.lower().strip()
#                 option_value = (option.get_attribute("value") or "").lower()
                
#                 if answer.lower() in option_text or answer.lower() == option_value:
#                     select.select_by_visible_text(option.text)
#                     print(f"  ✓ Selected: {question[:40]}... = {option.text}")
#                     time.sleep(0.2)
#                     return True
        
#     except:
#         pass
    
#     return False


def fill_select_field(driver, element, profile: Dict) -> bool:
    """Fill a select dropdown field"""
    try:
        # Get field identifiers
        field_id = element.get_attribute('id') or ''
        field_name = element.get_attribute('name') or ''
        field_class = element.get_attribute('class') or ''
        field_text = field_id + field_name + field_class
        
        # Create Select object
        select = Select(element)
        
        # Map field to profile data
        mapped_value = None
        
        # Check specific field identifiers with more detailed matching
        if any(x in field_text.lower() for x in ['make', 'brand', 'manufacturer', 'company']):
            mapped_value = profile.get('car_make')
            print(f"    Attempting to fill make field with: {mapped_value}")
        elif any(x in field_text.lower() for x in ['model']):
            mapped_value = profile.get('car_model')
            print(f"    Attempting to fill model field with: {mapped_value}")
        elif any(x in field_text.lower() for x in ['year', 'manufacturing']):
            mapped_value = profile.get('car_year')
            print(f"    Attempting to fill year field with: {mapped_value}")
        elif any(x in field_text.lower() for x in ['current value']):
            mapped_value=profile.get('current_value_PKR')
            print(f"Attempting to fill value field with: {mapped_value}")
        
        if not mapped_value:
            print(f"    No matching value found for field: {field_text}")
            return False
            
        # Wait for options to be available
        WebDriverWait(driver, 5).until(
            lambda d: len(select.options) > 1
        )
        
        # Try exact match first
        options = select.options
        exact_match = None
        partial_match = None
        
        for option in options:
            option_text = option.text.strip()
            if not option_text:
                continue
                
            if option_text.lower() == mapped_value.lower():
                exact_match = option
                break
            elif mapped_value.lower() in option_text.lower():
                partial_match = option
                
        # Use exact match if found, otherwise use partial match
        matched_option = exact_match or partial_match
        
        if matched_option:
            try:
                # Scroll element into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)
                
                # Select the option
                select.select_by_visible_text(matched_option.text)
                
                # Trigger change event for React/modern frameworks
                driver.execute_script("""
                    var select = arguments[0];
                    var event = new Event('change', { bubbles: true });
                    select.dispatchEvent(event);
                """, element)
                
                print(f"      ✓ Selected '{matched_option.text}' for {field_name or field_id}")
                time.sleep(1)  # Wait for any dynamic updates
                return True
                
            except Exception as e:
                print(f"      Error selecting option: {e}")
                return False
                
        print(f"      No matching option found for {mapped_value}")
        return False
        
    except Exception as e:
        print(f"      Error filling select: {e}")
        return False


# ================================================================
#  7. HANDLE CLICKABLE CHOICES (Radio/Checkbox/Buttons)
# ================================================================
def handle_clickable_choices(driver, profile: Dict) -> int:
    """Handle radio buttons, checkboxes, and button-style choices"""
    print("  🔘 Handling clickable choices...")
    filled = 0
    
    # Strategy 1: Find questions with nearby clickable options
    labels = driver.find_elements(By.CSS_SELECTOR, 
        "label, legend, div[class*='question'], div[class*='Question'], div[class*='label'], h1, h2, h3, h4, p[class*='question']")
    
    for label in labels:
        try:
            if not label.is_displayed():
                continue
            
            question_text = label.text.strip()
            if len(question_text) < 3 or len(question_text) > 300:
                continue
            
            print(f"    Question: '{question_text[:60]}...'")
            answer = get_answer_from_profile(question_text, profile)
            
            if not answer:
                continue
            
            print(f"      Answer needed: '{answer}'")
            
            # Find nearby clickable elements (within same container)
            parent = label.find_element(By.XPATH, "./..")
            clickables = parent.find_elements(By.CSS_SELECTOR, 
                "input[type='radio'], input[type='checkbox'], button, div[role='button'], span[role='button'], div[role='radio']")
            
            for elem in clickables:
                try:
                    if not elem.is_displayed():
                        continue
                        
                    elem_text = elem.text.strip().lower()
                    elem_value = (elem.get_attribute("value") or "").lower()
                    elem_label = (elem.get_attribute("aria-label") or "").lower()
                    elem_class = (elem.get_attribute("class") or "").lower()
                    
                    combined = f"{elem_text} {elem_value} {elem_label} {elem_class}"
                    
                    # Match answer (more flexible matching)
                    answer_words = answer.lower().split()
                    match_found = False
                    
                    # Exact or partial match
                    if answer.lower() in combined or combined.strip() == answer.lower():
                        match_found = True
                    # Check if any word from answer is in the combined text
                    elif any(word in combined for word in answer_words if len(word) > 3):
                        match_found = True
                    # Special cases
                    elif answer.lower() == "yes" and any(x in combined for x in ["yes", "true", "covered", "insured"]):
                        match_found = True
                    elif answer.lower() == "no" and any(x in combined for x in ["no", "false", "not", "none"]):
                        match_found = True
                    # Coverage level matching (typical, highest, lower, state minimum)
                    elif "typical" in answer.lower() and "typical" in combined:
                        match_found = True
                    elif "highest" in answer.lower() and "highest" in combined:
                        match_found = True
                    elif "lower" in answer.lower() and "lower" in combined:
                        match_found = True
                    elif "minimum" in answer.lower() and "minimum" in combined:
                        match_found = True
                    
                    if match_found:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                        time.sleep(0.3)
                        driver.execute_script("arguments[0].click();", elem)
                        print(f"      ✓ Clicked: {elem_text or elem_value or elem_class}")
                        filled += 1
                        time.sleep(0.5)
                        break
                except Exception as e:
                    print(f"      Error clicking element: {e}")
                    continue
        except Exception as e:
            continue
    
    # Strategy 2: Handle standalone Yes/No buttons (no nearby question)
    # This catches cases where the question is in page title/heading but buttons are separate
    if filled == 0:
        print("    No questions matched, trying standalone Yes/No buttons...")
        
        # Get the page title/heading as the question
        page_question = ""
        try:
            headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4")
            for h in headings:
                if h.is_displayed() and h.text.strip():
                    page_question = h.text.strip()
                    break
        except:
            pass
        
        if page_question:
            print(f"    Using page heading as question: '{page_question[:60]}...'")
            answer = get_answer_from_profile(page_question, profile)
            
            if answer:
                print(f"      Answer needed: '{answer}'")
                
                # Find all buttons on page
                all_buttons = driver.find_elements(By.CSS_SELECTOR, "button, div[role='button']")
                
                for btn in all_buttons:
                    try:
                        if not btn.is_displayed():
                            continue
                        
                        btn_text = btn.text.strip().lower()
                        btn_class = (btn.get_attribute("class") or "").lower()
                        btn_aria = (btn.get_attribute("aria-label") or "").lower()
                        btn_value = (btn.get_attribute("value") or "").lower()
                        
                        combined = f"{btn_text} {btn_class} {btn_aria} {btn_value}"
                        
                        # More flexible matching
                        answer_words = answer.lower().split()
                        match_found = False
                        
                        # Exact match
                        if answer.lower() in combined or combined.strip() == answer.lower():
                            match_found = True
                        # Partial word match (for multi-word answers like "typical level")
                        elif any(word in combined for word in answer_words if len(word) > 3):
                            match_found = True
                        # Yes/No specific
                        elif answer.lower() == "yes" and any(x in combined for x in ["yes", "true"]):
                            match_found = True
                        elif answer.lower() == "no" and combined.strip() == "no":
                            match_found = True
                        # Coverage levels
                        elif "typical" in answer.lower() and "typical" in combined:
                            match_found = True
                        elif "highest" in answer.lower() and "highest" in combined:
                            match_found = True
                        elif "lower" in answer.lower() and "lower" in combined:
                            match_found = True
                        elif "minimum" in answer.lower() and "minimum" in combined:
                            match_found = True
                        
                        if match_found:
                            print(f"      ✓ Found matching button: '{btn_text}' (class: {btn_class})")
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                            time.sleep(0.5)
                            driver.execute_script("arguments[0].click();", btn)
                            print(f"      ✓ Clicked: {btn_text}")
                            filled += 1
                            time.sleep(1)
                            break
                    except Exception as e:
                        print(f"      Error: {e}")
                        continue
    
    return filled




    
    # If no interactive elements handled, continue with regular form filling
    # ... rest of existing fill_current_step code ...
# ================================================================
#  8. PAGE FINGERPRINT
# ================================================================
def get_page_fingerprint(driver) -> str:
    try:
        url = driver.current_url.split("?")[0].split("#")[0]
        title = driver.title[:100]
        
        # Get visible text from key elements
        key_text = []
        for selector in ["h1", "h2", "h3", "legend", "div[class*='step']"]:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements[:3]:
                if el.is_displayed():
                    text = el.text.strip()
                    if text:
                        key_text.append(text)
        
        return f"{url}||{title}||{' | '.join(key_text[:5])}"
    except:
        return f"ERROR||{driver.current_url}"



# ================================================================
#  10. NEXT BUTTON CLICKER (Enhanced for Material-UI/React)
# ================================================================
def debug_print_all_buttons(driver):
    """Debug helper: print all buttons found on page"""
    print("\n  🔍 DEBUG - All buttons on page:")
    all_buttons = driver.find_elements(By.CSS_SELECTOR, "button, a[role='button'], div[role='button'], input[type='submit']")
    
    for i, btn in enumerate(all_buttons[:15]):  # Show first 15
        try:
            if btn.is_displayed():
                text = btn.text.strip() or btn.get_attribute("aria-label") or btn.get_attribute("value") or "[no text]"
                classes = btn.get_attribute("class") or "[no class]"
                print(f"    [{i+1}] Text: '{text[:50]}' | Classes: '{classes[:50]}'")
        except:
            pass

def click_next_button(driver) -> bool:
    """Find and click next/continue/submit button - handles MUI, React, etc."""
    print("  🔍 Looking for Next button...")
    
    next_keywords = ["next", "continue", "proceed", "submit", "get quote", "see quote", 
                     "compare quotes", "get started", "start", "begin", "let's go"]
    
    # Strategy 1: Look for buttons with nested spans (Material-UI pattern)
    print("    Trying Material-UI pattern...")
    try:
        mui_buttons = driver.find_elements(By.CSS_SELECTOR, 
            "button span.MuiButton-label, button span[class*='button'], button span[class*='Button']")
        
        for span in mui_buttons:
            if not span.is_displayed():
                continue
            
            text = span.text.strip().lower()
            if any(keyword in text for keyword in next_keywords):
                # Click the parent button, not the span
                parent_btn = span.find_element(By.XPATH, "./..")
                print(f"  ✓ Found MUI button: '{text}'")
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", parent_btn)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", parent_btn)
                
                return wait_for_page_change(driver)
    except Exception as e:
        print(f"    MUI search failed: {e}")
    
    # Strategy 2: Standard button search
    print("    Trying standard button search...")
    buttons = find_elements_by_keywords(
        driver, next_keywords,
        element_types=["button", "input[type='submit']", "a[role='button']", 
                      "div[role='button']", "button[type='button']", "button[type='submit']"]
    )
    
    if buttons:
        for btn in buttons[:3]:  # Try first 3 matches
            try:
                btn_text = btn.text.strip()[:40]
                print(f"  ✓ Clicking: '{btn_text}...'")
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", btn)
                
                return wait_for_page_change(driver)
                    
            except Exception as e:
                print(f"  ✗ Click failed: {e}")
                continue
    
    # Strategy 3: XPath search for common button patterns
    print("    Trying XPath patterns...")
    xpath_patterns = [
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'get started')]",
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]",
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'continue')]",
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]",
        "//span[contains(@class, 'Button-label') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'next')]/parent::button",
        "//span[contains(@class, 'Button-label') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'get started')]/parent::button",
    ]
    
    for xpath in xpath_patterns:
        try:
            btn = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            if btn and btn.is_displayed():
                print(f"  ✓ Found via XPath: '{btn.text.strip()[:40]}...'")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", btn)
                return wait_for_page_change(driver)
        except:
            continue
    
    # If still not found, print debug info
    print("  ⚠ No Next button found with any strategy")
    debug_print_all_buttons(driver)
    
    return False

def wait_for_page_change(driver, timeout: int = 10) -> bool:
    """Wait for page to change after clicking a button"""
    old_fp = get_page_fingerprint(driver)
    time.sleep(2)  # Initial wait for any immediate changes
    
    try:
        # Wait for page fingerprint to change
        WebDriverWait(driver, timeout).until(
            lambda d: get_page_fingerprint(d) != old_fp
        )
        print("  ✓ Page advanced")
        return True
    except TimeoutException:
        # Check if we're on results/quotes page
        page_source = driver.page_source.lower()
        if any(keyword in page_source for keyword in ["quote", "price", "premium", "$/month", "$/mo", "per month"]):
            print("  ✓ Reached quotes page")
            return False
        
        # Check if URL changed
        if driver.current_url != old_fp.split("||")[0]:
            print("  ✓ URL changed - page advanced")
            return True
        
        print("  ⚠ Page may not have changed")
        return False






def fill_input_field(driver, element, profile: Dict) -> bool:
    """Fill a single input field intelligently"""
    try:
        if not element.is_displayed() or not element.is_enabled():
            return False
        
        # Get all identifying attributes
        name = (element.get_attribute("name") or "").lower()
        placeholder = (element.get_attribute("placeholder") or "").lower()
        id_attr = (element.get_attribute("id") or "").lower()
        aria_label = (element.get_attribute("aria-label") or "").lower()
        input_type = (element.get_attribute("type") or "text").lower()
        class_attr = (element.get_attribute("class") or "").lower()
        
        # Find associated label
        label_text = ""
        try:
            # Try finding label by 'for' attribute
            if id_attr:
                label_for = driver.find_elements(By.CSS_SELECTOR, f"label[for='{id_attr}']")
                if label_for:
                    label_text = label_for[0].text.lower()
            
            # Try finding parent label
            if not label_text:
                parent = element.find_element(By.XPATH, "./..")
                if parent.tag_name == "label":
                    label_text = parent.text.lower()
                else:
                    # Look for nearby label (within grandparent)
                    grandparent = parent.find_element(By.XPATH, "./..")
                    nearby_labels = grandparent.find_elements(By.TAG_NAME, "label")
                    if nearby_labels:
                        label_text = nearby_labels[0].text.lower()
        except:
            pass
        
        # Combine all text for matching
        question = f"{label_text} {name} {placeholder} {aria_label} {id_attr} {class_attr}"
        
        print(f"      Analyzing: '{question[:60]}...'")
        
        # Get answer from profile
        answer = get_answer_from_profile(question, profile)
        
        if answer:
            try:
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.3)
                
                # Click to focus
                try:
                    element.click()
                except:
                    driver.execute_script("arguments[0].click();", element)
                time.sleep(0.2)
                
                # Clear existing value (try multiple methods)
                try:
                    element.clear()
                except:
                    pass
                    
                try:
                    element.send_keys(Keys.CONTROL + "a")
                    element.send_keys(Keys.BACKSPACE)
                except:
                    pass
                
                # Enter new value
                element.send_keys(str(answer))
                time.sleep(0.2)
                
                # Trigger change events (critical for React/Material-UI)
                driver.execute_script("""
                    var element = arguments[0];
                    var value = arguments[1];
                    
                    // Set the value directly
                    element.value = value;
                    
                    // Create and dispatch events
                    var inputEvent = new Event('input', { bubbles: true, cancelable: true });
                    var changeEvent = new Event('change', { bubbles: true, cancelable: true });
                    var blurEvent = new Event('blur', { bubbles: true, cancelable: true });
                    
                    element.dispatchEvent(inputEvent);
                    element.dispatchEvent(changeEvent);
                    
                    // For React, also dispatch the React synthetic event
                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(element, value);
                    
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    element.dispatchEvent(blurEvent);
                """, element, str(answer))
                
                time.sleep(0.3)
                
                # Verify value was set
                current_value = element.get_attribute("value") or ""
                if current_value == str(answer) or current_value:
                    print(f"  ✓ Filled: {question[:40]}... = {answer} (verified: {current_value})")
                    return True
                else:
                    print(f"  ⚠ Filled but verification failed: {question[:40]}... = {answer}")
                    # Still return True as sometimes React doesn't update the DOM attribute
                    return True
                    
            except Exception as e:
                print(f"  ✗ Failed to fill {question[:40]}...: {e}")
                return False
    except Exception as e:
        return False
    
    return False








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
#  9. MAIN STEP FILLER
# ================================================================
def fill_current_step(driver, profile: Dict) -> bool:
    global PAGE_FINGERPRINT_SEEN
    
    fp = get_page_fingerprint(driver)
    if fp in PAGE_FINGERPRINT_SEEN:
        print("  ⏭ Page already processed")
        return False
    
    PAGE_FINGERPRINT_SEEN.add(fp)
    print(f"\n📝 Filling step: {fp.split('||')[-1][:80]}...")
    
    filled_count = 0

    if handle_clickable_choices(driver, profile):
        return True
    
    # Wait a moment for page to fully load
    time.sleep(1)
    
    # 1. Fill text inputs (most important - do this first and thoroughly)
    print("  📝 Filling text inputs...")
    
    # Cast a wider net - find ALL input fields that might need filling
    all_input_selectors = [
        "input[type='text']",
        "input[type='email']", 
        "input[type='tel']",
        "input[type='number']",
        "input[type='search']",
        "input:not([type='hidden']):not([type='submit']):not([type='button']):not([type='radio']):not([type='checkbox'])",
        "input.MuiInputBase-input",  # Material-UI specific
        "input[class*='input']",      # Any input-related class
        "textarea"
    ]
    
    inputs = []
    for selector in all_input_selectors:
        try:
            found = driver.find_elements(By.CSS_SELECTOR, selector)
            for inp in found:
                if inp not in inputs:  # Avoid duplicates
                    inputs.append(inp)
        except:
            continue
    
    print(f"    Found {len(inputs)} input fields")
    for i, inp in enumerate(inputs):
        try:
            # Debug: show what we're trying to fill
            input_type = inp.get_attribute("type") or "unknown"
            input_class = inp.get_attribute("class") or ""
            input_name = inp.get_attribute("name") or ""
            print(f"      [{i+1}] Type: {input_type}, Name: {input_name[:20]}, Class: {input_class[:40]}")
            
            if fill_input_field(driver, inp, profile):
                filled_count += 1
        except Exception as e:
            print(f"      Error processing input {i+1}: {e}")
            continue
    
    # 2. Fill select dropdowns
    print("  📋 Filling select dropdowns...")
    # selects = driver.find_elements(By.CSS_SELECTOR, "select")
    # print(f"    Found {len(selects)} select fields")
    # for sel in selects:
    #     if fill_select_field(driver, sel, profile):
    #         filled_count += 1
    print("  📋 Filling select dropdowns...")
    selects = driver.find_elements(By.CSS_SELECTOR, "select")
    print(f"    Found {len(selects)} select fields")
    
    # Process all select fields
    for select in selects:
        try:
            if select.is_displayed() and select.is_enabled():
                fill_select_field(driver, select, profile)
                time.sleep(0.5)  # Add small delay between fields
        except Exception as e:
            print(f"    Error processing select field: {e}")
            continue
    
    # 3. Handle clickable choices (radio/checkbox/buttons)
    filled_count += handle_clickable_choices(driver, profile)
    
    print(f"  ✅ Filled {filled_count} fields on this step")
    
    # If we filled choices (like Yes/No), wait a bit longer for page to advance
    if filled_count > 0:
        print("  ⏳ Waiting for potential auto-advance...")
        time.sleep(2)
        
        # Check if page auto-advanced after clicking Yes/No
        new_fp = get_page_fingerprint(driver)
        if new_fp != fp:
            print("  ✓ Page auto-advanced after selection")
            return True
    
    # Give a moment for any validation
    time.sleep(1)
    
    # 4. Click Next/Continue button
    return click_next_button(driver)






