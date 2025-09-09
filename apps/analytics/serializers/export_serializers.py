"""
Serializers pour l'export de données Analytics
"""
from rest_framework import serializers
from apps.analytics.models import DataExport, ExportFormat


class ExportFormatSerializer(serializers.ModelSerializer):
    """Serializer pour les formats d'export"""
    
    class Meta:
        model = ExportFormat
        fields = [
            'id', 'name', 'format_type', 'description', 'mime_type',
            'file_extension', 'template_path', 'config', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DataExportSerializer(serializers.ModelSerializer):
    """Serializer pour les exports de données"""
    requested_by_email = serializers.EmailField(source='requested_by.email', read_only=True)
    export_format_name = serializers.CharField(source='export_format.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    file_size_display = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DataExport
        fields = [
            'id', 'name', 'description', 'export_format', 'export_format_name',
            'status', 'status_display', 'data_source', 'query', 'filters',
            'columns', 'date_range_start', 'date_range_end', 'file_path',
            'file_name', 'file_size', 'file_size_display', 'download_count',
            'requested_by', 'requested_by_email', 'processed_at', 'expires_at',
            'execution_time', 'error_message', 'include_metadata',
            'compression_enabled', 'password_protected', 'download_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'file_path', 'file_name', 'file_size',
            'download_count', 'processed_at', 'execution_time', 'error_message',
            'created_at', 'updated_at'
        ]
    
    def get_file_size_display(self, obj):
        """Formate la taille du fichier"""
        if not obj.file_size:
            return "N/A"
        
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_download_url(self, obj):
        """Génère l'URL de téléchargement"""
        if obj.status == 'completed' and obj.file_path:
            return f"/api/analytics/exports/{obj.id}/download/"
        return None


class DataExportCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'exports"""
    
    class Meta:
        model = DataExport
        fields = [
            'name', 'description', 'export_format', 'data_source', 'query',
            'filters', 'columns', 'date_range_start', 'date_range_end',
            'include_metadata', 'compression_enabled', 'password_protected'
        ]
    
    def validate(self, data):
        """Validation personnalisée"""
        export_format = data.get('export_format')
        data_source = data.get('data_source')
        
        # Vérifier que le format d'export est actif
        if not export_format.is_active:
            raise serializers.ValidationError(
                "Le format d'export sélectionné n'est pas actif"
            )
        
        # Vérifier que la source de données est supportée
        supported_sources = [
            'user_activity', 'security_events', 'performance_metrics',
            'api_logs', 'custom_query'
        ]
        if data_source not in supported_sources:
            raise serializers.ValidationError(
                f"Source de données non supportée. Sources disponibles: {', '.join(supported_sources)}"
            )
        
        # Pour les requêtes personnalisées, vérifier que la requête est fournie
        if data_source == 'custom_query' and not data.get('query'):
            raise serializers.ValidationError(
                "Une requête personnalisée est requise pour la source 'custom_query'"
            )
        
        return data


class ExportRequestSerializer(serializers.Serializer):
    """Serializer pour les demandes d'export rapide"""
    data_source = serializers.ChoiceField(choices=[
        ('user_activity', 'Activité Utilisateur'),
        ('security_events', 'Événements de Sécurité'),
        ('performance_metrics', 'Métriques de Performance'),
        ('api_logs', 'Logs API'),
    ])
    export_format = serializers.ChoiceField(choices=[
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
    ])
    date_range_days = serializers.IntegerField(min_value=1, max_value=365, default=30)
    filters = serializers.DictField(required=False, default=dict)
    columns = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Liste des colonnes à inclure dans l'export"
    )


class ExportStatusSerializer(serializers.Serializer):
    """Serializer pour le statut d'export"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    status = serializers.CharField()
    status_display = serializers.CharField()
    progress = serializers.FloatField(required=False)
    estimated_completion = serializers.DateTimeField(required=False)
    error_message = serializers.CharField(required=False)


class ExportSummarySerializer(serializers.Serializer):
    """Serializer pour les résumés d'export"""
    total_exports = serializers.IntegerField()
    completed_exports = serializers.IntegerField()
    failed_exports = serializers.IntegerField()
    pending_exports = serializers.IntegerField()
    total_downloads = serializers.IntegerField()
    most_used_format = serializers.CharField()
    recent_exports = DataExportSerializer(many=True)


class ExportTemplateSerializer(serializers.Serializer):
    """Serializer pour les templates d'export"""
    name = serializers.CharField()
    data_source = serializers.CharField()
    export_format = serializers.CharField()
    default_filters = serializers.DictField()
    default_columns = serializers.ListField(child=serializers.CharField())
    description = serializers.CharField()


class BulkExportSerializer(serializers.Serializer):
    """Serializer pour les exports en lot"""
    exports = serializers.ListField(
        child=ExportRequestSerializer(),
        min_length=1,
        max_length=10,
        help_text="Liste des exports à créer (maximum 10)"
    )
    
    def validate_exports(self, value):
        """Validation des exports en lot"""
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 exports autorisés par lot")
        
        # Vérifier qu'il n'y a pas de doublons
        export_keys = []
        for export in value:
            key = f"{export['data_source']}_{export['export_format']}"
            if key in export_keys:
                raise serializers.ValidationError(
                    f"Export en double détecté: {export['data_source']} en {export['export_format']}"
                )
            export_keys.append(key)
        
        return value

