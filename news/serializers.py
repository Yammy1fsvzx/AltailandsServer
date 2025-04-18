from rest_framework import serializers
from .models import Category, NewsArticle
# Импортируем MediaFileSerializer из приложения catalog
from catalog.serializers import MediaFileSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug'] # Slug генерируется автоматически

class NewsArticleSerializer(serializers.ModelSerializer):
    # Показываем название категории вместо ID
    category_name = serializers.CharField(source='category.name', read_only=True)
    # Убираем старое поле image_url
    # image_url = serializers.ImageField(source='image', read_only=True)

    # Добавляем поле для медиафайлов
    media_files = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            'id',
            'title',
            'content',
            # Убираем старое поле image
            # 'image',
            # Убираем старое поле image_url
            # 'image_url',
            'category', # ID категории для создания/обновления
            'category_name', # Название категории для чтения
            'created_at',
            'updated_at',
            # Добавляем новое поле media_files
            'media_files'
        ]
        # Убираем image_url из read_only_fields
        read_only_fields = ['created_at', 'updated_at', 'category_name', 'media_files']
        # Убираем extra_kwargs для image
        extra_kwargs = {
            'category': {'write_only': True, 'required': False, 'allow_null': True},
        }

    def get_media_files(self, obj):
        """ Получает и сериализует связанные медиафайлы. """
        media = obj.media_files.all()
        # Передаем контекст (request) из ViewSet в MediaFileSerializer для генерации полных URL
        return MediaFileSerializer(media, many=True, context=self.context).data

    # Переопределяем to_representation для надежной передачи контекста
    # (хотя context должен передаваться и через SerializerMethodField)
    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     # Убедимся, что медиафайлы сериализуются с контекстом
    #     representation['media_files'] = self.get_media_files(instance)
    #     return representation 