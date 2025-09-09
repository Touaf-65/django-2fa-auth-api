"""
Modèles pour les tableaux de bord Analytics
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class AnalyticsDashboard(TimestampedModel):
    """Tableau de bord analytique personnalisable"""
    
    TYPE_CHOICES = [
        ('executive', 'Direction'),
        ('operational', 'Opérationnel'),
        ('technical', 'Technique'),
        ('security', 'Sécurité'),
        ('custom', 'Personnalisé'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    dashboard_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Configuration
    layout_config = models.JSONField(default=dict)
    refresh_interval = models.PositiveIntegerField(default=300)  # en secondes
    is_public = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    
    # Permissions
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_dashboards')
    shared_with = models.ManyToManyField(User, blank=True, related_name='shared_dashboards')
    
    # Métadonnées
    last_updated = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Tableau de Bord Analytics"
        verbose_name_plural = "Tableaux de Bord Analytics"
        ordering = ['name']
        indexes = [
            models.Index(fields=['dashboard_type', 'is_public']),
            models.Index(fields=['owner', 'created_at']),
        ]
    
    def __str__(self):
        return self.name


class DashboardWidget(TimestampedModel):
    """Widget individuel dans un tableau de bord"""
    
    WIDGET_TYPE_CHOICES = [
        ('chart', 'Graphique'),
        ('metric', 'Métrique'),
        ('table', 'Tableau'),
        ('gauge', 'Jauge'),
        ('map', 'Carte'),
        ('text', 'Texte'),
        ('iframe', 'Iframe'),
    ]
    
    CHART_TYPE_CHOICES = [
        ('line', 'Ligne'),
        ('bar', 'Barres'),
        ('pie', 'Secteurs'),
        ('area', 'Aire'),
        ('scatter', 'Nuage de points'),
        ('heatmap', 'Carte de chaleur'),
    ]
    
    dashboard = models.ForeignKey(AnalyticsDashboard, on_delete=models.CASCADE, related_name='widgets')
    name = models.CharField(max_length=200)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPE_CHOICES)
    
    # Configuration du widget
    config = models.JSONField(default=dict)
    data_source = models.CharField(max_length=100, blank=True)
    query = models.TextField(blank=True)
    
    # Position et taille
    position_x = models.PositiveIntegerField(default=0)
    position_y = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=4)
    height = models.PositiveIntegerField(default=3)
    
    # Configuration du graphique
    chart_type = models.CharField(max_length=20, choices=CHART_TYPE_CHOICES, blank=True)
    x_axis = models.CharField(max_length=100, blank=True)
    y_axis = models.CharField(max_length=100, blank=True)
    
    # Filtres et paramètres
    filters = models.JSONField(default=dict)
    refresh_interval = models.PositiveIntegerField(null=True, blank=True)
    
    # État
    is_visible = models.BooleanField(default=True)
    is_loading = models.BooleanField(default=False)
    last_updated = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Widget de Tableau de Bord"
        verbose_name_plural = "Widgets de Tableau de Bord"
        ordering = ['position_y', 'position_x']
        indexes = [
            models.Index(fields=['dashboard', 'widget_type']),
            models.Index(fields=['data_source']),
        ]
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.name}"
