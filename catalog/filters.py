import django_filters
from django.db.models import Q
from .models import LandPlot, GenericProperty, Feature, LandUseType, LandCategory, PropertyType

class BaseRangeFilter(django_filters.FilterSet):
    """ Базовый класс для добавления фильтров по диапазону """
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        abstract = True

class LandPlotFilter(BaseRangeFilter):
    area_min = django_filters.NumberFilter(field_name="area", lookup_expr="gte")
    area_max = django_filters.NumberFilter(field_name="area", lookup_expr="lte")

    # Фильтр для выбора нескольких ВРИ (передавать ID через запятую: ?land_use_types=1,2)
    land_use_types = django_filters.BaseInFilter(field_name="land_use_types__id", lookup_expr="in")

    # Фильтр для выбора нескольких Особенностей (передавать ID: ?features=1,2)
    features = django_filters.BaseInFilter(field_name="features__id", lookup_expr="in")

    # Фильтр по местоположению
    location_region = django_filters.CharFilter(field_name="location__region", lookup_expr="icontains", label='Регион (часть названия)')
    location_locality = django_filters.CharFilter(field_name="location__locality", lookup_expr="icontains", label='Населенный пункт (часть названия)')

    class Meta:
        model = LandPlot
        fields = [
            "price_min", "price_max",
            "area_min", "area_max",
            "listing_status", "plot_status", "land_category",
            "land_use_types", "features",
            "location_region", "location_locality",
        ]

class GenericPropertyFilter(BaseRangeFilter):
    # Фильтр по типу объекта через slug
    property_type = django_filters.CharFilter(field_name="property_type__slug", lookup_expr="exact")

    # Фильтры по атрибутам (примеры для общих ключей)
    # Для них требуются GIN индексы в PostgreSQL для производительности!
    # Площадь (кв.м.)
    attr_area_sqm_min = django_filters.NumberFilter(field_name="attributes__area_sqm", lookup_expr="gte")
    attr_area_sqm_max = django_filters.NumberFilter(field_name="attributes__area_sqm", lookup_expr="lte")
    # Количество комнат
    attr_rooms_min = django_filters.NumberFilter(field_name="attributes__rooms", lookup_expr="gte")
    attr_rooms_max = django_filters.NumberFilter(field_name="attributes__rooms", lookup_expr="lte")
    # Этаж
    attr_floor_min = django_filters.NumberFilter(field_name="attributes__floor", lookup_expr="gte")
    attr_floor_max = django_filters.NumberFilter(field_name="attributes__floor", lookup_expr="lte")
    # Этажность дома
    attr_total_floors_min = django_filters.NumberFilter(field_name="attributes__total_floors", lookup_expr="gte")
    attr_total_floors_max = django_filters.NumberFilter(field_name="attributes__total_floors", lookup_expr="lte")
    # Наличие балкона
    attr_has_balcony = django_filters.BooleanFilter(field_name="attributes__has_balcony")
    # Материал стен (если строка)
    attr_material = django_filters.CharFilter(field_name="attributes__material", lookup_expr="icontains")

    # Фильтр по местоположению
    location_region = django_filters.CharFilter(field_name="location__region", lookup_expr="icontains")
    location_locality = django_filters.CharFilter(field_name="location__locality", lookup_expr="icontains")

    class Meta:
        model = GenericProperty
        fields = [
            "price_min", "price_max",
            "listing_status", "property_type",
            "location_region", "location_locality",
            # Атрибуты
            "attr_area_sqm_min", "attr_area_sqm_max",
            "attr_rooms_min", "attr_rooms_max",
            "attr_floor_min", "attr_floor_max",
            "attr_total_floors_min", "attr_total_floors_max",
            "attr_has_balcony", "attr_material",
        ]

# TODO: Добавить новый FilterSet для GenericProperty, когда он понадобится
# Он должен будет уметь фильтровать по общим полям и по полям внутри JSON 'attributes' 