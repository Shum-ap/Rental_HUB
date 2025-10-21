
Rental Hub — Платформа аренды жилья

Rental Hub — это современное веб-приложение для аренды недвижимости.
Платформа позволяет пользователям искать жильё, бронировать, оплачивать и оставлять отзывы.

----------- Основные возможности

Поиск жилья по датам, цене и удобствам

Онлайн-бронирование и оплата

Добавление и управление объявлениями (для арендодателей)

Отзывы и рейтинги

Личный кабинет пользователя

Панель администратора

Уведомления по электронной почте

Документация API (Swagger / ReDoc)

JWT-аутентификация для безопасного доступа

------------ Технологический стек
Компонент	Технология
Язык	Python 3.13
Фреймворк	Django 5.2
API	Django REST Framework
База данных	SQLite3
Аутентификация	JWT (rest_framework_simplejwt)
Документация	Swagger / ReDoc (drf_spectacular)
Email	Mailtrap (SMTP Sandbox)
Верстка	HTML / CSS (адаптивная)
--------- Установка и запуск
1. Клонируйте репозиторий
git clone https://github.com/your_username/Rental_Hub.git
cd Rental_Hub/backend

2. Создайте виртуальное окружение
python -m venv .venv


Активируйте окружение:

# Windows
.venv\Scripts\activate

# Linux / Mac
source .venv/bin/activate

3. Установите зависимости
pip install -r requirements.txt

4. Примените миграции
python manage.py migrate

5. Создайте суперпользователя
python manage.py createsuperuser

6. Запустите сервер
python manage.py runserver


После запуска приложение будет доступно по адресу:
 http://127.0.0.1:8000/

-------Основные страницы
Страница	URL	Описание
Главная	http://127.0.0.1:8000/
	Поиск и популярные объекты
Админка	http://127.0.0.1:8000/admin/
	Панель администратора
Список объектов (HTML)	http://127.0.0.1:8000/html/
	Все доступные объекты
Детали объекта	http://127.0.0.1:8000/html/1/
	Просмотр и бронирование
Подтверждение брони	http://127.0.0.1:8000/booking/1/confirmation/
	Подтверждение бронирования
Оплата	http://127.0.0.1:8000/booking/1/pay/
	Форма оплаты
------- API Endpoints
Категория	Endpoint	Метод	Описание
JWT-аутентификация	/api/token/	POST	Получить JWT токен
JWT обновление	/api/token/refresh/	POST	Обновить токен
Список объектов	/api/v1/properties/	GET	Получить список объектов
Детали объекта	/api/v1/properties/{id}/	GET	Получить детали конкретного объекта
Бронирования	/api/v1/bookings/	POST/GET	Создание и просмотр бронирований
Оплата	/payments/	POST	Проведение оплаты
Пользователи	/api/v1/users/	GET/POST	Регистрация, список, профиль
---------- Примеры API-запросов

Получение JWT токена

curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'


Создание бронирования

curl -X POST http://127.0.0.1:8000/api/v1/bookings/ \
  -H "Authorization: Bearer <ваш_токен>" \
  -H "Content-Type: application/json" \
  -d '{
    "rental_property": 1,
    "start_date": "2025-10-01",
    "end_date": "2025-10-05"
  }'

--------- Документация API
Тип документации	Ссылка
Swagger UI	http://127.0.0.1:8000/api/schema/swagger-ui/

ReDoc	http://127.0.0.1:8000/api/schema/redoc/

JSON Schema	http://127.0.0.1:8000/api/schema/
👥 Роли пользователей
Роль	Возможности
Администратор	Полный доступ ко всем данным, управлению пользователями, объектами, отзывами и бронированиями
Арендодатель (Landlord)	Добавление и редактирование своих объектов, управление бронированиями, просмотр отзывов
Арендатор (Tenant)	Поиск и бронирование жилья, оставление отзывов
Модератор	Проверка и удаление отзывов, контроль качества контента
Гость	Просмотр объектов и отзывов без авторизации
----------- Структура проекта
backend/
├── apps/
│   ├── listings/
│   │   ├── models.py
│   │   ├── views_html.py
│   │   ├── urls_html.py
│   │   └── templates/listings/
│   ├── bookings/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── payments/
│   ├── users/
│   ├── reviews/
│   └── core/
│
├── templates/
│   └── listings/
│       ├── property_list.html
│       ├── property_detail.html
│       ├── booking_confirmation.html
│       ├── booking_success.html
│       ├── payment_form.html
│       └── payment_success.html
│
├── media/           
│   └── properties/
│
├── staticfiles/            
├── manage.py
├── requirements.txt
└── README.md

--------- Тестирование
python manage.py test

--------- Контакты

Автор проекта: ICH
Email: apet5685@gmail.com
