# English Spelling Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development for independent work and review. The user's approval of both levels and Android target authorizes the implementation.

**Goal:** Produce an offline AnkiDroid package with 124 interactive spelling cards and a reviewable preview.

**Architecture:** Curated Python content builds four sibling cards per note through genanki. Shared HTML/CSS/JavaScript templates implement touch letter placement. A separate audio command caches British English MP3s. Stable note/model/deck identifiers permit reimport.

**Tech Stack:** Python, genanki, gTTS, HTML/CSS, pointer-event JavaScript; unittest and Playwright for checks.

## Chunk 1: Content and interaction
- [x] Write content and package validation tests first in tests/test_english_spelling.py.
- [x] Add scripts/english_spelling_content.py containing all 31 targets, cue and curated mask.
- [x] Add scripts/english_spelling_templates.py and scripts/english_spelling_assets/{card.js,card.css}; handle duplicates, punctuation, touch drag, tap placement, removal, reset, checking, and repeated review initialization.
- [x] Keep parent integration/audio work separate from the interaction implementer.

## Chunk 2: Packaging and delivery
- [x] Add scripts/build_english_spelling_apkg.py and scripts/generate_english_spelling_audio.py using existing genanki/gTTS conventions.
- [x] Bundle all 31 audio files and produce four cards per note in eight Unit/Level subdecks.
- [x] Produce standalone HTML preview from the actual card templates, linking cached audio.
- [x] Review spec compliance, then code quality; resolve material findings.
- [x] Run unit checks, browser interaction checks and APKG SQLite/media audit. Inspect narrow-screen screenshots and check audio durations.
- [x] Document import, gestures, grading and limitation of browser-only device simulation. Deliver APKG and preview links.
