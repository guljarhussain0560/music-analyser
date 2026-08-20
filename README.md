# AI Music Analyser

[![CI Pipeline](https://github.com/guljarhussain0560/music-analyser/actions/workflows/ci.yml/badge.svg)](https://github.com/guljarhussain0560/music-analyser/actions)
[![Docker Build](https://github.com/guljarhussain0560/music-analyser/actions/workflows/docker-build.yml/badge.svg)](https://github.com/guljarhussain0560/music-analyser/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type Checked: Mypy](https://img.shields.io/badge/types-mypy-blue.svg)](http://mypy-lang.org/)
[![Test Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)](https://github.com/guljarhussain0560/music-analyser)

**AI Music Analyser** is an asynchronous, high-throughput music analysis and audio processing backend built with **FastAPI**, **Spleeter**, **Librosa**, and **Groq Whisper**. It ingests audio tracks via YouTube URLs, Spotify links, or direct file uploads, executes parallel stem separation and analytical feature extraction, transcribes synchronized timestamped lyrics, and provides intelligent music-theory queries via an integrated LLM assistant.

---

## Key Features

- **Multi-Source Audio Ingestion**: High-res audio stream acquisition from YouTube, Spotify, and direct multipart uploads.
- **5-Stem AI Source Separation**: State-of-the-art instrument isolation (Vocals, Bass, Drums, Piano, Other) powered by Spleeter.
- **Deep Musical & Timbral Analytics**: Microtonal pitch tracking (pYIN), key/mode heuristics, tempo/beat tracking, spectral roll-off, chroma profiles, MFCCs, and voice quality metrics (jitter, shimmer, HNR, vocal range).
- **Specialized Instrument Profiling**: Dedicated analytics for isolated guitar (strum vs. pick, chord complexity), violin & flute (vibrato rate/depth, legato articulation).
- **Synchronized Lyric Transcription & AI Rewriting**: Sub-second speech-to-text with Groq Whisper-large-v3, timestamped `.lrc` formatting, and context-aware lyric rewriting.
- **Non-blocking Concurrency**: Multi-tiered concurrency leveraging `concurrent.futures.ThreadPoolExecutor` for network I/O and `multiprocessing.Pool` for CPU-intensive DSP tasks.
- **Production Hardened**: Structured JSON logging, Pydantic v2 settings validation, bcrypt password hashing (72-byte safe), JWT authentication, committed reproducible lockfile (`requirements.lock`), and full pytest test suite with >85% code coverage.

---

## System Architecture

```text
                                [ Client Request ]
                                        │
                         (Audio URL or File Upload)
                                        ▼
                             [ Audio Acquisition ]
                                        │
                                        ▼
                          [ Phase 1: ThreadPool ]
                                        │
           ┌────────────────────┬───────┴────────┬────────────────────┐
           ▼                    ▼                ▼                    ▼
     [ S3 Uploader ]       [ Librosa ]      [ Spleeter ]      [ Groq Whisper ]
    (Original to S3)    (Master Analytics) (Split 5 Stems)  (Transcribe Lyrics)
           │                    │                │                    │
           │                    │                ▼                    │
           │                    │    [ Phase 2: Parallel ]            │
           │                    │                │                    │
           │                    │       ┌────────┴────────┐           │
           │                    │       ▼                 ▼           │
           │                    │ [ Thread Pool ]  [ Multiprocess ]   │
           │                    │ (Upload Stems)   (Stem Analysis)    │
           │                    │       │                 │           │
           └────────────────────┴───────┼─────────────────┴───────────┘
                                        ▼
                             [ PostgreSQL Database ]
```

---

## Technology Stack

| Layer | Technology |
| :--- | :--- |
| **API Framework** | FastAPI, Uvicorn, Pydantic v2 |
| **Database & ORM** | PostgreSQL, SQLAlchemy 2.0, Alembic |
| **Audio Processing** | Librosa, Pydub, SoundFile, SciPy |
| **Machine Learning / AI** | Spleeter (TensorFlow 2.9.3), Groq API (Whisper-large-v3, LLaMA-3) |
| **Concurrency** | `ThreadPoolExecutor`, `multiprocessing.Pool` |
| **Cloud Storage** | AWS S3 (`boto3`) |
| **Testing & Tooling** | Pytest, Pytest-Cov, Ruff, MyPy, Pip-Audit |

---

## Quickstart & Installation

### 1. Clone and Setup Environment
```bash
git clone https://github.com/guljarhussain0560/music-analyser.git
cd music-analyser

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.lock
pip install spleeter>=2.4.0 --no-deps
```

### 2. Environment Configuration
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

Key environment variables:
- `DATABASE_URL`: PostgreSQL connection string (defaults to `sqlite:///./music_analyser.db` for local development).
- `SECRET_KEY`: 32+ character string for JWT signing.
- `GROQ_API_KEY`: Groq API key for Whisper transcription and Maestro AI.
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET_NAME`: AWS S3 configuration.
- `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`: Spotify Developer credentials.
- `YT_COOKIES_PATH`: Path to YouTube `cookies.txt` for `yt-dlp`.

### 3. Run Database Migrations
```bash
alembic upgrade head
```

### 4. Start the Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```
Interactive OpenAPI documentation will be available at: [http://localhost:8080/docs](http://localhost:8080/docs).

---

## Running with Docker & Docker Compose

Start the full stack with PostgreSQL database:
```bash
docker-compose up -d --build
```
Check application logs:
```bash
docker-compose logs -f app
```

---

## Running Tests & Code Quality

Run unit and integration test suite with coverage report:
```bash
pytest --cov=app --cov-report=term-missing
```

Run linter, formatting, and type checks:
```bash
ruff check app tests
ruff format --check app tests
mypy app
```

---

## Security

Security policies, secret management guidelines, and threat modeling are documented in [SECURITY.md](SECURITY.md).

---

## API Reference

### Health & Monitoring
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Application health and database connection status |
| `GET` | `/api/health` | API gateway health check |

### Authentication (`/api/auth`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/signup` | Register a new user |
| `POST` | `/api/auth/signin` | Authenticate and obtain JWT Bearer token |
| `POST` | `/api/auth/google` | Sign in / sign up with Google OAuth ID token |
| `GET` | `/api/auth/users/me` | Retrieve authenticated user profile |
| `POST` | `/api/auth/forgot-password` | Request password reset OTP |
| `POST` | `/api/auth/reset-password` | Reset password using verified OTP |

### Audio Processing (`/api/process`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/process/process_url` | Process YouTube or Spotify track URL |
| `POST` | `/api/process/process_audio_file` | Upload and process local audio file |
| `GET` | `/api/process/get-lyrics/{song_id}` | Retrieve timestamped `.lrc` lyrics |
| `POST` | `/api/process/rewrite-lyrics/{song_id}` | AI lyric rewrite preserving timestamps |

### Music Analytics (`/api/analytics`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/analytics/songs/{song_id}` | Master track Librosa audio analytics |
| `GET` | `/api/analytics/splits/vocals/{song_id}` | Vocal stem audio URL & pitch/vocal quality metrics |
| `GET` | `/api/analytics/splits/bass/{song_id}` | Bass stem audio URL & low-end analytics |
| `GET` | `/api/analytics/splits/drums/{song_id}` | Drum stem audio URL & groove analytics |
| `GET` | `/api/analytics/splits/piano/{song_id}` | Piano stem audio URL & harmonic complexity |
| `GET` | `/api/analytics/splits/other/{song_id}` | Other stem audio URL & timbral texture |
| `GET` | `/api/analytics/splits/guitar/{song_id}` | Guitar chord style & strum/pick metrics |
| `GET` | `/api/analytics/splits/violin/{song_id}` | Violin pitch range & vibrato metrics |
| `GET` | `/api/analytics/splits/flute/{song_id}` | Flute legato score & breathiness metrics |

### Maestro AI Assistant (`/api/chat`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/chat/ask` | Query AI music analyst on musical theory and track metrics |

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
