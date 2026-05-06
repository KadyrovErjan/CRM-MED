<div align="center">

# 🏥 CRM-MED

### CRM-система для медицинских учреждений

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.x-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-REST_API-red?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

<br/>

> 🩺 Управление пациентами, врачами и приёмами — всё в одном месте

</div>

---

## 📌 О проекте

**CRM-MED** — это система управления взаимоотношениями с клиентами (CRM), адаптированная для медицинских учреждений. Платформа позволяет вести учёт пациентов, управлять расписанием врачей, записями на приём и историей лечения через удобный REST API и панель администратора.

---

## ✨ Возможности

- 👤 Управление профилями пациентов
- 🩺 База врачей с специализациями
- 📅 Запись пациентов на приём
- 📋 История визитов и лечения
- 🔐 JWT-аутентификация и разграничение прав доступа
- 🐳 Полная контейнеризация через Docker

---

## 🛠️ Технологический стек

| Слой             | Технология                        |
|------------------|-----------------------------------|
| Backend          | Python 3.11+, Django 4.x          |
| API              | Django REST Framework             |
| Аутентификация   | JWT (SimpleJWT)                   |
| Контейнеризация  | Docker, Docker Compose            |

---

## 🚀 Быстрый старт

### Предварительные требования

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Установка и запуск

```bash
# 1. Клонируй репозиторий
git clone https://github.com/KadyrovErjan/CRM-MED.git
cd CRM-MED

# 2. Создай файл переменных окружения
cp .env.example .env
# Отредактируй .env под свои настройки

# 3. Запусти контейнеры
docker compose up -d --build

# 4. Примени миграции
docker compose exec web python manage.py migrate

# 5. Создай суперпользователя
docker compose exec web python manage.py createsuperuser
```

🌐 Приложение: **http://localhost:8000**  
🔧 Панель администратора: **http://localhost:8000/admin**  
📖 Swagger UI: **http://localhost:8000/docs/**

---

## ⚙️ Переменные окружения

Создай файл `.env` в корне проекта:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=crm_med_db
POSTGRES_USER=crm_med_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

---

## 📡 API Endpoints

### 🔐 Аутентификация

| Метод  | URL                        | Описание                   |
|--------|----------------------------|----------------------------|
| `POST` | `/api/auth/register/`      | Регистрация                |
| `POST` | `/api/auth/login/`         | Вход — получить JWT токен  |
| `POST` | `/api/auth/token/refresh/` | Обновить токен             |

### 👤 Пациенты

| Метод    | URL                       | Описание                   |
|----------|---------------------------|----------------------------|
| `GET`    | `/api/patients/`          | Список пациентов           |
| `POST`   | `/api/patients/`          | Добавить пациента          |
| `GET`    | `/api/patients/{id}/`     | Карточка пациента          |
| `PUT`    | `/api/patients/{id}/`     | Обновить данные            |
| `DELETE` | `/api/patients/{id}/`     | Удалить пациента           |

### 🩺 Врачи

| Метод    | URL                       | Описание                   |
|----------|---------------------------|----------------------------|
| `GET`    | `/api/doctors/`           | Список врачей              |
| `POST`   | `/api/doctors/`           | Добавить врача             |
| `GET`    | `/api/doctors/{id}/`      | Профиль врача              |

### 📅 Приёмы

| Метод    | URL                         | Описание                   |
|----------|-----------------------------|----------------------------|
| `GET`    | `/api/appointments/`        | Список записей             |
| `POST`   | `/api/appointments/`        | Создать запись             |
| `GET`    | `/api/appointments/{id}/`   | Детали приёма              |
| `PATCH`  | `/api/appointments/{id}/`   | Обновить статус            |
| `DELETE` | `/api/appointments/{id}/`   | Отменить запись            |

---

## 📁 Структура проекта

```
CRM-MED/
├── mysite/
│   ├── manage.py
│   ├── mysite/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── apps/
│       ├── patients/        # Пациенты
│       ├── doctors/         # Врачи и специализации
│       ├── appointments/    # Записи на приём
│       └── users/           # Аутентификация
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## 🧪 Запуск тестов

```bash
docker compose exec web python manage.py test
```

---

## 👤 Автор

**Erjan Kadyrov**

[![GitHub](https://img.shields.io/badge/GitHub-KadyrovErjan-181717?style=for-the-badge&logo=github)](https://github.com/KadyrovErjan)

---

<div align="center">

**🏥 Забота о пациентах начинается с правильной системы управления**

</div>
