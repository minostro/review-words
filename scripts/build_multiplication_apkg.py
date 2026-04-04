from __future__ import annotations

import argparse
import json
import sqlite3
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

import genanki

from scripts.generate_multiplication_audio import default_audio_dir
from scripts.multiplication_common import MultiplicationFact, configured_deck_names, load_supported_facts
from scripts.multiplication_content import playful_prompt_text
from scripts.multiplication_visuals import render_fact_svg, visual_filename


MODEL_ID = 1837452204
DECK_IDS = {
    "Tables::2-4": 1837452202,
    "Tables::5-10": 1837452203,
    "Tables::Focused::2 x 1-5": 1837452205,
    "Tables::Focused::2 x 6-10": 1837452206,
    "Tables::Focused::3 x 1-5": 1837452207,
    "Tables::Focused::3 x 6-10": 1837452208,
}

FRONT_TMPL = """
<div class="card-wrap">
  <div class="prompt">{{Prompt}}</div>
  <div class="visual">{{Visual}}</div>
  <div class="audio">{{PromptAudio}}</div>
</div>
"""

BACK_TMPL = """
<div class="card-wrap">
  <div class="prompt small">{{Prompt}}</div>
  <div class="answer">{{Answer}}</div>
  <div class="visual">{{Visual}}</div>
  <div class="playful">{{PlayfulPrompt}}</div>
  <div class="audio">{{AnswerAudio}} {{CelebrationAudio}}</div>
</div>
"""

STYLING = """
.card {
  font-family: "Avenir Next", "Helvetica Neue", sans-serif;
  background: #fffaf0;
  color: #0f172a;
  margin: 0;
  padding: 0;
}

.card-wrap {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 28px 20px 36px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background:
    linear-gradient(180deg, #fffaf0 0%, #fff1c2 100%);
}

.prompt {
  font-size: 52px;
  font-weight: 700;
  text-align: center;
  color: #0f172a;
  padding: 18px 22px;
  border-radius: 22px;
  background: #ffffff;
  border: 4px solid #0f172a;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.10);
}

.prompt.small {
  font-size: 34px;
}

.answer {
  margin-top: 16px;
  font-size: 64px;
  font-weight: 800;
  color: #0f172a;
  background: #facc15;
  border: 4px solid #0f172a;
  border-radius: 24px;
  padding: 10px 22px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.16);
}

.visual {
  margin-top: 18px;
}

.visual img {
  width: min(100%, 560px);
  border-radius: 24px;
  border: 4px solid #0f172a;
  background: #ffffff;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.14);
}

.playful {
  margin-top: 20px;
  max-width: 620px;
  font-size: 28px;
  line-height: 1.35;
  text-align: center;
  color: #0f172a;
  padding: 18px 22px;
  border-radius: 20px;
  background: #ffffff;
  border: 4px solid #0f172a;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
}

.audio {
  margin-top: 18px;
}

hr#answer {
  width: min(100%, 620px);
  margin: 22px 0 8px;
  border: 0;
  border-top: 4px solid #0f172a;
}

.nightMode .card {
  background: #020617;
  color: #f8fafc;
}

.nightMode .card-wrap {
  background:
    linear-gradient(180deg, #0f172a 0%, #111827 100%);
}

.nightMode .prompt {
  color: #f8fafc;
  background: #0f172a;
  border-color: #f8fafc;
  box-shadow: none;
}

.nightMode .answer {
  color: #0f172a;
  background: #fde047;
  border-color: #f8fafc;
  box-shadow: none;
}

.nightMode .visual img {
  background: #ffffff;
  border-color: #f8fafc;
  box-shadow: none;
}

.nightMode .playful {
  color: #f8fafc;
  background: #0f172a;
  border-color: #f8fafc;
  box-shadow: none;
}

.nightMode hr#answer {
  border-top-color: #f8fafc;
}
"""


@dataclass(frozen=True)
class PackageSummary:
    deck_names: set[str]
    deck_card_counts: dict[str, int]
    total_cards: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the animal multiplication Anki deck package.")
    parser.add_argument("--source-apkg", type=Path, required=True, help="Source multiplication .apkg file.")
    parser.add_argument("--audio-dir", type=Path, help="Directory containing generated audio files.")
    parser.add_argument("--output", type=Path, help="Output .apkg path. Defaults to out/<source>_animal_multiplication.apkg")
    return parser.parse_args()


def default_output_path(source_apkg: Path, output_path: Path | None) -> Path:
    if output_path is not None:
        return output_path
    return Path("out") / f"{source_apkg.stem}_animal_multiplication.apkg"


def prompt_audio_filename(fact: MultiplicationFact) -> str:
    return f"fact_{fact.left:02d}x{fact.right:02d}_prompt.mp3"


def answer_audio_filename(fact: MultiplicationFact) -> str:
    return f"fact_{fact.left:02d}x{fact.right:02d}_answer.mp3"


def celebration_audio_filename(fact: MultiplicationFact) -> str:
    celebration_index = ((fact.left + fact.right) % 3) + 1
    return f"celebration_{celebration_index:02d}.mp3"


def build_note_fields(fact: MultiplicationFact, visual_name: str, celebration_name: str) -> dict[str, str]:
    return {
        "Prompt": fact.front,
        "Answer": fact.back,
        "Visual": f'<img src="{visual_name}" alt="{fact.front}">',
        "PromptAudio": f"[sound:{prompt_audio_filename(fact)}]",
        "AnswerAudio": f"[sound:{answer_audio_filename(fact)}]",
        "CelebrationAudio": f"[sound:{celebration_name}]",
        "PlayfulPrompt": playful_prompt_text(fact),
    }


def note_fields_in_order(fields: dict[str, str]) -> list[str]:
    return [
        fields["Prompt"],
        fields["Answer"],
        fields["Visual"],
        fields["PromptAudio"],
        fields["AnswerAudio"],
        fields["CelebrationAudio"],
        fields["PlayfulPrompt"],
    ]


def note_guid(fact: MultiplicationFact, deck_name: str) -> str:
    return genanki.guid_for(fact.front, fact.back, deck_name)


def ensure_media_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing media file: {path}")


def build_model() -> genanki.Model:
    return genanki.Model(
        MODEL_ID,
        "Animal Multiplication Note High Contrast",
        fields=[
            {"name": "Prompt"},
            {"name": "Answer"},
            {"name": "Visual"},
            {"name": "PromptAudio"},
            {"name": "AnswerAudio"},
            {"name": "CelebrationAudio"},
            {"name": "PlayfulPrompt"},
        ],
        templates=[
            {
                "name": "Animal Multiplication",
                "qfmt": FRONT_TMPL,
                "afmt": "{{FrontSide}}\n<hr id=\"answer\">\n" + BACK_TMPL,
            }
        ],
        css=STYLING,
    )


def build_package(source_apkg: Path, audio_dir: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    facts = load_supported_facts(source_apkg)
    model = build_model()
    deck_names = configured_deck_names()
    decks = {
        deck_name: genanki.Deck(DECK_IDS[deck_name], deck_name)
        for deck_name in deck_names
    }
    media_files: list[str] = []

    with tempfile.TemporaryDirectory() as temp_dir:
        media_dir = Path(temp_dir)
        for fact in facts:
            visual_name = visual_filename(fact)
            visual_path = media_dir / visual_name
            visual_path.write_text(render_fact_svg(fact), encoding="utf-8")

            prompt_path = audio_dir / prompt_audio_filename(fact)
            answer_path = audio_dir / answer_audio_filename(fact)
            celebration_name = celebration_audio_filename(fact)
            celebration_path = audio_dir / celebration_name

            ensure_media_file(prompt_path)
            ensure_media_file(answer_path)
            ensure_media_file(celebration_path)

            fields = build_note_fields(fact, visual_name, celebration_name)
            note_fields = note_fields_in_order(fields)
            for deck_name in fact.deck_names:
                note = genanki.Note(
                    model=model,
                    fields=note_fields,
                    guid=note_guid(fact, deck_name),
                )
                decks[deck_name].add_note(note)

            media_files.extend([str(visual_path), str(prompt_path), str(answer_path), str(celebration_path)])

        genanki.Package(
            [decks[deck_name] for deck_name in deck_names],
            media_files=sorted(set(media_files)),
        ).write_to_file(output_path)

    return output_path


def inspect_package(output_path: Path) -> PackageSummary:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(output_path) as archive:
            archive.extract("collection.anki2", temp_path)

        conn = sqlite3.connect(temp_path / "collection.anki2")
        decks_json = conn.execute("select decks from col").fetchone()[0]
        deck_config = json.loads(decks_json)

        deck_id_to_name = {int(deck_id): data["name"] for deck_id, data in deck_config.items()}
        rows = conn.execute("select did, count(*) from cards group by did").fetchall()
        conn.close()

    deck_card_counts: dict[str, int] = {}
    for deck_id, count in rows:
        name = deck_id_to_name.get(deck_id)
        if name is None or name == "Default":
            continue
        deck_card_counts[name] = count

    return PackageSummary(
        deck_names=set(deck_card_counts),
        deck_card_counts=deck_card_counts,
        total_cards=sum(deck_card_counts.values()),
    )


def main() -> None:
    args = parse_args()
    audio_dir = default_audio_dir(args.source_apkg, args.audio_dir)
    output_path = default_output_path(args.source_apkg, args.output)
    print(build_package(args.source_apkg, audio_dir, output_path))


if __name__ == "__main__":
    main()
