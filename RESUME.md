# Resume: Agentic Agent System (paused 20 Oct 2026, 7:45pm Sydney)

Temporary. Delete this file once we've picked up.

## Where we are
- **Reply Desk (tasks 1.7, 1.8): LIVE since 20 Oct 2026, 7:40pm.** n8n `revenue-reply-desk` (78doWUk0vqhytWHO) is published. Smartlead sends replies to it through campaign webhooks 927340 (campaign 4122423, TEST_CopyA) and 927339 (campaign 4042388, Accounting Q4); read back and confirmed. Pattern: routing. Lanes: routine interested or meeting reply sends after 4 business hours unless Brad taps Don't send; other drafts need his tap (48 hour expiry); pricing, security, complaints and instructions get no draft; out of office and unsubscribe are logged only.
- **Proven 21 Oct 11:23am:** a real lead's out-of-office reply (campaign 4122423) reached Reply Desk through the campaign webhook (execution 174) and was logged. Campaign webhooks work; no router forward needed. The drafting lane is still unproven on a real reply.
- **Ermos Operating Map** (visual, for Brad): https://claude.ai/artifact/JW9jxTrEA6wdQoSJZxxF9h. Lanes by function, live status from the n8n connector, "Waiting on you" (db collection `asks`) and an Ideas inbox (db collection `intake`). At each session start, read `intake` and place new ideas; mark `asks` done as Brad answers. When a workflow is added or renamed, update the WF list in the page source.
- **Meeting Actions (9.4, 5.3, 8.5): LIVE since 20 Oct 2026.** n8n `hq-meeting-actions` (uKIfMi5y4Ah25K9k), weekdays 6:30am Sydney. Notion access and Wispr Flow login confirmed by a real run (0 meetings in Wispr Flow on 20 Oct). Pattern: prompt chaining. Drafts only; Brad sends.
- **HQ updated 20 Oct (write over):** Hormozi Standard v2.1, hq-approval-gate v0.3 (silent expiry), Everything I Do 1.7 and 1.8, Decisions Log entry.
- **Lead List:** stays in the n8n pod; needs n8n setup items and rulings from Brad.

- **Repo tidy (21 Oct):** `main` created from this branch plus the scraper wave runner (`claude/brave-darwin-ohugkg`). Tests pass on `main`. GitHub refused `archive/*` tags from the session, and the session may not delete branches, so Brad does those in GitHub. Brad still to: (1) set `main` as the default branch, (2) rename the repo to `ermos-automation`, (3) delete branches `claude/brave-darwin-ohugkg`, `claude/beautiful-cori-2ncjud`, `claude/zen-hawking-isjmkj` (all fully inside `main`). Branches `claude/agent-reply-desk`, `claude/agent-meeting-actions` and `claude/agent-lead-list` hold superseded agent designs (replaced by the n8n builds; the HQ architecture page holds the decision). They are the only copy, so delete them only on Brad's word.

## What I need from Brad
1. **Seed test (drafting lane):** Smartlead had not sent step 1 to brad@ermos.com.au by 11:11am 21 Oct; re-check scheduled 1:30pm. When it arrives, Brad replies "Can we book a call?" and checks #hq-approvals.
2. **The 3-Minute AI Exposure Check link** for the Hormozi Standard section 3. Until then every "yes please" reply goes to Brad to answer himself.
3. **Old router:** `smartlead-reply-router` still posts to #outreach and tags ActiveCampaign. Keep or switch off?
4. **Notion test row** "TEST row from n8n (delete me)" in Meeting Actions: delete it.

## Morning Brief (after the two workflows are live)
API key and `ant`: blocked 20 Oct. ANTHROPIC_API_KEY is not visible in the cloud session, and the session's safety screen blocked downloading `ant`. To unblock: add the key under the environment's settings (Network secrets or environment variables, named ANTHROPIC_API_KEY), start a new session, and allow the `ant` download. Then: confirm the key, install `ant` 1.42.0, show the dry-run plan, apply only on Brad's go, run one test brief with `python managed-agents/brief.py run`.

## Remember at go-live
Switch off the claude.ai scheduled task that runs today's morning brief, the same day the Morning Brief agent goes live.
