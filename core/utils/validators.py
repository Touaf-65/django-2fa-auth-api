"""
Validateurs personnalisés pour Django
"""
import re
import json
import os
from typing import Any, List, Optional, Union
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator, EmailValidator
from django.utils.translation import gettext_lazy as _
from PIL import Image
import phonenumbers
from phonenumbers import NumberParseException


def validate_email(value: str) -> None:
    """
    Valide une adresse email
    
    Args:
        value: Adresse email à valider
    
    Raises:
        ValidationError: Si l'email n'est pas valide
    """
    validator = EmailValidator()
    try:
        validator(value)
    except ValidationError:
        raise ValidationError(_('Adresse email invalide.'))


def validate_phone(value: str, country_code: str = 'FR') -> None:
    """
    Valide un numéro de téléphone
    
    Args:
        value: Numéro de téléphone à valider
        country_code: Code pays
    
    Raises:
        ValidationError: Si le numéro n'est pas valide
    """
    try:
        parsed_phone = phonenumbers.parse(value, country_code)
        if not phonenumbers.is_valid_number(parsed_phone):
            raise ValidationError(_('Numéro de téléphone invalide.'))
    except NumberParseException:
        raise ValidationError(_('Numéro de téléphone invalide.'))


def validate_password(value: str) -> None:
    """
    Valide un mot de passe
    
    Args:
        value: Mot de passe à valider
    
    Raises:
        ValidationError: Si le mot de passe n'est pas valide
    """
    if len(value) < 8:
        raise ValidationError(_('Le mot de passe doit contenir au moins 8 caractères.'))
    
    if not re.search(r'[A-Z]', value):
        raise ValidationError(_('Le mot de passe doit contenir au moins une majuscule.'))
    
    if not re.search(r'[a-z]', value):
        raise ValidationError(_('Le mot de passe doit contenir au moins une minuscule.'))
    
    if not re.search(r'\d', value):
        raise ValidationError(_('Le mot de passe doit contenir au moins un chiffre.'))
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(_('Le mot de passe doit contenir au moins un caractère spécial.'))


def validate_url(value: str) -> None:
    """
    Valide une URL
    
    Args:
        value: URL à valider
    
    Raises:
        ValidationError: Si l'URL n'est pas valide
    """
    validator = URLValidator()
    try:
        validator(value)
    except ValidationError:
        raise ValidationError(_('URL invalide.'))


def validate_ip_address(value: str) -> None:
    """
    Valide une adresse IP
    
    Args:
        value: Adresse IP à valider
    
    Raises:
        ValidationError: Si l'IP n'est pas valide
    """
    import ipaddress
    try:
        ipaddress.ip_address(value)
    except ValueError:
        raise ValidationError(_('Adresse IP invalide.'))


def validate_file_size(value, max_size_mb: int = 10) -> None:
    """
    Valide la taille d'un fichier
    
    Args:
        value: Fichier à valider
        max_size_mb: Taille maximale en MB
    
    Raises:
        ValidationError: Si le fichier est trop volumineux
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if value.size > max_size_bytes:
        raise ValidationError(_(f'Le fichier ne doit pas dépasser {max_size_mb} MB.'))


def validate_file_type(value, allowed_types: List[str]) -> None:
    """
    Valide le type d'un fichier
    
    Args:
        value: Fichier à valider
        allowed_types: Types de fichiers autorisés
    
    Raises:
        ValidationError: Si le type de fichier n'est pas autorisé
    """
    import mimetypes
    mime_type, _ = mimetypes.guess_type(value.name)
    
    if mime_type not in allowed_types:
        raise ValidationError(_(f'Type de fichier non autorisé. Types autorisés: {", ".join(allowed_types)}'))


def validate_image_dimensions(value, max_width: int = 2000, max_height: int = 2000) -> None:
    """
    Valide les dimensions d'une image
    
    Args:
        value: Image à valider
        max_width: Largeur maximale
        max_height: Hauteur maximale
    
    Raises:
        ValidationError: Si les dimensions ne sont pas valides
    """
    try:
        with Image.open(value) as img:
            width, height = img.size
            if width > max_width or height > max_height:
                raise ValidationError(_(f'Les dimensions de l\'image ne doivent pas dépasser {max_width}x{max_height} pixels.'))
    except Exception:
        raise ValidationError(_('Fichier image invalide.'))


def validate_json(value: str) -> None:
    """
    Valide une chaîne JSON
    
    Args:
        value: Chaîne JSON à valider
    
    Raises:
        ValidationError: Si le JSON n'est pas valide
    """
    try:
        json.loads(value)
    except json.JSONDecodeError:
        raise ValidationError(_('JSON invalide.'))


def validate_slug(value: str) -> None:
    """
    Valide un slug
    
    Args:
        value: Slug à valider
    
    Raises:
        ValidationError: Si le slug n'est pas valide
    """
    if not re.match(r'^[a-z0-9-]+$', value):
        raise ValidationError(_('Le slug ne peut contenir que des lettres minuscules, des chiffres et des tirets.'))
    
    if value.startswith('-') or value.endswith('-'):
        raise ValidationError(_('Le slug ne peut pas commencer ou se terminer par un tiret.'))


def validate_hex_color(value: str) -> None:
    """
    Valide une couleur hexadécimale
    
    Args:
        value: Couleur hexadécimale à valider
    
    Raises:
        ValidationError: Si la couleur n'est pas valide
    """
    if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
        raise ValidationError(_('Couleur hexadécimale invalide. Format attendu: #RRGGBB ou #RGB'))


def validate_credit_card(value: str) -> None:
    """
    Valide un numéro de carte de crédit (algorithme de Luhn)
    
    Args:
        value: Numéro de carte à valider
    
    Raises:
        ValidationError: Si le numéro de carte n'est pas valide
    """
    # Supprime les espaces et tirets
    value = re.sub(r'[\s-]', '', value)
    
    # Vérifie que ce sont uniquement des chiffres
    if not value.isdigit():
        raise ValidationError(_('Le numéro de carte ne peut contenir que des chiffres.'))
    
    # Vérifie la longueur
    if len(value) < 13 or len(value) > 19:
        raise ValidationError(_('Le numéro de carte doit contenir entre 13 et 19 chiffres.'))
    
    # Algorithme de Luhn
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10
    
    if luhn_checksum(value) != 0:
        raise ValidationError(_('Numéro de carte de crédit invalide.'))


def validate_postal_code(value: str, country_code: str = 'FR') -> None:
    """
    Valide un code postal
    
    Args:
        value: Code postal à valider
        country_code: Code pays
    
    Raises:
        ValidationError: Si le code postal n'est pas valide
    """
    patterns = {
        'FR': r'^\d{5}$',
        'US': r'^\d{5}(-\d{4})?$',
        'CA': r'^[A-Z]\d[A-Z] \d[A-Z]\d$',
        'GB': r'^[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}$',
        'DE': r'^\d{5}$',
        'IT': r'^\d{5}$',
        'ES': r'^\d{5}$',
    }
    
    pattern = patterns.get(country_code, patterns['FR'])
    if not re.match(pattern, value):
        raise ValidationError(_(f'Code postal invalide pour {country_code}.'))


def validate_iban(value: str) -> None:
    """
    Valide un numéro IBAN
    
    Args:
        value: Numéro IBAN à valider
    
    Raises:
        ValidationError: Si l'IBAN n'est pas valide
    """
    # Supprime les espaces et convertit en majuscules
    value = re.sub(r'\s', '', value.upper())
    
    # Vérifie la longueur (entre 15 et 34 caractères)
    if len(value) < 15 or len(value) > 34:
        raise ValidationError(_('IBAN invalide: longueur incorrecte.'))
    
    # Vérifie le format (2 lettres + 2 chiffres + caractères alphanumériques)
    if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]+$', value):
        raise ValidationError(_('IBAN invalide: format incorrect.'))
    
    # Algorithme de validation IBAN
    def mod_97(iban):
        iban = iban[4:] + iban[:4]  # Déplace les 4 premiers caractères à la fin
        iban = ''.join(str(ord(c) - ord('A') + 10) if c.isalpha() else c for c in iban)
        return int(iban) % 97
    
    if mod_97(value) != 1:
        raise ValidationError(_('IBAN invalide: numéro de contrôle incorrect.'))


def validate_swift_code(value: str) -> None:
    """
    Valide un code SWIFT/BIC
    
    Args:
        value: Code SWIFT à valider
    
    Raises:
        ValidationError: Si le code SWIFT n'est pas valide
    """
    # Supprime les espaces et convertit en majuscules
    value = re.sub(r'\s', '', value.upper())
    
    # Vérifie la longueur (8 ou 11 caractères)
    if len(value) not in [8, 11]:
        raise ValidationError(_('Code SWIFT invalide: longueur incorrecte.'))
    
    # Vérifie le format (4 lettres + 2 lettres + 2 caractères + optionnellement 3 caractères)
    if not re.match(r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$', value):
        raise ValidationError(_('Code SWIFT invalide: format incorrect.'))


def validate_tax_id(value: str, country_code: str = 'FR') -> None:
    """
    Valide un numéro de TVA
    
    Args:
        value: Numéro de TVA à valider
        country_code: Code pays
    
    Raises:
        ValidationError: Si le numéro de TVA n'est pas valide
    """
    # Supprime les espaces et convertit en majuscules
    value = re.sub(r'\s', '', value.upper())
    
    # Vérifie que ça commence par le code pays
    if not value.startswith(country_code):
        raise ValidationError(_(f'Le numéro de TVA doit commencer par {country_code}.'))
    
    # Validation spécifique par pays
    if country_code == 'FR':
        # Format: FR + 2 chiffres + 9 chiffres
        if not re.match(r'^FR\d{11}$', value):
            raise ValidationError(_('Numéro de TVA français invalide.'))
    elif country_code == 'DE':
        # Format: DE + 9 chiffres
        if not re.match(r'^DE\d{9}$', value):
            raise ValidationError(_('Numéro de TVA allemand invalide.'))
    # Ajouter d'autres pays selon les besoins


def validate_ssn(value: str, country_code: str = 'FR') -> None:
    """
    Valide un numéro de sécurité sociale
    
    Args:
        value: Numéro de sécurité sociale à valider
        country_code: Code pays
    
    Raises:
        ValidationError: Si le numéro de sécurité sociale n'est pas valide
    """
    # Supprime les espaces et tirets
    value = re.sub(r'[\s-]', '', value)
    
    if country_code == 'FR':
        # Format: 13 chiffres
        if not re.match(r'^\d{13}$', value):
            raise ValidationError(_('Numéro de sécurité sociale français invalide.'))
        
        # Validation du numéro INSEE
        def validate_insee(ssn):
            # Vérifie la clé de contrôle
            key = int(ssn[-2:])
            number = int(ssn[:-2])
            remainder = number % 97
            return remainder == key
        
        if not validate_insee(value):
            raise ValidationError(_('Numéro de sécurité sociale français invalide: clé de contrôle incorrecte.'))
    
    elif country_code == 'US':
        # Format: XXX-XX-XXXX
        if not re.match(r'^\d{3}-\d{2}-\d{4}$', value):
            raise ValidationError(_('Numéro de sécurité sociale américain invalide.'))
    
    # Ajouter d'autres pays selon les besoins


def validate_strong_password(value: str) -> None:
    """
    Valide un mot de passe fort
    
    Args:
        value: Mot de passe à valider
    
    Raises:
        ValidationError: Si le mot de passe n'est pas assez fort
    """
    if len(value) < 12:
        raise ValidationError(_('Le mot de passe doit contenir au moins 12 caractères.'))
    
    if not re.search(r'[A-Z]', value):
        raise ValidationError(_('Le mot de passe doit contenir au moins une majuscule.'))
    
    if not re.search(r'[a-z]', value):
        raise ValidationError(_('Le mot de passe doit contenir au moins une minuscule.'))
    
    if not re.search(r'\d', value):
        raise ValidationError(_('Le mot de passe doit contenir au moins un chiffre.'))
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(_('Le mot de passe doit contenir au moins un caractère spécial.'))
    
    # Vérifie qu'il n'y a pas de séquences communes
    common_sequences = ['123', 'abc', 'qwe', 'asd', 'zxc']
    value_lower = value.lower()
    for sequence in common_sequences:
        if sequence in value_lower:
            raise ValidationError(_('Le mot de passe ne peut pas contenir de séquences communes.'))


def validate_username(value: str) -> None:
    """
    Valide un nom d'utilisateur
    
    Args:
        value: Nom d'utilisateur à valider
    
    Raises:
        ValidationError: Si le nom d'utilisateur n'est pas valide
    """
    if len(value) < 3:
        raise ValidationError(_('Le nom d\'utilisateur doit contenir au moins 3 caractères.'))
    
    if len(value) > 30:
        raise ValidationError(_('Le nom d\'utilisateur ne peut pas dépasser 30 caractères.'))
    
    if not re.match(r'^[a-zA-Z0-9_.-]+$', value):
        raise ValidationError(_('Le nom d\'utilisateur ne peut contenir que des lettres, chiffres, points, tirets et underscores.'))
    
    if value.startswith('.') or value.endswith('.'):
        raise ValidationError(_('Le nom d\'utilisateur ne peut pas commencer ou se terminer par un point.'))
    
    if '..' in value:
        raise ValidationError(_('Le nom d\'utilisateur ne peut pas contenir deux points consécutifs.'))



