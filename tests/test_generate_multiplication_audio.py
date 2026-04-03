from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.generate_multiplication_audio import build_audio_jobs, should_skip_existing_audio
from scripts.multiplication_common import MultiplicationFact


class GenerateMultiplicationAudioTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fact = MultiplicationFact(
            left=3,
            right=4,
            answer=12,
            front="3 X 4 = ?",
            back="12",
            subdeck_name="Tables::2-4",
        )

    def test_build_audio_jobs_creates_prompt_and_answer_jobs(self) -> None:
        jobs = build_audio_jobs([self.fact])
        self.assertEqual(jobs[0].filename, "fact_03x04_prompt.mp3")
        self.assertEqual(jobs[1].filename, "fact_03x04_answer.mp3")

    def test_celebration_jobs_are_reused(self) -> None:
        jobs = build_audio_jobs([self.fact])
        celebration_files = {job.filename for job in jobs if job.kind == "celebration"}
        self.assertEqual(celebration_files, {"celebration_01.mp3", "celebration_02.mp3", "celebration_03.mp3"})

    def test_should_not_skip_zero_byte_audio_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "empty.mp3"
            audio_path.write_bytes(b"")
            self.assertFalse(should_skip_existing_audio(audio_path))

    def test_should_skip_non_empty_audio_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "audio.mp3"
            audio_path.write_bytes(b"audio")
            self.assertTrue(should_skip_existing_audio(audio_path))


if __name__ == "__main__":
    unittest.main()
