"""
Vues API pour SystemConfig
"""
from rest_framework import generics
from core.permissions import IsStaffOrReadOnly
from apps.admin_api.models import SystemConfig
from apps.admin_api.serializers import (
    SystemConfigSerializer,
    SystemConfigListSerializer,
    SystemConfigCreateSerializer,
    SystemConfigUpdateSerializer,
)


class SystemConfigListAPIView(generics.ListAPIView):
    """Liste des configurations système"""
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigListSerializer
    permission_classes = [IsStaffOrReadOnly]


class SystemConfigCreateAPIView(generics.CreateAPIView):
    """Créer une configuration système"""
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigCreateSerializer
    permission_classes = [IsStaffOrReadOnly]


class SystemConfigRetrieveAPIView(generics.RetrieveAPIView):
    """Récupérer une configuration système"""
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [IsStaffOrReadOnly]


class SystemConfigUpdateAPIView(generics.UpdateAPIView):
    """Mettre à jour une configuration système"""
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigUpdateSerializer
    permission_classes = [IsStaffOrReadOnly]


class SystemConfigDestroyAPIView(generics.DestroyAPIView):
    """Supprimer une configuration système"""
    queryset = SystemConfig.objects.all()
    permission_classes = [IsStaffOrReadOnly]



