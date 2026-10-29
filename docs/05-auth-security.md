# 05 — Authentication, Authorization, and Security

Security is a release gate, not a later enhancement.

## Authentication

- Verify the managed-auth token/session on the server for every private API call.
- Never trust a user ID sent in a request body as proof of identity.
- Reject invalid, expired, or malformed tokens.
- Keep server-only credentials out of client bundles and public environment variables.

## Authorization / tenant isolation

For every request, verify the authenticated user owns the workspace and the requested resource belongs to that workspace. Apply this to:
- Workspaces.
- Documents and source files.
- Chunks and vector retrieval.
- Conversations and messages.
- Ingestion jobs and job-status endpoints.
- Delete, retry, and export-like operations.

Do not authorize only by checking that an ID exists. A random UUID is not an access-control mechanism.

## Storage

- Source files must be private.
- Never create permanent public URLs for private uploads.
- Use short-lived signed URLs only if necessary, with narrow scope and expiry.
- Restrict upload size and accepted file formats.
- Sanitize filenames for display and storage; avoid trusting user-supplied paths.
- Delete source objects and derived database records according to a documented, retryable policy.

## File safety

- Allow only PDF, DOCX, and TXT in the MVP.
- Enforce maximum file size before expensive parsing.
- Validate actual file structure as well as filename/claimed MIME type where feasible.
- Handle corrupt, encrypted, malformed, and unsupported files gracefully.
- Do not execute or render uploaded active content.
- Apply parser time/resource limits where possible.
- Avoid logging file content.

## Prompt injection and RAG safety

- Treat all document text as untrusted data, never as system instructions.
- The system prompt must instruct the model to use retrieved passages only as evidence and ignore instructions embedded in those passages.
- Do not let retrieved text trigger tool use, secret disclosure, policy changes, or cross-document access.
- Keep authorization filtering in the retrieval query, before data reaches the model.
- Bound context length and retrieved excerpt size.
- Validate citation IDs against the actual retrieved result set.

## Rate limits and quotas

Initial target policy:
- Up to 20 questions/day/account.
- Up to 5 uploads/day/account.
- One active ingestion job/account.
- Up to 5 stored documents/account.
- 5 MB/file and 30 pages/document where count is available.

These are initial policy values and must be configurable. Apply limits server-side, not only in the UI.

## Secrets and privacy

- Keep `.env` files out of version control.
- Provide a `.env.example` containing variable names and descriptions only, never real values.
- Never log access tokens, service-role keys, provider keys, full prompts containing sensitive data, or document bodies.
- Send only the minimum relevant excerpts to the LLM provider.
- Document the provider's data handling terms before public use.
- Avoid sensitive real-world documents in demo fixtures.

## Minimum security tests

1. User A cannot read User B's workspace.
2. User A cannot download User B's file.
3. User A cannot query or cite User B's chunks.
4. User A cannot read User B's conversations/messages.
5. User A cannot delete or alter User B's resources.
6. Forged parent/child IDs are rejected.
7. Upload validation blocks disallowed formats and oversized files.
8. Prompt injection in a document cannot override system rules.
9. Rate limits cannot be bypassed by simply hiding UI controls.
10. Client responses do not expose stack traces or credentials.
