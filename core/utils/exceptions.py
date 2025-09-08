"""
Exceptions personnalisées pour l'application Core
"""
from django.core.exceptions import ValidationError as DjangoValidationError


class CoreException(Exception):
    """Exception de base pour l'application Core"""
    pass


class ValidationError(CoreException, DjangoValidationError):
    """Exception pour les erreurs de validation"""
    pass


class AuthenticationError(CoreException):
    """Exception pour les erreurs d'authentification"""
    pass


class PermissionError(CoreException):
    """Exception pour les erreurs de permissions"""
    pass


class NotFoundError(CoreException):
    """Exception pour les ressources non trouvées"""
    pass


class ConflictError(CoreException):
    """Exception pour les conflits de données"""
    pass


class RateLimitError(CoreException):
    """Exception pour les limites de taux dépassées"""
    pass


class CacheError(CoreException):
    """Exception pour les erreurs de cache"""
    pass


class ExternalServiceError(CoreException):
    """Exception pour les erreurs de services externes"""
    pass


class ConfigurationError(CoreException):
    """Exception pour les erreurs de configuration"""
    pass



