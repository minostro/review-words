# More Focused Multiplication Practice Decks Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add focused multiplication practice decks for tables `4` and `5` to the existing derived `.apkg` while preserving the current broad decks and focused `2` and `3` decks.

**Architecture:** Keep the current data-driven focused-deck structure and extend it with four more explicit deck definitions plus stable deck IDs. The common layer will expose all ten deck names and their matching rules, and the builder will continue to create one note per fact-per-deck while deduplicating shared media files.

**Tech Stack:** Python 3, stdlib (`dataclasses`, `pathlib`, `sqlite3`, `tempfile`, `zipfile`), `genanki`, `unittest`

---

## File Structure

- Modify `scripts/multiplication_common.py`
  Responsibility: add focused deck definitions for tables `4` and `5` and preserve multi-deck matching.
- Modify `scripts/build_multiplication_apkg.py`
  Responsibility: add stable deck IDs for the new focused decks while keeping dynamic deck creation.
- Modify `tests/test_multiplication_common.py`
  Responsibility: verify the expanded deck configuration and representative overlap rules.
- Modify `tests/test_build_multiplication_apkg.py`
  Responsibility: verify all ten deck names, new focused-deck counts, and the new total package size.
- Modify `README.md`
  Responsibility: document the expanded focused deck list and the new card totals.

## Chunk 1: Deck Assignment Rules

### Task 1: Add failing tests for the new focused deck definitions

**Files:**
- Modify: `tests/test_multiplication_common.py`
- Reference: `docs/superpowers/specs/2026-04-09-more-focused-multiplication-practice-decks-design.md`

- [ ] **Step 1: Write the failing tests for the ten configured deck names and representative `4`/`5` focused matches**
- [ ] **Step 2: Run `/Users/minostro/Documents/.venv-anki/bin/python -m unittest tests.test_multiplication_common -v` and verify the new tests fail for missing `4`/`5` deck behavior**
- [ ] **Step 3: Update `scripts/multiplication_common.py` with four more explicit focused deck definitions**
- [ ] **Step 4: Run `/Users/minostro/Documents/.venv-anki/bin/python -m unittest tests.test_multiplication_common -v` and verify it passes**

## Chunk 2: Package Building

### Task 2: Add failing tests for ten-deck package output

**Files:**
- Modify: `tests/test_build_multiplication_apkg.py`
- Modify: `scripts/build_multiplication_apkg.py`

- [ ] **Step 1: Write the failing package tests for all ten deck names, the new focused counts, and the new total of `166` cards**
- [ ] **Step 2: Run `/Users/minostro/Documents/.venv-anki/bin/python -m unittest tests.test_build_multiplication_apkg -v` and verify the new tests fail**
- [ ] **Step 3: Update the builder with stable deck IDs for the new `4` and `5` focused decks**
- [ ] **Step 4: Run `/Users/minostro/Documents/.venv-anki/bin/python -m unittest tests.test_build_multiplication_apkg -v` and verify it passes**

## Chunk 3: Documentation And Verification

### Task 3: Update docs and verify the package end to end

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the README deck list and totals to cover focused tables `2` through `5`**
- [ ] **Step 2: Run `/Users/minostro/Documents/.venv-anki/bin/python -m unittest tests.test_multiplication_common tests.test_build_multiplication_apkg -v`**
- [ ] **Step 3: Run `/Users/minostro/Documents/.venv-anki/bin/python -m unittest discover -s tests -v`**
- [ ] **Step 4: If `/Users/minostro/Downloads/1_to_20_Multiplication_Tables_100_accurate_value.apkg` and the audio cache are present, generate any missing audio and rebuild the real `.apkg`, then inspect its deck counts**

Plan complete and saved to `docs/superpowers/plans/2026-04-09-more-focused-multiplication-practice-decks.md`.
