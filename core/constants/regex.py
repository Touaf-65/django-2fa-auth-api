"""
Regular expressions constants for the Core application
"""
import re

# Email validation
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Phone validation
PHONE_REGEX = re.compile(r'^\+?[1-9]\d{1,14}$')

# Password validation
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

# Username validation
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9._-]{3,30}$')

# Slug validation
SLUG_REGEX = re.compile(r'^[a-z0-9-]+$')

# Hex color validation
HEX_COLOR_REGEX = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')

# Credit card validation
CREDIT_CARD_REGEX = re.compile(r'^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$')

# Postal code validation
POSTAL_CODE_REGEX = re.compile(r'^\d{5}$')  # French format

# IBAN validation
IBAN_REGEX = re.compile(r'^[A-Z]{2}\d{2}[A-Z0-9]+$')

# SWIFT code validation
SWIFT_CODE_REGEX = re.compile(r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$')

# Tax ID validation
TAX_ID_REGEX = re.compile(r'^[A-Z]{2}\d{11}$')  # French format

# SSN validation
SSN_REGEX = re.compile(r'^\d{13}$')  # French format

# URL validation
URL_REGEX = re.compile(r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$')

# IP address validation
IP_ADDRESS_REGEX = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')

# UUID validation
UUID_REGEX = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')



