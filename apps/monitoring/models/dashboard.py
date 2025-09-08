"""
Modèles pour les tableaux de bord de monitoring
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class Dashboard(TimestampedModel):
    """Tableau de bord de monitoring"""
    
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('shared', 'Shared'),
        ('public', 'Public'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    
    # Configuration
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
    is_active = models.BooleanField(default=True)
    refresh_interval = models.PositiveIntegerField(default=30, help_text="Refresh interval in seconds")
    
    # Layout
    layout_config = models.JSONField(default=dict, blank=True)
    
    # Métadonnées
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'monitoring_dashboard'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.owner.email})"
    
    @property
    def is_private(self):
        """Vérifie si le tableau de bord est privé"""
        return self.visibility == 'private'
    
    @property
    def is_shared(self):
        """Vérifie si le tableau de bord est partagé"""
        return self.visibility == 'shared'
    
    @property
    def is_public(self):
        """Vérifie si le tableau de bord est public"""
        return self.visibility == 'public'
    
    def get_widgets(self):
        """Récupère les widgets du tableau de bord"""
        return self.widgets.filter(is_active=True).order_by('position')
    
    def add_widget(self, widget_type, title, config, position=None):
        """Ajoute un widget au tableau de bord"""
        if position is None:
            position = self.widgets.count()
        
        widget = DashboardWidget.objects.create(
            dashboard=self,
            widget_type=widget_type,
            title=title,
            config=config,
            position=position
        )
        return widget


class DashboardWidget(TimestampedModel):
    """Widget de tableau de bord"""
    
    WIDGET_TYPE_CHOICES = [
        ('metric', 'Metric'),
        ('chart', 'Chart'),
        ('table', 'Table'),
        ('alert', 'Alert'),
        ('log', 'Log'),
        ('health', 'Health Check'),
        ('custom', 'Custom'),
    ]
    
    CHART_TYPE_CHOICES = [
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('area', 'Area Chart'),
        ('gauge', 'Gauge'),
        ('heatmap', 'Heatmap'),
    ]
    
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Configuration
    config = models.JSONField(default=dict, blank=True)
    position = models.PositiveIntegerField(default=0)
    size = models.JSONField(default=dict, blank=True)  # {width: 6, height: 4}
    
    # État
    is_active = models.BooleanField(default=True)
    
    # Métadonnées
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'monitoring_dashboard_widget'
        ordering = ['position']
    
    def __str__(self):
        return f"{self.title} ({self.widget_type})"
    
    @property
    def is_metric_widget(self):
        """Vérifie si c'est un widget de métrique"""
        return self.widget_type == 'metric'
    
    @property
    def is_chart_widget(self):
        """Vérifie si c'est un widget de graphique"""
        return self.widget_type == 'chart'
    
    @property
    def is_table_widget(self):
        """Vérifie si c'est un widget de tableau"""
        return self.widget_type == 'table'
    
    def get_config_value(self, key, default=None):
        """Récupère une valeur de configuration"""
        return self.config.get(key, default)
    
    def set_config_value(self, key, value):
        """Définit une valeur de configuration"""
        self.config[key] = value
        self.save()
    
    def get_size(self):
        """Récupère la taille du widget"""
        return self.size or {'width': 6, 'height': 4}
    
    def set_size(self, width, height):
        """Définit la taille du widget"""
        self.size = {'width': width, 'height': height}
        self.save()
    
    def move_to_position(self, new_position):
        """Déplace le widget à une nouvelle position"""
        # Réorganiser les positions des autres widgets
        widgets = self.dashboard.widgets.exclude(id=self.id)
        
        if new_position < self.position:
            # Déplacer vers le haut
            widgets.filter(
                position__gte=new_position,
                position__lt=self.position
            ).update(position=models.F('position') + 1)
        else:
            # Déplacer vers le bas
            widgets.filter(
                position__gt=self.position,
                position__lte=new_position
            ).update(position=models.F('position') - 1)
        
        self.position = new_position
        self.save()



