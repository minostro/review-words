const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const source = path.join(__dirname, '../scripts/english_spelling_assets/card.js');
const createPuzzle = fs.existsSync(source) ? require(source).createPuzzle : undefined;

test('duplicate letters are separate tiles and cannot be used twice', () => {
  assert.equal(typeof createPuzzle, 'function', 'spelling model is implemented');
  const p = createPuzzle('leaves', 'build', []);
  const es = p.tiles.filter(t => t.letter === 'e');
  assert.equal(es.length, 2);
  assert.notEqual(es[0].id, es[1].id);
  assert.equal(p.place(es[0].id, 1), true);
  assert.equal(p.place(es[0].id, 4), false);
  assert.equal(p.place(es[1].id, 4), true);
  assert.equal(p.remove(1), es[0].id);
  assert.equal(p.place(es[0].id, 1), true);
});

test('build fixes punctuation and spaces and preserves weekday capitals', () => {
  assert.equal(typeof createPuzzle, 'function');
  const p = createPuzzle("mustn't wash", 'build', []);
  assert.equal(p.hidden.includes(5), false);
  assert.equal(p.hidden.includes(7), false);
  assert.equal(p.tiles.length, 10);
  assert.equal(createPuzzle('Wednesday', 'build', []).tiles[0].letter, 'W');
});

test('completion uses the selected mask and adds exactly two distractors', () => {
  assert.equal(typeof createPuzzle, 'function');
  const p = createPuzzle('Wednesday', 'complete', [2, 3]);
  assert.deepEqual(p.hidden, [2, 3]);
  assert.equal(p.tiles.length, 4);
  assert.deepEqual(p.tiles.slice(0, 2).map(t => t.letter), ['d', 'n']);
});

test('checking preserves a wrong attempt, tracks gaps, and reset clears it', () => {
  assert.equal(typeof createPuzzle, 'function');
  const p = createPuzzle('cat', 'build', []);
  p.place('tile-0', 1);
  assert.deepEqual(p.check(), { correct: false, missing: 2, statuses: {0: 'empty', 1: 'wrong', 2: 'empty'} });
  assert.equal(p.placed[1], 'tile-0');
  p.reset();
  assert.deepEqual(p.placed, {});
  for (let i = 0; i < 3; i++) p.place('tile-' + i, i);
  assert.equal(p.check().correct, true);
});
