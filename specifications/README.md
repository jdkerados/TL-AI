# TL-AI Specifications

This directory contains the YAML specification corpus for Throne & Liberty — the single model
of the game domain (see `docs/MASTER_SPECIFICATION.md`, AD-11/AD-12). Everything else in the
platform is derived from these files: the TL Compiler validates them against the JSON Schemas
in `schemas/` and generates the runtime artifacts. **The runtime never reads YAML** (AD-20).

## Directory Layout

| Directory | Content | Schema |
|---|---|---|
| `entities/` | Generic entities | `entity.schema.json` |
| `items/weapons/` | Weapons | `weapon.schema.json` |
| `items/armor/` | Armor | `armor.schema.json` |
| `items/accessories/` | Accessories | `accessory.schema.json` |
| `skills/` | Skills | `skill.schema.json` |
| `skill_cores/` | Skill cores | `skill_core.schema.json` |
| `traits/` | Traits | `trait.schema.json` |
| `buffs/` | Buffs/debuffs | `buff.schema.json` |
| `monsters/` | Monsters | `monster.schema.json` |
| `bosses/` | Bosses | `boss.schema.json` |
| `npc/` | NPCs | `npc.schema.json` |
| `sets/` | Item sets | `set.schema.json` |
| `formulas/` | Mathematical formulas | `formula.schema.json` |
| `stats/` | Stat definitions | `stat.schema.json` |
| `events/` | Simulator events | `event.schema.json` |
| `world/` | World data | — (schema to be defined) |
| `localization/` | Localization catalogs | — (schema to be defined) |
| `patches/` | Game patch records | — (schema to be defined) |
| `validation/` | Validation reports and staging artifacts | — |

## One Entity per File

Each YAML file defines **exactly one entity** (AD-25). No lists of entities, no multi-document
YAML files. The file lives in the directory matching its entity type.

## Naming Convention

- **Entity names** use **PascalCase** (AD-27): `LongswordOfSolisium`, not `longsword_of_solisium`.
- **File names** match the entity name: `LongswordOfSolisium.yaml`.
- **Files use the `.yaml` extension** (not `.yml`).
- **Stable IDs** use lowercase `snake_case` segments (see below) and never change, even if the
  display name changes.

## Stable IDs

Every entity has a permanent identifier (AD-26) with the format:

```
tl.<category>.<identifier>
```

- `<category>` is the entity category (`weapon`, `armor`, `accessory`, `skill`, `skill_core`,
  `trait`, `buff`, `monster`, `boss`, `npc`, `set`, `formula`, `stat`, `event`, `item`, `entity`).
- `<identifier>` is lowercase `[a-z0-9_]+`.
- IDs are **never recycled** and **never renamed**. All cross-entity references use stable IDs
  only — never names.

## Versioning

- Every specification carries a `version` field using semantic versioning (`MAJOR.MINOR.PATCH`).
- **Specifications are immutable** (AD-24): once a version is published (merged to `main`), that
  version is never edited. Any change — even a typo fix — produces a new version.
- Version semantics:
  - **MAJOR** — breaking structural change of the entity.
  - **MINOR** — backward-compatible addition.
  - **PATCH** — correction with no structural change.

## Patch Management

- Every specification carries a `patch` field identifying the Throne & Liberty game patch the
  data applies to.
- When the game changes an entity in a new patch, a new specification version is created with
  the updated `patch` value; the previous version remains untouched (immutability).
- Game patch records are tracked under `patches/`.

## Validation Workflow

All content follows the **Staging + Validation workflow** (AD-19):

1. **Author or ingest** a specification with `metadata.status: staging`.
2. **Schema validation** — the file must validate against its JSON Schema
   (Draft 2020-12, in `schemas/`).
3. **Referential validation** — every referenced stable ID must exist.
4. **Review** — human review of the staged specification.
5. **Promotion** — `metadata.status` is set to `validated`; only validated specifications are
   compiled by the TL Compiler into runtime artifacts (AD-15, AD-21).

CI enforces schema validation on every push. Validation reports live under `validation/`.
