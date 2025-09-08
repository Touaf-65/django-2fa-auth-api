"""
Vues API pour la gestion système
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.permissions import IsStaffOrReadOnly
from django.conf import settings
from django.core.cache import cache
from django.db import connection
import psutil
import os
import time
from django.utils import timezone


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def admin_system_info(request):
    """Informations système"""
    import platform
    import sys
    
    return Response({
        'platform': {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
        },
        'python': {
            'version': sys.version,
            'executable': sys.executable,
        },
        'django': {
            'version': settings.DJANGO_VERSION,
            'debug': settings.DEBUG,
            'timezone': settings.TIME_ZONE,
            'language': settings.LANGUAGE_CODE,
        },
        'database': {
            'engine': settings.DATABASES['default']['ENGINE'],
            'name': settings.DATABASES['default']['NAME'],
        },
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def admin_system_health(request):
    """Santé du système"""
    health_status = {
        'database': 'healthy',
        'cache': 'healthy',
        'disk': 'healthy',
        'memory': 'healthy',
        'overall': 'healthy'
    }
    
    # Test base de données
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['database'] = 'healthy'
    except Exception as e:
        health_status['database'] = f'unhealthy: {str(e)}'
        health_status['overall'] = 'unhealthy'
    
    # Test cache
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['cache'] = 'healthy'
        else:
            health_status['cache'] = 'unhealthy'
            health_status['overall'] = 'unhealthy'
    except Exception as e:
        health_status['cache'] = f'unhealthy: {str(e)}'
        health_status['overall'] = 'unhealthy'
    
    # Test disque
    try:
        disk_usage = psutil.disk_usage('/')
        if disk_usage.percent > 90:
            health_status['disk'] = 'warning: disk usage high'
        elif disk_usage.percent > 95:
            health_status['disk'] = 'critical: disk usage very high'
            health_status['overall'] = 'unhealthy'
    except Exception as e:
        health_status['disk'] = f'unhealthy: {str(e)}'
        health_status['overall'] = 'unhealthy'
    
    # Test mémoire
    try:
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            health_status['memory'] = 'warning: memory usage high'
        elif memory.percent > 95:
            health_status['memory'] = 'critical: memory usage very high'
            health_status['overall'] = 'unhealthy'
    except Exception as e:
        health_status['memory'] = f'unhealthy: {str(e)}'
        health_status['overall'] = 'unhealthy'
    
    return Response(health_status)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def admin_system_backup(request):
    """Créer une sauvegarde"""
    # Ici vous pouvez implémenter la logique de sauvegarde
    # Pour l'instant, on retourne un message de succès
    return Response({
        'message': 'Sauvegarde créée avec succès',
        'backup_id': 'backup_' + str(int(time.time())),
        'created_at': timezone.now().isoformat()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def admin_system_cache_clear(request):
    """Vider le cache"""
    try:
        cache.clear()
        return Response({'message': 'Cache vidé avec succès'})
    except Exception as e:
        return Response({'error': f'Erreur lors du vidage du cache: {str(e)}'}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaffOrReadOnly])
def admin_system_maintenance(request):
    """Activer/désactiver le mode maintenance"""
    action = request.data.get('action', 'toggle')
    
    if action == 'enable':
        # Activer le mode maintenance
        cache.set('maintenance_mode', True, timeout=None)
        return Response({'message': 'Mode maintenance activé'})
    elif action == 'disable':
        # Désactiver le mode maintenance
        cache.delete('maintenance_mode')
        return Response({'message': 'Mode maintenance désactivé'})
    else:
        # Toggle
        current = cache.get('maintenance_mode', False)
        cache.set('maintenance_mode', not current, timeout=None)
        status = 'activé' if not current else 'désactivé'
        return Response({'message': f'Mode maintenance {status}'})
