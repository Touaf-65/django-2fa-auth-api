"""
Modèle pour les tentatives de connexion
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class LoginAttempt(models.Model):
    """
    Modèle pour enregistrer les tentatives de connexion
    """
    # Utilisateur (peut être null si tentative avec email inexistant)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='login_attempts',
        verbose_name="Utilisateur"
    )
    
    # Informations de connexion
    email = models.EmailField(
        verbose_name="Email utilisé"
    )
    username = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nom d'utilisateur utilisé"
    )
    
    # Résultat de la tentative
    SUCCESS = 'success'
    FAILED = 'failed'
    BLOCKED = 'blocked'
    LOCKED = 'locked'
    
    STATUS_CHOICES = [
        (SUCCESS, 'Succès'),
        (FAILED, 'Échec'),
        (BLOCKED, 'Bloqué'),
        (LOCKED, 'Verrouillé'),
    ]
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name="Statut"
    )
    
    # Informations de la requête
    ip_address = models.GenericIPAddressField(
        verbose_name="Adresse IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    country = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="Pays (code ISO)"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ville"
    )
    
    # Détails de l'échec
    failure_reason = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Raison de l'échec"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    class Meta:
        verbose_name = "Tentative de connexion"
        verbose_name_plural = "Tentatives de connexion"
        db_table = 'security_login_attempt'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Tentative {self.status} - {self.email} - {self.ip_address}"
    
    @classmethod
    def get_failed_attempts_count(cls, ip_address, email=None, minutes=15):
        """
        Compte les tentatives échouées récentes
        """
        since = timezone.now() - timezone.timedelta(minutes=minutes)
        queryset = cls.objects.filter(
            ip_address=ip_address,
            status__in=[cls.FAILED, cls.BLOCKED],
            created_at__gte=since
        )
        
        if email:
            queryset = queryset.filter(email=email)
        
        return queryset.count()
    
    @classmethod
    def is_ip_blocked(cls, ip_address, minutes=60):
        """
        Vérifie si une IP est bloquée
        """
        since = timezone.now() - timezone.timedelta(minutes=minutes)
        return cls.objects.filter(
            ip_address=ip_address,
            status=cls.BLOCKED,
            created_at__gte=since
        ).exists()
    
    @classmethod
    def is_user_locked(cls, user, minutes=30):
        """
        Vérifie si un utilisateur est verrouillé
        """
        since = timezone.now() - timezone.timedelta(minutes=minutes)
        return cls.objects.filter(
            user=user,
            status=cls.LOCKED,
            created_at__gte=since
        ).exists()
    
    @classmethod
    def record_attempt(cls, email, ip_address, user_agent, status, user=None, 
                      username=None, failure_reason=None, country=None, city=None):
        """
        Enregistre une tentative de connexion
        """
        return cls.objects.create(
            user=user,
            email=email,
            username=username or email,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            country=country or '',
            city=city or '',
            failure_reason=failure_reason or ''
        )



