from django.db import models
from django.conf import settings # Если будете связывать с User

class Contact(models.Model):
    phone = models.CharField(max_length=20, blank=True, verbose_name='Контактный телефон', help_text='Номер телефона в формате +7 XXX XXX XX XX')
    whatsapp = models.CharField(max_length=20, blank=True, verbose_name='WhatsApp', help_text='Номер WhatsApp, связанный с компанией')
    email = models.EmailField(blank=True, verbose_name='Email', help_text='Контактный email адрес')
    office_address = models.CharField(max_length=255, blank=True, verbose_name='Адрес офиса', help_text='Физический адрес офиса')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Контакт Компании'
        verbose_name_plural = 'Контакты Компании'

    def __str__(self):
        return f'Контакты компании (ID: {self.id})'

class WorkingHours(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    )
    contact = models.ForeignKey(Contact, related_name='working_hours', on_delete=models.CASCADE, verbose_name='Контакт Компании')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, verbose_name='День недели')
    start_time = models.TimeField(blank=True, null=True, verbose_name='Время начала работы', help_text='Время начала рабочего дня (ЧЧ:ММ)')
    end_time = models.TimeField(blank=True, null=True, verbose_name='Время окончания работы', help_text='Время окончания рабочего дня (ЧЧ:ММ)')
    is_active = models.BooleanField(default=True, verbose_name='Рабочий день', help_text='Отметьте, если это рабочий день. Если не отмечено, считается выходным.')

    class Meta:
        verbose_name = 'Режим работы'
        verbose_name_plural = 'Режим работы'
        unique_together = ('contact', 'day_of_week')

    def __str__(self):
        return f'{self.get_day_of_week_display()}: {self.start_time}-{self.end_time} (активен: {self.is_active})'


# --- Новая модель для запросов с контактной формы --- #

class ContactSubmission(models.Model):
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('in_progress', 'В обработке'),
        ('closed', 'Закрыт'),
    )
    name = models.CharField(max_length=100, verbose_name='Имя отправителя')
    email = models.EmailField(verbose_name='Email отправителя')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='Телефон отправителя')
    subject = models.CharField(max_length=200, blank=True, verbose_name='Тема сообщения')
    message = models.TextField(verbose_name='Сообщение')
    # Опциональная связь с зарегистрированным пользователем
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Не удалять запрос, если пользователь удален
        null=True,
        blank=True,
        related_name='contact_submissions',
        verbose_name='Пользователь (если известен)'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус обработки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата получения')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления статуса')

    class Meta:
        verbose_name = 'Запрос с контактной формы'
        verbose_name_plural = 'Запросы с контактной формы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Запрос от {self.name} ({self.email}) - {self.created_at.strftime("%d.%m.%Y %H:%M")}'
