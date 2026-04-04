# Focused Multiplication Practice Decks Design

## Summary

Extend the existing derived multiplication `.apkg` so it still includes the current broad review decks and also adds four smaller focused practice decks.

The updated package will:

- keep the existing broad decks:
  - `Tables::2-4`
  - `Tables::5-10`
- add four focused decks in the same `.apkg`:
  - `Tables::Focused::2 x 1-5`
  - `Tables::Focused::2 x 6-10`
  - `Tables::Focused::3 x 1-5`
  - `Tables::Focused::3 x 6-10`
- include commutative forms inside the focused decks
- continue reusing the same generated visuals and audio assets
- keep the current card styling and note model

## Goals

- preserve the current broad review flow without replacing it
- add smaller practice decks for tables `2` and `3`
- keep everything importable as one Anki package
- avoid duplicating media files even when the same fact appears in multiple decks
- keep the focused-deck rules explicit and easy to extend later

## Non-Goals

- changing the current visual or audio design
- removing or renaming the existing broad decks
- adding focused decks for tables beyond `2` and `3`
- introducing a second output package or new CLI mode for this request

## Target Deck Structure

The generated package should contain six subdecks under `Tables`:

- `Tables::2-4`
- `Tables::5-10`
- `Tables::Focused::2 x 1-5`
- `Tables::Focused::2 x 6-10`
- `Tables::Focused::3 x 1-5`
- `Tables::Focused::3 x 6-10`

The existing broad decks keep their current inclusion rules:

- `Tables::2-4` contains all supported facts where the practiced table is `2`, `3`, or `4`
- `Tables::5-10` contains all supported facts where the practiced table is `5` through `10`

The new focused decks use targeted inclusion rules:

- `Tables::Focused::2 x 1-5`
  - include `2 x 1` through `2 x 5`
  - also include `1 x 2` through `5 x 2`
- `Tables::Focused::2 x 6-10`
  - include `2 x 6` through `2 x 10`
  - also include `6 x 2` through `10 x 2`
- `Tables::Focused::3 x 1-5`
  - include `3 x 1` through `3 x 5`
  - also include `1 x 3` through `5 x 3`
- `Tables::Focused::3 x 6-10`
  - include `3 x 6` through `3 x 10`
  - also include `6 x 3` through `10 x 3`

Within a single focused deck, duplicate self-symmetric facts must be collapsed:

- `2 x 2` appears once in `Tables::Focused::2 x 1-5`
- `3 x 3` appears once in `Tables::Focused::3 x 1-5`

Across different decks, overlapping facts are allowed and expected:

- a fact can appear in one broad deck and one focused deck
- some facts such as `2 x 3` and `3 x 2` can also appear in both a `2` focused deck and a `3` focused deck

## Expected Card Totals

Broad decks remain unchanged:

- `Tables::2-4`: `30` cards
- `Tables::5-10`: `60` cards

Focused decks add:

- `Tables::Focused::2 x 1-5`: `9` cards
- `Tables::Focused::2 x 6-10`: `10` cards
- `Tables::Focused::3 x 1-5`: `9` cards
- `Tables::Focused::3 x 6-10`: `10` cards

Total package cards:

- `128` cards

This total is higher than `90` because cards are intentionally duplicated across decks when one fact belongs to multiple study groupings.

## Data Model And Builder Changes

The current implementation assigns each fact to one deck through a single `subdeck_name` value. That is no longer sufficient because one fact can now belong to multiple decks.

Update the deck-selection logic so each parsed fact exposes all matching deck names.

Recommended structure:

- define deck rules in `scripts/multiplication_common.py`
- keep broad-deck rules and focused-deck rules in one explicit configuration
- have parsing/loading produce one canonical fact object plus a derived list of matching deck names

The builder in `scripts/build_multiplication_apkg.py` should then:

- create one `genanki.Deck` per configured deck
- iterate through each fact and add one note per matching deck
- keep note field generation unchanged
- keep visual and audio filenames unchanged so media stays reusable
- package all six decks into one `.apkg`

## Media Strategy

No new media pipeline is needed.

- SVG visuals continue to be generated once per fact
- prompt audio, answer audio, and celebration audio continue to use the existing filenames
- duplicated cards in multiple decks should reference the same media filenames
- the final package should deduplicate media files before writing the archive

## Verification

Before implementation is considered complete, verify:

- the generated package still includes the existing broad decks
- the generated package now includes all four focused decks
- broad-deck counts remain `30` and `60`
- focused-deck counts are `9`, `10`, `9`, and `10`
- total cards are `128`
- `2 x 2` and `3 x 3` appear only once within their respective focused decks
- representative commutative pairs such as `2 x 5` and `5 x 2` both appear in the appropriate focused deck
- overlapping facts can appear in more than one deck without missing media references

## Recommendation

Implement this as a data-driven deck-definition update rather than as special-case conditionals in the builder.

That keeps the current deck behavior stable, makes the four new decks additive, and leaves room for future focused ranges without another structural rewrite.
