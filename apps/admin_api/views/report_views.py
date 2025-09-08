"""
Vues API pour les rapports automatiques
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from core.permissions import IsStaffOrReadOnly
from apps.admin_api.models import ReportTemplate, ScheduledReport, ReportExecution
from apps.admin_api.services import ReportService
from apps.admin_api.serializers import (
    ReportTemplateSerializer,
    ReportTemplateListSerializer,
    ReportTemplateCreateSerializer,
    ScheduledReportSerializer,
    ScheduledReportListSerializer,
    ScheduledReportCreateSerializer,
    ReportExecutionSerializer,
    ReportExecutionListSerializer,
)


class ReportTemplateListAPIView(generics.ListAPIView):
    """Liste des templates de rapport"""
    queryset = ReportTemplate.objects.filter(is_active=True)
    serializer_class = ReportTemplateListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['report_type', 'format', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ReportTemplateCreateAPIView(generics.CreateAPIView):
    """Créer un template de rapport"""
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateCreateSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ReportTemplateRetrieveAPIView(generics.RetrieveAPIView):
    """Récupérer un template de rapport"""
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class ReportTemplateUpdateAPIView(generics.UpdateAPIView):
    """Mettre à jour un template de rapport"""
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class ReportTemplateDestroyAPIView(generics.DestroyAPIView):
    """Supprimer un template de rapport"""
    queryset = ReportTemplate.objects.all()
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class ScheduledReportListAPIView(generics.ListAPIView):
    """Liste des rapports programmés"""
    queryset = ScheduledReport.objects.all()
    serializer_class = ScheduledReportListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['frequency', 'status', 'template__report_type']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'next_run', 'last_run']
    ordering = ['-created_at']


class ScheduledReportCreateAPIView(generics.CreateAPIView):
    """Créer un rapport programmé"""
    queryset = ScheduledReport.objects.all()
    serializer_class = ScheduledReportCreateSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    
    def perform_create(self, serializer):
        scheduled_report = serializer.save(created_by=self.request.user)
        # Calcule la prochaine exécution
        scheduled_report.next_run = scheduled_report.calculate_next_run()
        scheduled_report.save()


class ScheduledReportRetrieveAPIView(generics.RetrieveAPIView):
    """Récupérer un rapport programmé"""
    queryset = ScheduledReport.objects.all()
    serializer_class = ScheduledReportSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class ScheduledReportUpdateAPIView(generics.UpdateAPIView):
    """Mettre à jour un rapport programmé"""
    queryset = ScheduledReport.objects.all()
    serializer_class = ScheduledReportSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class ScheduledReportDestroyAPIView(generics.DestroyAPIView):
    """Supprimer un rapport programmé"""
    queryset = ScheduledReport.objects.all()
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def execute_scheduled_report(request, report_id):
    """Exécuter un rapport programmé manuellement"""
    try:
        scheduled_report = ScheduledReport.objects.get(id=report_id)
        report_service = ReportService()
        
        execution = report_service.execute_scheduled_report(scheduled_report)
        
        return Response({
            'message': 'Exécution du rapport démarrée',
            'execution_id': execution.id,
            'status': execution.status
        })
    except ScheduledReport.DoesNotExist:
        return Response({'error': 'Rapport programmé non trouvé'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def generate_report(request, template_id):
    """Générer un rapport à partir d'un template"""
    try:
        template = ReportTemplate.objects.get(id=template_id)
        report_service = ReportService()
        
        # Récupère les paramètres depuis la requête
        parameters = request.data.get('parameters', {})
        
        result = report_service.generate_report(template, parameters)
        
        if result['success']:
            return Response({
                'message': 'Rapport généré avec succès',
                'file_path': result['file_path'],
                'record_count': result['record_count']
            })
        else:
            return Response({
                'error': 'Erreur lors de la génération du rapport',
                'details': result['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except ReportTemplate.DoesNotExist:
        return Response({'error': 'Template de rapport non trouvé'}, status=status.HTTP_404_NOT_FOUND)


class ReportExecutionListAPIView(generics.ListAPIView):
    """Liste des exécutions de rapport"""
    queryset = ReportExecution.objects.all()
    serializer_class = ReportExecutionListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'scheduled_report', 'template']
    ordering_fields = ['created_at', 'started_at', 'completed_at']
    ordering = ['-created_at']


class ReportExecutionRetrieveAPIView(generics.RetrieveAPIView):
    """Récupérer une exécution de rapport"""
    queryset = ReportExecution.objects.all()
    serializer_class = ReportExecutionSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def report_statistics(request):
    """Statistiques des rapports"""
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    
    stats = {
        'total_templates': ReportTemplate.objects.filter(is_active=True).count(),
        'total_scheduled_reports': ScheduledReport.objects.count(),
        'active_scheduled_reports': ScheduledReport.objects.filter(status='active').count(),
        'total_executions': ReportExecution.objects.count(),
        'successful_executions': ReportExecution.objects.filter(status='completed').count(),
        'failed_executions': ReportExecution.objects.filter(status='failed').count(),
        'executions_24h': ReportExecution.objects.filter(created_at__gte=last_24h).count(),
        'executions_7d': ReportExecution.objects.filter(created_at__gte=last_7d).count(),
        'executions_by_status': list(
            ReportExecution.objects.values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        ),
        'executions_by_template': list(
            ReportExecution.objects.values('template__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        ),
    }
    
    return Response(stats)
