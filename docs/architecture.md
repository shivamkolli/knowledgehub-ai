# Architecture

Status: proposed target architecture, not a deployed or runnable system.

## Component responsibilities

```text
React browser client
    | REST requests and streamed answer responses (SSE framing)
    v
FastAPI ----------------------> PostgreSQL + pgvector
    |                           users, organizations, documents,
    |                           jobs, chunks, conversations, vectors
    |
    +----> private S3 storage: original documents
    |
    +----> Redis broker ----> Celery worker
    |                           | reads S3; updates PostgreSQL
    |                           +----> embedding provider
    +----> language-model provider for grounded answers
```

The frontend owns presentation, navigation, and cached server state. FastAPI owns
HTTP validation, authentication, authorization, and orchestration. Pydantic schemas
describe inputs/outputs; SQLAlchemy models map stored records. They serve different
purposes and should not be treated as interchangeable.

PostgreSQL is the durable source of truth. Alembic manages schema changes.
pgvector stores embeddings alongside relational ownership metadata. Celery runs
document processing outside request handlers. Redis carries queued tasks. S3
stores file bytes; PostgreSQL stores object keys and processing metadata.

## Backend organization as it grows

Start with a small application in `backend/app`. Introduce routers, schemas,
models, services, and worker tasks as real features need them. Routes translate
HTTP requests into application operations; services coordinate business rules;
database sessions define transaction boundaries. Do not generate all these layers
in increment 1.

Each request or worker operation owns its database session. Never share a request
session with a queued job. Choose sync/async database access in the SQLAlchemy
increment, and keep blocking work out of the API event loop. Celery is for durable
background work, not the delivery channel for interactive answer tokens.

## Upload and processing flow

1. Verify membership and validate the upload. Initially send the file through the
   API; direct browser-to-S3 uploads can be a later optimization.
2. Create document metadata and write the original file to a generated private
   object key. Never use a user-supplied filename as an authorization boundary.
3. Persist a queued processing job, commit the transaction, then dispatch its ID.
4. The worker loads the job and document, verifies their organization relationship
   and current state, and claims an attempt.
5. Extract text, split it into ordered chunks, and create embeddings. Store source
   locations for citations. Publish the successful chunk set and mark the document
   ready only when the whole processing attempt succeeds.
6. Record a safe error on failure. Retried or duplicated deliveries must not
   publish duplicate chunks or overwrite a newer successful attempt.

S3, PostgreSQL, and Redis do not share one transaction. The queue implementation
must recover persisted jobs that were never dispatched, and upload/deletion logic
must clean up orphan objects. A persisted job with a reconciliation dispatcher is
the proposed starting approach; exact mechanics belong to the queue increment.

## Question and answer flow

1. Verify membership and conversation ownership; store the user's question.
2. Embed the question with a model compatible with stored document embeddings.
3. Retrieve matching chunks with the organization and document-state filters
   applied inside the database query, before ranking/limiting results.
4. Build a bounded prompt that treats source passages as data. Ask the model to
   answer from those passages and acknowledge insufficient evidence.
5. Stream answer events to the client and persist completion/failure state.
6. Attach citations only to retrieved passages and validate source identifiers.

A planned POST answer endpoint will use a streaming fetch response with SSE
framing; the native browser `EventSource` API does not send a POST body. Define
event names, authentication, cancellation, and retry behavior in increment 13.
An interrupted stream must not appear as a completed answer. Reconnecting must
not silently create a second model request or duplicate a saved answer.

## Tenant and access boundaries

- A user identity alone does not grant access to an organization.
- Every tenant-owned query includes an authorized organization ID. A client-sent
  organization ID selects context but is never proof of membership.
- Workers use persisted ownership relationships, not arbitrary object keys or
  tenant IDs supplied in queue messages.
- Citation endpoints and file downloads recheck authorization. Previously created
  conversations do not bypass revoked membership.
- Database constraints prevent cross-organization relationships. Application
  authorization remains required; PostgreSQL row-level security can be evaluated
  later as an additional defense.
- Deletion and processing coordinate so a late worker cannot republish a deleted
  document. Existing answer text may outlive its sources, as described in requirements.

## Local development and eventual AWS deployment

The intended local setup runs the frontend and API with reload, plus containerized
PostgreSQL with pgvector, Redis, and S3-compatible storage. Add a worker when jobs
arrive. AWS will use private S3 and a container deployment with managed data
services where suitable; service selection, network boundaries, IAM, backup,
secrets, budget, and teardown are intentionally deferred to the deployment step.

Observability will connect request IDs, job IDs, and provider calls without logging
document contents. Health checks distinguish process liveness from dependency
readiness. Integration tests will cover tenant isolation and partial failures across
storage, queue delivery, worker retries, and model streaming.
