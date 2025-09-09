"""
URLs pour l'app Security
"""
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def security_status(request):
    """Endpoint de statut de sécurité"""
    return Response({
        'status': 'active',
        'message': 'Security app is active'
    })

urlpatterns = [
    path('status/', security_status, name='security-status'),
]
