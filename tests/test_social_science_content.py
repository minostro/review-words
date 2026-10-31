from __future__ import annotations

from collections import Counter
from dataclasses import FrozenInstanceError
import importlib
import importlib.util
import unittest


class SocialScienceContentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.assertIsNotNone(
            importlib.util.find_spec("scripts.social_science_content"),
            "The approved Social Science comprehension content must exist.",
        )
        self.content = importlib.import_module("scripts.social_science_content")

    def test_all_worksheet_topics_are_covered_without_duplicate_variants(self) -> None:
        items = self.content.ITEMS
        self.assertIsInstance(items, tuple)
        self.assertEqual(len(items), 44)
        self.assertEqual(Counter(item.category for item in items), {
            "school-places": 10, "school-workers": 8, "family": 11,
            "settlements": 4, "community-helpers": 8, "community": 3,
        })
        self.assertEqual(len({item.key for item in items}), len(items))
        self.assertEqual(len({item.question.casefold().strip() for item in items}), len(items))
        expected_answers = {
            "classroom", "playground", "library", "lab", "gym", "canteen",
            "reception", "toilets", "art-room", "nurse-office", "teacher",
            "headmaster", "school-nurse", "cook", "caretaker", "cleaner",
            "receptionist", "librarian", "mum", "dad", "sister", "brother",
            "grandma", "grandpa", "baby", "aunt", "uncle", "cousin", "pet",
            "neighbourhood", "village", "town", "city", "mayor", "doctor",
            "gardener", "firefighter", "police-officer", "bus-driver",
            "postman", "street-cleaner", "community-helpers", "public-services",
            "local-council",
        }
        self.assertEqual({item.correct for item in items}, expected_answers)

    def test_questions_have_three_distinct_answers_and_an_explanation(self) -> None:
        for item in self.content.ITEMS:
            with self.subTest(item=item.key):
                self.assertTrue(item.question.endswith("?"))
                self.assertTrue(item.explanation.strip())
                self.assertIsInstance(item.choices, tuple)
                self.assertEqual(len(item.choices), 3)
                self.assertEqual(len({choice.key for choice in item.choices}), 3)
                self.assertEqual(len({choice.label.casefold() for choice in item.choices}), 3)
                self.assertIn(item.correct, {choice.key for choice in item.choices})
                for choice in item.choices:
                    self.assertTrue(choice.label.strip())
                    self.assertNotIn(choice.label.casefold(), {"true", "false", "yes", "no"})
                self.assertNotIn("spell", item.question.casefold())

    def test_images_do_not_single_out_the_answer(self) -> None:
        image_categories = {"school-places", "school-workers", "community-helpers"}
        for item in self.content.ITEMS:
            with self.subTest(item=item.key):
                if item.category in image_categories:
                    self.assertEqual({choice.image for choice in item.choices},
                                     {choice.key for choice in item.choices})
                    self.assertEqual(item.image, "")
                if item.category == "family":
                    self.assertEqual(item.image, "family")
                    self.assertTrue(all(choice.image == "" for choice in item.choices))

    def test_synonyms_are_one_relationship_answer(self) -> None:
        family_labels = {choice.key: choice.label for item in self.content.ITEMS
                         if item.category == "family" for choice in item.choices}
        for key, synonym in (("mum", "mother"), ("dad", "father"),
                             ("grandma", "grandmother"), ("grandpa", "grandfather")):
            self.assertIn(synonym, family_labels[key].casefold())

    def test_content_records_are_frozen(self) -> None:
        item = self.content.ITEMS[0]
        with self.assertRaises(FrozenInstanceError):
            item.question = "Changed?"
        with self.assertRaises(FrozenInstanceError):
            item.choices[0].label = "Changed"


if __name__ == "__main__":
    unittest.main()
