from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LocationViewSet, FeatureViewSet, LandUseTypeViewSet,
    LandCategoryViewSet, MediaFileViewSet, LandPlotViewSet,
    ListingComplexViewSet,
    ListingUnitViewSet # Добавляем импорт
    # Добавим сюда ViewSets для основных моделей позже
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
router.register(r'complexes', ListingComplexViewSet, basename='complex') # Регистрируем ListingComplex
router.register(r'units', ListingUnitViewSet, basename='unit') # Регистрируем ListingUnit

urlpatterns = [
    path('', include(router.urls)),
] 