# Animal Multiplication Deck Design

## Summary

Build a new derived Anki package from the existing multiplication `.apkg` that is more engaging for a 7-year-old while staying compatible with normal Anki behavior.

The new package will:

- leave the original deck untouched
- include only multiplication tables `2` through `10`
- keep all combinations, including both `2 x 7` and `7 x 2`
- split the cards into two subdecks in one package:
  - `Tables::2-4`
  - `Tables::5-10`
- add animal-themed visuals
- add Spanish prompt audio, answer audio, and short celebration audio
- add short playful prompts on the answer side

## Goals

- make the deck feel warmer and more playful without turning it into a fragile custom app
- support short, repeatable study sessions for a young child
- preserve straightforward Anki import and review behavior
- make the derived deck reproducible from local tooling in this repo

## Non-Goals

- replacing Anki with a full game
- implementing real streak tracking or adaptive gameplay across cards
- supporting tables `11` through `20`
- hand-illustrating every card as a one-off bespoke asset

## Source Material

Input package:

- `/Users/minostro/Downloads/1_to_20_Multiplication_Tables_100_accurate_value.apkg`

Observed source structure:

- one note type with `Front` and `Back`
- one card per note
- prompts formatted like `3 X 4 = ?`
- numeric answers on the back
- no bundled media assets

## Target Deck Structure

Create a new package with parent deck `Tables` and two subdecks:

- `Tables::2-4`
- `Tables::5-10`

Card inclusion rules:

- include tables `2` through `10`
- include all combinations for those tables
- keep facts such as `1 x 2`, `1 x 7`, and `10 x 10` because they belong to tables `2` through `10`
- exclude any card where the table being practiced is `11` through `20`

Expected card totals:

- `Tables::2-4`: `30` cards
- `Tables::5-10`: `60` cards
- total: `90` cards

## Card Experience

Each card should remain simple enough for reliable Anki playback while adding a playful feel.

Front side:

- multiplication prompt, derived from the source card
- animal-themed visual that represents the multiplication as equal groups
- Spanish prompt audio for the fact

Back side:

- numeric answer
- Spanish answer audio
- short celebration audio
- one short playful prompt

Example playful prompts:

- `Da 6 palmadas`
- `Haz 3 filas de 4 con monedas`
- `Dilo como un leon`
- `Cuenta primero los grupos, luego el total`

## Media Strategy

### Visuals

Generate a consistent set of simple animal-themed visuals rather than bespoke art for every card.

Requirements:

- each card gets a visual asset
- the image should communicate grouped quantity, not only decoration
- visuals should be lightweight and reproducible from code
- style should stay consistent across all cards

Preferred implementation:

- generate SVG or PNG assets locally from templates or code
- represent equal groups using animals or animal-adjacent icons in rows, clusters, or arrays

### Audio

Generate three audio layers:

- Spanish prompt audio on the front
- Spanish answer audio on the back
- short reusable celebration audio on the back

Requirements:

- Spanish only
- prompt audio should say the multiplication expression naturally
- answer audio should say the result naturally
- celebration audio can be reused across many cards

### Prompt Library

Use a reusable library of short playful prompts instead of writing a unique activity for every fact.

Requirements:

- prompts should be short enough to scan quickly
- prompts should encourage movement, counting, speaking, or arranging objects
- prompts should fit the animal theme when possible
- distribution should feel varied across the deck

## Anki Constraints

This design intentionally works within standard Anki capabilities.

Supported well:

- images
- audio playback
- custom front and back templates
- encouraging text and themed presentation

Not supported as true app behavior:

- persistent streak tracking across cards
- adaptive mini-games triggered by misses
- real score systems or unlock logic

Design implication:

- "streak celebration" will be simulated through encouraging copy and celebration sounds, not persistent state

## Implementation Outline

1. Read the source `.apkg` and extract notes for tables `2` through `10`.
2. Partition those notes into `Tables::2-4` and `Tables::5-10`.
3. Create a derived card model or templates that support visuals, audio, and playful prompt text.
4. Generate animal-themed image assets for each card.
5. Generate Spanish prompt and answer audio for each card.
6. Add a small reusable set of celebration audio clips.
7. Build a new `.apkg` containing the two subdecks and all referenced media.
8. Re-open the generated package and verify structure, counts, and media references.

## Verification

Before calling the work complete, verify:

- the generated package imports cleanly
- the deck contains exactly two subdecks:
  - `Tables::2-4`
  - `Tables::5-10`
- card counts are `30` and `60`
- total cards are `90`
- sample cards from each subdeck show the correct prompt, answer, image, and audio references
- the original source package remains unchanged

## Open Questions For Implementation

- whether local text-to-speech and audio tooling in this repo are sufficient for natural Spanish playback
- whether celebration sounds should be synthesized, sourced locally, or replaced with short spoken praise
- whether visuals should be generated as SVG first and rasterized only if Anki compatibility requires it

## Recommendation

Start with a balanced multimedia deck:

- consistent animal visuals
- Spanish prompt and answer audio
- a small set of reusable celebration sounds
- lightweight playful prompts

This gives the deck a more joyful feel while keeping the package practical to build, verify, and use in Anki.
