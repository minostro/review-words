from __future__ import annotations

import re
import sqlite3
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path


FACT_PATTERN = re.compile(r"^\s*(\d+)\s*X\s*(\d+)\s*=\s*\?\s*$")


@dataclass(frozen=True)
class MultiplicationFact:
    left: int
    right: int
    answer: int
    front: str
    back: str
    subdeck_name: str


def target_subdeck_name(table: int) -> str:
    if 2 <= table <= 4:
        return "Tables::2-4"
    if 5 <= table <= 10:
        return "Tables::5-10"
    raise ValueError(f"Unsupported table: {table}")


def parse_source_fact(front: str, back: str) -> MultiplicationFact:
    match = FACT_PATTERN.match(front)
    if match is None:
        raise ValueError(f"Unsupported front format: {front}")

    left = int(match.group(1))
    right = int(match.group(2))
    if 2 <= right <= 10:
        subdeck_name = target_subdeck_name(right)
    else:
        subdeck_name = ""
    return MultiplicationFact(
        left=left,
        right=right,
        answer=int(back.strip()),
        front=front,
        back=back,
        subdeck_name=subdeck_name,
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
        if 1 <= fact.left <= 10 and 2 <= fact.right <= 10:
            facts.append(fact)
    return facts
