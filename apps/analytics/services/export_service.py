"""
Service pour l'export de données Analytics
"""
import csv
import json
import xlsxwriter
import io
import os
import time
from datetime import datetime, timedelta
from django.db import connection
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings

from apps.analytics.models import DataExport, ExportFormat
from apps.analytics.services.analytics_service import AnalyticsService

User = get_user_model()


class ExportService:
    """Service pour l'export de données"""
    
    def __init__(self):
        self.analytics_service = AnalyticsService()
        self.export_formats = {
            'csv': self._export_to_csv,
            'excel': self._export_to_excel,
            'json': self._export_to_json,
            'xml': self._export_to_xml,
        }
    
    def create_export(self, name, data_source, export_format, user, **kwargs):
        """Crée un nouvel export"""
        try:
            format_obj = ExportFormat.objects.get(name=export_format, is_active=True)
            
            export = DataExport.objects.create(
                name=name,
                export_format=format_obj,
                data_source=data_source,
                requested_by=user,
                **kwargs
            )
            
            return export
            
        except ExportFormat.DoesNotExist:
            raise ValueError(f"Format d'export '{export_format}' non supporté")
    
    def process_export(self, export_id):
        """Traite un export"""
        try:
            export = DataExport.objects.get(id=export_id)
            export.status = 'processing'
            export.save()
            
            start_time = time.time()
            
            # Générer les données selon la source
            data = self._get_export_data(export)
            
            # Exporter selon le format
            if export.export_format.format_type in self.export_formats:
                file_content = self.export_formats[export.export_format.format_type](data, export)
            else:
                raise ValueError(f"Format d'export non supporté: {export.export_format.format_type}")
            
            # Sauvegarder le fichier
            file_path = self._save_export_file(export, file_content)
            
            # Mettre à jour l'export
            execution_time = time.time() - start_time
            export.status = 'completed'
            export.file_path = file_path
            export.file_name = f"{export.name}.{export.export_format.file_extension}"
            export.file_size = len(file_content)
            export.processed_at = timezone.now()
            export.execution_time = execution_time
            export.save()
            
            return export
            
        except Exception as e:
            if 'export' in locals():
                export.status = 'failed'
                export.error_message = str(e)
                export.save()
            raise e
    
    def _get_export_data(self, export):
        """Récupère les données à exporter"""
        if export.data_source == 'user_activity':
            return self._get_user_activity_data(export)
        elif export.data_source == 'security_events':
            return self._get_security_events_data(export)
        elif export.data_source == 'performance_metrics':
            return self._get_performance_metrics_data(export)
        elif export.data_source == 'api_logs':
            return self._get_api_logs_data(export)
        elif export.data_source == 'custom_query':
            return self._get_custom_query_data(export)
        else:
            raise ValueError(f"Source de données non supportée: {export.data_source}")
    
    def _get_user_activity_data(self, export):
        """Récupère les données d'activité utilisateur"""
        from apps.authentication.models import User
        from apps.monitoring.models import LogEntry
        
        query = User.objects.all()
        
        # Appliquer les filtres
        if export.filters:
            if 'is_active' in export.filters:
                query = query.filter(is_active=export.filters['is_active'])
            if 'date_joined_after' in export.filters:
                query = query.filter(date_joined__gte=export.filters['date_joined_after'])
        
        # Appliquer la plage de dates
        if export.date_range_start:
            query = query.filter(date_joined__gte=export.date_range_start)
        if export.date_range_end:
            query = query.filter(date_joined__lte=export.date_range_end)
        
        # Sélectionner les colonnes
        columns = export.columns or ['id', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'last_login']
        
        data = []
        for user in query:
            row = {}
            for column in columns:
                if hasattr(user, column):
                    value = getattr(user, column)
                    if isinstance(value, datetime):
                        row[column] = value.isoformat()
                    else:
                        row[column] = value
                else:
                    row[column] = None
            data.append(row)
        
        return {
            'data': data,
            'columns': columns,
            'total_count': len(data)
        }
    
    def _get_security_events_data(self, export):
        """Récupère les données d'événements de sécurité"""
        from apps.security.models import SecurityEvent
        
        query = SecurityEvent.objects.all()
        
        # Appliquer la plage de dates
        if export.date_range_start:
            query = query.filter(created_at__gte=export.date_range_start)
        if export.date_range_end:
            query = query.filter(created_at__lte=export.date_range_end)
        
        # Appliquer les filtres
        if export.filters:
            if 'event_type' in export.filters:
                query = query.filter(event_type=export.filters['event_type'])
            if 'severity' in export.filters:
                query = query.filter(severity=export.filters['severity'])
        
        columns = export.columns or ['id', 'event_type', 'severity', 'description', 'ip_address', 'user_agent', 'created_at']
        
        data = []
        for event in query:
            row = {}
            for column in columns:
                if hasattr(event, column):
                    value = getattr(event, column)
                    if isinstance(value, datetime):
                        row[column] = value.isoformat()
                    else:
                        row[column] = value
                else:
                    row[column] = None
            data.append(row)
        
        return {
            'data': data,
            'columns': columns,
            'total_count': len(data)
        }
    
    def _get_performance_metrics_data(self, export):
        """Récupère les données de métriques de performance"""
        from apps.analytics.models import MetricValue
        
        query = MetricValue.objects.all()
        
        # Appliquer la plage de dates
        if export.date_range_start:
            query = query.filter(timestamp__gte=export.date_range_start)
        if export.date_range_end:
            query = query.filter(timestamp__lte=export.date_range_end)
        
        # Appliquer les filtres
        if export.filters:
            if 'metric_name' in export.filters:
                query = query.filter(metric__name=export.filters['metric_name'])
        
        columns = export.columns or ['metric__name', 'value', 'timestamp', 'labels', 'source']
        
        data = []
        for metric_value in query:
            row = {}
            for column in columns:
                if '__' in column:
                    # Relation
                    parts = column.split('__')
                    value = metric_value
                    for part in parts:
                        value = getattr(value, part, None)
                        if value is None:
                            break
                elif hasattr(metric_value, column):
                    value = getattr(metric_value, column)
                else:
                    value = None
                
                if isinstance(value, datetime):
                    row[column] = value.isoformat()
                elif isinstance(value, dict):
                    row[column] = json.dumps(value)
                else:
                    row[column] = value
            data.append(row)
        
        return {
            'data': data,
            'columns': columns,
            'total_count': len(data)
        }
    
    def _get_api_logs_data(self, export):
        """Récupère les données de logs API"""
        from apps.monitoring.models import LogEntry
        
        query = LogEntry.objects.filter(source='api')
        
        # Appliquer la plage de dates
        if export.date_range_start:
            query = query.filter(created_at__gte=export.date_range_start)
        if export.date_range_end:
            query = query.filter(created_at__lte=export.date_range_end)
        
        # Appliquer les filtres
        if export.filters:
            if 'level' in export.filters:
                query = query.filter(level=export.filters['level'])
            if 'method' in export.filters:
                query = query.filter(method=export.filters['method'])
        
        columns = export.columns or ['id', 'level', 'message', 'user__email', 'ip_address', 'method', 'path', 'status_code', 'response_time', 'created_at']
        
        data = []
        for log in query:
            row = {}
            for column in columns:
                if '__' in column:
                    # Relation
                    parts = column.split('__')
                    value = log
                    for part in parts:
                        value = getattr(value, part, None)
                        if value is None:
                            break
                elif hasattr(log, column):
                    value = getattr(log, column)
                else:
                    value = None
                
                if isinstance(value, datetime):
                    row[column] = value.isoformat()
                elif isinstance(value, dict):
                    row[column] = json.dumps(value)
                else:
                    row[column] = value
            data.append(row)
        
        return {
            'data': data,
            'columns': columns,
            'total_count': len(data)
        }
    
    def _get_custom_query_data(self, export):
        """Récupère les données via une requête personnalisée"""
        if not export.query:
            raise ValueError("Requête personnalisée requise")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(export.query)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                
                data = []
                for row in rows:
                    row_dict = {}
                    for i, value in enumerate(row):
                        if isinstance(value, datetime):
                            row_dict[columns[i]] = value.isoformat()
                        else:
                            row_dict[columns[i]] = value
                    data.append(row_dict)
                
                return {
                    'data': data,
                    'columns': columns,
                    'total_count': len(data)
                }
        except Exception as e:
            raise Exception(f"Erreur dans la requête personnalisée: {str(e)}")
    
    def _export_to_csv(self, data, export):
        """Exporte les données en CSV"""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data['columns'])
        writer.writeheader()
        writer.writerows(data['data'])
        
        return output.getvalue().encode('utf-8')
    
    def _export_to_excel(self, data, export):
        """Exporte les données en Excel"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        
        # Écrire les en-têtes
        for col, header in enumerate(data['columns']):
            worksheet.write(0, col, header)
        
        # Écrire les données
        for row, row_data in enumerate(data['data'], 1):
            for col, column in enumerate(data['columns']):
                value = row_data.get(column, '')
                worksheet.write(row, col, value)
        
        workbook.close()
        return output.getvalue()
    
    def _export_to_json(self, data, export):
        """Exporte les données en JSON"""
        return json.dumps({
            'export_info': {
                'name': export.name,
                'data_source': export.data_source,
                'total_count': data['total_count'],
                'exported_at': timezone.now().isoformat()
            },
            'columns': data['columns'],
            'data': data['data']
        }, indent=2, ensure_ascii=False).encode('utf-8')
    
    def _export_to_xml(self, data, export):
        """Exporte les données en XML"""
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<export>
    <info>
        <name>{export.name}</name>
        <data_source>{export.data_source}</data_source>
        <total_count>{data['total_count']}</total_count>
        <exported_at>{timezone.now().isoformat()}</exported_at>
    </info>
    <data>"""
        
        for row in data['data']:
            xml_content += "\n        <row>"
            for column in data['columns']:
                value = row.get(column, '')
                xml_content += f"\n            <{column}>{value}</{column}>"
            xml_content += "\n        </row>"
        
        xml_content += "\n    </data>\n</export>"
        
        return xml_content.encode('utf-8')
    
    def _save_export_file(self, export, content):
        """Sauvegarde le fichier d'export"""
        # Créer le répertoire d'exports s'il n'existe pas
        export_dir = os.path.join(settings.MEDIA_ROOT, 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        # Générer un nom de fichier unique
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{export.id}_{timestamp}.{export.export_format.file_extension}"
        file_path = os.path.join(export_dir, filename)
        
        # Écrire le fichier
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return file_path
    
    def get_export_file_response(self, export):
        """Retourne une réponse HTTP pour télécharger le fichier d'export"""
        if not export.file_path or not os.path.exists(export.file_path):
            raise FileNotFoundError("Fichier d'export non trouvé")
        
        with open(export.file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=export.export_format.mime_type)
            response['Content-Disposition'] = f'attachment; filename="{export.file_name}"'
            return response
    
    def cleanup_expired_exports(self):
        """Nettoie les exports expirés"""
        expired_exports = DataExport.objects.filter(
            expires_at__lt=timezone.now(),
            status='completed'
        )
        
        for export in expired_exports:
            if export.file_path and os.path.exists(export.file_path):
                try:
                    os.remove(export.file_path)
                except OSError:
                    pass  # Ignorer les erreurs de suppression
            
            export.status = 'expired'
            export.save()
        
        return expired_exports.count()
