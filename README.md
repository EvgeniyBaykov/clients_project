# FastAPI Приложение с Docker, PostgreSQL и Redis

Это приложение на **FastAPI** использует **PostgreSQL** для хранения данных, **Redis** для кэширования,  
**SQLalchemy** в качестве ORM, **alembic** для миграций, **JWT** для авторизации. 

Контейнеризация осуществляется с помощью **Docker** и **Docker Compose**. 

## Стек технологий

- **Python 3.12** и **FastAPI**
- **PostgreSQL** — основная база данных
- **Redis** — кэш
- **Docker и Docker Compose** для контейнеризации

## Установка

#### 1. Клонирование репозитория

```bash
git clone https://github.com/EvgeniyBaykov/clients_project.git
cd clients_project/
```

Переименуйте файл .env.template в .env и заполните переменные своими данными
#### 2. Запуск контейнеров
Для запуска всех сервисов используйте команду:

```bash
docker-compose up --build
```
Это создаст и запустит три контейнера:

* web_container — приложение на FastAPI
* postgres_container — база данных PostgreSQL
* redis_container — кэш Redis

Приложение будет доступно по адресу: http://localhost:8000

### Основные Endpoints
* POST /api/clients/create - регистрация нового пользователя.
* POST /api/clients/login - авторизация пользователя.
* POST /api/clients/logout - выход пользователя.
* POST /api/clients/{target_client_id}/match - оценка другого пользователя.
* GET /api/list - получение списка участников с фильтрацией.
* POST /api/token/refresh - обновление access-токена.

### Миграции
Применение миграций выполняется автоматически при запуске контейнера. 

Чтобы запустить миграции вручную, выполните:


```bash
docker-compose exec web alembic upgrade head
```
 
>by [Evgeniy Baykov](https://github.com/EvgeniyBaykov)