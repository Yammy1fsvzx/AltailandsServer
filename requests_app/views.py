from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from django.contrib.contenttypes.models import ContentType
from .models import Request, AdminComment
from .serializers import RequestSerializer, AdminCommentSerializer

# Create your views here.

@extend_schema_view(
    list=extend_schema(summary="Получить список заявок (только админ)"),
    retrieve=extend_schema(summary="Получить детали заявки (только админ)"),
    create=extend_schema(summary="Создать новую заявку (доступно всем)"),
    update=extend_schema(summary="Обновить заявку (полностью, только админ)"),
    partial_update=extend_schema(summary="Обновить заявку (частично, например, статус, только админ)"),
    destroy=extend_schema(summary="Удалить заявку (только админ)")
)
@extend_schema(tags=['Заявки'])
class RequestViewSet(viewsets.ModelViewSet):
    """
    API для управления заявками.
    Создание доступно всем, остальные операции - только администраторам.
    При создании заявки типа 'listing' или 'quiz' необходимо передать:
    - related_object_content_type_app_label (e.g., 'listings' or 'quizzes')
    - related_object_model_name (e.g., 'landplot', 'listingunit', 'quiz')
    - related_object_id (ID объекта)
    """
    queryset = Request.objects.prefetch_related('admin_comments__user').select_related('content_type').all()
    serializer_class = RequestSerializer
    filterset_fields = ['status', 'request_type']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            # Все остальные действия + комментарии требуют прав админа
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    # --- Вложенные действия для комментариев --- 
    @extend_schema(
        tags=['Заявки - Комментарии'],
        summary="Получить список комментариев к заявке",
        responses=AdminCommentSerializer(many=True)
    )
    @action(detail=True, methods=['get'], url_path='comments', permission_classes=[permissions.IsAdminUser])
    def list_comments(self, request, pk=None):
        request_obj = self.get_object()
        comments = request_obj.admin_comments.select_related('user').all()
        serializer = AdminCommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        tags=['Заявки - Комментарии'],
        summary="Добавить комментарий к заявке",
        request=AdminCommentSerializer,
        responses={201: AdminCommentSerializer}
    )
    @action(detail=True, methods=['post'], url_path='comments/add', permission_classes=[permissions.IsAdminUser])
    def add_comment(self, request, pk=None):
        request_obj = self.get_object()
        serializer = AdminCommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(request=request_obj) # Передаем заявку в save
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=['Заявки - Комментарии'],
        summary="Обновить комментарий к заявке",
        request=AdminCommentSerializer,
        responses={200: AdminCommentSerializer},
        parameters=[OpenApiParameter(name='comment_pk', location=OpenApiParameter.PATH, required=True, type=int)]
    )
    @action(detail=True, methods=['put', 'patch'], url_path=r'comments/(?P<comment_pk>\d+)', permission_classes=[permissions.IsAdminUser])
    def update_comment(self, request, pk=None, comment_pk=None):
        request_obj = self.get_object()
        comment = get_object_or_404(AdminComment, pk=comment_pk, request=request_obj)

        # Опционально: разрешить редактирование только автору
        # if comment.user != request.user:
        #     return Response({"detail": "Вы не можете редактировать чужие комментарии."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AdminCommentSerializer(
            comment, 
            data=request.data, 
            partial=request.method == 'PATCH', # Разрешаем частичное обновление для PATCH
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save() # User и request уже установлены
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=['Заявки - Комментарии'],
        summary="Удалить комментарий к заявке",
        responses={204: None},
        parameters=[OpenApiParameter(name='comment_pk', location=OpenApiParameter.PATH, required=True, type=int)]
    )
    @action(detail=True, methods=['delete'], url_path=r'comments/(?P<comment_pk>\d+)', permission_classes=[permissions.IsAdminUser])
    def destroy_comment(self, request, pk=None, comment_pk=None):
        request_obj = self.get_object()
        comment = get_object_or_404(AdminComment, pk=comment_pk, request=request_obj)

        # Опционально: разрешить удаление только автору
        # if comment.user != request.user:
        #     return Response({"detail": "Вы не можете удалять чужие комментарии."}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
