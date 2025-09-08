"""
Vues API pour la gestion des logs
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
import csv
import json

from apps.monitoring.models import LogEntry
from apps.monitoring.serializers import LogEntrySerializer, LogEntrySearchSerializer
from apps.monitoring.services import LoggingService
from core.permissions import IsStaffOrReadOnly


class LogEntryListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des entrées de log"""
    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['level', 'source', 'user', 'app_name', 'created_at']
    
    def get_queryset(self):
        """Filtre les logs selon les permissions"""
        queryset = super().get_queryset()
        
        # Les utilisateurs non-staff ne voient que leurs propres logs
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset.order_by('-created_at')


class LogEntryRetrieveView(generics.RetrieveAPIView):
    """Vue pour récupérer une entrée de log spécifique"""
    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    
    def get_queryset(self):
        """Filtre les logs selon les permissions"""
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset


class LogEntrySearchView(generics.ListAPIView):
    """Vue pour rechercher dans les logs"""
    serializer_class = LogEntrySerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    
    def get_queryset(self):
        """Recherche dans les logs"""
        logging_service = LoggingService()
        
        query = self.request.query_params.get('q', '')
        level = self.request.query_params.get('level')
        source = self.request.query_params.get('source')
        hours = int(self.request.query_params.get('hours', 24))
        limit = int(self.request.query_params.get('limit', 100))
        
        if query:
            logs = logging_service.search_logs(
                query=query,
                level=level,
                source=source,
                hours=hours,
                limit=limit
            )
        else:
            logs = logging_service.get_logs(
                level=level,
                source=source,
                hours=hours,
                limit=limit
            )
        
        # Filtrer selon les permissions
        if not self.request.user.is_staff:
            logs = logs.filter(user=self.request.user)
        
        return logs


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def log_statistics_view(request):
    """Vue pour les statistiques des logs"""
    logging_service = LoggingService()
    hours = int(request.query_params.get('hours', 24))
    
    stats = logging_service.get_log_statistics(hours=hours)
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def log_export_view(request):
    """Vue pour exporter les logs"""
    logging_service = LoggingService()
    
    # Paramètres d'export
    level = request.query_params.get('level')
    source = request.query_params.get('source')
    hours = int(request.query_params.get('hours', 24))
    format_type = request.query_params.get('format', 'csv')
    
    # Récupérer les logs
    logs = logging_service.get_logs(
        level=level,
        source=source,
        hours=hours,
        limit=10000  # Limite pour l'export
    )
    
    # Filtrer selon les permissions
    if not request.user.is_staff:
        logs = logs.filter(user=request.user)
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="logs_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Timestamp', 'Level', 'Source', 'Message', 'User', 'IP Address',
            'Method', 'Path', 'Status Code', 'Response Time'
        ])
        
        for log in logs:
            writer.writerow([
                log.created_at.isoformat(),
                log.level,
                log.source,
                log.message,
                log.user.email if log.user else '',
                log.ip_address or '',
                log.method or '',
                log.path or '',
                log.status_code or '',
                log.response_time or '',
            ])
        
        return response
    
    elif format_type == 'json':
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="logs_export.json"'
        
        logs_data = []
        for log in logs:
            logs_data.append({
                'timestamp': log.created_at.isoformat(),
                'level': log.level,
                'source': log.source,
                'message': log.message,
                'user': log.user.email if log.user else None,
                'ip_address': log.ip_address,
                'method': log.method,
                'path': log.path,
                'status_code': log.status_code,
                'response_time': log.response_time,
                'metadata': log.metadata,
                'tags': log.tags,
            })
        
        response.write(json.dumps(logs_data, indent=2))
        return response
    
    else:
        return Response(
            {'error': 'Unsupported format. Use csv or json.'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_create_view(request):
    """Vue pour créer un log via API"""
    logging_service = LoggingService()
    
    level = request.data.get('level', 'INFO')
    message = request.data.get('message')
    source = request.data.get('source', 'api')
    
    if not message:
        return Response(
            {'error': 'Message is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Créer le log
    log_entry = logging_service.log(
        level=level,
        message=message,
        source=source,
        user=request.user,
        request=request,
        metadata=request.data.get('metadata', {}),
        tags=request.data.get('tags', []),
    )
    
    serializer = LogEntrySerializer(log_entry)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
