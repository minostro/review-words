# Social Science Comprehension Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development. Steps use checkbox syntax for tracking.

**Goal:** Deliver one illustrated, tap-answer comprehension subdeck inside Salvador, with optional question audio.
**Architecture:** A content module declares stable items and choices. Committed worksheet crops form reusable media. Separate templates/interaction code power both an Anki package and a local preview. The existing bundler gains one subject input with no extra category subdecks.
**Tech Stack:** Python, Pillow (worksheet extraction), genanki, gTTS, HTML/CSS/JS, unittest, Playwright.

## Chunk 1: Source and content
- [x] Review supplied pages; create original-photo crop manifest and extraction script `scripts/extract_social_science_images.py`; commit crops in `scripts/social_science_assets/images/` and provenance.
- [x] Add `scripts/social_science_content.py`: approximately 40–50 nonredundant questions spanning six categories, three unambiguous choices, feedback explanation, stable keys and picture keys.
- [x] Write failing content validation tests in `tests/test_social_science.py`, then implement/validate content. Independently review question scope and ambiguity.

## Chunk 2: Interaction and package
- [x] Write browser regression tests for answer selection, feedback, no autoplay, replay, navigation/flip, and mobile overflow.
- [x] Implement `scripts/social_science_templates.py`, `scripts/social_science_assets/card.js`, and `card.css`: accessible shuffled-choice buttons, locked attempts, manual audio, rating guidance.
- [x] Implement `scripts/build_social_science_apkg.py`: one card/note, single exact deck name, stable IDs/GUIDs, offline media and preview.
- [x] Implement `scripts/generate_social_science_audio.py`: cache keyed by question digest, British English narration, bounded concurrency and timeout.
- [x] Verify standalone note/card/media integrity and correct image/audio references. Render phone-size screenshots and inspect.

## Chunk 3: Distribution
- [x] Extend `scripts/build_salvador_apkg.py` and bundler tests to include social science with exact child name; preserve existing subject source packages.
- [x] Generate cached audio, build standalone package and combined Salvador.apkg, confirm existing 508 cards plus new unique cards.
- [x] Run `/Users/minostro/Documents/.venv-anki/bin/python -m unittest discover -s tests` and Node/Playwright tests with bundled runtime/NODE_PATH.
- [x] Review specification compliance then code quality; resolve findings.
- [x] Update README, preview and Drive file `1g9EfIRJYW0qzWKq4D-L5uYqBm7xUbOYP`, verify readback.

## Verification record

- Independent content, specification, and code-quality reviews approved.
- 45 Python tests and 7 Node/browser tests passed.
- All 44 MP3s decoded; real browser playback starts only after a tap.
- Every question checked at 360px for working images and no horizontal overflow.
- All original 415 notes / 508 cards and 536 media files preserved by identity and content.
- Combined package: 459 notes, 552 cards, 611 media; Drive readback size 12,356,360 bytes.
- Physical AnkiDroid testing remains a user-device check.

Release action: commit this verified source tree, integrate into main, and push.
