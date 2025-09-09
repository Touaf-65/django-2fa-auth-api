"""
Vues API pour l'export de données Analytics
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from django.db import models
from django.utils import timezone
from datetime import timedelta

from apps.analytics.models import DataExport, ExportFormat
from apps.analytics.serializers import (
    DataExportSerializer, DataExportCreateSerializer, ExportFormatSerializer,
    ExportRequestSerializer, ExportStatusSerializer, ExportSummarySerializer,
    BulkExportSerializer
)
from apps.analytics.services import ExportService


class ExportFormatListView(generics.ListAPIView):
    """Vue pour lister les formats d'export disponibles"""
    queryset = ExportFormat.objects.filter(is_active=True)
    serializer_class = ExportFormatSerializer
    permission_classes = [permissions.IsAuthenticated]


class DataExportListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des exports de données"""
    serializer_class = DataExportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les exports selon les permissions"""
        queryset = DataExport.objects.filter(requested_by=self.request.user)
        
        # Filtrer par statut si spécifié
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filtrer par format si spécifié
        export_format = self.request.query_params.get('format')
        if export_format:
            queryset = queryset.filter(export_format__name=export_format)
        
        # Filtrer par source de données si spécifié
        data_source = self.request.query_params.get('data_source')
        if data_source:
            queryset = queryset.filter(data_source=data_source)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Associe l'utilisateur demandeur"""
        serializer.save(requested_by=self.request.user)


class DataExportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour les détails d'un export de données"""
    serializer_class = DataExportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les exports selon les permissions"""
        return DataExport.objects.filter(requested_by=self.request.user)
    
    def perform_update(self, serializer):
        """Vérifie les permissions de modification"""
        if serializer.instance.requested_by != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez modifier que vos propres exports")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Vérifie les permissions de suppression"""
        if instance.requested_by != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez supprimer que vos propres exports")
        instance.delete()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_export(request, export_id):
    """Traite un export de données"""
    try:
        export = get_object_or_404(DataExport, id=export_id, requested_by=request.user)
        
        if export.status == 'processing':
            return Response(
                {'error': 'L\'export est déjà en cours de traitement'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if export.status == 'completed':
            return Response(
                {'error': 'L\'export est déjà terminé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Traiter l'export
        export_service = ExportService()
        processed_export = export_service.process_export(export.id)
        
        serializer = DataExportSerializer(processed_export)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except DataExport.DoesNotExist:
        return Response(
            {'error': 'Export non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_export(request, export_id):
    """Télécharge un fichier d'export"""
    try:
        export = get_object_or_404(DataExport, id=export_id, requested_by=request.user)
        
        if export.status != 'completed':
            return Response(
                {'error': 'L\'export n\'est pas encore terminé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Télécharger le fichier
        export_service = ExportService()
        response = export_service.get_export_file_response(export)
        
        # Incrémenter le compteur de téléchargements
        export.download_count += 1
        export.save()
        
        return response
        
    except DataExport.DoesNotExist:
        return Response(
            {'error': 'Export non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except FileNotFoundError:
        return Response(
            {'error': 'Fichier d\'export non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def quick_export(request):
    """Crée et traite un export rapide"""
    try:
        serializer = ExportRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Créer l'export
        export_service = ExportService()
        export = export_service.create_export(
            name=f"Export rapide - {data['data_source']}",
            data_source=data['data_source'],
            export_format=data['export_format'],
            user=request.user,
            date_range_start=timezone.now() - timedelta(days=data['date_range_days']),
            date_range_end=timezone.now(),
            filters=data.get('filters', {}),
            columns=data.get('columns', [])
        )
        
        # Traiter l'export immédiatement
        processed_export = export_service.process_export(export.id)
        
        serializer = DataExportSerializer(processed_export)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_export(request):
    """Crée plusieurs exports en lot"""
    try:
        serializer = BulkExportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        exports_data = serializer.validated_data['exports']
        created_exports = []
        
        export_service = ExportService()
        
        for export_data in exports_data:
            # Créer l'export
            export = export_service.create_export(
                name=f"Export en lot - {export_data['data_source']}",
                data_source=export_data['data_source'],
                export_format=export_data['export_format'],
                user=request.user,
                date_range_start=timezone.now() - timedelta(days=export_data.get('date_range_days', 30)),
                date_range_end=timezone.now(),
                filters=export_data.get('filters', {}),
                columns=export_data.get('columns', [])
            )
            
            # Traiter l'export
            processed_export = export_service.process_export(export.id)
            created_exports.append(processed_export)
        
        serializer = DataExportSerializer(created_exports, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_status(request, export_id):
    """Récupère le statut d'un export"""
    try:
        export = get_object_or_404(DataExport, id=export_id, requested_by=request.user)
        
        status_data = {
            'id': export.id,
            'name': export.name,
            'status': export.status,
            'status_display': export.get_status_display(),
            'error_message': export.error_message
        }
        
        # Ajouter des informations supplémentaires selon le statut
        if export.status == 'processing':
            # Estimer le temps de completion (exemple)
            if export.created_at:
                elapsed_time = (timezone.now() - export.created_at).total_seconds()
                estimated_completion = timezone.now() + timedelta(seconds=elapsed_time * 2)
                status_data['estimated_completion'] = estimated_completion
        
        return Response(status_data)
        
    except DataExport.DoesNotExist:
        return Response(
            {'error': 'Export non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_summary(request):
    """Récupère un résumé des exports de l'utilisateur"""
    try:
        user_exports = DataExport.objects.filter(requested_by=request.user)
        
        summary = {
            'total_exports': user_exports.count(),
            'completed_exports': user_exports.filter(status='completed').count(),
            'failed_exports': user_exports.filter(status='failed').count(),
            'pending_exports': user_exports.filter(status='pending').count(),
            'total_downloads': user_exports.aggregate(
                total=models.Sum('download_count')
            )['total'] or 0,
            'most_used_format': user_exports.filter(
                export_format__isnull=False
            ).values('export_format__name').annotate(
                count=models.Count('id')
            ).order_by('-count').first()['export_format__name'] if user_exports.filter(
                export_format__isnull=False
            ).exists() else None,
            'recent_exports': DataExportSerializer(
                user_exports.order_by('-created_at')[:5], many=True
            ).data
        }
        
        return Response(summary)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cleanup_expired_exports(request):
    """Nettoie les exports expirés"""
    try:
        export_service = ExportService()
        cleaned_count = export_service.cleanup_expired_exports()
        
        return Response(
            {'message': f'{cleaned_count} exports expirés ont été nettoyés'},
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
