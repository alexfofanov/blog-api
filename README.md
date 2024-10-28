# Тестовое задание
## Создайте простой API блога.

API должен иметь следующие конечные точки:

1. GET /posts: Возвращает список всех сообщений блога.
2. GET /posts/{id}: Возвращает одну запись блога по идентификатору.
3. POST /posts: Создать новую запись в блоге.
4. PUT /posts/{id}: Обновить существующую запись в блоге.
5. DELETE /posts/{id}: Удалить запись в блоге.

Каждая запись в блоге должна иметь следующие поля:
1. id (integer, primary key)
2. title (string)
3. content (string)
4. created_at (datetime)
5. updated_at (datetime)

# Решение
В рамках выполнения задания реализованы:
- API сервиса
- JWT авторизация
- тесты
- Docker и Docker Compose файлы

Для решения задачи выбран популярный фреймворк [FastAPI](https://fastapi.tiangolo.com/).
Для аутентификации и авторизации пользователя используется технология [JWT токенов](https://ru.wikipedia.org/wiki/JSON_Web_Token).
Миграции БД реализованы через [alembic](https://alembic.sqlalchemy.org/en/latest/index.html).
Для тестов использован [pytest](https://docs.pytest.org/en/stable/)

Сервис позволяет:

Любому пользователю: 
- создавать учётную запись пользователя
- авторизовать пользователя
- получать список всех сообщений блога
- получать одну запись блога по идентификатору
- искать записи в блоге по названию или содержанию
- возвращать среднее количество сообщений в блоге за месяц для заданного пользователя

Пример запроса без авторизации:
```
curl --request GET \
  --url 'http://127.0.0.1:8000/api/v1/posts?offset=1&limit=5'
```

Авторизованному пользователю:
- создать новую запись в блоге
- обновить существующую запись в блоге
- удалить существующую запись в блоге

Пример запроса с авторизацие:
```
curl --request POST \
  --url http://127.0.0.1:8000/api/v1/posts/ \
  --header "Authorization: Bearer YOUR_JWT_TOKEN" \
  --header "Content-Type: application/json" \
  --data '{
    "title": "Заголовок поста",
    "content": "Содержимое поста"
  }'
```

Описание API доступно по ссылке: http://127.0.0.1:8000/api/openapi

## Установка и запуск
Проверяем установлены ли docker и docker-compose:
```
docker -v
docker-compose -v
```
В случае отсутствия установите согласно документации по установке [docker](https://docs.docker.com/engine/install/) и [docker-compose](https://docs.docker.com/compose/install/) на официальном сайте.

Клонируем репозиторий:
```
git clone git@github.com:alexfofanov/blog-api.git
```
Переходим в папку проекта:
```
cd blog-api
```
Создаём и редактируем файл .env по обарзцу .env.example:
```
cp .env.example .env
```
Запуск сервиса:
```
make start
```
Запуск тестов
```
make test
```
Остановка сервиса: 
```
make stop
```
## Технологии
- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- Pytest
- PostgreSQL
- Docker
- Docker Compose