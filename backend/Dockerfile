
FROM python:3.11-slim


RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    gettext \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn


COPY . .


RUN if [ ! -f .env.dev ]; then echo "ERROR: .env.dev not found!" && exit 1; fi


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


EXPOSE 8000


CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]