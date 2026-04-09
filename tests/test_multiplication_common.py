from __future__ import annotations

import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.multiplication_common import configured_deck_names, load_supported_facts, parse_source_fact, target_subdeck_name


def build_sample_apkg(apkg_path: Path, notes: list[tuple[str, str]]) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        db_path = temp_path / "collection.anki2"
        conn = sqlite3.connect(db_path)
        conn.execute("create table notes(id integer primary key, flds text not null)")
        for index, (front, back) in enumerate(notes, start=1):
            conn.execute(
                "insert into notes(id, flds) values (?, ?)",
                (index, f"{front}{chr(31)}{back}"),
            )
        conn.commit()
        conn.close()

        media_path = temp_path / "media"
        media_path.write_text("{}", encoding="utf-8")

        with zipfile.ZipFile(apkg_path, "w") as archive:
            archive.write(db_path, "collection.anki2")
            archive.write(media_path, "media")


class MultiplicationCommonTest(unittest.TestCase):
    def test_parse_front_extracts_operands_and_answer(self) -> None:
        fact = parse_source_fact("3 X 4 = ?", "12")
        self.assertEqual((fact.left, fact.right, fact.answer), (3, 4, 12))

    def test_target_subdeck_for_supported_tables(self) -> None:
        self.assertEqual(target_subdeck_name(4), "Tables::2-4")
        self.assertEqual(target_subdeck_name(7), "Tables::5-10")

    def test_configured_deck_names_include_broad_and_focused_decks(self) -> None:
        self.assertEqual(
            configured_deck_names(),
            (
                "Tables::2-4",
                "Tables::5-10",
                "Tables::Focused::2 x 1-5",
                "Tables::Focused::2 x 6-10",
                "Tables::Focused::3 x 1-5",
                "Tables::Focused::3 x 6-10",
                "Tables::Focused::4 x 1-5",
                "Tables::Focused::4 x 6-10",
                "Tables::Focused::5 x 1-5",
                "Tables::Focused::5 x 6-10",
            ),
        )

    def test_parse_source_fact_assigns_broad_and_focused_decks(self) -> None:
        fact = parse_source_fact("5 X 4 = ?", "20")
        self.assertEqual(fact.subdeck_name, "Tables::2-4")
        self.assertEqual(
            fact.deck_names,
            ("Tables::2-4", "Tables::Focused::4 x 1-5", "Tables::Focused::5 x 1-5"),
        )

    def test_parse_source_fact_keeps_one_facts_only_for_focused_decks(self) -> None:
        fact = parse_source_fact("5 X 1 = ?", "5")
        self.assertEqual(fact.subdeck_name, "")
        self.assertEqual(fact.deck_names, ("Tables::Focused::5 x 1-5",))

    def test_load_supported_facts_includes_requested_one_facts_and_ignores_unused_ones(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            apkg_path = Path(temp_dir) / "tables.apkg"
            build_sample_apkg(
                apkg_path,
                [
                    ("1 X 2 = ?", "2"),
                    ("2 X 4 = ?", "8"),
                    ("7 X 10 = ?", "70"),
                    ("2 X 1 = ?", "2"),
                    ("3 X 1 = ?", "3"),
                    ("4 X 1 = ?", "4"),
                    ("5 X 1 = ?", "5"),
                    ("5 X 4 = ?", "20"),
                    ("7 X 1 = ?", "7"),
                    ("12 X 4 = ?", "48"),
                    ("1 X 11 = ?", "11"),
                    ("3 X 20 = ?", "60"),
                ],
            )

            facts = load_supported_facts(apkg_path)

        self.assertEqual(
            [fact.front for fact in facts],
            ["1 X 2 = ?", "2 X 4 = ?", "7 X 10 = ?", "2 X 1 = ?", "3 X 1 = ?", "4 X 1 = ?", "5 X 1 = ?", "5 X 4 = ?"],
        )
        self.assertEqual(
            [fact.deck_names for fact in facts],
            [
                ("Tables::2-4", "Tables::Focused::2 x 1-5"),
                ("Tables::2-4", "Tables::Focused::2 x 1-5", "Tables::Focused::4 x 1-5"),
                ("Tables::5-10",),
                ("Tables::Focused::2 x 1-5",),
                ("Tables::Focused::3 x 1-5",),
                ("Tables::Focused::4 x 1-5",),
                ("Tables::Focused::5 x 1-5",),
                ("Tables::2-4", "Tables::Focused::4 x 1-5", "Tables::Focused::5 x 1-5"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
