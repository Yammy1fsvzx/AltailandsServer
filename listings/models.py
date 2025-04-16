from django.db import models
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

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

    file = models.FileField(upload_to='listings_media/', verbose_name='Файл') # Путь будет уточнен позже, возможно динамически
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
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name='Slug (ЧПУ)')
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='land_plots', verbose_name='Местоположение')
    cadastral_numbers = models.TextField(blank=True, verbose_name='Кадастровые номера (через запятую или JSON)')
    land_use_types = models.ManyToManyField(LandUseType, blank=True, related_name='land_plots', verbose_name='ВРИ')
    land_category = models.ForeignKey(LandCategory, on_delete=models.PROTECT, null=True, blank=True, related_name='land_plots', verbose_name='Категория земель')
    features = models.ManyToManyField(Feature, blank=True, related_name='land_plots', limit_choices_to={'type__in': ['communication', 'plot_feature']}, verbose_name='Коммуникации и особенности')
    area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Площадь (в сотках)')
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Цена (руб.)')
    price_per_are = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Цена за сотку (руб.)')
    plot_status = models.CharField(max_length=10, choices=PLOT_STATUS_CHOICES, default='available', verbose_name='Статус участка')
    listing_status = models.CharField(max_length=10, choices=LISTING_STATUS_CHOICES, default='hidden', verbose_name='Статус объявления')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0, verbose_name='Счетчик просмотров')

    media_files = GenericRelation(MediaFile) # Связь с медиафайлами

    class Meta:
        verbose_name = 'Земельный участок'
        verbose_name_plural = 'Земельные участки'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
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

class ListingComplex(models.Model):
    COMPLEX_TYPE_CHOICES = (
        ('apart_hotel', 'Апарт-отель'),
        ('residential_complex', 'Жилой комплекс'),
        ('cottage_village', 'Коттеджный поселок'),
        ('business_center', 'Бизнес-центр'),
    )
    LISTING_STATUS_CHOICES = (
        ('published', 'Опубликовано'),
        ('hidden', 'Скрыто'),
    )

    complex_type = models.CharField(max_length=30, choices=COMPLEX_TYPE_CHOICES, verbose_name='Тип комплекса')
    name = models.CharField(max_length=200, verbose_name='Название комплекса')
    description = models.TextField(blank=True, verbose_name='Описание комплекса')
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name='Slug (ЧПУ)')
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='complexes', verbose_name='Местоположение')
    features = models.ManyToManyField(Feature, blank=True, related_name='complexes', limit_choices_to={'type': 'complex_infrastructure'}, verbose_name='Инфраструктура/Особенности комплекса')
    listing_status = models.CharField(max_length=10, choices=LISTING_STATUS_CHOICES, default='hidden', verbose_name='Статус объявления')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0, verbose_name='Счетчик просмотров')

    media_files = GenericRelation(MediaFile) # Связь с медиафайлами

    class Meta:
        verbose_name = 'Комплекс/Проект'
        verbose_name_plural = 'Комплексы/Проекты'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            # Генерируем slug из названия и типа, чтобы избежать коллизий
            base_slug = slugify(self.name)
            self.slug = f"{base_slug}-{self.complex_type}"
            # Можно добавить логику проверки уникальности и добавления суффикса при необходимости
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ListingUnit(models.Model):
    UNIT_STATUS_CHOICES = (
        ('available', 'Доступно'),
        ('sold', 'Продано'),
        ('reserved', 'Бронь'),
    )

    complex = models.ForeignKey(ListingComplex, related_name='units', on_delete=models.CASCADE, verbose_name='Комплекс')
    unit_identifier = models.CharField(max_length=100, verbose_name='Идентификатор юнита (номер, название)')
    floor = models.IntegerField(null=True, blank=True, verbose_name='Этаж')
    area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Площадь')
    rooms = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Количество комнат (0 - студия)')
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Цена (руб.)')
    unit_status = models.CharField(max_length=10, choices=UNIT_STATUS_CHOICES, default='available', verbose_name='Статус юнита')
    features = models.ManyToManyField(Feature, blank=True, related_name='units', limit_choices_to={'type': 'unit_feature'}, verbose_name='Особенности юнита (отделка и т.д.)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0, verbose_name='Счетчик просмотров')

    media_files = GenericRelation(MediaFile) # Связь с медиафайлами

    class Meta:
        verbose_name = 'Юнит в комплексе (квартира, апартамент, офис)'
        verbose_name_plural = 'Юниты в комплексах'
        ordering = ['complex', 'unit_identifier']
        unique_together = ('complex', 'unit_identifier') # Уникальный идентификатор в рамках комплекса

    def __str__(self):
        return f"{self.complex.name} - {self.unit_identifier}"
