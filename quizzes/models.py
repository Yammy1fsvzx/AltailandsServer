from django.db import models
from django.utils.text import slugify

class Quiz(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок квиза')
    slug = models.SlugField(max_length=220, unique=True, blank=True, help_text='Уникальный идентификатор для URL (если квизов будет несколько)')
    description = models.TextField(blank=True, verbose_name='Описание квиза', help_text='Краткое описание или введение к квизу')
    is_active = models.BooleanField(default=False, verbose_name='Активен', help_text='Отметьте, если этот квиз должен отображаться на сайте')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Квиз'
        verbose_name_plural = 'Квизы'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Простая логика для уникальности slug, можно усложнить при необходимости
            original_slug = self.slug
            counter = 1
            while Quiz.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE, verbose_name='Квиз')
    text = models.TextField(verbose_name='Текст вопроса')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок вопроса')

    class Meta:
        verbose_name = 'Вопрос квиза'
        verbose_name_plural = 'Вопросы квиза'
        ordering = ['quiz', 'order']

    def __str__(self):
        return f"Вопрос {self.order}: {self.text[:50]}... (Квиз: {self.quiz.title})"

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE, verbose_name='Вопрос')
    text = models.CharField(max_length=255, verbose_name='Текст ответа')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок ответа')

    class Meta:
        verbose_name = 'Ответ на вопрос квиза'
        verbose_name_plural = 'Ответы на вопросы квиза'
        ordering = ['question', 'order']

    def __str__(self):
        return f"Ответ {self.order}: {self.text} (Вопрос: {self.question.id})"
