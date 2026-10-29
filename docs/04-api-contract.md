# 04 — API Contract

The route list below is the expected contract. Exact response shapes and status codes should be formalized during implementation and documented before frontend integration. Prefix: `/api/v1`.

## General conventions

- JSON for normal requests/responses; multipart upload for files.
- Authenticate all private endpoints.
- Validate input and output at API boundaries.
- Use consistent error bodies with a stable machine-readable code and safe human-readable message.
- Do not leak stack traces, secrets, storage internals, or other users' resource existence.
- Pagination is recommended for list endpoints.
- Use request IDs or correlation IDs where practical.
- Enforce owner and parent-resource checks for every nested ID.

## Health endpoints

- `GET /health/live` — process is alive.
- `GET /health/ready` — essential dependencies are reachable and service can accept work. Do not expose credentials or sensitive diagnostics.

## Workspace endpoints

- `POST /workspaces` — create a workspace.
- `GET /workspaces` — list current user's workspaces.
- `GET /workspaces/{workspace_id}` — get an owned workspace.
- `PATCH /workspaces/{workspace_id}` — rename/update permitted fields.
- `DELETE /workspaces/{workspace_id}` — delete only according to the documented cascade policy.

## Document endpoints

- `POST /workspaces/{workspace_id}/documents` — validate and upload a document; create document and job.
- `GET /workspaces/{workspace_id}/documents` — list documents and status.
- `GET /documents/{document_id}` — retrieve owned document metadata.
- `DELETE /documents/{document_id}` — delete/queue deletion of the source file and derived records.
- Optional: `GET /documents/{document_id}/status` if the list/detail response is not sufficient.

The upload response should make clear whether the file is accepted and queued, not imply indexing has already completed.

## Conversation endpoints

- `POST /workspaces/{workspace_id}/conversations` — create a conversation.
- `GET /workspaces/{workspace_id}/conversations` — list conversations for the owned workspace.
- `GET /conversations/{conversation_id}/messages` — list messages only after checking conversation ownership.
- `POST /conversations/{conversation_id}/messages` — submit a question and receive a grounded answer with citation metadata.
- Optional rename/delete routes only if included in MVP.

## Question-answering response requirements

The response should contain:
- Answer text.
- Evidence/citation array.
- A status indicating whether evidence was sufficient, if useful for UI.
- Optional safe metadata such as model/provider label and elapsed time, only if it does not expose secrets.

Each citation should resolve to a real retrieved chunk and document. Include a document title, page number when reliable, and short excerpt or chunk reference. Never invent a citation or silently substitute a non-retrieved chunk.

## Expected error categories

- `UNAUTHENTICATED`
- `FORBIDDEN` or a privacy-preserving `NOT_FOUND`
- `VALIDATION_ERROR`
- `FILE_TOO_LARGE`
- `UNSUPPORTED_FILE_TYPE`
- `QUOTA_EXCEEDED`
- `DOCUMENT_NOT_READY`
- `INSUFFICIENT_EVIDENCE` (may be a successful answer state rather than HTTP error)
- `RATE_LIMITED`
- `PROVIDER_UNAVAILABLE`
- `PROCESSING_FAILED`
- `INTERNAL_ERROR`

The implementation must define exact HTTP status mapping. Never expose raw provider errors or stack traces to the client.
