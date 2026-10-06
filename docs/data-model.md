# Proposed data model

Status: conceptual design. No tables or migrations exist yet. UUID primary keys
and timezone-aware timestamps are the proposed defaults. UUIDs do not replace
authorization. Names below may evolve when the corresponding feature is built.

## Relationships

```text
User ---< Membership >--- Organization
                             |
                             +---< Document ---< ProcessingJob
                             |        |
                             |        +---< DocumentChunk
                             |
                             +---< Conversation ---< Message ---< Citation
                                                                    |
                                                        DocumentChunk (nullable
                                                        after source deletion)
```

## Entities

| Entity | Proposed fields and purpose |
| --- | --- |
| User | `id`, `email`, `password_hash`, `display_name`, `created_at`, `updated_at`; global identity with normalized unique email |
| Organization | `id`, `name`, `created_by_id`, timestamps; tenant boundary |
| Membership | `id`, `organization_id`, `user_id`, `role`, timestamps; role is owner or member |
| Document | `id`, `organization_id`, `uploaded_by_id`, `filename`, `content_type`, `size_bytes`, `object_key`, `status`, `active_processing_job_id`, `error_code`, timestamps, `deleted_at`; metadata for one upload |
| ProcessingJob | `id`, `organization_id`, `document_id`, `status`, `attempt_count`, `pipeline_version`, `embedding_model`, `embedding_dimensions`, `last_error_code`, `started_at`, `finished_at`, timestamps; durable processing and retry record |
| DocumentChunk | `id`, `organization_id`, `document_id`, `processing_job_id`, `chunk_index`, `text`, `page_number` (nullable), `location_metadata`, `embedding`, `created_at`; source passage and its vector |
| Conversation | `id`, `organization_id`, `created_by_id`, `title`, timestamps; private to its creator within the organization |
| Message | `id`, `organization_id`, `conversation_id`, `sequence_number`, `role`, `content`, `status`, `model_name` (nullable), timestamps; persisted user question or assistant answer |
| Citation | `id`, `organization_id`, `message_id`, `chunk_id` (nullable), `source_label`, `page_number` (nullable), `created_at`; link from an answer to a retrieved passage |

Store generated system prompts separately from user-visible message history if
needed later. Do not persist copied source passages inside citations by default;
source deletion should remove extracted chunk text. Saved answer text is separate
and may still contain information from a deleted source.

## Constraints and indexes

- Unique normalized user email and unique `(organization_id, user_id)` membership.
- Validate role/status values and nonnegative file sizes and attempt counts.
- A document's object key is generated server-side and unique.
- Each tenant-owned table carries `organization_id` for explicit filtering.
  Use composite foreign keys and matching unique constraints, for example
  `(organization_id, document_id)` references Document `(organization_id, id)`.
  Apply the same rule to jobs, chunks, conversations, messages, and citations.
- A chunk's job must belong to the same document. A document's active job must
  belong to that document. Design the corresponding composite constraints in the
  processing migration; organization equality alone is insufficient.
- Unique `(processing_job_id, chunk_index)` prevents duplicate chunk positions.
  Retried attempts replace/stage their output under controlled job ownership.
- Unique `(conversation_id, sequence_number)` gives deterministic message order.
- Index tenant-filtered access paths, including document state, memberships,
  conversation ownership, message sequence, and pending jobs.
- Choose the vector dimension and similarity metric with the embedding model.
  Start with correctness on a small dataset; add a vector index after measuring.
  Model changes require re-embedding, not mixing incompatible vectors.

Membership must be checked at operation time. Foreign keys to users preserve
authorship but do not establish current access. The last-owner rule requires a
transaction-safe application operation; a basic role check constraint is not enough.

## Lifecycle and retention

Documents normally move `queued → processing → ready` or `processing → failed`.
A retry can move `failed → queued`. Upload success must precede queue dispatch;
partial upload failures are cleaned up and never exposed as ready documents.

Deletion moves an active document to `deleting`, immediately hides it from
retrieval, and cancels/prevents publication by processing jobs. Cleanup removes
S3 bytes and chunks/vectors, nulls affected citation references, and retains a
minimal `deleted` document tombstone. Cleanup is retryable. Historical citations
show “source unavailable”; historical answer text remains until its conversation
is deleted. We will define precise retention behavior in the deletion feature.

Jobs use queued, running, succeeded, failed, and cancelled states. Document state
summarizes user-facing availability; job state tracks execution. Update related
database state within transactions and use conditional claims to prevent workers
from racing with retries or deletion.

Messages use pending, streaming, completed, failed, or cancelled states as needed.
User messages are completed when accepted. Assistant messages become completed
only after successful generation; partial content must be labeled appropriately.

## Migration approach

Introduce tables alongside their features: users first, then organizations and
memberships, documents/jobs/chunks, and conversations/messages/citations. When
adding tenancy to existing development data, define a backfill before making
organization IDs mandatory. Review every migration and its upgrade behavior;
data-destructive downgrades require explicit consideration.
