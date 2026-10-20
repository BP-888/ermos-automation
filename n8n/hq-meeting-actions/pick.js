// Code node "Pick new meetings" (all items).
// ---8<---
const mcp = function (x) {
  if (!x) { return {}; }
  if (x.structuredContent && typeof x.structuredContent === 'object') { return x.structuredContent; }
  if (Array.isArray(x.content)) {
    const obj = x.content.filter(function (c) { return c && c.type === 'text' && c.text && typeof c.text === 'object'; })[0];
    if (obj) { return obj.text; }
    const t = x.content.filter(function (c) { return c && c.type === 'text'; }).map(function (c) { return c.text; }).join('\n');
    try { return JSON.parse(t); } catch (e) { return { text: t }; }
  }
  if (typeof x.result === 'string') { try { return JSON.parse(x.result); } catch (e) { return { text: x.result }; } }
  return x.result && typeof x.result === 'object' ? x.result : x;
};
const found = mcp($('Find meetings').first().json);
const list = Array.isArray(found.meetings) ? found.meetings : [];
const doneRows = ($('Read done meetings').first().json.results) || [];
const done = {};
doneRows.forEach(function (row) {
  const p = (row.properties || {})['Meeting ID'];
  const id = p && p.rich_text ? p.rich_text.map(function (t) { return t.plain_text; }).join('') : '';
  if (id) { done[id] = true; }
});
const now = Date.now();
const fresh = [];
const skipped = [];
list.forEach(function (m) {
  const id = String(m.id || m.meeting_id || '');
  const end = Date.parse(m.end_time || m.ended_at || m.end || '');
  if (!id) { return; }
  if (done[id]) { skipped.push(id + ' already done'); return; }
  if (!m.has_transcript) { skipped.push(id + ' no transcript yet'); return; }
  if (!isNaN(end) && end > now) { skipped.push(id + ' still running'); return; }
  fresh.push({
    meeting_id: id,
    title: String(m.title || 'Untitled meeting'),
    start: String(m.start_time || m.started_at || m.start || ''),
    end: String(m.end_time || m.ended_at || m.end || ''),
    share_link: String(m.share_link || ''),
  });
});
return [{ json: { meetings: fresh, count: fresh.length, seen: list.length, skipped: skipped, more_available: !!found.has_more } }];
