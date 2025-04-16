from rest_framework import serializers
from .models import Location, Feature, LandUseType, LandCategory, MediaFile, LandPlot, ListingComplex, ListingUnit

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

class ListingComplexSerializer(serializers.ModelSerializer):
    # Вложенные сериализаторы для чтения
    location = LocationSerializer(read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    media_files = MediaFileSerializer(many=True, read_only=True)

    # Поля для записи связей по ID
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='location', write_only=True, required=True, label='ID Местоположения'
    )
    feature_ids = serializers.PrimaryKeyRelatedField(
        queryset=Feature.objects.filter(type='complex_infrastructure'),
        source='features', many=True, write_only=True, required=False, label='ID Инфраструктуры/Особенностей комплекса'
    )

    # Отображение choices
    complex_type_display = serializers.CharField(source='get_complex_type_display', read_only=True)
    listing_status_display = serializers.CharField(source='get_listing_status_display', read_only=True)

    class Meta:
        model = ListingComplex
        fields = [
            'id',
            'name', 'slug', 'description',
            'complex_type', 'complex_type_display',
            'location', # Чтение
            'location_id', # Запись
            'features', # Чтение
            'feature_ids', # Запись
            'listing_status', 'listing_status_display',
            'created_at', 'updated_at',
            'media_files' # Только чтение медиа
            # 'units' - не включаем сюда список юнитов
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'media_files']

    # Передаем контекст в MediaFileSerializer
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['media_files'] = MediaFileSerializer(instance.media_files.all(), many=True, context=self.context).data
        return representation 

class ListingUnitSerializer(serializers.ModelSerializer):
    # Вложенные для чтения
    # complex = ListingComplexSerializer(read_only=True) # Можно сделать так, но может быть избыточно
    complex_name = serializers.CharField(source='complex.name', read_only=True)
    features = FeatureSerializer(many=True, read_only=True)
    media_files = MediaFileSerializer(many=True, read_only=True)

    # Поля для записи ID
    complex_id = serializers.PrimaryKeyRelatedField(
        queryset=ListingComplex.objects.all(), source='complex', write_only=True, required=True, label='ID Комплекса'
    )
    feature_ids = serializers.PrimaryKeyRelatedField(
        queryset=Feature.objects.filter(type='unit_feature'),
        source='features', many=True, write_only=True, required=False, label='ID Особенностей юнита'
    )

    # Отображение choices
    unit_status_display = serializers.CharField(source='get_unit_status_display', read_only=True)

    class Meta:
        model = ListingUnit
        fields = [
            'id',
            'complex', # ID комплекса для фильтрации/чтения
            'complex_name', # Название комплекса для удобства чтения
            'complex_id', # Для записи связи с комплексом
            'unit_identifier', 'floor', 'area', 'rooms', 'price',
            'unit_status', 'unit_status_display',
            'features', # Чтение
            'feature_ids', # Запись
            'created_at', 'updated_at',
            'media_files' # Чтение медиа
        ]
        read_only_fields = ['complex', 'created_at', 'updated_at', 'media_files']

    # Передаем контекст в MediaFileSerializer
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Включаем ID комплекса в представление для удобства
        representation['complex'] = instance.complex_id
        representation['media_files'] = MediaFileSerializer(instance.media_files.all(), many=True, context=self.context).data
        return representation 