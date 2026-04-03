from __future__ import annotations

import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.multiplication_common import load_supported_facts, parse_source_fact, target_subdeck_name


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

    def test_load_supported_facts_ignores_tables_above_ten(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            apkg_path = Path(temp_dir) / "tables.apkg"
            build_sample_apkg(
                apkg_path,
                [
                    ("1 X 2 = ?", "2"),
                    ("2 X 4 = ?", "8"),
                    ("7 X 10 = ?", "70"),
                    ("12 X 4 = ?", "48"),
                    ("1 X 11 = ?", "11"),
                    ("3 X 20 = ?", "60"),
                ],
            )

            facts = load_supported_facts(apkg_path)

        self.assertEqual([fact.front for fact in facts], ["1 X 2 = ?", "2 X 4 = ?", "7 X 10 = ?"])
        self.assertEqual([fact.subdeck_name for fact in facts], ["Tables::2-4", "Tables::2-4", "Tables::5-10"])


if __name__ == "__main__":
    unittest.main()
