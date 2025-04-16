import django_filters
from .models import LandPlot, ListingUnit, Feature, LandUseType, LandCategory, ListingComplex

class LandPlotFilter(django_filters.FilterSet):
    # Фильтры по диапазону для цены и площади
    price = django_filters.RangeFilter(label='Цена (от/до)')
    area = django_filters.RangeFilter(label='Площадь (от/до, в сотках)')

    # Фильтры по связанным моделям (позволяют передавать несколько ID)
    land_use_types = django_filters.ModelMultipleChoiceFilter(
        field_name='land_use_types__id', # Или __slug, если удобнее
        queryset=LandUseType.objects.all(),
        label='ВРИ (ID)'
    )
    features = django_filters.ModelMultipleChoiceFilter(
        field_name='features__id', # Или __name
        queryset=Feature.objects.filter(type__in=['communication', 'plot_feature']),
        label='Коммуникации/Особенности (ID)'
    )

    # Фильтры по местоположению (точные совпадения)
    region = django_filters.CharFilter(field_name='location__region', lookup_expr='icontains', label='Регион (часть названия)')
    locality = django_filters.CharFilter(field_name='location__locality', lookup_expr='icontains', label='Населенный пункт (часть названия)')

    class Meta:
        model = LandPlot
        fields = {
            'land_type': ['exact'],
            'plot_status': ['exact'],
            'listing_status': ['exact'],
            'land_category': ['exact'], # Фильтр по ID категории
            # Диапазоны и ManyToMany определены выше
            # 'price': [...],
            # 'area': [...],
            # 'land_use_types': [...],
            # 'features': [...],
            # 'location__region': [...],
            # 'location__locality': [...],
        }

class ListingUnitFilter(django_filters.FilterSet):
    # Фильтры по диапазону для цены и площади юнита
    price = django_filters.RangeFilter(label='Цена (от/до)')
    area = django_filters.RangeFilter(label='Площадь (от/до)')

    # Фильтры по характеристикам связанного комплекса
    complex_type = django_filters.ChoiceFilter(
        field_name='complex__complex_type',
        choices=ListingComplex.COMPLEX_TYPE_CHOICES,
        label='Тип комплекса'
    )
    region = django_filters.CharFilter(field_name='complex__location__region', lookup_expr='icontains', label='Регион комплекса (часть названия)')
    locality = django_filters.CharFilter(field_name='complex__location__locality', lookup_expr='icontains', label='Населенный пункт комплекса (часть названия)')

    # Фильтры по особенностям юнита
    features = django_filters.ModelMultipleChoiceFilter(
        field_name='features__id',
        queryset=Feature.objects.filter(type='unit_feature'),
        label='Особенности юнита (ID)'
    )

    class Meta:
        model = ListingUnit
        fields = {
            'complex': ['exact'], # Фильтр по ID комплекса
            'unit_status': ['exact'],
            'rooms': ['exact', 'gte', 'lte'], # Точное кол-во, больше или равно, меньше или равно
            'floor': ['exact', 'gte', 'lte'],
            # Диапазоны и связанные поля определены выше
            # 'price': [...],
            # 'area': [...],
            # 'complex__complex_type': [...],
            # 'complex__location__region': [...],
            # 'complex__location__locality': [...],
            # 'features': [...],
        } 