"""
Fonctions utilitaires communes
"""
import re
import hashlib
import secrets
import string
import mimetypes
import os
from datetime import datetime, timedelta
from typing import Optional, Union, List, Dict, Any
from urllib.parse import urlparse
from html import unescape
from html.parser import HTMLParser
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.conf import settings
import requests
import phonenumbers
from phonenumbers import NumberParseException


class HTMLStripper(HTMLParser):
    """Parser HTML pour supprimer les balises"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    
    def handle_data(self, d):
        self.fed.append(d)
    
    def get_data(self):
        return ''.join(self.fed)


def generate_random_string(length: int = 32, include_symbols: bool = False) -> str:
    """
    Génère une chaîne aléatoire
    
    Args:
        length: Longueur de la chaîne
        include_symbols: Inclure les symboles
    
    Returns:
        Chaîne aléatoire
    """
    characters = string.ascii_letters + string.digits
    if include_symbols:
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_slug(text: str, max_length: int = 50) -> str:
    """
    Génère un slug à partir d'un texte
    
    Args:
        text: Texte à convertir
        max_length: Longueur maximale
    
    Returns:
        Slug généré
    """
    slug = slugify(text)
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    return slug


def format_file_size(size_bytes: int) -> str:
    """
    Formate la taille d'un fichier en unités lisibles
    
    Args:
        size_bytes: Taille en octets
    
    Returns:
        Taille formatée
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def format_duration(seconds: Union[int, float]) -> str:
    """
    Formate une durée en secondes en format lisible
    
    Args:
        seconds: Durée en secondes
    
    Returns:
        Durée formatée
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
    else:
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        return f"{days}j {hours}h"


def get_client_ip(request) -> str:
    """
    Récupère l'adresse IP du client
    
    Args:
        request: Requête Django
    
    Returns:
        Adresse IP
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request) -> str:
    """
    Récupère le User-Agent du client
    
    Args:
        request: Requête Django
    
    Returns:
        User-Agent
    """
    return request.META.get('HTTP_USER_AGENT', '')


def is_valid_email(email: str) -> bool:
    """
    Vérifie si un email est valide
    
    Args:
        email: Adresse email
    
    Returns:
        True si valide
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone: str, country_code: str = 'FR') -> bool:
    """
    Vérifie si un numéro de téléphone est valide
    
    Args:
        phone: Numéro de téléphone
        country_code: Code pays
    
    Returns:
        True si valide
    """
    try:
        parsed_phone = phonenumbers.parse(phone, country_code)
        return phonenumbers.is_valid_number(parsed_phone)
    except NumberParseException:
        return False


def clean_html(html_content: str) -> str:
    """
    Nettoie le contenu HTML en supprimant les balises
    
    Args:
        html_content: Contenu HTML
    
    Returns:
        Texte nettoyé
    """
    stripper = HTMLStripper()
    stripper.feed(html_content)
    return stripper.get_data().strip()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Tronque un texte à une longueur maximale
    
    Args:
        text: Texte à tronquer
        max_length: Longueur maximale
        suffix: Suffixe à ajouter
    
    Returns:
        Texte tronqué
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def convert_to_snake_case(text: str) -> str:
    """
    Convertit un texte en snake_case
    
    Args:
        text: Texte à convertir
    
    Returns:
        Texte en snake_case
    """
    # Insère un underscore avant les majuscules
    text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    # Insère un underscore avant les majuscules suivies de minuscules
    text = re.sub('([a-z0-9])([A-Z])', r'\1_\2', text)
    return text.lower()


def convert_to_camel_case(text: str) -> str:
    """
    Convertit un texte en camelCase
    
    Args:
        text: Texte à convertir
    
    Returns:
        Texte en camelCase
    """
    components = text.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])


def get_file_extension(filename: str) -> str:
    """
    Récupère l'extension d'un fichier
    
    Args:
        filename: Nom du fichier
    
    Returns:
        Extension du fichier
    """
    return os.path.splitext(filename)[1].lower()


def get_mime_type(filename: str) -> str:
    """
    Récupère le type MIME d'un fichier
    
    Args:
        filename: Nom du fichier
    
    Returns:
        Type MIME
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


def hash_password(password: str) -> str:
    """
    Hache un mot de passe
    
    Args:
        password: Mot de passe en clair
    
    Returns:
        Mot de passe haché
    """
    return hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000).hex()


def verify_password(password: str, hashed: str) -> bool:
    """
    Vérifie un mot de passe
    
    Args:
        password: Mot de passe en clair
        hashed: Mot de passe haché
    
    Returns:
        True si le mot de passe est correct
    """
    return hash_password(password) == hashed


def generate_otp(length: int = 6) -> str:
    """
    Génère un code OTP
    
    Args:
        length: Longueur du code
    
    Returns:
        Code OTP
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def generate_token(length: int = 32) -> str:
    """
    Génère un token aléatoire
    
    Args:
        length: Longueur du token
    
    Returns:
        Token généré
    """
    return secrets.token_urlsafe(length)


def parse_date(date_string: str, formats: List[str] = None) -> Optional[datetime]:
    """
    Parse une date depuis une chaîne
    
    Args:
        date_string: Chaîne de date
        formats: Formats à essayer
    
    Returns:
        Objet datetime ou None
    """
    if formats is None:
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y',
            '%d/%m/%Y %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
        ]
    
    for format_str in formats:
        try:
            return datetime.strptime(date_string, format_str)
        except ValueError:
            continue
    
    return None


def format_date(date_obj: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Formate une date
    
    Args:
        date_obj: Objet datetime
        format_str: Format de sortie
    
    Returns:
        Date formatée
    """
    return date_obj.strftime(format_str)


def get_timezone_offset(timezone_name: str = None) -> int:
    """
    Récupère le décalage horaire en minutes
    
    Args:
        timezone_name: Nom du timezone
    
    Returns:
        Décalage en minutes
    """
    if timezone_name is None:
        timezone_name = settings.TIME_ZONE
    
    tz = timezone.get_current_timezone()
    now = timezone.now()
    offset = tz.utcoffset(now)
    return int(offset.total_seconds() / 60)


def calculate_age(birth_date: datetime) -> int:
    """
    Calcule l'âge à partir d'une date de naissance
    
    Args:
        birth_date: Date de naissance
    
    Returns:
        Âge en années
    """
    today = timezone.now().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def is_business_day(date: datetime = None) -> bool:
    """
    Vérifie si une date est un jour ouvrable
    
    Args:
        date: Date à vérifier (par défaut aujourd'hui)
    
    Returns:
        True si c'est un jour ouvrable
    """
    if date is None:
        date = timezone.now()
    
    # Lundi = 0, Dimanche = 6
    return date.weekday() < 5


def get_next_business_day(date: datetime = None) -> datetime:
    """
    Récupère le prochain jour ouvrable
    
    Args:
        date: Date de départ (par défaut aujourd'hui)
    
    Returns:
        Prochain jour ouvrable
    """
    if date is None:
        date = timezone.now()
    
    next_day = date + timedelta(days=1)
    while not is_business_day(next_day):
        next_day += timedelta(days=1)
    
    return next_day


def get_previous_business_day(date: datetime = None) -> datetime:
    """
    Récupère le jour ouvrable précédent
    
    Args:
        date: Date de départ (par défaut aujourd'hui)
    
    Returns:
        Jour ouvrable précédent
    """
    if date is None:
        date = timezone.now()
    
    prev_day = date - timedelta(days=1)
    while not is_business_day(prev_day):
        prev_day -= timedelta(days=1)
    
    return prev_day


def validate_url(url: str) -> bool:
    """
    Valide une URL
    
    Args:
        url: URL à valider
    
    Returns:
        True si l'URL est valide
    """
    validator = URLValidator()
    try:
        validator(url)
        return True
    except ValidationError:
        return False


def is_valid_ip_address(ip: str) -> bool:
    """
    Vérifie si une adresse IP est valide
    
    Args:
        ip: Adresse IP
    
    Returns:
        True si l'IP est valide
    """
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Récupère les informations d'un fichier
    
    Args:
        file_path: Chemin du fichier
    
    Returns:
        Dictionnaire avec les informations
    """
    if not os.path.exists(file_path):
        return {}
    
    stat = os.stat(file_path)
    return {
        'size': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'created': datetime.fromtimestamp(stat.st_ctime),
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'extension': get_file_extension(file_path),
        'mime_type': get_mime_type(file_path),
    }


def sanitize_filename(filename: str) -> str:
    """
    Nettoie un nom de fichier
    
    Args:
        filename: Nom de fichier
    
    Returns:
        Nom de fichier nettoyé
    """
    # Supprime les caractères dangereux
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Supprime les espaces en début/fin
    filename = filename.strip()
    # Limite la longueur
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Divise une liste en chunks
    
    Args:
        lst: Liste à diviser
        chunk_size: Taille des chunks
    
    Returns:
        Liste de chunks
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusionne plusieurs dictionnaires
    
    Args:
        *dicts: Dictionnaires à fusionner
    
    Returns:
        Dictionnaire fusionné
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusionne récursivement deux dictionnaires
    
    Args:
        dict1: Premier dictionnaire
        dict2: Deuxième dictionnaire
    
    Returns:
        Dictionnaire fusionné
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    return result



