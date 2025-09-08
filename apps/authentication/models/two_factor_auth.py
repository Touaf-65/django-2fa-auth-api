"""
Modèle pour l'authentification à deux facteurs (2FA)
"""

import pyotp
import qrcode
import io
import base64
from django.db import models
from django.conf import settings


class TwoFactorAuth(models.Model):
    """
    Modèle pour gérer l'authentification à deux facteurs TOTP
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='two_factor_auth',
        verbose_name="Utilisateur",
        help_text="Utilisateur associé à cette configuration 2FA"
    )
    
    secret_key = models.CharField(
        max_length=32,
        verbose_name="Clé secrète",
        help_text="Clé secrète pour générer les codes TOTP"
    )
    
    backup_codes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Codes de secours",
        help_text="Codes de secours pour récupérer l'accès"
    )
    
    is_enabled = models.BooleanField(
        default=False,
        verbose_name="Activé",
        help_text="Indique si la 2FA est activée pour cet utilisateur"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
        help_text="Date et heure de création de la configuration 2FA"
    )
    
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière utilisation",
        help_text="Date et heure de dernière utilisation de la 2FA"
    )
    
    class Meta:
        verbose_name = "Authentification 2FA"
        verbose_name_plural = "Authentifications 2FA"
        db_table = 'auth_two_factor_auth'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"2FA pour {self.user.email} ({'Activé' if self.is_enabled else 'Désactivé'})"
    
    def generate_secret_key(self):
        """Génère une nouvelle clé secrète"""
        self.secret_key = pyotp.random_base32()
        return self.secret_key
    
    def generate_backup_codes(self, count=10):
        """Génère des codes de secours"""
        import secrets
        import string
        
        codes = []
        for _ in range(count):
            # Génère un code de 8 caractères alphanumériques
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            codes.append(code)
        
        self.backup_codes = codes
        return codes
    
    def get_totp_uri(self):
        """Génère l'URI TOTP pour l'application d'authentification"""
        totp = pyotp.TOTP(self.secret_key)
        return totp.provisioning_uri(
            name=self.user.email,
            issuer_name=getattr(settings, 'SITE_NAME', 'Django 2FA Auth API')
        )
    
    def generate_qr_code(self):
        """Génère un QR code pour l'URI TOTP"""
        uri = self.get_totp_uri()
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir l'image en base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
    
    def verify_totp_code(self, code):
        """Vérifie un code TOTP"""
        totp = pyotp.TOTP(self.secret_key)
        return totp.verify(code, valid_window=1)  # Tolérance de 1 période (30 secondes)
    
    def verify_backup_code(self, code):
        """Vérifie un code de secours"""
        if code in self.backup_codes:
            # Retire le code de secours après utilisation
            self.backup_codes.remove(code)
            self.save(update_fields=['backup_codes'])
            return True
        return False
    
    def enable(self):
        """Active la 2FA"""
        self.is_enabled = True
        self.user.two_factor_enabled = True
        self.user.save(update_fields=['two_factor_enabled'])
        self.save(update_fields=['is_enabled'])
    
    def disable(self):
        """Désactive la 2FA"""
        self.is_enabled = False
        self.user.two_factor_enabled = False
        self.user.save(update_fields=['two_factor_enabled'])
        self.save(update_fields=['is_enabled'])
    
    def update_last_used(self):
        """Met à jour la dernière utilisation"""
        from django.utils import timezone
        self.last_used = timezone.now()
        self.save(update_fields=['last_used'])
    
    @classmethod
    def create_for_user(cls, user):
        """Crée une configuration 2FA pour un utilisateur"""
        two_factor_auth = cls(user=user)
        two_factor_auth.generate_secret_key()
        two_factor_auth.generate_backup_codes()
        two_factor_auth.save()
        return two_factor_auth

