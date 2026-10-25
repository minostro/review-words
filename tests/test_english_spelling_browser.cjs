// Run with Playwright available on NODE_PATH; uses installed Chrome by default.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { chromium } = require('playwright');
const os = require('node:os');
const repo = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(repo, 'scripts/english_spelling_assets/card.js'), 'utf8');
const template = execFileSync('python3', ['-c', 'import json; from scripts.english_spelling_templates import front_template, STYLING; print(json.dumps({"front":front_template("build"),"css":STYLING}))'], {cwd: repo, encoding:'utf8'});
const assets = JSON.parse(template);
function html(answer) {
  return '<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>' + assets.css + '</style></head><body class="card">' + assets.front.replace('{{Answer}}', answer).replace('{{Unit}}', '1').replace('{{Picture}}', '').replace('{{Audio}}', '') + '</body></html>';
}

test('preview autoplays only whole-word prompts and keeps manual audio on every side', async () => {
  const folder = fs.mkdtempSync(path.join(os.tmpdir(), 'spelling-audio-'));
  const browser = await chromium.launch({headless:true, channel:process.env.SPELLING_BROWSER_CHANNEL || 'chrome'});
  try {
    execFileSync(process.env.SPELLING_PYTHON || 'python3', ['-c',
      'import sys; from pathlib import Path; from scripts.build_english_spelling_apkg import write_preview; p=Path(sys.argv[1]); (p/"audio").mkdir(); write_preview(p,p/"audio")', folder], {cwd:repo});
    const page = await browser.newPage();
    // Observe playback requests without relying on Chrome's autoplay policy or speakers.
    await page.addInitScript(() => {
      window.playRequests = [];
      HTMLMediaElement.prototype.play = function () { window.playRequests.push(this.getAttribute('src')); return Promise.resolve(); };
    });
    await page.goto('file://' + path.join(folder, 'preview.html'));
    for (const index of ['0', '1', '2', '4', '5', '6']) {
      await page.selectOption('#choose', index);
      assert.equal(await page.evaluate(() => window.playRequests.length), 0);
      assert.equal(await page.locator('audio').evaluate(a => a.controls && !a.autoplay), true);
      assert.match(await page.locator('audio').getAttribute('src'), /^audio\/english-spelling-.*\.mp3$/);
    }
    await page.selectOption('#choose', '3');
    assert.equal(await page.evaluate(() => window.playRequests.length), 1);
    await page.click('#flip');
    assert.equal(await page.evaluate(() => window.playRequests.length), 1);
    assert.equal(await page.locator('audio').evaluate(a => a.controls), true);
    await page.selectOption('#choose', '0');
    assert.equal(await page.evaluate(() => window.playRequests.length), 1);
    await page.locator('audio').evaluate(a => a.play());
    assert.equal(await page.evaluate(() => window.playRequests.length), 2);
  } finally {
    await browser.close();
    fs.rmSync(folder, {recursive:true, force:true});
  }
});

test('mobile tap, drag, cancellation, reset, checks, and repeated initialization', async () => {
  const browser = await chromium.launch({headless: true, channel: process.env.SPELLING_BROWSER_CHANNEL || 'chrome'});
  try {
    const context = await browser.newContext({viewport: {width:360,height:780}, hasTouch:true, isMobile:true});
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.setContent(html('leaves'));
    await page.locator('[data-tile="tile-0"]').tap();
    await page.locator('[data-gap="1"]').tap();
    await page.locator('[data-action="check"]').tap();
    assert.equal(await page.locator('[data-gap="1"]').textContent(), 'l');
    assert.match(await page.locator('[data-gap="1"]').getAttribute('class'), /is-wrong/);
    await page.locator('[data-gap="1"]').tap();
    assert.equal(await page.locator('[data-tile]').count(), 6);
    for (let i = 0; i < 6; i++) {
      await page.locator('[data-tile="tile-' + i + '"]').tap();
      await page.locator('[data-gap="' + i + '"]').tap();
    }
    await page.locator('[data-action="check"]').tap();
    assert.equal(await page.locator('.is-correct').count(), 6);
    await page.locator('[data-action="reset"]').tap();
    assert.equal(await page.locator('[data-tile]').count(), 6);
    assert.equal(await page.locator('.is-filled').count(), 0);

    // Installing the same script twice must replace handlers, not duplicate them.
    await page.evaluate(source);
    await page.evaluate(source);
    await page.locator('[data-tile="tile-0"]').tap();
    assert.equal(await page.locator('[aria-pressed="true"]').count(), 1);
    await page.locator('[data-gap="0"]').tap();
    assert.equal(await page.locator('.is-filled').count(), 1);
    await page.locator('[data-action="reset"]').tap();

    const tile = await page.locator('[data-tile="tile-0"]').boundingBox();
    const gap = await page.locator('[data-gap="0"]').boundingBox();
    await page.mouse.move(tile.x + tile.width/2, tile.y + tile.height/2);
    await page.mouse.down();
    await page.mouse.move(gap.x + gap.width/2, gap.y + gap.height/2, {steps:8});
    assert.equal(await page.locator('.spelling-drag-ghost').count(), 1);
    await page.mouse.up();
    assert.equal(await page.locator('.spelling-drag-ghost').count(), 0);
    assert.equal(await page.locator('[data-gap="0"]').textContent(), 'l');
    // Let the browser's synthetic click window expire before starting a new action.
    await page.waitForTimeout(360);
    await page.locator('[data-action="reset"]').tap();
    const cancelTile = await page.locator('[data-tile="tile-0"]').boundingBox();
    await page.mouse.move(cancelTile.x + 20, cancelTile.y + 20);
    await page.mouse.down();
    await page.mouse.move(cancelTile.x + 45, cancelTile.y - 10, {steps:4});
    assert.equal(await page.locator('.spelling-drag-ghost').count(), 1);
    await page.locator('#spelling-card').dispatchEvent('pointercancel', {pointerId:1});
    assert.equal(await page.locator('.spelling-drag-ghost').count(), 0);
    assert.equal(await page.locator('.is-dragging').count(), 0);
    await page.mouse.up();
    assert.deepEqual(errors, []);

    for (const answer of ['Wednesday', 'to wash your hands', "mustn't"]) {
      await page.setContent(html(answer));
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true, answer + ' overflows');
      const sizes = await page.locator('[data-tile]').evaluateAll(nodes => nodes.map(n => ({w:n.getBoundingClientRect().width,h:n.getBoundingClientRect().height})));
      assert.ok(sizes.every(s => s.w >=44 && s.h >=44));
      assert.equal(await page.locator('[data-gap]').count(), answer.replace(/[^a-z]/gi, '').length);
    }
  } finally { await browser.close(); }
});
