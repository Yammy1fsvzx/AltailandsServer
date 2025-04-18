# Этап 1: Установка зависимостей и сборка wheels
FROM python:3.11-slim as builder

WORKDIR /app

# Устанавливаем системные зависимости, если нужны (например, для Pillow или баз данных)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev

# Копируем файл зависимостей
COPY requirements.txt .
# Устанавливаем wheel, чтобы собрать wheels для зависимостей
RUN pip install --no-cache-dir wheel
# Собираем wheels
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Этап 2: Сборка финального образа
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем gunicorn (можно добавить в requirements.txt)
RUN pip install --no-cache-dir gunicorn

# Копируем собранные wheels из builder'а
COPY --from=builder /wheels /wheels
# Копируем requirements.txt
COPY requirements.txt .
# Устанавливаем зависимости из wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# Копируем остальной код приложения ПОСЛЕ установки зависимостей
COPY . .

# Создаем пользователя для запуска приложения (для безопасности)
RUN useradd --create-home --shell /bin/bash appuser

# Создаем директории для статики и медиа и меняем владельца
# Убедись, что STATIC_ROOT в твоих Django settings указывает на /app/static_root
RUN mkdir -p /app/static_root /app/media && chown -R appuser:appuser /app/static_root /app/media

# Собираем статику
# Убедись, что DEBUG=False в настройках для production, иначе collectstatic может не сработать как надо
RUN python manage.py collectstatic --noinput

# Меняем владельца всего кода приложения
RUN chown -R appuser:appuser /app

USER appuser

# Порт, который будет слушать gunicorn
EXPOSE 8000

# Запуск приложения через gunicorn
# Количество воркеров (workers) можно настроить (например, 2 * <кол-во CPU> + 1)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "core.wsgi:application"] 