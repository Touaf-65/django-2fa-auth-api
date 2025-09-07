"""
Modèle pour la gestion des sessions utilisateur
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class UserSession(models.Model):
    """
    Modèle pour gérer les sessions utilisateur avec informations de device
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name="Utilisateur",
        help_text="Utilisateur propriétaire de cette session"
    )
    
    session_key = models.CharField(
        max_length=40,
        unique=True,
        verbose_name="Clé de session",
        help_text="Clé unique de la session Django"
    )
    
    device_info = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Informations du device",
        help_text="Informations sur l'appareil (navigateur, OS, etc.)"
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name="Adresse IP",
        help_text="Adresse IP de la connexion"
    )
    
    user_agent = models.TextField(
        verbose_name="User Agent",
        help_text="User Agent du navigateur/appareil"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Session active",
        help_text="Indique si la session est active"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
        help_text="Date et heure de création de la session"
    )
    
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière activité",
        help_text="Date et heure de dernière activité sur cette session"
    )
    
    expires_at = models.DateTimeField(
        verbose_name="Expire le",
        help_text="Date et heure d'expiration de la session"
    )
    
    class Meta:
        verbose_name = "Session utilisateur"
        verbose_name_plural = "Sessions utilisateur"
        db_table = 'auth_user_session'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Session {self.session_key[:8]}... pour {self.user.email}"
    
    def is_expired(self):
        """Vérifie si la session a expiré"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Vérifie si la session est valide (active et non expirée)"""
        return self.is_active and not self.is_expired()
    
    def deactivate(self):
        """Désactive la session"""
        self.is_active = False
        self.save(update_fields=['is_active'])
    
    def update_activity(self):
        """Met à jour la dernière activité"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def extend_expiration(self, hours=24):
        """Prolonge l'expiration de la session"""
        self.expires_at = timezone.now() + timezone.timedelta(hours=hours)
        self.save(update_fields=['expires_at'])
    
    def get_device_name(self):
        """Retourne un nom lisible pour le device"""
        device_info = self.device_info or {}
        
        # Essayer de construire un nom à partir des informations disponibles
        parts = []
        
        if device_info.get('browser'):
            parts.append(device_info['browser'])
        
        if device_info.get('os'):
            parts.append(device_info['os'])
        
        if device_info.get('device_type'):
            parts.append(device_info['device_type'])
        
        if parts:
            return ' '.join(parts)
        
        # Fallback sur l'IP si pas d'autres infos
        return f"Device depuis {self.ip_address}"
    
    @classmethod
    def create_session(cls, user, session_key, request):
        """Crée une nouvelle session pour un utilisateur"""
        from django.utils import timezone
        import uuid
        
        # Si pas de session_key, en générer une
        if not session_key:
            session_key = str(uuid.uuid4())
        
        # Extraire les informations du device
        device_info = cls._extract_device_info(request)
        
        # Calculer l'expiration (24h par défaut)
        expires_at = timezone.now() + timezone.timedelta(hours=24)
        
        session = cls.objects.create(
            user=user,
            session_key=session_key,
            device_info=device_info,
            ip_address=cls._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            expires_at=expires_at
        )
        
        return session
    
    @classmethod
    def _extract_device_info(cls, request):
        """Extrait les informations du device depuis la requête"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Parsing basique du User Agent
        device_info = {
            'user_agent': user_agent,
            'ip_address': cls._get_client_ip(request),
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
        else:
            device_info['browser'] = 'Unknown'
        
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
        else:
            device_info['os'] = 'Unknown'
        
        # Détection du type de device
        if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
            device_info['device_type'] = 'Mobile'
        elif 'Tablet' in user_agent or 'iPad' in user_agent:
            device_info['device_type'] = 'Tablet'
        else:
            device_info['device_type'] = 'Desktop'
        
        return device_info
    
    @classmethod
    def _get_client_ip(cls, request):
        """Récupère l'IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """Nettoie les sessions expirées"""
        expired_sessions = cls.objects.filter(
            expires_at__lt=timezone.now()
        )
        count = expired_sessions.count()
        expired_sessions.delete()
        return count
