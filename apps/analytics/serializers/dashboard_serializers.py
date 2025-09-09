"""
Serializers pour les tableaux de bord Analytics
"""
from rest_framework import serializers
from apps.analytics.models import AnalyticsDashboard, DashboardWidget


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer pour les widgets de tableau de bord"""
    chart_type_display = serializers.CharField(source='get_chart_type_display', read_only=True)
    widget_type_display = serializers.CharField(source='get_widget_type_display', read_only=True)
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'dashboard', 'name', 'widget_type', 'widget_type_display', 'config',
            'data_source', 'query', 'position_x', 'position_y', 'width', 'height',
            'chart_type', 'chart_type_display', 'x_axis', 'y_axis', 'filters',
            'refresh_interval', 'is_visible', 'is_loading', 'last_updated', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_loading', 'last_updated', 'error_message', 'created_at', 'updated_at'
        ]


class DashboardWidgetCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de widgets"""
    
    class Meta:
        model = DashboardWidget
        fields = [
            'name', 'widget_type', 'config', 'data_source', 'query',
            'position_x', 'position_y', 'width', 'height', 'chart_type',
            'x_axis', 'y_axis', 'filters', 'refresh_interval', 'is_visible'
        ]
    
    def validate(self, data):
        """Validation personnalisée"""
        widget_type = data.get('widget_type')
        chart_type = data.get('chart_type')
        
        # Vérifier que le type de graphique est compatible avec le type de widget
        if widget_type == 'chart' and not chart_type:
            raise serializers.ValidationError(
                "Le type de graphique est requis pour les widgets de type 'chart'"
            )
        
        return data


class AnalyticsDashboardSerializer(serializers.ModelSerializer):
    """Serializer pour les tableaux de bord"""
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    dashboard_type_display = serializers.CharField(source='get_dashboard_type_display', read_only=True)
    widgets = DashboardWidgetSerializer(many=True, read_only=True)
    shared_with_emails = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyticsDashboard
        fields = [
            'id', 'name', 'description', 'dashboard_type', 'dashboard_type_display',
            'layout_config', 'refresh_interval', 'is_public', 'is_default',
            'owner', 'owner_email', 'shared_with', 'shared_with_emails', 'widgets',
            'last_updated', 'view_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_updated', 'view_count', 'created_at', 'updated_at'
        ]
    
    def get_shared_with_emails(self, obj):
        """Récupère les emails des utilisateurs avec qui le tableau de bord est partagé"""
        return [user.email for user in obj.shared_with.all()]


class AnalyticsDashboardCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de tableaux de bord"""
    
    class Meta:
        model = AnalyticsDashboard
        fields = [
            'name', 'description', 'dashboard_type', 'layout_config',
            'refresh_interval', 'is_public', 'is_default'
        ]
    
    def validate(self, data):
        """Validation personnalisée"""
        # Vérifier qu'il n'y a qu'un seul tableau de bord par défaut par type
        if data.get('is_default'):
            dashboard_type = data.get('dashboard_type')
            if AnalyticsDashboard.objects.filter(
                dashboard_type=dashboard_type,
                is_default=True
            ).exists():
                raise serializers.ValidationError(
                    f"Un tableau de bord par défaut existe déjà pour le type '{dashboard_type}'"
                )
        
        return data


class DashboardDataSerializer(serializers.Serializer):
    """Serializer pour les données de tableau de bord"""
    dashboard = AnalyticsDashboardSerializer()
    widgets = serializers.ListField(child=serializers.DictField())
    metadata = serializers.DictField()


class WidgetDataSerializer(serializers.Serializer):
    """Serializer pour les données de widget"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    type = serializers.CharField()
    data = serializers.DictField()
    config = serializers.DictField()
    position = serializers.DictField()
    last_updated = serializers.DateTimeField()
    error = serializers.CharField(required=False)


class DashboardShareSerializer(serializers.Serializer):
    """Serializer pour le partage de tableaux de bord"""
    user_emails = serializers.ListField(
        child=serializers.EmailField(),
        help_text="Liste des emails des utilisateurs avec qui partager le tableau de bord"
    )
    
    def validate_user_emails(self, value):
        """Validation des emails"""
        if not value:
            raise serializers.ValidationError("Au moins un email est requis")
        
        # Vérifier que les utilisateurs existent
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        existing_emails = User.objects.filter(email__in=value).values_list('email', flat=True)
        invalid_emails = set(value) - set(existing_emails)
        
        if invalid_emails:
            raise serializers.ValidationError(
                f"Utilisateurs non trouvés: {', '.join(invalid_emails)}"
            )
        
        return value


class DashboardLayoutSerializer(serializers.Serializer):
    """Serializer pour la mise en page des tableaux de bord"""
    widgets = serializers.ListField(
        child=serializers.DictField(),
        help_text="Liste des widgets avec leurs positions et tailles"
    )
    
    def validate_widgets(self, value):
        """Validation de la mise en page des widgets"""
        if not value:
            raise serializers.ValidationError("Au moins un widget est requis")
        
        # Vérifier que tous les widgets ont les champs requis
        required_fields = ['id', 'position_x', 'position_y', 'width', 'height']
        for widget in value:
            for field in required_fields:
                if field not in widget:
                    raise serializers.ValidationError(
                        f"Le champ '{field}' est requis pour tous les widgets"
                    )
        
        return value


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer pour les résumés de tableaux de bord"""
    total_dashboards = serializers.IntegerField()
    public_dashboards = serializers.IntegerField()
    private_dashboards = serializers.IntegerField()
    total_widgets = serializers.IntegerField()
    most_viewed_dashboard = serializers.CharField()
    recent_dashboards = AnalyticsDashboardSerializer(many=True)

