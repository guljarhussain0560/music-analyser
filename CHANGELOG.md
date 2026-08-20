# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-20

### Added
- **Production Test Suite**: Added 100% runnable test suite in `tests/` covering authentication, CRUD, Pydantic schemas, modular analytics, downloaders, and API routes with >85% code coverage.
- **CI/CD Pipeline**: GitHub Actions workflow (`ci.yml`) enforcing linting (`ruff`), type-checking (`mypy`), security scanning (`pip-audit`), and automated test execution.
- **Health & Monitoring**: Added `GET /health` and `GET /api/health` endpoints returning system status, database connectivity, and version information.
- **Structured Logging**: Replaced all `print()` statements with standard structured logging via `app.core.logging`.
- **Modularized Analytics Subpackage**: Split monolithic `extract_analytics.py` (553 LOC) into focused, clean submodules (`common.py`, `full_song.py`, `vocal.py`, `rhythm_bass.py`, `instruments.py`) all under 200 LOC.
- **Strict Settings Validation**: Introduced Pydantic `BaseSettings` (`app.core.config`) validating all environment variables with graceful fallback and clear diagnostic alerts.
- **Security Hardening**: Removed hardcoded dummy password literals in OAuth flow in favor of cryptographically secure random token generation (`secrets.token_urlsafe(32)`).
- **Dependency Health**: Added pinned versions, committed `requirements.lock.txt`, and configured weekly Dependabot updates.
- **Documentation**: Added comprehensive `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, and full `.env.example` documenting all 7 `MAIL_*` variables.

### Fixed
- Fixed Split CRUD query bug where instrument queries filtered by split primary key instead of song foreign key.
- Fixed JWT subject type inconsistency between user ID and email in route authentication.
- Fixed unhandled `SystemExit` exception on missing downloader environment variables.
- Fixed SQLAlchemy JSON compatibility allowing cross-database execution on PostgreSQL and SQLite in-memory test environments.
