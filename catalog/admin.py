from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db import models
# Убираем импорты, связанные с django-jsonform
# from django_jsonform.widgets import JSONSchemaEditorWidget
# Импортируем виджет NumberInput из unfold
from unfold.contrib.forms import widgets

from .models import (
    Location, Feature, LandUseType, LandCategory, MediaFile,
    LandPlot, PropertyType, GenericProperty
)

# --- Инлайны и Админки справочников (без изменений) --- #
class MediaFileInline(GenericTabularInline):
    model = MediaFile
    extra = 1
    fields = (
        "file",
        "type",
        "description",
        "is_main",
        "order",
    )
    verbose_name = "Медиафайл"
    verbose_name_plural = "Медиафайлы"

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "region",
        "locality",
        "address_line",
    )
    search_fields = (
        "region",
        "locality",
        "address_line",
    )
    list_filter = ("region",)

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
    list_filter = ("type",)
    search_fields = ("name",)

@admin.register(LandUseType)
class LandUseTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(LandCategory)
class LandCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

# --- Админки для основных моделей --- #
@admin.register(LandPlot)
class LandPlotAdmin(admin.ModelAdmin):
    list_display = (
        "title", "land_type", "area", "price",
        "plot_status", "listing_status", "view_count",
    )
    list_filter = (
        "land_type", "plot_status", "listing_status",
        "location__region", "land_category",
    )
    search_fields = (
        "title", "description", "location__locality",
        "cadastral_numbers", "slug",
    )
    readonly_fields = ("created_at", "updated_at", "price_per_are", "view_count")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("land_use_types", "features")
    inlines = [MediaFileInline]
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "title", "slug", "land_type", "description",
                    "listing_status", "plot_status",
                )
            },
        ),
        (
            "Местоположение и Земля",
            {
                "fields": (
                    "location", "cadastral_numbers", "land_category",
                    "land_use_types",
                )
            },
        ),
        ("Характеристики", {"fields": ("area", "price", "price_per_are", "features")}),
        (
            "Статистика и Даты",
            {
                "fields": ("view_count", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

# --- Админки для новых моделей --- #
@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug")}),
        ("Схема атрибутов", {"fields": ("attribute_schema",)}),
    )

@admin.register(GenericProperty)
class GenericPropertyAdmin(admin.ModelAdmin):
    list_display = (
        "title", "property_type", "parent",
        "price", "listing_status", "view_count",
    )
    list_filter = ("property_type", "listing_status", "location__region")
    search_fields = ("title", "description", "location__locality", "slug")
    readonly_fields = ("created_at", "updated_at", "view_count")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ["parent", "location", "property_type"]
    inlines = [MediaFileInline]
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "title", "slug", "property_type", "parent",
                    "description", "listing_status",
                )
            },
        ),
        ("Местоположение и Цена", {"fields": ("location", "price")}),
        ("Динамические атрибуты", {"fields": ("attributes",)}),
        (
            "Статистика и Даты",
            {
                "fields": ("view_count", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

# MediaFile можно не регистрировать отдельно, если управляем только через инлайны
# admin.site.register(MediaFile)
