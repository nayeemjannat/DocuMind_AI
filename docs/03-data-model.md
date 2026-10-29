# 03 — Data Model

This is a logical schema specification, not executable SQL. Final column types, constraints, indexes, and migration syntax must be decided during implementation and tested.

## Core entities

### `profiles`
Purpose: app-level profile associated with the managed-auth identity.
- `id` — same identity key as the auth provider where appropriate.
- `display_name` — optional.
- `created_at`, `updated_at`.

### `workspaces`
Purpose: container for documents and conversations.
- `id` — primary identifier.
- `owner_id` — authenticated user's identity.
- `name`.
- `created_at`, `updated_at`.

### `documents`
Purpose: source file metadata and processing status.
- `id`.
- `workspace_id`, `owner_id`.
- `original_filename` — display-safe filename.
- `storage_path` — private object key, not a public URL.
- `mime_type`, `size_bytes`, `page_count` where available.
- `status` — documented state enum/string.
- `checksum` where useful for duplicate detection/idempotency.
- `created_at`, `updated_at`, `deleted_at` where soft deletion is chosen.
- Safe error category/code when processing fails; do not store sensitive stack traces for clients.

### `document_chunks`
Purpose: searchable, traceable extracted passages.
- `id`.
- `document_id`, `workspace_id`, `owner_id`.
- `chunk_index`.
- `content` — extracted passage; access is private.
- `page_number` and/or section metadata where reliably available.
- `embedding` — vector with dimension matching the chosen embedding model.
- `content_hash` or idempotency key where useful.
- `created_at`.

### `conversations`
Purpose: chat session within a workspace.
- `id`.
- `workspace_id`, `owner_id`.
- `title` — optional.
- `created_at`, `updated_at`.

### `messages`
Purpose: ordered user/assistant conversation history.
- `id`.
- `conversation_id`, `workspace_id`, `owner_id`.
- `role` — user or assistant; constrain allowed values.
- `content`.
- `citation_metadata` — structured references to retrieved chunks/documents.
- `created_at`.

### `ingestion_jobs`
Purpose: durable background processing state.
- `id`.
- `document_id`, `workspace_id`, `owner_id`.
- `status`.
- `attempt_count`, `max_attempts`.
- `available_at` or equivalent retry scheduling.
- `claimed_at`, `lease_expires_at`, `worker_id` or equivalent lease fields.
- `last_error_code` and safe diagnostic metadata.
- `created_at`, `updated_at`, `finished_at`.

### Optional `audit_events`
Use only if needed for debugging/security events. Avoid logging document contents, access tokens, or secrets.

## Relationship expectations

- One owner can have multiple workspaces.
- One workspace can have multiple documents and conversations.
- One document can have many chunks and ingestion jobs/retries.
- One conversation can have many messages.
- Every private child row must carry enough relationship information to verify ownership safely, or be joined through a verified parent.
- Enforce foreign keys and useful uniqueness constraints.
- Define deletion/cascade semantics explicitly before implementing delete.

## Indexing guidance

- Index ownership and parent lookup columns.
- Index job status and availability/lease fields used to claim work.
- Add a vector index only after confirming the selected pgvector index is supported and useful at MVP scale.
- Add a unique idempotency constraint for chunk identity, such as document + chunk index + ingestion version, if consistent with the final design.

## Data isolation requirements

- Enable row-level security where appropriate.
- If a server uses a privileged service-role credential that bypasses RLS, application-level ownership checks remain mandatory for every request.
- Do not assume RLS alone protects calls made with a bypass credential.
- Private storage objects must be authorized through server-controlled access or properly scoped policies.
