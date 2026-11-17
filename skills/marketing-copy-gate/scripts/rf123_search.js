// 123RF image research for LinkedIn posts (SOP step 5a: own photos, then 123RF, then
// Unsplash or Pexels). Opens 123RF in the built-in Chromium (it passes 123RF's bot
// check, plain requests do not), runs each search, and for each result keeps the
// image number, title, contributor, listing URL and watermarked preview.
//
//   node rf123_search.js OUTDIR "search one" "search two" ...      search, photos only
//   node rf123_search.js --check OUTDIR 123456789 987654321 ...   open listings, read type
//
// Search writes OUTDIR/results.json and OUTDIR/previews/<id>.jpg. --check writes
// OUTDIR/listings.json with each listing's type label (the line under the image number:
// "Stock Photo" or "AI-generated image"), contributor, largest size and any keyword that
// suggests a 3D render or AI, for the evidence record.
// Never buys or downloads a licensed file: Brad licenses on his paid account.
const {chromium} = require('playwright');
const fs = require('fs');
const path = require('path');

const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36';

async function open(ctx, url) {
  const p = await ctx.newPage();
  await p.goto(url, {waitUntil: 'domcontentloaded', timeout: 60000});
  for (let i = 0; i < 12; i++) {
    await p.waitForTimeout(2000);
    if (!/Verification/i.test(await p.title())) break;
  }
  return p;
}

function imageObjects(html) {
  const out = [];
  const re = /<script[^>]*application\/ld\+json[^>]*>([\s\S]*?)<\/script>/g;
  let m;
  while ((m = re.exec(html))) {
    let j;
    try { j = JSON.parse(m[1]); } catch (e) { continue; }
    const walk = (x) => {
      if (Array.isArray(x)) return x.forEach(walk);
      if (x && typeof x === 'object') {
        if (x['@type'] === 'ImageObject' && x.acquireLicensePage) out.push(x);
        Object.values(x).forEach(walk);
      }
    };
    walk(j);
  }
  return out;
}

async function search(outdir, queries) {
  fs.mkdirSync(path.join(outdir, 'previews'), {recursive: true});
  const b = await chromium.launch();
  const ctx = await b.newContext({userAgent: UA, viewport: {width: 1400, height: 1000}});
  const seen = new Map();
  for (const q of queries) {
    const url = `https://www.123rf.com/stock-photo/${encodeURIComponent(q.trim().replace(/\s+/g, '_'))}.html?imgtype=1`;
    const p = await open(ctx, url);
    const objs = imageObjects(await p.content());
    await p.close();
    for (const o of objs) {
      const id = (o.acquireLicensePage.match(/photo_(\d+)_/) || [])[1];
      if (!id || seen.has(id)) continue;
      seen.set(id, {id, query: q, title: o.name, contributor: (o.creator || {}).name || o.copyrightNotice,
                    listing: o.acquireLicensePage, preview: o.contentUrl});
    }
    console.error(`${q}: ${objs.length} results`);
  }
  for (const r of seen.values()) {
    try {
      const res = await ctx.request.get(r.preview);
      if (res.ok()) fs.writeFileSync(path.join(outdir, 'previews', `${r.id}.jpg`), await res.body());
    } catch (e) { r.preview_error = String(e); }
  }
  fs.writeFileSync(path.join(outdir, 'results.json'), JSON.stringify([...seen.values()], null, 1));
  console.log(`${seen.size} images -> ${outdir}`);
  await b.close();
}

async function check(outdir, ids) {
  const b = await chromium.launch();
  const ctx = await b.newContext({userAgent: UA, viewport: {width: 1400, height: 1000}});
  let known = [];
  try { known = JSON.parse(fs.readFileSync(path.join(outdir, 'results.json'))); } catch (e) {}
  const out = [];
  for (const id of ids) {
    const k = known.find(x => x.id === id);
    const p = await open(ctx, k ? k.listing : `https://www.123rf.com/photo_${id}_.html`);
    await p.waitForTimeout(3000);
    await p.mouse.wheel(0, 1500);
    await p.waitForTimeout(2500);
    const lines = (await p.evaluate(() => document.body.innerText)).split('\n').map(s => s.trim()).filter(Boolean);
    const at = lines.indexOf(id);
    const label = at >= 0 ? lines[at + 1] : '';
    const rel = lines.indexOf('Related searches');
    const keywords = rel >= 0 && at > rel ? lines.slice(rel + 1, at).filter(w => !/^(Show More|Collection|Preview|Share)$/.test(w)) : [];
    const sizes = lines.filter(l => /\d+ x \d+ px/.test(l));
    out.push({id, listing: p.url(), title: (await p.title()).replace(/ Stock Photo, Picture.*$/, ''),
              contributor: rel > 1 ? lines[rel - 1] : '',
              available: !lines.some(l => /no longer available/i.test(l)),
              type_label: label,
              stock_photo: label === 'Stock Photo',
              ai_generated: /ai[- ]generated|generated with ai/i.test(label),
              render_or_ai_keywords: keywords.filter(w => /^(3d|render|rendering|illustration|ai|generative|generated|cgi)$/i.test(w)),
              largest_size: sizes[sizes.length - 1] || ''});
    await p.close();
  }
  fs.mkdirSync(outdir, {recursive: true});
  fs.writeFileSync(path.join(outdir, 'listings.json'), JSON.stringify(out, null, 1));
  console.log(JSON.stringify(out, null, 1));
  await b.close();
}

(async () => {
  const a = process.argv.slice(2);
  if (a[0] === '--check') await check(a[1], a.slice(2));
  else await search(a[0], a.slice(1));
})();
