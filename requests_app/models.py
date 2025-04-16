from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings # Для ссылки на User

class Request(models.Model):
    REQUEST_TYPE_CHOICES = (
        ('quiz', 'Квиз'),
        ('contact', 'Контактная форма'),
        ('listing', 'Объявление'),
    )
    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('processing', 'В обработке'),
        ('completed', 'Завершена'),
        ('rejected', 'Отклонена'),
    )

    name = models.CharField(max_length=150, verbose_name='Имя клиента')
    phone = models.CharField(max_length=20, verbose_name='Телефон клиента')
    email = models.EmailField(blank=True, null=True, verbose_name='Email клиента')
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPE_CHOICES, verbose_name='Тип заявки')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    # Поля для связи с источником (GenericForeignKey)
    # null=True, blank=True нужны, если заявка типа 'contact' и не связана ни с чем
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Тип связанного объекта')
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='ID связанного объекта')
    related_object = GenericForeignKey('content_type', 'object_id')

    # Поля для специфических данных
    quiz_answers = models.JSONField(null=True, blank=True, verbose_name='Ответы на квиз')
    user_message = models.TextField(blank=True, verbose_name='Сообщение пользователя')

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка №{self.id} от {self.name} ({self.get_request_type_display()})"

class AdminComment(models.Model):
    request = models.ForeignKey(Request, related_name='admin_comments', on_delete=models.CASCADE, verbose_name='Заявка')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Администратор')
    comment = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Комментарий администратора'
        verbose_name_plural = 'Комментарии администраторов'
        ordering = ['created_at']

    def __str__(self):
        user_name = self.user.username if self.user else 'Удаленный пользователь'
        return f"Комментарий от {user_name} к заявке №{self.request_id}"
