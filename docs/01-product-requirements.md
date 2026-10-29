# 01 — Product Requirements (MVP)

## User journey

1. Visitor opens the app and understands its purpose.
2. User signs up or signs in.
3. User creates or opens a workspace.
4. User uploads a PDF, DOCX, or TXT document.
5. The app validates the file and stores it privately.
6. The app queues an ingestion job and shows its status.
7. A worker extracts text, chunks it, creates embeddings, and stores searchable chunks.
8. User starts or opens a conversation and asks a question.
9. The system retrieves relevant authorized chunks and generates a grounded answer.
10. The UI displays the answer and citations.
11. User can review conversation history and delete a document.

## Functional requirements

### Authentication and ownership
- Require authentication for all private app actions.
- Every workspace, document, conversation, and message request must verify ownership server-side.
- Never rely on a UUID being difficult to guess as authorization.
- Expired or invalid sessions must not access protected resources.

### Workspaces
- Authenticated users can create, list, view, rename, and delete their own workspaces, subject to the chosen MVP deletion policy.
- A workspace belongs to exactly one user in the MVP.
- Workspace IDs must be checked against the authenticated user's identity on every nested request.

### Documents
- Accept PDF, DOCX, and TXT only.
- Initial limit: 5 MB per file, 30 pages per document where page count is available, up to 5 documents per account.
- Initial limits are configurable policy values, not hard-coded assumptions across the codebase.
- Validate extension, MIME type, file signature/format where feasible, size, and parser outcome.
- Store source files in private object storage.
- Show uploaded time, processing status, and safe error messages.
- Allow owner to delete a document and its derived chunks/embeddings.
- Do not log full document contents or secrets.

### Ingestion
- Persist job state in the database.
- Expected states: `uploaded`, `queued`, `processing`, `ready`, `failed`, `deleting`, `deleted`.
- Failed jobs must provide a safe user-facing reason and a diagnosable server-side error category.
- Retries must be bounded and idempotent.
- A process restart must not silently lose the job or leave it permanently processing.

### Question answering
- Retrieve only chunks authorized for the signed-in user and current workspace.
- Use the same embedding model for document chunks and questions.
- Use a configurable top-k, initially 8.
- Apply a relevance/evidence gate before asking the LLM to answer.
- Answers should be based on retrieved excerpts, not general model knowledge.
- If evidence is insufficient, clearly say so.
- Citations must refer to actual retrieved chunks and the correct document.
- Treat uploaded content as untrusted data; it must not override system instructions.

### Conversations
- Store conversation and message history for the owning user.
- Associate a conversation with a workspace.
- Keep user messages, assistant answers, and citation metadata consistent.
- Do not reveal another user's history.

### Operational controls
- Initial target limits: 20 questions/day/account, 5 uploads/day/account, one active ingestion job/account.
- These are configurable initial caps. Return a clear rate/limit response when reached.
- Do not use paid fallback providers.
- Provide liveness and readiness endpoints.
- Provide a safe demo flow without exposing real secrets or private sample documents.

## Non-functional requirements

- Type-safe frontend.
- API validation at trust boundaries.
- Consistent error format and request correlation where practical.
- Basic accessibility: labels, keyboard navigation, readable errors, loading and empty states.
- Responsive layout for desktop and mobile.
- Automated tests for authorization, parsing, retrieval, citations, and primary user flow.
- Clear setup and deployment documentation.

## Explicitly out of scope for MVP

- OCR for scanned PDFs.
- Billing or paid subscriptions.
- Team collaboration and shared workspaces.
- Multiple organizations and complex role hierarchies.
- Arbitrary file types, ZIP uploads, executable files, or URL ingestion.
- Fine-tuning a model.
- Guaranteed zero latency, always-on free hosting, or enterprise availability.
- Legal, medical, or financial decision-making claims.

## Product questions that must be decided before relevant implementation

Record decisions in `13-decisions.md`:
- Workspace deletion semantics and cascade behavior.
- Exact LLM provider/model available on a free tier at implementation time.
- Whether citations show page number, section heading, chunk excerpt, or available subset.
- Final embedding implementation after the resource test.
- Demo data and public-demo access policy.
