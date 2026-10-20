// n8n Code node "Load HQ rules" (run once for all items). Input: blocks from "Read page text".
// ---8<---
const pages = $('HQ pages').all().map(function (i) { return i.json; });
const vers = $('Read page version').all().map(function (i) { return i.json; });
const rt = function (arr) { return (arr || []).map(function (t) { return (t.plain_text || '') + (t.href && (t.plain_text || '').indexOf(t.href) === -1 ? ' (' + t.href + ')' : ''); }).join(''); };
const lineOf = function (b) {
  const v = b[b.type] || {};
  if (b.type === 'table_row') { return (v.cells || []).map(function (c) { return rt(c); }).join(' | '); }
  if (b.type === 'bookmark' || b.type === 'embed' || b.type === 'link_preview') { return v.url || ''; }
  if (b.type === 'child_page' || b.type === 'child_database') { return ''; }
  const s = rt(v.rich_text || v.text);
  if (/^heading_/.test(b.type)) { return '#'.repeat(Number(b.type.slice(-1)) + 1) + ' ' + s; }
  if (b.type === 'bulleted_list_item' || b.type === 'numbered_list_item' || b.type === 'to_do') { return '- ' + s; }
  return s;
};
const norm = function (id) { return String(id || '').replace(/-/g, ''); };
const pageIdx = {};
pages.forEach(function (p, k) { pageIdx[norm(p.id)] = k; });
const blocks = $input.all().map(function (i) { return i.json; });
const parentOf = {};
blocks.forEach(function (b) { parentOf[norm(b.id)] = norm(b.parent_id || (b.parent && (b.parent.page_id || b.parent.block_id))); });
const pageOf = function (id) {
  let cur = norm(id);
  for (let n = 0; n < 20 && cur; n++) {
    if (pageIdx[cur] !== undefined) { return pageIdx[cur]; }
    cur = parentOf[cur];
  }
  return -1;
};
const texts = pages.map(function () { return []; });
blocks.forEach(function (b) {
  const k = pageOf(b.id);
  if (k >= 0) { const l = lineOf(b); if (l && l.trim() && !/^[#-]+\s*$/.test(l.trim())) { texts[k].push(l); } }
});
const prop = function (p) {
  if (!p) { return ''; }
  if (p.type === 'select') { return p.select ? p.select.name : ''; }
  if (p.type === 'status') { return p.status ? p.status.name : ''; }
  if (p.type === 'rich_text') { return rt(p.rich_text); }
  if (p.type === 'title') { return rt(p.title); }
  return '';
};
const missing = [];
const parts = pages.map(function (p, k) {
  const props = (vers[k] && vers[k].properties) || {};
  const version = prop(props.Version) || 'no version';
  const status = prop(props.Status) || 'no status';
  if (!texts[k].length) { missing.push(p.name); }
  return { name: p.name, version: version, status: status, text: texts[k].join('\n') };
});
return [{ json: {
  rules_text: parts.map(function (p) { return '=== ' + p.name + ' (' + p.version + ', ' + p.status + ') ===\n' + p.text; }).join('\n\n'),
  versions: parts.map(function (p) { return p.name + ' ' + p.version; }).join('; '),
  missing_pages: missing,
} }];
