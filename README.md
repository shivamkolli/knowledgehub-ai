# KnowledgeHub AI

A learning-oriented monorepo for a multi-tenant AI document intelligence platform.
Users will create organizations, upload documents, and ask questions with answers
grounded in those documents and linked to source passages.

## Current state

**Increment 2: runnable FastAPI foundation.** The backend has a health endpoint,
validated environment settings, interactive API documentation, and pytest tests.
The frontend, database, Docker services, and cloud resources are still planned.

See [the increment 2 walkthrough](docs/step-02-fastapi.md) for setup, commands,
and a guided explanation of the code.

We will build one reviewable increment at a time. Each increment explains the
Python/FastAPI concepts it introduces, includes appropriate verification, and
stops for review. You decide when to commit. Nothing is committed automatically.

## Planned stack

| Layer | Technologies and responsibilities |
| --- | --- |
| Frontend | React + TypeScript, Vite, Tailwind CSS, React Router, TanStack Query |
| API | Python, FastAPI, Pydantic for request/response validation |
| Persistence | SQLAlchemy, PostgreSQL + pgvector, Alembic migrations |
| Background work | Celery workers with Redis as broker |
| Documents | Private S3 object storage; local S3-compatible storage during development |
| Testing | pytest for backend behavior; frontend checks introduced with the frontend |
| Operations | Docker for reproducible services; AWS deployment in a later increment |
| AI | Embedding and language-model integrations behind replaceable interfaces |

## Repository map

```text
knowledgehub-ai/
├── README.md
├── .gitignore
├── docs/
│   ├── requirements.md     # Scope, user journeys, acceptance criteria
│   ├── architecture.md     # Components, trust boundaries, request flows
│   ├── data-model.md       # Proposed entities and integrity rules
│   └── step-02-fastapi.md  # Run and understand the first endpoint
├── frontend/
│   └── src/               # React source, added in a later increment
└── backend/
    ├── app/               # Application entry point and settings
    ├── tests/             # Health and configuration tests
    ├── .env.example       # Safe example configuration
    ├── .python-version    # Python 3.14
    ├── pyproject.toml     # pytest configuration
    ├── requirements.txt   # Runtime dependencies
    ├── requirements-dev.txt # Test dependencies
    └── requirements.lock  # Resolved version constraints
```

The empty frontend source directory contains a `.gitkeep` placeholder so Git can
track it. Infrastructure files will arrive with the services they configure.

## Learning roadmap

These are proposed commit boundaries, not existing commits. Scope can be adjusted
at each review, but implementation never skips ahead without your agreement.

| Increment | Deliverable | Main learning topic |
| --- | --- | --- |
| 1 | Structure and these design documents | Separating requirements, architecture, and data modeling |
| 2 | FastAPI foundation, configuration, health route, first test | Python modules, type hints, Pydantic, dependency injection |
| 3 | Local PostgreSQL and SQLAlchemy integration | Sessions, transactions, ORM models |
| 4 | Alembic setup and first schema migration | Versioning and evolving a database |
| 5 | Users and authentication | Password hashing, identity, authenticated requests |
| 6 | React foundation and API integration | Components, routing, typed requests, server-state caching |
| 7 | Organizations, memberships, tenant isolation | Authorization and organization-scoped queries |
| 8 | Document metadata and S3 uploads | Object storage, upload validation, ownership |
| 9 | Redis and Celery workers | Queues, retries, idempotency, job state |
| 10 | Text extraction and chunking | Processing pipelines and error handling |
| 11 | Embeddings and pgvector retrieval | Vector dimensions, similarity, retrieval quality |
| 12 | RAG questions, answers, and citations | Grounding, provider interfaces, context selection |
| 13 | SSE answer streaming | Incremental delivery, cancellation, stream failures |
| 14 | Broader integration and isolation tests | End-to-end failure cases and regression coverage |
| 15 | Observability | Structured logs, correlation IDs, service health |
| 16 | AWS deployment | Containers, secrets, IAM, networking, deployment and teardown |

Tests start with executable behavior; increment 14 expands coverage rather than
postponing all testing until the end. Docker support will grow with local services.
Cloud deployment will be an explicit later step with costs and teardown explained.

## Read next

1. [Requirements](docs/requirements.md): what users should be able to do.
2. [Architecture](docs/architecture.md): how components cooperate.
3. [Data model](docs/data-model.md): what we store and how records relate.

Review and run increment 2 before moving to PostgreSQL/SQLAlchemy. No credentials
or external services are needed for the current backend.
