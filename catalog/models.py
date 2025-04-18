from django.db import models
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import random
import os # Импортируем os для работы с путями

# --- Вспомогательные модели ---

class Location(models.Model):
    region = models.CharField(max_length=100, verbose_name='Регион')
    locality = models.CharField(max_length=100, verbose_name='Населенный пункт')
    address_line = models.CharField(max_length=255, blank=True, verbose_name='Улица, дом и т.д.')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Широта')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Долгота')

    class Meta:
        verbose_name = 'Местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return f"{self.region}, {self.locality}, {self.address_line}"

class Feature(models.Model):
    FEATURE_TYPE_CHOICES = (
        ('communication', 'Коммуникация участка'),
        ('plot_feature', 'Особенность участка'),
        ('complex_infrastructure', 'Инфраструктура комплекса'),
        ('unit_feature', 'Особенность юнита (отделка и т.п.)'),
    )
    name = models.CharField(max_length=150, unique=True, verbose_name='Название')
    type = models.CharField(max_length=30, choices=FEATURE_TYPE_CHOICES, verbose_name='Тип')

    class Meta:
        verbose_name = 'Особенность/Характеристика'
        verbose_name_plural = 'Особенности/Характеристики'
        ordering = ['type', 'name']

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"

class LandUseType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название ВРИ')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Вид разрешенного использования (ВРИ)'
        verbose_name_plural = 'Виды разрешенного использования (ВРИ)'

    def __str__(self):
        return self.name

class LandCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название категории земель')

    class Meta:
        verbose_name = 'Категория земель'
        verbose_name_plural = 'Категории земель'

    def __str__(self):
        return self.name

# --- Функция для динамического пути загрузки медиа ---

def get_media_upload_path(instance, filename):
    """ Определяет путь для загрузки медиафайла в зависимости от родительского объекта. """
    # instance - это объект MediaFile
    # filename - исходное имя файла

    # Получаем родительский объект
    content_object = instance.content_object
    object_pk = instance.object_id or "unknown_pk" # ID родительского объекта

    # Определяем базовую папку
    base_folder = "other_media" # Папка по умолчанию

    if isinstance(content_object, LandPlot):
        base_folder = "landplots"
    elif isinstance(content_object, GenericProperty):
        prop_type_slug = content_object.property_type.slug if content_object.property_type else "unknown_type"
        if prop_type_slug == 'news': # <--- Специальный случай для новостей
            base_folder = "news"
        else:
            # Для других GenericProperty можно использовать slug типа
            base_folder = f"properties/{prop_type_slug}"

    # Генерируем путь: media_root/base_folder/object_pk/filename
    # object_pk добавляется, чтобы файлы разных объектов не конфликтовали
    return os.path.join(base_folder, str(object_pk), filename)

# --- Модель для Медиа ---

class MediaFile(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('image', 'Изображение'),
        ('video', 'Видео'),
        ('document', 'Документ'),
        ('plan', 'Планировка'),
    )
    # Настройка Generic Foreign Key
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Используем динамический путь загрузки
    file = models.FileField(upload_to=get_media_upload_path, verbose_name='Файл')
    type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image', verbose_name='Тип файла')
    is_main = models.BooleanField(default=False, verbose_name='Главный файл (обложка)')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')
    description = models.CharField(max_length=255, blank=True, verbose_name='Описание файла')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Медиафайл'
        verbose_name_plural = 'Медиафайлы'
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return f"{self.get_type_display()} для {self.content_object} (ID: {self.id})"

# --- Основные модели объявлений ---

class LandPlot(models.Model):
    LAND_TYPE_CHOICES = (
        ('standard', 'Стандартный участок'),
        ('new_territory', 'Новообразованная территория'),
    )
    PLOT_STATUS_CHOICES = (
        ('available', 'Доступен'),
        ('sold', 'Продан'),
        ('reserved', 'Бронь'),
    )
    LISTING_STATUS_CHOICES = (
        ('published', 'Опубликовано'),
        ('hidden', 'Скрыто'),
    )

    land_type = models.CharField(max_length=20, choices=LAND_TYPE_CHOICES, default='standard', verbose_name='Тип участка')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(blank=True, verbose_name='Описание')
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name='Slug (ЧПУ)', db_index=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='land_plots', verbose_name='Местоположение', db_index=True)
    cadastral_numbers = models.TextField(blank=True, verbose_name='Кадастровые номера (через запятую или JSON)')
    land_use_types = models.ManyToManyField(LandUseType, blank=True, related_name='land_plots', verbose_name='ВРИ')
    land_category = models.ForeignKey(LandCategory, on_delete=models.PROTECT, null=True, blank=True, related_name='land_plots', verbose_name='Категория земель')
    features = models.ManyToManyField(Feature, blank=True, related_name='land_plots', limit_choices_to={'type__in': ['communication', 'plot_feature']}, verbose_name='Коммуникации и особенности')
    area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Площадь (в сотках)', db_index=True)
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Цена (руб.)', db_index=True)
    price_per_are = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Цена за сотку (руб.)')
    plot_status = models.CharField(max_length=10, choices=PLOT_STATUS_CHOICES, default='available', verbose_name='Статус участка')
    listing_status = models.CharField(max_length=10, choices=LISTING_STATUS_CHOICES, default='hidden', verbose_name='Статус объявления', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    view_count = models.PositiveIntegerField(default=0, verbose_name='Счетчик просмотров')

    media_files = GenericRelation(MediaFile) # Связь с медиафайлами

    class Meta:
        verbose_name = 'Земельный участок'
        verbose_name_plural = 'Земельные участки'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            # Улучшенная генерация slug с проверкой уникальности
            base_slug = slugify(self.title) or f"landplot-{random.randint(1000, 9999)}"
            slug = base_slug
            counter = 1
            while LandPlot.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Рассчитываем цену за сотку, если не указана
        if self.price and self.area and not self.price_per_are:
            try:
                self.price_per_are = round(self.price / self.area, 2)
            except: # Обработка деления на ноль или других ошибок
                pass
        elif self.price_per_are and self.area and not self.price: # Рассчитываем цену, если указана цена за сотку
             try:
                 self.price = round(self.price_per_are * self.area, 2)
             except:
                 pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# --- Новые модели для динамических типов недвижимости ---

class PropertyType(models.Model):
    """ Определяет тип объекта недвижимости (кроме LandPlot) и схему его атрибутов """
    name = models.CharField(max_length=100, unique=True, verbose_name="Название типа")
    slug = models.SlugField(max_length=120, unique=True, blank=True, verbose_name="Slug типа")
    # Схема атрибутов в формате JSON Schema (или упрощенном виде)
    # Пример: {"area_sqm": {"type": "number", "label": "Площадь (кв.м.)", "required": True},
    #          "rooms": {"type": "integer", "label": "Кол-во комнат", "required": False},
    #          "floor": {"type": "integer", "label": "Этаж"} }
    attribute_schema = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Схема атрибутов (JSON)",
        help_text="Определите поля для этого типа недвижимости в формате JSON"
    )

    class Meta:
        verbose_name = "Тип объекта недвижимости"
        verbose_name_plural = "Типы объектов недвижимости"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) or f"type-{self.id or random.randint(1000, 9999)}"
            # Проверка уникальности slug (можно добавить цикл как в др. моделях)
        super().save(*args, **kwargs)
        # Валидация JSON Schema (опционально, требует jsonschema)
        # self.validate_schema()

    # def validate_schema(self):
    #     if JSONSCHEMA_AVAILABLE:
    #         try:
    #             # Здесь можно добавить более строгую валидацию самой схемы
    #             # jsonschema.Draft7Validator.check_schema(self.attribute_schema)
    #             pass # Простая проверка, что это словарь
    #             if not isinstance(self.attribute_schema, dict):
    #                 raise ValidationError("Схема атрибутов должна быть JSON-объектом (словарем).")
    #         except Exception as e: # jsonschema.exceptions.SchemaError
    #             raise ValidationError(f"Ошибка в JSON Schema атрибутов: {e}")
    #     elif not isinstance(self.attribute_schema, dict):
    #          raise ValidationError("Схема атрибутов должна быть JSON-объектом (словарем).")

    def __str__(self):
        return self.name

class GenericProperty(models.Model):
    """ Универсальная модель для объектов недвижимости (кроме LandPlot) """
    LISTING_STATUS_CHOICES = (
        ("published", "Опубликовано"),
        ("hidden", "Скрыто"),
        ("reserved", "Резерв"),
        ("sold", "Продано"),
    )

    property_type = models.ForeignKey(
        PropertyType, on_delete=models.PROTECT,
        related_name="properties",
        verbose_name="Тип объекта",
        db_index=True
    )
    # Связь для представления иерархии (например, Юнит внутри Комплекса)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="children",
        verbose_name="Родительский объект (комплекс)"
    )
    # Кто владелец/добавил объект - УДАЛЕНО
    # owner = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.SET_NULL,
    #     null=True, blank=True,
    #     related_name='generic_properties',
    #     verbose_name='Владелец/Агент'
    # )

    # Общие поля
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name="Slug (ЧПУ)", db_index=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="generic_properties", verbose_name="Местоположение", db_index=True)
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Цена (руб.)", db_index=True)
    listing_status = models.CharField(
        max_length=10, choices=LISTING_STATUS_CHOICES,
        default="hidden", verbose_name="Статус объявления", db_index=True
    )

    # Динамические атрибуты
    attributes = models.JSONField(
        default=dict, blank=True,
        verbose_name="Атрибуты объекта",
        help_text="Значения атрибутов согласно схеме типа объекта"
    )

    # Стандартные поля
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    view_count = models.PositiveIntegerField(default=0, verbose_name="Счетчик просмотров")

    # Связь с медиафайлами
    media_files = GenericRelation(MediaFile)

    class Meta:
        verbose_name = "Объект недвижимости (универсальный)"
        verbose_name_plural = "Объекты недвижимости (универсальные)"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # Генерация slug (можно улучшить проверкой уникальности)
        if not self.slug:
            base_slug = slugify(self.title) or f"{self.property_type.slug}-{random.randint(1000, 9999)}"
            slug = base_slug
            counter = 1
            while GenericProperty.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        # Валидация атрибутов по схеме (опционально)
        # self.validate_attributes()
        super().save(*args, **kwargs)

    # def validate_attributes(self):
    #     schema = self.property_type.attribute_schema
    #     if not schema or not JSONSCHEMA_AVAILABLE:
    #         return
    #     try:
    #         jsonschema.validate(instance=self.attributes, schema=schema)
    #     except jsonschema.exceptions.ValidationError as e:
    #         raise ValidationError(f"Ошибка валидации атрибутов: {e.message}")

    def __str__(self):
        return self.title
