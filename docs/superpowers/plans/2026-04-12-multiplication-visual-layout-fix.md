# Multiplication Visual Layout Fix Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the `Total` subtitle from multiplication SVG visuals and prevent the first row of circles from overlapping the `Grupo` labels.

**Architecture:** Keep the current SVG structure and styling, but tighten the layout in one place: the visuals generator. Update the test first to reflect the new expected SVG output, then adjust the label gutter and circle start positions so the rows render cleanly without changing the rest of the card design.

**Tech Stack:** Python 3, stdlib, `unittest`

---

## File Structure

- Modify `tests/test_multiplication_visuals.py`
  Responsibility: verify the SVG no longer includes the `Total` line and still renders the visual structure.
- Modify `scripts/multiplication_visuals.py`
  Responsibility: remove the subtitle line and shift row-label/circle spacing to avoid overlap.

## Chunk 1: Visual Regression Fix

### Task 1: Update the visual test and fix the SVG layout

**Files:**
- Modify: `tests/test_multiplication_visuals.py`
- Modify: `scripts/multiplication_visuals.py`

- [ ] **Step 1: Write the failing test for the removed `Total` line and updated row layout markers**
- [ ] **Step 2: Run `/Users/minostro/Documents/.venv-anki/bin/python -m unittest tests.test_multiplication_visuals -v` and verify it fails**
- [ ] **Step 3: Implement the minimal SVG layout fix**
- [ ] **Step 4: Run `/Users/minostro/Documents/.venv-anki/bin/python -m unittest tests.test_multiplication_visuals -v` and verify it passes**
- [ ] **Step 5: Run `/Users/minostro/Documents/.venv-anki/bin/python -m unittest discover -s tests -v` for full verification**

Plan complete and saved to `docs/superpowers/plans/2026-04-12-multiplication-visual-layout-fix.md`.
