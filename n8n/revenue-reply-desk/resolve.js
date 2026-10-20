// n8n Code node "Resolve the decision" (run once for all items). Input: either Slack wait node.
// ---8<---
const d = $('Check the draft').first().json;
const r = $input.first().json;
const ans = (r.data || r).approved;
let send, how;
if (d.lane === 'auto') {
  send = ans !== false;
  how = ans === true ? 'Brad tapped Send now' : (ans === false ? "Brad tapped Don't send" : 'no answer by ' + d.send_at_text + ', sent on silent expiry');
} else {
  send = ans === true;
  how = ans === true ? 'Brad tapped Approve and send' : (ans === false ? 'Brad tapped Reject' : 'no answer in 48 hours, not sent');
}
return [{ json: Object.assign({}, d, { send: send, how: how, answered: typeof ans === 'boolean' }) }];
