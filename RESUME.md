# Resume: Agentic Agent System (paused 20 Oct 2026, 7:15pm Sydney)

Temporary. Delete this file once we've picked up.

## Where we are
- **Reply Desk (tasks 1.7, 1.8): built and tested in n8n, not live.** Workflow `revenue-reply-desk` (78doWUk0vqhytWHO), unpublished. Pattern: routing (fixed n8n steps, one Claude call). Smartlead reply in, Claude labels and drafts from the HQ pages, fixed checks pick a lane:
  - routine interested or meeting reply: posted to #hq-approvals, sends from Smartlead after 4 business hours (7am to 7pm Sydney, weekdays) unless Brad taps Don't send;
  - any other draft: sends only on Brad's tap, expires unsent after 48 hours;
  - pricing, security, complaints, instructions in the reply, unclear: no draft, Brad answers in Smartlead;
  - out of office, unsubscribe: logged only.
  Tests run 20 Oct: 20 local logic checks; 6 real replies through real Claude with sending off (all routed correctly); simulated send, reject and log paths.
- **Meeting Actions (9.4, 5.3, 8.5): built and tested with sample data, not live.** Workflow `hq-meeting-actions` (uKIfMi5y4Ah25K9k), unpublished, weekdays 6:30am Sydney. Pattern: prompt chaining. Wispr Flow transcripts to Notion **Ermos Ops / Meeting Actions** (new database) plus Gmail drafts for Will and David that Brad sends. Its Run Log step is switched off until the first real run.
- **HQ updated 20 Oct (write over):** Hormozi Standard v2.1 (phone, booking link, silent-expiry exception), hq-approval-gate v0.3 Correspondence rule (silent expiry), Everything I Do 1.7 and 1.8, Decisions Log entry "Reply Desk and Meeting Actions rebuilt in n8n; silent expiry…".
- **Morning Brief agent:** waits until both workflows are live (Brad, 20 Oct).
- **Lead List:** stays in the n8n pod; needs n8n setup items and rulings from Brad.

## What I need from Brad
1. **The 3-Minute AI Exposure Check link.** Add it to the Hormozi Standard section 3 (or give it to Claude). Until then every "yes please" reply goes to Brad to answer himself.
2. **Share Meeting Actions with n8n:** in Notion open Ermos Ops / Meeting Actions, ••• menu, Connections, add "ERMOS n8n". A test write on 20 Oct failed with "not shared with your integration". Then rerun `TEMP meeting-actions notion write check` (SbO9fHQiNrwxAFvV), delete its test row, and archive it.
3. **Wispr Flow login in n8n:** open hq-meeting-actions, the "Find meetings" step, Credential, create "Wispr Flow" (MCP OAuth2, server https://api.wisprflow.ai/connect/mcp), Connect, sign in. Use the same credential on the other three Wispr steps. Note: Wispr Flow showed no recorded meetings on 20 Oct.
4. **Go-live go-ahead for Reply Desk:** Claude publishes the workflow and adds its webhook to the live Smartlead campaigns; first live test is a seed reply from Brad's own address.
5. **Old router:** `smartlead-reply-router` still posts to #outreach and tags ActiveCampaign. Keep or switch off once Reply Desk is live?

## Morning Brief (after the two workflows are live)
API key and `ant`: blocked 20 Oct. ANTHROPIC_API_KEY is not visible in the cloud session, and the session's safety screen blocked downloading `ant`. To unblock: add the key under the environment's settings (Network secrets or environment variables, named ANTHROPIC_API_KEY), start a new session, and allow the `ant` download. Then: confirm the key, install `ant` 1.42.0, show the dry-run plan, apply only on Brad's go, run one test brief with `python managed-agents/brief.py run`.

## Remember at go-live
Switch off the claude.ai scheduled task that runs today's morning brief, the same day the Morning Brief agent goes live.
