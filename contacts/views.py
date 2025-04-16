from django.shortcuts import render
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Contact, WorkingHours
from .serializers import ContactSerializer, WorkingHoursSerializer

@extend_schema_view(
    list=extend_schema(
        summary="Получить список всех контактов",
        description="Возвращает список всех созданных контактных данных."
    ),
    retrieve=extend_schema(
        summary="Получить детали контакта",
        description="Возвращает подробную информацию о конкретном контакте по его ID."
    ),
    create=extend_schema(
        summary="Создать новый контакт",
        description="Создает новую запись с контактной информацией.",
        request=ContactSerializer,
        responses={201: ContactSerializer},
        examples=[
            OpenApiExample(
                'Пример создания контакта',
                summary='Базовый пример',
                description='Пример тела запроса для создания нового контакта.',
                value={
                    "phone": "+7 999 123 45 67",
                    "whatsapp": "+7 999 123 45 67",
                    "email": "info@altailands.ru",
                    "office_address": "г. Горно-Алтайск, ул. Примерная, д. 1"
                }
            ),
        ]
    ),
    update=extend_schema(
        summary="Обновить контакт (полностью)",
        description="Полностью обновляет существующую запись контакта по его ID."
    ),
    partial_update=extend_schema(
        summary="Обновить контакт (частично)",
        description="Частично обновляет существующую запись контакта по его ID."
    ),
    destroy=extend_schema(
        summary="Удалить контакт",
        description="Удаляет существующую запись контакта по его ID."
    )
)
@extend_schema(tags=['Контактная информация'])
class ContactViewSet(viewsets.ModelViewSet):
    """
    API эндпоинт для управления контактной информацией.

    Позволяет создавать, просматривать, редактировать и удалять контактные данные.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

@extend_schema_view(
    list=extend_schema(
        summary="Получить список всех записей режима работы",
        description="Возвращает список всех записей о рабочем времени."
    ),
    retrieve=extend_schema(
        summary="Получить детали режима работы для дня",
        description="Возвращает подробную информацию о режиме работы для конкретной записи по ее ID."
    ),
    create=extend_schema(
        summary="Создать запись о режиме работы",
        description="Создает новую запись о рабочем времени для конкретного дня недели, связанную с контактом.",
        request=WorkingHoursSerializer,
        responses={201: WorkingHoursSerializer},
        examples=[
            OpenApiExample(
                'Пример создания режима работы',
                summary='Рабочий день (Понедельник)',
                description='Пример тела запроса для создания записи о рабочем времени.',
                value={
                    "contact": 1, # ID существующего контакта
                    "day_of_week": 0, # 0 - Понедельник
                    "start_time": "09:00",
                    "end_time": "18:00",
                    "is_active": True
                }
            ),
            OpenApiExample(
                'Пример создания выходного дня',
                summary='Выходной день (Воскресенье)',
                description='Пример тела запроса для обозначения выходного дня.',
                value={
                    "contact": 1, # ID существующего контакта
                    "day_of_week": 6, # 6 - Воскресенье
                    "is_active": False
                }
            ),
        ]
    ),
    update=extend_schema(
        summary="Обновить режим работы (полностью)",
        description="Полностью обновляет существующую запись о режиме работы по ее ID."
    ),
    partial_update=extend_schema(
        summary="Обновить режим работы (частично)",
        description="Частично обновляет существующую запись о режиме работы по ее ID."
    ),
    destroy=extend_schema(
        summary="Удалить запись о режиме работы",
        description="Удаляет существующую запись о режиме работы по ее ID."
    )
)
@extend_schema(tags=['Контактная информация'])
class WorkingHoursViewSet(viewsets.ModelViewSet):
    """
    API эндпоинт для управления режимом работы.

    Позволяет создавать, просматривать, редактировать и удалять записи о рабочем времени
    для конкретного дня недели, связанного с контактом.
    """
    queryset = WorkingHours.objects.all()
    serializer_class = WorkingHoursSerializer
