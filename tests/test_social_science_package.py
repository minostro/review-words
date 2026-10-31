import json
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.social_science_content import ITEMS
from scripts.build_social_science_apkg import build_package, fields_for, question_audio_filename, FIELD_NAMES
from scripts.social_science_templates import FRONT, BACK


class SocialPackageTests(unittest.TestCase):
    def test_manual_audio_has_no_native_sound_tag_on_either_side(self):
        for item in ITEMS:
            fields = fields_for(item)
            for template in (FRONT, BACK):
                for key, value in zip(FIELD_NAMES, fields):
                    template = template.replace('{{' + key + '}}', value)
                self.assertNotIn('[sound:', template)
                self.assertNotIn(' autoplay', template)
                self.assertIn('Hear question', template)
                self.assertIn(question_audio_filename(item), template)
                self.assertIn('<img', template)
                self.assertNotIn('{{', template)

    def test_package_is_one_exact_subdeck_and_includes_all_media(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for item in ITEMS:
                (root / question_audio_filename(item)).write_bytes(b'ID3' + b'\0' * 100)
            path = root / 'social.apkg'
            build_package(path, root)
            with zipfile.ZipFile(path) as z:
                z.extract('collection.anki2', root)
                media = json.loads(z.read('media'))
                self.assertEqual(len(media), len(ITEMS) + 31)
            with sqlite3.connect(root / 'collection.anki2') as db:
                self.assertEqual(db.execute('select count(*) from notes').fetchone()[0],len(ITEMS))
                self.assertEqual(db.execute('select count(*) from cards').fetchone()[0],len(ITEMS))
                decks=json.loads(db.execute('select decks from col').fetchone()[0])
                self.assertEqual({decks[str(r[0])]['name'] for r in db.execute('select did from cards')},
                                 {'Salvador::Social Science - Oct - 2026'})
                self.assertTrue(all('[sound:social-oct26-' in r[0] for r in db.execute('select flds from notes')))

    def test_missing_audio_rejects_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                build_package(Path(tmp)/'bad.apkg',Path(tmp))
