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
| `deployment-weekday.md` | The 7:15am weekday schedule |
| `brief.py` (in `managed-agents/`) | `run` starts a test run now and streams it; `latest` lists recent runs |

## Credentials

All six are connected in the Console vault `vlt_011CgCxQhrLNh6Y4G437tf79` ("Brad - Morning Brief"), each with Add credential > MCP OAuth > Connect, signed in as Brad (20 Oct 2026). No separate Google, Slack or HubSpot app was needed. Logins live only in the vault, never in this repo, and renew themselves.

| Server | URL |
|---|---|
| Gmail | `https://gmailmcp.googleapis.com/mcp/v1` |
| Google Calendar | `https://calendarmcp.googleapis.com/mcp/v1` |
| Slack | `https://mcp.slack.com/mcp` |
| HubSpot | `https://mcp.hubspot.com` |
| Wispr Flow | `https://api.wisprflow.ai/connect/mcp` |
| Notion | `https://mcp.notion.com/mcp` |

The agent has no n8n connection: it only POSTs to the hq-morning-notify webhook, which needs no credential.

## Setup order

```sh
cd managed-agents
ant apply --dry-run -v agents/morning-brief/agent.md agents/morning-brief/environment.yaml agents/morning-brief/deployment-weekday.md
ant apply agents/morning-brief/agent.md agents/morning-brief/environment.yaml agents/morning-brief/deployment-weekday.md
export MORNING_BRIEF_DEPLOYMENT_ID=$(jq -r '.resources["./agents/morning-brief/deployment-weekday.md"].id' claude-lock.json)
python brief.py run   # test run before the first 7:15am firing
```

Commit `claude-lock.json` after each apply. It holds the ids, and without it the next apply creates duplicates.

## Changing it later

- **Letting internal messages send without approval:** first change the Correspondence rule in hq-approval-gate, then enable the matching tool in `agent.md` and run `ant apply` again.
- **Pausing it:** `ant beta:deployments pause` on the deployment id. Missed mornings are not backfilled.
