# TBOI Tears Test

A free, ad-free static website for The Binding of Isaac community. Players select items and see how Isaac's main attack changes when items are combined: which item replaces the weapon, which adds an effect, which changes the number of shots. It includes a live animated preview of Isaac shooting.

All code, data, documentation and UI text are in English.

## Project rules

- **Never invent synergies.** Every rule or interaction must have a `source`: a link to the wiki page (https://bindingofisaacrebirth.wiki.gg) and the sentence it was derived from.
- **Target version: Repentance+.** On the wiki, `{{Dlc|...}}` tags mark which game version a sentence applies to. Discard information that only applies to older versions.
- If two wiki pages contradict each other, keep both versions and flag the conflict on the site. Do not pick one.
- Numeric values used by the animation (frames, speeds, angles) come from the wiki when available. Mark any estimated value as `estimated`.
- Wiki categories are incomplete (e.g. "Tear-modifying items" lists only 9 items). Do not rely on them to decide which items are in scope; read each item's Effects section instead.
- Secondary source for vocabulary: the modding API docs (https://wofsauge.github.io/IsaacDocs/rep/), enums `TearFlags` and `WeaponType`. They name what the game itself treats as a weapon (`replaces`) or a tear effect (`adds`), but say nothing about how effects combine; behavior still comes from the wiki.
- Forums (Reddit, Steam) are not a source for rules. Use them only to spot possible wiki errors or to prioritize popular combinations.
- Game sprites and assets must not be copied into the repository. Graphics are original, "Isaac-style" drawings.

## Item scope

- In: items that change the **type, behavior, effect or number** of shots of the main attack, including weapons that replace tears (Brimstone, Mom's Knife, ...). Stat items that change attack behavior are also in (Soy Milk, Chocolate Milk, ...).
- Out: items that only change numeric stats (damage, fire rate, range, shot speed), hearts, consumables, active items unrelated to shooting.
- Out: familiars, including those that copy Isaac's tears (Incubus, Twisted Pair, ...).

## Effect categories

- `replaces`: changes the weapon (Brimstone, Mom's Knife, Dr. Fetus, Tech X, ...)
- `adds`: adds an effect to the attack (homing, piercing, poison, split, ...)
- `multiplies`: changes the number of shots (20/20, The Inner Eye, Mutant Spider, ...)
- `firing`: changes how Isaac fires, e.g. charging, hovering or aiming (Soy Milk, Chocolate Milk, Cursed Eye, Anti-Gravity, Marked, ...)
- `exception`: a specific interaction between two or more items (from the wiki's Synergies/Interactions sections)

## Scope status (`data/scope.csv`)

- `in`: in scope, with one of the categories above.
- `conditional`: only changes the attack together with specific weapons (bomb modifiers with Dr. Fetus / Epic Fetus).
- `active`: active item that changes the attack temporarily. Not in scope for now.
- `out`: not in scope.

`data/scope.csv` is reviewed and edited by hand: it is the source of truth for which items are in scope. Do not regenerate it from scratch.

## Data pipeline

1. `python3 scripts/fetch_wiki.py` downloads every collectible page to `data/raw/wiki_pages.json` (not committed).
2. `python3 scripts/extract_items.py` builds `data/wiki_items.json`: infobox data plus the Effects, Synergies and Interactions sections, filtered to Repentance+.

## Licensing

- Code: MIT (see `LICENSE`).
- Data derived from the wiki: CC BY-SA 4.0, with attribution to the wiki (see `DATA_LICENSE.md`).
