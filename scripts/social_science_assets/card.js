(function () {
  'use strict';
  var root = document.getElementById('social-card');
  if (!root) return;
  if (root._socialCleanup) root._socialCleanup();
  var list = root.querySelector('.social-choices');
  var buttons = Array.from(list.querySelectorAll('[data-choice]'));
  var key = root.getAttribute('data-key');
  var correct = root.getAttribute('data-correct');
  var back = root.getAttribute('data-side') === 'back';
  var feedback = root.querySelector('.social-feedback');
  var explanation = root.querySelector('.social-explanation');
  var audio = root.querySelector('audio');
  var hear = root.querySelector('[data-action="hear"]');
  var storageKey = 'salvador-social-oct26-attempt';
  var state = root._socialState;
  function remember() {
    window._salvadorSocialAttempt = state;
    try { sessionStorage.setItem(storageKey, JSON.stringify(state)); } catch (_) { /* Some WebViews disable storage. */ }
  }
  if (!state && back) {
    state = window._salvadorSocialAttempt;
    if (!state) {
      try { state = JSON.parse(sessionStorage.getItem(storageKey)); } catch (_) { state = null; }
    }
    if (!state || state.key !== key) state = null;
  }
  if (!state) {
    var order = buttons.map(function (b) { return b.getAttribute('data-choice'); });
    if (!back) {
      for (var i = order.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1)), swap = order[i];
        order[i] = order[j]; order[j] = swap;
      }
    }
    state = {key:key, order:order, selected:null};
  }
  root._socialState = state;
  state.order.forEach(function (id) {
    var button = buttons.find(function (b) { return b.getAttribute('data-choice') === id; });
    if (button) list.appendChild(button);
  });
  function showResult() {
    var answered = !!state.selected;
    buttons.forEach(function (button) {
      var id = button.getAttribute('data-choice');
      button.disabled = answered || back;
      button.classList.toggle('is-correct', (answered || back) && id === correct);
      button.classList.toggle('is-wrong', answered && id === state.selected && id !== correct);
      button.setAttribute('aria-pressed', id === state.selected ? 'true' : 'false');
      var mark = button.querySelector('.social-mark');
      mark.textContent = (answered || back) && id === correct ? '✓' : answered && id === state.selected ? '✕' : '';
    });
    explanation.hidden = !(answered || back);
    if (answered) {
      feedback.textContent = state.selected === correct ? "That's right!" : 'Not quite. The correct answer has a tick.';
    } else {
      feedback.textContent = back ? 'Read the answer and why it is correct.' : 'Read the question. Tap one answer.';
    }
  }
  function choose(event) {
    var button = event.target.closest('[data-choice]');
    if (!button || !list.contains(button) || back || state.selected) return;
    state.selected = button.getAttribute('data-choice');
    remember(); showResult();
  }
  function playQuestion() {
    var status = root.querySelector('.social-audio-status');
    status.textContent = '';
    audio.currentTime = 0;
    var playing = audio.play();
    if (playing && playing.catch) playing.catch(function () {
      status.textContent = 'Audio is unavailable. You can still read the question.';
    });
  }
  list.addEventListener('click', choose);
  hear.addEventListener('click', playQuestion);
  root._socialCleanup = function () {
    list.removeEventListener('click', choose);
    hear.removeEventListener('click', playQuestion);
    audio.pause();
  };
  if (!back) remember();
  showResult();
}());
