# Agentic Agent System: blueprint

Status: agreed in part, 20 Oct 2026 (see section 8).

## 1. What this changes, and what it doesn't

The framework stays locked (Decisions Log, 16 Oct 2026, R1 to R3). "Everything I Do" populates Ermos HQ: Function → Capability → Workflow → Tool. Change the SOP, never the framework.

This blueprint adds one rule: **how each piece of work gets built.**

## 2. Terms

- **Task:** one row in "Everything I Do" (e.g. 1.7 Reply to cold email responses).
- **Workflow:** the procedure for one task, with its SOP (a row in the Workflows database).
- **Engine:** a chain of tasks that turns one input into one output and hands it on (the 17 Oct engine map: 25 engines). Example: `leadgen-list-engine` = tasks 1.1 to 1.3, from "approved ICP" to "verified Smartlead file". An engine is the unit of ownership: one engine, one output, one owner.

An engine is not automatically an agent. Each engine is built from the simplest of four building blocks that does the job.

## 3. The four building blocks (Anthropic best practice: start simple)

Anthropic's guidance ("Building effective agents") separates **workflows**, where the steps are fixed in advance, from **agents**, where Claude decides the steps. Agents cost more and are harder to check, so they are only used when the work is open-ended. Before choosing an agent, all four must be true: the work is multi-step and hard to script, it is worth the extra cost, Claude is good at it, and mistakes can be caught.

| Block | Use when | Example |
|---|---|---|
| **n8n workflow** | Steps are fixed and repeatable | Campaign guard, contact guard, Stripe billing |
| **n8n workflow with a Claude step** | Fixed steps, with one judgement call per item (classify, extract, draft) | Classify a cold reply and draft the answer; pull actions out of one transcript |
| **Cowork skill** | Brad starts it and works with Claude live | Proposals, cold copy, job posts |
| **Managed Agent** | Runs on its own; reads many sources and decides what matters; can't be scripted step by step | Morning Brief |

Rule: **at most one Managed Agent per engine, and most engines need none.** Within an engine, each task uses the simplest block that works.

The named patterns from Anthropic's guidance, as they show up here:

| Pattern | Where it fits in ERMOS |
|---|---|
| Prompt chaining (fixed steps in order) | Lead list pod, onboarding, meeting notes to actions |
| Routing (classify, then send to the right path) | Cold reply handling (1.7): positive, objection, unsubscribe |
| Parallelization (independent pieces at once) | Checking many firms or many sources in one run |
| Evaluator-optimizer (draft, check, revise) | The copy gate: every draft is checked against No AI Slop and the claims register |
| Agent (Claude decides the steps) | Morning Brief only, for now |

Sources: see section 10. Where they disagree with this file, they win.

## 4. Every engine, sorted

| Engine | Tasks | Built as |
|---|---|---|
| `hq-daily-engine` | 9.1, 9.2, 9.4 | **Managed Agent: Morning Brief** (9.1). Meeting actions (9.4) is an n8n workflow with a Claude step, one run per transcript; the brief reads its output |
| `outreach-campaign-engine` | 1.4 to 1.7 | Reply handling (1.7) is an n8n workflow with a Claude step. Copy (1.4) is a Cowork skill plus the copy gate. Guards are n8n |
| `leadgen-list-engine` | 1.1 to 1.3 | n8n pod with Claude steps (as built) |
| `revenue-meeting-engine` | 1.8 to 1.10 | n8n (booking link). Call prep research (1.10) is a Claude step; promote it to an agent only if it needs multi-step research |
| `revenue-close-engine` | 1.11, 1.12 | Cowork skills |
| `onboarding-client-engine` | 2.1 to 2.8 | n8n (folders, board, Stripe) with Claude steps (kickoff brief) |
| `delivery-design-engine`, `delivery-build-engine`, `delivery-golive-engine` | 3.1 to 3.8 | Cowork skills; n8n for the go-live trigger (3.8) |
| `marketing-copy-gate` | 4.1, 4.10 | Shared skill used by everything that writes copy |
| `marketing-content-engine` | 4.2 to 4.4, 4.15 | **Managed Agent candidate:** a weekly batch of LinkedIn and update drafts from decisions, wins and news |
| `marketing-collateral-engine` | 4.5 to 4.7, 4.16 | Cowork skills; drift check is n8n with a Claude step |
| `marketing-benchmark-engine` | 4.8, 4.9 | n8n |
| `marketing-proof-engine` | 4.11 to 4.14 | Cowork skills |
| `client-cadence-engine` | 5.1 to 5.5 | **Managed Agent candidate:** per-client updates and call agendas from usage, tasks and email |
| `client-growth-engine` | 5.6 to 5.8 | Cowork skills; testimonial asks are n8n with a Claude step |
| `maintenance-health-engine` | 6.1 to 6.6 | n8n guards. Changelog watch (6.4) is a **Managed Agent candidate** (weekly web research) |
| `finance-billing-engine` | 7.1 to 7.3 | n8n and Stripe, with a Claude step for chase drafts |
| `finance-books-engine` | 7.4 to 7.8 | n8n with a Claude step (receipt extraction); close packet is a Cowork skill |
| `team-hiring-engine` | 8.1 to 8.3 | Cowork skills |
| `team-rhythm-engine` | 8.4, 8.5 | Claude step inside the meeting-actions workflow (SOP drafts, team status) |
| `hq-review-engine` | 9.3, 9.5 to 9.8 | n8n (Friday report is live); Claude steps for the Decisions Log and Proposed Changes digest |
| `hq-documents-engine` | 9.9, 9.13 | n8n |
| `hq-strategy-engine` | 9.10, 9.11, 9.14, 9.15 | Brad, with Cowork |
| `partner-recruit-engine` | 9.12 | Later; research may justify an agent |

That gives one Managed Agent now (Morning Brief) and three candidates, each built only once the simpler blocks around it are working.

## 5. How a Managed Agent is set up from the blueprint

| In HQ | In the agent |
|---|---|
| The engine's tasks | What the agent is responsible for |
| Task Target: Agent / Assisted / Human | Acts inside ERMOS systems / drafts for Brad / prepares only |
| The engine's output | The agent's "done when" check |
| Hands to | What it passes on, and to which engine |
| SOP page | The agent's instructions, read live every run |
| 11 Systems & Tool Registry | Its connections; credit-spending tools always gated |
| Run Log | One row per run |

## 6. Standing rules for everything that runs on its own

1. Drafts only for anything another person reads (Correspondence rule, 16 Oct).
2. Live data every run, never memory (Agent Memory Standard, 17 Oct).
3. Prices, claims and caps come from HQ.
4. Credit spend waits at a gate; one approval covers one run.
5. Unattended runs never pause waiting for Brad: a gate is a hand-off to the next run.
6. One Run Log row per run; failures go to #hq-run-alerts.
7. All copy passes the copy gate skill.

## 7. Trial and review

- Each new automation runs drafts-only from its first live day.
- **Review three weeks after the Morning Brief goes live.** Claude compares the drafts it prepared with what Brad actually sent or changed, and reports what is accurate enough to trust.
- At the review, Brad decides what can send on its own. Internal messages stay as drafts if the copy isn't accurate yet.

## 8. Decisions

| # | Decision | Status |
|---|---|---|
| 1 | Engine = unit of ownership; build each with the simplest block; at most one agent per engine | Proposed (section 3) |
| 2 | Copy gate is a shared skill, not an agent | Agreed, 20 Oct |
| 3 | Review in three weeks; internal messages may stay drafts if copy isn't accurate | Agreed, 20 Oct |
| 4 | Save this blueprint in Ermos HQ (Notion) | Open |

## 9. Found while drafting

- The engine map lists tasks 9.10 to 9.15, but "Everything I Do" stops at 9.9.
- The `hq-approval-gate` n8n workflow is built but switched off.

## 10. Sources (Anthropic, the source of truth)

1. Building effective agents: https://www.anthropic.com/engineering/building-effective-agents
2. Claude Code best practices: https://code.claude.com/docs/en/best-practices
3. Writing effective tools for agents: https://www.anthropic.com/engineering/writing-tools-for-agents
4. Common workflow patterns for AI agents: https://claude.com/resources/articles/common-workflow-patterns-for-ai-agents-and-when-to-use-them
