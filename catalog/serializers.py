from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
import jsonschema
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from .models import (
    Location, Feature, LandUseType, LandCategory, MediaFile, LandPlot,
    PropertyType, GenericProperty
)

User = get_user_model()

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'region', 'locality', 'address_line', 'latitude', 'longitude']

class FeatureSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Feature
        fields = ['id', 'name', 'type', 'type_display']

class LandUseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandUseType
        fields = ['id', 'name', 'description']

class LandCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LandCategory
        fields = ['id', 'name']

class MediaFileSerializer(serializers.ModelSerializer):
    # Поле для получения полного URL
    file_url = serializers.SerializerMethodField(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = MediaFile
        fields = [
            'id',
            'file', # Для загрузки файла (write-only)
            'file_url', # Для чтения URL
            'type', # Тип файла при загрузке
            'type_display', # Отображение типа файла
            'is_main',
            'order',
            'description',
            'uploaded_at'
        ]
        read_only_fields = ['uploaded_at', 'file_url', 'type_display']
        extra_kwargs = {
            'file': {'write_only': True}
        }

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

class LandPlotSerializer(serializers.ModelSerializer):
    # Вложенные сериализаторы для чтения связанных объектов
    location = LocationSerializer(read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    land_use_types = LandUseTypeSerializer(many=True, read_only=True)
    land_category = LandCategorySerializer(read_only=True)
    media_files = MediaFileSerializer(many=True, read_only=True)

    # Поля PrimaryKeyRelatedField для записи связей по ID
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='location', write_only=True, required=True, label='ID Местоположения'
    )
    feature_ids = serializers.PrimaryKeyRelatedField(
        queryset=Feature.objects.filter(type__in=['communication', 'plot_feature']),
        source='features', many=True, write_only=True, required=False, label='ID Коммуникаций/Особенностей'
    )
    land_use_type_ids = serializers.PrimaryKeyRelatedField(
        queryset=LandUseType.objects.all(), source='land_use_types',
        many=True, write_only=True, required=False, label='ID ВРИ'
    )
    land_category_id = serializers.PrimaryKeyRelatedField(
        queryset=LandCategory.objects.all(), source='land_category',
        write_only=True, required=False, allow_null=True, label='ID Категории земель'
    )

    # Поля для читаемого отображения choices
    land_type_display = serializers.CharField(source='get_land_type_display', read_only=True)
    plot_status_display = serializers.CharField(source='get_plot_status_display', read_only=True)
    listing_status_display = serializers.CharField(source='get_listing_status_display', read_only=True)

    class Meta:
        model = LandPlot
        fields = [
            'id',
            'title', 'slug', 'description',
            'land_type', 'land_type_display',
            'location', # Для чтения
            'location_id', # Для записи
            'cadastral_numbers',
            'land_use_types', # Для чтения
            'land_use_type_ids', # Для записи
            'land_category', # Для чтения
            'land_category_id', # Для записи
            'features', # Для чтения
            'feature_ids', # Для записи
            'area', 'price', 'price_per_are',
            'plot_status', 'plot_status_display',
            'listing_status', 'listing_status_display',
            'created_at', 'updated_at',
            'media_files' # Только чтение медиа, привязанных к участку
        ]
        read_only_fields = ['slug', 'price_per_are', 'created_at', 'updated_at', 'media_files'] # slug и price_per_are генерируются/рассчитываются

    # Передаем контекст в MediaFileSerializer для генерации URL
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Передаем контекст в MediaFileSerializer
        representation['media_files'] = MediaFileSerializer(instance.media_files.all(), many=True, context=self.context).data
        return representation 

class PropertyTypeSerializer(serializers.ModelSerializer):
    """ Сериализатор для Типа Объекта Недвижимости """
    available_filters = serializers.SerializerMethodField()

    class Meta:
        model = PropertyType
        fields = ["id", "name", "slug", "attribute_schema", "available_filters"]
        read_only_fields = ["slug"] # Slug генерируется автоматически

    def get_available_filters(self, obj):
        filters = []
        schema = obj.attribute_schema

        # 1. Убедимся, что schema вообще является словарем
        if not isinstance(schema, dict):
            return filters # Если не словарь (или null), возвращаем пусто

        # 2. Определяем, где находятся описания свойств
        properties_dict = None
        if 'properties' in schema and isinstance(schema.get('properties'), dict):
            # Стандартный случай: есть ключ 'properties' и его значение - словарь
            properties_dict = schema['properties']
        elif schema: # Если ключа 'properties' нет, но сам schema не пустой словарь
            # Проверяем, похожи ли значения в schema на описания свойств (т.е. являются словарями)
            # Это эвристика, чтобы случайно не обработать {"type": "object"} как свойство
            is_likely_properties = all(isinstance(v, dict) for k, v in schema.items() if k != 'type') # Игнорируем ключ 'type' если он есть
            if is_likely_properties:
                 # Считаем, что атрибуты находятся прямо в корне schema
                properties_dict = {k: v for k, v in schema.items() if k != 'type'} # Копируем все, кроме 'type'

        # 3. Если не удалось найти словарь со свойствами, выходим
        if not isinstance(properties_dict, dict):
             return filters

        # 4. Итерируем по найденному словарю свойств
        for attr_name, attr_props in properties_dict.items():
            # Убедимся, что описание свойства - это словарь
            if not isinstance(attr_props, dict):
                continue # Пропускаем, если описание некорректно

            # Пытаемся получить 'title', потом 'label', иначе используем имя атрибута
            label = attr_props.get('title', attr_props.get('label', attr_name))
            attr_type = attr_props.get('type')
            param_base = f"attr_{attr_name}"

            # --- Логика генерации фильтров (остается без изменений) ---
            if attr_type in ['integer', 'number']:
                filters.append({
                    "param_min": f"{param_base}_min",
                    "param_max": f"{param_base}_max",
                    "label": label,
                    "type": "range",
                    "units": attr_props.get('units', '')
                })
            elif attr_type == 'boolean':
                 filters.append({
                    "param": param_base,
                    "label": label,
                    "type": "boolean"
                })
            elif attr_type == 'string' and 'enum' in attr_props:
                 filters.append({
                    "param": f"{param_base}_in",
                    "label": label,
                    "type": "select",
                    "options": attr_props.get('enum', [])
                })
            # ... можно добавить другие типы ...

        return filters

class GenericPropertySerializer(serializers.ModelSerializer):
    """ Сериализатор для Универсального Объекта Недвижимости """
    # Вложенные сериализаторы для чтения
    property_type = PropertyTypeSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    # media_files = MediaFileSerializer(many=True, read_only=True) # Media files handled by GenericRelation
    # parent = serializers.PrimaryKeyRelatedField(read_only=True) # Показываем только ID родителя
    parent_slug = serializers.SlugField(source="parent.slug", read_only=True) # Или slug родителя
    children_count = serializers.IntegerField(source="children.count", read_only=True) # Кол-во дочерних элементов

    # Поля для записи связей по ID
    property_type_id = serializers.PrimaryKeyRelatedField(
        queryset=PropertyType.objects.all(), source="property_type", write_only=True,
        required=True, label="ID Типа объекта"
    )
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source="location", write_only=True,
        required=True, label="ID Местоположения"
    )
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=GenericProperty.objects.all(), source="parent", write_only=True,
        required=False, allow_null=True, label="ID Родительского объекта (комплекса)"
    )

    # Отображение choices
    listing_status_display = serializers.CharField(source="get_listing_status_display", read_only=True)

    # Сериализатор для медиафайлов
    media_files = serializers.SerializerMethodField()

    class Meta:
        model = GenericProperty
        fields = [
            "id", "title", "slug", "description",
            "property_type", "property_type_id",
            "parent", "parent_id", "parent_slug", "children_count", # Связи иерархии
            "location", "location_id",
            "price", "listing_status", "listing_status_display",
            "attributes", # Динамические атрибуты как JSON
            "created_at", "updated_at", "view_count",
            "media_files" # Медиафайлы
        ]
        read_only_fields = [
            "slug", "created_at", "updated_at", "view_count", "media_files",
            "property_type", "location", "parent", "parent_slug", "children_count"
        ]
        # Важно: атрибуты (JSON) должны быть writable

    def get_media_files(self, obj):
        # Используем существующий MediaFileSerializer для представления медиафайлов
        media = obj.media_files.all()
        return MediaFileSerializer(media, many=True, context=self.context).data

    def validate(self, data):
        """ Валидируем атрибуты по схеме типа объекта """
        # Получаем property_type: либо из данных запроса (при создании/изменении типа),
        # либо из существующего инстанса (при частичном обновлении без изменения типа)
        prop_type = data.get("property_type")
        if not prop_type and self.instance:
            prop_type = self.instance.property_type

        # Получаем атрибуты из данных запроса
        attributes = data.get("attributes")

        # Если есть и тип, и атрибуты, и схема у типа - валидируем
        if prop_type and attributes and isinstance(prop_type.attribute_schema, dict) and prop_type.attribute_schema:
            schema = prop_type.attribute_schema
            try:
                # Проверяем саму схему на валидность (базово)
                # jsonschema.Draft7Validator.check_schema(schema)
                # Валидируем данные по схеме
                jsonschema.validate(instance=attributes, schema=schema)
            except JsonSchemaValidationError as e:
                # Если ошибка валидации данных по схеме
                raise ValidationError({"attributes": f"Ошибка валидации данных атрибутов: {e.message}"}) # Указываем поле 'attributes'
            except Exception as e:
                # Если ошибка в самой схеме (менее вероятно, но возможно)
                # В продакшене лучше логировать эту ошибку
                print(f"Warning: Invalid JSON schema for PropertyType ID {prop_type.id}: {e}")
                # Можно либо пропустить валидацию, либо вернуть ошибку 500
                # raise ValidationError({"attribute_schema": f"Невалидная схема для типа {prop_type.name}: {e}"})
                pass # Пропускаем валидацию, если сама схема некорректна

        # Простая проверка, что атрибуты - это словарь, если не было валидации по схеме
        elif attributes and not isinstance(attributes, dict):
             raise ValidationError({"attributes": "Атрибуты должны быть JSON-объектом (словарем)."})

        return data