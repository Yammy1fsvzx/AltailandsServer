from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet, WorkingHoursViewSet

router = DefaultRouter()
router.register(r'contacts', ContactViewSet)
router.register(r'working-hours', WorkingHoursViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 