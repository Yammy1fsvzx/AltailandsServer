from django.db import models
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericRelation
from catalog.models import MediaFile

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название категории')
    slug = models.SlugField(max_length=120, unique=True, blank=True, verbose_name='Slug (ЧПУ)')

    class Meta:
        verbose_name = 'Категория новостей'
        verbose_name_plural = 'Категории новостей'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "category"
            potential_slug = base_slug
            counter = 1
            # Проверяем, существует ли такой slug
            while Category.objects.filter(slug=potential_slug).exclude(pk=self.pk).exists():
                # Если существует, добавляем суффикс
                potential_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = potential_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class NewsArticle(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    category = models.ForeignKey(Category, related_name='articles', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Категория')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    view_count = models.PositiveIntegerField(default=0, verbose_name='Счетчик просмотров')

    media_files = GenericRelation(MediaFile)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
