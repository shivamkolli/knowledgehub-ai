# Development decisions and setup

Keep implementation decisions and current setup instructions in this file as the
project grows. Do not create a separate walkthrough for each increment.

## Current decisions

| Area | Decision and reason |
| --- | --- |
| Python | Python 3.14 with a backend `.venv` isolates project dependencies. |
| Dependencies | pip requirements separate runtime and test dependencies; `requirements.lock` records tested version constraints. It is not a hash-verified cross-platform lock. |
| API | FastAPI handles routing; Uvicorn serves HTTP; Pydantic validates settings and response models. |
| Configuration | `KNOWLEDGEHUB_` environment variables override `backend/.env`, then defaults. Settings load at startup and are cached; restart after changes. |
| Application factory | `create_app(settings)` gives tests their own application and explicit configuration. |
| Local database | Docker Compose runs PostgreSQL 17 on localhost port 55432 to avoid the usual PostgreSQL port. A named volume preserves data. |
| Database access | Synchronous SQLAlchemy with psycopg keeps the initial transaction flow straightforward. Synchronous routes run in FastAPI's thread pool. |
| Connection lifecycle | One engine per application manages pooled connections; each request gets its own Session, closed after the request. |
| Transactions | Write operations explicitly commit. Closing a session rolls back uncommitted work; the session dependency never auto-commits. |
| Health checks | `/health` reports process liveness. `/ready` executes `SELECT 1` and returns a generic 503 on database failure. It does not check schema readiness yet. |
| Schema | Permanent application tables and Alembic arrive next; pgvector arrives with embeddings. |

`get_session()` uses `yield` to supply a session and then run cleanup. Do not share
sessions across concurrent requests or pass them to queued workers. The engine
opens connections lazily and is disposed at application shutdown.

`Depends(get_settings)` supplies configuration to a route. `HealthResponse` defines
its response shape. Python type hints describe types; Pydantic performs runtime
validation. The asynchronous lifespan hook does not make database queries async.

The database URL uses `SecretStr` to redact normal representations. Connection,
pool-wait, and statement timeouts bound common failure waits, but do not form one
end-to-end request deadline. Internal error logging will be added with observability.

## Local setup

From the repository root, with Python 3.14 and Docker Desktop available:

```sh
docker compose up -d --wait postgres
cd backend
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

Use `python3` instead of `python3.14` if it already points to Python 3.14. Skip
creating the virtual environment if it exists. `.python-version` records the
version but does not install Python.

Defaults work without `.env`. For custom settings, copy `.env.example` to `.env`
once; if `.env` already exists, add needed entries without overwriting it. Unknown
entries are ignored. The environment label does not automatically configure a
secure production deployment. Local database credentials are demo values only.

Open http://127.0.0.1:8000/docs to try `/health` and `/ready`. The API schema is at
http://127.0.0.1:8000/openapi.json. Stop Uvicorn with Ctrl+C.

## Database operations

Run from the repository root:

```sh
docker compose ps
docker compose stop postgres
docker compose start postgres
```

While PostgreSQL is stopped, `/health` still returns 200 and `/ready` returns 503.
`docker compose down` removes containers/network but preserves the named volume;
adding `--volumes` deletes database data.

Host port 55432 maps to container port 5432. If occupied, set
`KNOWLEDGEHUB_POSTGRES_PORT` when running Compose and update the backend database
URL to match. Initialization credentials apply only to a new volume; editing them
does not change existing database passwords. The PostgreSQL 17 image tag may pick
up minor releases; immutable deployment images are a later deployment decision.

## Verification

From `backend/` with the virtual environment active:

```sh
python -m pytest
KNOWLEDGEHUB_TEST_DATABASE_URL='postgresql+psycopg://knowledgehub:knowledgehub_local@127.0.0.1:55432/knowledgehub' python -m pytest
python -m pip check
```

The ordinary suite skips the live database test. Setting the test URL enables it:
it checks readiness and commit/rollback using a connection-local temporary table.
No permanent application tables are created. TestClient exercises HTTP behavior
without a listening server; unit tests cover settings and safe failure responses.
The tested suite currently has five unit tests and one integration test.

Re-resolve dependency versions intentionally when upgrading, using an isolated
environment and rerunning tests. Do not regenerate the constraints snapshot from
an environment containing unrelated packages.

## References

- [FastAPI settings](https://fastapi.tiangolo.com/advanced/settings/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy sessions](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [PostgreSQL Docker image](https://hub.docker.com/_/postgres)
