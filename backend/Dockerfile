# Используем официальный Python-образ
FROM python:3.11-slim

# Устанавливаем системные зависимости (включая gettext для локализации)
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Копируем проект
COPY . .

# Настройки окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Открываем порт 8000
EXPOSE 8000

# Основная команда запуска
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
