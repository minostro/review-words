"""Combine generated subject packages into one offline Salvador distribution.

This accepts new-card distribution APKGs, not collection backups or study-history
exports. Original note GUIDs, model IDs, templates, fields and media are retained.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import zipfile

import genanki

SUBJECT_PREFIXES = {
    'Reading': 'Salvador Review Words::Storybook Audio',
    'Multiplication': 'Tables',
    'English': 'Salvador English Spelling',
    'Social Science': 'Salvador::Social Science - Oct - 2026',
}


class DestinationCard(genanki.Card):
    def __init__(self, ordinal, destination, suspend=False):
        super().__init__(ordinal, suspend=suspend)
        self.destination = destination

    def write_to_db(self, cursor, timestamp, deck_id, note_id, id_gen, due=0):
        super().write_to_db(cursor, timestamp, self.destination, note_id, id_gen, due)


def subject_deck_name(subject, original):
    prefix = SUBJECT_PREFIXES[subject]
    suffix = original[len(prefix):] if original == prefix or original.startswith(prefix + '::') else '::' + original
    child = 'Social Science - Oct - 2026' if subject == 'Social Science' else subject
    return f'Salvador::{child}{suffix}'


def build_bundle(sources: dict[str, Path], output: Path) -> dict:
    if not sources or set(sources) - SUBJECT_PREFIXES.keys():
        raise ValueError('Provide Reading, Multiplication, English and/or Social Science source packages.')
    if output.resolve() in {path.resolve() for path in sources.values()}:
        raise ValueError('Output must not replace a source package.')
    decks, models, seen_guids, media, counts = {}, {}, set(), {}, {}
    with tempfile.TemporaryDirectory(prefix='salvador-bundle-') as temporary:
        workspace = Path(temporary)
        for subject, source in sources.items():
            with zipfile.ZipFile(source) as archive:
                if 'collection.anki2' not in archive.namelist():
                    raise ValueError(f'{source}: expected a generated legacy APKG with collection.anki2.')
                db_path = workspace / f'{subject}.sqlite'
                db_path.write_bytes(archive.read('collection.anki2'))
                with closing(sqlite3.connect(db_path)) as db:
                    db.row_factory = sqlite3.Row
                    if db.execute('SELECT count(*) FROM revlog').fetchone()[0] or db.execute('SELECT count(*) FROM cards WHERE type != 0').fetchone()[0]:
                        raise ValueError(f'{source}: study history is not supported; use the generated distribution package.')
                    collection = db.execute('SELECT models, decks FROM col').fetchone()
                    source_decks = json.loads(collection['decks'])
                    source_models = json.loads(collection['models'])
                    notes = db.execute('SELECT * FROM notes ORDER BY id').fetchall()
                    cards = db.execute('SELECT nid, did, ord, queue FROM cards ORDER BY nid, ord').fetchall()
                by_note = {}
                for card in cards:
                    by_note.setdefault(card['nid'], []).append(card)
                    deck_id = card['did']
                    name = subject_deck_name(subject, source_decks[str(deck_id)]['name'])
                    if deck_id in decks and decks[deck_id].name != name:
                        raise ValueError(f'Deck ID conflict: {deck_id}')
                    decks.setdefault(deck_id, genanki.Deck(deck_id, name))
                for identifier, original in source_models.items():
                    model_id = int(identifier)
                    if model_id in models:
                        raise ValueError(f'Model ID conflict: {identifier}')
                    models[model_id] = genanki.Model(
                        model_id, original['name'], fields=original['flds'], templates=original['tmpls'],
                        css=original['css'], model_type=original['type'], sort_field_index=original['sortf'],
                        latex_pre=original['latexPre'], latex_post=original['latexPost'],
                    )
                for row in notes:
                    if row['guid'] in seen_guids:
                        raise ValueError(f'Duplicate note GUID: {row["guid"]}')
                    seen_guids.add(row['guid'])
                    original_cards = by_note.get(row['id'], [])
                    if not original_cards:
                        raise ValueError(f'Note without cards in {source}: {row["guid"]}')
                    note = genanki.Note(
                        models[row['mid']], fields=row['flds'].split('\x1f'), guid=row['guid'],
                        tags=list(dict.fromkeys(row['tags'].split() + [f'subject::{subject.lower().replace(" ", "_")}'])),
                        due=len(seen_guids),
                    )
                    note.cards = [DestinationCard(card['ord'], card['did'], card['queue'] == -1) for card in original_cards]
                    decks[original_cards[0]['did']].add_note(note)
                counts[subject] = {'notes': len(notes), 'cards': len(cards)}
                for member, name in json.loads(archive.read('media')).items():
                    if not name or '/' in name or '\\' in name or name in {'.', '..'}:
                        raise ValueError(f'Unsafe media filename: {name!r}')
                    data = archive.read(member)
                    if name in media and media[name] != data:
                        raise ValueError(f'Media filename conflict: {name}')
                    media[name] = data

        # Include actual parent decks, so one visible root contains every subject.
        names = {deck.name for deck in decks.values()}
        ancestors = { '::'.join(name.split('::')[:depth]) for name in names
                      for depth in range(1, len(name.split('::'))) }
        for name in sorted(ancestors - names):
            identifier = int.from_bytes(hashlib.sha256(('salvador-deck:' + name).encode()).digest()[:6], 'big')
            if identifier in decks:
                raise ValueError(f'Parent deck ID collision: {name}')
            decks[identifier] = genanki.Deck(identifier, name)
        media_dir = workspace / 'media'
        media_dir.mkdir()
        media_paths = []
        for name, data in sorted(media.items()):
            path = media_dir / name
            path.write_bytes(data)
            media_paths.append(str(path))
        staged = workspace / 'Salvador.apkg'
        genanki.Package(list(decks.values()), media_files=media_paths).write_to_file(staged)
        # Build completely before replacing a previous good distribution.
        output.parent.mkdir(parents=True, exist_ok=True)
        pending = output.with_suffix('.apkg.tmp')
        pending.write_bytes(staged.read_bytes())
        pending.replace(output)
    return {'subjects': counts, 'notes': len(seen_guids),
            'cards': sum(value['cards'] for value in counts.values()), 'media': len(media)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reading', type=Path, default=Path('out/salvador_review_words_storybook_audio_v7_2026-10-04.apkg'))
    parser.add_argument('--multiplication', type=Path, default=Path('out/1_to_20_Multiplication_Tables_100_accurate_value_animal_multiplication.apkg'))
    parser.add_argument('--english', type=Path, default=Path('out/english-spelling/Salvador-English-Spelling.apkg'))
    parser.add_argument('--social-science', type=Path, default=Path('out/social-science/Social-Science-Oct-2026.apkg'))
    parser.add_argument('--output', type=Path, default=Path('out/salvador/Salvador.apkg'))
    args = parser.parse_args()
    sources = {'Reading': args.reading, 'Multiplication': args.multiplication, 'English': args.english,
               'Social Science': args.social_science}
    result = build_bundle(sources, args.output)
    print(json.dumps(result, indent=2))
    print(args.output.resolve())


if __name__ == '__main__':
    main()
