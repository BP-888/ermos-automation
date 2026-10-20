// n8n Code node "Build the log row" (run once for all items). Reached from every lane.
// ---8<---
const d = $('Check the draft').first().json;
let dec = null; try { dec = $('Resolve the decision').first().json; } catch (e) {}
let snt = null; try { snt = $('Check the send').first().json; } catch (e) {}
let result, approval, by, what;
if (snt) {
  result = snt.sent_ok ? 'Success' : 'Failed';
  approval = dec.answered ? 'Brad (Slack #hq-approvals)' : 'Silent expiry (4 business hours)';
  by = dec.answered ? 'Brad' : 'No answer (silent expiry)';
  what = snt.sent_ok ? 'sent from Smartlead: ' + dec.how : 'SEND FAILED (' + snt.send_error + '): ' + dec.how;
} else if (dec) {
  result = 'Rejected';
  approval = dec.answered ? 'Rejected' : 'Pending';
  by = dec.answered ? 'Brad' : 'No answer';
  what = 'not sent: ' + dec.how;
} else if (d.lane === 'notify') {
  result = 'Waiting approval'; approval = 'Pending'; by = ''; what = 'Brad to answer in Smartlead himself';
} else {
  result = 'Success'; approval = 'Not required'; by = 'n/a'; what = 'no reply needed';
}
return [{ json: {
  run: 'revenue-reply-desk ' + d.lead_email + ' ' + DateTime.now().setZone('Australia/Sydney').toFormat('yyyy-LL-dd HH:mm'),
  tool: 'revenue-reply-desk (n8n + Claude)',
  requested_by: 'Smartlead webhook',
  inputs: 'campaign ' + d.campaign_name + ', step ' + d.sequence_number + ', lane ' + d.lane + ', flags: ' + d.reasons_text,
  result: result,
  approval: approval,
  approved_by: by,
  summary: d.label + ' (' + d.confidence + '): ' + d.reply_summary + ' | ' + what,
  sop_version: d.sop_versions,
} }];
