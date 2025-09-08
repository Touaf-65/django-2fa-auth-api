"""
Modèle pour la sécurité des utilisateurs
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class UserSecurity(models.Model):
    """
    Modèle pour gérer la sécurité des utilisateurs
    """
    # Utilisateur
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='security_profile',
        verbose_name="Utilisateur"
    )
    
    # Statut de sécurité
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    LOCKED = 'locked'
    PENDING_VERIFICATION = 'pending_verification'
    
    STATUS_CHOICES = [
        (ACTIVE, 'Actif'),
        (SUSPENDED, 'Suspendu'),
        (LOCKED, 'Verrouillé'),
        (PENDING_VERIFICATION, 'En attente de vérification'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=ACTIVE,
        verbose_name="Statut de sécurité"
    )
    
    # Compteurs de sécurité
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Tentatives de connexion échouées"
    )
    last_failed_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière connexion échouée"
    )
    last_successful_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière connexion réussie"
    )
    
    # Informations de connexion
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dernière IP de connexion"
    )
    last_login_country = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="Dernier pays de connexion"
    )
    last_login_city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Dernière ville de connexion"
    )
    
    # Historique des IPs
    known_ips = models.JSONField(
        default=list,
        blank=True,
        verbose_name="IPs connues"
    )
    
    # Historique des appareils
    known_devices = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Appareils connus"
    )
    
    # Paramètres de sécurité
    require_2fa = models.BooleanField(
        default=False,
        verbose_name="2FA obligatoire"
    )
    allow_multiple_sessions = models.BooleanField(
        default=True,
        verbose_name="Autoriser les sessions multiples"
    )
    max_concurrent_sessions = models.PositiveIntegerField(
        default=5,
        verbose_name="Nombre maximum de sessions simultanées"
    )
    
    # Notifications de sécurité
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Notifications par email"
    )
    sms_notifications = models.BooleanField(
        default=False,
        verbose_name="Notifications par SMS"
    )
    push_notifications = models.BooleanField(
        default=True,
        verbose_name="Notifications push"
    )
    
    # Restrictions géographiques
    allowed_countries = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Pays autorisés"
    )
    blocked_countries = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Pays bloqués"
    )
    
    # Restrictions temporelles
    allowed_hours_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure de début autorisée"
    )
    allowed_hours_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure de fin autorisée"
    )
    allowed_days = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Jours autorisés (0=dimanche, 6=samedi)"
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
        verbose_name = "Profil de sécurité utilisateur"
        verbose_name_plural = "Profils de sécurité utilisateur"
        db_table = 'security_user_security'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Sécurité - {self.user.username}"
    
    def record_failed_login(self, ip_address, user_agent=None):
        """
        Enregistre une tentative de connexion échouée
        """
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        self.save(update_fields=['failed_login_attempts', 'last_failed_login'])
        
        # Vérifier si l'utilisateur doit être verrouillé
        if self.failed_login_attempts >= 5:  # Configurable
            self.lock_user("Trop de tentatives de connexion échouées")
    
    def record_successful_login(self, ip_address, country=None, city=None, user_agent=None):
        """
        Enregistre une connexion réussie
        """
        self.failed_login_attempts = 0
        self.last_successful_login = timezone.now()
        self.last_login_ip = ip_address
        self.last_login_country = country or ''
        self.last_login_city = city or ''
        
        # Ajouter l'IP aux IPs connues si elle n'y est pas
        if ip_address not in self.known_ips:
            self.known_ips.append(ip_address)
            # Garder seulement les 10 dernières IPs
            if len(self.known_ips) > 10:
                self.known_ips = self.known_ips[-10:]
        
        # Ajouter l'appareil aux appareils connus
        if user_agent:
            device_info = {
                'user_agent': user_agent,
                'ip_address': ip_address,
                'first_seen': timezone.now().isoformat(),
                'last_seen': timezone.now().isoformat()
            }
            
            # Vérifier si l'appareil existe déjà
            device_exists = False
            for device in self.known_devices:
                if device.get('user_agent') == user_agent:
                    device['last_seen'] = timezone.now().isoformat()
                    device_exists = True
                    break
            
            if not device_exists:
                self.known_devices.append(device_info)
                # Garder seulement les 20 derniers appareils
                if len(self.known_devices) > 20:
                    self.known_devices = self.known_devices[-20:]
        
        self.save()
    
    def lock_user(self, reason="Raison non spécifiée"):
        """
        Verrouille l'utilisateur
        """
        self.status = self.LOCKED
        self.save(update_fields=['status', 'updated_at'])
        
        # Créer un événement de sécurité
        from .security_event import SecurityEvent
        SecurityEvent.create_event(
            event_type='suspicious_activity',
            title='Utilisateur verrouillé',
            description=f'Utilisateur {self.user.username} verrouillé: {reason}',
            ip_address=self.last_login_ip or '0.0.0.0',
            user=self.user,
            severity='high'
        )
    
    def unlock_user(self):
        """
        Déverrouille l'utilisateur
        """
        self.status = self.ACTIVE
        self.failed_login_attempts = 0
        self.save(update_fields=['status', 'failed_login_attempts', 'updated_at'])
    
    def is_ip_allowed(self, ip_address):
        """
        Vérifie si une IP est autorisée pour cet utilisateur
        """
        # Vérifier les restrictions géographiques
        # (Implémentation simplifiée - nécessite un service de géolocalisation)
        return True
    
    def is_time_allowed(self):
        """
        Vérifie si la connexion est autorisée à cette heure
        """
        now = timezone.now()
        current_time = now.time()
        current_day = now.weekday()
        
        # Vérifier les jours autorisés
        if self.allowed_days and current_day not in self.allowed_days:
            return False
        
        # Vérifier les heures autorisées
        if self.allowed_hours_start and self.allowed_hours_end:
            if not (self.allowed_hours_start <= current_time <= self.allowed_hours_end):
                return False
        
        return True
    
    def is_device_known(self, user_agent):
        """
        Vérifie si l'appareil est connu
        """
        for device in self.known_devices:
            if device.get('user_agent') == user_agent:
                return True
        return False
    
    def get_security_score(self):
        """
        Calcule un score de sécurité pour l'utilisateur
        """
        score = 100
        
        # Pénalités
        if self.failed_login_attempts > 0:
            score -= min(self.failed_login_attempts * 10, 50)
        
        if not self.require_2fa:
            score -= 20
        
        if self.allow_multiple_sessions:
            score -= 10
        
        if len(self.known_ips) > 5:
            score -= 10
        
        if len(self.known_devices) > 10:
            score -= 10
        
        return max(score, 0)
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """
        Récupère ou crée un profil de sécurité pour un utilisateur
        """
        profile, created = cls.objects.get_or_create(
            user=user,
            defaults={
                'status': cls.ACTIVE,
                'require_2fa': False,
                'allow_multiple_sessions': True,
                'max_concurrent_sessions': 5,
                'email_notifications': True,
                'sms_notifications': False,
                'push_notifications': True,
            }
        )
        return profile

