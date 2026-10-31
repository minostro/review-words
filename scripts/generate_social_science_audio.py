"""Cache offline question-only British English audio; no answer narration."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from gtts import gTTS
from scripts.social_science_content import ITEMS
from scripts.build_social_science_apkg import question_audio_filename


def generate(item, directory):
    directory.mkdir(parents=True, exist_ok=True)
    path=directory/question_audio_filename(item)
    if path.exists() and path.stat().st_size>100:
        return f'cached {item.key}'
    pending=path.with_suffix('.tmp.mp3')
    try:
        gTTS(item.question,lang='en',tld='co.uk',slow=True,timeout=30).save(str(pending))
        if pending.stat().st_size<100:
            raise ValueError(f'Empty question audio: {item.key}')
        pending.replace(path)
    finally:
        pending.unlink(missing_ok=True)
    return f'created {item.key}'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio-dir',type=Path,default=Path('out/social-science/audio'))
    args=parser.parse_args()
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(lambda item:generate(item,args.audio_dir),ITEMS):
            print(result,flush=True)


if __name__=='__main__':
    main()
