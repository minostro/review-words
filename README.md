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
- animal-themed SVG visuals
- Spanish prompt audio, answer audio, and celebration audio
- playful prompts on the answer side

The derived package now contains:

- `90` broad-review cards across `Tables::2-4` and `Tables::5-10`
- `38` additional focused-practice cards across the four `Tables::Focused::*` decks

The broad decks keep facts where both numbers are `10` or below and the practiced table is `2` through `10`.
The focused decks add the requested `2` and `3` practice ranges, including commutative forms such as `5 x 2` and `10 x 3`.

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
