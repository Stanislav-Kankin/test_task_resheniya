# Deribit Prices API

Сервис собирает **index price** с Deribit для тикеров `btc_usd` и `eth_usd` (каждую минуту) и сохраняет данные в PostgreSQL.
Далее предоставляет внешнее API на FastAPI для чтения сохранённых цен.

## Стек
- Python 3.12+
- FastAPI
- PostgreSQL
- SQLAlchemy (async) + asyncpg
- Celery + Celery Beat
- Redis (broker/result backend)
- aiohttp (HTTP client)

## Переменные окружения
Скопируйте `.env.example` в `.env` и при необходимости измените значения.

## API
Все методы **GET** и требуют обязательный query-параметр `ticker` (`btc_usd` или `eth_usd`).

- Получить все сохранённые данные по валюте  
  `GET /prices?ticker=btc_usd&limit=1000&offset=0`

- Получить последнюю цену валюты  
  `GET /prices/latest?ticker=btc_usd`

- Получить цену валюты с фильтром по дате (UNIX timestamp)  
  `GET /prices/range?ticker=btc_usd&from_ts=1700000000&to_ts=1700003600`

Дополнительно:  
`GET /health`

Swagger: `/docs`

## Быстрый запуск (Docker: db + redis)
Поднять PostgreSQL и Redis:
```bash
docker compose -f docker-compose.dev.yml up -d
```

Установить зависимости и запустить API:
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt

python -m uvicorn app.main:app --host 0.0.0.0 --port 8011
```

Запустить Celery (в отдельных терминалах):
```bash
source env/bin/activate
python -m celery -A app.tasks.celery_app:celery_app worker -l INFO
```

```bash
source env/bin/activate
python -m celery -A app.tasks.celery_app:celery_app beat -l INFO
```

Проверка записей в БД:
```bash
psql "postgresql://postgres:postgres@localhost:5432/deribit" -c "SELECT ticker, price, ts_unix FROM prices ORDER BY ts_unix DESC LIMIT 10;"
```

## Design decisions
1) **Celery + Beat для периодического сбора**  
   Используется Celery Beat с расписанием “каждую минуту” для двух тикеров. Это простой и расширяемый способ планирования задач.

2) **Redis как брокер и backend**  
   Redis легко поднять локально и в Docker, для тестового задания достаточно и типично для Celery.

3) **aiohttp для клиента Deribit**  
   aiohttp даёт неблокирующие запросы. Клиент вынесен в отдельный модуль, чтобы отделить работу с внешним API от бизнес-логики.

4) **UNIX timestamp в БД**  
   В задании требуется хранить время в UNIX timestamp, поэтому фильтрация диапазоном делается через `from_ts/to_ts`.

5) **Разделение по слоям**
- `clients/` — запросы к Deribit
- `repositories/` — доступ к БД
- `services/` — бизнес-логика (fetch + store)
- `api/` — HTTP слой (FastAPI endpoints)

6) **Создание таблиц при старте**
Для упрощения разворачивания в рамках тестового задания таблицы создаются на старте приложения через SQLAlchemy `create_all`.
В production предпочтительнее миграции (например, Alembic).
