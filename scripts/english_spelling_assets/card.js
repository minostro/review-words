(function () {
  'use strict';

  function createPuzzle(answer, mode, mask) {
    var letters = Array.from(answer);
    var hidden = letters.map(function (_, i) { return i; }).filter(function (i) {
      return /[a-z]/i.test(letters[i]) && (mode === 'build' || mask.indexOf(i) !== -1);
    });
    var tiles = hidden.map(function (i, n) { return { id: 'tile-' + n, letter: letters[i] }; });
    if (mode === 'complete') {
      var choices = ['e', 'a', 'i', 'o', 'u', 's', 't', 'r', 'n', 'l'];
      choices.filter(function (letter) {
        return !tiles.some(function (tile) { return tile.letter.toLowerCase() === letter; });
      }).slice(0, 2).forEach(function (letter) {
        tiles.push({ id: 'tile-' + tiles.length, letter: letter });
      });
    }
    var puzzle = {
      letters: letters, hidden: hidden, tiles: tiles, placed: {},
      place: function (id, index) {
        if (hidden.indexOf(index) === -1 || puzzle.placed[index] ||
            Object.keys(puzzle.placed).some(function (key) { return puzzle.placed[key] === id; }) ||
            !tiles.some(function (tile) { return tile.id === id; })) return false;
        puzzle.placed[index] = id;
        return true;
      },
      remove: function (index) {
        var id = puzzle.placed[index];
        delete puzzle.placed[index];
        return id;
      },
      reset: function () { puzzle.placed = {}; },
      check: function () {
        var statuses = {}, missing = 0, correct = true;
        hidden.forEach(function (i) {
          var tile = tiles.find(function (t) { return t.id === puzzle.placed[i]; });
          statuses[i] = !tile ? 'empty' : tile.letter === letters[i] ? 'correct' : 'wrong';
          if (!tile) missing++;
          if (statuses[i] !== 'correct') correct = false;
        });
        return { correct: correct, missing: missing, statuses: statuses };
      }
    };
    return puzzle;
  }

  function init(root) {
    if (root._spellingCleanup) root._spellingCleanup();
    var answer = root.querySelector('[data-answer]').textContent;
    var mask = JSON.parse(root.querySelector('[data-mask]').textContent || '[]');
    var puzzle = createPuzzle(answer, root.getAttribute('data-mode'), mask);
    var board = root.querySelector('.spelling-board');
    var tray = root.querySelector('.spelling-tray');
    var feedback = root.querySelector('.spelling-feedback');
    var selected = null, checked = null, drag = null, suppressClickUntil = 0;
    var tileOrder = puzzle.tiles.slice();
    for (var n = tileOrder.length - 1; n > 0; n--) {
      var j = Math.floor(Math.random() * (n + 1)), swap = tileOrder[n];
      tileOrder[n] = tileOrder[j]; tileOrder[j] = swap;
    }
    var listeners = [];
    function listen(type, handler, options) {
      root.addEventListener(type, handler, options);
      listeners.push([type, handler, options]);
    }
    function tileById(id) { return puzzle.tiles.find(function (tile) { return tile.id === id; }); }
    function say(message) { feedback.textContent = message; }
    function render() {
      board.textContent = ''; tray.textContent = '';
      var word = null;
      puzzle.letters.forEach(function (letter, index) {
        if (/\s/.test(letter)) { word = null; return; }
        if (!word) {
          word = document.createElement('span'); word.className = 'spelling-word';
          var length = 0;
          while (index + length < puzzle.letters.length && !/\s/.test(puzzle.letters[index + length])) length++;
          word.style.setProperty('--word-length', length);
          board.appendChild(word);
        }
        var hidden = puzzle.hidden.indexOf(index) !== -1;
        var cell = document.createElement(hidden ? 'button' : 'span');
        cell.className = hidden ? 'spelling-gap' : 'spelling-fixed';
        if (hidden) {
          cell.type = 'button'; cell.setAttribute('data-gap', index);
          var tile = tileById(puzzle.placed[index]);
          cell.textContent = tile ? tile.letter : '\u00a0';
          cell.setAttribute('aria-label', tile ? 'Letter ' + tile.letter + ', tap to return' : 'Empty letter space ' + (index + 1));
          if (tile) cell.classList.add('is-filled');
          if (checked) {
            cell.classList.add('is-' + checked.statuses[index]);
            cell.setAttribute('aria-label', cell.getAttribute('aria-label') + ', ' + checked.statuses[index]);
          }
        } else { cell.textContent = letter; }
        word.appendChild(cell);
      });
      tileOrder.forEach(function (tile) {
        if (Object.keys(puzzle.placed).some(function (key) { return puzzle.placed[key] === tile.id; })) return;
        var button = document.createElement('button');
        button.type = 'button'; button.className = 'spelling-tile';
        button.textContent = tile.letter; button.setAttribute('data-tile', tile.id);
        button.setAttribute('aria-label', 'Letter ' + tile.letter);
        button.setAttribute('aria-pressed', selected === tile.id ? 'true' : 'false');
        if (selected === tile.id) button.classList.add('is-selected');
        tray.appendChild(button);
      });
    }
    function place(id, index) {
      if (puzzle.place(id, index)) {
        checked = null; selected = null;
        say('Keep going. Tap Check when you are ready.'); render();
      }
    }
    function endDrag() {
      var previous = drag; drag = null;
      if (!previous) return;
      if (previous.ghost) previous.ghost.remove();
      previous.button.classList.remove('is-dragging');
      root.querySelectorAll('.is-drop-target').forEach(function (gap) { gap.classList.remove('is-drop-target'); });
      if (previous.button.hasPointerCapture && previous.button.hasPointerCapture(previous.pointerId)) {
        previous.button.releasePointerCapture(previous.pointerId);
      }
    }
    function gapAt(x, y) {
      var element = document.elementFromPoint(x, y);
      var gap = element && element.closest('[data-gap]');
      return gap && root.contains(gap) && !puzzle.placed[Number(gap.getAttribute('data-gap'))] ? gap : null;
    }
    listen('click', function (event) {
      if (Date.now() < suppressClickUntil) { event.preventDefault(); return; }
      var tile = event.target.closest('[data-tile]');
      var gap = event.target.closest('[data-gap]');
      var action = event.target.closest('[data-action]');
      if (tile) {
        selected = selected === tile.getAttribute('data-tile') ? null : tile.getAttribute('data-tile');
        say(selected ? 'Now tap an empty space.' : 'Choose a letter.'); render();
      } else if (gap) {
        var index = Number(gap.getAttribute('data-gap'));
        if (puzzle.placed[index]) {
          puzzle.remove(index); checked = null;
          say('Letter returned. You can try another.'); render();
        } else if (selected) place(selected, index);
        else say('Tap a letter first, then tap an empty space.');
      } else if (action) {
        endDrag();
        if (action.getAttribute('data-action') === 'reset') {
          puzzle.reset(); selected = null; checked = null;
          say('Fresh start. Listen, then choose your letters.'); render();
        } else {
          checked = puzzle.check();
          say(checked.correct ? 'That matches! Show Answer when you are ready.' : checked.missing ?
            'Some spaces are empty. Keep building, then check again.' : 'Some letters need another look. Listen and try again.');
          render();
        }
      }
    });
    listen('pointerdown', function (event) {
      var tile = event.target.closest('[data-tile]');
      if (!tile || event.isPrimary === false || (event.button !== undefined && event.button !== 0)) return;
      endDrag();
      drag = { id: tile.getAttribute('data-tile'), button: tile, pointerId: event.pointerId,
        x: event.clientX, y: event.clientY, active: false, ghost: null };
      if (tile.setPointerCapture) tile.setPointerCapture(event.pointerId);
    });
    listen('pointermove', function (event) {
      if (!drag || event.pointerId !== drag.pointerId) return;
      if (!drag.active && Math.hypot(event.clientX - drag.x, event.clientY - drag.y) < 8) return;
      if (!drag.active) {
        drag.active = true; drag.button.classList.add('is-dragging');
        drag.ghost = document.createElement('span'); drag.ghost.className = 'spelling-drag-ghost';
        drag.ghost.textContent = tileById(drag.id).letter; drag.ghost.setAttribute('aria-hidden', 'true');
        root.appendChild(drag.ghost);
      }
      event.preventDefault();
      drag.ghost.style.left = event.clientX + 'px'; drag.ghost.style.top = event.clientY + 'px';
      root.querySelectorAll('.is-drop-target').forEach(function (gap) { gap.classList.remove('is-drop-target'); });
      var gap = gapAt(event.clientX, event.clientY); if (gap) gap.classList.add('is-drop-target');
    }, { passive: false });
    listen('pointerup', function (event) {
      if (!drag || event.pointerId !== drag.pointerId) return;
      var active = drag.active, id = drag.id;
      var gap = active ? gapAt(event.clientX, event.clientY) : null;
      endDrag();
      if (active) {
        suppressClickUntil = Date.now() + 350;
        event.preventDefault();
        if (gap) place(id, Number(gap.getAttribute('data-gap')));
        else say('Drop on an empty space, or tap a letter then a space.');
      }
    });
    listen('pointercancel', endDrag);
    listen('lostpointercapture', endDrag);
    root._spellingCleanup = function () {
      endDrag();
      listeners.forEach(function (entry) { root.removeEventListener(entry[0], entry[1], entry[2]); });
      delete root._spellingCleanup;
    };
    render();
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { createPuzzle: createPuzzle, init: init };
  if (typeof document !== 'undefined') {
    var root = document.getElementById('spelling-card');
    if (root) init(root);
  }
}());
