# Security Policy

## Supported Versions

We actively provide security updates and patches for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Threat Model & Security Architecture

### Authentication & Secrets Management
- All authentication utilizes industry-standard bcrypt password hashing (`passlib[bcrypt]`) with cost-factor salting.
- OAuth 2.0 / Google authentication generates cryptographically secure randomized credentials using Python's `secrets.token_urlsafe(32)`. Hardcoded dummy secrets are strictly prohibited.
- JWT tokens are signed using HMAC-SHA256 (`HS256`) with configurable expiration windows and validated cryptographic signatures.
- Configuration variables and secrets are managed strictly through typed Pydantic `BaseSettings` validated at startup. Missing sensitive credentials trigger explicit configuration alerts rather than silent failures.

### Audio Ingestion & File Processing
- File uploads are validated for MIME type, file header signatures, and file size constraints before processing.
- Temporary files created during audio stem separation and transcode operations are confined to isolated ephemeral temp directories and securely purged upon pipeline completion via `try...finally` context managers.
- Path traversal vectors in filenames downloaded via YouTube / Spotify are mitigated by strict regex sanitization.

### Dependency Vulnerability Auditing
- Continuous automated security scanning is enforced in GitHub Actions using `pip-audit`.
- Dependabot provides weekly security patch updates for all direct and transitive dependencies.

## Reporting a Vulnerability

If you discover a potential security vulnerability in this project, please report it responsibly:

1. **Do not create a public GitHub issue.**
2. Send a detailed report to `security@musicanalyser.io` including:
   - Description of the vulnerability.
   - Steps to reproduce or proof-of-concept exploit.
   - Potential impact and affected components.
3. We acknowledge receipt within 48 hours and aim to provide a remediation patch within 7 business days.
