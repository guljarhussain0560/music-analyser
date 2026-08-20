# Contributing to AI Music Analyser

Thank you for your interest in contributing to the AI Music Analyser project! We welcome contributions from developers of all skill levels.

## Development Workflow

### 1. Prerequisites
- Python 3.10 or 3.11
- FFmpeg (required for audio decoding and transcode operations)
- PostgreSQL (or SQLite for local lightweight testing)
- Git

### 2. Local Environment Setup
```bash
# Clone the repository
git clone https://github.com/guljarhussain0560/AI-Music-Analyser.git
cd AI-Music-Analyser

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies in editable mode
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### 3. Code Standards & Linting
We enforce clean code formatting and strict linting rules using **Ruff**:
```bash
# Run linter
ruff check app tests

# Run auto-formatter
ruff format app tests
```

### 4. Running the Test Suite
All new features and bug fixes must include unit or integration tests with high test coverage:
```bash
# Run pytest with coverage report
pytest --cov=app --cov-report=term-missing
```

### 5. Git Commit Guidelines
We follow conventional commit specifications:
- `feat(scope)`: A new feature
- `fix(scope)`: A bug fix
- `refactor(scope)`: Code restructuring without feature changes
- `test(scope)`: Adding or updating tests
- `docs(scope)`: Documentation improvements
- `ci(scope)`: CI/CD workflow updates

## Submitting Pull Requests
1. Fork the repository and create your feature branch: `git checkout -b feat/your-feature-name`.
2. Ensure all tests pass (`pytest`) and linting is clean (`ruff check`).
3. Commit your changes in small, logical increments.
4. Submit a Pull Request targeting the `main` branch with a clear description of changes.
