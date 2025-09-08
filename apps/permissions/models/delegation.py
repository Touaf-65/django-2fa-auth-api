"""
Modèles pour la délégation de permissions
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class PermissionDelegation(models.Model):
    """
    Modèle pour la délégation de permissions
    """
    # Délégateur et délégué
    delegator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='delegated_permissions',
        verbose_name="Délégateur"
    )
    delegatee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_permissions',
        verbose_name="Délégué"
    )
    permission = models.ForeignKey(
        'Permission',
        on_delete=models.CASCADE,
        verbose_name="Permission"
    )
    
    # Contraintes temporelles
    start_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date de début"
    )
    end_date = models.DateTimeField(
        verbose_name="Date de fin"
    )
    
    # Contraintes d'usage
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Nombre maximum d'utilisations"
    )
    current_uses = models.PositiveIntegerField(
        default=0,
        verbose_name="Utilisations actuelles"
    )
    
    # Contraintes de contexte
    allowed_ips = models.JSONField(
        default=list,
        blank=True,
        verbose_name="IPs autorisées"
    )
    allowed_actions = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Actions autorisées"
    )
    
    # Conditions supplémentaires
    conditions = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Conditions supplémentaires"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active"
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
        verbose_name = "Délégation de permission"
        verbose_name_plural = "Délégations de permissions"
        db_table = 'permissions_permission_delegation'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['delegator', 'is_active']),
            models.Index(fields=['delegatee', 'is_active']),
            models.Index(fields=['permission', 'is_active']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f"{self.delegator.username} → {self.delegatee.username} : {self.permission.name}"
    
    def is_valid(self):
        """
        Vérifie si la délégation est valide
        """
        now = timezone.now()
        
        # Vérifier les dates
        if not (self.start_date <= now <= self.end_date):
            return False
        
        # Vérifier le statut
        if not self.is_active:
            return False
        
        # Vérifier les utilisations
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
        
        return True
    
    def can_use(self, request=None):
        """
        Vérifie si la délégation peut être utilisée
        """
        if not self.is_valid():
            return False
        
        # Vérifier les IPs autorisées
        if self.allowed_ips and request:
            client_ip = self._get_client_ip(request)
            if client_ip not in self.allowed_ips:
                return False
        
        return True
    
    def use(self):
        """
        Utilise la délégation (incrémente le compteur)
        """
        if self.max_uses:
            self.current_uses += 1
            self.save(update_fields=['current_uses'])
    
    def get_remaining_uses(self):
        """
        Retourne le nombre d'utilisations restantes
        """
        if not self.max_uses:
            return None
        
        return max(0, self.max_uses - self.current_uses)
    
    def get_remaining_time(self):
        """
        Retourne le temps restant avant expiration
        """
        remaining = self.end_date - timezone.now()
        if remaining.total_seconds() <= 0:
            return 0
        
        return remaining
    
    def _get_client_ip(self, request):
        """
        Récupère l'IP du client
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '127.0.0.1'
    
    @classmethod
    def create_delegation(cls, delegator, delegatee, permission, constraints=None):
        """
        Crée une délégation de permission
        """
        constraints = constraints or {}
        
        return cls.objects.create(
            delegator=delegator,
            delegatee=delegatee,
            permission=permission,
            start_date=constraints.get('start_date', timezone.now()),
            end_date=constraints.get('end_date', timezone.now() + timezone.timedelta(days=7)),
            max_uses=constraints.get('max_uses'),
            allowed_ips=constraints.get('allowed_ips', []),
            allowed_actions=constraints.get('allowed_actions', []),
            conditions=constraints.get('conditions', {})
        )
    
    @classmethod
    def get_active_delegations(cls, user, permission=None):
        """
        Récupère les délégations actives d'un utilisateur
        """
        queryset = cls.objects.filter(
            delegatee=user,
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )
        
        if permission:
            queryset = queryset.filter(permission=permission)
        
        return queryset


class RoleDelegation(models.Model):
    """
    Modèle pour la délégation de rôles
    """
    # Délégateur et délégué
    delegator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='delegated_roles',
        verbose_name="Délégateur"
    )
    delegatee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_roles',
        verbose_name="Délégué"
    )
    role = models.ForeignKey(
        'Role',
        on_delete=models.CASCADE,
        verbose_name="Rôle"
    )
    
    # Permissions spécifiques à exclure
    excluded_permissions = models.ManyToManyField(
        'Permission',
        blank=True,
        verbose_name="Permissions exclues"
    )
    
    # Contraintes temporelles
    start_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date de début"
    )
    end_date = models.DateTimeField(
        verbose_name="Date de fin"
    )
    
    # Contraintes d'usage
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Nombre maximum d'utilisations"
    )
    current_uses = models.PositiveIntegerField(
        default=0,
        verbose_name="Utilisations actuelles"
    )
    
    # Contraintes de contexte
    allowed_ips = models.JSONField(
        default=list,
        blank=True,
        verbose_name="IPs autorisées"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active"
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
        verbose_name = "Délégation de rôle"
        verbose_name_plural = "Délégations de rôles"
        db_table = 'permissions_role_delegation'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['delegator', 'is_active']),
            models.Index(fields=['delegatee', 'is_active']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f"{self.delegator.username} → {self.delegatee.username} : {self.role.name}"
    
    def is_valid(self):
        """
        Vérifie si la délégation est valide
        """
        now = timezone.now()
        
        # Vérifier les dates
        if not (self.start_date <= now <= self.end_date):
            return False
        
        # Vérifier le statut
        if not self.is_active:
            return False
        
        # Vérifier les utilisations
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
        
        return True
    
    def can_use(self, request=None):
        """
        Vérifie si la délégation peut être utilisée
        """
        if not self.is_valid():
            return False
        
        # Vérifier les IPs autorisées
        if self.allowed_ips and request:
            client_ip = self._get_client_ip(request)
            if client_ip not in self.allowed_ips:
                return False
        
        return True
    
    def use(self):
        """
        Utilise la délégation (incrémente le compteur)
        """
        if self.max_uses:
            self.current_uses += 1
            self.save(update_fields=['current_uses'])
    
    def get_remaining_uses(self):
        """
        Retourne le nombre d'utilisations restantes
        """
        if not self.max_uses:
            return None
        
        return max(0, self.max_uses - self.current_uses)
    
    def get_remaining_time(self):
        """
        Retourne le temps restant avant expiration
        """
        remaining = self.end_date - timezone.now()
        if remaining.total_seconds() <= 0:
            return 0
        
        return remaining
    
    def get_effective_permissions(self):
        """
        Retourne les permissions effectives (rôle moins exclusions)
        """
        role_permissions = self.role.get_permissions()
        excluded_permissions = self.excluded_permissions.all()
        
        return role_permissions.exclude(id__in=excluded_permissions.values_list('id', flat=True))
    
    def _get_client_ip(self, request):
        """
        Récupère l'IP du client
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '127.0.0.1'
    
    @classmethod
    def create_delegation(cls, delegator, delegatee, role, constraints=None):
        """
        Crée une délégation de rôle
        """
        constraints = constraints or {}
        
        return cls.objects.create(
            delegator=delegator,
            delegatee=delegatee,
            role=role,
            start_date=constraints.get('start_date', timezone.now()),
            end_date=constraints.get('end_date', timezone.now() + timezone.timedelta(days=7)),
            max_uses=constraints.get('max_uses'),
            allowed_ips=constraints.get('allowed_ips', [])
        )
    
    @classmethod
    def get_active_delegations(cls, user, role=None):
        """
        Récupère les délégations de rôles actives d'un utilisateur
        """
        queryset = cls.objects.filter(
            delegatee=user,
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )
        
        if role:
            queryset = queryset.filter(role=role)
        
        return queryset

