# Review Words Tooling

Small Python tools for turning a Notion export CSV into Anki deck packages.

The repo stores the tooling only. Generated exports, audio files, and deck packages are intentionally ignored by git.

## Setup

```bash
cd /Users/minostro/Repos/review-words
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests
```

## Expected CSV Columns

The deck builders expect a CSV with these columns:

- `Front`
- `Syllables`
- `Example sentence`
- `Tags`

## Build A Styled Deck

```bash
cd /Users/minostro/Repos/review-words
. .venv/bin/activate
python -m scripts.build_storybook_apkg \
  --csv /path/to/export.csv
```

By default this writes an `.apkg` into `out/`.

## Generate Word Audio

```bash
cd /Users/minostro/Repos/review-words
. .venv/bin/activate
python -m scripts.generate_word_audio \
  --csv /path/to/export.csv
```

By default this writes one MP3 per card into `out/audio/<csv-name>/`.

## Build The Audio Deck

```bash
cd /Users/minostro/Repos/review-words
. .venv/bin/activate
python -m scripts.build_storybook_audio_apkg \
  --csv /path/to/export.csv
```

If you want to reuse an existing audio folder, pass `--audio-dir /path/to/audio`.

## Build The Animal Multiplication Deck

This builder derives a child-friendly multiplication deck from an existing `.apkg`.

What it produces:

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
- animal-themed SVG visuals
- Spanish prompt audio, answer audio, and celebration audio
- playful prompts on the answer side

The derived package now contains:

- `90` broad-review cards across `Tables::2-4` and `Tables::5-10`
- `76` additional focused-practice cards across the eight `Tables::Focused::*` decks

The broad decks keep facts where both numbers are `10` or below and the practiced table is `2` through `10`.
The focused decks add the requested `2` through `5` practice ranges, including commutative forms such as `5 x 2`, `5 x 4`, and `10 x 5`.

```bash
cd /Users/minostro/Repos/review-words
. .venv/bin/activate
python -m scripts.generate_multiplication_audio \
  --source-apkg /Users/minostro/Downloads/1_to_20_Multiplication_Tables_100_accurate_value.apkg

python -m scripts.build_multiplication_apkg \
  --source-apkg /Users/minostro/Downloads/1_to_20_Multiplication_Tables_100_accurate_value.apkg \
  --audio-dir out/audio/1_to_20_Multiplication_Tables_100_accurate_value
```

By default this writes:

- audio files under `out/audio/<source-apkg-stem>/`
- the final package under `out/<source-apkg-stem>_animal_multiplication.apkg`

Notes:

- `gTTS` needs network access when generating real MP3 files
- SVG visuals are generated automatically during package creation
- you can inspect the output package quickly with `unzip -l out/*animal_multiplication.apkg`

## Current Salvador Export

These commands reproduce the current deck from the files we already generated:

```bash
cd /Users/minostro/Repos/review-words
. /Users/minostro/Documents/.venv-anki/bin/activate
python -m scripts.build_storybook_apkg \
  --csv /Users/minostro/Documents/anki_exports/salvador_review_words_v1_2026-03-22.csv

python -m scripts.generate_word_audio \
  --csv /Users/minostro/Documents/anki_exports/salvador_review_words_v1_2026-03-22.csv \
  --audio-dir /Users/minostro/Documents/anki_exports/audio/storybook_audio_v1_2026-03-22

python -m scripts.build_storybook_audio_apkg \
  --csv /Users/minostro/Documents/anki_exports/salvador_review_words_v1_2026-03-22.csv \
  --audio-dir /Users/minostro/Documents/anki_exports/audio/storybook_audio_v1_2026-03-22 \
  --output /Users/minostro/Documents/anki_exports/salvador_review_words_storybook_audio_v1_2026-03-22.apkg
```

## Illustrated English Spelling (AnkiDroid)

The English deck contains the supplied school vocabulary Units 1 and 2: 31
vocabulary notes and 124 cards. Each note has three complementary completion
patterns and one whole-word/phrase build. Cards use school-style illustrations,
bundled British English audio, and draggable letter tiles with a tap alternative.
The four card types remain siblings so Anki can bury related cards.

```bash
python -m scripts.generate_english_spelling_audio
python -m scripts.build_english_spelling_apkg
```

Outputs are under `out/english-spelling/`: `Salvador-English-Spelling.apkg` and
`preview.html`. The preview shares the real templates and requires its adjacent
PNG files and `audio/` folder. Audio generation needs a network connection;
study works offline. Re-running audio generation reuses existing nonempty files.

Import the APKG into **AnkiDroid Flashcards**. Start with a completion subdeck,
then add the full-build exercises when comfortable. Enable burying of new and
review siblings to avoid seeing all four versions of a target together. A
starting daily limit of five new cards is reasonable; adjust to the child.
Ensure automatic audio playback is enabled in deck options.

Drag a tile into a gap, or tap a tile and then a gap. Tap a placed letter to
return it. Check provides spelling feedback; it does not submit a review rating.
Use Anki's Show Answer, then choose Again after an error/help or Good after an
independent correct answer. Spaces and apostrophes stay visible; weekday capital
letters are preserved. Full-build phrases use all their letters.

Checks: `python -m unittest discover -s tests` and, with Playwright on NODE_PATH,
`node --test tests/test_english_spelling_interaction.cjs tests/test_english_spelling_browser.cjs`.
Browser interaction checks use installed Chrome. They simulate mobile size/touch;
physical AnkiDroid-device testing is still needed. Native audio autoplay depends
on the app's setting; the audio replay button is always available.

Artwork is in `scripts/english_spelling_assets/images/`. Generated atlases are
referenced by actual image tags for Anki media discovery and sync; no Internet
image URLs are used. See that directory's parent `ARTWORK.md` for generation
prompts and provenance.

## One Salvador Package: Reading, Multiplication, and English

Build one distribution file containing a `Salvador` parent deck with all three
subjects beneath it:

```bash
python -m scripts.build_salvador_apkg
```

The current defaults combine the Reading v7 export, the existing animal
multiplication export, and the illustrated English package. The result is
`out/salvador/Salvador.apkg`: **415 notes, 508 cards, and 536 bundled media files**.
The card counts are Reading 218, Multiplication 166, and English 124.

Use `--reading`, `--multiplication`, `--english`, and `--output` to supply future
versions explicitly. Build updated subject packages first, then rerun this
command. Upload/distribute only `Salvador.apkg`; it includes every child deck and
all audio/images. This is a distribution package, not an export of a learner's
study history. The bundler rejects inputs containing review history.

The bundler preserves source note GUIDs, model/field/template structure,
sibling relationships, and media bytes; it adds subject tags and changes deck
names under `Salvador`. Duplicate IDs/GUIDs and conflicting media filenames
fail clearly instead of silently dropping content. Identical shared media is
included only once. Generated APKGs remain ignored by git.

Import the file with AnkiDroid. Existing imported cards can retain their old
deck placement: if they do, move those existing decks/cards under the matching
Salvador subject once. Do not delete studied cards merely to reorganize them.
When offered an import-learning-progress option, leave it off for this shared
package. See [Anki's package import documentation](https://docs.ankiweb.net/importing/packaged-decks.html).

The Google Drive destination for the distribution is the existing private
`salvador-anki` folder. Uploading a new version there does not publish it publicly.
