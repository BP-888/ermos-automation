// n8n Code node "Clean the reply" (run once for all items). Paste the body below the marker.
// ---8<---
const POSITIVE = ['yes', 'yes please', 'send', 'send it', 'send it over', 'sure', 'please do', 'go on'];
const ESCALATE = ['price', 'pricing', 'cost', 'how much', 'quote', 'fee', 'fees', 'security questionnaire', 'penetration test', 'pen test', 'soc 2', 'soc2', 'iso 27001', 'tpb', 'tax practitioners board', 'professional standards', 'cpa', 'ca anz', 'complaint', 'legal', 'lawyer', 'solicitor', 'unhappy', 'privacy act', 'oaic', 'breach', 'spam', 'how did you get', 'where did you get'];
const NEGATIVE = ['not interested', 'no thanks', 'no thank you', 'unsubscribe', 'remove me', 'take me off', 'stop emailing', 'stop contacting', 'do not contact', "don't contact", 'not a fit', 'we are fine', 'already have', 'go away'];
const INSTRUCTION = ['ignore previous', 'ignore your', 'ignore all', 'disregard', 'system prompt', 'you are an ai', 'as an ai', 'forward this', 'send this to', 'reply to this address', 'cc', 'bcc', 'new instructions', 'pretend', 'act as', 'http://', 'https://', 'www.'];
const OOO = /out of (the )?office|annual leave|on leave|maternity|paternity|automatic reply|auto-?reply|away until|back on|limited access to email/i;

const out = [];
for (const item of $input.all()) {
  const p = item.json.body ? item.json.body : item.json;
  const src = String(p.reply_body || p.preview_text || '');
  const text = src.replace(/<br\s*\/?>/gi, '\n').replace(/<\/(p|div)>/gi, '\n').replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&#39;|&apos;/g, "'").replace(/&quot;/g, '"')
    .split(/(?:^|\n)\s*(?:On .{0,120}wrote:|-{2,}\s*Original Message|From:\s|Sent from my )/i)[0]
    .replace(/\s+/g, ' ').trim();
  if (!text) { continue; }
  const lower = text.toLowerCase();
  const normal = lower.replace(/[^a-z ]/g, '').replace(/\s+/g, ' ').trim();
  const hits = function (list) { return list.filter(function (k) {
    const t = k.trim();
    const e = t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const pre = /^[a-z0-9]/.test(t) ? '(^|[^a-z0-9])' : '';
    const post = /[a-z0-9]$/.test(t) ? '($|[^a-z0-9])' : '';
    return new RegExp(pre + e + post).test(lower);
  }); };
  const lead = String(p.to_email || p.sl_lead_email || '').toLowerCase().trim();
  const flags = [];
  const esc = hits(ESCALATE); if (esc.length) { flags.push('keyword: ' + esc.join(', ')); }
  const neg = hits(NEGATIVE); if (neg.length) { flags.push('negative: ' + neg.join(', ')); }
  const ins = hits(INSTRUCTION); if (ins.length) { flags.push('instruction or link in reply: ' + ins.join(', ').trim()); }
  if (text.length > 600) { flags.push('long reply (' + text.length + ' characters)'); }
  out.push({ json: {
    lead_email: lead,
    lead_name: String(p.to_name || ''),
    first_name: String(p.to_name || '').split(' ')[0] || '',
    reply_text: text.slice(0, 4000),
    subject: String(p.subject || ''),
    campaign_id: p.campaign_id ?? null,
    campaign_name: String(p.campaign_name || ''),
    sequence_number: p.sequence_number ?? null,
    replied_at: String(p.time_replied || p.event_timestamp || ''),
    from_mailbox: String(p.from_email || ''),
    stats_id: String(p.stats_id || ''),
    message_id: String(p.message_id || ''),
    reply_html: src.slice(0, 20000),
    exact_positive: POSITIVE.indexOf(normal) !== -1,
    out_of_office: OOO.test(text),
    risk_flags: flags,
    event_type: String(p.event_type || ''),
  } });
}
return out;
