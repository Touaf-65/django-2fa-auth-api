"""
Utilitaires de sécurité
"""
import re
import hashlib
import secrets
import logging
from django.http import HttpRequest
from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_client_ip(request: HttpRequest) -> str:
    """
    Récupère l'adresse IP réelle du client
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Nettoyer l'IP
    if ip:
        ip = ip.strip()
        # Vérifier que c'est une IP valide
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip) or ':' in ip:
            return ip
    
    return '127.0.0.1'  # IP par défaut


def get_geolocation(ip_address: str) -> dict:
    """
    Récupère les informations de géolocalisation d'une IP
    Note: Implémentation simplifiée - utiliser un service réel en production
    """
    # Pour le développement, retourner des données fictives
    if ip_address.startswith('127.') or ip_address == 'localhost':
        return {
            'country': 'FR',
            'country_name': 'France',
            'city': 'Paris',
            'region': 'Île-de-France',
            'timezone': 'Europe/Paris'
        }
    
    # En production, utiliser un service comme ipapi.co, ipinfo.io, etc.
    # Exemple avec ipapi.co (nécessite une clé API)
    try:
        import requests
        # response = requests.get(f'https://ipapi.co/{ip_address}/json/')
        # if response.status_code == 200:
        #     return response.json()
        pass
    except ImportError:
        pass
    
    # Retourner des données par défaut
    return {
        'country': 'US',
        'country_name': 'United States',
        'city': 'Unknown',
        'region': 'Unknown',
        'timezone': 'UTC'
    }


def is_suspicious_request(request: HttpRequest) -> dict:
    """
    Détecte les requêtes suspectes
    """
    suspicious_indicators = []
    risk_score = 0
    
    # Vérifier les headers suspects
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    if not user_agent:
        suspicious_indicators.append('User-Agent manquant')
        risk_score += 20
    elif len(user_agent) < 10:
        suspicious_indicators.append('User-Agent suspect')
        risk_score += 10
    
    # Vérifier les tentatives de SQL injection
    query_params = request.GET.dict()
    post_data = request.POST.dict() if hasattr(request, 'POST') else {}
    
    sql_keywords = ['union', 'select', 'drop', 'delete', 'insert', 'update', 'alter', 'create']
    for key, value in {**query_params, **post_data}.items():
        value_lower = str(value).lower()
        if any(keyword in value_lower for keyword in sql_keywords):
            suspicious_indicators.append(f'Possible injection SQL dans {key}')
            risk_score += 30
    
    # Vérifier les tentatives de XSS
    xss_patterns = ['<script>', '<iframe>', 'javascript:', 'onload=', 'onerror=']
    for key, value in {**query_params, **post_data}.items():
        value_lower = str(value).lower()
        if any(pattern in value_lower for pattern in xss_patterns):
            suspicious_indicators.append(f'Possible XSS dans {key}')
            risk_score += 25
    
    # Vérifier les tentatives de path traversal
    path_traversal_patterns = ['../', '..\\', '%2e%2e%2f', '%2e%2e%5c']
    for key, value in {**query_params, **post_data}.items():
        value_lower = str(value).lower()
        if any(pattern in value_lower for pattern in path_traversal_patterns):
            suspicious_indicators.append(f'Possible path traversal dans {key}')
            risk_score += 20
    
    # Vérifier les requêtes avec des paramètres suspects
    if len(query_params) > 50:  # Trop de paramètres
        suspicious_indicators.append('Trop de paramètres de requête')
        risk_score += 15
    
    # Vérifier la taille de la requête
    content_length = request.META.get('CONTENT_LENGTH', 0)
    if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
        suspicious_indicators.append('Requête trop volumineuse')
        risk_score += 10
    
    return {
        'is_suspicious': risk_score > 50,
        'risk_score': risk_score,
        'indicators': suspicious_indicators
    }


def generate_security_token(length: int = 32) -> str:
    """
    Génère un token de sécurité aléatoire
    """
    return secrets.token_urlsafe(length)


def validate_security_token(token: str, expected_length: int = 32) -> bool:
    """
    Valide un token de sécurité
    """
    if not token or len(token) < expected_length:
        return False
    
    # Vérifier que le token ne contient que des caractères valides
    import base64
    try:
        base64.urlsafe_b64decode(token + '==')  # Ajouter padding si nécessaire
        return True
    except Exception:
        return False


def hash_sensitive_data(data: str) -> str:
    """
    Hash des données sensibles
    """
    return hashlib.sha256(data.encode()).hexdigest()


def is_valid_ip(ip_address: str) -> bool:
    """
    Vérifie si une adresse IP est valide
    """
    import ipaddress
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False


def is_private_ip(ip_address: str) -> bool:
    """
    Vérifie si une adresse IP est privée
    """
    import ipaddress
    try:
        ip = ipaddress.ip_address(ip_address)
        return ip.is_private
    except ValueError:
        return False


def sanitize_input(input_string: str) -> str:
    """
    Nettoie une chaîne d'entrée
    """
    if not input_string:
        return ''
    
    # Supprimer les caractères de contrôle
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', input_string)
    
    # Limiter la longueur
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
    
    return sanitized.strip()


def get_request_fingerprint(request: HttpRequest) -> str:
    """
    Génère une empreinte unique pour une requête
    """
    fingerprint_data = [
        get_client_ip(request),
        request.META.get('HTTP_USER_AGENT', ''),
        request.META.get('HTTP_ACCEPT_LANGUAGE', ''),
        request.META.get('HTTP_ACCEPT_ENCODING', ''),
    ]
    
    fingerprint_string = '|'.join(fingerprint_data)
    return hashlib.md5(fingerprint_string.encode()).hexdigest()


def log_security_event(event_type: str, message: str, request: HttpRequest = None, **kwargs):
    """
    Enregistre un événement de sécurité
    """
    log_data = {
        'event_type': event_type,
        'message': message,
        'timestamp': str(timezone.now()),
    }
    
    if request:
        log_data.update({
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'path': request.path,
            'method': request.method,
        })
    
    log_data.update(kwargs)
    
    logger.warning(f"Security Event: {log_data}")


def check_rate_limit(identifier: str, limit: int, window_seconds: int) -> bool:
    """
    Vérifie si un identifiant a dépassé la limite de taux
    """
    cache_key = f"rate_limit:{identifier}:{int(time.time() // window_seconds)}"
    current_count = cache.get(cache_key, 0)
    
    if current_count >= limit:
        return False
    
    cache.set(cache_key, current_count + 1, window_seconds)
    return True



