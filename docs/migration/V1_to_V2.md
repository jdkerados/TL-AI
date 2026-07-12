# Migration: Entity Model V1 → V2

Date: 2026-07-12. All 37 specifications, all 15 JSON Schemas, the compiler, the importer,
and the database schema were migrated to Entity Model V2 (`docs/architecture/EntityModelV2.md`).
Stable IDs were **not** changed; every V2 entity was imported as a semantic-version upgrade
(1.x → 2.0.0) over the existing V1 rows.

## Envelope changes (all entity types)

| V1 | V2 |
|---|---|
| `name` (PascalCase, doubled as display name) | `internalName` (PascalCase, must match file name) + `displayName` (human-readable) |
| — | `localizationKey` (optional) |
| — | `flavorText` (optional) |
| freeform `effects`/`stats` strings | strongly typed `StatModifier` (`attribute` enum × `modifier` Flat/Percent × numeric `value`) |
| `version: 1.x` | `version: 2.0.0` |

## Type-specific changes

- **Items** (`Weapon`/`Armor`/`Accessory`): added `itemLevel`, `requirement`, typed `baseStats`,
  `traitPool` (references validated against the trait's `appliesTo`), `maxTraitSlots`, `acquisition`.
  Items no longer reference sets; membership lives on the set side.
- **Weapon**: `weaponType` enum. **Armor**: `armorType` + `slot` enums. **Accessory**: `slot` enum.
- **Trait**: added `traitCategory`, `appliesTo`, and `effects` as `RarityScaledModifier`
  (`valuesByRarity` keyed by rarity).
- **Skill**: `skillType` Active/Passive discriminates required fields (`timing`/`cost`/`targeting`
  vs `passiveEffects`); added typed `damage`, `appliesBuffs`/`appliesDebuffs`.
- **SkillCore**: entity `type` unchanged; added `coreType` enum, typed `skills` references, typed `effects`.
- **Set → SetBonus**: entity `type` renamed to `SetBonus` (stable IDs keep the `tl.set.*` category);
  `members` is the canonical relationship; `bonuses` are per-piece-count `PieceBonus` objects.
- **Buff**: `buffCategory`, `dispellable`, `maxStacks`, `duration` xor `permanent`, typed
  `modifiers`/`tick`/`crowdControl`.
- **Monster/Boss**: `grade`, `family`, typed `combatStats`, typed `drops`; Boss adds
  `encounterType`, `peaceMode`, `mechanics`.

## Toolchain changes

- **Schemas**: `entity.schema.json` requires the V2 envelope; `common.schema.json` carries the
  shared `$defs` (attributes, modifiers, typed references per category). Leaf schemas are closed
  with `unevaluatedProperties: false`; base schemas (`entity`, `item`) stay open.
- **Compiler**: file names validated against `internalName`; new semantic checks
  `SET_PIECES_EXCEED_MEMBERS`, `SET_PIECES_NOT_INCREASING`, `DROP_QUANTITY_INVALID`; new reference
  check `TRAIT_NOT_APPLICABLE`. IR/manifest now carry `internalName`, `displayName`, `rarity`.
- **Database**: Alembic revision `b7c2d4e6f8a1` adds `entities.display_name`, `entities.rarity`
  (both indexed) and `entities.payload` (full spec JSON, JSONB on PostgreSQL).
- **Importer**: stores the new columns and populates the association tables (`item_traits`,
  `set_bonus_items`, `skill_buffs`, `skill_core_skills`, `monster_skills`) from the canonical
  relationship fields on every import (idempotent delete-and-reinsert per owner).

## How to re-run

```powershell
uv run alembic upgrade head   # apply b7c2d4e6f8a1
uv run tl-ai validate         # 37 files, 0 errors
uv run tl-import              # upsert + link relationships into PostgreSQL and SQLite
uv run tl-stats               # regenerate build/database_statistics.json
```
