import json
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path

import genanki
from scripts.build_salvador_apkg import build_bundle


def sample_package(root, subject, *, media_bytes=b'example', filename='shared.mp3'):
    index = {'Reading': 1, 'Multiplication': 2, 'English': 3, 'Social Science': 4}[subject]
    deck_name = {'Reading': 'Salvador Review Words::Storybook Audio',
                 'Multiplication': 'Tables::2-4', 'English': 'Salvador English Spelling::Unit 1',
                 'Social Science': 'Salvador::Social Science - Oct - 2026'}[subject]
    model = genanki.Model(9000 + index, subject, fields=[{'name': 'Front'}, {'name': 'Audio'}],
                          templates=[{'name': 'Card', 'qfmt': '{{Front}} {{Audio}}', 'afmt': '{{Front}}'}])
    deck = genanki.Deck(8000 + index, deck_name)
    deck.add_note(genanki.Note(model, fields=[subject, f'[sound:{filename}]'], guid=f'fixed-{subject}'))
    audio_dir = root / subject
    audio_dir.mkdir(exist_ok=True)
    audio = audio_dir / filename
    audio.write_bytes(media_bytes)
    output = root / f'{subject}.apkg'
    genanki.Package(deck, media_files=[str(audio)]).write_to_file(output)
    return output


class BundleTests(unittest.TestCase):
    def test_social_science_is_one_exact_child_alongside_existing_subjects(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            sources={subject:sample_package(root,subject) for subject in ('Reading','Multiplication','English','Social Science')}
            output=root/'all.apkg'
            result=build_bundle(sources,output)
            self.assertEqual(result['cards'],4)
            with zipfile.ZipFile(output) as archive:
                archive.extract('collection.anki2',root)
            with sqlite3.connect(root/'collection.anki2') as db:
                decks=json.loads(db.execute('select decks from col').fetchone()[0])
                social_names=[d['name'] for d in decks.values() if 'Social Science' in d['name']]
                self.assertEqual(social_names,['Salvador::Social Science - Oct - 2026'])
                tags=db.execute("select tags from notes where guid='fixed-Social Science'").fetchone()[0]
                self.assertIn('subject::social_science',tags.split())

    def test_preserves_notes_media_and_subject_hierarchy(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            sources = {subject: sample_package(root, subject) for subject in ('Reading', 'Multiplication', 'English')}
            output = root / 'Salvador.apkg'
            result = build_bundle(sources, output)
            self.assertEqual(result['notes'], 3)
            self.assertEqual(result['cards'], 3)
            self.assertEqual(result['media'], 1)
            with zipfile.ZipFile(output) as archive:
                archive.extract('collection.anki2', root)
                manifest = json.loads(archive.read('media'))
                self.assertEqual(set(manifest.values()), {'shared.mp3'})
                self.assertEqual(archive.read(next(iter(manifest))), b'example')
            with sqlite3.connect(root / 'collection.anki2') as db:
                self.assertEqual({r[0] for r in db.execute('select guid from notes')},
                                 {'fixed-Reading', 'fixed-Multiplication', 'fixed-English'})
                decks = json.loads(db.execute('select decks from col').fetchone()[0])
                self.assertEqual({decks[str(row[0])]['name'] for row in db.execute('select did from cards')},
                                 {'Salvador::Reading', 'Salvador::Multiplication::2-4', 'Salvador::English::Unit 1'})
                self.assertIn('Salvador', {d['name'] for d in decks.values()})
                self.assertTrue(all('subject::' in row[0] for row in db.execute('select tags from notes')))

    def test_media_name_collision_fails_without_overwriting_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            a = sample_package(root, 'Reading', media_bytes=b'first')
            b = sample_package(root, 'English', media_bytes=b'second')
            output = root / 'Salvador.apkg'
            output.write_bytes(b'previous good package')
            with self.assertRaisesRegex(ValueError, 'Media filename conflict'):
                build_bundle({'Reading': a, 'English': b}, output)
            self.assertEqual(output.read_bytes(), b'previous good package')

    def test_duplicate_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = sample_package(root, 'Reading')
            with self.assertRaisesRegex(ValueError, 'Duplicate note GUID|Deck ID conflict'):
                build_bundle({'Reading': source, 'English': source}, root / 'out.apkg')


if __name__ == '__main__':
    unittest.main()
