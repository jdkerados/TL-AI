# TL Compiler — Phase 1

The TL Compiler (`src/tl_compiler`) validates the YAML specification corpus and compiles it into
runtime artifacts. It implements AD-15 and AD-21 of `docs/MASTER_SPECIFICATION.md`: the compiler
is the **only** component that reads YAML; the runtime consumes generated artifacts exclusively
(AD-20).

Phase 1 scope: validation pipeline, Intermediate Representation (IR), and build manifest.
No Formula Engine, no Simulator, no AI, no database/code/documentation generation.

## Pipeline

```
specifications/*.yaml
        │
        ▼
1. YAML loader            (parser/)     one document per file, mapping at top level
        │
        ▼
2. JSON Schema validator  (validator/)  Draft 2020-12, schemas from schemas/
3. Stable ID validator    (validator/)  pattern + category prefix + uniqueness
4. Cross-ref validator    (validator/)  every referenced stable ID must exist
5. Semantic validator     (validator/)  type ↔ directory, file name ↔ entity name
        │
        ▼
6. IR builder             (ir/)         frozen dataclasses, sorted by stable ID
        │
        ▼
7. Generators             (generators/) build/ir.json + build/build_manifest.json
```

The `resolver/` package builds the stable-ID index and collects references.

## Directory ↔ Schema Mapping

Each specification directory maps to one schema, one expected `type`, and one stable-ID
category prefix (see `src/tl_compiler/config.py`). Directories without a schema yet
(`world/`, `localization/`, `patches/`, `validation/`) produce a `NO_SCHEMA` **warning**.

## Reference Rule (Zero Magic)

Any string value anywhere in a specification document that matches the stable-ID pattern
`tl.<category>.<identifier>` is treated as a reference to another entity. The entity's own
top-level `id` is not a reference. Every reference must resolve, or validation fails with
`REF_UNRESOLVED`.

## Issue Codes

| Code | Severity | Meaning |
|---|---|---|
| `PARSE_ERROR` | error | Unreadable file, invalid YAML, multi-document, non-mapping, `.yml` extension |
| `SCHEMA_INVALID` | error | JSON Schema violation |
| `SCHEMA_MISSING` | error | Mapped schema file not found in `schemas/` |
| `ID_PATTERN` | error | `id` does not match `tl.<category>.<identifier>` |
| `ID_CATEGORY_MISMATCH` | error | `id` category prefix does not match the directory |
| `ID_DUPLICATE` | error | Stable ID defined in more than one file |
| `REF_UNRESOLVED` | error | Referenced stable ID does not exist |
| `TYPE_MISMATCH` | error | `type` does not match the directory's expected type |
| `FILENAME_MISMATCH` | error | File name does not match the entity `name` |
| `NO_SCHEMA` | warning | Directory has no schema mapping yet |

## CLI

```bash
# Validate the corpus and write build/validation_report.json
uv run tl-ai validate

# Compile: validate, then write build/ir.json and build/build_manifest.json
uv run tl-ai compile
```

Options (both commands): `--specs DIR` (default `specifications/`), `--schemas DIR`
(default `schemas/`). `validate` accepts `--report PATH`; `compile` accepts `--output DIR`
(default `build/`). Exit code `0` on success, `1` when validation errors exist.
`compile` aborts before generating artifacts if validation fails.

All outputs are written to `build/`, which is git-ignored: artifacts are generated, never
committed.

## Artifacts

### `build/validation_report.json`

`compilerVersion`, `generatedAt`, `specificationsDir`, `schemasDir`, `filesScanned`, `valid`,
`errorCount`, `warningCount`, and the list of `issues` (`severity`, `code`, `file`, `message`).

### `build/ir.json`

The full IR: one record per entity with `stableId`, `type`, `name`, `version`, `patch`,
`status`, `sourcePath`, `references`, and the complete `payload`.

### `build/build_manifest.json`

`compilerVersion`, `generatedAt`, `specificationsDir`, `entityCount`, `entityCounts` per type,
`artifacts`, and one entry per entity with its `sha256` source hash and `references`.

## Tests

Unit tests live in `tests/compiler/` and cover the parser, all validators, the IR builder,
the manifest generator, and both CLI commands:

```bash
uv run pytest tests/compiler
```
