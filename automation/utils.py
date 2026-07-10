
from typing import Dict , List, Optional
import re


# ================================================================
#  2. USER PROFILE
# ================================================================
def temp_user_profile(overrides: Dict = None) -> Dict:
    base = {
        "first_name": "John",
        "last_name": "Smith",
        "full_name": "John Smith",
        "gender": "male",
        "marital_status": "single",
        "married": "no",
        "dob": "01/01/1990",
        "age": "34",
        "email": "john.smith@gmail.com",
        "phone": "(212) 568-7961",
        "address": "140 E 14th St, New York, NY 10003, USA",
        "street": "14th Street",
        "city": "New York",
        "state": "NY",
        "zip": "10003",
        "zipcode": "10003",
        "postal_code": "10003",
        "education_level": "Bachelors Degree",
        "occupation": "Self Employed",
        "credit": "Good",
        "credit_score": "excellent",
        
        "car_year": "2022",
        "year": "2022",
        "car_make": "Suzuki",
        "make": "Suzuki",
        "car_model": "Boulevard",
        "model": "Boulevard",
        "ownership": "owned",
        "vehicle_use": "commute",
        "miles_per_year": "12000",
        "second_vehicle": "no",
        
        "currently_insured": "yes",
        "current_insurance": "yes",
        "coverage": "typical",  # Changed from "full" to match button text
        "coverage_level": "typical level",  # Added explicit match
        "protection_level": "typical",
        "active_license": "yes",
        "license": "yes",
        "tickets": "0",
        "violations": "no",
        "accidents": "no",
        "claims": "no",
        "dui": "no",
        "home_ownership": "own",
        "homeowner": "yes",
        "bundle_insurance": "no",
        "bundle": "no",
        "military": "no",
        'credit_rating':'Good',
        'bundle_policy':'yes',
        'served_military':'no',
        'insurance_provider':'AllState',
        'at_fault_accidents':'no',
        'car_parked':'140 E 14th St, New York, NY 10003, USA',
        'Current_Value_PKR':'200000'
    }
    if overrides:
        base.update(overrides)
    return base

# ================================================================
#  3. INTELLIGENT TEXT MATCHER
# ================================================================

def fuzzy_match(text: str, keywords: List[str], threshold: float = 0.75) -> bool:
    """Check if text contains any keyword (case-insensitive, whole word match)"""
    text_lower = text.lower().strip()
    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Use word boundaries for single words, partial match for phrases
        if ' ' in keyword_lower:
            # Multi-word phrase - use partial match
            if keyword_lower in text_lower:
                return True
        else:
            # Single word - use word boundary match
            pattern = r'\b' + re.escape(keyword_lower) + r'\b'
            if re.search(pattern, text_lower):
                return True
    return False


def get_answer_from_profile(question: str, profile: Dict) -> Optional[str]:
    """Smart mapping from question text to profile value"""
    q = question.lower().strip()
    
    # Direct field mappings
    field_keywords = {
        "zip": ["zip", "postal", "zipcode", "postal code"],
        "first_name": ["first name", "firstname", "given name"],
        "last_name": ["last name", "lastname", "surname", "family name"],
        "full_name": ["full name", "name", "your name"],
        "email": ["email", "e-mail"],
        "phone": ["phone", "telephone", "mobile", "cell"],
        "address": ["address", "street"],
        "city": ["city", "town"],
        "state": ["state", "province"],
        "dob": ["birth", "dob", "birthday", "date of birth"],
        "age": ["age", "how old"],
        "gender": ["gender", "sex"],
        "marital_status": ["marital", "married", "marital status"],
        
        "car_year": ["year", "vehicle year", "model year"],
        "car_make": ["make", "manufacturer"],
        "car_model": ["model", "vehicle model"],
        "ownership": ["own", "lease", "ownership"],
        "vehicle_use": ["use", "primary use", "drive for"],
        "miles_per_year": ["miles", "annual miles", "yearly miles"],
        
        "currently_insured": ["currently insured"],
        "coverage": ["coverage", "coverage level", "type of coverage", "level of coverage", "protection level"],
        "active_license": ["license", "driver license", "valid license", "driver's license"],
        "tickets": ["tickets", "violations", "moving violations"],
        "at_fault_accidents": ["at_fault_accidents", "fault_accident","collision", "at-fault","accidents"],
        "dui": ["dui", "dwi", "drunk driving"],
        "home_ownership": ["home", "homeowner", "own home", "rent"],
        "military": ["military", "armed forces", "veteran"],
        'second_vehicle':["second vehicle", "add another vehicle", "additional vehicle", "add a second"],
        'credit_rating':['credit_rating','rating','rate'],
        'bundle_policy':['bundle policy'],
        'served_military':['military service','served_military','militray veteran'],
        'insurance_provider':['insurance provider','service provider'],
        'education_level':['education_level','qualification','degree','education'],
        'occupation':['occupation','occupation_level','job'],
        'car_parked':['car_parking','car_parked','parking'],
        'current_value_PKR':['price','current_price','current_value_PKR']
    }
    
    for field, keywords in field_keywords.items():
        if fuzzy_match(q, keywords) and field in profile:
            value = str(profile[field])
            print(f"    Mapped '{q[:40]}...' → {field} = '{value}'")
            return value
    
    return None