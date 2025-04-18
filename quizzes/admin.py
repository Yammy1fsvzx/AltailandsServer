from django.contrib import admin
from .models import Quiz, Question, Answer

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    fields = ('text', 'order')
    ordering = ('order',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'order')
    list_filter = ('quiz',)
    search_fields = ('text',)
    inlines = [AnswerInline]
    ordering = ('quiz', 'order')

class QuestionInline(admin.StackedInline): # Используем StackedInline для вопросов
    model = Question
    extra = 1
    fields = ('text', 'order')
    ordering = ('order',)
    ordering_field = 'order'
    hide_ordering_field = True
    show_change_link = True

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [QuestionInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'is_active')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
