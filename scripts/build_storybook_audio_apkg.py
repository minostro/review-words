from __future__ import annotations

import argparse
from pathlib import Path

import genanki

from scripts.storybook_common import (
    BACK_AUDIO_TMPL,
    FRONT_TMPL,
    STYLING,
    audio_field_value,
    audio_filename,
    default_audio_dir,
    default_output_path,
    display_syllables,
    load_cards,
)


MODEL_ID = 1837452105
DECK_ID = 1837452106
DEFAULT_DECK_NAME = "Salvador Review Words::Storybook Audio"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an audio-enabled Anki deck package from a review words CSV.")
    parser.add_argument("--csv", type=Path, required=True, help="CSV export with Front/Syllables/Example sentence/Tags columns.")
    parser.add_argument("--audio-dir", type=Path, help="Directory containing generated MP3 files.")
    parser.add_argument("--output", type=Path, help="Output .apkg path. Defaults to out/<csv>_storybook_audio.apkg")
    parser.add_argument("--deck-name", default=DEFAULT_DECK_NAME, help="Deck name inside Anki.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audio_dir = default_audio_dir(args.csv, args.audio_dir)
    output_path = default_output_path(args.csv, "storybook_audio", args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    model = genanki.Model(
        MODEL_ID,
        "Salvador Storybook Audio Note",
        fields=[
            {"name": "Front"},
            {"name": "Syllables"},
            {"name": "Example Sentence"},
            {"name": "Audio"},
        ],
        templates=[
            {
                "name": "Storybook Audio Card",
                "qfmt": FRONT_TMPL,
                "afmt": f"{{{{FrontSide}}}}\n<hr id=\"answer\">\n{BACK_AUDIO_TMPL}",
            }
        ],
        css=STYLING,
    )

    deck = genanki.Deck(DECK_ID, args.deck_name)
    media_files: list[str] = []

    for card in load_cards(args.csv):
        filename = audio_filename(card.index, card.front)
        audio_path = audio_dir / filename
        if not audio_path.exists():
            raise FileNotFoundError(f"Missing audio for {card.front}: {audio_path}")
        media_files.append(str(audio_path))
        note = genanki.Note(
            model=model,
            fields=[
                card.front,
                display_syllables(card.syllables),
                card.example_sentence,
                audio_field_value(filename),
            ],
            tags=card.tags,
        )
        deck.add_note(note)

    genanki.Package(deck, media_files=media_files).write_to_file(output_path)
    print(output_path)


if __name__ == "__main__":
    main()
