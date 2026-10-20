// Code node "Build the Notion rows" (all items). Input: Claude output per meeting, same order as "Assemble the meeting".
// ---8<---
const DB = 'f6850d5325b0468aa4095c737eb206ea';
const OWNERS = ['Brad', 'Will', 'David', 'External', 'Unassigned'];
const CONF = ['Stated', 'Inferred', 'Unassigned'];
const TYPES = ['Client', 'Team', 'Partner', 'Other'];
const meetings = $('Assemble the meeting').all();
const txt = function (s) { return [{ text: { content: String(s || '').slice(0, 1900) } }]; };
const out = [];
$input.all().forEach(function (item, i) {
  const m = meetings[i] ? meetings[i].json : {};
  const raw = item.json || {};
  const parts = Array.isArray(raw.content) ? raw.content.filter(function (c) { return c && c.type === 'text'; }).map(function (c) { return c.text; }) : [String(raw.text || '')];
  const text = parts.join('\n');
  let ai;
  const flags = [];
  try { const f = text.match(/```(?:json)?\s*([\s\S]*?)```/); ai = JSON.parse((f ? f[1] : text).trim()); }
  catch (e) { ai = { actions: [], decisions: [], open_questions: [], parked: [] }; flags.push('Claude did not return readable JSON; check this meeting by hand'); }
  if (m.transcript_cut) { flags.push('Transcript longer than 120,000 characters; only the first part was read'); }
  if (!m.transcript) { flags.push('Transcript came back empty'); }
  const type = TYPES.indexOf(ai.meeting_type) !== -1 ? ai.meeting_type : 'Other';
  const date = m.start ? { start: m.start } : null;
  const common = function (title, kind) {
    const p = {
      'Action': { title: txt(title) },
      'Kind': { select: { name: kind } },
      'Status': { select: { name: 'Open' } },
      'Meeting': { rich_text: txt(m.title) },
      'Meeting type': { select: { name: type } },
      'Meeting ID': { rich_text: txt(m.meeting_id) },
    };
    if (date) { p['Meeting date'] = { date: date }; }
    if (m.share_link) { p['Source'] = { url: m.share_link }; }
    return p;
  };
  const actions = ai.personal ? [] : (Array.isArray(ai.actions) ? ai.actions : []);
  actions.forEach(function (a) {
    if (!a || !String(a.action || '').trim()) { return; }
    let owner = OWNERS.indexOf(a.owner) !== -1 ? a.owner : 'Unassigned';
    let conf = CONF.indexOf(a.owner_confidence) !== -1 ? a.owner_confidence : 'Unassigned';
    if (owner === 'Unassigned') { conf = 'Unassigned'; }
    if (conf === 'Unassigned' && owner !== 'Unassigned') { owner = 'Unassigned'; }
    const alloc = owner === 'Brad' ? "Brad's own" : ((owner === 'Will' || owner === 'David') && conf === 'Stated' ? 'Email drafted' : 'Needs Brad');
    const p = common(a.action, 'Action');
    p['Owner'] = { select: { name: owner } };
    p['Owner confidence'] = { select: { name: conf } };
    p['Allocation'] = { select: { name: alloc } };
    if (a.owner_name) { p['Owner name'] = { rich_text: txt(a.owner_name) }; }
    if (/^\d{4}-\d{2}-\d{2}$/.test(String(a.due || ''))) { p['Due'] = { date: { start: a.due } }; }
    p['Why'] = { rich_text: txt(a.why || 'The meeting did not say why; check with Brad.') };
    p['Done when'] = { rich_text: txt(a.done_when) };
    if (a.considered_dropped) { p['Considered and dropped'] = { rich_text: txt(a.considered_dropped) }; }
    if (a.timestamp) { p['Timestamp'] = { rich_text: txt(a.timestamp) }; }
    out.push({ json: { kind: 'Action', meeting_id: m.meeting_id, meeting: m.title, start: m.start, owner: owner, allocation: alloc, action: String(a.action), why: String(a.why || ''), done_when: String(a.done_when || ''), due: String(a.due || ''), body: { parent: { database_id: DB }, properties: p } } });
  });
  const list = function (label, arr) { const xs = (arr || []).filter(Boolean); return xs.length ? label + ':\n- ' + xs.join('\n- ') : ''; };
  const why = [ai.personal ? 'Personal meeting: no actions recorded.' : '', list('Decisions', ai.decisions), list('Open questions', ai.open_questions), list('Parked', ai.parked), list('Flagged for Brad', [].concat(ai.flags_for_brad || [], flags))].filter(Boolean).join('\n\n');
  const s = common('Summary: ' + m.title, 'Meeting summary');
  s['Why'] = { rich_text: txt(why || 'No decisions or open questions recorded.') };
  out.push({ json: { kind: 'Meeting summary', meeting_id: m.meeting_id, meeting: m.title, start: m.start, actions: actions.length, flags: flags.length + (ai.flags_for_brad || []).filter(Boolean).length, body: { parent: { database_id: DB }, properties: s } } });
});
return out;
