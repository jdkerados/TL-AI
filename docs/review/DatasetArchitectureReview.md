# Dataset Architecture Review (T011A)

Review of the TL-AI dataset architecture as of commit `548df16`
(`feat(dataset): initial epic heroic dataset`), before population of the complete
Throne & Liberty dataset. Scope: database model, YAML model, JSON Schemas, stable IDs,
naming, relationships, gaps, scalability, normalization, AI and Simulator compatibility.

**Review only — no code, schema, or database changes were made.**

Severity scale: **Critical** (blocks the stated goal), **High** (causes rework of every
entity authored after this point), **Medium** (causes friction/debt, fixable later without
mass rework), **Low** (cosmetic or deferred by design).

---

## 1. Database Model

Current state: joined-table inheritance rooted at `entities` with 14 concrete models,
UUID PKs, unique indexed `stable_id`, `semantic_version`, `patch_version`, `is_validated`,
JSONB `metadata`, pgvector `embedding`, timestamps, 9 association tables, `patches` and
`sources` tables. Dual-dialect (PostgreSQL/SQLite) verified.

Overall sound and aligned with AD-12. Issues:

### Issue DB-1 — Association tables exist but are never populated
- **Severity**: High
- **Reason**: The importer stores references only as strings inside the JSONB `metadata`
  column (`meta.references`). `item_traits`, `set_bonus_items`, `skill_core_skills`, etc.
  stay empty. The relational model and the actual data diverge.
- **Suggested solution**: In the importer, resolve references after all inserts (second
  pass) and populate the association tables; keep `meta.references` as provenance only.
- **Impact if unchanged**: Every relational query ("items with trait X", "set members")
  requires JSON containment operators; SQLite/PostgreSQL JSON semantics differ; the API
  (M4) and Simulator will be built on JSON string matching instead of joins. Rework cost
  grows with every imported entity.

### Issue DB-2 — Rarity is not a first-class column
- **Severity**: High
- **Reason**: Rarity is mandatory in the YAML model but stored only as `meta.rarity`
  (JSON). It is a primary filter dimension for the whole product (builds, statistics,
  API queries).
- **Suggested solution**: Add an indexed `rarity` column on `entities` (nullable for
  types without rarity) via an Alembic migration; keep JSON copy for provenance.
- **Impact if unchanged**: Rarity filtering and statistics require dialect-specific JSON
  queries; no index support; statistics tooling (e.g. per-rarity counts) stays ad hoc.

### Issue DB-3 — Database storage is lossy relative to the specifications
- **Severity**: Medium
- **Reason**: Only name/description/versions/metadata are persisted. The full payload
  (e.g. future numeric fields) is not stored, while AD-20 mandates the runtime reads
  artifacts/DB, never YAML. Today DB consumers cannot reconstruct an entity.
- **Suggested solution**: Persist the full canonical payload (JSONB `payload` column or
  guarantee `build/ir.json` is a runtime artifact with equal standing).
- **Impact if unchanged**: Runtime features will silently depend on re-reading YAML or IR
  files, violating AD-20, or require re-import after every consumer change.

### Issue DB-4 — `patches`/`sources` tables are dead
- **Severity**: Low
- **Reason**: `patch_version` is a free string on `entities`; no `Patch` rows exist and
  `source_id` is never set, although `metadata.source` exists in every YAML.
- **Suggested solution**: Importer creates/links `Patch` and `Source` rows.
- **Impact if unchanged**: No referential integrity on patches; provenance queries
  impossible; harmless short-term.

### Issue DB-5 — No version history
- **Severity**: Medium
- **Reason**: Upsert keeps exactly one row per stable ID. AD-24 declares specifications
  immutable and versioned, but the DB forgets superseded versions.
- **Suggested solution**: Either declare Git as the canonical history (document it) or
  add an `entity_versions` history table.
- **Impact if unchanged**: "What changed in patch X" queries impossible from the DB;
  acceptable if Git remains the source of truth, but it is currently undocumented.

### Issue DB-6 — `Event` type has a schema but no database model
- **Severity**: Low (deferred content)
- **Reason**: `event.schema.json` and the compiler category exist; the importer counts
  events as `unsupported`.
- **Suggested solution**: Add an `Event` model before events enter scope.
- **Impact if unchanged**: Events silently skipped on import.

## 2. YAML Model

### Issue YM-1 — No display names (identity conflated with presentation)
- **Severity**: **Critical** (for population)
- **Reason**: `name` must be PascalCase and equal the file name. The real in-game name
  ("Adentus's Gargantuan Greatsword", with spaces and apostrophes) survives only inside
  free-text `description`. The complete dataset is *game data*; losing exact display
  names breaks search, UI, AI grounding, and any mapping back to the game.
- **Suggested solution**: Add a required `displayName` (free string) to the entity schema
  (or a `localizationKey` into `specifications/localization/`); keep PascalCase `name`
  as technical identifier.
- **Impact if unchanged**: Every one of the thousands of entities authored during full
  population must be edited later to add the display name — maximal rework.

### Issue YM-2 — No numeric/gameplay attributes exist anywhere
- **Severity**: **Critical** (for Simulator), High (for population sequencing)
- **Reason**: Schemas only allow identity + references. Items have no damage/defense/
  item level/level requirement; skills have no cooldown/cost/cast time/coefficients;
  traits have no magnitudes per rarity; sets have no piece-count thresholds
  (2/4-piece bonuses). A "complete dataset" without these is a name catalog.
- **Suggested solution**: Before mass population, extend schemas with typed attribute
  blocks per entity type (e.g. `stats`, `weaponType`, `slot`, `requiredLevel`,
  `cooldown`, `bonuses: [{pieces, effect}]`), backed by the Stat entity catalog.
- **Impact if unchanged**: Full re-authoring of the entire dataset once the Formula
  Engine/Simulator (M5) needs numbers; the Simulator cannot compute anything.

### Issue YM-3 — Rarity enum is limited to Epic/Heroic
- **Severity**: High
- **Reason**: Deliberate M1 scope, but the *complete* Throne & Liberty dataset includes
  other tiers (e.g. Rare/blue gear and higher-tier Epic/archboss variants). The enum in
  `common.schema.json` will reject them.
- **Suggested solution**: Decide the full rarity taxonomy now (one-line enum change when
  scope opens); document that Epic/Heroic is a content gate, not a data-model limit.
- **Impact if unchanged**: Hard validation failures the moment out-of-scope content is
  added; trivial to fix, but the taxonomy decision should precede mass authoring.

### Issue YM-4 — No item classification fields
- **Severity**: High
- **Reason**: Weapon class (greatsword/longbow/…), armor weight (plate/leather/cloth)
  and slot (head/chest/…), accessory slot (necklace/ring/…) live only in free-form
  `metadata.tags`. Tags are unvalidated and unqueryable in a typed way.
- **Suggested solution**: Add typed enums: `weaponType` on Weapon, `armorType` + `slot`
  on Armor, `slot` on Accessory.
- **Impact if unchanged**: Build-crafting logic (two weapons, one item per slot) is
  impossible to express; every item file needs later editing (same rework class as YM-1).

## 3. JSON Schemas

Strengths: Draft 2020-12, composition via `allOf` + `unevaluatedProperties: false`,
shared `common.schema.json`, per-type ID pattern narrowing, metadata workflow enum.

### Issue JS-1 — References are not type-constrained
- **Severity**: Medium
- **Reason**: `traits: [tl.skill.strafing]` validates — `ReferenceList` accepts any
  stable ID; the cross-reference validator checks existence only, not target type.
- **Suggested solution**: Per-field ID patterns (e.g. `^tl\.trait\.` inside `traits`)
  or a target-type check in the compiler's reference validator.
- **Impact if unchanged**: Silent wrong-type links at scale; import would store them and
  relationship population (DB-1) would fail late instead of at validation time.

### Issue JS-2 — `Set` (schema/type) vs `SetBonus` (DB/task vocabulary) mismatch
- **Severity**: Medium
- **Reason**: YAML type is `Set` with `tl.set.*` IDs; the database model and milestone
  vocabulary say "Set Bonus" (`set_bonuses` table, importer maps `"Set" → SetBonus`).
  Two names for one concept violates Zero Magic (AD-23) in spirit.
- **Suggested solution**: Pick one term (recommend `SetBonus` everywhere or rename the
  DB model to `Set`); do it before mass population while only 2 set files exist.
- **Impact if unchanged**: Permanent bilingual naming in queries, docs, and AI prompts;
  stable IDs make later renames of `tl.set.*` impossible.

## 4. Stable IDs

Format `tl.<category>.<identifier>` is enforced end-to-end (schema pattern, compiler
category-prefix check, DB CHECK constraint, uniqueness at compile and DB level). Good.

### Issue SI-1 — Category set is frozen by directory mapping only
- **Severity**: Low
- **Reason**: `tl_compiler.config.CATEGORIES` is the single source of the taxonomy —
  good — but new content areas (see §7) require code edits.
- **Suggested solution**: None needed now; keep the mapping explicit (Zero Magic).
- **Impact if unchanged**: None; noted for awareness.

## 5. Naming Conventions

PascalCase names, file = `<Name>.yaml`, snake_case identifiers in IDs — consistent and
machine-checked. The one structural problem is YM-1 (no display names). Additionally:

### Issue NC-1 — Name uniqueness is not enforced
- **Severity**: Medium
- **Reason**: Two entities of different categories may share `name` (file names only
  collide within one directory). Real T&L data has near-duplicate names; PascalCase
  collapsing ("ResistanceGreatsword" from several similar blues) will collide *within*
  a directory at scale.
- **Suggested solution**: Define a deterministic naming rule for collisions (suffix with
  tier/level) and consider a corpus-wide uniqueness warning in the compiler.
- **Impact if unchanged**: Ad hoc names invented during population; inconsistent corpus.

## 6. Entity Relationships

Modeled: item→traits, item→sets, set→members, skill→buffs, core→skills, monster→skills,
trait→stats, buff→stats, formula→stats. Two gaps beyond DB-1/JS-1:

### Issue ER-1 — Bidirectional references are duplicated by hand
- **Severity**: Medium
- **Reason**: Armor lists `sets: [tl.set.shock_commander]` *and* the set lists
  `members: [...]`. Nothing validates symmetry.
- **Suggested solution**: Declare one side canonical (recommend set→members) or add a
  compiler symmetry check.
- **Impact if unchanged**: Drift between the two sides at scale; conflicting data with
  no error.

### Issue ER-2 — No acquisition relationships
- **Severity**: Medium (future scope)
- **Reason**: There is no way to express "dropped by Adentus", "crafted from X",
  "bought with Y" — boss→loot exists only as prose in descriptions.
- **Suggested solution**: Plan a `drops`/`acquisition` reference model for when monsters
  and bosses enter scope.
- **Impact if unchanged**: Descriptions become unstructured data that must be re-mined.

## 7. Missing Entity Types

For the *complete* game dataset, the current taxonomy lacks (severity **Medium**,
deliberate scope for most): **Stats catalog** (referenced by traits today — zero stat
entities exist, making `trait.stats` unusable), Buffs/Debuffs (schema exists, excluded),
Weapon Masteries, Runes/Artifacts, Consumables (potions/food/scrolls), Crafting
materials & recipes, Lithographs, Guardians, Amitoi, Morphs, Zones/Dungeons (world),
Quests, Currencies.
- **Reason**: M1 scope; but stats are a *dependency of already-imported traits*.
- **Suggested solution**: Author the Stat catalog first in the next population step;
  schedule the rest per milestone.
- **Impact if unchanged**: Traits stay semantically empty; every downstream consumer
  (Formula Engine, Simulator) blocks on stats.

## 8. Missing Attributes

Consolidated from YM-1/2/4 (details there): `displayName`/localization key (all),
`itemLevel`/`tier`/`requiredLevel`/`weaponType`/`armorType`/`slot`/base stats (items),
trait magnitudes per rarity, skill mechanics (cooldown, cost, cast time, range, damage,
weapon binding, active/passive, specializations), set piece thresholds, drop sources.
Severity **Critical→High** as itemized above.

## 9. Scalability to the Complete Dataset

- File-per-entity + in-memory compilation: fine for the expected corpus (thousands of
  files; current pipeline is O(n) with n·refs lookups against a dict).
- **Issue SC-1 — Reference collection by pattern-matching every string**
  - **Severity**: Low
  - **Reason**: Any string matching `tl.<cat>.<id>` anywhere (including descriptions)
    is a reference. A description quoting an ID creates a phantom edge.
  - **Suggested solution**: Restrict collection to known reference fields once JS-1 is
    addressed.
  - **Impact if unchanged**: Rare false-positive references; low probability, confusing
    when it happens.
- **Issue SC-2 — Importer does one SELECT per entity**
  - **Severity**: Low
  - **Reason**: N+1 upsert pattern; fine to ~10k entities, slow beyond.
  - **Suggested solution**: Batch-prefetch existing stable IDs per run.
  - **Impact if unchanged**: Minutes-long imports at large scale; no correctness issue.
- Schema evolution: adding *required* fields (YM-1/2/4) invalidates existing files —
  doing it **now**, at 37 files, is cheap; after full population it is a mass migration.
  This is the central sequencing argument of this review.

## 10. Normalization Improvements

Recommended (consolidates earlier issues): promote `rarity` to a column (DB-2); populate
association tables (DB-1); introduce the Stat catalog and give `trait_stats` magnitude
columns (association object, not bare m2m); link `patches`/`sources` (DB-4); persist the
full payload (DB-3); unify Set/SetBonus vocabulary (JS-2). No over-normalization is
advised: JSONB metadata for provenance is appropriate.

## 11. Future AI Compatibility

Positive: pgvector `embedding` (1024-d, matches a local embedding model) already on
every entity; stable IDs are ideal grounding anchors for RAG citations; descriptions
exist on all 37 entities; deterministic versioning supports cache invalidation.

- **Issue AI-1 — Text quality is thin for retrieval**
  - **Severity**: Medium
  - **Reason**: One-line descriptions and PascalCase names limit embedding quality;
    display names (YM-1) are the biggest single win for lexical + semantic search.
  - **Suggested solution**: Fix YM-1; adopt a description style guide (mechanics, source,
    usage) during population; embed `displayName + description + typed attributes`.
  - **Impact if unchanged**: Weak retrieval precision; AI answers grounded on IDs users
    do not recognize.

## 12. Future Simulator Compatibility

Positive: event-driven simulator (AD-16) needs deterministic, versioned, typed data —
stable IDs, semver, and the compiler pipeline provide exactly that skeleton.

- **Issue SIM-1 — Nothing to simulate yet** (= YM-2 from the simulator's viewpoint)
  - **Severity**: Critical for M5, expected at M1
  - **Reason**: No stats, no formulas, no skill mechanics, no trait magnitudes.
  - **Suggested solution**: Define the numeric attribute schemas *before* mass
    population so data is authored once; author the Stat catalog + Formula entities in
    the next milestones.
  - **Impact if unchanged**: The complete dataset would need a second full authoring
    pass; the Simulator milestone inherits a data debt equal to the entire corpus.

---

## Issue Summary

| # | Issue | Severity |
|---|---|---|
| YM-1 | No display names in the YAML model | **Critical** |
| YM-2 / SIM-1 | No numeric/gameplay attributes anywhere | **Critical** |
| DB-1 | Association tables never populated | High |
| DB-2 | Rarity not a first-class DB column | High |
| YM-3 | Rarity enum limited to Epic/Heroic | High |
| YM-4 | No typed item classification (weapon type, slot, armor weight) | High |
| DB-3 | DB storage lossy vs specifications (AD-20 risk) | Medium |
| DB-5 | No version history in DB | Medium |
| JS-1 | References not type-constrained | Medium |
| JS-2 | Set vs SetBonus vocabulary split | Medium |
| NC-1 | Name uniqueness/collision rule undefined | Medium |
| ER-1 | Unvalidated bidirectional references | Medium |
| ER-2 | No acquisition/drop relationships | Medium |
| §7 | Stat catalog missing (trait dependency) | Medium |
| AI-1 | Thin text for retrieval | Medium |
| DB-4 | patches/sources tables unused | Low |
| DB-6 | Event type lacks DB model | Low |
| SC-1 | Pattern-based reference collection | Low |
| SC-2 | N+1 import queries | Low |
| SI-1 | Category taxonomy in code | Low |

## Verdict

# **NO GO**

**for mass population in the current shape** — with a short, cheap unblock path.

The pipeline itself (compiler → IR → dual-DB import) is proven and healthy; nothing
found invalidates the architecture. But two Critical and four High issues are all of the
form *"every entity authored from now on will have to be edited again"*:

1. **YM-1** — add `displayName` (or localization key) to the entity schema.
2. **YM-2/YM-4** — define the typed attribute blocks (item classification, stats,
   skill mechanics, set thresholds) before authoring thousands of files.
3. **YM-3** — settle the full rarity taxonomy.
4. **DB-1/DB-2** — make the importer populate relationships and promote rarity to a
   column, so the DB is queryable relationally from day one.

At 37 entities these fixes cost hours; after full population they cost a full re-author
of the corpus. Once items 1–4 are addressed (a single focused task), the verdict flips
to **GO** without reservation.
