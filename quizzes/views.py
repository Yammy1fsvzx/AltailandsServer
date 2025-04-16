from django.shortcuts import render
from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Quiz # Question, Answer не нужны напрямую во ViewSet
from .serializers import QuizSerializer

# Create your views here.

@extend_schema_view(
    list=extend_schema(summary="Получить список всех квизов"),
    retrieve=extend_schema(summary="Получить детали квиза (включая вопросы и ответы)"),
    create=extend_schema(summary="Создать новый квиз (только админ)"),
    update=extend_schema(summary="Обновить квиз (только админ)"),
    partial_update=extend_schema(summary="Частично обновить квиз (только админ)"),
    destroy=extend_schema(summary="Удалить квиз (только админ)")
)
@extend_schema(tags=['Квизы'])
class QuizViewSet(viewsets.ModelViewSet):
    """
    API для управления квизами.
    Возвращает структуру квиза с вложенными вопросами и вариантами ответов.
    Чтение доступно всем, создание/изменение/удаление - только администраторам.
    Вопросы и ответы управляются через админ-панель Django или требуют кастомной логики API (не реализовано).
    Для получения активного квиза используйте фильтр ?is_active=true
    """
    queryset = Quiz.objects.prefetch_related(
        'questions__answers' # Оптимизируем запрос для вложенных данных
    ).all()
    serializer_class = QuizSerializer
    lookup_field = 'slug' # Используем slug для доступа
    filterset_fields = ['is_active'] # Фильтр по активным квизам

    def get_permissions(self):
        """Чтение разрешено всем, запись - только админам."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
