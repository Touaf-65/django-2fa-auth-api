"""
Modèle pour les permissions granulaires
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class Permission(models.Model):
    """
    Modèle pour les permissions granulaires
    """
    # Informations de base
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom de la permission"
    )
    codename = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Code de la permission"
    )
    description = models.TextField(
        verbose_name="Description"
    )
    
    # Granularité par app/model/action
    app_label = models.CharField(
        max_length=50,
        verbose_name="Application"
    )
    model = models.CharField(
        max_length=50,
        verbose_name="Modèle"
    )
    action = models.CharField(
        max_length=50,
        verbose_name="Action"
    )
    
    # Granularité par champ
    field_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nom du champ"
    )
    
    # Conditions de valeur (pour les champs monétaires)
    min_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valeur minimale"
    )
    max_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valeur maximale"
    )
    
    # Conditions de contexte
    conditions = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Conditions"
    )
    
    # Métadonnées
    is_custom = models.BooleanField(
        default=False,
        verbose_name="Permission personnalisée"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_permissions',
        verbose_name="Créé par"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de dernière modification"
    )
    
    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        db_table = 'permissions_permission'
        ordering = ['app_label', 'model', 'action', 'field_name']
        indexes = [
            models.Index(fields=['app_label', 'model', 'action']),
            models.Index(fields=['codename']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.codename})"
    
    @classmethod
    def create_permission(cls, name, codename, description, app_label, model, action,
                         field_name=None, min_value=None, max_value=None, conditions=None, created_by=None):
        """
        Crée une nouvelle permission
        """
        return cls.objects.create(
            name=name,
            codename=codename,
            description=description,
            app_label=app_label,
            model=model,
            action=action,
            field_name=field_name or '',
            min_value=min_value,
            max_value=max_value,
            conditions=conditions or {},
            is_custom=True,
            created_by=created_by
        )
    
    def check_value_constraints(self, value):
        """
        Vérifie les contraintes de valeur
        """
        if value is None:
            return True
        
        try:
            decimal_value = Decimal(str(value))
            
            if self.min_value is not None and decimal_value < self.min_value:
                return False
            
            if self.max_value is not None and decimal_value > self.max_value:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    def check_conditions(self, context):
        """
        Vérifie les conditions contextuelles
        """
        if not self.conditions:
            return True
        
        for key, expected_value in self.conditions.items():
            if key not in context:
                return False
            
            actual_value = context[key]
            
            # Comparaison simple
            if actual_value != expected_value:
                return False
        
        return True


class ConditionalPermission(models.Model):
    """
    Modèle pour les permissions conditionnelles
    """
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='conditional_permissions',
        verbose_name="Permission"
    )
    
    # Type de condition
    TEMPORAL = 'temporal'
    GEOGRAPHIC = 'geographic'
    RESOURCE_OWNERSHIP = 'resource_ownership'
    DEPARTMENT = 'department'
    HIERARCHY = 'hierarchy'
    IP_RESTRICTION = 'ip_restriction'
    
    CONDITION_TYPE_CHOICES = [
        (TEMPORAL, 'Temporelle'),
        (GEOGRAPHIC, 'Géographique'),
        (RESOURCE_OWNERSHIP, 'Propriété de ressource'),
        (DEPARTMENT, 'Département'),
        (HIERARCHY, 'Hiérarchie'),
        (IP_RESTRICTION, 'Restriction IP'),
    ]
    
    condition_type = models.CharField(
        max_length=20,
        choices=CONDITION_TYPE_CHOICES,
        verbose_name="Type de condition"
    )
    
    # Données de la condition
    condition_data = models.JSONField(
        default=dict,
        verbose_name="Données de condition"
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
        verbose_name = "Permission conditionnelle"
        verbose_name_plural = "Permissions conditionnelles"
        db_table = 'permissions_conditional_permission'
        ordering = ['permission', 'condition_type']
        indexes = [
            models.Index(fields=['permission', 'condition_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.permission.name} - {self.get_condition_type_display()}"
    
    def evaluate_condition(self, user, resource=None, request=None):
        """
        Évalue la condition
        """
        if not self.is_active:
            return True
        
        if self.condition_type == self.TEMPORAL:
            return self._evaluate_temporal_condition()
        elif self.condition_type == self.GEOGRAPHIC:
            return self._evaluate_geographic_condition(user, request)
        elif self.condition_type == self.RESOURCE_OWNERSHIP:
            return self._evaluate_ownership_condition(user, resource)
        elif self.condition_type == self.DEPARTMENT:
            return self._evaluate_department_condition(user, resource)
        elif self.condition_type == self.HIERARCHY:
            return self._evaluate_hierarchy_condition(user, resource)
        elif self.condition_type == self.IP_RESTRICTION:
            return self._evaluate_ip_condition(request)
        
        return True
    
    def _evaluate_temporal_condition(self):
        """
        Évalue une condition temporelle
        """
        now = timezone.now()
        current_time = now.time()
        current_weekday = now.weekday()  # 0=lundi, 6=dimanche
        
        conditions = self.condition_data
        
        # Vérifier les jours de la semaine
        if 'days' in conditions:
            allowed_days = conditions['days']
            day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            if day_names[current_weekday] not in allowed_days:
                return False
        
        # Vérifier les heures
        if 'start_time' in conditions and 'end_time' in conditions:
            start_time = timezone.datetime.strptime(conditions['start_time'], '%H:%M').time()
            end_time = timezone.datetime.strptime(conditions['end_time'], '%H:%M').time()
            
            if not (start_time <= current_time <= end_time):
                return False
        
        return True
    
    def _evaluate_geographic_condition(self, user, request):
        """
        Évalue une condition géographique
        """
        if not request:
            return True
        
        conditions = self.condition_data
        
        # Vérifier les IPs autorisées
        if 'allowed_ips' in conditions:
            client_ip = self._get_client_ip(request)
            allowed_ips = conditions['allowed_ips']
            
            # Vérification simple (en production, utiliser ipaddress)
            if client_ip not in allowed_ips:
                return False
        
        # Vérifier les pays autorisés
        if 'allowed_countries' in conditions:
            # Implémentation simplifiée - en production, utiliser un service de géolocalisation
            pass
        
        return True
    
    def _evaluate_ownership_condition(self, user, resource):
        """
        Évalue une condition de propriété
        """
        if not resource:
            return True
        
        conditions = self.condition_data
        
        # Vérifier si l'utilisateur est propriétaire de la ressource
        if 'owner_field' in conditions:
            owner_field = conditions['owner_field']
            if hasattr(resource, owner_field):
                owner = getattr(resource, owner_field)
                return owner == user
        
        return True
    
    def _evaluate_department_condition(self, user, resource):
        """
        Évalue une condition de département
        """
        if not resource:
            return True
        
        conditions = self.condition_data
        
        # Vérifier si l'utilisateur et la ressource sont dans le même département
        user_department_field = conditions.get('user_department_field', 'profile.department')
        resource_department_field = conditions.get('resource_department_field', 'department')
        
        # Implémentation simplifiée
        try:
            user_department = self._get_nested_attribute(user, user_department_field)
            resource_department = self._get_nested_attribute(resource, resource_department_field)
            return user_department == resource_department
        except AttributeError:
            return False
    
    def _evaluate_hierarchy_condition(self, user, resource):
        """
        Évalue une condition hiérarchique
        """
        if not resource:
            return True
        
        conditions = self.condition_data
        
        # Vérifier le niveau hiérarchique
        user_level_field = conditions.get('user_level_field', 'profile.level')
        resource_level_field = conditions.get('resource_level_field', 'level')
        comparison = conditions.get('comparison', 'greater_than')
        
        try:
            user_level = self._get_nested_attribute(user, user_level_field)
            resource_level = self._get_nested_attribute(resource, resource_level_field)
            
            if comparison == 'greater_than':
                return user_level > resource_level
            elif comparison == 'greater_than_or_equal':
                return user_level >= resource_level
            elif comparison == 'equal':
                return user_level == resource_level
            
        except (AttributeError, TypeError):
            return False
        
        return True
    
    def _evaluate_ip_condition(self, request):
        """
        Évalue une condition IP
        """
        if not request:
            return True
        
        conditions = self.condition_data
        client_ip = self._get_client_ip(request)
        
        # Vérifier les IPs autorisées
        if 'allowed_ips' in conditions:
            allowed_ips = conditions['allowed_ips']
            if client_ip not in allowed_ips:
                return False
        
        # Vérifier les IPs bloquées
        if 'blocked_ips' in conditions:
            blocked_ips = conditions['blocked_ips']
            if client_ip in blocked_ips:
                return False
        
        return True
    
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
    
    def _get_nested_attribute(self, obj, field_path):
        """
        Récupère un attribut imbriqué
        """
        attrs = field_path.split('.')
        value = obj
        
        for attr in attrs:
            value = getattr(value, attr)
        
        return value

