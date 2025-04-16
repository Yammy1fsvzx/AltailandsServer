from django.shortcuts import render
from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view
from .filters import LandPlotFilter, ListingUnitFilter
from .models import Location, Feature, LandUseType, LandCategory, MediaFile, LandPlot, ListingComplex, ListingUnit
from .serializers import (
    LocationSerializer, FeatureSerializer, LandUseTypeSerializer,
    LandCategorySerializer, MediaFileSerializer, LandPlotSerializer,
    ListingComplexSerializer, ListingUnitSerializer
)

@extend_schema_view(
    list=extend_schema(summary="Получить список местоположений"),
    retrieve=extend_schema(summary="Получить детали местоположения")
)
@extend_schema(tags=['Объявления - Справочники'])
class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """API для просмотра местоположений."""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]

@extend_schema_view(
    list=extend_schema(summary="Получить список характеристик/особенностей"),
    retrieve=extend_schema(summary="Получить детали характеристики/особенности")
)
@extend_schema(tags=['Объявления - Справочники'])
class FeatureViewSet(viewsets.ReadOnlyModelViewSet):
    """API для просмотра характеристик/особенностей (коммуникации, инфраструктура и т.д.)."""
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['type'] # Добавляем возможность фильтрации по типу

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
    # Применяем класс фильтра
    filterset_class = LandPlotFilter 
    # Поля для поиска
    search_fields = ['title', 'description', 'location__region', 'location__locality', 'cadastral_numbers']
    # Поля для сортировки
    ordering_fields = ['created_at', 'price', 'area']
    ordering = ['-created_at'] # Сортировка по умолчанию

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

@extend_schema_view(
    list=extend_schema(summary="Получить список комплексов/проектов"),
    retrieve=extend_schema(summary="Получить детали комплекса/проекта"),
    create=extend_schema(summary="Создать комплекс/проект"),
    update=extend_schema(summary="Обновить комплекс/проект (полностью)"),
    partial_update=extend_schema(summary="Обновить комплекс/проект (частично)"),
    destroy=extend_schema(summary="Удалить комплекс/проект")
)
@extend_schema(tags=['Объявления - Комплексы'])
class ListingComplexViewSet(viewsets.ModelViewSet):
    """
    API для управления комплексами/проектами.
    Поддерживает поиск по названию, описанию, региону, населенному пункту.
    Поддерживает сортировку по названию, дате создания.
    """
    queryset = ListingComplex.objects.select_related(
        'location'
    ).prefetch_related(
        'features', 'media_files'
    ).filter(listing_status='published') # По умолчанию показываем только опубликованные
    serializer_class = ListingComplexSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    # Фильтрация по типу и статусу (простые поля)
    filterset_fields = ['complex_type', 'listing_status'] 
    # Поля для поиска
    search_fields = ['name', 'description', 'location__region', 'location__locality']
    # Поля для сортировки
    ordering_fields = ['created_at', 'name']
    ordering = ['name'] # Сортировка по умолчанию

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

@extend_schema_view(
    list=extend_schema(summary="Получить список юнитов (квартир, апартаментов и т.д.)"),
    retrieve=extend_schema(summary="Получить детали юнита"),
    create=extend_schema(summary="Создать юнит"),
    update=extend_schema(summary="Обновить юнит (полностью)"),
    partial_update=extend_schema(summary="Обновить юнит (частично)"),
    destroy=extend_schema(summary="Удалить юнит")
)
@extend_schema(tags=['Объявления - Юниты в комплексах'])
class ListingUnitViewSet(viewsets.ModelViewSet):
    """
    API для управления юнитами (квартиры, апартаменты, офисы и т.д.) внутри комплексов.
    Поддерживает фильтрацию по комплексу, статусу, комнатам, этажу, диапазонам цены/площади, типу комплекса, местоположению.
    Поддерживает поиск по идентификатору, названию комплекса, региону, населенному пункту.
    Поддерживает сортировку по цене, площади, дате создания.
    """
    queryset = ListingUnit.objects.select_related(
        'complex__location' # Загружаем и локацию комплекса
    ).prefetch_related(
        'features', 'media_files'
    ).filter(complex__listing_status='published') # Показываем юниты только из опубликованных комплексов
    serializer_class = ListingUnitSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # Применяем класс фильтра
    filterset_class = ListingUnitFilter 
    # Поля для поиска
    search_fields = ['unit_identifier', 'complex__name', 'complex__location__region', 'complex__location__locality']
    # Поля для сортировки
    ordering_fields = ['created_at', 'price', 'area', 'floor', 'rooms']
    ordering = ['complex__name', 'unit_identifier'] # Сортировка по умолчанию

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
