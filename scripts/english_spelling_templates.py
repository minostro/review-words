"""Self-contained Anki spelling templates shared with the local preview."""
from pathlib import Path

_ASSETS = Path(__file__).with_name("english_spelling_assets")
STYLING = (_ASSETS / "card.css").read_text(encoding="utf-8")
_SCRIPT = (_ASSETS / "card.js").read_text(encoding="utf-8")


def front_template(mode: str, mask_field: str = "Mask") -> str:
    """Build one template; mask_field selects a completion sibling's mask."""
    if mode not in {"complete", "build"}:
        raise ValueError("mode must be complete or build")
    if mask_field not in {"Mask", "Mask1", "Mask2", "Mask3"}:
        raise ValueError("unknown mask field")
    title = "Complete the word" if mode == "complete" else "Build the whole word"
    subtitle = "Listen. Find the missing letters." if mode == "complete" else "Listen. Put every letter in its place."
    mask = "{{" + mask_field + "}}" if mode == "complete" else "[]"
    return """
<main class="spelling-shell">
  <div class="spelling-eyebrow">English garden · Unit {{Unit}}</div>
  <h1 class="spelling-heading">__TITLE__</h1>
  <p class="spelling-subtitle">__SUBTITLE__</p>
  <div class="spelling-picture">{{Picture}}</div>
  <div class="spelling-audio"><span>Listen again</span>{{Audio}}</div>
  <section id="spelling-card" data-mode="MODE" aria-label="Spelling activity">
    <span data-answer hidden aria-hidden="true">{{Answer}}</span>
    <span data-mask hidden aria-hidden="true">MASK</span>
    <div class="spelling-panel">
      <div class="spelling-board" aria-label="Word spaces"></div>
      <div class="spelling-tray-label">Your letters</div>
      <div class="spelling-tray" aria-label="Letter tiles"></div>
    </div>
    <p class="spelling-feedback" role="status" aria-live="polite">Drag a letter, or tap a letter then a space.</p>
    <div class="spelling-actions">
      <button type="button" class="spelling-reset" data-action="reset">Start again</button>
      <button type="button" class="spelling-check" data-action="check">Check</button>
    </div>
    <p class="spelling-tip">Tap a placed letter to return it. Use Show Answer whenever you need help.</p>
  </section>
</main>
<script>SCRIPT</script>
""".replace("__TITLE__", title).replace("__SUBTITLE__", subtitle).replace("MODE", mode).replace("MASK", mask).replace("SCRIPT", _SCRIPT)


BACK_TMPL = """
<main class="spelling-shell spelling-back">
  <div class="spelling-eyebrow">English garden · Unit {{Unit}}</div>
  <h1 class="spelling-heading">Read it. Say it. Remember it.</h1>
  <div class="spelling-picture">{{Picture}}</div>
  <div class="spelling-answer">{{Answer}}</div>
  <div class="spelling-audio"><span>Listen again</span>{{Audio}}</div>
  <p class="spelling-rating">Needed help or made a mistake? <strong>Again.</strong><br>
  Correct without help? <strong>Good.</strong></p>
</main>
"""
