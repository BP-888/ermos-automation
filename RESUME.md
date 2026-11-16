# Resume notes

Temporary. Delete each section once it is picked up; delete the file when none remain.

# Collateral for Flyers (paused 16 Nov 2026; resume 17 Nov, 9:30am Sydney)

Session: "Collateral for Flyers". Presentations get their own later session, "Collateral for Presentations". Video is last and parked.

## Agreed with Brad (16 Nov)
- Look and feel: the Outbound Collateral Style Guide v2.1 is correct for all outbound collateral.
- Images: Brad generates in Ideogram or licenses stock from 123RF; Claude turns them into the finished piece. No generator makes the finished branded asset.
- Copy: every piece goes through the shared marketing-copy skill, No AI Slop and the Hormozi Standard. Quality bar: high impact, punchy, interesting.
- Facts and audience for outbound collateral: the selected ICP page first (proposed: the Claims Register still blocks unsupported product claims).
- Order: LinkedIn (being built now) -> Facebook and Instagram organic posts -> video. No paid ads.
- marketing-copy becomes the one copy step every channel calls; its rules live only there.

## Done
- HQ Proposed Change: "B2B sounding board for marketing-copy review" (Hormozi lead; Dunford, Ehrenberg-Bass/B2B Institute, Wiebe, Walker): https://app.notion.com/p/41a77626a809819eb2adccc6daa690e2. Waiting on Brad.
- B2B best-practice research for Australian AI/IT (in chat, 16 Nov): win before the first call, lead with trust and assurance, show you understand the specific problem, build memory for the 95%, sell practical outcomes, arm the champion, no AI washing.

## HQ edits listed for Brad (not made; Brad said he would make them)
1. marketing-copy s1: add "high impact, punchy and interesting"; read the ICP page first for outbound collateral.
2. Outbound Collateral Style Guide s7: name Ideogram and 123RF; copy the stock licence rule from marketing-linkedin-posts.
3. Decisions Log: LinkedIn -> Facebook/Instagram organic -> video.
4. Business Brain (HAU) 05 Tools: paid Meta ads line conflicts; correct or mark Superseded.
5. marketing-flyers: step 2 names the ICP page; step 6 adds 123RF; s9 item 4 (style guide still Draft) is stale.

## Flyer process today (marketing-flyers V4)
11 steps, two gates: concept -> ground brief -> brief -> copy and review (marketing-copy) -> Gate 1 copy -> image (Ideogram by hand) -> build from master HTML -> export check -> review -> Gate 2 -> file and register.

## Tomorrow: what Claude needs from Brad to draw the flyer process flow
1. Approve, change or reject the B2B sounding board Proposed Change.
2. The five HQ edits above: has Brad made them, or should Claude?
3. Format and home for the flow: a visual diagram on the marketing-flyers page (recommended) or a Miro board.
4. Who generates Ideogram images and buys 123RF licences (Brad assumed), and where licence records go.
5. One real flyer to walk through end to end (candidates: Barristers V3 finish, or the first Aged Care brief).
6. Access to ~/ERMOS Files on Brad's Mac (connect the folder, or upload the master source, Dominion render and images).

## Still open (no action until LinkedIn ships)
- No Facebook Page; Metricool has no social account connected (checked 16 Nov).
- marketing-copy-gate not built; marketing-copy skill not validated.
- Wispr Flow has no meetings recorded since August (voice-of-customer source).

# Agentic Agent System (paused 20 Oct 2026, 7:45pm Sydney)

## Where we are
- **Reply Desk (tasks 1.7, 1.8): LIVE since 20 Oct 2026, 7:40pm.** n8n `revenue-reply-desk` (78doWUk0vqhytWHO) is published. Smartlead sends replies to it through campaign webhooks 927340 (campaign 4122423, TEST_CopyA) and 927339 (campaign 4042388, Accounting Q4); read back and confirmed. Pattern: routing. Lanes: routine interested or meeting reply sends after 4 business hours unless Brad taps Don't send; other drafts need his tap (48 hour expiry); pricing, security, complaints and instructions get no draft; out of office and unsubscribe are logged only.
- **Proven 21 Oct 11:23am:** a real lead's out-of-office reply (campaign 4122423) reached Reply Desk through the campaign webhook (execution 174) and was logged. Campaign webhooks work; no router forward needed. The drafting lane is still unproven on a real reply.
- **Ermos Operating Map** (visual, for Brad): https://claude.ai/artifact/JW9jxTrEA6wdQoSJZxxF9h. Lanes by function, live status from the n8n connector, "Waiting on you" (db collection `asks`) and an Ideas inbox (db collection `intake`). At each session start, read `intake` and place new ideas; mark `asks` done as Brad answers. When a workflow is added or renamed, update the WF list in the page source.
- **Meeting Actions (9.4, 5.3, 8.5): LIVE since 20 Oct 2026.** n8n `hq-meeting-actions` (uKIfMi5y4Ah25K9k), weekdays 6:30am Sydney. Notion access and Wispr Flow login confirmed by a real run (0 meetings in Wispr Flow on 20 Oct). Pattern: prompt chaining. Drafts only; Brad sends.
- **HQ updated 20 Oct (write over):** Hormozi Standard v2.1, hq-approval-gate v0.3 (silent expiry), Everything I Do 1.7 and 1.8, Decisions Log entry.
- **Lead List:** stays in the n8n pod; needs n8n setup items and rulings from Brad.

- **Repo tidy (21 Oct):** `main` created from this branch plus the scraper wave runner (`claude/brave-darwin-ohugkg`). Tests pass on `main`. GitHub refused `archive/*` tags from the session, and the session may not delete branches, so Brad does those in GitHub. Brad still to: (1) set `main` as the default branch, (2) rename the repo to `ermos-automation`, (3) delete branches `claude/brave-darwin-ohugkg`, `claude/beautiful-cori-2ncjud`, `claude/zen-hawking-isjmkj` (all fully inside `main`). Branches `claude/agent-reply-desk`, `claude/agent-meeting-actions` and `claude/agent-lead-list` hold superseded agent designs (replaced by the n8n builds; the HQ architecture page holds the decision). They are the only copy, so delete them only on Brad's word.

## What I need from Brad
1. **Seed test (drafting lane):** stuck. Brad's seed lead (4793094320) is at the back of TEST_CopyA's queue: 2,973 of 3,394 leads not started, about 40 new leads a day (checked 22 Oct noon). Proposed fix waiting on Brad: a one-lead test campaign (Brad only, same mailbox, Reply Desk webhook attached) and take the seed lead out of TEST_CopyA. Reply Desk has handled 5 real out-of-office replies correctly (log only).
2. **The 3-Minute AI Exposure Check link** for the Hormozi Standard section 3. Until then every "yes please" reply goes to Brad to answer himself.
3. **Old router:** `smartlead-reply-router` still posts to #outreach and tags ActiveCampaign. Keep or switch off?
4. **Notion test row** "TEST row from n8n (delete me)" in Meeting Actions: delete it.

## Morning Brief (after the two workflows are live)
API key and `ant`: blocked 20 Oct. ANTHROPIC_API_KEY is not visible in the cloud session, and the session's safety screen blocked downloading `ant`. To unblock: add the key under the environment's settings (Network secrets or environment variables, named ANTHROPIC_API_KEY), start a new session, and allow the `ant` download. Then: confirm the key, install `ant` 1.42.0, show the dry-run plan, apply only on Brad's go, run one test brief with `python managed-agents/brief.py run`.

## Remember at go-live
Switch off the claude.ai scheduled task that runs today's morning brief, the same day the Morning Brief agent goes live.
