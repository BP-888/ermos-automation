# Resume: Agentic Agent System (paused 20 Oct 2026, 7:45pm Sydney)

Temporary. Delete this file once we've picked up.

## Where we are
- **Reply Desk (tasks 1.7, 1.8): LIVE since 20 Oct 2026, 7:40pm.** n8n `revenue-reply-desk` (78doWUk0vqhytWHO) is published. Smartlead sends replies to it through campaign webhooks 927340 (campaign 4122423, TEST_CopyA) and 927339 (campaign 4042388, Accounting Q4); read back and confirmed. Pattern: routing. Lanes: routine interested or meeting reply sends after 4 business hours unless Brad taps Don't send; other drafts need his tap (48 hour expiry); pricing, security, complaints and instructions get no draft; out of office and unsubscribe are logged only.
- **Still to prove:** Brad's seed reply reaches #hq-approvals. Smartlead says an account-wide webhook overrides campaign webhooks; the old `smartlead-reply-router` may be account-wide. If the seed reply does not arrive, delete webhooks 927339 and 927340 and add a forward step to the router instead (never both: a reply could send twice).
- **Meeting Actions (9.4, 5.3, 8.5): LIVE since 20 Oct 2026.** n8n `hq-meeting-actions` (uKIfMi5y4Ah25K9k), weekdays 6:30am Sydney. Notion access and Wispr Flow login confirmed by a real run (0 meetings in Wispr Flow on 20 Oct). Pattern: prompt chaining. Drafts only; Brad sends.
- **HQ updated 20 Oct (write over):** Hormozi Standard v2.1, hq-approval-gate v0.3 (silent expiry), Everything I Do 1.7 and 1.8, Decisions Log entry.
- **Lead List:** stays in the n8n pod; needs n8n setup items and rulings from Brad.

## What I need from Brad
1. **Seed test:** reply "Can we book a call?" from brad@ermos.com.au to an email from the TEST_CopyA campaign, then check #hq-approvals.
2. **The 3-Minute AI Exposure Check link** for the Hormozi Standard section 3. Until then every "yes please" reply goes to Brad to answer himself.
3. **Old router:** `smartlead-reply-router` still posts to #outreach and tags ActiveCampaign. Keep or switch off?
4. **Notion test row** "TEST row from n8n (delete me)" in Meeting Actions: delete it.

## Morning Brief (after the two workflows are live)
API key and `ant`: blocked 20 Oct. ANTHROPIC_API_KEY is not visible in the cloud session, and the session's safety screen blocked downloading `ant`. To unblock: add the key under the environment's settings (Network secrets or environment variables, named ANTHROPIC_API_KEY), start a new session, and allow the `ant` download. Then: confirm the key, install `ant` 1.42.0, show the dry-run plan, apply only on Brad's go, run one test brief with `python managed-agents/brief.py run`.

## Remember at go-live
Switch off the claude.ai scheduled task that runs today's morning brief, the same day the Morning Brief agent goes live.
