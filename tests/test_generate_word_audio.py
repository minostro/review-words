from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.generate_word_audio import should_skip_existing_audio


class GenerateWordAudioTest(unittest.TestCase):
    def test_should_not_skip_zero_byte_audio_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "empty.mp3"
            audio_path.write_bytes(b"")

            self.assertFalse(should_skip_existing_audio(audio_path))

    def test_should_skip_non_empty_audio_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "word.mp3"
            audio_path.write_bytes(b"audio")

            self.assertTrue(should_skip_existing_audio(audio_path))


if __name__ == "__main__":
    unittest.main()
