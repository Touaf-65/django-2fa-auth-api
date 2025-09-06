"""
Modèle User étendu pour l'authentification 2FA
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Manager personnalisé pour le modèle User
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """Crée et sauvegarde un utilisateur avec l'email donné et le mot de passe"""
        if not email:
            raise ValueError('L\'email doit être défini')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crée et sauvegarde un superutilisateur avec l'email donné et le mot de passe"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Modèle utilisateur étendu avec support 2FA et gestion de profil
    """
    
    # Informations de base
    email = models.EmailField(
        unique=True,
        verbose_name="Adresse email",
        help_text="Adresse email unique pour l'authentification"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Numéro de téléphone",
        help_text="Numéro de téléphone pour SMS 2FA"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Avatar",
        help_text="Photo de profil de l'utilisateur"
    )
    
    # Authentification
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Email vérifié",
        help_text="Indique si l'email de l'utilisateur a été vérifié"
    )
    two_factor_enabled = models.BooleanField(
        default=False,
        verbose_name="2FA activé",
        help_text="Indique si l'authentification à deux facteurs est activée"
    )
    backup_codes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Codes de secours",
        help_text="Codes de secours pour l'authentification 2FA"
    )
    
    # Sécurité
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dernière IP de connexion",
        help_text="Adresse IP de la dernière connexion"
    )
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Tentatives de connexion échouées",
        help_text="Nombre de tentatives de connexion échouées"
    )
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Verrouillé jusqu'à",
        help_text="Date/heure jusqu'à laquelle le compte est verrouillé"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
        help_text="Date et heure de création du compte"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification",
        help_text="Date et heure de dernière modification"
    )
    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière activité",
        help_text="Date et heure de la dernière activité"
    )
    
    # Préférences
    language = models.CharField(
        max_length=5,
        default='fr',
        choices=[
            ('fr', 'Français'),
            ('en', 'English'),
            ('es', 'Español'),
            ('de', 'Deutsch'),
        ],
        verbose_name="Langue",
        help_text="Langue préférée de l'utilisateur"
    )
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        verbose_name="Fuseau horaire",
        help_text="Fuseau horaire préféré de l'utilisateur"
    )
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Notifications email",
        help_text="Recevoir les notifications par email"
    )
    
    # Champs Django par défaut à ignorer
    username = None
    
    # Manager personnalisé
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        db_table = 'auth_user'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"
    
    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Retourne le prénom de l'utilisateur"""
        return self.first_name
    
    def is_account_locked(self):
        """Vérifie si le compte est verrouillé"""
        if self.locked_until:
            return timezone.now() < self.locked_until
        return False
    
    def lock_account(self, duration_minutes=15):
        """Verrouille le compte pour une durée donnée"""
        self.locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=['locked_until'])
    
    def unlock_account(self):
        """Déverrouille le compte"""
        self.locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['locked_until', 'failed_login_attempts'])
    
    def increment_failed_attempts(self):
        """Incrémente le nombre de tentatives échouées"""
        self.failed_login_attempts += 1
        self.save(update_fields=['failed_login_attempts'])
    
    def reset_failed_attempts(self):
        """Remet à zéro le nombre de tentatives échouées"""
        self.failed_login_attempts = 0
        self.save(update_fields=['failed_login_attempts'])
    
    def update_last_activity(self):
        """Met à jour la dernière activité"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def has_2fa_enabled(self):
        """Vérifie si l'utilisateur a activé la 2FA"""
        return self.two_factor_enabled
    
    def can_use_backup_code(self, code):
        """Vérifie si un code de secours est valide"""
        return code in self.backup_codes
    
    def use_backup_code(self, code):
        """Utilise un code de secours (le retire de la liste)"""
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save(update_fields=['backup_codes'])
            return True
        return False
