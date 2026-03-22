from __future__ import annotations

import unittest

from scripts.storybook_common import audio_field_value, audio_filename, display_syllables


class StorybookCommonTest(unittest.TestCase):
    def test_audio_filename_normalizes_accents_and_symbols(self) -> None:
        self.assertEqual(audio_filename(19, "joyería"), "019_joyeria.mp3")

    def test_audio_field_value_uses_anki_sound_markup(self) -> None:
        self.assertEqual(audio_field_value("019_joyeria.mp3"), "[sound:019_joyeria.mp3]")

    def test_display_syllables_uses_middle_dots(self) -> None:
        self.assertEqual(display_syllables("jo-ye-rí-a"), "jo · ye · rí · a")


if __name__ == "__main__":
    unittest.main()
