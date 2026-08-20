# Security Policy & Threat Model

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## Threat Model & Trust Boundaries

The AI Music Analyser crosses multiple system and network boundaries. All input data entering the system is treated as untrusted and subjected to strict validation.

```text
[ Untrusted Public Internet ]
           │
           │ (HTTPS / Bearer JWT)
           ▼
[ API Gateway / FastAPI Boundary ]  <-- Rate limiting, CORS, Pydantic DTO validation
           │
           ├───► [ Auth Service ]   <-- Bcrypt hashing (salted, 72-byte truncation), JWT validation
           │
           ├───► [ YouTube / Spotify Downloader ]  <-- Subprocess isolation, filename sanitization
           │
           ├───► [ Spleeter DSP ]   <-- Local temp file isolation, non-root sandbox execution
           │
           └───► [ AWS S3 / Groq API ]  <-- HTTPS with TLS 1.3, IAM least privilege
```

### Trust Boundaries & Mitigations

1. **Client Audio Ingestion (URLs & File Uploads)**:
   - *Risk*: Path traversal, command injection, Denial of Service (DoS) via oversized files.
   - *Mitigation*: Regex filename sanitization via `app.utils.downloader.sanitize_filename`, strictly enforced audio MIME type validation, and streaming file writes to isolated temporary directories with automatic cleanup.

2. **External API Calls (Groq Whisper, Groq LLM, Spotify API)**:
   - *Risk*: Credential leakage, API quota exhaustion, untrusted LLM prompt injection.
   - *Mitigation*: Outbound HTTPS with TLS 1.3, strict payload schemas, retry backoff with jitter, and input length capping before prompt construction.

3. **Authentication & Session Tokens**:
   - *Risk*: Password database theft, JWT tampering, Google OAuth impersonation.
   - *Mitigation*: Bcrypt password hashing with unique salts, cryptographically strong random token generation (`secrets.token_urlsafe(32)`), audience (`aud`) verification on Google OAuth ID tokens, and short token lifespans.

4. **Cloud Storage (AWS S3)**:
   - *Risk*: Bucket enumeration, unauthorized stem access.
   - *Mitigation*: UUID-based non-guessable object paths (`songs/uploads/<uuid>.<ext>`), private S3 ACLs, and temporary signed URLs for playback where required.

---

## Production Secret Management

In production environments, credentials **must never** be stored in plaintext `.env` files. Secrets should be injected dynamically using one of the following mechanisms:

1. **AWS Secrets Manager / AWS Parameter Store**:
   - Store credentials under secret path `/production/music-analyser/`.
   - Grant EC2/ECS/EKS IAM task role with `secretsmanager:GetSecretValue` permission only.

2. **HashiCorp Vault / Kubernetes Secrets**:
   - Mount credentials as environment variables directly inside the container pod spec.

3. **Required Secrets Rotation Schedule**:
   - `SECRET_KEY`: Rotate every 90 days.
   - `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`: Rotate every 60 days via IAM user rotation.
   - `GROQ_API_KEY`: Rotate every 90 days.
   - `DATABASE_URL`: Managed via RDS IAM database authentication or rotated via Vault.

---

## Reporting a Vulnerability

If you discover a potential security vulnerability in this project, please report it responsibly:

- **Email**: `security@musicanalyser.io` (or `guljarhussain0560@gmail.com`)
- **PGP Key**: Available upon request.
- **Expected Response**: Initial response within 48 hours; resolution plan within 7 business days.

Please **do not** open public GitHub issues for undisclosed security vulnerabilities.
