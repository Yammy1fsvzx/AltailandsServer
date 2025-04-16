from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Request, AdminComment

class AdminCommentInline(admin.TabularInline):
    model = AdminComment
    extra = 0 # Не показывать пустые формы по умолчанию
    fields = ('user', 'comment', 'created_at')
    readonly_fields = ('user', 'created_at')
    ordering = ('-created_at',)
    # Запрещаем добавление комментариев через этот инлайн, если хотим
    # can_delete = False
    # def has_add_permission(self, request, obj=None):
    #     return False
    # def has_change_permission(self, request, obj=None):
    #      return False # Запрет изменения через инлайн

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'request_type_display', 'status', 'created_at', 'related_object_link')
    list_filter = ('status', 'request_type', 'created_at')
    search_fields = ('name', 'phone', 'email', 'user_message')
    readonly_fields = (
        'id', 'name', 'phone', 'email', 'request_type',
        'created_at', 'updated_at', 'related_object_link',
        'quiz_answers', 'user_message' # Отображаем, но не даем редактировать
    )
    list_editable = ('status',) # Позволяем быстро менять статус из списка
    inlines = [AdminCommentInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'name', 'phone', 'email', 'request_type')
        }),
         ('Статус и обработка', {
            'fields': ('status',) # Только статус можно менять
        }),
        ('Детали заявки', {
            'fields': ('user_message', 'quiz_answers', 'related_object_link')
        }),
         ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Связанный объект')
    def related_object_link(self, obj):
        if obj.related_object:
            link = reverse(f"admin:{obj.content_type.app_label}_{obj.content_type.model}_change", args=[obj.object_id])
            return format_html('<a href="{}">{}</a>', link, obj.related_object)
        return "-"

    def get_queryset(self, request):
        # Оптимизация запроса для отображения связанного объекта
        return super().get_queryset(request).select_related('content_type').prefetch_related('admin_comments__user')

    def request_type_display(self, obj):
        return obj.get_request_type_display()
    request_type_display.short_description = 'Тип заявки'

# Отдельно AdminComment можно не регистрировать
# admin.site.register(AdminComment)
