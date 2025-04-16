from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import (
    Location, Feature, LandUseType, LandCategory, MediaFile,
    LandPlot, ListingComplex, ListingUnit
)

# --- Инлайны ---
class MediaFileInline(GenericTabularInline):
    model = MediaFile
    extra = 1
    fields = ('file', 'type', 'description', 'is_main', 'order')
    verbose_name = "Медиафайл"
    verbose_name_plural = "Медиафайлы"

class ListingUnitInline(admin.TabularInline):
    model = ListingUnit
    extra = 1
    fields = ('unit_identifier', 'floor', 'area', 'rooms', 'price', 'unit_status')
    readonly_fields = ('view_count',)
    show_change_link = True # Ссылка на редактирование юнита
    verbose_name = "Юнит (квартира, апартамент...)"
    verbose_name_plural = "Юниты в комплексе"

# --- Админки для справочников ---
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('region', 'locality', 'address_line')
    search_fields = ('region', 'locality', 'address_line')
    list_filter = ('region',)

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    list_filter = ('type',)
    search_fields = ('name',)

@admin.register(LandUseType)
class LandUseTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(LandCategory)
class LandCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# --- Админки для основных моделей ---

@admin.register(LandPlot)
class LandPlotAdmin(admin.ModelAdmin):
    list_display = ('title', 'land_type', 'area', 'price', 'plot_status', 'listing_status', 'view_count')
    list_filter = ('land_type', 'plot_status', 'listing_status', 'location__region', 'land_category')
    search_fields = ('title', 'description', 'location__locality', 'cadastral_numbers', 'slug')
    readonly_fields = ('created_at', 'updated_at', 'price_per_are', 'view_count')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('land_use_types', 'features')
    inlines = [MediaFileInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'land_type', 'description', 'listing_status', 'plot_status')
        }),
        ('Местоположение и Земля', {
            'fields': ('location', 'cadastral_numbers', 'land_category', 'land_use_types')
        }),
        ('Характеристики', {
            'fields': ('area', 'price', 'price_per_are', 'features')
        }),
        ('Статистика и Даты', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

@admin.register(ListingComplex)
class ListingComplexAdmin(admin.ModelAdmin):
    list_display = ('name', 'complex_type', 'location', 'listing_status', 'view_count')
    list_filter = ('complex_type', 'listing_status', 'location__region')
    search_fields = ('name', 'description', 'location__locality', 'slug')
    readonly_fields = ('created_at', 'updated_at', 'view_count')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('features',)
    inlines = [ListingUnitInline, MediaFileInline]
    fieldsets = (
         ('Основная информация', {
            'fields': ('name', 'slug', 'complex_type', 'description', 'listing_status')
        }),
        ('Местоположение и Инфраструктура', {
            'fields': ('location', 'features')
        }),
         ('Статистика и Даты', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

@admin.register(ListingUnit)
class ListingUnitAdmin(admin.ModelAdmin):
    list_display = ('unit_identifier', 'complex', 'area', 'rooms', 'price', 'unit_status', 'view_count')
    list_filter = ('complex', 'unit_status', 'rooms', 'floor')
    search_fields = ('unit_identifier', 'complex__name')
    readonly_fields = ('created_at', 'updated_at', 'view_count')
    filter_horizontal = ('features',)
    inlines = [MediaFileInline]
    list_select_related = ('complex',) # Оптимизация для отображения complex в list_display
    fieldsets = (
        (None, {
            'fields': ('complex', 'unit_identifier', 'unit_status')
        }),
        ('Характеристики', {
            'fields': ('floor', 'area', 'rooms', 'price', 'features')
        }),
        ('Статистика и Даты', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

# MediaFile можно не регистрировать отдельно, если управляем только через инлайны
# admin.site.register(MediaFile)
