from __future__ import annotations

import argparse
from pathlib import Path

import genanki

from scripts.storybook_common import BACK_TMPL, FRONT_TMPL, STYLING, default_output_path, display_syllables, load_cards


MODEL_ID = 1837452101
DECK_ID = 1837452102
DEFAULT_DECK_NAME = "Salvador Review Words::Storybook"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a styled Anki deck package from a review words CSV.")
    parser.add_argument("--csv", type=Path, required=True, help="CSV export with Front/Syllables/Example sentence/Tags columns.")
    parser.add_argument("--output", type=Path, help="Output .apkg path. Defaults to out/<csv>_storybook.apkg")
    parser.add_argument("--deck-name", default=DEFAULT_DECK_NAME, help="Deck name inside Anki.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = default_output_path(args.csv, "storybook", args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    model = genanki.Model(
        MODEL_ID,
        "Salvador Storybook Note",
        fields=[
            {"name": "Front"},
            {"name": "Syllables"},
            {"name": "Example Sentence"},
        ],
        templates=[
            {
                "name": "Storybook Card",
                "qfmt": FRONT_TMPL,
                "afmt": f"{{{{FrontSide}}}}\n<hr id=\"answer\">\n{BACK_TMPL}",
            }
        ],
        css=STYLING,
    )

    deck = genanki.Deck(DECK_ID, args.deck_name)
    for card in load_cards(args.csv):
        note = genanki.Note(
            model=model,
            fields=[card.front, display_syllables(card.syllables), card.example_sentence],
            tags=card.tags,
        )
        deck.add_note(note)

    genanki.Package(deck).write_to_file(output_path)
    print(output_path)


if __name__ == "__main__":
    main()
