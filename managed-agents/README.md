# Managed Agents

Claude Managed Agents definitions for ERMOS. Anthropic hosts and runs them; these files are the source of truth, synced with `ant apply`.

## Morning Brief (`agents/morning-brief/`)

The hq-morning SOP as a hosted agent. Weekdays at 7:15am Sydney it reads Gmail, Google Calendar, Slack, HubSpot, Wispr Flow and Notion, then:

- writes the brief as a Notion page,
- saves reply drafts in Gmail,
- DMs Brad the link (POST to the n8n `hq-morning-notify` webhook),
- writes one Run Log row straight into Notion.

It never sends anything another person sees. Send, invite, post and edit tools are switched off in `agent.md`; every enabled tool reads, or writes only to Brad's own space.

| File | What it is |
|---|---|
| `agent.md` | Model, tools (allowlist per service), MCP servers, and the instructions (system prompt) |
| `environment.yaml` | The sandbox: locked to the MCP servers and the n8n webhook host only |
| `vault.yaml` | The credential store (container only, no secrets in this repo) |
| `deployment-weekday.md` | The 7:15am weekday schedule |
| `brief.py` (in `managed-agents/`) | `run` starts a test run now and streams it; `latest` lists recent runs |

## What still has to be filled in

| Placeholder | File | Value |
|---|---|---|
| `MORNING_BRIEFS_PAGE_URL` | `agent.md` | The Notion page that briefs are created under |
| `VAULT_ID` | `deployment-weekday.md` | The `vlt_...` id, after the vault is applied |

## Credentials

One per MCP server, six in all, stored in the vault and never in this repo. Each is tied to its server URL. The agent has no n8n connection: it only POSTs to the hq-morning-notify webhook, which needs no credential.

| Server | URL | Credential |
|---|---|---|
| Gmail | `https://gmailmcp.googleapis.com/mcp/v1` | Google OAuth (scopes `gmail.readonly`, `gmail.compose`). Needs a Google Cloud project with the Gmail MCP service enabled and an OAuth client |
| Google Calendar | `https://calendarmcp.googleapis.com/mcp/v1` | Google OAuth (read-only calendar scopes), same Google Cloud project and client |
| Slack | `https://mcp.slack.com/mcp` | Slack OAuth user token from a Slack app with search and history read scopes |
| HubSpot | `https://mcp.hubspot.com` | HubSpot OAuth from a HubSpot app (client id and secret) |
| Wispr Flow | `https://api.wisprflow.ai/connect/mcp` | Wispr Flow OAuth (read-only server) |
| Notion | `https://mcp.notion.com/mcp` | Notion MCP OAuth (not an `ntn_` integration token) |

OAuth credentials carry a refresh token so Anthropic renews them automatically.

## Setup order

```sh
cd managed-agents
ant apply --dry-run -v agents/morning-brief/vault.yaml agents/morning-brief/agent.md agents/morning-brief/environment.yaml
ant apply agents/morning-brief/vault.yaml agents/morning-brief/agent.md agents/morning-brief/environment.yaml
# add the six credentials to the vault, put its vlt_ id in deployment-weekday.md, then:
ant apply agents/morning-brief/deployment-weekday.md
export MORNING_BRIEF_DEPLOYMENT_ID=$(jq -r '.resources["./agents/morning-brief/deployment-weekday.md"].id' claude-lock.json)
python brief.py run   # test run before the first 7:15am firing
```

Commit `claude-lock.json` after each apply. It holds the ids, and without it the next apply creates duplicates.

## Changing it later

- **Letting internal messages send without approval:** first change the Correspondence rule in hq-approval-gate, then enable the matching tool in `agent.md` and run `ant apply` again.
- **Pausing it:** `ant beta:deployments pause` on the deployment id. Missed mornings are not backfilled.
