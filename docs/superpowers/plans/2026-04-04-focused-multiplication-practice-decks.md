# Focused Multiplication Practice Decks Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add four focused multiplication practice decks to the existing derived `.apkg` while preserving the current two broad decks.

**Architecture:** Keep the current multiplication media and note pipeline unchanged, but replace single-deck assignment with data-driven multi-deck matching. The common layer will define deck rules and expose all matching deck names for each fact, and the package builder will duplicate notes across the relevant decks while deduplicating shared media files.

**Tech Stack:** Python 3, stdlib (`dataclasses`, `pathlib`, `sqlite3`, `tempfile`, `zipfile`), `genanki`, `unittest`

---

## File Structure

- Modify `scripts/multiplication_common.py`
  Responsibility: define deck rules, expose all matching deck names, and preserve supported-fact loading.
- Modify `scripts/build_multiplication_apkg.py`
  Responsibility: build all six decks from the configured deck rules and add one note per fact-per-deck.
- Modify `tests/test_multiplication_common.py`
  Responsibility: verify focused deck membership and broad-deck compatibility.
- Modify `tests/test_build_multiplication_apkg.py`
  Responsibility: verify all deck names, focused deck counts, and final package total.
- Modify `README.md`
  Responsibility: document the updated package contents and totals.

## Chunk 1: Deck Assignment Rules

### Task 1: Add failing tests for multi-deck assignment

**Files:**
- Modify: `tests/test_multiplication_common.py`
- Reference: `docs/superpowers/specs/2026-04-04-focused-multiplication-practice-decks-design.md`

- [ ] **Step 1: Write the failing tests for broad and focused deck matching**
- [ ] **Step 2: Run `python -m unittest tests.test_multiplication_common -v` and verify the new tests fail for missing multi-deck behavior**
- [ ] **Step 3: Update `scripts/multiplication_common.py` with data-driven deck rules and matching helpers**
- [ ] **Step 4: Run `python -m unittest tests.test_multiplication_common -v` and verify it passes**

## Chunk 2: Package Building

### Task 2: Add failing tests for six-deck package output

**Files:**
- Modify: `tests/test_build_multiplication_apkg.py`
- Modify: `scripts/build_multiplication_apkg.py`

- [ ] **Step 1: Write the failing package tests for all six deck names and counts**
- [ ] **Step 2: Run `python -m unittest tests.test_build_multiplication_apkg -v` and verify the new tests fail**
- [ ] **Step 3: Update the builder to create decks dynamically and add duplicated notes where needed**
- [ ] **Step 4: Run `python -m unittest tests.test_build_multiplication_apkg -v` and verify it passes**

## Chunk 3: Documentation And Verification

### Task 3: Document and verify the updated package

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the README deck list and totals**
- [ ] **Step 2: Run `python -m unittest tests.test_multiplication_common tests.test_build_multiplication_apkg -v`**
- [ ] **Step 3: Run `python -m unittest -v` for full repo verification**

Plan complete and saved to `docs/superpowers/plans/2026-04-04-focused-multiplication-practice-decks.md`.
