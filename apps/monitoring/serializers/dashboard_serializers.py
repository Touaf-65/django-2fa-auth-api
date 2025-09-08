"""
Serializers pour les tableaux de bord
"""
from rest_framework import serializers
from apps.monitoring.models import Dashboard, DashboardWidget


class DashboardSerializer(serializers.ModelSerializer):
    """Serializer pour les tableaux de bord"""
    
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    is_private = serializers.BooleanField(read_only=True)
    is_shared = serializers.BooleanField(read_only=True)
    is_public = serializers.BooleanField(read_only=True)
    widgets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'owner', 'owner_email', 'visibility',
            'is_active', 'refresh_interval', 'layout_config', 'tags', 'metadata',
            'is_private', 'is_shared', 'is_public', 'widgets_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_widgets_count(self, obj):
        """Récupère le nombre de widgets"""
        return obj.widgets.filter(is_active=True).count()
    
    def create(self, validated_data):
        """Crée un nouveau tableau de bord"""
        # Extraire les métadonnées et tags
        tags = validated_data.pop('tags', [])
        metadata = validated_data.pop('metadata', {})
        layout_config = validated_data.pop('layout_config', {})
        
        dashboard = Dashboard.objects.create(
            **validated_data,
            tags=tags,
            metadata=metadata,
            layout_config=layout_config
        )
        
        return dashboard


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer pour les widgets de tableau de bord"""
    
    dashboard_name = serializers.CharField(source='dashboard.name', read_only=True)
    is_metric_widget = serializers.BooleanField(read_only=True)
    is_chart_widget = serializers.BooleanField(read_only=True)
    is_table_widget = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'dashboard', 'dashboard_name', 'widget_type', 'title',
            'description', 'config', 'position', 'size', 'is_active',
            'metadata', 'is_metric_widget', 'is_chart_widget', 'is_table_widget',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Crée un nouveau widget"""
        # Extraire les métadonnées et configuration
        metadata = validated_data.pop('metadata', {})
        config = validated_data.pop('config', {})
        size = validated_data.pop('size', {'width': 6, 'height': 4})
        
        widget = DashboardWidget.objects.create(
            **validated_data,
            metadata=metadata,
            config=config,
            size=size
        )
        
        return widget


class DashboardCreateSerializer(serializers.Serializer):
    """Serializer pour créer un tableau de bord"""
    
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.ChoiceField(choices=Dashboard.VISIBILITY_CHOICES, default='private')
    is_active = serializers.BooleanField(default=True)
    refresh_interval = serializers.IntegerField(min_value=1, max_value=3600, default=30)
    layout_config = serializers.JSONField(default=dict, required=False)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        default=list,
        required=False
    )
    metadata = serializers.JSONField(default=dict, required=False)
    
    def validate_name(self, value):
        """Valide le nom du tableau de bord"""
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        return value.strip()
    
    def validate_refresh_interval(self, value):
        """Valide l'intervalle de rafraîchissement"""
        if value < 1:
            raise serializers.ValidationError("Refresh interval must be at least 1 second")
        if value > 3600:  # 1 heure maximum
            raise serializers.ValidationError("Refresh interval cannot exceed 1 hour")
        return value


class DashboardWidgetCreateSerializer(serializers.Serializer):
    """Serializer pour créer un widget"""
    
    dashboard_id = serializers.IntegerField()
    widget_type = serializers.ChoiceField(choices=DashboardWidget.WIDGET_TYPE_CHOICES)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    config = serializers.JSONField(default=dict, required=False)
    position = serializers.IntegerField(min_value=0, required=False)
    size = serializers.JSONField(default=dict, required=False)
    metadata = serializers.JSONField(default=dict, required=False)
    
    def validate_dashboard_id(self, value):
        """Valide l'ID du tableau de bord"""
        try:
            Dashboard.objects.get(id=value)
        except Dashboard.DoesNotExist:
            raise serializers.ValidationError("Dashboard not found")
        return value
    
    def validate_title(self, value):
        """Valide le titre du widget"""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()
    
    def validate_size(self, value):
        """Valide la taille du widget"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Size must be a dictionary")
        
        if 'width' not in value or 'height' not in value:
            raise serializers.ValidationError("Size must contain 'width' and 'height'")
        
        width = value.get('width')
        height = value.get('height')
        
        if not isinstance(width, int) or not isinstance(height, int):
            raise serializers.ValidationError("Width and height must be integers")
        
        if width < 1 or width > 12:
            raise serializers.ValidationError("Width must be between 1 and 12")
        
        if height < 1 or height > 12:
            raise serializers.ValidationError("Height must be between 1 and 12")
        
        return value


class DashboardCloneSerializer(serializers.Serializer):
    """Serializer pour cloner un tableau de bord"""
    
    name = serializers.CharField(max_length=200)
    
    def validate_name(self, value):
        """Valide le nom du nouveau tableau de bord"""
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        return value.strip()


class DashboardReorderSerializer(serializers.Serializer):
    """Serializer pour réorganiser les widgets"""
    
    widget_positions = serializers.DictField(
        child=serializers.IntegerField(min_value=0)
    )
    
    def validate_widget_positions(self, value):
        """Valide les positions des widgets"""
        if not value:
            raise serializers.ValidationError("widget_positions cannot be empty")
        
        # Vérifier que toutes les positions sont uniques
        positions = list(value.values())
        if len(positions) != len(set(positions)):
            raise serializers.ValidationError("Widget positions must be unique")
        
        return value


class DashboardDataSerializer(serializers.Serializer):
    """Serializer pour les données d'un tableau de bord"""
    
    dashboard = serializers.DictField()
    widgets = serializers.ListField(
        child=serializers.DictField()
    )


class WidgetDataSerializer(serializers.Serializer):
    """Serializer pour les données d'un widget"""
    
    id = serializers.IntegerField()
    type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    position = serializers.IntegerField()
    size = serializers.DictField()
    config = serializers.DictField()
    data = serializers.JSONField(required=False, allow_null=True)


class DashboardStatisticsSerializer(serializers.Serializer):
    """Serializer pour les statistiques des tableaux de bord"""
    
    total_dashboards = serializers.IntegerField()
    active_dashboards = serializers.IntegerField()
    public_dashboards = serializers.IntegerField()
    shared_dashboards = serializers.IntegerField()
    private_dashboards = serializers.IntegerField()
    total_widgets = serializers.IntegerField()
    active_widgets = serializers.IntegerField()
    widgets_by_type = serializers.ListField(
        child=serializers.DictField()
    )


