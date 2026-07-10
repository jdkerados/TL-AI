# Initial Epic & Heroic Dataset

The first production dataset of TL-AI: manually curated YAML specifications for Throne &
Liberty **Epic** and **Heroic** content, imported through the Manual Provider. No scraping,
no Playwright, no external APIs, no automatic import.

## Patch Version

All entities target game patch **1.2** and start at specification version **1.0.0** with
`metadata.status: validated`.

## Included Content (37 entities)

| Entity type | Count | Rarities |
|---|---|---|
| Weapons | 8 | 6 Epic, 2 Heroic |
| Armor | 6 | 4 Epic, 2 Heroic |
| Accessories | 4 | 3 Epic, 1 Heroic |
| Traits | 8 | 8 Epic |
| Set Bonuses | 2 | 2 Epic |
| Skills | 6 | 4 Epic, 2 Heroic |
| Skill Cores | 3 | 2 Epic, 1 Heroic |

Highlights:

- **Weapons**: world-boss Epic weapons (Adentus's Gargantuan Greatsword, Nirma's Sword of
  Echoes, Karnix's Netherbow, Talus's Crystalline Staff, Excavator's Mysterious Scepter,
  Minezerok's Daggers of Crippling) plus Heroic Resistance crafted weapons.
- **Armor & sets**: Shock Commander (plate) and Arcane Shadow (cloth) Epic set pieces with
  their `Set` entities, plus Heroic Resistance pieces.
- **Traits**: the core item traits referenced by every item (Critical Hit Chance, Heavy
  Attack Chance, Hit Chance, Max Health, Attack Speed, Cooldown Speed, Mana Regen,
  Melee Evasion).
- **Skills & cores**: weapon skills (Gigantic Impact, Guillotine Blade, Zephyr's Nock,
  Strafing, Judgment Lightning, Curse Explosion) grouped by three skill cores.

All cross-references (item → trait, item → set, set → item, core → skill) resolve inside
the corpus.

Every entity carries: StableId, Name, EntityType, **Rarity**, Metadata, PatchVersion,
SemanticVersion. The `rarity` field was added to the item/trait/set/skill/skill-core schemas
(`common.schema.json#/$defs/Rarity`, enum `Epic`/`Heroic` for Milestone M1) and is required.

## Excluded Content (by design, this milestone)

- Monsters, Bosses, NPCs
- Buffs, Events, Formulas
- Any rarity other than Epic and Heroic

## Verification & Import Statistics

Verified end to end:

1. **Compiler validation**: `uv run tl-ai validate` — 37 files, 0 errors, 0 warnings.
2. **IR generation**: `uv run tl-ai compile` — 37 entities in `build/ir.json` +
   `build/build_manifest.json`.
3. **PostgreSQL import**: `uv run tl-import --database both` — 37 inserted, 0 updated,
   0 skipped, 0 downgrades rejected, 0 unsupported.
4. **SQLite import**: same run — 37 inserted into `build/tl-ai.sqlite3`.

Reports (generated, git-ignored under `build/`):

- `build/import_report.json` — full per-entity import actions for both databases.
- `build/database_statistics.json` — generated with `uv run tl-stats`:

| Statistic | PostgreSQL | SQLite |
|---|---|---|
| Weapon count | 8 | 8 |
| Armor count | 6 | 6 |
| Accessory count | 4 | 4 |
| Skill count | 6 | 6 |
| Skill Core count | 3 | 3 |
| Trait count | 8 | 8 |
| Set Bonus count | 2 | 2 |
| **Total** | **37** | **37** |

All entities are stored with `is_validated = true`, their metadata (including rarity and
references), `patch_version = "1.2"`, and `semantic_version = "1.0.0"`.

## Reproducing

```bash
uv run tl-ai validate            # compiler validation
uv run tl-ai compile             # IR + build manifest
uv run tl-import --database both # PostgreSQL + SQLite import + import report
uv run tl-stats --database both  # database statistics
```
