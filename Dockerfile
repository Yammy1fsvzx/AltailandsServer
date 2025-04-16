# Этап 1: Установка зависимостей
FROM python:3.11-slim as builder

WORKDIR /app

# Устанавливаем системные зависимости, если нужны (например, для Pillow или баз данных)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Этап 2: Сборка финального образа
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем gunicorn
RUN pip install --no-cache-dir gunicorn

# Установка зависимостей из wheels
# COPY --from=builder /wheels /wheels
# RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем пользователя для запуска приложения (для безопасности)
RUN useradd --create-home --shell /bin/bash appuser
# Создаем директории и меняем владельца, если они еще не существуют
RUN mkdir -p /app/static_root /app/media && chown -R appuser:appuser /app/static_root /app/media
# Меняем владельца всего кода приложения (опционально, но может быть полезно)
RUN chown -R appuser:appuser /app

USER appuser

# Порт, который будет слушать gunicorn
EXPOSE 8000

# Запуск приложения через gunicorn
# Количество воркеров (workers) можно настроить
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "core.wsgi:application"] 