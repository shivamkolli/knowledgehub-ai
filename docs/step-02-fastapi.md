# Increment 2: your first FastAPI endpoint

This increment introduces Python packages, typed functions, Pydantic models,
configuration, dependency injection, and HTTP testing. No database is needed yet.

## Run it

Use Python 3.14 (verified with 3.14.4). From the repository root:

```sh
cd backend
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```

If `python3` is already Python 3.14, use it instead of `python3.14`. The environment
may already exist if you are continuing in the same checkout. Activation makes
`python` point to that environment, keeping these packages out of global Python.
The `.python-version` file records the version; it does not install Python itself.
Copy `.env.example` only on first setup; do not overwrite your later settings.

Open:

- http://127.0.0.1:8000/health — JSON response.
- http://127.0.0.1:8000/docs — interactive API documentation; expand GET /health
  and use “Try it out,” then “Execute.”
- http://127.0.0.1:8000/openapi.json — machine-readable API schema.

Expected health response:

```json
{"status": "ok", "service": "KnowledgeHub AI"}
```

Stop the development server with Ctrl+C. In the activated environment, run:

```sh
python -m pytest
```

There are three tests: HTTP status/body, environment-variable loading, and invalid
configuration rejection. No live server or external service is needed for tests.

## Follow one request through the code

1. `app/__init__.py` makes `app` an explicit Python package.
2. `app.main:app` tells Uvicorn to import `app/main.py` and serve its `app` object.
   Uvicorn handles HTTP; FastAPI matches routes and builds responses.
3. `create_app()` constructs a fresh FastAPI application. Tests can create their
   own instances without carrying state between them.
4. `@application.get("/health")` is a decorator: it registers the function below
   it as the handler for GET requests at that path.
5. `Annotated[Settings, Depends(get_settings)]` describes the parameter's type and
   tells FastAPI how to supply it. The route receives settings without reading
   environment variables itself. This is dependency injection.
6. `-> HealthResponse` is a return type hint. Python type hints alone do not
   enforce values at runtime; constructing the Pydantic model validates its data,
   and FastAPI uses `response_model` to validate/serialize the HTTP response.
7. `Literal["ok"]` restricts the status value to that exact string. Returning the
   model produces JSON; no manual JSON encoding is needed.

The route uses a normal `def` because it does no awaited I/O. We will introduce
`async def` and explain blocking I/O when a feature actually needs them.

## Settings

`Settings` extends Pydantic's `BaseSettings`. It reads `KNOWLEDGEHUB_`-prefixed
variables from the process environment and `backend/.env`. Environment variables
win over the file, which wins over defaults. The file path is anchored to the
backend directory, not whichever directory happens to launch the process.

`environment` accepts only development, test, or production. It is a validated
label at this stage; it does not automatically secure or configure deployment.
`app_name` must be nonempty. Unknown `.env` entries are ignored, so check names
carefully. The example contains no secrets; `.env` itself is ignored by Git.

`@lru_cache` reuses the settings object instead of rereading the file on every
request. Restart the server after changing configuration. For this small app,
settings load on the first health request; startup validation can be introduced
when dependencies are initialized.

Try changing `KNOWLEDGEHUB_APP_NAME` in `.env`, restarting the server, and calling
`/health` again. Predict the response before trying it.

## How the tests work

`TestClient` sends requests directly through the application without opening a
network port. The health test overrides `get_settings` with a controlled test
value, so local `.env` contents cannot change its expected response. The two
configuration tests disable `.env` loading and use pytest's `monkeypatch` to set
and automatically restore environment variables.

The health endpoint is a **liveness** check: it demonstrates that the API can
respond. It does not claim that PostgreSQL, Redis, S3, or a model provider works.
Dependency readiness will be a separate concern once those dependencies exist.

## Dependencies

`requirements.txt` lists runtime packages. `requirements-dev.txt` adds pytest and
`httpx2`, which the installed Starlette TestClient uses. Both use the exact version constraints in
`requirements.lock`, captured from the tested environment. This is a pip
constraints snapshot, not a hash-verified or universal cross-platform lock.
Re-resolve and test intentionally when upgrading; do not casually regenerate it
from an environment containing unrelated packages. `pyproject.toml` currently
contains pytest settings only; we are not packaging a distributable library yet.

The approach follows FastAPI's official guides for
[settings](https://fastapi.tiangolo.com/advanced/settings/) and
[testing](https://fastapi.tiangolo.com/tutorial/testing/).

## Review checkpoint

Explain in your own words what Uvicorn, FastAPI, Pydantic, and pytest each do.
Then trace `/health` through the decorator, injected settings, and response model.
After review, the suggested commit message is:

```text
feat: add FastAPI foundation with settings and health tests
```

Next increment: PostgreSQL and SQLAlchemy sessions/transactions. Stop here until
this increment is reviewed. No commits are made automatically.
