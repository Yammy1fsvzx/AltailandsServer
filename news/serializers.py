from rest_framework import serializers
from .models import Category, NewsArticle

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug'] # Slug генерируется автоматически

class NewsArticleSerializer(serializers.ModelSerializer):
    # Показываем название категории вместо ID
    category_name = serializers.CharField(source='category.name', read_only=True)
    # Поле для получения полного URL изображения
    image_url = serializers.ImageField(source='image', read_only=True)

    class Meta:
        model = NewsArticle
        fields = [
            'id',
            'title',
            'content',
            'image', # Поле для загрузки/обновления изображения (write-only в DRF >= 3.11)
            'image_url', # Поле для чтения URL изображения
            'category', # ID категории для создания/обновления
            'category_name', # Название категории для чтения
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'image_url', 'category_name']
        # Делаем поле image write-only для создания/обновления, а image_url read-only для получения
        # (Для DRF < 3.11 может потребоваться другая настройка или кастомное поле)
        extra_kwargs = {
            'image': {'write_only': True, 'required': False}, # Изображение не обязательно
            'category': {'write_only': True, 'required': False, 'allow_null': True}, # Категория не обязательна
        } 