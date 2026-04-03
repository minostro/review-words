# Animal Multiplication Deck Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a derived Anki package from the source multiplication deck with two subdecks, animal-themed visuals, Spanish audio, and playful prompts for a 7-year-old learner.

**Architecture:** Add a multiplication-specific pipeline alongside the existing storybook scripts instead of forcing this feature into the CSV word-deck code. One layer will read and filter facts from the source `.apkg`, one layer will generate deterministic content and media metadata, and one builder will assemble the two subdecks plus bundled media into a final `.apkg`.

**Tech Stack:** Python 3, stdlib (`zipfile`, `sqlite3`, `tempfile`, `pathlib`, `xml.sax.saxutils`), `genanki`, `gTTS`, `unittest`

---

## File Structure

- Create `scripts/multiplication_common.py`
  Responsibility: source `.apkg` parsing, multiplication fact modeling, filtering to tables `2-10`, and subdeck assignment.
- Create `scripts/multiplication_content.py`
  Responsibility: Spanish phrase generation, deterministic playful prompt selection, and animal/theme metadata.
- Create `scripts/multiplication_visuals.py`
  Responsibility: SVG markup generation for equal-group animal visuals and deterministic visual filenames.
- Create `scripts/generate_multiplication_audio.py`
  Responsibility: front prompt audio, back answer audio, and reusable celebration audio generation.
- Create `scripts/build_multiplication_apkg.py`
  Responsibility: build the final `Tables::2-4` and `Tables::5-10` package and attach generated media.
- Create `tests/test_multiplication_common.py`
  Responsibility: coverage for source parsing, filtering, and subdeck grouping.
- Create `tests/test_multiplication_content.py`
  Responsibility: coverage for Spanish text, prompt assignment, and animal selection.
- Create `tests/test_multiplication_visuals.py`
  Responsibility: coverage for SVG output structure and quantity rendering.
- Create `tests/test_generate_multiplication_audio.py`
  Responsibility: coverage for audio job planning, filename conventions, and skip logic without calling the network.
- Create `tests/test_build_multiplication_apkg.py`
  Responsibility: package-level coverage for note fields, deck names, and bundled media references.
- Modify `README.md`
  Responsibility: document the new multiplication build flow and verification commands.

## Chunk 1: Source Facts And Deterministic Content

### Task 1: Parse The Source `.apkg` And Split Facts Into Subdecks

**Files:**
- Create: `scripts/multiplication_common.py`
- Test: `tests/test_multiplication_common.py`
- Reference: `docs/superpowers/specs/2026-03-28-animal-multiplication-deck-design.md`

- [ ] **Step 1: Write the failing tests for parsing, filtering, and deck assignment**

```python
def test_parse_front_extracts_operands_and_answer() -> None:
    fact = parse_source_fact("3 X 4 = ?", "12")
    self.assertEqual((fact.left, fact.right, fact.answer), (3, 4, 12))

def test_target_subdeck_for_supported_tables() -> None:
    self.assertEqual(target_subdeck_name(4), "Tables::2-4")
    self.assertEqual(target_subdeck_name(7), "Tables::5-10")

def test_load_supported_facts_ignores_tables_above_ten() -> None:
    facts = load_supported_facts(self.sample_apkg)
    self.assertEqual({fact.right for fact in facts}, {2, 3, 4, 5, 6, 7, 8, 9, 10})
```

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `python -m unittest tests.test_multiplication_common -v`

Expected: `ImportError` or `NameError` for missing multiplication helpers.

- [ ] **Step 3: Write the minimal source loader and fact model**

```python
@dataclass(frozen=True)
class MultiplicationFact:
    left: int
    right: int
    answer: int
    front: str
    back: str

def parse_source_fact(front: str, back: str) -> MultiplicationFact:
    left_text, right_text = front.split("X")
    left = int(left_text.strip())
    right = int(right_text.split("=")[0].strip())
    return MultiplicationFact(left=left, right=right, answer=int(back), front=front, back=back)

def target_subdeck_name(table: int) -> str:
    if 2 <= table <= 4:
        return "Tables::2-4"
    if 5 <= table <= 10:
        return "Tables::5-10"
    raise ValueError(f"Unsupported table: {table}")
```

Implementation notes:
- read `collection.anki2` from the source package with `zipfile.ZipFile`
- query the `notes` table via `sqlite3`
- split `flds` on `chr(31)` to recover `Front` and `Back`
- treat the practiced table as the right-hand operand because the source deck is ordered as `1 X 2`, `2 X 2`, ... `20 X 2`

- [ ] **Step 4: Run the focused tests to verify they pass**

Run: `python -m unittest tests.test_multiplication_common -v`

Expected: PASS with coverage for parsing, filtering, and subdeck assignment.

- [ ] **Step 5: Commit the source-loader slice**

```bash
git add scripts/multiplication_common.py tests/test_multiplication_common.py
git commit -m "feat: add multiplication source parsing"
```

### Task 2: Add Spanish Text, Animal Themes, And Playful Prompt Selection

**Files:**
- Create: `scripts/multiplication_content.py`
- Test: `tests/test_multiplication_content.py`
- Reference: `docs/superpowers/specs/2026-03-28-animal-multiplication-deck-design.md`

- [ ] **Step 1: Write the failing tests for Spanish phrases and deterministic prompt selection**

```python
def test_prompt_audio_text_uses_spanish_number_words() -> None:
    fact = MultiplicationFact(left=3, right=4, answer=12, front="3 X 4 = ?", back="12")
    self.assertEqual(prompt_audio_text(fact), "tres por cuatro")

def test_answer_audio_text_uses_spanish_result() -> None:
    self.assertEqual(answer_audio_text(fact), "doce")

def test_playful_prompt_is_deterministic() -> None:
    self.assertEqual(playful_prompt_text(fact), "Haz 3 filas de 4 con monedas")
```

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `python -m unittest tests.test_multiplication_content -v`

Expected: FAIL because the content module does not exist yet.

- [ ] **Step 3: Implement the smallest deterministic content helpers**

```python
ANIMALS = ["ranas", "pinguinos", "zorros", "jirafas", "abejas", "gatitos"]

def prompt_audio_text(fact: MultiplicationFact) -> str:
    return f"{spanish_number(fact.left)} por {spanish_number(fact.right)}"

def answer_audio_text(fact: MultiplicationFact) -> str:
    return spanish_number(fact.answer)

def playful_prompt_text(fact: MultiplicationFact) -> str:
    prompts = [
        f"Da {fact.answer} palmadas",
        f"Haz {fact.left} filas de {fact.right} con monedas",
        f"Dilo como un leon",
        "Cuenta primero los grupos, luego el total",
    ]
    return prompts[(fact.left + fact.right) % len(prompts)]
```

Implementation notes:
- support number words through at least `100`
- keep prompt selection deterministic so tests and rebuilds stay stable
- expose `animal_name(fact)` separately so the visuals layer can reuse it

- [ ] **Step 4: Run the focused tests to verify they pass**

Run: `python -m unittest tests.test_multiplication_content -v`

Expected: PASS with deterministic Spanish text and prompt selection.

- [ ] **Step 5: Commit the content slice**

```bash
git add scripts/multiplication_content.py tests/test_multiplication_content.py
git commit -m "feat: add multiplication content helpers"
```

### Task 3: Generate Animal-Themed SVG Visuals

**Files:**
- Create: `scripts/multiplication_visuals.py`
- Test: `tests/test_multiplication_visuals.py`
- Reference: `scripts/multiplication_common.py`
- Reference: `scripts/multiplication_content.py`

- [ ] **Step 1: Write the failing tests for SVG structure and quantity rendering**

```python
def test_visual_filename_uses_fact_coordinates() -> None:
    self.assertEqual(visual_filename(fact), "fact_03x04.svg")

def test_render_fact_svg_includes_group_count_and_animal_label() -> None:
    svg = render_fact_svg(fact)
    self.assertIn("3 grupos de 4", svg)
    self.assertIn("ranas", svg)
```

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `python -m unittest tests.test_multiplication_visuals -v`

Expected: FAIL because the visuals module does not exist yet.

- [ ] **Step 3: Implement the SVG renderer**

```python
def visual_filename(fact: MultiplicationFact) -> str:
    return f"fact_{fact.left:02d}x{fact.right:02d}.svg"

def render_fact_svg(fact: MultiplicationFact) -> str:
    title = f"{fact.left} grupos de {fact.right} {animal_name(fact)}"
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="900" height="620">
      <text x="450" y="72" text-anchor="middle">{escape(title)}</text>
      {render_rows(fact.left, fact.right)}
    </svg>
    """.strip()
```

Implementation notes:
- keep assets as SVG so no new image dependency is required
- render equal groups clearly as repeated rows or clusters
- add a caption line with the total, for example `Total: 12`
- escape text with `xml.sax.saxutils.escape`

- [ ] **Step 4: Run the focused tests to verify they pass**

Run: `python -m unittest tests.test_multiplication_visuals -v`

Expected: PASS with stable filenames and readable grouped-quantity SVG output.

- [ ] **Step 5: Commit the visuals slice**

```bash
git add scripts/multiplication_visuals.py tests/test_multiplication_visuals.py
git commit -m "feat: add multiplication visual generation"
```

## Chunk 2: Audio And Deck Packaging

### Task 4: Add The Spanish Audio Generator

**Files:**
- Create: `scripts/generate_multiplication_audio.py`
- Test: `tests/test_generate_multiplication_audio.py`
- Reference: `scripts/multiplication_common.py`
- Reference: `scripts/multiplication_content.py`

- [ ] **Step 1: Write the failing tests for audio job planning and filename conventions**

```python
def test_build_audio_jobs_creates_prompt_and_answer_jobs() -> None:
    jobs = build_audio_jobs([fact])
    self.assertEqual(jobs[0].filename, "fact_03x04_prompt.mp3")
    self.assertEqual(jobs[1].filename, "fact_03x04_answer.mp3")

def test_celebration_jobs_are_reused() -> None:
    jobs = build_audio_jobs([fact])
    celebration_files = {job.filename for job in jobs if job.kind == "celebration"}
    self.assertEqual(celebration_files, {"celebration_01.mp3", "celebration_02.mp3", "celebration_03.mp3"})
```

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `python -m unittest tests.test_generate_multiplication_audio -v`

Expected: FAIL because the audio planner does not exist yet.

- [ ] **Step 3: Implement the audio planning and synthesis layer**

```python
@dataclass(frozen=True)
class AudioJob:
    filename: str
    text: str
    kind: str

def build_audio_jobs(facts: list[MultiplicationFact]) -> list[AudioJob]:
    jobs: list[AudioJob] = []
    for fact in facts:
        slug = f"fact_{fact.left:02d}x{fact.right:02d}"
        jobs.append(AudioJob(filename=f"{slug}_prompt.mp3", text=prompt_audio_text(fact), kind="prompt"))
        jobs.append(AudioJob(filename=f"{slug}_answer.mp3", text=answer_audio_text(fact), kind="answer"))
    jobs.extend(DEFAULT_CELEBRATION_JOBS)
    return jobs
```

Implementation notes:
- keep celebration audio as short spoken praise in Spanish, for example `Muy bien`, `Excelente`, `Vamos`
- keep `should_skip_existing_audio()` semantics consistent with the existing audio script
- tests should stub or skip the actual `gTTS(...).save(...)` call; do not hit the network in unit tests

- [ ] **Step 4: Run the focused tests to verify they pass**

Run: `python -m unittest tests.test_generate_multiplication_audio -v`

Expected: PASS with deterministic filenames and reusable celebration clips.

- [ ] **Step 5: Commit the audio slice**

```bash
git add scripts/generate_multiplication_audio.py tests/test_generate_multiplication_audio.py
git commit -m "feat: add multiplication audio generator"
```

### Task 5: Build The Final Two-Subdeck `.apkg`

**Files:**
- Create: `scripts/build_multiplication_apkg.py`
- Test: `tests/test_build_multiplication_apkg.py`
- Reference: `scripts/multiplication_common.py`
- Reference: `scripts/multiplication_content.py`
- Reference: `scripts/multiplication_visuals.py`
- Reference: `scripts/generate_multiplication_audio.py`

- [ ] **Step 1: Write the failing tests for deck names, note fields, and bundled media**

```python
def test_build_package_uses_two_expected_subdecks() -> None:
    output_path = build_package(self.sample_apkg, self.audio_dir, self.output_path)
    summary = inspect_package(output_path)
    self.assertEqual(summary.deck_names, {"Tables::2-4", "Tables::5-10"})

def test_notes_include_visual_and_audio_markup() -> None:
    note_fields = build_note_fields(fact, "fact_03x04.svg")
    self.assertIn('<img src="fact_03x04.svg">', note_fields["Visual"])
    self.assertEqual(note_fields["PromptAudio"], "[sound:fact_03x04_prompt.mp3]")
```

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `python -m unittest tests.test_build_multiplication_apkg -v`

Expected: FAIL because the package builder does not exist yet.

- [ ] **Step 3: Implement the minimal package builder**

```python
model = genanki.Model(
    1837452111,
    "Animal Multiplication Note",
    fields=[
        {"name": "Prompt"},
        {"name": "Answer"},
        {"name": "Visual"},
        {"name": "PromptAudio"},
        {"name": "AnswerAudio"},
        {"name": "CelebrationAudio"},
        {"name": "PlayfulPrompt"},
    ],
    templates=[{"name": "Animal Multiplication", "qfmt": FRONT_TMPL, "afmt": BACK_TMPL}],
    css=STYLING,
)

deck_24 = genanki.Deck(1837452112, "Tables::2-4")
deck_510 = genanki.Deck(1837452113, "Tables::5-10")
genanki.Package([deck_24, deck_510], media_files=media_files).write_to_file(output_path)
```

Implementation notes:
- generate SVG media into a temporary directory while building
- assign each fact to `deck_24` or `deck_510` from `target_subdeck_name(fact.right)`
- reuse celebration clips across notes instead of copying them under new names
- keep front and back templates child-friendly: large prompt, clear image, answer reveal, and one playful prompt on the back

- [ ] **Step 4: Run the focused tests to verify they pass**

Run: `python -m unittest tests.test_build_multiplication_apkg -v`

Expected: PASS with both subdecks present and media references attached to the notes.

- [ ] **Step 5: Commit the package-builder slice**

```bash
git add scripts/build_multiplication_apkg.py tests/test_build_multiplication_apkg.py
git commit -m "feat: add multiplication deck builder"
```

## Chunk 3: Docs, End-To-End Verification, And Handoff

### Task 6: Document The Build Flow And Add An End-To-End Smoke Test

**Files:**
- Modify: `README.md`
- Modify: `tests/test_build_multiplication_apkg.py`
- Reference: `/Users/minostro/Downloads/1_to_20_Multiplication_Tables_100_accurate_value.apkg`

- [ ] **Step 1: Extend the package test into a smoke test that checks counts and media presence**

```python
def test_built_package_contains_expected_card_counts() -> None:
    summary = inspect_package(output_path)
    self.assertEqual(summary.total_cards, 90)
    self.assertEqual(summary.deck_card_counts["Tables::2-4"], 30)
    self.assertEqual(summary.deck_card_counts["Tables::5-10"], 60)
```

- [ ] **Step 2: Run the focused package tests to verify the new smoke assertions fail first**

Run: `python -m unittest tests.test_build_multiplication_apkg -v`

Expected: FAIL until package inspection reports the correct counts.

- [ ] **Step 3: Update the README with build and verification commands**

```bash
. .venv/bin/activate
python -m scripts.generate_multiplication_audio \
  --source-apkg /Users/minostro/Downloads/1_to_20_Multiplication_Tables_100_accurate_value.apkg

python -m scripts.build_multiplication_apkg \
  --source-apkg /Users/minostro/Downloads/1_to_20_Multiplication_Tables_100_accurate_value.apkg \
  --audio-dir out/audio/1_to_20_Multiplication_Tables_100_accurate_value
```

README content to add:
- what the new builder produces
- where media files are written
- that `gTTS` requires network access during real audio generation
- how to re-open the resulting `.apkg` as a zip for quick verification

- [ ] **Step 4: Run the full automated test suite**

Run: `python -m unittest discover -s tests -v`

Expected: PASS for the existing storybook tests plus the new multiplication tests.

- [ ] **Step 5: Run the end-to-end local verification with the real source deck**

Run: `python -m scripts.generate_multiplication_audio --source-apkg /Users/minostro/Downloads/1_to_20_Multiplication_Tables_100_accurate_value.apkg`

Expected: prompt, answer, and celebration MP3 files written under `out/audio/...`

Run: `python -m scripts.build_multiplication_apkg --source-apkg /Users/minostro/Downloads/1_to_20_Multiplication_Tables_100_accurate_value.apkg --audio-dir out/audio/1_to_20_Multiplication_Tables_100_accurate_value`

Expected: an `.apkg` written under `out/` that imports as `Tables::2-4` and `Tables::5-10`

Run: `unzip -l out/*multiplication*.apkg | sed -n '1,40p'`

Expected: bundled `.svg`, prompt `.mp3`, answer `.mp3`, celebration `.mp3`, plus `collection.anki2` and `media`

- [ ] **Step 6: Commit docs and verification updates**

```bash
git add README.md tests/test_build_multiplication_apkg.py
git commit -m "docs: add multiplication deck build flow"
```

## Risks And Guardrails

- `gTTS` needs network access for real MP3 generation, so unit tests must never rely on live synthesis.
- `genanki` deck IDs and model IDs must stay stable once chosen; pick constants once and do not randomize them.
- Keep SVG assets lightweight so the final package stays importable on mobile devices.
- Tests must not depend on the source `.apkg` in `/Users/minostro/Downloads`; generate temporary fixtures inside the test suite.
- Keep all media filenames deterministic so re-running the pipeline does not create duplicate Anki assets.

## Execution Notes

- Prefer implementing one task at a time and running its focused test before moving on.
- Do not mix the multiplication pipeline into `scripts/storybook_common.py`; keep the new feature isolated.
- Reuse the existing repo patterns for CLI parsing and output directories unless a task explicitly requires a new helper.
- If `genanki.Package([deck_24, deck_510], ...)` behaves differently than expected, verify the accepted constructor shape before broad refactors.

Plan complete and saved to `docs/superpowers/plans/2026-03-28-animal-multiplication-deck.md`. Ready to execute?
