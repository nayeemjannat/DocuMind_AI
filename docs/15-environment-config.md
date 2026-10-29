# 15 — Environment Configuration Guide

This document describes categories of configuration. It intentionally does not provide actual secrets or assume final variable names. The implementation should choose names consistently and document them in `.env.example`.

## Configuration categories

### Frontend-public configuration
Only values safe for every visitor:
- Public app URL.
- Managed-auth public URL/project identifier.
- Public client key only if the provider explicitly designates it as safe and policies are correctly configured.

### Backend-only configuration
- API environment and allowed frontend origins.
- Managed-auth JWT verification settings or issuer/audience.
- Database connection configuration.
- Storage access credentials.
- LLM provider API key and selected model.
- Embedding model name and vector dimension.
- Upload and quota policy values.
- Worker polling, lease, retry, and timeout settings.
- Logging level and request ID configuration.

## Rules

- Never commit `.env`, `.env.local`, real API keys, service-role keys, database passwords, signed URLs, or tokens.
- Commit only a `.env.example` with placeholder descriptions, not real values.
- Keep backend secrets out of variables exposed to the browser.
- Validate required configuration at startup and fail clearly if missing.
- Do not log secret values when validation fails.
- Use separate development and deployment credentials.
- Rotate any credential that was accidentally committed or shared.
- Set production values in the hosting platform's secret/environment settings.
- Avoid exposing full environment configuration in health endpoints.

## Environment setup checklist

- [ ] Create local environment file from the documented example.
- [ ] Fill local-only values without committing the file.
- [ ] Verify frontend public variables contain no secret.
- [ ] Verify backend starts only with required configuration.
- [ ] Verify health endpoints do not disclose secret values.
- [ ] Verify repository ignore rules exclude secret files.
- [ ] Verify deployment dashboard values match the documented provider setup.
