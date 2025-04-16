from django.urls import path
from .views import IncrementViewAPI, RequestsByTypeAPI, RequestsByStatusAPI

urlpatterns = [
    path('increment-view/', IncrementViewAPI.as_view(), name='increment-view'),
    path('requests/by-type/', RequestsByTypeAPI.as_view(), name='requests-by-type'),
    path('requests/by-status/', RequestsByStatusAPI.as_view(), name='requests-by-status'),
    # Сюда добавим URL для статистики по заявкам позже
] 