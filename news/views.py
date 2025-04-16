from django.shortcuts import render
from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiTypes
from .models import Category, NewsArticle
from .serializers import CategorySerializer, NewsArticleSerializer

# Create your views here.

@extend_schema_view(
    list=extend_schema(summary="Получить список категорий новостей"),
    retrieve=extend_schema(summary="Получить детали категории новостей")
)
@extend_schema(tags=['Новости - Категории'])
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API эндпоинт для просмотра категорий новостей."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny] # Категории могут смотреть все

@extend_schema_view(
    list=extend_schema(summary="Получить список новостей"),
    retrieve=extend_schema(summary="Получить детали новости"),
    create=extend_schema(
        summary="Создать новость",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'content': {'type': 'string'},
                    'image': {'type': 'string', 'format': 'binary'},
                    'category': {'type': 'integer'},
                },
                'required': ['title', 'content']
            }
        },
        responses=NewsArticleSerializer
    ),
    update=extend_schema(
        summary="Обновить новость (полностью)",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'content': {'type': 'string'},
                    'image': {'type': 'string', 'format': 'binary'},
                    'category': {'type': 'integer'},
                },
                 'required': ['title', 'content']
            }
        },
        responses=NewsArticleSerializer
    ),
    partial_update=extend_schema(
        summary="Обновить новость (частично)",
         request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'content': {'type': 'string'},
                    'image': {'type': 'string', 'format': 'binary'},
                    'category': {'type': 'integer'},
                }
            }
        },
        responses=NewsArticleSerializer
    ),
    destroy=extend_schema(summary="Удалить новость")
)
@extend_schema(tags=['Новости - Статьи'])
class NewsArticleViewSet(viewsets.ModelViewSet):
    """
    API эндпоинт для управления новостями.
    Позволяет создавать, просматривать, редактировать и удалять новости.
    Доступ к созданию/редактированию/удалению только для аутентифицированных пользователей.
    """
    queryset = NewsArticle.objects.select_related('category').all()
    serializer_class = NewsArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Чтение для всех, запись для аутентифицированных
