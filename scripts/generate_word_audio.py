from __future__ import annotations

import argparse
from pathlib import Path

from gtts import gTTS

from scripts.storybook_common import audio_filename, default_audio_dir, load_cards


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate one Spanish MP3 per word in a review words CSV.")
    parser.add_argument("--csv", type=Path, required=True, help="CSV export with Front/Syllables/Example sentence/Tags columns.")
    parser.add_argument("--audio-dir", type=Path, help="Output directory for MP3 files. Defaults to out/audio/<csv-stem>/")
    parser.add_argument("--lang", default="es", help="gTTS language code. Defaults to es.")
    return parser.parse_args()


def synthesize_word(word: str, output_path: Path, lang: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gTTS(text=word, lang=lang).save(str(output_path))


def should_skip_existing_audio(output_path: Path) -> bool:
    return output_path.exists() and output_path.stat().st_size > 0


def main() -> None:
    args = parse_args()
    audio_dir = default_audio_dir(args.csv, args.audio_dir)

    created = 0
    skipped = 0
    for card in load_cards(args.csv):
        output_path = audio_dir / audio_filename(card.index, card.front)
        if should_skip_existing_audio(output_path):
            skipped += 1
            continue
        if output_path.exists():
            output_path.unlink()
        synthesize_word(card.front, output_path, args.lang)
        created += 1
        print(f"created {output_path.name}")

    print(f"done created={created} skipped={skipped} dir={audio_dir}")


if __name__ == "__main__":
    main()
