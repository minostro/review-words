"""Generate and cache offline British English vocabulary audio."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from gtts import gTTS
from scripts.english_spelling_content import ITEMS


def generate(item, audio_dir):
    path = audio_dir / item.audio_filename
    if path.exists() and path.stat().st_size > 100:
        return f"cached {item.answer}"
    temporary = path.with_suffix('.tmp.mp3')
    try:
        gTTS(item.answer, lang='en', tld='co.uk', slow=True, timeout=30).save(str(temporary))
        if temporary.stat().st_size < 100:
            raise ValueError(f"Empty audio for {item.answer}")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return f"created {item.answer}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio-dir', type=Path, default=Path('out/english-spelling/audio'))
    args = parser.parse_args()
    args.audio_dir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(lambda item: generate(item, args.audio_dir), ITEMS):
            print(result, flush=True)


if __name__ == '__main__':
    main()
