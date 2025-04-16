from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import F, Count
from drf_spectacular.utils import extend_schema
from .serializers import IncrementViewSerializer
from requests_app.models import Request

@extend_schema(
    tags=["Аналитика"],
    summary="Зарегистрировать просмотр объекта",
    description="Увеличивает счетчик просмотров для указанного объекта (новость, участок, комплекс, юнит). Вызывается фронтендом при просмотре.",
    request=IncrementViewSerializer,
    responses={200: None, 400: None, 404: None} # Возвращает пустой ответ при успехе
)
class IncrementViewAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny] # Доступно всем
    serializer_class = IncrementViewSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            target_object = serializer.validated_data['target_object']
            # Атомарно увеличиваем счетчик
            target_object.__class__.objects.filter(pk=target_object.pk).update(view_count=F('view_count') + 1)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=["Аналитика"],
    summary="Статистика заявок по типам",
    description="Возвращает количество заявок, сгруппированных по типам (quiz, contact, listing). Доступно только администраторам.",
    responses={200: {"type": "object", "example": {"quiz": 15, "contact": 5, "listing": 25}}}
)
class RequestsByTypeAPI(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        counts = Request.objects.values('request_type').annotate(count=Count('id'))
        # Преобразуем в удобный словарь {type: count}
        summary = {item['request_type']: item['count'] for item in counts}
        # Добавим типы с нулевым количеством, если их нет
        for code, name in Request.REQUEST_TYPE_CHOICES:
             if code not in summary:
                 summary[code] = 0
        return Response(summary)

@extend_schema(
    tags=["Аналитика"],
    summary="Статистика заявок по статусам",
    description="Возвращает количество заявок, сгруппированных по статусам обработки (new, processing, etc.). Доступно только администраторам.",
     responses={200: {"type": "object", "example": {"new": 30, "processing": 10, "completed": 5, "rejected": 0}}}
)
class RequestsByStatusAPI(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        counts = Request.objects.values('status').annotate(count=Count('id'))
        summary = {item['status']: item['count'] for item in counts}
        for code, name in Request.STATUS_CHOICES:
             if code not in summary:
                 summary[code] = 0
        return Response(summary)
