"""
URLs pour l'app API
"""
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_status(request):
    """Endpoint de statut de l'API"""
    return Response({
        'status': 'active',
        'message': 'API app is active'
    })

urlpatterns = [
    path('status/', api_status, name='api-status'),
]
