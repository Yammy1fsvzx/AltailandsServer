from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import Request, AdminComment
# Импортируем модели для instanceof проверок
from catalog.models import LandPlot, GenericProperty
from quizzes.models import Quiz
# Импортируем сериализаторы для связанных объектов (для отображения)
from catalog.serializers import LandPlotSerializer, GenericPropertySerializer
from quizzes.serializers import QuizSerializer

User = get_user_model()

class AdminCommentSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AdminComment
        fields = ['id', 'request', 'user_id', 'username', 'comment', 'created_at']
        read_only_fields = ['id', 'request', 'user_id', 'username', 'created_at']

    def create(self, validated_data):
        # Пользователь берется из контекста запроса
        validated_data['user'] = self.context['request'].user
        # Заявка будет установлена во ViewSet
        # validated_data['request'] = self.context['request_instance']
        return super().create(validated_data)

class RequestSerializer(serializers.ModelSerializer):
    admin_comments = AdminCommentSerializer(many=True, read_only=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Поля для GenericForeignKey при записи
    related_object_content_type_app_label = serializers.CharField(write_only=True, required=False, allow_null=True, label="App label связанного объекта (e.g., 'listings')")
    related_object_model_name = serializers.CharField(write_only=True, required=False, allow_null=True, label="Model name связанного объекта (e.g., 'landplot', 'genericproperty')")
    related_object_id = serializers.IntegerField(write_only=True, required=False, allow_null=True, label="ID связанного объекта")

    # Поле для отображения связанного объекта при чтении
    related_object_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Request
        fields = [
            'id', 'name', 'phone', 'email',
            'request_type', 'request_type_display',
            'status', 'status_display',
            'user_message', 'quiz_answers',
            'related_object_content_type_app_label', # Для записи
            'related_object_model_name', # Для записи
            'related_object_id', # Для записи
            'related_object_info', # Для чтения
            'created_at', 'updated_at',
            'admin_comments'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'admin_comments', 'related_object_info']
        # Email не обязателен
        extra_kwargs = {
            'email': {'required': False, 'allow_null': True},
            'quiz_answers': {'required': False, 'allow_null': True},
            'user_message': {'required': False, 'allow_blank': True, 'allow_null': True},
        }

    def get_related_object_info(self, obj):
        """Возвращает базовую информацию о связанном объекте."""
        if obj.related_object:
            serializer_context = {'request': self.context.get('request')}
            # Теперь instanceof будет работать
            if isinstance(obj.related_object, Quiz):
                 return QuizSerializer(obj.related_object, context=serializer_context).data
            elif isinstance(obj.related_object, LandPlot):
                 return LandPlotSerializer(obj.related_object, context=serializer_context).data
            elif isinstance(obj.related_object, GenericProperty):
                 return GenericPropertySerializer(obj.related_object, context=serializer_context).data
            else:
                 return {'type': obj.content_type.model, 'id': obj.object_id, 'name': str(obj.related_object)}
        return None

    def validate(self, data):
        app_label = data.get('related_object_content_type_app_label')
        model_name = data.get('related_object_model_name')
        object_id = data.get('related_object_id')

        if app_label and model_name and object_id:
            try:
                content_type = ContentType.objects.get(app_label=app_label, model=model_name)
                model_class = content_type.model_class()
                if model_class is None:
                    raise serializers.ValidationError(f"Модель для {app_label}.{model_name} не найдена. Возможно, приложение или модель были удалены.")
                
                if not model_class.objects.filter(pk=object_id).exists():
                    raise serializers.ValidationError(f"Объект {model_name} с ID {object_id} не найден.")
                
                data['content_type'] = content_type
                data['object_id'] = object_id
            except ContentType.DoesNotExist:
                raise serializers.ValidationError(f"Неверный тип контента: {app_label}.{model_name}")
        elif any([app_label, model_name, object_id]):
             raise serializers.ValidationError("Для указания связанного объекта необходимо передать все три поля: related_object_content_type_app_label, related_object_model_name, related_object_id")

        # Убираем временные поля из данных для сохранения
        data.pop('related_object_content_type_app_label', None)
        data.pop('related_object_model_name', None)
        # !!! Добавляем удаление временного ID !!!
        data.pop('related_object_id', None)

        return data

    # Метод create/update будет использовать content_type и object_id из data 