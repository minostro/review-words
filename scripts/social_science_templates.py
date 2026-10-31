"""Shared Anki and browser markup. Audio is never exposed as a native sound tag."""
from pathlib import Path

ASSETS = Path(__file__).with_name('social_science_assets')
STYLING = (ASSETS / 'card.css').read_text(encoding='utf-8')
SCRIPT = (ASSETS / 'card.js').read_text(encoding='utf-8')


def template(side):
    return '''<main class="social-shell" id="social-card" data-key="{{NoteKey}}" data-correct="{{CorrectKey}}" data-side="SIDE">
  <div class="social-topline"><span class="social-subject">Social Science · October</span><span class="social-category">{{Category}}</span></div>
  <h1 class="social-question">{{Question}}</h1>
  <div class="social-context">{{Picture}}</div>
  <div class="social-audio"><button type="button" class="social-hear" data-action="hear">▶ Hear question</button>
    <audio preload="none" src="{{QuestionAudio}}"></audio><span class="social-audio-status" role="status"></span></div>
  <div class="social-choices" role="group" aria-label="Choose one answer">{{Choices}}</div>
  <p class="social-feedback" role="status" aria-live="polite"></p>
  <div class="social-explanation" hidden><strong>{{CorrectLabel}}</strong><br>{{Explanation}}</div>
  <p class="social-rating">Use Show Answer when you are ready.<br>Wrong or needed the answer? <strong>Again.</strong> Understood it? <strong>Good.</strong></p>
</main>
<script>SCRIPT</script>'''.replace('SIDE', side).replace('SCRIPT', SCRIPT)


FRONT = template('front')
BACK = template('back').replace('Use Show Answer when you are ready.<br>', '')
