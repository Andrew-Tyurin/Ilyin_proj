### `python3.13`

#### 1) Для генерации SECRET_KEY можно использовать команду:
- ```bash
  openssl rand -base64 48 | tr '+/' '-_' | tr -d '='
  ```

#### 2) Субд postgres рабочая и тестовая + асинхронный драйвер(asyncpg), можно попробовать и другую субд, но тогда: без изменения engine врят-ли получится и обязательно субд должна быть с поддержкой асинхронных запросов.

#### 3) Обязательно создаем ручками в корне проекта `/.env`:

- ```
  DB_URL_ASYNCPG=postgresql+asyncpg://user:1234@localhost:5432/name_db
  SECRET_KEY=create_seckret
  APP_ENV=prod
  ```

#### 4) И для pytest в директории `/tests/.test.env` :

- ```
  DB_URL_ASYNCPG=postgresql+asyncpg://user:1234@localhost:5432/test_name_db
  SECRET_KEY=test_create_seckret
  APP_ENV=test
  ```

#### 5) APP_ENV как указаны в примерах. Создаем и активируем окружение, ставим зависимости.

#### 6) Создаём таблицы из корня проекта: python -m app.db_table_management

#### 7) запускаем из корня проекта, bash: `python main.py` или `uvicorn app.main:app --reload`, а для тестов: pytest -vs

#### 8) Документация по http://localhost:8000/docs а фронт по http://localhost:8000/ui/index.html но проверить main.py и раскомитить строку с подключением.
