# Entity Model V2 — Canonical Throne & Liberty Entity Model

**Status**: Design (T011B). No code, schemas, database, or dataset were modified.
This document is the definitive reference for every future YAML specification. It
supersedes the implicit V1 model and resolves the Critical/High findings of
`docs/review/DatasetArchitectureReview.md` (YM-1, YM-2, YM-3, YM-4, JS-1, JS-2, ER-1).

---

## 1. Design Principles

1. **Strongly typed everywhere** — no generic `value`/`data`/`extra` fields. Every
   gameplay number is attached to a named attribute from the closed catalog in §6.
2. **Author once** — the model must carry the complete game dataset so no entity is
   ever re-authored for a later milestone.
3. **Identity ≠ presentation** — technical names (PascalCase) are permanent; display
   text is data (YM-1).
4. **One canonical side per relationship** — no hand-maintained mirrors (ER-1).
5. **Typed references** — every reference field declares the entity category it may
   point to (JS-1).
6. **Zero Magic (AD-23)** — all enums are closed and listed in this document; the
   compiler rejects anything outside them.

## 2. Common Entity Envelope

Every entity of every type carries this envelope. Field order in YAML follows this
table (top-down) for human readability (AD-22).

| Field | Type | Required | Rules |
|---|---|---|---|
| `id` | StableId | yes | `tl.<category>.<snake_case>`; permanent, never recycled (AD-26) |
| `type` | enum | yes | Entity type constant (PascalCase) |
| `internalName` | PascalCaseName | yes | Technical identifier; **must equal the file name** (`<InternalName>.yaml`); unique per category |
| `displayName` | string (1–200) | yes | Exact in-game English name, free text ("Adentus's Gargantuan Greatsword") |
| `localizationKey` | LocalizationKey | no | Key into `specifications/localization/<lang>.yaml`; see §4 |
| `description` | string | yes | Factual, mechanical description (see §11 style rules) |
| `flavorText` | string | no | In-game lore/flavor text, verbatim if it exists |
| `version` | SemanticVersion | yes | Specification version; see §5.1 |
| `patch` | GamePatch | yes | Game patch the data was verified against; see §5.2 |
| `metadata` | Metadata | yes | `createdAt`, `status` (staging/validated), `author`, `source`, `tags`, `notes`, `updatedAt` |

Notes:

- V1's `name` is renamed to `internalName`. The V1 rule "name = file name" is retained
  for `internalName`.
- `displayName` collisions are allowed (the game has duplicates); `internalName`
  collisions within a category are not. Collision rule: suffix `internalName` with a
  distinguishing qualifier (`GreatswordOfDawnT2`), never invent a different display name.

## 3. Rarity and Grade Taxonomies

### 3.1 Rarity (items, traits, skills, skill cores, set bonuses)

Closed enum, full game taxonomy (fixes YM-3):

`Common`, `Uncommon`, `Rare`, `Epic`, `Epic2` (second-tier Epic / archboss gear),
`Heroic`, `Legendary`.

- Content *population* may still be gated (M1 = Epic + Heroic), but the **model**
  accepts the full taxonomy. Gating is a curation decision, not a schema constraint.
- `rarity` is **required** on: Weapon, Armor, Accessory, Trait, Skill, SkillCore,
  SetBonus. It is **forbidden** on: Buff, Monster, Boss, NPC.

### 3.2 Monster Grade (monsters and bosses only)

`Normal`, `Elite`, `Named`, `Boss`, `Archboss`.

## 4. Localization Strategy

- **English is canonical.** `displayName`, `description`, and `flavorText` in the
  entity file are the canonical English strings.
- `localizationKey` (optional) links the entity to translation catalogs:
  `specifications/localization/<lang>.yaml` (e.g. `de.yaml`), flat maps of
  `<localizationKey>.<field>` → translated string, where `<field>` ∈
  {`displayName`, `description`, `flavorText`}.
- Key format: `<category>.<identifier>` mirroring the stable ID
  (`weapon.adentus_gargantuan_greatsword`). Explicit, never derived at runtime.
- Validation: every `localizationKey` present in a catalog must belong to an existing
  entity; catalogs never introduce keys without entities.
- Localization catalogs are **out of scope for population** until a dedicated
  milestone; the model reserves the mechanism now so no entity changes later.

## 5. Versioning and Patch Management

### 5.1 Semantic Versioning (`version`)

- **PATCH** (`1.0.x`): typo fixes, metadata/tag changes, description clarifications.
  No gameplay meaning changes.
- **MINOR** (`1.x.0`): additive, backward-compatible data (new optional field filled,
  added trait in a pool, added localization key).
- **MAJOR** (`x.0.0`): gameplay values or relationships changed (game rebalance,
  mechanic rework), or removal of data.
- Published specifications are immutable (AD-24): any change = new version in Git.
  The database keeps the newest version only; **Git is the canonical version history**
  (resolves DB-5 by decision, documented here).
- The importer's rules remain: upsert by stable ID, update only on strictly newer
  version, downgrades rejected.

### 5.2 Game Patch (`patch`)

- `patch` records the game patch against which the data was last verified
  (`MAJOR.MINOR` or `MAJOR.MINOR.HOTFIX`, e.g. `1.2`, `2.0.1`).
- A game patch that changes an entity's data ⇒ MAJOR version bump + new `patch` value.
- A game patch that merely re-verifies unchanged data ⇒ MINOR bump + new `patch` value.
- A future compiler rule validates `patch` against a maintained list in
  `specifications/patches/` (one file per patch: id `tl.patch.<x_y>`, release date,
  summary). Until that exists, the regex constraint applies.

## 6. Gameplay Attributes Catalog

The closed, strongly-typed attribute enumeration. Every numeric gameplay value in any
entity references exactly one of these attributes — never a bare number with an ad hoc
name, never a generic `value` field without an attribute.

**Unit legend**: `flat` (absolute points), `pct` (percentage points, 0–100),
`sec` (seconds), `m` (meters), `pct_rate` (percentage that may exceed 100, e.g. 250%
critical damage).

### 6.1 Offense

| Attribute | Unit | Meaning |
|---|---|---|
| `MinDamage` | flat | Minimum base weapon damage |
| `MaxDamage` | flat | Maximum base weapon damage |
| `Attack` | flat | Physical attack power (melee/ranged) |
| `MagicAttack` | flat | Magic attack power |
| `AttackSpeed` | sec | Base attack interval (lower = faster) |
| `AttackSpeedBoost` | pct | Attack speed increase |
| `CriticalChance` | flat | Critical hit rating |
| `CriticalDamage` | pct_rate | Critical damage multiplier |
| `HeavyAttackChance` | flat | Heavy attack rating |
| `Hit` | flat | Physical hit rating |
| `MagicHit` | flat | Magic hit rating |
| `SkillDamageBoost` | pct | Outgoing skill damage increase |
| `ShieldPenetration` | flat | Chance rating to bypass block |
| `DefensePenetration` | flat | Ignores target defense |

### 6.2 Defense

| Attribute | Unit | Meaning |
|---|---|---|
| `Defense` | flat | Physical damage mitigation rating |
| `MagicDefense` | flat | Magic damage mitigation rating |
| `MeleeEvasion` | flat | Evasion rating vs melee |
| `RangedEvasion` | flat | Evasion rating vs ranged |
| `MagicEvasion` | flat | Evasion rating vs magic |
| `MeleeEndurance` | flat | Crit resistance vs melee |
| `RangedEndurance` | flat | Crit resistance vs ranged |
| `MagicEndurance` | flat | Crit resistance vs magic |
| `DamageReduction` | flat | Flat incoming damage reduction |
| `SkillDamageResistance` | pct | Incoming skill damage reduction |
| `ShieldBlockChance` | flat | Block rating (shield equipped) |

### 6.3 Resources

| Attribute | Unit | Meaning |
|---|---|---|
| `Health` | flat | Maximum health |
| `HealthRegen` | flat | Health regenerated per tick |
| `Mana` | flat | Maximum mana |
| `ManaRegen` | flat | Mana regenerated per tick |
| `ManaCostEfficiency` | pct | Skill mana cost reduction |
| `StaminaRegen` | flat | Stamina regenerated per tick |

### 6.4 Tempo & Mobility

| Attribute | Unit | Meaning |
|---|---|---|
| `CooldownSpeed` | pct | Cooldown reduction |
| `CastTime` | sec | Base cast/channel time |
| `Cooldown` | sec | Base skill cooldown |
| `MoveSpeed` | pct | Movement speed modifier |
| `Range` | m | Skill effect range |
| `AttackRange` | m | Basic attack range |
| `AreaRadius` | m | Area-of-effect radius |
| `ProjectileSpeed` | m | Projectile travel speed (m/s) |

### 6.5 Support & Utility

| Attribute | Unit | Meaning |
|---|---|---|
| `HealingPower` | pct | Outgoing healing increase |
| `HealingReceived` | pct | Incoming healing increase |
| `BuffDuration` | pct | Outgoing buff duration increase |
| `DebuffDuration` | pct | Outgoing debuff duration increase |
| `CrowdControlChance` | flat | CC application rating |
| `CrowdControlResistance` | flat | CC resistance rating |
| `AggroBoost` | pct | Threat generation modifier |
| `WeightLimit` | flat | Inventory weight capacity |
| `Luck` | flat | Loot/proc luck rating |

Extending the catalog is a **MINOR change to this document plus a schema change**; it
must never be bypassed with free-form attribute names.

## 7. Reusable Components

Typed building blocks referenced by the entity models in §8. Each becomes a `$defs`
entry in `common.schema.json` at implementation time.

### 7.1 `StatModifier`

One attribute modification. Used by items (base stats), buffs, set bonuses.

| Field | Type | Required |
|---|---|---|
| `attribute` | GameplayAttribute (§6) | yes |
| `modifier` | enum: `Flat`, `Percent` | yes |
| `value` | number | yes |

The `value` unit is fixed by the attribute's declared unit; `Percent` modifiers on flat
attributes mean "% of base". Validation: `Percent` values in −100..1000; `Flat` values
bounded per attribute (implementation detail).

### 7.2 `RarityScaledModifier`

Trait-style modification that scales with the rarity of the carrying item.

| Field | Type | Required |
|---|---|---|
| `attribute` | GameplayAttribute | yes |
| `modifier` | enum: `Flat`, `Percent` | yes |
| `valuesByRarity` | map Rarity → number | yes (≥1 entry) |

### 7.3 `ResourceCost`

| Field | Type | Required |
|---|---|---|
| `resource` | enum: `Mana`, `Health`, `Stamina` | yes |
| `amount` | number ≥ 0 | yes |

### 7.4 `SkillTiming`

| Field | Type | Required |
|---|---|---|
| `castTime` | sec ≥ 0 (0 = instant) | yes |
| `cooldown` | sec ≥ 0 | yes |
| `duration` | sec ≥ 0 | no (channel/effect duration) |

### 7.5 `Targeting`

| Field | Type | Required |
|---|---|---|
| `targetType` | enum: `Self`, `Ally`, `Enemy`, `Ground`, `Cone`, `Area` | yes |
| `range` | m ≥ 0 | yes |
| `areaRadius` | m ≥ 0 | no |
| `maxTargets` | int ≥ 1 | no |

### 7.6 `PieceBonus` (set bonuses)

| Field | Type | Required |
|---|---|---|
| `pieces` | int 2–7 | yes |
| `modifiers` | StatModifier[] (≥1) | yes* |
| `grantsBuff` | Reference→Buff | no |

*At least one of `modifiers`/`grantsBuff`.

### 7.7 `DropSource` (acquisition; resolves ER-2)

| Field | Type | Required |
|---|---|---|
| `sourceType` | enum: `MonsterDrop`, `BossDrop`, `Crafting`, `Vendor`, `Quest`, `Event`, `WorldChest`, `Gacha` | yes |
| `source` | Reference→Monster/Boss/Npc/Event | no (required for drop/vendor/quest types) |
| `dropChance` | pct (0–100] | no |

### 7.8 `Requirement`

| Field | Type | Required |
|---|---|---|
| `requiredLevel` | int 1–70 | no |
| `requiredWeaponMastery` | WeaponType + int | no |

## 8. Canonical Entity Models

Common envelope (§2) applies to all; only type-specific fields are listed. "Reference→X"
means a stable ID whose category is validated against X (typed references, JS-1).

### 8.1 Weapon (`tl.weapon.*`)

| Field | Type | Required |
|---|---|---|
| `rarity` | Rarity | yes |
| `weaponType` | enum: `Sword`, `Greatsword`, `Dagger`, `Crossbow`, `Longbow`, `Staff`, `Wand`, `SpearAndShield`* | yes |
| `itemLevel` | int ≥ 1 | yes |
| `tier` | int ≥ 1 | no (T2 archboss variants etc.) |
| `requirement` | Requirement | no |
| `baseStats` | StatModifier[] | yes — must include `MinDamage` and `MaxDamage` |
| `traitPool` | Reference→Trait [] (unique) | yes (may be empty while unresearched) |
| `maxTraitSlots` | int 0–5 | yes |
| `grantsSkills` | Reference→Skill [] | no (weapon-bound skills) |
| `acquisition` | DropSource[] | no |

*Weapon type list = current game classes; extending it is a model MINOR change.

Relationships: Weapon →(traitPool)→ Trait; Weapon →(grantsSkills)→ Skill;
SetBonus →(members)→ Weapon (canonical on the set side; **the V1 item-side `sets`
field is removed**, ER-1). Validation: `traits`/`sets` fields from V1 are illegal;
trait references must be `tl.trait.*`; `weaponType` tag duplication in `metadata.tags`
is discouraged (tags stay free-form curation hints only).

### 8.2 Armor (`tl.armor.*`)

| Field | Type | Required |
|---|---|---|
| `rarity` | Rarity | yes |
| `armorType` | enum: `Plate`, `Leather`, `Cloth` | yes |
| `slot` | enum: `Head`, `Chest`, `Hands`, `Legs`, `Feet`, `Cloak` | yes |
| `itemLevel` | int ≥ 1 | yes |
| `requirement` | Requirement | no |
| `baseStats` | StatModifier[] | yes — must include `Defense` |
| `traitPool` | Reference→Trait [] (unique) | yes |
| `maxTraitSlots` | int 0–5 | yes |
| `acquisition` | DropSource[] | no |

Validation: `Cloak` slot has no `armorType` weight in-game ⇒ `armorType` still required
(use the set's weight); slot+internalName uniqueness recommended check.

### 8.3 Accessory (`tl.accessory.*`)

| Field | Type | Required |
|---|---|---|
| `rarity` | Rarity | yes |
| `slot` | enum: `Necklace`, `Bracelet`, `Ring`, `Belt` | yes |
| `itemLevel` | int ≥ 1 | yes |
| `requirement` | Requirement | no |
| `baseStats` | StatModifier[] (≥1) | yes |
| `traitPool` | Reference→Trait [] (unique) | yes |
| `maxTraitSlots` | int 0–5 | yes |
| `acquisition` | DropSource[] | no |

Note: two Ring slots exist in-game; slot describes the item kind, not the equip slot
index.

### 8.4 Trait (`tl.trait.*`)

| Field | Type | Required |
|---|---|---|
| `rarity` | Rarity | yes (rarity of the trait definition itself) |
| `traitCategory` | enum: `Offense`, `Defense`, `Utility`, `Resource`, `Mobility` | yes |
| `appliesTo` | enum[] ⊆ {`Weapon`, `Armor`, `Accessory`} (≥1, unique) | yes |
| `effects` | RarityScaledModifier[] (≥1) | yes |

Relationships: referenced by item `traitPool`s. Validation: each `effects.attribute`
must be a §6 attribute; `valuesByRarity` keys ⊆ Rarity enum; a trait with
`appliesTo: [Weapon]` may only appear in weapon trait pools (typed-reference plus
target check). **Replaces the V1 empty trait** (no `stats` reference list; the V1
`trait.stats → Stat entity` indirection is dropped — the attribute catalog is the
stat model, resolving the missing-Stat-catalog issue).

### 8.5 Skill (`tl.skill.*`)

| Field | Type | Required |
|---|---|---|
| `rarity` | Rarity | yes |
| `skillType` | enum: `Active`, `Passive` | yes |
| `weaponType` | WeaponType (§8.1) | yes |
| `timing` | SkillTiming | yes for Active; forbidden for Passive |
| `cost` | ResourceCost[] | yes for Active (may be empty list for free skills); forbidden for Passive |
| `targeting` | Targeting | yes for Active; forbidden for Passive |
| `damage` | SkillDamage | no |
| `passiveEffects` | StatModifier[] | Passive only (≥1 for Passive) |
| `appliesBuffs` | Reference→Buff [] | no |
| `appliesDebuffs` | Reference→Buff [] | no |

`SkillDamage` component: `baseDamage` (flat ≥ 0), `scalingAttribute`
(enum: `Attack`, `MagicAttack`), `scalingRatio` (pct_rate ≥ 0), `damageSchool`
(enum: `Physical`, `Magic`). Formula composition itself remains the Formula Engine's
domain (M5, AD-17); the skill carries only its own typed inputs.

Relationships: Skill →(appliesBuffs/appliesDebuffs)→ Buff; SkillCore →(skills)→ Skill;
Weapon →(grantsSkills)→ Skill; Monster →(skills)→ Skill.

### 8.6 SkillCore (`tl.skill_core.*`) — **entity type renamed usage note**

| Field | Type | Required |
|---|---|---|
| `rarity` | Rarity | yes |
| `coreType` | enum: `Fortitude`, `Doom`, `Grace`* | yes |
| `skills` | Reference→Skill [] (≥1, unique) | yes |
| `effects` | StatModifier[] (≥1) | yes |

*Core type list per current game systems; extend via model MINOR change.

### 8.7 SetBonus (`tl.set.*`, type `SetBonus`)

Resolves JS-2: the entity **type constant becomes `SetBonus`** (matching the DB model
and milestone vocabulary); the existing stable-ID category `tl.set.*` is retained
because stable IDs are immutable.

| Field | Type | Required |
|---|---|---|
| `rarity` | Rarity | yes |
| `members` | Reference→Weapon/Armor/Accessory [] (≥2, unique) | yes — **canonical side** |
| `bonuses` | PieceBonus[] (≥1) | yes |

Validation: `bonuses[].pieces` ≤ `len(members)`; pieces values strictly increasing;
member items must not declare a set on their side (V1 `sets` field removed).

### 8.8 Buff (`tl.buff.*`) — covers buffs and debuffs

No `rarity`.

| Field | Type | Required |
|---|---|---|
| `buffCategory` | enum: `Buff`, `Debuff` | yes |
| `dispellable` | bool | yes |
| `maxStacks` | int ≥ 1 | yes |
| `duration` | sec > 0, or `-1` sentinel forbidden → use `permanent: true` | yes (`duration` XOR `permanent`) |
| `permanent` | bool | see above |
| `modifiers` | StatModifier[] | no |
| `tick` | TickEffect | no |
| `crowdControl` | enum: `Stun`, `Sleep`, `Silence`, `Bind`, `Slow`, `Fear`, `Knockdown`, `Pull` | no |

`TickEffect` component: `interval` (sec > 0), `school` (`Physical`/`Magic`/`Heal`),
`baseAmount` (flat), `scalingAttribute` + `scalingRatio` (as in SkillDamage).
Validation: at least one of `modifiers`/`tick`/`crowdControl`.

### 8.9 Monster (`tl.monster.*`)

No `rarity`; uses `grade` (§3.2).

| Field | Type | Required |
|---|---|---|
| `grade` | MonsterGrade, ∈ {`Normal`, `Elite`, `Named`} | yes |
| `level` | int 1–70 | yes |
| `family` | enum: `Humanoid`, `Beast`, `Undead`, `Demon`, `Construct`, `Elemental`, `Plant`, `Wildkin` | yes |
| `combatStats` | StatModifier[] | yes — must include `Health`, `Attack` or `MagicAttack`, `Defense`, `MagicDefense` |
| `skills` | Reference→Skill [] | no |
| `drops` | MonsterDrop[] | no |
| `zone` | string (free until a Zone entity exists) | no |

`MonsterDrop` component: `item` (Reference→Weapon/Armor/Accessory), `dropChance`
(pct (0–100]), `quantityMin`/`quantityMax` (int ≥ 1, min ≤ max).

### 8.10 Boss (`tl.boss.*`)

All Monster fields (with `grade` ∈ {`Boss`, `Archboss`}) plus:

| Field | Type | Required |
|---|---|---|
| `encounterType` | enum: `WorldBoss`, `ArchBoss`, `DungeonBoss`, `RaidBoss`, `EventBoss` | yes |
| `peaceMode` | bool (peace/conflict spawn variants exist) | yes |
| `mechanics` | BossMechanic[] | no |

`BossMechanic` component: `internalName` (PascalCase), `description` (string, required),
`triggersBuffs` (Reference→Buff [], optional). Mechanics are documentation-grade data
for AI answers; simulation-grade mechanics arrive with the Simulator milestone.

### 8.11 NPC (`tl.npc.*`)

No `rarity`, no combat block.

| Field | Type | Required |
|---|---|---|
| `role` | enum: `Merchant`, `QuestGiver`, `Crafter`, `Teleporter`, `Storyline`, `GuildClerk`, `Other` | yes |
| `location` | string (free until a Zone entity exists) | yes |
| `services` | string[] | no |
| `sells` | Reference→Weapon/Armor/Accessory [] | no |

## 9. Relationship Matrix (canonical directions)

| From | Field | To | Cardinality |
|---|---|---|---|
| Weapon/Armor/Accessory | `traitPool` | Trait | n:m |
| Weapon | `grantsSkills` | Skill | n:m |
| SetBonus | `members` | Weapon/Armor/Accessory | n:m (canonical; no mirror) |
| SetBonus | `bonuses[].grantsBuff` | Buff | n:1 |
| Skill | `appliesBuffs` / `appliesDebuffs` | Buff | n:m |
| SkillCore | `skills` | Skill | n:m |
| Monster/Boss | `skills` | Skill | n:m |
| Monster/Boss | `drops[].item` | Item | n:m + payload (chance, quantity) |
| Item | `acquisition[].source` | Monster/Boss/NPC/Event | n:m + payload |
| NPC | `sells` | Item | n:m |

Implementation note (informative): association tables must be populated from these
fields (review issue DB-1); `drops`/`acquisition` need association *objects* with
payload columns, not bare m2m.

## 10. Validation Rules (consolidated)

**Envelope**: id pattern + category/directory agreement; `internalName` = file name;
`internalName` unique per category; `displayName` non-empty; version/patch regexes;
metadata status ∈ {staging, validated}; only `status: validated` entities are imported
to production databases (staging entities importable to dev with a flag — future).

**Typing**: every reference field validates target category (JS-1); every attribute
name ∈ §6 catalog; every enum value ∈ its closed list; `unevaluatedProperties: false`
everywhere; no `value` fields without an `attribute`.

**Semantics**: rarity required/forbidden per §3.1; Active/Passive conditional fields
(§8.5); buff `duration` XOR `permanent`; set piece counts ≤ member count and strictly
increasing; drop chances in (0, 100]; `quantityMin ≤ quantityMax`; traits used in a
pool must list the pool's item kind in `appliesTo`; `maxTraitSlots` ≤ 5.

**Cross-entity**: all references resolve (existing rule); no reference cycles across
`grantsBuff`/`appliesBuffs` chains (warning); set members must not overlap between two
sets of the same slot (warning).

## 11. Description & FlavorText Style Rules

- `description`: factual and mechanical — what it does, where it comes from, notable
  interactions. 1–4 sentences. No lore.
- `flavorText`: verbatim in-game flavor only; omit if none exists.
- Both feed AI embeddings (review issue AI-1): embedding input =
  `displayName + description + typed attributes` (informative note for M7).

## 12. Migration Notes from V1 (informative, not part of this design's actions)

The 37 existing entities require: `name` → `internalName`; add `displayName`; items:
add `weaponType`/`armorType`/`slot`/`itemLevel`/`baseStats`/`maxTraitSlots`, rename
`traits` → `traitPool`, delete `sets`; traits: add `traitCategory`/`appliesTo`/
`effects`, delete `stats` capability; skills: add full mechanics block; skill cores:
add `coreType`/`effects`; sets: type `Set` → `SetBonus`, add `bonuses`. Stable IDs and
semantic-version rules make this a MAJOR version bump (`2.0.0`) for every migrated
entity. Schemas, importer meta handling, DB columns (rarity), and association
population follow in the implementation task(s).

---

## Verdict

# READY FOR IMPLEMENTATION

The model covers all 11 required entity types plus the identity quintet
(DisplayName, InternalName, LocalizationKey, Description, FlavorText), a closed
44-attribute gameplay catalog with units, 8 reusable typed components, canonical
relationship directions, versioning/patch governance, and consolidated validation
rules. It resolves every Critical and High finding of T011A (YM-1, YM-2, YM-3, YM-4,
JS-1, JS-2, ER-1/ER-2) at the model level. Remaining open points (Zone/Quest/Consumable
entity types, localization population, formula composition) are explicitly deferred and
do not affect the ability to author items, traits, skills, cores, sets, buffs, and
monsters/bosses/NPCs exactly once.
