# URL Shortener

FastAPI URL-shortening service with PostgreSQL persistence, Redis-backed
distributed ID allocation, seven-character Base62 codes, RedisBloom examples,
and permanent/temporary redirects.

## Architecture

- API routes validate HTTP input and translate responses.
- `UrlService` owns use cases and transaction boundaries.
- `UrlRepository` owns SQL queries but never commits transactions.
- Redis allocates ID blocks atomically; each instance serves IDs locally from
  its block, avoiding a Redis or database round trip per generated code.
- PostgreSQL's unique constraint is the final integrity boundary.
- Application resources are created and closed through FastAPI lifespan.

## Local setup

```powershell
Copy-Item .env.example .env
docker compose up -d
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

If PostgreSQL or Redis already runs locally, adjust `.env` before starting.
Redis Stack is required because the comparison endpoint uses `BF.*` commands.
Docker initializes a fresh PostgreSQL volume from `db/init.sql`. For an
existing external database, run that SQL file once before starting the API.

## Endpoints

- `POST /api/v1/urls/with-base-conversion` — production ID allocation path
- `POST /api/v1/urls/with-bloom-filter` — in-process Bloom-filter comparison
- `POST /api/v1/urls/with-redis-bloom-filter` — RedisBloom comparison
- `GET /api/v1/urls/{short_code}/permanent` — HTTP 301 redirect
- `GET /api/v1/urls/{short_code}/temporary` — HTTP 302 redirect
- `GET /api/v1/health/live` — process liveness
- `GET /api/v1/health/ready` — PostgreSQL and Redis readiness
- `/v1/docs` — OpenAPI UI

Create request:

```json
{
  "original_url": "https://example.com",
  "expires_at": null
}
```

## Verification

```powershell
python -m pytest
ruff check .
```

## Deployment notes

- Keep the Redis counter key persistent; deleting it can reissue old IDs.
- Do not use Uvicorn `--reload` in production.
- Put TLS termination, rate limiting, request IDs, and access logs at the
  gateway or ingress layer.
