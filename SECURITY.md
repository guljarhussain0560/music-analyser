# Security Policy & Threat Model

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## Architectural Threat Model & Trust Boundaries

The AI Music Analyser backend ingests user-supplied audio streams and communicates with third-party cloud infrastructure. All data passing through system boundaries is validated using defensive programming principles.

```text
               [ Untrusted External Network ]
                              │
              (TLS 1.3 / Bearer JWT / Multipart)
                              ▼
    ┌─────────────────────────────────────────────────────┐
    │              FastAPI Perimeter Gateway              │
    │  - Rate Limiting (SlowAPI)                          │
    │  - CORS Policy Restriction                          │
    │  - Pydantic v2 Schema Sanitization                  │
    └──────────────┬──────────────────────┬───────────────┘
                   │                      │
                   ▼                      ▼
    ┌──────────────────────────┐  ┌───────────────────────────┐
    │      Authentication      │  │     Audio Ingestion       │
    │  - Bcrypt 72-byte safe   │  │  - Filename Sanitization  │
    │  - JWT HS256 validation  │  │  - MIME Type Verification │
    │  - Google OAuth ID token │  │  - Isolated Temp Subdirs  │
    └──────────────────────────┘  └─────────────┬─────────────┘
                                                │
                                                ▼
    ┌─────────────────────────────────────────────────────────┐
    │               Internal Processing Domain                │
    │  - Spleeter 5-Stem Separation (TensorFlow Sandbox)      │
    │  - Librosa DSP Feature Extraction (Memory Bound)        │
    │  - Groq Whisper Speech-to-Text (Encrypted API Calls)    │
    │  - AWS S3 Stem Storage (UUID-Named S3 Objects)          │
    └─────────────────────────────────────────────────────────┘
```

### Threat Boundary Risk Assessment

| Trust Boundary | Risk Vector | Mitigation Strategy |
| :--- | :--- | :--- |
| **Audio File Ingestion** | Path traversal (`../../etc/passwd`), zip bombs, arbitrary code execution. | Filename sanitization via `app.utils.downloader.sanitize_filename`, strictly enforced MIME whitelist (`audio/*`), random temp dir allocation via `tempfile.TemporaryDirectory()`. |
| **YouTube & Spotify Acquisition** | Command injection in `yt-dlp` subprocess. | Execution with list argument format avoiding shell interpolation; strict URL regex matching. |
| **Authentication & Tokens** | Password enumeration, rainbow table attacks, token forgery. | Bcrypt password hashing with high salt rounds and 72-byte truncation; cryptographically strong random token generation (`secrets.token_urlsafe(32)`). |
| **Groq & Spotify APIs** | Prompt injection in LLM music assistant, API quota exhaustion. | Input length truncation, structured JSON response schema enforcement, and exponential backoff retry logic. |
| **Cloud Storage (AWS S3)** | Bucket enumeration, public stem exposure. | UUID-based unguessable keys (`songs/<user_id>/stems/<uuid>.mp3`), bucket ACL set to private. |

---

## Production Secrets Management

In production deployments (Kubernetes, AWS ECS, GCP Cloud Run), **plaintext `.env` files must not be used**.

### 1. AWS Secrets Manager Integration
Store production secrets in AWS Secrets Manager under `/production/music-analyser/credentials`:
```json
{
  "SECRET_KEY": "<generated-random-32-char-key>",
  "DATABASE_URL": "postgresql+psycopg2://<user>:<pwd>@<rds-endpoint>:5432/musicanalyser",
  "AWS_ACCESS_KEY_ID": "<iam-key>",
  "AWS_SECRET_ACCESS_KEY": "<iam-secret>",
  "GROQ_API_KEY": "<groq-key>"
}
```
Inject via IAM Task Role using `app.core.secrets_manager.SecretManagerProvider`.

### 2. HashiCorp Vault Integration
Mount Vault dynamic secrets into container pods at `/vault/secrets/config.env` using Vault Agent Sidecar Injector.

### 3. Secret Rotation Schedule
- **`SECRET_KEY`**: 90 days.
- **`AWS Credentials`**: 60 days via AWS IAM automated credential rotation.
- **`GROQ_API_KEY`**: 90 days.

---

## Reporting a Vulnerability

If you discover a potential security issue in AI Music Analyser, please contact our security team:

- **Email**: `security@musicanalyser.io` / `guljarhussain0560@gmail.com`
- **Initial Response Window**: Within 48 hours.
- **Remediation SLA**: Within 7 business days for critical findings.

Please do not disclose security issues on public issue trackers before a patch has been released.
