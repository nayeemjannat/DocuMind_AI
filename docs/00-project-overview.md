# 00 — Project Overview

## Product summary

DocuMind AI is a web application that lets an authenticated user upload documents and ask questions about their contents. It should answer from the uploaded evidence, cite the supporting document passages, and clearly say when the available documents do not support an answer.

## Problem

People often need to find specific facts across long documents. Manually searching is slow, and generic chatbots may invent answers or provide unverifiable references. DocuMind AI aims to make document-based answers easier to inspect and verify.

## Primary user and use case

A user signs in, creates a workspace, uploads a small collection of documents, waits for indexing to finish, then asks questions and reviews answers with citations.

## Product principles

1. **Grounded over confident:** unsupported questions should receive an honest insufficient-evidence response.
2. **Citations must be verifiable:** every citation must map to retrieved source material.
3. **Privacy by default:** private files and workspace data are accessible only to their owner.
4. **Small and maintainable:** one frontend, one API, and one worker process boundary where practical; no unnecessary microservices.
5. **Zero-budget MVP:** avoid paid dependencies during initial development and demo, while clearly documenting free-tier limits.
6. **Observable work:** ingestion jobs have durable status, failures are visible, and retries are controlled.
7. **Honest portfolio claims:** performance targets are goals until test results prove them.

## Target and non-target

**Target:** a working portfolio demonstration for approximately 2–4 users, suitable for a developer to explain in an interview.

**Not a target:** enterprise uptime, high concurrency, legal/medical decision support, large-scale multi-tenant SaaS, guaranteed free unlimited hosting, or production-grade compliance certification.

## MVP success definition

A user can sign in, create a workspace, upload a valid PDF/DOCX/TXT file, see processing status, ask a question, receive an evidence-grounded answer with valid citations, view conversation history, and delete the document. Another user cannot access the first user's workspace, document, chunks, or conversations.

## Key risks

- Free hosting may sleep, restart, or impose strict CPU/RAM limits.
- Local embedding models may exceed available memory.
- Free LLM quotas or terms can change.
- PDF page extraction and citation page numbers may be imperfect.
- Background jobs must recover after restarts.
- Prompt injection can appear inside uploaded documents.
- Provider-specific APIs can change.

See `17-risk-register.md` for mitigation notes.
