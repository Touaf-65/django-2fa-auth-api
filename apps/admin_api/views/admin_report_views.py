"""
Vues API pour AdminReport
"""
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.permissions import IsStaffOrReadOnly
from django.utils import timezone
from apps.admin_api.models import AdminReport
from apps.admin_api.serializers import (
    AdminReportSerializer,
    AdminReportListSerializer,
    AdminReportCreateSerializer,
)


class AdminReportListAPIView(generics.ListAPIView):
    """Liste des rapports d'administration"""
    queryset = AdminReport.objects.all()
    serializer_class = AdminReportListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class AdminReportCreateAPIView(generics.CreateAPIView):
    """Créer un rapport d'administration"""
    queryset = AdminReport.objects.all()
    serializer_class = AdminReportCreateSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


class AdminReportRetrieveAPIView(generics.RetrieveAPIView):
    """Récupérer un rapport d'administration"""
    queryset = AdminReport.objects.all()
    serializer_class = AdminReportSerializer
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def admin_report_generate(request, report_id):
    """Générer un rapport"""
    try:
        report = AdminReport.objects.get(id=report_id)
        
        # Ici vous pouvez implémenter la logique de génération de rapport
        # Pour l'instant, on retourne un message de succès
        
        return Response({
            'message': 'Rapport généré avec succès',
            'report_id': report.id,
            'generated_at': timezone.now().isoformat()
        })
    except AdminReport.DoesNotExist:
        return Response({'error': 'Rapport non trouvé'}, status=404)
