"""Package illustrated touch spelling cards and a faithful HTML preview."""
import argparse
import html
import json
import shutil
from pathlib import Path

import genanki
from scripts.english_spelling_content import ITEMS, completion_masks, picture_html
from scripts.english_spelling_templates import BACK_TMPL, STYLING, front_template

ASSETS = Path(__file__).with_name('english_spelling_assets')
DECK_ROOT = 'Salvador English Spelling'
FIELD_NAMES = ['Answer', 'Picture', 'Unit', 'Mask1', 'Mask2', 'Mask3', 'Audio', 'NoteKey']
LEVEL_NAMES = ['1 Complete - middle', '2 Complete - ending', '3 Complete - beginning', '4 Build the whole word']


class TemplateDeckCard(genanki.Card):
    """genanki records template overrides but does not route exported cards."""

    def __init__(self, ordinal, destination):
        super().__init__(ordinal)
        self.destination = destination

    def write_to_db(self, cursor, timestamp, deck_id, note_id, id_gen, due=0):
        super().write_to_db(cursor, timestamp, self.destination, note_id, id_gen, due)


def fields_for(item):
    return [html.escape(item.answer), picture_html(item), str(item.unit),
            *[json.dumps(mask) for mask in completion_masks(item.answer)],
            f'[sound:{item.audio_filename}]', item.key]


def make_decks():
    decks = {}
    models = {}
    for unit in (1, 2):
        templates = []
        for index, label in enumerate(LEVEL_NAMES):
            deck_id = 2076102500 + unit * 10 + index
            decks[(unit, index)] = genanki.Deck(deck_id, f'{DECK_ROOT}::Unit {unit}::{label}')
            templates.append({
                'name': label,
                'qfmt': front_template('build' if index == 3 else 'complete', f'Mask{index + 1}' if index < 3 else 'Mask1'),
                'afmt': BACK_TMPL,
                'did': deck_id,
            })
        models[unit] = genanki.Model(
            2076102400 + unit, f'English Spelling Touch - Unit {unit} v1',
            fields=[{'name': name} for name in FIELD_NAMES], templates=templates, css=STYLING,
        )
    for item in ITEMS:
        note = genanki.Note(
            model=models[item.unit], fields=fields_for(item),
            guid=genanki.guid_for('english-spelling-v1', item.key),
            tags=['english', 'spelling', f'unit_{item.unit}'],
        )
        note.cards = [TemplateDeckCard(index, decks[(item.unit, index)].deck_id) for index in range(4)]
        decks[(item.unit, 0)].add_note(note)
    return list(decks.values())


def build_package(output_path, audio_dir):
    media = []
    for item in ITEMS:
        path = audio_dir / item.audio_filename
        if not path.exists() or path.stat().st_size < 100:
            raise FileNotFoundError(f'Missing audio: {path}; generate audio first.')
        media.append(str(path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    for unit in (1, 2):
        source = ASSETS / 'images' / f'unit{unit}.png'
        destination = output_path.parent / f'english-spelling-unit{unit}.png'
        shutil.copyfile(source, destination)
        media.append(str(destination))
    genanki.Package(make_decks(), media_files=media).write_to_file(str(output_path))
    return output_path


def render_template(template, fields):
    for name, value in zip(FIELD_NAMES, fields):
        template = template.replace('{{' + name + '}}', value)
    return template


def write_preview(directory, audio_dir):
    directory.mkdir(parents=True, exist_ok=True)
    preview_audio = directory / 'audio'
    if audio_dir.resolve() != preview_audio.resolve():
        shutil.copytree(audio_dir, preview_audio, dirs_exist_ok=True)
    for unit in (1, 2):
        shutil.copyfile(ASSETS / 'images' / f'unit{unit}.png', directory / f'english-spelling-unit{unit}.png')
    cards = []
    for item in ITEMS:
        fields = fields_for(item)
        fields[6] = f'<audio controls preload="auto" src="audio/{item.audio_filename}" aria-label="Listen to the word"></audio>'
        def preview_side(template):
            return render_template(template, fields).replace(
                f'src="{item.audio_filename}"', f'src="audio/{item.audio_filename}"')
        for level in range(4):
            template = front_template('build' if level == 3 else 'complete', f'Mask{level + 1}' if level < 3 else 'Mask1')
            cards.append({'title': f'Unit {item.unit} · {item.answer} · {LEVEL_NAMES[level]}',
                          'autoplay': level == 3,
                          'front': preview_side(template), 'back': preview_side(BACK_TMPL)})
    payload = json.dumps(cards, ensure_ascii=False).replace('</', '<\\/')
    preview = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>English Spelling - card preview</title><style>STYLE
.preview-bar {position:relative;max-width:600px;margin:10px auto;padding:10px;background:#fff;border-radius:16px;display:flex;gap:8px;flex-wrap:wrap;align-items:center;box-sizing:border-box}
.preview-bar select{font:inherit;padding:8px;width:100%;min-width:0}.preview-bar button{font:inherit;padding:10px 14px;border:1px solid #ddd;border-radius:10px;background:#fff;cursor:pointer}
.preview-note{font:13px/1.4 sans-serif;color:#536b65;margin:0} .preview-bar button.primary{background:#215f54;color:white}
</style></head><body class="card"><nav class="preview-bar" aria-label="Preview controls">
<select id="choose" aria-label="Choose a sample"></select><button id="previous">Previous</button><button id="next">Next</button><button class="primary" id="flip">Show Answer</button>
<p class="preview-note">Parent preview: the selector names answers. In Anki, only the card below appears. Audio may need one tap in this browser.</p></nav>
<div id="preview-card"></div><script>
const cards=PAYLOAD; let selected=0, back=false;
const choose=document.getElementById('choose');
cards.forEach((c,i)=>{const o=document.createElement('option');o.value=i;o.textContent=c.title;choose.appendChild(o)});
function render(){
 const previous=document.getElementById('spelling-card');if(previous&&previous._spellingCleanup)previous._spellingCleanup();
 document.querySelectorAll('audio').forEach(a=>{a.pause()});
 const host=document.getElementById('preview-card');host.innerHTML=cards[selected][back?'back':'front'];
 host.querySelectorAll('script').forEach(old=>{const s=document.createElement('script');s.textContent=old.textContent;old.replaceWith(s)});
 choose.value=selected;document.getElementById('flip').textContent=back?'Try again':'Show Answer';
 const a=host.querySelector('audio');if(a&&!back&&cards[selected].autoplay){a.play().catch(()=>{})}
}
choose.onchange=()=>{selected=Number(choose.value);back=false;render()};
document.getElementById('next').onclick=()=>{selected=(selected+1)%cards.length;back=false;render()};
document.getElementById('previous').onclick=()=>{selected=(selected+cards.length-1)%cards.length;back=false;render()};
document.getElementById('flip').onclick=()=>{back=!back;render()};render();
</script></body></html>'''.replace('STYLE', STYLING).replace('PAYLOAD', payload)
    path = directory / 'preview.html'
    path.write_text(preview, encoding='utf-8')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio-dir', type=Path, default=Path('out/english-spelling/audio'))
    parser.add_argument('--output', type=Path, default=Path('out/english-spelling/Salvador-English-Spelling.apkg'))
    args = parser.parse_args()
    print(build_package(args.output, args.audio_dir))
    print(write_preview(args.output.parent, args.audio_dir))


if __name__ == '__main__':
    main()
