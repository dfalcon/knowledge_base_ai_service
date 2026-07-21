# ai-service

Knowledge Base AI service built with [FastAPI](https://fastapi.tiangolo.com/).

## Requirements

- Python `3.13.7` (pinned in `.python-version`)
- Either [uv](https://docs.astral.sh/uv/) **or** [pyenv](https://github.com/pyenv/pyenv) + `pip`

## Setup

### Option A: uv (recommended)

[Install uv](https://docs.astral.sh/uv/getting-started/installation/) if you don't have it yet.

```bash
# Installs the pinned Python version (if missing) and creates .venv
uv sync

# Run the app (dev mode, with auto-reload)
uv run fastapi dev main.py

# Run the app (production mode)
uv run fastapi run main.py
```

`uv sync` installs both the runtime and dev dependency groups (ruff, mypy, pre-commit) from `uv.lock`, so the environment is fully reproducible.

To install only runtime dependencies (no dev tools):

```bash
uv sync --no-dev
```

### Option B: pyenv + pip

Use this if you don't have (or don't want) `uv`.

```bash
# Install and select the pinned Python version
pyenv install --skip-existing 3.13.7
pyenv local 3.13.7

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Runtime dependencies only
pip install -r requirements.txt

# ...or runtime + dev tools (ruff, mypy, pre-commit)
pip install -r requirements-dev.txt

# Run the app (dev mode, with auto-reload)
fastapi dev main.py

# Run the app (production mode)
fastapi run main.py
```

`requirements.txt` and `requirements-dev.txt` are generated from `uv.lock` (see below), so both setup paths install the exact same pinned versions.

## Development tooling

- **[ruff](https://docs.astral.sh/ruff/)** — linting and formatting: `uv run ruff check .` / `uv run ruff format .`
- **[mypy](https://mypy.readthedocs.io/)** — static type checking: `uv run mypy .`
- **[pre-commit](https://pre-commit.com/)** — git hooks, installed via `uv run pre-commit install`

### Keeping requirements files in sync

`requirements.txt` (runtime only) and `requirements-dev.txt` (runtime + dev) are auto-generated from `pyproject.toml`/`uv.lock` by a pre-commit hook (`uv-export`). Whenever dependencies change, the hook regenerates both files on commit — if they're stale, the commit fails once, the files get updated, and you just need to `git add` them and commit again.

To run it manually:

```bash
uv run pre-commit run --all-files
```
