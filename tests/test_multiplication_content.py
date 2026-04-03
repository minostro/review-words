from __future__ import annotations

import unittest

from scripts.multiplication_common import MultiplicationFact
from scripts.multiplication_content import animal_name, answer_audio_text, playful_prompt_text, prompt_audio_text


class MultiplicationContentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fact = MultiplicationFact(
            left=3,
            right=4,
            answer=12,
            front="3 X 4 = ?",
            back="12",
            subdeck_name="Tables::2-4",
        )

    def test_prompt_audio_text_uses_spanish_number_words(self) -> None:
        self.assertEqual(prompt_audio_text(self.fact), "tres por cuatro")

    def test_answer_audio_text_uses_spanish_result(self) -> None:
        self.assertEqual(answer_audio_text(self.fact), "doce")

    def test_playful_prompt_is_deterministic(self) -> None:
        self.assertEqual(playful_prompt_text(self.fact), "Da 12 palmadas")

    def test_animal_name_is_deterministic(self) -> None:
        self.assertEqual(animal_name(self.fact), "pinguinos")


if __name__ == "__main__":
    unittest.main()
