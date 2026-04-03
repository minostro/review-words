from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from gtts import gTTS

from scripts.multiplication_common import MultiplicationFact, load_supported_facts
from scripts.multiplication_content import answer_audio_text, prompt_audio_text


@dataclass(frozen=True)
class AudioJob:
    filename: str
    text: str
    kind: str


DEFAULT_CELEBRATION_JOBS = [
    AudioJob(filename="celebration_01.mp3", text="Muy bien", kind="celebration"),
    AudioJob(filename="celebration_02.mp3", text="Excelente", kind="celebration"),
    AudioJob(filename="celebration_03.mp3", text="Vamos", kind="celebration"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Spanish audio for the animal multiplication deck.")
    parser.add_argument("--source-apkg", type=Path, required=True, help="Source multiplication .apkg file.")
    parser.add_argument("--audio-dir", type=Path, help="Output directory for generated MP3 files.")
    parser.add_argument("--lang", default="es", help="gTTS language code. Defaults to es.")
    return parser.parse_args()


def audio_dir_name(source_apkg: Path) -> str:
    return source_apkg.stem


def default_audio_dir(source_apkg: Path, audio_dir: Path | None) -> Path:
    if audio_dir is not None:
        return audio_dir
    return Path("out") / "audio" / audio_dir_name(source_apkg)


def build_audio_jobs(facts: list[MultiplicationFact]) -> list[AudioJob]:
    jobs: list[AudioJob] = []
    for fact in facts:
        slug = f"fact_{fact.left:02d}x{fact.right:02d}"
        jobs.append(AudioJob(filename=f"{slug}_prompt.mp3", text=prompt_audio_text(fact), kind="prompt"))
        jobs.append(AudioJob(filename=f"{slug}_answer.mp3", text=answer_audio_text(fact), kind="answer"))
    jobs.extend(DEFAULT_CELEBRATION_JOBS)
    return jobs


def should_skip_existing_audio(output_path: Path) -> bool:
    return output_path.exists() and output_path.stat().st_size > 0


def synthesize_audio(text: str, output_path: Path, lang: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gTTS(text=text, lang=lang).save(str(output_path))


def main() -> None:
    args = parse_args()
    facts = load_supported_facts(args.source_apkg)
    audio_dir = default_audio_dir(args.source_apkg, args.audio_dir)

    created = 0
    skipped = 0
    for job in build_audio_jobs(facts):
        output_path = audio_dir / job.filename
        if should_skip_existing_audio(output_path):
            skipped += 1
            continue
        if output_path.exists():
            output_path.unlink()
        synthesize_audio(job.text, output_path, args.lang)
        created += 1
        print(f"created {output_path.name}")

    print(f"done created={created} skipped={skipped} dir={audio_dir}")


if __name__ == "__main__":
    main()
