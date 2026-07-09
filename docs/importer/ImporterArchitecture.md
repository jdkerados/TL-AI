# TL-AI Importer Architecture

The import framework (`src/tl_importer`) defines the architecture for bringing Throne & Liberty
data into TL-AI. This milestone delivers **only the framework**: interfaces, data model, and
pipeline orchestration. There is no scraping, no external API access, no Playwright usage, and
no data import.

Scope of this milestone: **Epic** and **Heroic** content only.

## Pipeline

```
Source (Provider)          fetches SourceDocument
        │
        ▼
Parser                     SourceDocument -> RawEntity (provider-specific shape)
        │
        ▼
Normalizer                 RawEntity -> NormalizedEntity (canonical TL-AI shape)
        │                  (uses declarative mapping/ rules)
        ▼
Validator                  NormalizedEntity -> ValidationReport
        │
        ▼
Compiler                   validated entities staged as YAML specifications
        │                  (TL Compiler, AD-15/AD-21 — runtime never reads YAML, AD-20)
        ▼
Database                   compiled results persisted via tl_database
```

The Compiler and Database stages are represented by the `EntityImporter` interface; concrete
implementations arrive in a later milestone.

## Data Model (`models.py`)

| Class | Role |
|---|---|
| `ImportJob` | A request: provider, entity types, rarities, parameters |
| `ImportContext` | Execution context for all stages (job, specs dir, dry-run, options) |
| `ImportResult` | Aggregated run outcome: status, stage counters, reports, errors |
| `SourceDocument` | A fetched document (provider, URI, content type, content, metadata) |
| `RawEntity` | Entity extracted from a document, still in provider-specific shape |
| `NormalizedEntity` | Entity in canonical shape (stable ID, type, rarity, payload, references) |
| `ValidationReport` | Per-entity issues with error/warning severity |
| `EntityType` | Weapon, Armor, Accessory, Skill, SkillCore, Trait, Buff, SetBonus, Monster, Boss, Npc |
| `Rarity` | Epic, Heroic |
| `ImportStatus` | success, partial, failed |

`SourceDocument`, `RawEntity`, `NormalizedEntity`, `ImportJob`, and `ImportContext` are frozen
dataclasses: pipeline data is immutable.

## Interfaces (No Concrete Implementations)

| Interface | Package | Contract |
|---|---|---|
| `Provider` | `providers/` | `name`, `supports(entity_type)`, `fetch(context) -> Iterator[SourceDocument]` |
| `WikiProvider`, `QuestlogProvider`, `MaxrollProvider`, `YoutubeProvider`, `ManualProvider` | `providers/` | Named provider interfaces extending `Provider` |
| `Parser` | `parsers/` | `can_parse(document)`, `parse(document, context) -> Iterator[RawEntity]` |
| `Normalizer` | `normalizers/` | `entity_type`, `normalize(raw, context) -> NormalizedEntity` |
| `ImportValidator` | `validators/` | `validate(entity, context) -> ValidationReport` |
| `EntityMapper` + `MappingRule` | `mapping/` | Declarative field mapping from provider shape to canonical shape |
| `EntityImporter` | `importers/` | `persist(entities, context) -> int` (Compiler + Database handoff) |

All interfaces are `abc.ABC` with abstract members only; none can be instantiated.

## ImportPipeline (`pipeline/`)

`ImportPipeline` is the single concrete class of the framework: pure orchestration over injected
interfaces (dependency injection, zero magic):

- Iterates provider documents, counts every stage.
- Skips documents the parser cannot handle (recorded as errors).
- Collects one `ValidationReport` per normalized entity.
- Persists only valid entities, and only when `ImportContext.dry_run` is `False`
  (dry-run is the default).
- Status: `success` (no invalid entities), `partial` (some invalid or document errors),
  `failed` (entities produced but none valid).

## CLI (`cli/`)

`tl-importer info` prints the supported entity types, rarities, and provider interfaces.
No import command exists yet, by design.

## Staging + Validation

Imported entities always enter the corpus with `metadata.status: staging` and pass the full
validation workflow (AD-19) before promotion. Rarities outside Epic/Heroic are out of scope
for this milestone.

## Tests

`tests/importer/` validates only the architecture:

- data model invariants (entity types, rarities, immutability, report severity logic),
- every interface is abstract and cannot be instantiated, with the expected abstract members,
- pipeline orchestration semantics (stage counts, dry-run, status transitions) using in-memory
  test doubles.
