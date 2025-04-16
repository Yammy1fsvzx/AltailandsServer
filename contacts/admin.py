from django.contrib import admin
from .models import Contact, WorkingHours

class WorkingHoursInline(admin.TabularInline):
    model = WorkingHours
    extra = 1 # Показать 1 пустую форму для добавления
    fields = ('day_of_week', 'start_time', 'end_time', 'is_active')
    ordering = ('day_of_week',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'whatsapp', 'email', 'office_address', 'updated_at')
    search_fields = ('phone', 'whatsapp', 'email', 'office_address')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [WorkingHoursInline]
    fieldsets = (
        (None, {
            'fields': ('phone', 'whatsapp', 'email', 'office_address')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',), # Скрыть по умолчанию
        }),
    )

# Отдельно регистрировать WorkingHours не обязательно, если управляем через inline
# admin.site.register(WorkingHours)
