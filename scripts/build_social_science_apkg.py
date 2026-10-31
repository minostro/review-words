"""Build one illustrated comprehension subdeck and its faithful browser preview."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import shutil

import genanki
from scripts.social_science_content import ITEMS
from scripts.social_science_templates import ASSETS, FRONT, BACK, STYLING

DECK_NAME = 'Salvador::Social Science - Oct - 2026'
DECK_ID = 2076103101
MODEL_ID = 2076103102
FIELD_NAMES = ['NoteKey', 'Question', 'Category', 'Choices', 'CorrectKey', 'CorrectLabel',
               'Explanation', 'Picture', 'QuestionAudio', 'AudioReference']
CATEGORIES = {'school-places':'Places at school', 'school-workers':'People at school',
              'family':'Family', 'settlements':'Where we live',
              'community-helpers':'Community helpers', 'community':'Our community'}


def question_audio_filename(item):
    digest = hashlib.sha256(item.question.encode()).hexdigest()[:10]
    return f'social-oct26-{item.key}-{digest}.mp3'


def image_filename(key):
    return f'social-oct26-{key}.jpg'


def image_html(key):
    return f'<img src="{image_filename(key)}" alt="Worksheet illustration">' if key else ''


def fields_for(item):
    choices = ''.join(
        f'<button type="button" class="social-choice" data-choice="{html.escape(c.key, quote=True)}" aria-pressed="false">'
        f'{image_html(c.image)}<span class="social-label">{html.escape(c.label)}</span><span class="social-mark" aria-hidden="true"></span></button>'
        for c in item.choices)
    correct = next(c for c in item.choices if c.key == item.correct)
    audio = question_audio_filename(item)
    return [item.key, html.escape(item.question), CATEGORIES[item.category], choices,
            item.correct, html.escape(correct.label), html.escape(item.explanation),
            image_html(item.image), audio, f'[sound:{audio}]']


def build_package(output_path, audio_dir):
    model = genanki.Model(MODEL_ID, 'Social Science Comprehension October 2026 v1',
                          fields=[{'name':n} for n in FIELD_NAMES], css=STYLING,
                          templates=[{'name':'Understand and choose', 'qfmt':FRONT, 'afmt':BACK}])
    deck = genanki.Deck(DECK_ID, DECK_NAME)
    media = {}
    for item in ITEMS:
        audio = audio_dir / question_audio_filename(item)
        if not audio.exists() or audio.stat().st_size < 100:
            raise FileNotFoundError(f'Missing question audio: {audio}')
        media[audio.name] = audio
        for key in [item.image] + [c.image for c in item.choices]:
            if key:
                picture = ASSETS / 'images' / image_filename(key)
                if not picture.exists():
                    raise FileNotFoundError(picture)
                media[picture.name] = picture
        deck.add_note(genanki.Note(model, fields=fields_for(item),
                                  guid=genanki.guid_for('salvador-social-oct26-v1',item.key),
                                  tags=['social_science','october_2026',f'topic::{item.category}']))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pending=output_path.with_suffix('.apkg.tmp')
    genanki.Package(deck, media_files=[str(p) for p in media.values()]).write_to_file(str(pending))
    pending.replace(output_path)
    return output_path


def render(template, fields):
    for name,value in zip(FIELD_NAMES,fields):
        template=template.replace('{{'+name+'}}',value)
    return template


def write_preview(directory, audio_dir):
    directory.mkdir(parents=True,exist_ok=True)
    if audio_dir.resolve() != (directory/'audio').resolve():
        shutil.copytree(audio_dir,directory/'audio',dirs_exist_ok=True)
    for picture in (ASSETS/'images').glob('*.jpg'):
        shutil.copyfile(picture,directory/picture.name)
    cards=[]
    for item in ITEMS:
        fields=fields_for(item)
        fields[8]='audio/'+question_audio_filename(item)
        cards.append({'title':CATEGORIES[item.category]+' · '+item.question,
                      'front':render(FRONT,fields),'back':render(BACK,fields)})
    payload=json.dumps(cards,ensure_ascii=False).replace('</','<\\/')
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Social Science - Oct - 2026</title><style>STYLE
.preview-bar{max-width:640px;margin:0 auto 20px;padding:12px;border-radius:14px;background:#fff;display:flex;flex-wrap:wrap;gap:8px;box-sizing:border-box}
.preview-bar select{width:100%;padding:10px;font:14px Arial;min-width:0}.preview-bar button{min-height:44px;padding:8px 15px;border:1px solid #bdcdcb;border-radius:9px;background:#edf4ee;color:#243d47;font:700 14px Arial}.preview-bar p{font:12px/1.4 Arial;margin:0;color:#52676e}
</style></head><body class="card"><nav class="preview-bar"><select id="choose" aria-label="Choose a question"></select><button id="previous">Previous</button><button id="next">Next</button><button id="flip">Show Answer</button><p>Parent preview · 44 comprehension cards · In Anki, only the card below appears. Audio plays only when tapped.</p></nav><div id="preview-card"></div><script>
const cards=PAYLOAD;let selected=0,back=false;const choose=document.getElementById('choose');
cards.forEach((c,i)=>{const o=document.createElement('option');o.value=i;o.textContent=(i+1)+'. '+c.title;choose.appendChild(o)});
function render(){const old=document.getElementById('social-card');if(old&&old._socialCleanup)old._socialCleanup();
const host=document.getElementById('preview-card');host.innerHTML=cards[selected][back?'back':'front'];
host.querySelectorAll('script').forEach(old=>{const s=document.createElement('script');s.textContent=old.textContent;old.replaceWith(s)});
choose.value=selected;document.getElementById('flip').textContent=back?'Try again':'Show Answer';}
choose.onchange=()=>{selected=Number(choose.value);back=false;render()};
document.getElementById('next').onclick=()=>{selected=(selected+1)%cards.length;back=false;render()};
document.getElementById('previous').onclick=()=>{selected=(selected+cards.length-1)%cards.length;back=false;render()};
document.getElementById('flip').onclick=()=>{back=!back;render()};render();
</script></body></html>'''.replace('STYLE',STYLING).replace('PAYLOAD',payload)
    path=directory/'preview.html';path.write_text(page,encoding='utf-8');return path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('out/social-science/Social-Science-Oct-2026.apkg'))
    parser.add_argument('--audio-dir',type=Path,default=Path('out/social-science/audio'))
    args=parser.parse_args()
    print(build_package(args.output,args.audio_dir))
    print(write_preview(args.output.parent,args.audio_dir))


if __name__=='__main__':
    main()
