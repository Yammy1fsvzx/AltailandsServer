from django.shortcuts import render
from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

# Импортируем наши кастомные фильтры
from .filters import LandPlotFilter, GenericPropertyFilter

# Исправляем импорты моделей
from .models import (
    Location, Feature, LandUseType, LandCategory, MediaFile, LandPlot,
    PropertyType, GenericProperty # Добавляем новые
    # ListingComplex, ListingUnit # Убираем старые
)

# Исправляем импорты сериализаторов
from .serializers import (
    LocationSerializer, FeatureSerializer, LandUseTypeSerializer,
    LandCategorySerializer, MediaFileSerializer, LandPlotSerializer,
    # ListingComplexSerializer, ListingUnitSerializer # Убираем старые
    PropertyTypeSerializer, GenericPropertySerializer # TODO: Создать эти сериализаторы
)

# --- Кастомные классы разрешений --- #

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает чтение всем, а запись/изменение/удаление только админам (is_staff).
    """
    def has_permission(self, request, view):
        # Разрешаем GET, HEAD, OPTIONS запросы всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Для остальных методов требуем права стаффа (админа)
        return request.user and request.user.is_staff

@extend_schema_view(
    list=extend_schema(summary="Получить список местоположений"),
    retrieve=extend_schema(summary="Получить детали местоположения")
)
@extend_schema(tags=['Объявления - Справочники'])
class LocationViewSet(viewsets.ModelViewSet):
    """API для просмотра местоположений."""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["region", "locality", "address_line"]
    ordering_fields = ["region", "locality"]

@extend_schema_view(
    list=extend_schema(summary="Получить список характеристик/особенностей"),
    retrieve=extend_schema(summary="Получить детали характеристики/особенности")
)
@extend_schema(tags=['Объявления - Справочники'])
class FeatureViewSet(viewsets.ModelViewSet):
    """API для просмотра характеристик/особенностей (коммуникации, инфраструктура и т.д.)."""
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["type"]
    search_fields = ["name"]
    ordering_fields = ["type", "name"]

@extend_schema_view(
    list=extend_schema(summary="Получить список ВРИ"),
    retrieve=extend_schema(summary="Получить детали ВРИ")
)
@extend_schema(tags=['Объявления - Справочники'])
class LandUseTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """API для просмотра видов разрешенного использования (ВРИ)."""
    queryset = LandUseType.objects.all()
    serializer_class = LandUseTypeSerializer
    permission_classes = [permissions.AllowAny]

@extend_schema_view(
    list=extend_schema(summary="Получить список категорий земель"),
    retrieve=extend_schema(summary="Получить детали категории земель")
)
@extend_schema(tags=['Объявления - Справочники'])
class LandCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API для просмотра категорий земель."""
    queryset = LandCategory.objects.all()
    serializer_class = LandCategorySerializer
    permission_classes = [permissions.AllowAny]

@extend_schema_view(
    list=extend_schema(summary="Получить список всех медиафайлов"),
    retrieve=extend_schema(summary="Получить детали медиафайла"),
    # Описываем загрузку файла для create и update
    create=extend_schema(
        summary="Загрузить новый медиафайл",
        description="Требуется указать content_type_id и object_id объекта, к которому привязан файл.",
        request={'multipart/form-data': MediaFileSerializer}
    ),
    update=extend_schema(
        summary="Обновить медиафайл (полностью)",
        request={'multipart/form-data': MediaFileSerializer}
    ),
    partial_update=extend_schema(
        summary="Обновить медиафайл (частично)",
        request={'multipart/form-data': MediaFileSerializer}
    ),
    destroy=extend_schema(summary="Удалить медиафайл")
)
@extend_schema(tags=['Объявления - Медиафайлы'])
class MediaFileViewSet(viewsets.ModelViewSet):
    """
    API для управления медиафайлами (изображения, видео, документы).
    Запись/изменение/удаление доступны только аутентифицированным пользователям.
    При создании/обновлении файл передается через multipart/form-data.
    Необходимо указывать ID ContentType и ID объекта для связи.
    """
    queryset = MediaFile.objects.all()
    serializer_class = MediaFileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Добавляем передачу request в контекст сериализатора для генерации URL
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

@extend_schema_view(
    list=extend_schema(summary="Получить список земельных участков"),
    retrieve=extend_schema(summary="Получить детали земельного участка"),
    create=extend_schema(summary="Создать объявление о земельном участке"),
    update=extend_schema(summary="Обновить объявление (полностью)"),
    partial_update=extend_schema(summary="Обновить объявление (частично)"),
    destroy=extend_schema(summary="Удалить объявление")
)
@extend_schema(tags=['Объявления - Земельные участки'])
class LandPlotViewSet(viewsets.ModelViewSet):
    """
    API для управления объявлениями о земельных участках.
    Поддерживает фильтрацию по диапазонам цены/площади, типу, статусу, ВРИ, характеристикам, местоположению.
    Поддерживает поиск по заголовку, описанию, региону, населенному пункту.
    Поддерживает сортировку по цене, площади, дате создания.
    """
    queryset = LandPlot.objects.select_related(
        'location', 'land_category'
    ).prefetch_related(
        'land_use_types', 'features', 'media_files'
    ).filter(listing_status='published') # По умолчанию показываем только опубликованные
    serializer_class = LandPlotSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LandPlotFilter
    search_fields = ["title", "description", "cadastral_numbers", "location__locality", "location__address_line"]
    ordering_fields = ["created_at", "updated_at", "price", "area", "price_per_are", "view_count"]
    ordering = ["-created_at"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

@extend_schema_view(
    list=extend_schema(summary="Получить список типов объектов недвижимости"),
    retrieve=extend_schema(summary="Получить детали типа объекта недвижимости")
)
@extend_schema(tags=["Объявления - Типы объектов"])
class PropertyTypeViewSet(viewsets.ModelViewSet):
    """ API для просмотра типов объектов недвижимости (квартира, апарт-отель и т.д.) и их схем атрибутов. """
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name"]

@extend_schema_view(
    list=extend_schema(summary="Получить список универсальных объектов недвижимости"),
    retrieve=extend_schema(summary="Получить детали объекта недвижимости"),
    create=extend_schema(summary="Создать объект недвижимости"),
    update=extend_schema(summary="Обновить объект (полностью)"),
    partial_update=extend_schema(summary="Обновить объект (частично)"),
    destroy=extend_schema(summary="Удалить объект")
)
@extend_schema(tags=["Объявления - Универсальные объекты"])
class GenericPropertyViewSet(viewsets.ModelViewSet):
    """
    API для управления универсальными объектами недвижимости (квартиры, апартаменты, коттеджи и т.д.).
    Поддерживает фильтрацию по типу, цене, местоположению и некоторым атрибутам (area_sqm, rooms и т.д.).
    """
    queryset = (
        GenericProperty.objects.select_related("property_type", "location", "parent")
        .prefetch_related("children", "media_files")
        .filter(listing_status="published") # По умолчанию показываем только опубликованные
    )
    serializer_class = GenericPropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = GenericPropertyFilter
    search_fields = [
        "title", "description",
        "location__region", "location__locality",
        "property_type__name",
        "attributes__material" # Пример поиска по атрибуту (если текстовый)
    ]
    ordering_fields = ["created_at", "updated_at", "price", "view_count"]
    ordering = ["-created_at"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
