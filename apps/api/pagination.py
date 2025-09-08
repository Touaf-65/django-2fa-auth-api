"""
Pagination personnalisée pour l'API
"""
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.conf import settings


class APIPageNumberPagination(PageNumberPagination):
    """Pagination par numéro de page avec métadonnées étendues"""
    
    page_size = getattr(settings, 'API_PAGE_SIZE', 20)
    page_size_query_param = 'page_size'
    max_page_size = getattr(settings, 'API_MAX_PAGE_SIZE', 100)
    
    def get_paginated_response(self, data):
        """Réponse paginée avec métadonnées étendues"""
        return Response({
            'pagination': {
                'type': 'page_number',
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'page_size': self.page.paginator.per_page,
                'total_count': self.page.paginator.count,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'next_page': self.get_next_link(),
                'previous_page': self.get_previous_link(),
                'first_page': self.get_first_link(),
                'last_page': self.get_last_link(),
            },
            'data': data
        })
    
    def get_first_link(self):
        """Lien vers la première page"""
        if self.page.number > 1:
            return self.request.build_absolute_uri(
                self.request.path + f'?{self.page_query_param}=1'
            )
        return None
    
    def get_last_link(self):
        """Lien vers la dernière page"""
        if self.page.number < self.page.paginator.num_pages:
            return self.request.build_absolute_uri(
                self.request.path + f'?{self.page_query_param}={self.page.paginator.num_pages}'
            )
        return None


class APILimitOffsetPagination(LimitOffsetPagination):
    """Pagination par limite et offset avec métadonnées étendues"""
    
    default_limit = getattr(settings, 'API_PAGE_SIZE', 20)
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = getattr(settings, 'API_MAX_PAGE_SIZE', 100)
    
    def get_paginated_response(self, data):
        """Réponse paginée avec métadonnées étendues"""
        return Response({
            'pagination': {
                'type': 'limit_offset',
                'limit': self.limit,
                'offset': self.offset,
                'total_count': self.count,
                'has_next': bool(self.get_next_link()),
                'has_previous': bool(self.get_previous_link()),
                'next_link': self.get_next_link(),
                'previous_link': self.get_previous_link(),
                'first_link': self.get_first_link(),
                'last_link': self.get_last_link(),
            },
            'data': data
        })
    
    def get_first_link(self):
        """Lien vers la première page"""
        if self.offset > 0:
            return self.request.build_absolute_uri(
                self.request.path + f'?{self.limit_query_param}={self.limit}&{self.offset_query_param}=0'
            )
        return None
    
    def get_last_link(self):
        """Lien vers la dernière page"""
        if self.offset + self.limit < self.count:
            last_offset = max(0, self.count - self.limit)
            return self.request.build_absolute_uri(
                self.request.path + f'?{self.limit_query_param}={self.limit}&{self.offset_query_param}={last_offset}'
            )
        return None


class APICursorPagination(CursorPagination):
    """Pagination par curseur avec métadonnées étendues"""
    
    page_size = getattr(settings, 'API_PAGE_SIZE', 20)
    max_page_size = getattr(settings, 'API_MAX_PAGE_SIZE', 100)
    ordering = '-created_at'
    
    def get_paginated_response(self, data):
        """Réponse paginée avec métadonnées étendues"""
        return Response({
            'pagination': {
                'type': 'cursor',
                'page_size': self.page_size,
                'has_next': bool(self.get_next_link()),
                'has_previous': bool(self.get_previous_link()),
                'next_link': self.get_next_link(),
                'previous_link': self.get_previous_link(),
            },
            'data': data
        })


class APIDynamicPagination:
    """Pagination dynamique basée sur les paramètres de requête"""
    
    @staticmethod
    def get_pagination_class(request):
        """Retourne la classe de pagination appropriée"""
        pagination_type = request.query_params.get('pagination_type', 'page_number')
        
        if pagination_type == 'limit_offset':
            return APILimitOffsetPagination
        elif pagination_type == 'cursor':
            return APICursorPagination
        else:
            return APIPageNumberPagination
    
    @staticmethod
    def paginate_queryset(queryset, request):
        """Pagine un queryset avec la pagination appropriée"""
        pagination_class = APIDynamicPagination.get_pagination_class(request)
        paginator = pagination_class()
        return paginator.paginate_queryset(queryset, request)


class APICustomPagination(PageNumberPagination):
    """Pagination personnalisée avec options avancées"""
    
    page_size = getattr(settings, 'API_PAGE_SIZE', 20)
    page_size_query_param = 'page_size'
    max_page_size = getattr(settings, 'API_MAX_PAGE_SIZE', 100)
    
    def get_paginated_response(self, data):
        """Réponse paginée avec options personnalisées"""
        # Récupère les options de la requête
        include_metadata = self.request.query_params.get('include_metadata', 'true').lower() == 'true'
        include_links = self.request.query_params.get('include_links', 'true').lower() == 'true'
        
        response_data = {
            'data': data
        }
        
        if include_metadata:
            response_data['pagination'] = {
                'type': 'page_number',
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'page_size': self.page.paginator.per_page,
                'total_count': self.page.paginator.count,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            }
            
            if include_links:
                response_data['pagination'].update({
                    'next_page': self.get_next_link(),
                    'previous_page': self.get_previous_link(),
                    'first_page': self.get_first_link(),
                    'last_page': self.get_last_link(),
                })
        
        return Response(response_data)
    
    def get_first_link(self):
        """Lien vers la première page"""
        if self.page.number > 1:
            return self.request.build_absolute_uri(
                self.request.path + f'?{self.page_query_param}=1'
            )
        return None
    
    def get_last_link(self):
        """Lien vers la dernière page"""
        if self.page.number < self.page.paginator.num_pages:
            return self.request.build_absolute_uri(
                self.request.path + f'?{self.page_query_param}={self.page.paginator.num_pages}'
            )
        return None



