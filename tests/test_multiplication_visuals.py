from __future__ import annotations

import unittest

from scripts.multiplication_common import MultiplicationFact
from scripts.multiplication_visuals import render_fact_svg, visual_filename


class MultiplicationVisualsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fact = MultiplicationFact(
            left=3,
            right=4,
            answer=12,
            front="3 X 4 = ?",
            back="12",
            subdeck_name="Tables::2-4",
        )

    def test_visual_filename_uses_fact_coordinates(self) -> None:
        self.assertEqual(visual_filename(self.fact), "fact_03x04.svg")

    def test_render_fact_svg_includes_group_count_and_animal_label(self) -> None:
        svg = render_fact_svg(self.fact)
        self.assertIn("3 grupos de 4 pinguinos", svg)
        self.assertIn("Total: 12", svg)
        self.assertIn('fill="#0f172a"', svg)
        self.assertIn("<svg", svg)


if __name__ == "__main__":
    unittest.main()
