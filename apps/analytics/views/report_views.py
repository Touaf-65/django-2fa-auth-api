"""
Vues API pour les rapports Analytics
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.db import models

from apps.analytics.models import Report, ReportTemplate, ReportSchedule
from apps.analytics.serializers import (
    ReportSerializer, ReportCreateSerializer, ReportTemplateSerializer,
    ReportScheduleSerializer, ReportScheduleCreateSerializer, ReportSummarySerializer
)
from apps.analytics.services import ReportService


class ReportTemplateListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des templates de rapports"""
    queryset = ReportTemplate.objects.filter(is_active=True)
    serializer_class = ReportTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les templates selon les permissions"""
        queryset = super().get_queryset()
        
        # Filtrer par type de rapport si spécifié
        report_type = self.request.query_params.get('report_type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        return queryset
    
    def perform_create(self, serializer):
        """Associe l'utilisateur créateur"""
        serializer.save(created_by=self.request.user)


class ReportTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour les détails d'un template de rapport"""
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_update(self, serializer):
        """Vérifie les permissions de modification"""
        if serializer.instance.created_by != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez modifier que vos propres templates")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Marque le template comme inactif au lieu de le supprimer"""
        if instance.created_by != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez supprimer que vos propres templates")
        instance.is_active = False
        instance.save()


class ReportListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des rapports"""
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les rapports selon les permissions"""
        queryset = Report.objects.all()
        
        # L'utilisateur ne voit que ses propres rapports
        queryset = queryset.filter(generated_by=self.request.user)
        
        # Filtrer par statut si spécifié
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filtrer par type de rapport si spécifié
        report_type = self.request.query_params.get('report_type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        # Filtrer par date si spécifié
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Associe l'utilisateur créateur"""
        serializer.save(generated_by=self.request.user)


class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour les détails d'un rapport"""
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les rapports selon les permissions"""
        return Report.objects.filter(generated_by=self.request.user)
    
    def perform_update(self, serializer):
        """Vérifie les permissions de modification"""
        if serializer.instance.generated_by != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez modifier que vos propres rapports")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Vérifie les permissions de suppression"""
        if instance.generated_by != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez supprimer que vos propres rapports")
        instance.delete()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_report(request, report_id):
    """Génère un rapport"""
    try:
        report = get_object_or_404(Report, id=report_id, generated_by=request.user)
        
        if report.status == 'generating':
            return Response(
                {'error': 'Le rapport est déjà en cours de génération'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Générer le rapport
        report_service = ReportService()
        generated_report = report_service.generate_report(report.id, request.user)
        
        serializer = ReportSerializer(generated_report)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def report_data(request, report_id):
    """Récupère les données d'un rapport"""
    try:
        report = get_object_or_404(Report, id=report_id, generated_by=request.user)
        
        if report.status != 'completed':
            return Response(
                {'error': 'Le rapport n\'est pas encore terminé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'data': report.data,
            'summary': report.summary,
            'metadata': {
                'generated_at': report.generated_at,
                'execution_time': report.execution_time,
                'file_size': report.file_size
            }
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ReportScheduleListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des planifications de rapports"""
    serializer_class = ReportScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les planifications selon les permissions"""
        queryset = ReportSchedule.objects.all()
        
        # L'utilisateur ne voit que ses propres planifications
        queryset = queryset.filter(created_by=self.request.user)
        
        # Filtrer par statut actif si spécifié
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Associe l'utilisateur créateur"""
        serializer.save(created_by=self.request.user)


class ReportScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour les détails d'une planification de rapport"""
    serializer_class = ReportScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les planifications selon les permissions"""
        return ReportSchedule.objects.filter(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Vérifie les permissions de modification"""
        if serializer.instance.created_by != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez modifier que vos propres planifications")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Vérifie les permissions de suppression"""
        if instance.created_by != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez supprimer que vos propres planifications")
        instance.delete()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def execute_schedule(request, schedule_id):
    """Exécute une planification de rapport"""
    try:
        schedule = get_object_or_404(ReportSchedule, id=schedule_id, created_by=request.user)
        
        if not schedule.is_active:
            return Response(
                {'error': 'La planification n\'est pas active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Exécuter la planification
        report_service = ReportService()
        report = report_service.schedule_report(schedule.id)
        
        from apps.analytics.serializers import ReportSerializer
        serializer = ReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def report_summary(request):
    """Récupère un résumé des rapports de l'utilisateur"""
    try:
        user_reports = Report.objects.filter(generated_by=request.user)
        
        summary = {
            'total_reports': user_reports.count(),
            'completed_reports': user_reports.filter(status='completed').count(),
            'failed_reports': user_reports.filter(status='failed').count(),
            'pending_reports': user_reports.filter(status='pending').count(),
            'avg_execution_time': user_reports.filter(
                execution_time__isnull=False
            ).aggregate(avg=models.Avg('execution_time'))['avg'] or 0,
            'most_used_template': user_reports.filter(
                template__isnull=False
            ).values('template__name').annotate(
                count=models.Count('id')
            ).order_by('-count').first()['template__name'] if user_reports.filter(
                template__isnull=False
            ).exists() else None,
            'recent_reports': ReportSerializer(
                user_reports.order_by('-created_at')[:5], many=True
            ).data
        }
        
        return Response(summary)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
