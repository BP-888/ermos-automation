# Managed Agents

Claude Managed Agents definitions for ERMOS. Anthropic hosts and runs them; these files are the source of truth, synced with `ant apply`.

## Morning Brief (`agents/morning-brief/`)

The hq-morning SOP as a hosted agent. Weekdays at 7:15am Sydney it reads Gmail, Google Calendar, Slack, HubSpot, Wispr Flow and Notion, then:

- writes the brief as a Notion page,
- saves reply drafts in Gmail,
- DMs Brad the link (n8n `hq-morning-notify`),
- writes one Run Log row (n8n `hq-log-run`).

It never sends anything another person sees. Send, invite, post and edit tools are switched off in `agent.md`; every enabled tool reads, or writes only to Brad's own space.

| File | What it is |
|---|---|
| `agent.md` | Model, tools (allowlist per service), MCP servers, and the instructions (system prompt) |
| `environment.yaml` | The sandbox: locked to the MCP servers only |
| `vault.yaml` | The credential store (container only, no secrets in this repo) |
| `deployment-weekday.md` | The 7:15am weekday schedule |
| `../../brief.py` | `run` starts a test run now and streams it; `latest` lists recent runs |

## What still has to be filled in

| Placeholder | File | Value |
|---|---|---|
| `N8N_DOMAIN` | `agent.md` | Your n8n host, from n8n Settings > Instance-level MCP > Server URL |
| `MORNING_BRIEFS_PAGE_URL` | `agent.md` | The Notion page that briefs are created under |
| `VAULT_ID` | `deployment-weekday.md` | The `vlt_...` id, after the vault is applied |

## Credentials

One per MCP server, stored in the vault and never in this repo. Each is tied to its server URL.

| Server | URL | Credential |
|---|---|---|
| Gmail | `https://gmailmcp.googleapis.com/mcp/v1` | Google OAuth (scopes `gmail.readonly`, `gmail.compose`). Needs a Google Cloud project with the Gmail MCP service enabled and an OAuth client |
| Google Calendar | `https://calendarmcp.googleapis.com/mcp/v1` | Google OAuth (read-only calendar scopes), same Google Cloud project and client |
| Slack | `https://mcp.slack.com/mcp` | Slack OAuth user token from a Slack app with search and history read scopes |
| HubSpot | `https://mcp.hubspot.com` | HubSpot OAuth from a HubSpot app (client id and secret) |
| Wispr Flow | `https://api.wisprflow.ai/connect/mcp` | Wispr Flow OAuth (read-only server) |
| Notion | `https://mcp.notion.com/mcp` | Notion MCP OAuth (not an `ntn_` integration token) |
| n8n | `https://N8N_DOMAIN/mcp-server/http` | n8n instance MCP access token (`static_bearer`) |

OAuth credentials carry a refresh token so Anthropic renews them automatically.

## Setup order

```sh
cd managed-agents
ant apply --dry-run -v agents/morning-brief/vault.yaml agents/morning-brief/agent.md agents/morning-brief/environment.yaml
ant apply agents/morning-brief/vault.yaml agents/morning-brief/agent.md agents/morning-brief/environment.yaml
# add the seven credentials to the vault, put its vlt_ id in deployment-weekday.md, then:
ant apply agents/morning-brief/deployment-weekday.md
export MORNING_BRIEF_DEPLOYMENT_ID=$(jq -r '.resources["./agents/morning-brief/deployment-weekday.md"].id' claude-lock.json)
python brief.py run   # test run before the first 7:15am firing
```

Commit `claude-lock.json` after each apply. It holds the ids, and without it the next apply creates duplicates.

## Changing it later

- **Letting internal messages send without approval:** first change the Correspondence rule in hq-approval-gate, then enable the matching tool in `agent.md` and run `ant apply` again.
- **Pausing it:** `ant beta:deployments pause` on the deployment id. Missed mornings are not backfilled.

## Meeting Actions (`agents/meeting-actions/`)

Build first #4: the "Turn meeting notes into action items" workflow (Everything I Do 9.4, 5.3 and 8.5) as a hosted agent. Weekdays at 6:30am Sydney, before the Morning Brief, it reads the Wispr Flow meetings that have ended since the last run, then:

- writes each action item as a row in the Notion Meeting Actions database, with owner, why, done-when and the transcript timestamp,
- saves one Gmail draft per team member (Will, David) listing their new actions, for Brad to read and send,
- writes one Run Log row (n8n `hq-log-run`).

It never sends anything another person sees. Brad's own actions get no email: they sit in Notion and the Morning Brief picks them up. Actions with an unclear owner, and actions for clients or partners, are recorded as "Needs Brad" and are never drafted. Its Notion access can only add rows; it cannot edit or delete one.

| File | What it is |
|---|---|
| `agent.md` | Model, tools (allowlist per service), MCP servers, the team roster and the instructions |
| `environment.yaml` | The sandbox: locked to the MCP servers only |
| `vault.yaml` | Its own credential store, so its Gmail access can be narrower than the Morning Brief's |
| `deployment-weekday.md` | The 6:30am weekday schedule |
| `run.py` | `run` starts a test run now and streams it; `latest` lists recent runs |

### What starts a run

A schedule, not the end of each meeting. Wispr Flow has no way to start an Anthropic agent when a recording finishes, so a per-meeting trigger would need an n8n workflow polling Wispr Flow and calling the deployment's run endpoint. The 6:30am run covers every meeting from the last 4 days that is finished and transcribed, and skips any meeting already in the database, so a missed or repeated run does no harm. If same-day emails matter, add a second deployment at 5pm with the same files.

### Where the tasks live (proposed, not created)

A new Notion database, **Ermos HQ / Meeting Actions**, one row per action plus one summary row per meeting (decisions, open questions, parked items). Columns are listed in `agent.md` under "Meeting Actions columns". Suggested views: **Needs Brad** (Allocation = Needs Brad), **By owner** (Kind = Action, Status = Open, grouped by Owner), **Brad today** (Owner = Brad, Status = Open) for the Morning Brief.

### What still has to be filled in

| Placeholder | File | Value |
|---|---|---|
| `N8N_DOMAIN` | `agent.md` | Same n8n host as the Morning Brief |
| `MEETING_ACTIONS_DATA_SOURCE` | `agent.md` (2 places) | The `collection://...` id of the Meeting Actions database, once Brad creates it |
| `WILL_EMAIL`, `DAVID_EMAIL` | `agent.md` | Will's and David's work email addresses |
| `VAULT_ID` | `deployment-weekday.md` | The `vlt_...` id of the Meeting Actions vault, after it is applied |

### Credentials

Four, in the Meeting Actions vault. Same servers as the Morning Brief, so the same apps and clients can be reused.

| Server | Credential |
|---|---|
| Wispr Flow | Wispr Flow OAuth (read-only server) |
| Notion | Notion MCP OAuth |
| Gmail | Google OAuth with `gmail.compose` only (drafts; no reading of mail) |
| n8n | n8n instance MCP access token (`static_bearer`) |

### Setup order

```sh
cd managed-agents
ant apply --dry-run -v agents/meeting-actions/vault.yaml agents/meeting-actions/agent.md agents/meeting-actions/environment.yaml
ant apply agents/meeting-actions/vault.yaml agents/meeting-actions/agent.md agents/meeting-actions/environment.yaml
# add the four credentials to the vault, put its vlt_ id in deployment-weekday.md, then:
ant apply agents/meeting-actions/deployment-weekday.md
export MEETING_ACTIONS_DEPLOYMENT_ID=$(jq -r '.resources["./agents/meeting-actions/deployment-weekday.md"].id' claude-lock.json)
python agents/meeting-actions/run.py run   # test run once a meeting has been recorded
```

### Changing it later

- **Drafting to clients or partners:** add them to the People table in `agent.md` and change step 5. Their drafts would also need the claims register check from hq-approval-gate.
- **Writing back to rows (for example marking them sent):** needs `notion-update-page`, which can edit any page the Notion login can reach. Add it only with a written rule limiting it to the Meeting Actions database.
