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
