# TL-AI

TL-AI project workspace.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Docker Desktop (PostgreSQL 17 + pgvector)

## Getting Started

```bash
git clone https://github.com/jdkerados/TL-AI.git
cd TL-AI
uv sync
uv run pre-commit install
```

## Development

| Command | Purpose |
|---|---|
| `uv run ruff check .` | Lint |
| `uv run black --check .` | Format check |
| `uv run mypy` | Type check |
| `uv run pytest` | Tests |

## Project Structure

```
docs/            Documentation (architecture, domain, ai, workflow, adr)
specifications/  Specifications
schemas/         Schemas
config/          Configuration
database/        Database assets
scripts/         Utility scripts
tests/           Test suite
tools/           Developer tools
src/             Source packages (tl_core, tl_database, tl_api, tl_compiler,
                 tl_simulator, tl_studio, tl_lab, tl_common)
```

See `docs/MASTER_SPECIFICATION.md` for the master specification.
