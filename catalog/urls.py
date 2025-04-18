from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LocationViewSet, FeatureViewSet, LandUseTypeViewSet,
    LandCategoryViewSet, MediaFileViewSet, LandPlotViewSet,
    PropertyTypeViewSet, GenericPropertyViewSet
)

router = DefaultRouter()

# Справочники
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'features', FeatureViewSet, basename='feature')
router.register(r'land-use-types', LandUseTypeViewSet, basename='land-use-type')
router.register(r'land-categories', LandCategoryViewSet, basename='land-category')

# Медиафайлы
router.register(r'media-files', MediaFileViewSet, basename='media-file')

# Основные объявления (будут добавлены позже)
router.register(r'land-plots', LandPlotViewSet, basename='land-plot') # Регистрируем LandPlot

# Регистрируем новые маршруты
router.register(r'property-types', PropertyTypeViewSet, basename='property-type')
router.register(r'properties', GenericPropertyViewSet, basename='property')

urlpatterns = [
    path('', include(router.urls)),
    # Можно добавить вложенные роуты, если нужно, например:
    # GET /api/v1/catalog/property-types/{slug}/properties/ -> список GenericProperty этого типа
    # path('property-types/<slug:property_type_slug>/properties/',
    #      GenericPropertyViewSet.as_view({'get': 'list'}),
    #      name='property-type-properties-list'),
] 