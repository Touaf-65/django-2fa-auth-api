"""
Modèles pour les profils utilisateur étendus
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator


class UserProfile(models.Model):
    """
    Profil utilisateur étendu avec informations détaillées
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_profile',
        verbose_name="Utilisateur"
    )
    
    # Informations personnelles
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Biographie",
        help_text="Description personnelle (500 caractères max)"
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de naissance"
    )
    gender = models.CharField(
        max_length=20,
        choices=[
            ('male', 'Homme'),
            ('female', 'Femme'),
            ('other', 'Autre'),
            ('prefer_not_to_say', 'Préfère ne pas dire'),
        ],
        blank=True,
        verbose_name="Genre"
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Localisation"
    )
    website = models.URLField(
        blank=True,
        verbose_name="Site web personnel"
    )
    
    # Informations professionnelles
    job_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Poste"
    )
    company = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Entreprise"
    )
    industry = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Secteur d'activité"
    )
    
    # Réseaux sociaux
    linkedin_url = models.URLField(
        blank=True,
        verbose_name="LinkedIn"
    )
    twitter_handle = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Twitter",
        validators=[
            RegexValidator(
                regex=r'^@?[A-Za-z0-9_]{1,15}$',
                message="Format Twitter invalide. Utilisez @username ou username"
            )
        ]
    )
    github_username = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="GitHub",
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9]([a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$',
                message="Nom d'utilisateur GitHub invalide"
            )
        ]
    )
    
    # Paramètres de confidentialité
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('friends', 'Amis seulement'),
            ('private', 'Privé'),
        ],
        default='public',
        verbose_name="Visibilité du profil"
    )
    show_email = models.BooleanField(
        default=False,
        verbose_name="Afficher l'email"
    )
    show_phone = models.BooleanField(
        default=False,
        verbose_name="Afficher le téléphone"
    )
    show_birth_date = models.BooleanField(
        default=False,
        verbose_name="Afficher la date de naissance"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de dernière modification"
    )
    last_profile_update = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière mise à jour du profil"
    )
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateur"
        db_table = 'users_user_profile'
    
    def __str__(self):
        return f"Profil de {self.user.email}"
    
    def get_age(self):
        """Calcule l'âge de l'utilisateur"""
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None
    
    def get_display_name(self):
        """Retourne le nom d'affichage complet"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.email
    
    def update_last_profile_update(self):
        """Met à jour la date de dernière modification du profil"""
        self.last_profile_update = timezone.now()
        self.save(update_fields=['last_profile_update'])


class UserPreference(models.Model):
    """
    Préférences utilisateur pour l'interface et les fonctionnalités
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_preferences',
        verbose_name="Utilisateur"
    )
    
    # Préférences d'interface
    theme = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Clair'),
            ('dark', 'Sombre'),
            ('auto', 'Automatique'),
        ],
        default='auto',
        verbose_name="Thème"
    )
    language = models.CharField(
        max_length=5,
        choices=[
            ('en', 'English'),
            ('fr', 'Français'),
            ('es', 'Español'),
            ('de', 'Deutsch'),
        ],
        default='fr',
        verbose_name="Langue"
    )
    timezone = models.CharField(
        max_length=50,
        default='Europe/Paris',
        verbose_name="Fuseau horaire"
    )
    
    # Préférences de notification
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Notifications email"
    )
    push_notifications = models.BooleanField(
        default=True,
        verbose_name="Notifications push"
    )
    sms_notifications = models.BooleanField(
        default=False,
        verbose_name="Notifications SMS"
    )
    
    # Types de notifications
    notify_new_followers = models.BooleanField(
        default=True,
        verbose_name="Nouveaux abonnés"
    )
    notify_new_messages = models.BooleanField(
        default=True,
        verbose_name="Nouveaux messages"
    )
    notify_system_updates = models.BooleanField(
        default=True,
        verbose_name="Mises à jour système"
    )
    notify_security_alerts = models.BooleanField(
        default=True,
        verbose_name="Alertes de sécurité"
    )
    
    # Préférences de confidentialité
    allow_search_engines = models.BooleanField(
        default=True,
        verbose_name="Autoriser les moteurs de recherche"
    )
    show_online_status = models.BooleanField(
        default=True,
        verbose_name="Afficher le statut en ligne"
    )
    allow_friend_requests = models.BooleanField(
        default=True,
        verbose_name="Autoriser les demandes d'amitié"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de dernière modification"
    )
    
    class Meta:
        verbose_name = "Préférence utilisateur"
        verbose_name_plural = "Préférences utilisateur"
        db_table = 'users_user_preference'
    
    def __str__(self):
        return f"Préférences de {self.user.email}"


class UserActivity(models.Model):
    """
    Historique des activités utilisateur
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_activities',
        verbose_name="Utilisateur"
    )
    
    # Type d'activité
    activity_type = models.CharField(
        max_length=50,
        choices=[
            ('login', 'Connexion'),
            ('logout', 'Déconnexion'),
            ('profile_update', 'Mise à jour du profil'),
            ('password_change', 'Changement de mot de passe'),
            ('2fa_enabled', '2FA activé'),
            ('2fa_disabled', '2FA désactivé'),
            ('email_verification', 'Vérification email'),
            ('account_created', 'Compte créé'),
            ('account_deleted', 'Compte supprimé'),
            ('security_alert', 'Alerte de sécurité'),
        ],
        verbose_name="Type d'activité"
    )
    
    # Détails de l'activité
    description = models.TextField(
        verbose_name="Description"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Adresse IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    device_info = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Informations du device"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    class Meta:
        verbose_name = "Activité utilisateur"
        verbose_name_plural = "Activités utilisateur"
        db_table = 'users_user_activity'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()} ({self.created_at})"
    
    @classmethod
    def log_activity(cls, user, activity_type, description, request=None, **kwargs):
        """Enregistre une nouvelle activité utilisateur"""
        device_info = {}
        ip_address = None
        user_agent = ""
        
        if request:
            ip_address = cls._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            device_info = cls._extract_device_info(request)
        
        return cls.objects.create(
            user=user,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info,
            **kwargs
        )
    
    @staticmethod
    def _get_client_ip(request):
        """Récupère l'adresse IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def _extract_device_info(request):
        """Extrait les informations du device depuis la requête"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Analyse basique du User Agent
        device_info = {
            'user_agent': user_agent,
            'browser': 'Unknown',
            'os': 'Unknown',
            'device_type': 'Unknown'
        }
        
        # Détection basique du navigateur
        if 'Chrome' in user_agent:
            device_info['browser'] = 'Chrome'
        elif 'Firefox' in user_agent:
            device_info['browser'] = 'Firefox'
        elif 'Safari' in user_agent:
            device_info['browser'] = 'Safari'
        elif 'Edge' in user_agent:
            device_info['browser'] = 'Edge'
        
        # Détection basique de l'OS
        if 'Windows' in user_agent:
            device_info['os'] = 'Windows'
        elif 'Mac' in user_agent:
            device_info['os'] = 'macOS'
        elif 'Linux' in user_agent:
            device_info['os'] = 'Linux'
        elif 'Android' in user_agent:
            device_info['os'] = 'Android'
        elif 'iOS' in user_agent:
            device_info['os'] = 'iOS'
        
        # Détection du type de device
        if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
            device_info['device_type'] = 'Mobile'
        elif 'Tablet' in user_agent or 'iPad' in user_agent:
            device_info['device_type'] = 'Tablet'
        else:
            device_info['device_type'] = 'Desktop'
        
        return device_info
