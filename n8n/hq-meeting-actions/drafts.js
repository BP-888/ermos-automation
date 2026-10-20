// Code node "Plan the emails" (all items). One Gmail draft per person with new Stated actions.
// ---8<---
const TEAM = { Will: { email: 'will@ermos.com.au', first: 'Will' }, David: { email: 'david@ermos.com.au', first: 'David' } };
const rows = $('Build the Notion rows').all().map(function (i) { return i.json; });
const sydney = function (iso) { const d = DateTime.fromISO(iso || '', { zone: 'utc' }); return d.isValid ? d.setZone('Australia/Sydney').toFormat('d LLL') : ''; };
const out = [];
Object.keys(TEAM).forEach(function (who) {
  const mine = rows.filter(function (r) { return r.kind === 'Action' && r.owner === who && r.allocation === 'Email drafted'; });
  if (!mine.length) { return; }
  const byMeeting = {};
  mine.forEach(function (r) { (byMeeting[r.meeting_id] = byMeeting[r.meeting_id] || []).push(r); });
  const ids = Object.keys(byMeeting);
  const first = byMeeting[ids[0]][0];
  const subject = ids.length === 1 ? 'Actions from ' + first.meeting + ', ' + sydney(first.start) : 'Your actions from ' + ids.length + ' meetings, ' + DateTime.now().setZone('Australia/Sydney').toFormat('d LLL');
  const blocks = ids.map(function (id) {
    const rs = byMeeting[id];
    const head = rs[0].meeting + ' (' + sydney(rs[0].start) + ')';
    const lines = rs.map(function (r) {
      return '- ' + r.action + '\n  Why: ' + (r.why || 'see the meeting notes') + '\n  Done when: ' + r.done_when + (r.due ? '\n  Due: ' + DateTime.fromISO(r.due).toFormat('ccc d LLL') : '');
    });
    return head + '\n' + lines.join('\n');
  });
  const message = 'Hi ' + TEAM[who].first + ',\n\nHere are your actions from our meeting' + (ids.length > 1 ? 's' : '') + '.\n\n' + blocks.join('\n\n') + '\n\nThanks,\nBrad';
  if (/\[[^\]]*\]|\{\{|TBC/.test(message)) { return; }
  out.push({ json: { owner: who, to: TEAM[who].email, subject: subject, message: message, count: mine.length } });
});
return out.length ? out : [{ json: { none: true } }];
