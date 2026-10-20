# Lead List Agent: decision

**Decision (20 Oct 2026): do not build a Managed Agent for the Lead List Agent yet.** Lenny stays what he is today: the n8n Outbound Extraction Pod (`leadgen-extraction-pod`, workflow `7drQVtu9CFmdZFd1`), with Claude inside it at the judgement points. Revisit when the conditions at the end of this page are met.

Nothing was created, applied or run for this agent. There is no `agent.md`, `environment.yaml`, `vault.yaml` or deployment file, on purpose.

## What was read

| Source | Version read |
|---|---|
| leadgen-extraction-pod SOP | Approved, 19 Oct 2026 V4 (change log to V4.2) |
| leadgen-list-engine (engine map page for tasks 1.1 to 1.3) | Draft 19 Oct 2026 V1 |
| hq-approval-gate | Draft v0.2 (gates, live approvals, Correspondence rule) |
| Agent Build Standard | Draft 19 Oct 2026 V1 |
| Everything I Do rows 1.1, 1.2, 1.3 | 1.1 Building, 1.2 and 1.3 Mapping |
| RESUME: Lead List Agent + agent oversight | written 19 Oct 2026 for 20 Oct |
| Workflow record: Outbound Extraction Pod (fixed n8n chain) | edited 19 Oct 2026 |
| n8n `leadgen-extraction-pod` | 45 nodes, inactive, updated 19 Oct 2026 (read only, not changed) |
| `skills/leadgen-google-scraper` in this repo | current |

## What the n8n Pod already does

Steps 1 to 8, end to end, as a fixed chain:

1. Checks input, then the kill switch (Paused box on the Workflow record).
2. Loads the Pod SOP, the Google Scraper SOP and the segment's ICP from Notion; stops if the ICP is not Approved.
3. **Claude node:** ICP to search parameters (judgement spec `leadgen-icp-to-params`), checked against a schema.
4. **Gate 0, pilot brief:** posts to #hq-approvals and waits (up to 24 hours) before any Apify spend. A live approval only counts with Brad's quoted words and a key.
5. Google Maps scrape (Apify, capped), normalise, exclusions, dedupe by domain against both Smartlead Extraction Registers.
6. Firecrawl reads the homepage and team page.
7. **Claude node:** website check (judgement spec `leadgen-website-check`): headcount, tier, fit, named contacts, evidence line.
8. Writes a per-run Google Sheet, builds the Gate 1 summary (counts, drop reasons, spend in AUD), posts **Gate 1** and waits (up to 48 hours). Logs through hq-log-run; failures alert #hq-run-alerts.

The gates are already hand-offs held by n8n (Slack send-and-wait), not by an AI agent, so nothing would sit paused inside a Managed Agent session.

## What a Managed Agent could add, and why each does not hold up now

| Possible job for a Managed Agent | Why not now |
|---|---|
| **Website fit check** (step 7) | Already a Claude node reading its spec from the SOP on every run, with schema checks, a cached prompt and the Batch API. Moving it to a hosted agent duplicates it, costs more per firm and breaks the Audit 20 result (95% right person) that was measured on the n8n version. |
| **ICP to parameters** (step 1) | Same: already a Claude node with a fixed output schema. |
| **Gate summaries** | Brad has not ruled yet between Claude (the SOP's `leadgen-gate-summary` spec) and the deterministic template n8n uses now. Either way it is one bounded step inside the chain, not an agent. |
| **Gate decisions** (keep, check, drop at Gate 1) | These are Brad's by the SOP and hq-approval-gate. An agent must not make them. The only thing it could do is pre-sort the "check" pile, which the website check already does with `fit = check`. |
| **Register dedupe questions** | Domain dedupe is code in n8n. Brand-level dedupe (merged firms, e.g. Steiner Legal into Thornton + King) is an open finding and the RESUME page already puts the fix in the website check. That is a spec change, not a new agent. |
| **Orchestrating runs across segments and locations** | There is one live segment (Law, pilot) and Accounting waits on the law pilot. Every run already needs Brad's Gate 0 approval of its brief, so an agent choosing the next suburb saves him almost nothing today. Batch caps are set by Brad per wave. |
| **Wiring steps 9 to 12** (email ladder, Gates 2 and 3, Smartlead files, register append) | This is the actual next piece of work, and it is fixed plumbing: the ruled build pattern is a fixed n8n chain with Claude at three judgement points only. |

The standards point the same way:

- **Agent Build Standard rule 1:** use the simplest pattern that works. An autonomous agent is the last rung and needs a reason. The Pod is a prompt chain with two Claude steps, which is what Brad ruled on 19 Oct 2026.
- **Agent Build Standard rule 2:** one engine, one job, one output. The engine's job and output are already owned by the Pod.
- **Build pattern ruling (Pod SOP, 19 Oct 2026):** fixed n8n chain; every step other than the three judgement points is a plain node.

And the Pod is not ready to be orchestrated by anything yet:

- It still stops at the kill switch until the n8n Notion integration can see the Workflow record.
- Steps 9 to 12 are not wired; firms were passed to the email ladder by hand on 19 Oct.
- The n8n deployment gate eval has not run.
- The hq-agent-auditor scored it "Scalable: Fail for now" (Firecrawl rate limit, Spam Act question, sending capacity).

An agent placed over an unfinished, unproven chain adds a second thing that can go wrong and makes failures harder to trace.

## Risks a Managed Agent would add today

- **Spend without a person.** The only way an agent could start work is the Pod's webhook, which takes the run's caps as inputs. An agent that can call it can spend Apify, Firecrawl and Claude credits once Gate 0 is approved. Today Brad starts every run himself, which is the safer state while the Pod is unproven.
- **Approval bypass risk.** The Pod accepts `approval_mode = live` plus a key to skip the Slack gate. A hosted agent must never be able to send that. Not giving it the tool is simpler than guarding it.
- **Two "Lennys".** The engine page, the RESUME pages and the Everything I Do dashboard already name the n8n Pod as Lenny. A second, hosted Lead List Agent would split ownership of the same job.

## When to revisit, and what it would be

Revisit when **all** of these are true:

1. Pod steps 1 to 12 are wired and have passed the n8n deployment gate eval for at least one segment.
2. The Spam Act question has a legal view and a test campaign has sent, so cost per reply is known.
3. There are enough segment and location runs queued (for example Law and Accounting, several suburbs a week) that choosing the next batch is real work for Brad.

At that point the useful agent is a **run planner**, not a replacement for any Pod step:

- **Starts from:** a weekly scheduled deployment.
- **Reads:** the Run Log, both Smartlead Extraction Registers, the holding tabs, the segment configs and caps in the Pod SOP, and open items in #hq-approvals.
- **Does:** picks the next locations per segment within the SOP caps, and starts the Pod through its webhook, so the Pod's own Gate 0 posts the brief to #hq-approvals and n8n waits for Brad. The agent then stops. It never waits on an approval itself; the next weekly run reads what happened.
- **Never:** sends `approval_mode = live`, raises a cap, runs Apify, Apollo, LeadMagic, Clay or Firecrawl directly, touches Smartlead or HubSpot, or sends anything a person reads except through the gate.
- **Writes:** one Run Log row through hq-log-run.

The same folder layout as `agents/morning-brief/` would be used (`agent.md` with tool allowlists, a locked-down `environment.yaml`, `vault.yaml`, a deployment file). That design should be checked against the SOP as it stands then, not this page.

## Conflicts and unclear points found in the blueprint and SOPs

1. **The Workflow record for the Pod is out of date.** It says it implements V3, lists Apollo and Clay as connections, gives a "Weekly schedule (Mon 7am Sydney)" trigger and "Apollo Target List pushed to Smartlead" as the output, and promises three Smartlead files (main, catch-all, generic). The SOP V4.2 has no Apollo and no Clay, a manual webhook trigger, and two files (main, generic).
2. **Gate summaries:** the SOP says Claude writes them; the n8n build uses a fixed template. Still waiting on Brad's ruling (engine page, open items).
3. **Gate 0 is not in the SOP.** n8n adds a pilot-brief approval before any spend. Good practice, but the SOP's step list starts gating at Gate 1.
4. **Approval timeout:** hq-approval-gate says no response in 24 hours means Rejected. The Pod's Gate 1 waits 48 hours.
5. **hq-approval-gate is still Draft v0.2 with Build status "To build"**, yet the Pod and the Morning Brief depend on it.
6. **Register check for Maps-sourced firms:** SOP step 5 says they run the segment's register lookup. n8n marks every Law firm `unverified` ("Law Society lookup not built yet"), and the RESUME page says not to scrape the Law Society register without written authorisation.
7. **Apify call style:** the `leadgen-google-scraper` skill says never use the synchronous run-and-get-items endpoint because it times out. The n8n Pod uses exactly that endpoint (`run-sync-get-dataset-items`, 300-second timeout).
8. **Workflow names differ between places.** Everything I Do 1.2 names `enrichment-contact-enrich | enrichment-assign-tier`; the RESUME page names `leadgen-email-ladder` (`kV78QXi5FQEaiROd`) for the same step.
9. **SOP version label:** the Version property says V4; the change log is at V4.2.
10. **AUD conversion rule:** the Pod SOP has an "Always" rule for spend in AUD via frankfurter.app, but a Proposed Change page ("QUESTION: Lead-gen pod applies an unapproved USD-to-AUD conversion rule") says it was never approved.
11. **Security, worth fixing soon:** the Pod's webhook needs no credentials, and the live-approval key is written in plain text inside an n8n Code node ("Validate input"). Anyone who can see that node, or the key, can mark a run as approved live by Brad. Move the key into an n8n credential and add header auth to the webhook. (The key is not repeated in this repo.)
