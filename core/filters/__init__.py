"""
Filtres personnalisés pour l'application Core
"""
from .base_filters import (
    BaseFilterSet,
    TimestampedFilterSet,
    SoftDeleteFilterSet,
    StatusFilterSet,
    OrderingFilterSet,
    CreatedByFilterSet,
    UpdatedByFilterSet,
)

from .field_filters import (
    DateRangeFilter,
    DateTimeRangeFilter,
    NumberRangeFilter,
    ChoiceFilter,
    MultipleChoiceFilter,
    BooleanFilter,
    CharFilter,
    NumberFilter,
    DateFilter,
    DateTimeFilter,
    TimeFilter,
    UUIDFilter,
    EmailFilter,
    PhoneFilter,
    URLFilter,
    IPAddressFilter,
    SlugFilter,
    JSONFilter,
    FileFilter,
    ImageFilter,
)

from .search_filters import (
    SearchFilter,
    FullTextSearchFilter,
    FuzzySearchFilter,
    AutocompleteFilter,
    RelatedSearchFilter,
    NestedSearchFilter,
)

from .ordering_filters import (
    OrderingFilter,
    MultiOrderingFilter,
    RelatedOrderingFilter,
    CustomOrderingFilter,
)

from .aggregation_filters import (
    CountFilter,
    SumFilter,
    AvgFilter,
    MinFilter,
    MaxFilter,
    GroupByFilter,
    HavingFilter,
)

__all__ = [
    # Base filters
    'BaseFilterSet',
    'TimestampedFilterSet',
    'SoftDeleteFilterSet',
    'StatusFilterSet',
    'OrderingFilterSet',
    'CreatedByFilterSet',
    'UpdatedByFilterSet',
    
    # Field filters
    'DateRangeFilter',
    'DateTimeRangeFilter',
    'NumberRangeFilter',
    'ChoiceFilter',
    'MultipleChoiceFilter',
    'BooleanFilter',
    'CharFilter',
    'NumberFilter',
    'DateFilter',
    'DateTimeFilter',
    'TimeFilter',
    'UUIDFilter',
    'EmailFilter',
    'PhoneFilter',
    'URLFilter',
    'IPAddressFilter',
    'SlugFilter',
    'JSONFilter',
    'FileFilter',
    'ImageFilter',
    
    # Search filters
    'SearchFilter',
    'FullTextSearchFilter',
    'FuzzySearchFilter',
    'AutocompleteFilter',
    'RelatedSearchFilter',
    'NestedSearchFilter',
    
    # Ordering filters
    'OrderingFilter',
    'MultiOrderingFilter',
    'RelatedOrderingFilter',
    'CustomOrderingFilter',
    
    # Aggregation filters
    'CountFilter',
    'SumFilter',
    'AvgFilter',
    'MinFilter',
    'MaxFilter',
    'GroupByFilter',
    'HavingFilter',
]



