from django.urls import path
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from .views import LogoutView # Импортируем LogoutView

# Декорируем представление для получения токенов
@extend_schema(
    tags=['Аутентификация'],
    summary="Получение JWT токенов (Access и Refresh)",
    description="Обменивает имя пользователя и пароль на пару JWT токенов: Access (короткоживущий) и Refresh (долгоживущий).",
    request=TokenObtainPairSerializer,
    responses=TokenObtainPairSerializer,
)
class DecoratedTokenObtainPairView(TokenObtainPairView):
    pass

# Декорируем представление для обновления токена
@extend_schema(
    tags=['Аутентификация'],
    summary="Обновление Access токена",
    description="Обменивает валидный Refresh токен на новый Access токен (и, возможно, новый Refresh токен, если включена ротация).",
    request=TokenRefreshSerializer,
    responses=TokenRefreshSerializer,
)
class DecoratedTokenRefreshView(TokenRefreshView):
    pass

urlpatterns = [
    path(
        'token/',
        DecoratedTokenObtainPairView.as_view(), # Используем декорированное представление
        name='token_obtain_pair'
    ),
    path(
        'token/refresh/',
        DecoratedTokenRefreshView.as_view(), # Используем декорированное представление
        name='token_refresh'
    ),
    path(
        'logout/', # Добавляем URL для Logout
        LogoutView.as_view(),
        name='logout'
    ),
    # Можно добавить сюда и другие URL, связанные с аутентификацией, если понадобятся
] 