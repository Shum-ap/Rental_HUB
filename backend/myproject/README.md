#  Rental Hub — Property Rental Platform / Платформа аренды жилья

---

## 🇬🇧 English Version

###  Overview
**Rental Hub** is a modern web platform for property rentals, inspired by Airbnb.  
It allows users to search, book, pay for rentals, and leave reviews — all in one intuitive Django-based system.

###  Key Features
- Property search and filtering  
- Booking management  
- Secure online payments  
- JWT authentication (login & refresh)  
- User registration and profiles  
- Reviews and ratings  
- Django Admin panel  
- REST API + HTML interface  
- API documentation (Swagger / ReDoc)  
- Multi-language support  
- Email notifications  

###  Technologies
- Python 3.13  
- Django 5.2  
- Django REST Framework  
- SQLite3 (default DB)  
- JWT via `rest_framework_simplejwt`  
- Swagger / ReDoc via `drf_spectacular`  
- HTML / CSS frontend  

###  Installation
```bash
git clone https://github.com/Shum-ap/Rental_HUB.git
cd Rental_HUB
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
 Available Pages
Page	URL	Description
Home	http://127.0.0.1:8000/	Main property list
Property Details	/properties/<id>/	Individual listing page
Add Property	/properties/add/	Add a new rental listing
Booking Success	/booking/<id>/success/	Successful booking
Booking Confirmation	/booking/<id>/confirmation/	Confirmation page
Booking Cancelled	/booking/<id>/cancelled/	Cancelled booking
Payment	/booking/<id>/pay/	Payment page
Payment Success	/booking/<id>/paid/	Payment success page
Admin Panel	http://127.0.0.1:8000/admin/	Django Admin

 REST API Endpoints
Resource	Method	URL
JWT Token	POST	/api/token/
Refresh Token	POST	/api/token/refresh/
Users	GET / POST	/api/v1/users/
Properties	GET / POST	/api/v1/properties/
Bookings	GET / POST	/api/v1/bookings/
Payments	GET / POST	/api/v1/payments/
Reviews	GET / POST	/api/v1/reviews/
Search History	GET	/api/v1/search-history/

 API Documentation
Type	URL
Swagger UI	http://127.0.0.1:8000/api/schema/swagger-ui/
ReDoc	http://127.0.0.1:8000/api/schema/redoc/

 Example API Requests
Obtain a Token
bash
Копировать код
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
Create a Booking
bash
Копировать код
curl -X POST http://127.0.0.1:8000/api/v1/bookings/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
        "rental_property": 1,
        "start_date": "2025-10-25",
        "end_date": "2025-10-28"
      }'
 Project Structure
bash
Копировать код
Rental_HUB/
├── backend/
│   ├── apps/
│   │   ├── listings/
│   │   ├── bookings/
│   │   ├── reviews/
│   │   ├── users/
│   │   ├── payments/
│   │   └── log/
│   ├── myproject/
│   │   ├── urls.py
│   │   ├── routers.py
│   │   └── settings.py
│   ├── templates/
│   ├── media/
│   ├── staticfiles/
│   └── manage.py
├── requirements.txt
└── README.md
 Contributing
bash
Копировать код
git checkout -b feature/new-feature
git commit -m "Add new feature"
git push origin feature/new-feature
 Contact
Author: Shum-ap
Email: apet5685@gmail.com

🇷🇺 Русская версия
 Обзор
Rental Hub — это современная платформа для аренды жилья, созданная на Django.
Позволяет пользователям искать жильё, бронировать, оплачивать и оставлять отзывы.

 Основные возможности
Поиск и фильтрация жилья

Создание и управление бронированиями

Онлайн-оплата

JWT-аутентификация

Личный кабинет пользователя

Добавление отзывов

Панель администратора Django

REST API и HTML-интерфейс

Документация Swagger / ReDoc

Многоязычная поддержка

Email-уведомления

 Установка
bash
Копировать код
git clone https://github.com/Shum-ap/Rental_HUB.git
cd Rental_HUB
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
 Основные страницы
Страница	URL	Описание
Главная	http://127.0.0.1:8000/	Список объектов
Объявление	/properties/<id>/	Страница жилья
Добавить объект	/properties/add/	Добавление жилья
Бронирование — успех	/booking/<id>/success/	Успешное бронирование
Подтверждение	/booking/<id>/confirmation/	Подтверждение брони
Отмена	/booking/<id>/cancelled/	Отмена бронирования
Оплата	/booking/<id>/pay/	Страница оплаты
Оплата — успех	/booking/<id>/paid/	Успешная оплата
Админка	http://127.0.0.1:8000/admin/	Django Admin

 REST API
Ресурс	Метод	URL
JWT токен	POST	/api/token/
Обновить токен	POST	/api/token/refresh/
Пользователи	GET / POST	/api/v1/users/
Объявления	GET / POST	/api/v1/properties/
Бронирования	GET / POST	/api/v1/bookings/
Платежи	GET / POST	/api/v1/payments/
Отзывы	GET / POST	/api/v1/reviews/
История поиска	GET	/api/v1/search-history/

 Документация API
Тип	URL
Swagger UI	http://127.0.0.1:8000/api/schema/swagger-ui/
ReDoc	http://127.0.0.1:8000/api/schema/redoc/

 Контакты
Автор: Shum-ap
Email: apet5685@gmail.com





