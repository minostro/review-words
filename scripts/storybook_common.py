from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


FRONT_TMPL = """
<div class="card-wrap">
  <div class="word">{{Front}}</div>
</div>
"""

BACK_TMPL = """
<div class="card-wrap">
  <div class="word small">{{Front}}</div>
  <div class="syllables">{{Syllables}}</div>
  <div class="sentence">{{Example Sentence}}</div>
</div>
"""

BACK_AUDIO_TMPL = """
<div class="card-wrap">
  <div class="word small">{{Front}}</div>
  <div class="syllables">{{Syllables}}</div>
  <div class="sentence">{{Example Sentence}}</div>
  <div class="audio">{{Audio}}</div>
</div>
"""

STYLING = """
.card {
  font-family: -apple-system, BlinkMacSystemFont, "Avenir Next", "Helvetica Neue", sans-serif;
  background: #f7f1e3;
  color: #16324f;
  margin: 0;
  padding: 0;
}

.card-wrap {
  min-height: 100vh;
  box-sizing: border-box;
  padding: 40px 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background:
    radial-gradient(circle at top right, #fff7d6 0%, transparent 30%),
    radial-gradient(circle at bottom left, #dff3ff 0%, transparent 28%),
    #f7f1e3;
}

.word {
  font-size: 56px;
  line-height: 1.1;
  font-weight: 700;
  text-align: center;
  letter-spacing: 0.5px;
  padding: 24px 28px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.55);
  box-shadow: 0 10px 30px rgba(22, 50, 79, 0.10);
}

.word.small {
  font-size: 38px;
  margin-bottom: 20px;
}

.syllables {
  margin-top: 8px;
  font-size: 30px;
  font-weight: 600;
  color: #2f5d62;
  letter-spacing: 2px;
  text-align: center;
}

.sentence {
  margin-top: 28px;
  max-width: 620px;
  font-size: 30px;
  line-height: 1.4;
  text-align: center;
  padding: 22px 24px;
  border-radius: 22px;
  background: #fffdf8;
  border: 3px solid #ffd6a5;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.audio {
  margin-top: 22px;
}

.nightMode .card {
  background: #1f2937;
  color: #f9fafb;
}

.nightMode .card-wrap {
  background:
    radial-gradient(circle at top right, rgba(255, 214, 165, 0.10) 0%, transparent 30%),
    radial-gradient(circle at bottom left, rgba(125, 211, 252, 0.10) 0%, transparent 28%),
    #1f2937;
}

.nightMode .word {
  background: rgba(255, 255, 255, 0.06);
  box-shadow: none;
}

.nightMode .syllables {
  color: #93c5fd;
}

.nightMode .sentence {
  background: rgba(255, 255, 255, 0.06);
  border-color: #fdba74;
}
"""


@dataclass(frozen=True)
class CardRow:
    index: int
    front: str
    syllables: str
    example_sentence: str
    tags: list[str]


def normalize_filename_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    slug = re.sub(r"[^a-z0-9]+", "_", without_accents.lower()).strip("_")
    return slug or "word"


def audio_filename(index: int, word: str) -> str:
    return f"{index:03d}_{normalize_filename_text(word)}.mp3"


def audio_field_value(filename: str) -> str:
    return f"[sound:{filename}]"


def display_syllables(syllables: str) -> str:
    return syllables.replace("-", " · ")


def load_cards(csv_path: Path) -> list[CardRow]:
    cards: list[CardRow] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, start=1):
            cards.append(
                CardRow(
                    index=index,
                    front=row["Front"],
                    syllables=row["Syllables"],
                    example_sentence=row["Example sentence"],
                    tags=[tag for tag in row["Tags"].split() if tag],
                )
            )
    return cards


def default_output_path(csv_path: Path, suffix: str, output_path: Path | None) -> Path:
    if output_path is not None:
        return output_path
    return Path("out") / f"{csv_path.stem}_{suffix}.apkg"


def default_audio_dir(csv_path: Path, audio_dir: Path | None) -> Path:
    if audio_dir is not None:
        return audio_dir
    return Path("out") / "audio" / csv_path.stem
