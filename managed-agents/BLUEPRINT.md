# Agentic Agent System: blueprint (proposal for Brad)

Status: proposal, 20 Oct 2026. Nothing here is live until Brad agrees it.

## 1. What this changes, and what it doesn't

The framework stays locked (Decisions Log, 16 Oct 2026, R1 to R3). "Everything I Do" populates Ermos HQ: Function → Capability → Workflow → Tool. Change the SOP, never the framework.

This blueprint adds one layer only: **each SOP engine is run by one agent.** The 25 engines from the 17 Oct engine rule already group the tasks, say what each one produces, and say what it hands on to. An agent is the thing that runs an engine.

## 2. How the blueprint becomes an agent

| In "Everything I Do" / HQ | In the agent |
|---|---|
| Engine (e.g. `hq-daily-engine`) | One agent, same name |
| The engine's tasks (e.g. 9.1, 9.2, 9.4) | What the agent is responsible for |
| Task Target = Agent | The agent does it, but only reads or writes to ERMOS's own systems |
| Task Target = Assisted | The agent drafts; Brad approves or sends |
| Task Target = Human | The agent only prepares (brief, agenda, numbers); Brad does it |
| Engine output (e.g. "Brad's day cleared") | The agent's "done when" check |
| Hands to (e.g. `hq-review-engine`) | What starts the next engine's agent |
| Starts from (e.g. "An approved ICP") | What starts this agent: a schedule, an event, or Brad |
| Components (n8n chains, SOPs) | Tools the agent calls. Fixed chains stay in n8n; the agent handles the judgement around them |
| SOP page | The agent's instructions. The agent reads the SOP live every run, so changing the SOP changes the agent |
| 11 Systems & Tool Registry | The agent's connections. "Spends credits" tools always sit behind a gate |
| Run Log | One row per agent run |
| hq-approval-gate | Every message another person reads goes through Brad, no exceptions while early stage |

## 3. Standing rules for every agent

1. Drafts only for anything another person reads (Correspondence rule, 16 Oct).
2. Live data every run, never memory. If a source disagrees with memory, the source wins (Agent Memory Standard, 17 Oct).
3. Prices, claims and caps come from HQ, never from the agent.
4. Anything that spends credits waits at a gate. An approval covers one run only.
5. Unattended runs never pause mid-run waiting for Brad. A gate is a hand-off: the agent stops, reports, and the next run picks up after Brad approves.
6. One Run Log row per run. Failures go to #hq-run-alerts.
7. `marketing-copy-gate` (4.1, 4.10) is shared. It becomes a skill every agent uses, not an agent of its own.

## 4. Build order (from the Build first rank)

| Order | Engine | Build first ranks inside it | State |
|---|---|---|---|
| 1 | `hq-daily-engine` (9.1, 9.2, 9.4) | 9.1 = rank 1, 9.4 = rank 4 | Morning Brief drafted (`agents/morning-brief`). Meeting actions (9.4) joins this engine |
| 2 | `outreach-campaign-engine` (1.4 to 1.7) | 1.7 = rank 2 | Not started |
| 3 | `leadgen-list-engine` (1.1 to 1.3) | 1.1 = rank 3 | n8n pod being built; agent to wrap its judgement steps |
| 4 | `hq-review-engine` (9.3, 9.5 to 9.8) | 9.3 = rank 5 | Friday report live in n8n |
| 5 | `marketing-copy-gate` | 4.1 = rank 6 | Built as a shared skill |
| 6+ | The other engines, in section order | none ranked | Ranked when Brad sets Build first |

Ranks 4 (5.3 and 8.5, also on "Turn meeting notes into action items") also touch `client-cadence-engine` and `team-rhythm-engine`; the meeting-notes workflow is built once inside `hq-daily-engine` and those engines read its output.

## 5. Life of an agent

1. **Draft:** the agent's files written from its engine row and SOPs.
2. **Agreed:** Brad approves the draft.
3. **Test run:** one run by hand, before any schedule.
4. **Trial:** about three weeks, drafts only, Brad checks every output.
5. **Live:** Brad lifts specific limits by changing the SOP (e.g. internal messages send without approval).
6. **Monthly review:** with the monthly rebuild of "Everything I Do" (R2).

## 6. Record keeping

- Each task row's **Agent name** = its engine's agent name, so the dashboard shows which agent owns which task.
- Each agent gets a row in 11 Systems & Tool Registry (Type: Agent).
- The agent's files live in this repo under `managed-agents/agents/<engine-name>/`.

## 7. Found while drafting

- The engine map lists tasks 9.10 to 9.15, but "Everything I Do" stops at 9.9. Those rows need adding, or the engines `hq-strategy-engine`, `hq-documents-engine` and `partner-recruit-engine` have nothing to run.
- The `hq-approval-gate` n8n workflow is built but switched off. Agents work around it today by leaving drafts for Brad to send himself.

## 8. Decisions for Brad

1. One agent per engine: agreed?
2. Copy gate as a shared skill rather than its own agent: agreed?
3. Trial length (three weeks proposed), and what has to be true to lift drafts-only.
4. File this in 06 Proposed Changes so it goes through the usual weekly review?
