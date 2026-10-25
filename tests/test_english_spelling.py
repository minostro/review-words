import json
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.english_spelling_content import ITEMS, completion_masks, picture_html
from scripts.build_english_spelling_apkg import build_package


class SpellingContentTests(unittest.TestCase):
    def test_source_coverage(self):
        self.assertEqual(len(ITEMS), 31)
        self.assertEqual(sum(item.unit == 1 for item in ITEMS), 16)
        self.assertEqual(sum(item.unit == 2 for item in ITEMS), 15)
        self.assertEqual(len({item.key for item in ITEMS}), 31)
        targets = {item.answer for item in ITEMS}
        self.assertTrue({'leaf', 'leaves', 'Wednesday', "mustn't", 'to wash your hands', 'to write an email'} <= targets)

    def test_three_patterns_cover_every_letter_and_preserve_punctuation(self):
        for item in ITEMS:
            masks = completion_masks(item.answer)
            with self.subTest(item=item.answer):
                self.assertEqual(len({tuple(mask) for mask in masks}), 3)
                self.assertTrue(all(mask for mask in masks))
                letters = {i for i, c in enumerate(item.answer) if c.isalpha()}
                self.assertEqual(set().union(*map(set, masks)), letters)
                self.assertTrue(all(set(mask) < letters for mask in masks))

    def test_picture_has_media_reference_without_answer_label(self):
        for item in ITEMS:
            markup = picture_html(item)
            self.assertIn('<img', markup)
            self.assertNotIn(item.answer, markup)
            self.assertIn('alt="Vocabulary illustration"', markup)


class PackageTests(unittest.TestCase):
    def test_real_package_note_card_deck_and_media_structure(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            audio = root / 'audio'
            audio.mkdir()
            for item in ITEMS:
                (audio / item.audio_filename).write_bytes(b'ID3' + b'\0' * 100)
            target = root / 'test.apkg'
            build_package(target, audio)
            with zipfile.ZipFile(target) as archive:
                archive.extract('collection.anki2', root)
                media = json.loads(archive.read('media'))
                self.assertEqual(len(media), 33)
                self.assertEqual(len(set(media.values())), 33)
            con = sqlite3.connect(root / 'collection.anki2')
            self.assertEqual(con.execute('select count(*) from notes').fetchone()[0], 31)
            self.assertEqual(con.execute('select count(*) from cards').fetchone()[0], 124)
            self.assertEqual(con.execute('select count(distinct did) from cards').fetchone()[0], 8)
            self.assertEqual(con.execute('select count(*) from (select nid from cards group by nid having count(*) = 4)').fetchone()[0], 31)
            models = json.loads(con.execute('select models from col').fetchone()[0])
            self.assertEqual(len(models), 2)
            for model in models.values():
                self.assertEqual(len(model['tmpls']), 4)
                self.assertNotIn('FrontSide', model['tmpls'][0]['afmt'])
            con.close()

    def test_missing_audio_fails_before_writing_package(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaises(FileNotFoundError):
                build_package(root / 'bad.apkg', root)
            self.assertFalse((root / 'bad.apkg').exists())


if __name__ == '__main__':
    unittest.main()
