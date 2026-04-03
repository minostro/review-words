from __future__ import annotations

import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.build_multiplication_apkg import (
    STYLING,
    answer_audio_filename,
    build_note_fields,
    build_package,
    celebration_audio_filename,
    inspect_package,
    prompt_audio_filename,
)
from scripts.multiplication_common import MultiplicationFact, load_supported_facts


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


class BuildMultiplicationApkgTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fact = MultiplicationFact(
            left=3,
            right=4,
            answer=12,
            front="3 X 4 = ?",
            back="12",
            subdeck_name="Tables::2-4",
        )

    def test_notes_include_visual_and_audio_markup(self) -> None:
        fields = build_note_fields(self.fact, "fact_03x04.svg", "celebration_01.mp3")
        self.assertEqual(fields["Prompt"], "3 X 4 = ?")
        self.assertIn('<img src="fact_03x04.svg"', fields["Visual"])
        self.assertEqual(fields["PromptAudio"], "[sound:fact_03x04_prompt.mp3]")
        self.assertEqual(fields["AnswerAudio"], "[sound:fact_03x04_answer.mp3]")
        self.assertEqual(fields["CelebrationAudio"], "[sound:celebration_01.mp3]")

    def test_styling_uses_explicit_high_contrast_colors_for_light_and_dark_modes(self) -> None:
        self.assertIn(".nightMode .card", STYLING)
        self.assertIn(".nightMode .prompt", STYLING)
        self.assertIn(".nightMode .answer", STYLING)
        self.assertIn("color: #0f172a", STYLING)
        self.assertIn("color: #f8fafc", STYLING)

    def test_build_package_uses_new_note_model_name_for_high_contrast_imports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_apkg = temp_path / "tables.apkg"
            audio_dir = temp_path / "audio"
            output_path = temp_path / "result.apkg"
            build_sample_apkg(source_apkg, [("1 X 2 = ?", "2")])
            for filename in [
                "fact_01x02_prompt.mp3",
                "fact_01x02_answer.mp3",
                "celebration_01.mp3",
                "celebration_02.mp3",
                "celebration_03.mp3",
            ]:
                path = audio_dir / filename
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"audio")

            build_package(source_apkg, audio_dir, output_path)

            with tempfile.TemporaryDirectory() as inspect_dir:
                inspect_path = Path(inspect_dir)
                with zipfile.ZipFile(output_path) as archive:
                    archive.extract("collection.anki2", inspect_path)
                conn = sqlite3.connect(inspect_path / "collection.anki2")
                models_json = conn.execute("select models from col").fetchone()[0]
                conn.close()

        self.assertIn("Animal Multiplication Note High Contrast", models_json)

    def test_build_package_uses_two_expected_subdecks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_apkg = temp_path / "tables.apkg"
            audio_dir = temp_path / "audio"
            output_path = temp_path / "result.apkg"
            build_sample_apkg(
                source_apkg,
                [
                    ("1 X 2 = ?", "2"),
                    ("2 X 4 = ?", "8"),
                    ("7 X 10 = ?", "70"),
                    ("1 X 11 = ?", "11"),
                ],
            )
            for filename in [
                "fact_01x02_prompt.mp3",
                "fact_01x02_answer.mp3",
                "fact_02x04_prompt.mp3",
                "fact_02x04_answer.mp3",
                "fact_07x10_prompt.mp3",
                "fact_07x10_answer.mp3",
                "celebration_01.mp3",
                "celebration_02.mp3",
                "celebration_03.mp3",
            ]:
                path = audio_dir / filename
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"audio")

            build_package(source_apkg, audio_dir, output_path)
            summary = inspect_package(output_path)

        self.assertEqual(summary.deck_names, {"Tables::2-4", "Tables::5-10"})
        self.assertEqual(summary.deck_card_counts["Tables::2-4"], 2)
        self.assertEqual(summary.deck_card_counts["Tables::5-10"], 1)
        self.assertEqual(summary.total_cards, 3)

    def test_built_package_contains_expected_card_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_apkg = temp_path / "tables.apkg"
            audio_dir = temp_path / "audio"
            output_path = temp_path / "result.apkg"
            notes = []
            for right in range(1, 21):
                for left in range(1, 21):
                    notes.append((f"{left} X {right} = ?", str(left * right)))
            build_sample_apkg(source_apkg, notes)

            for fact in load_supported_facts(source_apkg):
                for filename in [
                    prompt_audio_filename(fact),
                    answer_audio_filename(fact),
                    celebration_audio_filename(fact),
                ]:
                    path = audio_dir / filename
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(b"audio")

            build_package(source_apkg, audio_dir, output_path)
            summary = inspect_package(output_path)

        self.assertEqual(summary.total_cards, 90)
        self.assertEqual(summary.deck_card_counts["Tables::2-4"], 30)
        self.assertEqual(summary.deck_card_counts["Tables::5-10"], 60)


if __name__ == "__main__":
    unittest.main()
