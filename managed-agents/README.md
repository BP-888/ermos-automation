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

## Reply Desk (`agents/reply-desk/`)

Tasks 1.7 and 1.8 (`revenue-classify-reply`, `revenue-book-meeting`) as a hosted agent. It runs once per cold email reply. A new n8n workflow, `revenue-reply-desk-start`, receives the Smartlead reply webhook, exact-matches the positive set, and starts a session through the session API (`POST /v1/sessions`). The agent then:

- reads the reply thread in Gmail, the contact in HubSpot, and the reply rules in Ermos HQ,
- labels the reply (interested, meeting, objection, referral, escalate, unsubscribe, out of office, unclear),
- saves one Gmail draft in the prospect's thread for Brad to send: the Exposure Check link for "send it", the HubSpot meeting link when they ask for a call,
- ends with a JSON result. n8n reads it, posts 🔴 to #hq-approvals, DMs Brad, and writes the Run Log row.

It never sends anything another person sees. Its only write is a Gmail draft. It has no n8n, Slack, Calendar or HubSpot write tool, because the reply text comes from outside ERMOS and must not be able to steer a tool that reaches anyone.

| File | What it is |
|---|---|
| `agent.md` | Model, tools (allowlist per service), MCP servers, and the instructions (system prompt) |
| `environment.yaml` | The sandbox: locked to the MCP servers only |
| `vault.yaml` | The credential store (container only, no secrets in this repo) |
| `trigger.md` | What starts it: the n8n workflow to build, node by node |
| `reply_desk.py` | `check` shows the session request for a saved reply; `run` starts a test run; `result` reads a run's JSON; `latest` lists recent runs |
| `samples/` | Two fake Smartlead reply bodies for testing |

### What still has to be filled in

| Placeholder | File | Value |
|---|---|---|
| `HUBSPOT_MEETING_LINK` | `agent.md` | The HubSpot meeting link for the 20-minute discovery call |
| `REPLY_DESK_AGENT_ID`, `REPLY_DESK_ENVIRONMENT_ID`, `REPLY_DESK_VAULT_ID` | n8n Code node, env vars for `reply_desk.py` | The `agent_`, `env_` and `vlt_` ids from `claude-lock.json` after apply |
| `REPLY_DESK_WEBHOOK_TOKEN` | n8n Webhook node, Smartlead webhook URL | A new random secret (not the router's) |
| `anthropic_reply_desk` | n8n credential | Header Auth, `x-api-key` = an Anthropic API key for the workspace the agent lives in |

### Credentials

Three MCP servers, stored in the vault and never in this repo. Same servers and kinds as the Morning Brief, so the same OAuth apps can be reused; the vault is separate.

| Server | URL | Credential |
|---|---|---|
| Gmail | `https://gmailmcp.googleapis.com/mcp/v1` | Google OAuth (scopes `gmail.readonly`, `gmail.compose`), for the Gmail account the replies land in |
| HubSpot | `https://mcp.hubspot.com` | HubSpot OAuth (read scopes for contacts, deals, meetings, owners) |
| Notion | `https://mcp.notion.com/mcp` | Notion MCP OAuth |

Outside the vault: the Anthropic API key in n8n (`anthropic_reply_desk`), and the existing `slack_api` credential in n8n for the 🔴 post and DM.

### Setup order

```sh
cd managed-agents
ant apply --dry-run -v agents/reply-desk/vault.yaml agents/reply-desk/agent.md agents/reply-desk/environment.yaml
ant apply agents/reply-desk/vault.yaml agents/reply-desk/agent.md agents/reply-desk/environment.yaml
# add the three credentials to the vault, then:
export REPLY_DESK_AGENT_ID=$(jq -r '.resources["./agents/reply-desk/agent.md"].id' claude-lock.json)
export REPLY_DESK_ENVIRONMENT_ID=$(jq -r '.resources["./agents/reply-desk/environment.yaml"].id' claude-lock.json)
export REPLY_DESK_VAULT_ID=$(jq -r '.resources["./agents/reply-desk/vault.yaml"].id' claude-lock.json)
python agents/reply-desk/reply_desk.py run agents/reply-desk/samples/reply-pricing.json   # test run
# build revenue-reply-desk-start in n8n (trigger.md), test it, then add its URL as a Smartlead webhook
```

Commit `claude-lock.json` after each apply.

### Changing it later

- **Letting Reply Desk send without Brad:** first change the Correspondence rule in hq-approval-gate. Then it still needs a sending tool; do not give the agent n8n access to do it, because the reply text could steer it.
- **Changing the positive set:** edit `POSITIVE_SET` in `reply_desk.py` and the `POSITIVE` list in the n8n Code node together.
- **Pausing it:** deactivate `revenue-reply-desk-start` in n8n. Replies still reach `smartlead-reply-router` as now.
- **Cost cap:** each run is capped at US$3.00 (`budget` in the session request). A run that hits it stops and n8n reports it in #hq-run-alerts.
