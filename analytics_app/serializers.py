from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

class IncrementViewSerializer(serializers.Serializer):
    app_label = serializers.CharField(max_length=100, write_only=True, help_text="App label модели (e.g., 'listings', 'news')")
    model_name = serializers.CharField(max_length=100, write_only=True, help_text="Имя модели в нижнем регистре (e.g., 'landplot', 'newsarticle')")
    # Идентификатор может быть ID или slug
    identifier = serializers.CharField(max_length=255, write_only=True, help_text="ID или Slug объекта")

    def validate(self, data):
        app_label = data['app_label']
        model_name = data['model_name']
        identifier = data['identifier']

        try:
            ct = ContentType.objects.get(app_label=app_label, model=model_name)
            model_class = ct.model_class()
            # Проверяем наличие поля view_count
            if not hasattr(model_class, 'view_count'):
                raise serializers.ValidationError(f"Модель {app_label}.{model_name} не имеет поля 'view_count'.")

            # Пытаемся найти объект по ID или slug
            obj = None
            lookup_kwargs = {}
            if identifier.isdigit():
                 lookup_kwargs['pk'] = int(identifier)
            # Для моделей с slug используем его
            elif hasattr(model_class, 'slug'):
                 lookup_kwargs['slug'] = identifier
            else: # Если не число и нет slug, предполагаем, что это неверный идентификатор
                 raise serializers.ValidationError("Неверный формат идентификатора.")

            obj = model_class.objects.filter(**lookup_kwargs).first()

            if not obj:
                raise serializers.ValidationError(f"Объект {model_name} с идентификатором '{identifier}' не найден.")

            # Передаем найденный объект дальше
            data['target_object'] = obj
        except ContentType.DoesNotExist:
            raise serializers.ValidationError(f"Неверный тип контента: {app_label}.{model_name}")
        except Exception as e:
             raise serializers.ValidationError(f"Ошибка поиска объекта: {e}")

        return data 