// Render a local HTML file to PDF or PNG with the built-in Chromium.
//   node render_html.js in.html out.pdf WIDTH HEIGHT     one page per <section>, page size W x H px
//   node render_html.js in.html out.png WIDTH [HEIGHT]   full-page screenshot at W px wide
// Waits for web fonts so Sora and Inter are embedded, not substituted.
const {chromium} = require('playwright');
(async () => {
  const [inp, out, w, h] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: +w, height: +(h || 1000)}, deviceScaleFactor: out.endsWith('.png') ? 2 : 1});
  await p.goto('file://' + require('path').resolve(inp), {waitUntil: 'networkidle'});
  await p.evaluate(() => document.fonts.ready);
  if (out.endsWith('.pdf')) await p.pdf({path: out, width: `${w}px`, height: `${h}px`, printBackground: true});
  else await p.screenshot({path: out, fullPage: true});
  await b.close();
})();
