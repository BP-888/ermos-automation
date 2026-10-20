// n8n Code node "Summarise the CRM" (run once for all items).
// ---8<---
const c = $input.first() ? $input.first().json : {};
const p = c.properties || {};
const v = function (x) { return x && typeof x === 'object' && 'value' in x ? x.value : x; };
return [{ json: {
  found: !!(c.id || c.vid || v(p.hs_object_id)),
  contact_id: String(c.id || c.vid || v(p.hs_object_id) || ''),
  lifecyclestage: String(v(p.lifecyclestage) || ''),
  deals: Number(v(p.num_associated_deals) || 0),
  meeting_booked: !!v(p.engagements_last_meeting_booked),
  company: String(v(p.company) || ''),
} }];
