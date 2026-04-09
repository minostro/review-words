from __future__ import annotations

import re
import sqlite3
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path


FACT_PATTERN = re.compile(r"^\s*(\d+)\s*X\s*(\d+)\s*=\s*\?\s*$")
BROAD_DECK_NAMES = ("Tables::2-4", "Tables::5-10")


@dataclass(frozen=True)
class FocusedDeckDefinition:
    name: str
    table: int
    other_start: int
    other_end: int

    def matches(self, left: int, right: int) -> bool:
        return (
            (left == self.table and self.other_start <= right <= self.other_end)
            or (right == self.table and self.other_start <= left <= self.other_end)
        )


FOCUSED_DECKS = (
    FocusedDeckDefinition("Tables::Focused::2 x 1-5", table=2, other_start=1, other_end=5),
    FocusedDeckDefinition("Tables::Focused::2 x 6-10", table=2, other_start=6, other_end=10),
    FocusedDeckDefinition("Tables::Focused::3 x 1-5", table=3, other_start=1, other_end=5),
    FocusedDeckDefinition("Tables::Focused::3 x 6-10", table=3, other_start=6, other_end=10),
    FocusedDeckDefinition("Tables::Focused::4 x 1-5", table=4, other_start=1, other_end=5),
    FocusedDeckDefinition("Tables::Focused::4 x 6-10", table=4, other_start=6, other_end=10),
    FocusedDeckDefinition("Tables::Focused::5 x 1-5", table=5, other_start=1, other_end=5),
    FocusedDeckDefinition("Tables::Focused::5 x 6-10", table=5, other_start=6, other_end=10),
)


@dataclass(frozen=True)
class MultiplicationFact:
    left: int
    right: int
    answer: int
    front: str
    back: str
    subdeck_name: str
    deck_names: tuple[str, ...] = ()


def configured_deck_names() -> tuple[str, ...]:
    return BROAD_DECK_NAMES + tuple(deck.name for deck in FOCUSED_DECKS)


def target_subdeck_name(table: int) -> str:
    if 2 <= table <= 4:
        return "Tables::2-4"
    if 5 <= table <= 10:
        return "Tables::5-10"
    raise ValueError(f"Unsupported table: {table}")


def matching_deck_names(left: int, right: int) -> tuple[str, ...]:
    if not (1 <= left <= 10 and 1 <= right <= 10):
        return ()

    deck_names: list[str] = []
    if 2 <= right <= 10:
        deck_names.append(target_subdeck_name(right))

    for deck in FOCUSED_DECKS:
        if deck.matches(left, right):
            deck_names.append(deck.name)

    return tuple(deck_names)


def parse_source_fact(front: str, back: str) -> MultiplicationFact:
    match = FACT_PATTERN.match(front)
    if match is None:
        raise ValueError(f"Unsupported front format: {front}")

    left = int(match.group(1))
    right = int(match.group(2))
    deck_names = matching_deck_names(left, right)
    subdeck_name = next((deck_name for deck_name in deck_names if deck_name in BROAD_DECK_NAMES), "")
    return MultiplicationFact(
        left=left,
        right=right,
        answer=int(back.strip()),
        front=front,
        back=back,
        subdeck_name=subdeck_name,
        deck_names=deck_names,
    )


def load_supported_facts(source_apkg: Path) -> list[MultiplicationFact]:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(source_apkg) as archive:
            archive.extract("collection.anki2", temp_path)

        conn = sqlite3.connect(temp_path / "collection.anki2")
        rows = conn.execute("select flds from notes order by id").fetchall()
        conn.close()

    facts: list[MultiplicationFact] = []
    for (fields_text,) in rows:
        front, back, *_rest = fields_text.split(chr(31))
        fact = parse_source_fact(front, back)
        if fact.deck_names:
            facts.append(fact)
    return facts
