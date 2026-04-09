# More Focused Multiplication Practice Decks Design

## Summary

Extend the current derived multiplication `.apkg` again so it keeps the existing broad decks and focused `2` and `3` decks, and also adds four new focused practice decks for tables `4` and `5`.

The updated package will:

- keep the existing broad decks:
  - `Tables::2-4`
  - `Tables::5-10`
- keep the existing focused decks:
  - `Tables::Focused::2 x 1-5`
  - `Tables::Focused::2 x 6-10`
  - `Tables::Focused::3 x 1-5`
  - `Tables::Focused::3 x 6-10`
- add four more focused decks in the same `.apkg`:
  - `Tables::Focused::4 x 1-5`
  - `Tables::Focused::4 x 6-10`
  - `Tables::Focused::5 x 1-5`
  - `Tables::Focused::5 x 6-10`
- apply the same focused-deck inclusion rule already used for tables `2` and `3`
- continue reusing the same generated visuals and audio assets

## Goals

- preserve the existing broad-review and focused-review structure
- add smaller practice decks for tables `4` and `5`
- keep everything importable as one Anki package
- keep the focused-deck configuration explicit and easy to maintain
- avoid duplicating media files even when the same fact appears in several decks

## Non-Goals

- changing the broad-deck rules
- removing or renaming any existing decks
- introducing focused decks for tables beyond `5`
- introducing a second output package or a separate builder mode

## Target Deck Structure

The generated package should contain ten subdecks under `Tables`:

- `Tables::2-4`
- `Tables::5-10`
- `Tables::Focused::2 x 1-5`
- `Tables::Focused::2 x 6-10`
- `Tables::Focused::3 x 1-5`
- `Tables::Focused::3 x 6-10`
- `Tables::Focused::4 x 1-5`
- `Tables::Focused::4 x 6-10`
- `Tables::Focused::5 x 1-5`
- `Tables::Focused::5 x 6-10`

The new focused decks follow the exact same rule as the current `2` and `3` focused decks:

- `Tables::Focused::4 x 1-5`
  - include `4 x 1` through `4 x 5`
  - also include `1 x 4` through `5 x 4`
- `Tables::Focused::4 x 6-10`
  - include `4 x 6` through `4 x 10`
  - also include `6 x 4` through `10 x 4`
- `Tables::Focused::5 x 1-5`
  - include `5 x 1` through `5 x 5`
  - also include `1 x 5` through `5 x 5`
- `Tables::Focused::5 x 6-10`
  - include `5 x 6` through `5 x 10`
  - also include `6 x 5` through `10 x 5`

Within a single focused deck, duplicate self-symmetric facts must still be collapsed:

- `4 x 4` appears once in `Tables::Focused::4 x 1-5`
- `5 x 5` appears once in `Tables::Focused::5 x 1-5`

Across different decks, overlapping facts remain allowed and expected:

- a fact can appear in one broad deck and one or more focused decks
- facts such as `4 x 5` and `5 x 4` can appear in both a `4` focused deck and a `5` focused deck

## Expected Card Totals

Broad decks remain unchanged:

- `Tables::2-4`: `30` cards
- `Tables::5-10`: `60` cards

Existing focused decks remain unchanged:

- `Tables::Focused::2 x 1-5`: `9` cards
- `Tables::Focused::2 x 6-10`: `10` cards
- `Tables::Focused::3 x 1-5`: `9` cards
- `Tables::Focused::3 x 6-10`: `10` cards

New focused decks add:

- `Tables::Focused::4 x 1-5`: `9` cards
- `Tables::Focused::4 x 6-10`: `10` cards
- `Tables::Focused::5 x 1-5`: `9` cards
- `Tables::Focused::5 x 6-10`: `10` cards

Total package cards:

- `166` cards

This total is higher than `128` because cards are intentionally duplicated across decks when one fact belongs to multiple study groupings.

## Implementation Outline

Keep the current structure introduced for the first focused-deck expansion and extend it in place.

- add four more `FocusedDeckDefinition` entries in `scripts/multiplication_common.py`
- extend `configured_deck_names()` so the builder includes all ten decks
- assign stable new deck IDs in `scripts/build_multiplication_apkg.py`
- preserve the current note model, media filenames, and deck-building flow
- update tests to cover the new deck names, counts, and self-commutative examples
- update the README so the documented package contents and totals stay accurate

## Media Strategy

No new media pipeline is needed.

- existing visuals remain generated once per fact
- existing media filenames remain stable
- new focused inclusion rules mean `4 x 1` and `5 x 1` will now need generated audio, just as `2 x 1` and `3 x 1` did in the earlier focused expansion
- duplicated cards in multiple decks should continue to reuse the same media filenames

## Verification

Before implementation is considered complete, verify:

- the package includes all ten deck names
- broad-deck counts remain `30` and `60`
- focused-deck counts are `9`, `10`, `9`, `10`, `9`, `10`, `9`, and `10` across tables `2` through `5`
- total cards are `166`
- `4 x 4` and `5 x 5` appear only once within their respective focused `1-5` decks
- representative commutative pairs such as `4 x 5` and `5 x 4` appear in the appropriate focused decks
- overlapping facts continue to import correctly without missing media references

## Recommendation

Extend the existing explicit focused-deck configuration rather than introducing a more abstract rule generator now.

That keeps the change small, matches the current code structure, and still leaves the deck rules easy to inspect and extend later.
