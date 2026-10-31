const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');
const {chromium}=require('playwright');
const repo=path.resolve(__dirname,'..');

test('comprehension choices, locked feedback, flip memory, manual audio and mobile layout',async()=>{
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'social-preview-'));
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try {
  execFileSync(process.env.SPELLING_PYTHON||'python3',['-c',
   'import sys; from pathlib import Path; from scripts.build_social_science_apkg import write_preview; p=Path(sys.argv[1]); (p/"audio").mkdir(); write_preview(p,p/"audio")',tmp],{cwd:repo});
  const page=await browser.newPage({viewport:{width:360,height:780},hasTouch:true,isMobile:true});
  await page.addInitScript(()=>{window.audioRequests=[]; HTMLMediaElement.prototype.play=function(){window.audioRequests.push(this.getAttribute('src'));return Promise.resolve()};});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('file://'+path.join(tmp,'preview.html'));
  assert.equal(await page.evaluate(()=>window.audioRequests.length),0);
  await page.locator('[data-action="hear"]').tap();
  assert.equal(await page.evaluate(()=>window.audioRequests.length),1);
  const correct=await page.locator('#social-card').getAttribute('data-correct');
  const wrongKey=await page.locator('[data-choice]').evaluateAll((nodes,c)=>nodes.find(n=>n.dataset.choice!==c).dataset.choice,correct);
  const originalOrder=await page.locator('[data-choice]').evaluateAll(n=>n.map(x=>x.dataset.choice));
  await page.locator(`[data-choice="${wrongKey}"]`).tap();
  assert.match(await page.locator('.social-feedback').textContent(),/Not quite/);
  assert.equal(await page.locator('[data-choice]:disabled').count(),3);
  assert.equal(await page.locator('.is-wrong').count(),1);
  assert.equal(await page.locator('.is-correct').count(),1);
  assert.equal(await page.locator('.social-explanation').isVisible(),true);
  await page.locator('#flip').tap();
  assert.deepEqual(await page.locator('[data-choice]').evaluateAll(n=>n.map(x=>x.dataset.choice)),originalOrder);
  assert.equal(await page.locator('.is-wrong').count(),1);
  assert.equal(await page.evaluate(()=>window.audioRequests.length),1);
  await page.locator('#flip').tap();
  assert.equal(await page.locator('[data-choice]:disabled').count(),0);
  await page.locator(`[data-choice="${correct}"]`).tap();
  assert.match(await page.locator('.social-feedback').textContent(),/That's right/);
  await page.locator('#next').tap();
  assert.equal(await page.locator('[data-choice]:disabled').count(),0);
  // Every generated card fits a narrow phone and has no broken image references.
  const count=await page.locator('#choose option').count();
  for(let i=0;i<count;i++){
   await page.selectOption('#choose',String(i));
   await page.waitForFunction(()=>Array.from(document.querySelectorAll('#social-card img')).every(x=>x.complete));
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`overflow card ${i}`);
   assert.equal(await page.locator('#social-card img').evaluateAll(ns=>ns.every(n=>n.naturalWidth>0)),true,`images card ${i}`);
   assert.equal(await page.locator('[data-choice]').evaluateAll(ns=>ns.every(n=>n.getBoundingClientRect().height>=48)),true);
  }
  assert.equal(await page.evaluate(()=>window.audioRequests.length),1);
  assert.deepEqual(errors,[]);
 } finally {await browser.close();fs.rmSync(tmp,{recursive:true,force:true});}
});
