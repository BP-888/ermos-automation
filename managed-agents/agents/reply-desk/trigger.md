# What starts Reply Desk

Reply Desk has no schedule. It runs once per reply, started by a **new** n8n workflow, `revenue-reply-desk-start`, which calls the Claude Managed Agents session API. Nothing here changes an existing n8n workflow.

```
Smartlead reply ──webhook──▶ n8n revenue-reply-desk-start
                               1. check token + event type
                               2. strip quoted thread, exact-match positive set
                               3. POST /v1/sessions  (starts Reply Desk)
                               4. wait, poll until the run is idle
                               5. read the result JSON
                               6. 🔴 #hq-approvals post + DM to Brad
                               7. hq-log-run (one Run Log row)
```

## Why this shape

- **Webhook straight from Smartlead into the agent is not possible.** Anthropic's webhooks only report on its own sessions; nothing in the API accepts a Smartlead payload. Something has to turn the reply into a session request, and n8n already receives Smartlead webhooks.
- **A scheduled deployment does not fit.** A deployment run cannot carry the reply, so the agent would have to go looking for new replies. One session per reply is simpler and faster.
- **The agent has no n8n tool.** The reply text is written by a stranger. If the agent could run n8n workflows, a reply could try to talk it into running one that sends email (`revenue-weekly-report` and `MTG 1 · Distribute Approved Actions` both do, and both are open to MCP). So the agent only reads and saves drafts, and n8n does the notify and the log after the run, from the agent's JSON result.
- **Note for the Morning Brief:** `hq-log-run` can only be started by another workflow ("When called by a workflow" trigger); n8n says it cannot be run through MCP. The Morning Brief's step 7 depends on running it through MCP, so check that run's Run Log rows.

## Smartlead side

Add a **second** webhook in Smartlead pointing at the new workflow's URL, for reply events, on every live campaign (or globally). The existing `smartlead-reply-router` webhook stays as it is.

If Smartlead only allows one webhook URL, the other way is one extra node at the end of `smartlead-reply-router` that forwards the original body to this workflow. That is a change to an existing workflow, so it needs Brad's say-so first.

## Nodes

1. **Webhook** `POST`, path `smartlead-reply-desk-<random>`, respond immediately with 200. Same guard as the router: only run if `query.token` equals a new secret (`REPLY_DESK_WEBHOOK_TOKEN`, not the router's), `body.event_type` is `EMAIL_REPLY` or `UNTRACKED_REPLIES`, and `body.to_email` contains `@`. Treat the URL with its token like a password.

2. **Code** (JavaScript, run once for each item). Same logic as `build_session_request()` in `reply_desk.py`; keep them in step.

   ```javascript
   const POSITIVE = ['yes', 'yes please', 'send', 'send it', 'send it over', 'sure', 'please do', 'go on'];
   const p = $json.body;
   const src = p.preview_text || p.reply_body || '';
   const text = src.replace(/<br\s*\/?>/gi, '\n').replace(/<[^>]+>/g, ' ')
     .split(/(?:^|\n)\s*(?:On .{0,80}wrote:|-{2,}\s*Original Message|From:\s)/i)[0]
     .replace(/\s+/g, ' ').trim();
   const normal = text.toLowerCase().replace(/[^a-z ]/g, '').replace(/\s+/g, ' ').trim();
   const lead = (p.to_email || '').toLowerCase();
   const input = {
     lead_email: lead, lead_name: p.to_name || '',
     reply_text: text.slice(0, 4000), reply_raw: src.slice(0, 8000),
     subject: p.subject || '', campaign_name: p.campaign_name || '', campaign_id: p.campaign_id ?? null,
     sequence_number: p.sequence_number ?? null, replied_at: p.time_replied || '',
     from_mailbox: p.from_email || '', exact_positive: POSITIVE.includes(normal),
   };
   if (!text) return [];
   return [{ json: { request: {
     agent: 'REPLY_DESK_AGENT_ID',
     environment_id: 'REPLY_DESK_ENVIRONMENT_ID',
     vault_ids: ['REPLY_DESK_VAULT_ID'],
     title: `Reply from ${lead}`,
     metadata: { source: 'smartlead', lead_email: lead.slice(0, 512) },
     budget: { type: 'limit', max_list_cost: { amount: '300', currency: 'USD' } },
     initial_events: [{ type: 'user.message', content: [{ type: 'text', text: JSON.stringify(input, null, 2) }] }],
   }, input } }];
   ```

3. **HTTP Request** `POST https://api.anthropic.com/v1/sessions`, JSON body `{{ $json.request }}`, headers:
   - `x-api-key`: from an n8n Header Auth credential `anthropic_reply_desk` (Brad pastes the key; it never goes in a node or this repo)
   - `anthropic-version: 2023-06-01`
   - `anthropic-beta: managed-agents-2026-04-01`
   - `content-type: application/json`

   The response `id` (`sesn_...`) is the session. The run has already started.

4. **Wait** 2 minutes.

5. **HTTP Request** `GET https://api.anthropic.com/v1/sessions/{{id}}` (same headers). **If** `status` is `idle` or `terminated`, go on. Otherwise loop back to Wait, at most 10 times; after that, post to #hq-run-alerts ("Reply Desk run still going after 20 minutes", with the Console link) and stop.

6. **HTTP Request** `GET https://api.anthropic.com/v1/sessions/{{id}}/events?limit=100`, following `next_page` until it is `null`. **Code:** take the last `agent.message` event's text, pull out the ```` ```json ```` block and parse it. Also take the last `session.status_idle` event: if its `stop_reason.type` is not `end_turn` (for example `budget_reached`), or the JSON will not parse, treat the run as failed: post to #hq-run-alerts and log Result = Failed.

7. **Slack** (the existing `slack_api` credential), by `action` and `label`:
   - `draft_saved`, `no_thread`, or label `escalate`, `meeting`, `unclear`: post to **#hq-approvals** opening with `🔴 URGENT` (customer and revenue lane, hq-approval-gate) and DM Brad the same text. Include: lead name and email, campaign, the label, `reply_summary`, the full `draft_text`, `next_step_for_brad`, any `questions_for_brad`, and the Console link `https://platform.claude.com/workspaces/default/sessions/{{id}}`. No Approve button: Brad approves by sending the draft himself from Gmail (or pasting `draft_text` into Smartlead when `no_thread`).
   - `out_of_office`, `unsubscribe`, or `action` `none`: no Slack post. The Run Log row is enough.

8. **Execute Workflow** `hq-log-run` (`B7cs3zsJjzkLP7BO`) with:

   | Input | Value |
   |---|---|
   | `run` | `revenue-classify-reply <lead_email> <date>` |
   | `tool` | `Reply Desk agent` |
   | `requested_by` | `Smartlead webhook` |
   | `inputs` | campaign, sequence step, `exact_positive`, session id |
   | `result` | `Waiting approval` when a draft or a Brad answer is needed, `Success` when nothing is needed, `Failed` on a failed run |
   | `approval` | `Pending` when waiting on Brad, else `Not required` |
   | `approved_by` | empty |
   | `summary` | label, action, `reply_summary` |
   | `sop_version` | `sop_versions` from the result |

## Testing before Smartlead is pointed at it

From `managed-agents/agents/reply-desk/`:

```sh
python reply_desk.py check samples/reply-exact-positive.json   # what n8n will send; no API call
python reply_desk.py run samples/reply-pricing.json            # a real run against a test address
```

Use a test prospect address whose thread exists in Brad's Gmail, so the draft lands in a real thread. Then send the same sample body to the n8n test URL to check nodes 3 to 8.
