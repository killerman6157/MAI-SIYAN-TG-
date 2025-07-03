"""
Utility functions
"""

import re
import logging

logger = logging.getLogger(__name__)

def is_valid_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    # Remove spaces and special characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Check if it's a valid international format
    if re.match(r'^\+\d{10,15}$', cleaned):
        return True
    
    # Check if it's a Nigerian number without +
    if re.match(r'^(\d{11}|234\d{10})$', cleaned):
        return True
        
    return False

def format_phone_number(phone: str) -> str:
    """Format phone number to international format"""
    # Remove spaces and special characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # If it starts with +, return as is
    if cleaned.startswith('+'):
        return cleaned
    
    # If it's 11 digits starting with 0, replace 0 with +234
    if len(cleaned) == 11 and cleaned.startswith('0'):
        return '+234' + cleaned[1:]
    
    # If it's 10 digits, add +234
    if len(cleaned) == 10:
        return '+234' + cleaned
    
    # If it starts with 234, add +
    if cleaned.startswith('234') and len(cleaned) == 13:
        return '+' + cleaned
    
    # Return as is if no pattern matches
    return cleaned

def validate_otp(otp: str) -> bool:
    """Validate OTP format"""
    return bool(re.match(r'^\d{5}$', otp.strip()))

def extract_country_from_phone(phone: str) -> str:
    """Extract country from phone number"""
    # Simple country mapping based on country code
    country_codes = {
        '+234': 'Nigeria',
        '+1': 'United States',
        '+44': 'United Kingdom',
        '+91': 'India',
        # Add more as needed
    }
    
    for code, country in country_codes.items():
        if phone.startswith(code):
            return country
    
    return 'Unknown'
