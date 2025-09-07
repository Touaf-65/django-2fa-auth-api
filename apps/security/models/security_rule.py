"""
Modèle pour les règles de sécurité
"""
from django.db import models
from django.utils import timezone


class SecurityRule(models.Model):
    """
    Modèle pour définir les règles de sécurité
    """
    # Nom de la règle
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom de la règle"
    )
    
    # Description
    description = models.TextField(
        verbose_name="Description"
    )
    
    # Type de règle
    RATE_LIMIT = 'rate_limit'
    LOGIN_ATTEMPTS = 'login_attempts'
    IP_BLOCKING = 'ip_blocking'
    SUSPICIOUS_ACTIVITY = 'suspicious_activity'
    GEOGRAPHIC = 'geographic'
    TIME_BASED = 'time_based'
    
    RULE_TYPE_CHOICES = [
        (RATE_LIMIT, 'Limitation de taux'),
        (LOGIN_ATTEMPTS, 'Tentatives de connexion'),
        (IP_BLOCKING, 'Blocage IP'),
        (SUSPICIOUS_ACTIVITY, 'Activité suspecte'),
        (GEOGRAPHIC, 'Géographique'),
        (TIME_BASED, 'Basé sur le temps'),
    ]
    
    rule_type = models.CharField(
        max_length=20,
        choices=RULE_TYPE_CHOICES,
        verbose_name="Type de règle"
    )
    
    # Conditions de la règle
    conditions = models.JSONField(
        default=dict,
        verbose_name="Conditions"
    )
    
    # Actions à exécuter
    actions = models.JSONField(
        default=list,
        verbose_name="Actions"
    )
    
    # Priorité (plus le nombre est élevé, plus la priorité est haute)
    priority = models.PositiveIntegerField(
        default=1,
        verbose_name="Priorité"
    )
    
    # Statut
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    TESTING = 'testing'
    
    STATUS_CHOICES = [
        (ACTIVE, 'Actif'),
        (INACTIVE, 'Inactif'),
        (TESTING, 'En test'),
    ]
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=ACTIVE,
        verbose_name="Statut"
    )
    
    # Statistiques
    times_triggered = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de déclenchements"
    )
    last_triggered = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernier déclenchement"
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
        verbose_name = "Règle de sécurité"
        verbose_name_plural = "Règles de sécurité"
        db_table = 'security_security_rule'
        ordering = ['-priority', 'name']
        indexes = [
            models.Index(fields=['rule_type', 'status']),
            models.Index(fields=['status', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"
    
    def trigger(self):
        """
        Marque la règle comme déclenchée
        """
        self.times_triggered += 1
        self.last_triggered = timezone.now()
        self.save(update_fields=['times_triggered', 'last_triggered'])
    
    def is_condition_met(self, context):
        """
        Vérifie si les conditions de la règle sont remplies
        """
        # Implémentation basique - à étendre selon les besoins
        for key, expected_value in self.conditions.items():
            if key not in context:
                return False
            
            actual_value = context[key]
            
            # Comparaison simple
            if actual_value != expected_value:
                return False
        
        return True
    
    def execute_actions(self, context):
        """
        Exécute les actions définies dans la règle
        """
        results = []
        
        for action in self.actions:
            action_type = action.get('type')
            action_params = action.get('params', {})
            
            if action_type == 'block_ip':
                from .ip_block import IPBlock
                block = IPBlock.block_ip(
                    ip_address=context.get('ip_address'),
                    reason=action_params.get('reason', 'Règle de sécurité'),
                    block_type=action_params.get('block_type', 'automatic'),
                    duration_minutes=action_params.get('duration_minutes')
                )
                results.append({'action': 'block_ip', 'result': block})
            
            elif action_type == 'send_alert':
                from .security_event import SecurityEvent
                event = SecurityEvent.create_event(
                    event_type='suspicious_activity',
                    title=action_params.get('title', 'Règle de sécurité déclenchée'),
                    description=action_params.get('description', ''),
                    ip_address=context.get('ip_address'),
                    severity=action_params.get('severity', 'medium')
                )
                results.append({'action': 'send_alert', 'result': event})
            
            elif action_type == 'log_event':
                # Log simple
                results.append({'action': 'log_event', 'result': 'Logged'})
        
        return results
    
    @classmethod
    def get_active_rules(cls, rule_type=None):
        """
        Récupère les règles actives, optionnellement filtrées par type
        """
        queryset = cls.objects.filter(status=cls.ACTIVE)
        
        if rule_type:
            queryset = queryset.filter(rule_type=rule_type)
        
        return queryset.order_by('-priority')
    
    @classmethod
    def evaluate_rules(cls, context):
        """
        Évalue toutes les règles actives contre un contexte donné
        """
        triggered_rules = []
        
        for rule in cls.get_active_rules():
            if rule.is_condition_met(context):
                rule.trigger()
                actions_results = rule.execute_actions(context)
                triggered_rules.append({
                    'rule': rule,
                    'actions_results': actions_results
                })
        
        return triggered_rules
