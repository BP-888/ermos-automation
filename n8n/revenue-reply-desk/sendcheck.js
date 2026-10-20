// n8n Code node "Check the send" (run once for all items). Input: Smartlead HTTP full response.
// ---8<---
const d = $('Resolve the decision').first().json;
const r = $input.first().json;
const code = Number(r.statusCode || 0);
const b = r.body || {};
const ok = code >= 200 && code < 300 && b.success !== false;
const err = ok ? '' : String((b && (b.message || b.error)) || ('HTTP ' + code)).slice(0, 300);
return [{ json: Object.assign({}, d, { sent_ok: ok, send_error: err }) }];
