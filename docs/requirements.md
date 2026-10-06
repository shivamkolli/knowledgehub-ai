# Requirements

Status: proposed design for incremental implementation; no features implemented.

## Purpose

Practice building a Python/FastAPI application with a separate React frontend,
real persistence, asynchronous work, and a grounded AI workflow. Keep each step
small enough to understand, run, and review before the next one.

## Core journey

1. Register and sign in.
2. Create an organization and become its owner.
3. Select an organization where you are a member.
4. Upload a document and see its processing state.
5. Wait while a worker extracts text, creates chunks, and embeds them.
6. Ask a question about ready documents in the selected organization.
7. Read a streamed answer and inspect its source passages.
8. Return to the conversation later or delete a document you own through the organization.

## Initial scope and acceptance criteria

| Area | Planned behavior and acceptance criteria |
| --- | --- |
| Identity | Unique email accounts, hashed passwords, login/logout, and protected endpoints; never return password hashes. Authentication mechanism will be chosen in increment 5. |
| Organizations | Owner and member roles. An owner can add an existing registered user by email and remove members; invitations and ownership transfer are deferred. The last owner cannot be removed. |
| Authorization | Both roles can upload, ask, and read within their organization. Only owners manage membership or delete documents. Every organization-scoped operation verifies current membership. |
| Uploads | Start with UTF-8 text and text-based PDFs. Enforce a documented size limit and validate actual content in addition to file extension. Unsupported, encrypted, empty, or image-only inputs produce actionable errors; OCR is deferred. |
| Processing | Expose queued, processing, ready, failed, deleting, and deleted states. Retry transient failures safely. A duplicate job must not create duplicate active chunks. |
| Retrieval | Search only ready, active documents in the selected organization. Keep source text and location metadata for citations. |
| Answers | Use retrieved passages as evidence, display citations, and state when evidence is insufficient. Do not present grounding as a guarantee of factual correctness. |
| Streaming | Render answer content incrementally; distinguish completion from interruption or failure. Preserve the final successful answer and citation references. |
| Conversations | Store questions and answers under an organization and creator. Initially only the creator can access a conversation; document access still depends on current organization membership. |
| Deletion | Immediately exclude a deleting document from retrieval; asynchronously remove objects, extracted text, chunks, and vectors. Historical answers can remain but unavailable citations are labeled. |

## Boundaries and quality goals

- Tenant isolation must hold for metadata, file access, job execution, retrieval,
  conversation history, citations, and streaming, including guessed record IDs.
- S3 buckets stay private. Any download link is issued only after authorization
  and expires. Redis is not the durable source of business state.
- Secrets stay outside source control. Logs omit passwords, tokens, raw document
  contents, and full prompts by default.
- Treat uploaded content as untrusted data, including instructions embedded in
  documents. The initial RAG system has no tools or authority to perform actions.
- Validate inputs with Pydantic and enforce persistent invariants in PostgreSQL.
- Introduce tests with each feature, especially access control and retry behavior.
- Keep local development reproducible; external AI calls use fakes in normal tests.
- Before real provider or AWS use, document data destinations, usage limits,
  expected costs, and cleanup. Use non-sensitive sample documents for the demo.

## Deferred features

Billing, enterprise SSO, public sharing, email invitations, OCR, arbitrary web
crawling, agentic tool execution, document version history, collaborative editing,
and production compliance certification are outside the initial learning scope.

## Decisions to make when needed

Choose supported runtime and dependency versions in the relevant implementation
step. Choose authentication details in increment 5, upload limits and local object
storage in increment 8, AI providers/models and vector dimension in increment 11,
and AWS services/region in increment 16. These choices are not prerequisites for
the documentation scaffold.
