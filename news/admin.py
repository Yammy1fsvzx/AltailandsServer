from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Category, NewsArticle
from catalog.models import MediaFile # Импортируем MediaFile из listings

class MediaFileInline(GenericTabularInline):
    model = MediaFile
    extra = 1
    fields = ('file', 'type', 'description', 'is_main', 'order')
    # Добавляем ссылку на изменение объекта MediaFile (если он зарегистрирован отдельно)
    # show_change_link = True 

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at', 'view_count', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at', 'view_count')
    inlines = [MediaFileInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'category', 'content')
        }),
        ('Статистика и Даты', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
