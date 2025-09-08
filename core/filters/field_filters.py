"""
Filtres de champs personnalisés pour l'application Core
"""
import django_filters
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, date, time
import uuid


class DateRangeFilter(django_filters.DateFromToRangeFilter):
    """Filtre pour les plages de dates"""
    pass


class DateTimeRangeFilter(django_filters.DateTimeFromToRangeFilter):
    """Filtre pour les plages de datetime"""
    pass


class NumberRangeFilter(django_filters.RangeFilter):
    """Filtre pour les plages de nombres"""
    pass


class ChoiceFilter(django_filters.ChoiceFilter):
    """Filtre pour les choix"""
    pass


class MultipleChoiceFilter(django_filters.MultipleChoiceFilter):
    """Filtre pour les choix multiples"""
    pass


class BooleanFilter(django_filters.BooleanFilter):
    """Filtre pour les booléens"""
    pass


class CharFilter(django_filters.CharFilter):
    """Filtre pour les chaînes de caractères"""
    pass


class NumberFilter(django_filters.NumberFilter):
    """Filtre pour les nombres"""
    pass


class DateFilter(django_filters.DateFilter):
    """Filtre pour les dates"""
    pass


class DateTimeFilter(django_filters.DateTimeFilter):
    """Filtre pour les datetime"""
    pass


class TimeFilter(django_filters.TimeFilter):
    """Filtre pour les heures"""
    pass


class UUIDFilter(django_filters.UUIDFilter):
    """Filtre pour les UUID"""
    pass


class EmailFilter(django_filters.CharFilter):
    """Filtre pour les emails"""
    
    def filter(self, qs, value):
        if value:
            # Validation basique de l'email
            if '@' not in value:
                return qs.none()
        return super().filter(qs, value)


class PhoneFilter(django_filters.CharFilter):
    """Filtre pour les numéros de téléphone"""
    
    def filter(self, qs, value):
        if value:
            # Supprime les caractères non numériques sauf + au début
            cleaned_value = ''.join(c for c in value if c.isdigit() or c == '+')
            if not cleaned_value:
                return qs.none()
            return qs.filter(**{f'{self.field_name}__icontains': cleaned_value})
        return qs


class URLFilter(django_filters.CharFilter):
    """Filtre pour les URLs"""
    
    def filter(self, qs, value):
        if value:
            # Validation basique de l'URL
            if not (value.startswith('http://') or value.startswith('https://')):
                return qs.none()
        return super().filter(qs, value)


class IPAddressFilter(django_filters.CharFilter):
    """Filtre pour les adresses IP"""
    
    def filter(self, qs, value):
        if value:
            # Validation basique de l'IP
            parts = value.split('.')
            if len(parts) != 4:
                return qs.none()
            try:
                for part in parts:
                    if not 0 <= int(part) <= 255:
                        return qs.none()
            except ValueError:
                return qs.none()
        return super().filter(qs, value)


class SlugFilter(django_filters.CharFilter):
    """Filtre pour les slugs"""
    
    def filter(self, qs, value):
        if value:
            # Nettoie le slug
            cleaned_value = value.lower().replace(' ', '-')
            return qs.filter(**{f'{self.field_name}__icontains': cleaned_value})
        return qs


class JSONFilter(django_filters.CharFilter):
    """Filtre pour les champs JSON"""
    
    def filter(self, qs, value):
        if value:
            try:
                import json
                json_value = json.loads(value)
                return qs.filter(**{f'{self.field_name}__contains': json_value})
            except (json.JSONDecodeError, ValueError):
                return qs.none()
        return qs


class FileFilter(django_filters.CharFilter):
    """Filtre pour les fichiers"""
    
    def filter(self, qs, value):
        if value:
            # Filtre par extension de fichier
            if '.' in value:
                extension = value.split('.')[-1].lower()
                return qs.filter(**{f'{self.field_name}__endswith': extension})
        return super().filter(qs, value)


class ImageFilter(django_filters.CharFilter):
    """Filtre pour les images"""
    
    def filter(self, qs, value):
        if value:
            # Extensions d'images supportées
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            if any(value.lower().endswith(ext) for ext in image_extensions):
                return qs.filter(**{f'{self.field_name}__icontains': value})
            return qs.none()
        return qs


class RecentFilter(django_filters.BooleanFilter):
    """Filtre pour les objets récents"""
    
    def __init__(self, *args, **kwargs):
        self.days = kwargs.pop('days', 7)
        super().__init__(*args, **kwargs)
    
    def filter(self, qs, value):
        if value:
            cutoff = timezone.now() - timezone.timedelta(days=self.days)
            return qs.filter(created_at__gte=cutoff)
        return qs


class ActiveFilter(django_filters.BooleanFilter):
    """Filtre pour les objets actifs"""
    
    def filter(self, qs, value):
        if value is not None:
            if value:
                return qs.filter(status='active')
            else:
                return qs.exclude(status='active')
        return qs


class PublishedFilter(django_filters.BooleanFilter):
    """Filtre pour les objets publiés"""
    
    def filter(self, qs, value):
        if value is not None:
            if value:
                return qs.filter(
                    models.Q(status='active') | models.Q(status='published')
                )
            else:
                return qs.exclude(
                    models.Q(status='active') | models.Q(status='published')
                )
        return qs


class FeaturedFilter(django_filters.BooleanFilter):
    """Filtre pour les objets en vedette"""
    
    def filter(self, qs, value):
        if value is not None:
            if value:
                return qs.filter(featured=True)
            else:
                return qs.filter(featured=False)
        return qs


class PopularFilter(django_filters.BooleanFilter):
    """Filtre pour les objets populaires"""
    
    def __init__(self, *args, **kwargs):
        self.min_views = kwargs.pop('min_views', 100)
        super().__init__(*args, **kwargs)
    
    def filter(self, qs, value):
        if value:
            return qs.filter(views__gte=self.min_views)
        return qs


class TagFilter(django_filters.CharFilter):
    """Filtre pour les tags"""
    
    def filter(self, qs, value):
        if value:
            tags = [tag.strip() for tag in value.split(',')]
            return qs.filter(tags__name__in=tags)
        return qs


class CategoryFilter(django_filters.CharFilter):
    """Filtre pour les catégories"""
    
    def filter(self, qs, value):
        if value:
            return qs.filter(category__name__icontains=value)
        return qs


class PriceRangeFilter(django_filters.RangeFilter):
    """Filtre pour les plages de prix"""
    
    def filter(self, qs, value):
        if value:
            if value.start is not None:
                qs = qs.filter(price__gte=value.start)
            if value.stop is not None:
                qs = qs.filter(price__lte=value.stop)
        return qs


class RatingFilter(django_filters.NumberFilter):
    """Filtre pour les notes"""
    
    def filter(self, qs, value):
        if value is not None:
            return qs.filter(rating__gte=value)
        return qs


class DistanceFilter(django_filters.NumberFilter):
    """Filtre pour la distance géographique"""
    
    def __init__(self, *args, **kwargs):
        self.lat_field = kwargs.pop('lat_field', 'latitude')
        self.lng_field = kwargs.pop('lng_field', 'longitude')
        super().__init__(*args, **kwargs)
    
    def filter(self, qs, value):
        if value and hasattr(self, 'lat') and hasattr(self, 'lng'):
            # Utilise une formule de distance approximative
            # En production, utilisez PostGIS ou une solution géospatiale
            return qs.extra(
                where=[
                    "6371 * acos(cos(radians(%s)) * cos(radians(%s)) * cos(radians(%s) - radians(%s)) + sin(radians(%s)) * sin(radians(%s))) <= %s"
                ],
                params=[self.lat, self.lat_field, self.lng_field, self.lng, self.lat, self.lat_field, value]
            )
        return qs



