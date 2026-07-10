# Manual Import Provider

The Manual Provider is the **only** provider implemented in Milestone M1. It imports locally
curated YAML specifications from `specifications/` into the TL-AI databases. There is no
scraping, no Playwright, and no external website access.

## Data Flow

```
specifications/*.yaml
        │
        ▼
LocalManualProvider        scans specifications/ and fetches one SourceDocument per file
        │
        ▼
tl_compiler pipeline       YAML loader + schema / stable-ID / cross-reference / semantic
        │                  validation (import aborts on any validation error)
        ▼
tl_compiler IR             build_ir: canonical, sorted intermediate representation
        │
        ▼
DatabaseImporter           upserts IR entities into PostgreSQL and/or SQLite (tl_database)
        │
        ▼
build/import_report.json   full machine-readable run report
```

## Components

- **`tl_importer.providers.manual.LocalManualProvider`** — concrete implementation of the
  `ManualProvider` interface: `name == "manual"`, supports every entity type, `fetch()` yields
  one `SourceDocument` per YAML file.
- **`tl_importer.importers.database.DatabaseImporter`** — upserts compiled `IREntity` records
  into a SQLAlchemy engine using the `tl_database` models (joined-table inheritance per type).
- **`tl_importer.service.ManualImportService`** — orchestration: scan, validate via
  `tl_compiler`, build IR, import into each target, write the report.

## Database Behavior

- **UPSERT by stable ID**: existing entities are looked up by `stable_id`.
- **Version gate**: an existing entity is updated only when the incoming semantic version is
  strictly newer. Equal versions are skipped; older versions are **rejected** as downgrades.
- **Type gate**: a change of entity type for an existing stable ID is rejected.
- **Validation flag**: every imported entity is stored with `is_validated = true`.
- **Stored fields**: name, description, `semantic_version`, `patch_version`, and `metadata`
  (the specification `metadata` block plus the entity's stable-ID references).
- Entity types without a database model (currently `Event`) are counted as `unsupported`.
- Tables are created idempotently (`Base.metadata.create_all`) so a fresh SQLite file works
  out of the box; PostgreSQL normally receives its schema via Alembic.

Every action (insert, update, skip, rejection) is logged via the `tl_importer.*` loggers.

## CLI

```bash
uv run tl-import                      # import into PostgreSQL AND SQLite (default: both)
uv run tl-import --validate-only      # validate + compile only, no database access
uv run tl-import --database postgres  # PostgreSQL only
uv run tl-import --database sqlite    # SQLite only
uv run tl-import --database both      # both databases
```

Options: `--specs DIR`, `--schemas DIR`, `--postgres-url URL` (default: `TL_DATABASE_URL`
env var or the local dev default), `--sqlite-url URL` (default:
`sqlite:///build/tl-ai.sqlite3`), `--report PATH` (default: `build/import_report.json`).

Exit codes: `0` on success (downgrade rejections are reported, not fatal), `1` when
validation fails — no database is touched in that case.

## Import Report (`build/import_report.json`)

- `generatedAt`, `provider`, `jobId`, `specificationsDir`, `documentsScanned`, `validateOnly`
- `validation` — the full tl_compiler validation report (issues, error/warning counts)
- `entityCount` — number of IR entities (present when validation passed)
- `databases` — one entry per target: `database`, `dialect`, `inserted`, `updated`,
  `skipped`, `rejectedDowngrades`, `unsupported`, `errors`, and per-entity `entities`
  actions with `fromVersion`/`toVersion`.

## Tests

`tests/importer/test_manual_import.py` covers: empty specifications, invalid YAML, invalid
reference, duplicate stable ID, valid SQLite import, re-import (skip), version upgrade,
version downgrade rejection, validate-only, CLI import, and PostgreSQL import (skipped
automatically when PostgreSQL is unreachable).
