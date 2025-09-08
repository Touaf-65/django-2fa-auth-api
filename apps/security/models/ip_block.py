"""
Modèle pour le blocage d'adresses IP
"""
from django.db import models
from django.utils import timezone


class IPBlock(models.Model):
    """
    Modèle pour gérer le blocage d'adresses IP
    """
    # Adresse IP bloquée
    ip_address = models.GenericIPAddressField(
        unique=True,
        verbose_name="Adresse IP"
    )
    
    # Type de blocage
    TEMPORARY = 'temporary'
    PERMANENT = 'permanent'
    MANUAL = 'manual'
    AUTOMATIC = 'automatic'
    
    BLOCK_TYPE_CHOICES = [
        (TEMPORARY, 'Temporaire'),
        (PERMANENT, 'Permanent'),
        (MANUAL, 'Manuel'),
        (AUTOMATIC, 'Automatique'),
    ]
    
    block_type = models.CharField(
        max_length=10,
        choices=BLOCK_TYPE_CHOICES,
        default=AUTOMATIC,
        verbose_name="Type de blocage"
    )
    
    # Raison du blocage
    reason = models.CharField(
        max_length=200,
        verbose_name="Raison du blocage"
    )
    
    # Détails supplémentaires
    details = models.TextField(
        blank=True,
        verbose_name="Détails"
    )
    
    # Durée du blocage (pour les blocages temporaires)
    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Durée en minutes"
    )
    
    # Dates
    blocked_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de blocage"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'expiration"
    )
    
    # Statut
    ACTIVE = 'active'
    EXPIRED = 'expired'
    MANUALLY_REMOVED = 'manually_removed'
    
    STATUS_CHOICES = [
        (ACTIVE, 'Actif'),
        (EXPIRED, 'Expiré'),
        (MANUALLY_REMOVED, 'Supprimé manuellement'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=ACTIVE,
        verbose_name="Statut"
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
        verbose_name = "Blocage IP"
        verbose_name_plural = "Blocages IP"
        db_table = 'security_ip_block'
        ordering = ['-blocked_at']
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['block_type', 'status']),
        ]
    
    def __str__(self):
        return f"IP {self.ip_address} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        """
        Calcule automatiquement la date d'expiration pour les blocages temporaires
        """
        if self.block_type == self.TEMPORARY and self.duration_minutes and not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=self.duration_minutes)
        
        super().save(*args, **kwargs)
    
    @classmethod
    def is_ip_blocked(cls, ip_address):
        """
        Vérifie si une adresse IP est bloquée
        """
        now = timezone.now()
        
        # Vérifier les blocages actifs
        active_blocks = cls.objects.filter(
            ip_address=ip_address,
            status=cls.ACTIVE
        )
        
        for block in active_blocks:
            # Vérifier l'expiration pour les blocages temporaires
            if block.block_type == cls.TEMPORARY and block.expires_at:
                if now > block.expires_at:
                    # Marquer comme expiré
                    block.status = cls.EXPIRED
                    block.save(update_fields=['status', 'updated_at'])
                    continue
            
            return True
        
        return False
    
    @classmethod
    def block_ip(cls, ip_address, reason, block_type=AUTOMATIC, duration_minutes=None, details=None):
        """
        Bloque une adresse IP
        """
        # Vérifier si l'IP n'est pas déjà bloquée
        if cls.is_ip_blocked(ip_address):
            return None
        
        expires_at = None
        if block_type == cls.TEMPORARY and duration_minutes:
            expires_at = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        
        return cls.objects.create(
            ip_address=ip_address,
            block_type=block_type,
            reason=reason,
            details=details or '',
            duration_minutes=duration_minutes,
            expires_at=expires_at
        )
    
    @classmethod
    def unblock_ip(cls, ip_address):
        """
        Débloque une adresse IP
        """
        blocks = cls.objects.filter(
            ip_address=ip_address,
            status=cls.ACTIVE
        )
        
        for block in blocks:
            block.status = cls.MANUALLY_REMOVED
            block.save(update_fields=['status', 'updated_at'])
        
        return blocks.count()
    
    def is_expired(self):
        """
        Vérifie si le blocage est expiré
        """
        if self.block_type != self.TEMPORARY or not self.expires_at:
            return False
        
        return timezone.now() > self.expires_at
    
    def get_remaining_time(self):
        """
        Retourne le temps restant avant expiration (en minutes)
        """
        if self.block_type != self.TEMPORARY or not self.expires_at:
            return None
        
        remaining = self.expires_at - timezone.now()
        if remaining.total_seconds() <= 0:
            return 0
        
        return int(remaining.total_seconds() / 60)

