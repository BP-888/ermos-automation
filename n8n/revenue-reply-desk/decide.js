// n8n Code node "Check the draft and pick a lane" (run once for all items). Paste the body below the marker.
// Reads: $('Clean the reply'), $('Read the CRM'), $('Load HQ rules'), and the Claude node output on $input.
// ---8<---
const LABELS = ['interested', 'meeting', 'objection', 'referral', 'escalate', 'unsubscribe', 'out_of_office', 'unclear'];
const AUTO_LABELS = ['interested', 'meeting'];
const NO_DRAFT = ['escalate', 'unsubscribe', 'out_of_office', 'unclear'];
const WINDOW_HOURS = 4;
const DAY_START = 7;
const DAY_END = 19;
const ZONE = 'Australia/Sydney';

const r = $('Clean the reply').first().json;
const crm = $('Summarise the CRM').first().json;
const hq = $('Load HQ rules').first().json;
const raw = $input.first().json;
const parts = Array.isArray(raw.content) ? raw.content.filter(function (c) { return c && c.type === 'text'; }).map(function (c) { return c.text; }) : [];
const text = String(parts.length ? parts.join('\n') : (raw.text ?? raw.output ?? raw.message?.content ?? ''));

let ai = null;
const problems = [];
try {
  const m = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  ai = JSON.parse((m ? m[1] : text).trim());
} catch (e) {
  problems.push('Claude did not return readable JSON');
  ai = { label: 'unclear', confidence: 'low', draft_text: '', reply_summary: '', reasoning: text.slice(0, 500) };
}
let label = LABELS.indexOf(ai.label) !== -1 ? ai.label : 'unclear';
if (r.exact_positive && label !== 'escalate') { label = 'interested'; ai.confidence = 'high'; }
const confidence = ['high', 'medium', 'low'].indexOf(ai.confidence) !== -1 ? ai.confidence : 'low';
let draft = NO_DRAFT.indexOf(label) !== -1 ? '' : String(ai.draft_text || '').replace(/\r/g, '').trim();

const allowed = (String(hq.rules_text || '').match(/https?:\/\/[^\s)\]>"'`,]+/g) || []).map(function (u) { return u.replace(/[.;:]+$/, ''); });
if (draft) {
  const urls = draft.match(/https?:\/\/[^\s)\]>"'`,]+/g) || [];
  urls.map(function (u) { return u.replace(/[.;:]+$/, ''); }).forEach(function (u) {
    if (allowed.indexOf(u) === -1) { problems.push('link not found in HQ: ' + u); }
  });
  const noUrls = draft.replace(/https?:\/\/\S+/g, '');
  if (/[\[\]{}<>]|\bTBC\b|\bXXX\b|lorem/i.test(noUrls)) { problems.push('blank or placeholder in the draft'); }
  if (noUrls.indexOf('!') !== -1) { problems.push('exclamation mark'); }
  const bodyOnly = noUrls.split(/\n\s*Regards\b/)[0];
  if (/\w-\w/.test(bodyOnly)) { problems.push('hyphen in the email body'); }
  if (/[–—]|\s-\s/.test(noUrls)) { problems.push('em or en dash'); }
  if ((noUrls.match(/\?/g) || []).length !== 1) { problems.push('needs exactly one question, has ' + (noUrls.match(/\?/g) || []).length); }
  if (noUrls.indexOf('Brad Pickett') === -1) { problems.push('sign-off missing'); }
  if (draft.length > 1500) { problems.push('draft too long'); }
} else if (NO_DRAFT.indexOf(label) === -1) {
  problems.push('no draft written');
}

const crmFlags = [];
if (crm.found && Number(crm.deals || 0) > 0) { crmFlags.push('has a HubSpot deal'); }
if (crm.found && /customer|opportunity|evangelist/i.test(String(crm.lifecyclestage || ''))) { crmFlags.push('HubSpot stage: ' + crm.lifecyclestage); }
if (crm.found && crm.meeting_booked) { crmFlags.push('meeting already booked'); }

const reasons = [].concat(r.risk_flags || [], crmFlags, problems);
if (AUTO_LABELS.indexOf(label) === -1 && draft) { reasons.push('label ' + label + ' always needs Brad'); }
if (confidence !== 'high' && draft) { reasons.push('Claude confidence ' + confidence); }

let lane;
if (label === 'out_of_office' || label === 'unsubscribe') { lane = 'log_only'; }
else if (!draft) { lane = 'notify'; }
else if (reasons.length === 0) { lane = 'auto'; }
else { lane = 'manual'; }
if ((lane === 'auto' || lane === 'manual') && (!r.stats_id || !r.campaign_id)) {
  reasons.push('Smartlead did not send a thread id, so it cannot be sent from here');
  lane = 'notify';
}

const now = DateTime.now().setZone(ZONE);
let t = now;
let left = WINDOW_HOURS * 60;
while (left > 0) {
  const open = t.set({ hour: DAY_START, minute: 0, second: 0, millisecond: 0 });
  const close = t.set({ hour: DAY_END, minute: 0, second: 0, millisecond: 0 });
  if (t.weekday > 5 || t >= close) { t = t.plus({ days: 1 }).set({ hour: DAY_START, minute: 0, second: 0, millisecond: 0 }); continue; }
  if (t < open) { t = open; }
  const room = close.diff(t, 'minutes').minutes;
  const step = Math.min(room, left);
  t = t.plus({ minutes: step });
  left -= step;
}
const sendAt = t;

const esc = function (s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); };
const html = draft ? draft.split(/\n{2,}/).map(function (para) { return '<p>' + esc(para).replace(/\n/g, '<br>') + '</p>'; }).join('') : '';

return [{ json: {
  lane: lane,
  label: label,
  confidence: confidence,
  reasons: reasons,
  reasons_text: reasons.length ? reasons.join('; ') : 'none',
  draft_text: draft,
  draft_html: html,
  reply_summary: String(ai.reply_summary || ''),
  reasoning: String(ai.reasoning || ''),
  next_step_for_brad: String(ai.next_step_for_brad || ''),
  send_at_iso: sendAt.toISO(),
  send_at_text: sendAt.toFormat("h:mm a ccc d LLL"),
  lead_email: r.lead_email,
  lead_name: r.lead_name,
  campaign_id: r.campaign_id,
  campaign_name: r.campaign_name,
  sequence_number: r.sequence_number,
  stats_id: r.stats_id,
  message_id: r.message_id,
  replied_at: r.replied_at,
  reply_text: r.reply_text,
  reply_html: r.reply_html,
  sop_versions: String(hq.versions || ''),
} }];
