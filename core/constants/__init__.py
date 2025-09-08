"""
Constantes et enums pour l'application Core
"""
from .enums import (
    StatusChoices,
    UserRoleChoices,
    NotificationTypeChoices,
    SecurityLevelChoices,
    PermissionTypeChoices,
    FileTypeChoices,
    LanguageChoices,
    TimezoneChoices,
    CurrencyChoices,
    CountryChoices,
)

from .settings import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    CACHE_TIMEOUT,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    FILE_MAX_SIZE,
    IMAGE_MAX_DIMENSIONS,
    TOKEN_LENGTH,
    OTP_LENGTH,
    SESSION_TIMEOUT,
    PASSWORD_RESET_TIMEOUT,
    EMAIL_VERIFICATION_TIMEOUT,
)

from .messages import (
    SUCCESS_MESSAGES,
    ERROR_MESSAGES,
    WARNING_MESSAGES,
    INFO_MESSAGES,
    VALIDATION_MESSAGES,
    SECURITY_MESSAGES,
    NOTIFICATION_MESSAGES,
    PERMISSION_MESSAGES,
)

from .regex import (
    EMAIL_REGEX,
    PHONE_REGEX,
    PASSWORD_REGEX,
    USERNAME_REGEX,
    SLUG_REGEX,
    HEX_COLOR_REGEX,
    CREDIT_CARD_REGEX,
    POSTAL_CODE_REGEX,
    IBAN_REGEX,
    SWIFT_CODE_REGEX,
    TAX_ID_REGEX,
    SSN_REGEX,
    URL_REGEX,
    IP_ADDRESS_REGEX,
    UUID_REGEX,
)

__all__ = [
    # Enums
    'StatusChoices',
    'UserRoleChoices',
    'NotificationTypeChoices',
    'SecurityLevelChoices',
    'PermissionTypeChoices',
    'FileTypeChoices',
    'LanguageChoices',
    'TimezoneChoices',
    'CurrencyChoices',
    'CountryChoices',
    
    # Settings
    'DEFAULT_PAGE_SIZE',
    'MAX_PAGE_SIZE',
    'CACHE_TIMEOUT',
    'RATE_LIMIT_REQUESTS',
    'RATE_LIMIT_WINDOW',
    'PASSWORD_MIN_LENGTH',
    'PASSWORD_MAX_LENGTH',
    'USERNAME_MIN_LENGTH',
    'USERNAME_MAX_LENGTH',
    'EMAIL_MAX_LENGTH',
    'PHONE_MAX_LENGTH',
    'FILE_MAX_SIZE',
    'IMAGE_MAX_DIMENSIONS',
    'TOKEN_LENGTH',
    'OTP_LENGTH',
    'SESSION_TIMEOUT',
    'PASSWORD_RESET_TIMEOUT',
    'EMAIL_VERIFICATION_TIMEOUT',
    
    # Messages
    'SUCCESS_MESSAGES',
    'ERROR_MESSAGES',
    'WARNING_MESSAGES',
    'INFO_MESSAGES',
    'VALIDATION_MESSAGES',
    'SECURITY_MESSAGES',
    'NOTIFICATION_MESSAGES',
    'PERMISSION_MESSAGES',
    
    # Regex
    'EMAIL_REGEX',
    'PHONE_REGEX',
    'PASSWORD_REGEX',
    'USERNAME_REGEX',
    'SLUG_REGEX',
    'HEX_COLOR_REGEX',
    'CREDIT_CARD_REGEX',
    'POSTAL_CODE_REGEX',
    'IBAN_REGEX',
    'SWIFT_CODE_REGEX',
    'TAX_ID_REGEX',
    'SSN_REGEX',
    'URL_REGEX',
    'IP_ADDRESS_REGEX',
    'UUID_REGEX',
]



