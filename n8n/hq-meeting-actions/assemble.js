// Code node "Assemble the meeting" (all items). One output item per meeting, same order as "Split meetings".
// ---8<---
const mcp = function (x) {
  if (!x) { return {}; }
  if (Array.isArray(x.content)) {
    const t = x.content.filter(function (c) { return c && c.type === 'text'; }).map(function (c) { return c.text; }).join('\n');
    try { return JSON.parse(t); } catch (e) { return { text: t }; }
  }
  if (typeof x.result === 'string') { try { return JSON.parse(x.result); } catch (e) { return { text: x.result }; } }
  return x.result && typeof x.result === 'object' ? x.result : x;
};
const pick = function (o) { return String(o.transcript || o.transcript_text || (o.transcript_range && o.transcript_range.text) || ''); };
const strip = function (s) { return s.replace(/\[[^\]]*(truncated|continu|start_char)[^\]]*\]/gi, '').trim(); };
const meetings = $('Split meetings').all();
const parts = ['Transcript part 1', 'Transcript part 2', 'Transcript part 3'].map(function (n) { try { return $(n).all(); } catch (e) { return []; } });
const people = $('Who was there').all();
return meetings.map(function (m, i) {
  const p1 = mcp(parts[0][i] && parts[0][i].json);
  const chunks = parts.map(function (arr) { return strip(pick(mcp(arr[i] && arr[i].json))); }).filter(Boolean);
  const raw3 = pick(mcp(parts[2][i] && parts[2][i].json));
  const who = mcp(people[i] && people[i].json);
  const attendees = (who.participants || []).map(function (p) {
    return { name: p.name || '', relationship: p.relationship || '', spoke: !!p.spoke };
  });
  return { json: {
    meeting_id: m.json.meeting_id,
    title: m.json.title,
    start: m.json.start || String(p1.start_time || ''),
    share_link: m.json.share_link || String(p1.share_link || ''),
    summary: String(p1.summary || '').slice(0, 6000),
    attendees: attendees,
    transcript: chunks.join('\n'),
    transcript_cut: /truncated|continu|start_char/i.test(raw3),
  } };
});
