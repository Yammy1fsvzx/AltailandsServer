from django.db import models

class Contact(models.Model):
    phone = models.CharField(max_length=20, blank=True, verbose_name='Контактный телефон', help_text='Номер телефона в формате +7 XXX XXX XX XX')
    whatsapp = models.CharField(max_length=20, blank=True, verbose_name='WhatsApp', help_text='Номер WhatsApp, связанный с компанией')
    email = models.EmailField(blank=True, verbose_name='Email', help_text='Контактный email адрес')
    office_address = models.CharField(max_length=255, blank=True, verbose_name='Адрес офиса', help_text='Физический адрес офиса')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f'Контакты (тел: {self.phone})'

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
    contact = models.ForeignKey(Contact, related_name='working_hours', on_delete=models.CASCADE, verbose_name='Контакт')
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
