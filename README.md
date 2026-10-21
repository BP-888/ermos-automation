# Ermos automation

Code and config for everything that runs on its own at Ermos. The rules live in Ermos HQ (Notion); this repo holds only what builds and runs them. How anything is built: HQ / 01 Standards / AI Operating System Architecture.

See what's running, and what's waiting on Brad: [Ermos Operating Map](https://claude.ai/artifact/JW9jxTrEA6wdQoSJZxxF9h).

## Where each piece runs

| Folder | Runs in | Use when (HQ architecture, section 3) |
|---|---|---|
| `n8n/` | n8n ([ermos.app.n8n.cloud](https://ermos.app.n8n.cloud)) | Fixed steps, with at most one Claude judgement per item. Each subfolder holds one workflow's Code steps, Claude prompt and tests. See `n8n/README.md`. |
| `managed-agents/` | Claude Managed Agents | Open-ended work that can't be scripted. Today only the Morning Brief. See `managed-agents/README.md`. |
| `skills/` + `.claude-plugin/` | Claude Code / Cowork (plugin `b2b-outbound-engine`) | Brad starts it and works live with Claude. |

## Working in this repo

- `main` is always the current, working version. Every Claude Code session starts from it.
- Each session works on its own branch, merges into `main` when the work is tested, and the branch is then deleted.
- `RESUME.md`, when present, is the note for picking up paused work. Delete it once picked up.
- Write over, don't add: when something changes, change the file that holds it. Don't keep a second copy, here or in Notion.

## Conventions

- Secrets come from the environment or the tool's own credential store (n8n, the Claude Console vault), never from a file in this repo.
- Scripts are Python standard library plus `requests`, or plain Node for n8n Code steps.
- Australian English throughout.
- Anything that spends credits has a run cap and pilots before a batch.

## Skill naming

Every skill name carries its department prefix: `hq-` (coordination and reporting), `leadgen-` (finding raw leads), `enrichment-` (filling out and verifying lead records), `outreach-` (contacting leads).

`skills/leadgen-google-scraper` scrapes Google Maps listings into a raw CSV via the Apify actor `compass/crawler-google-places`; `scripts/run_wave.sh` runs a capped wave over a locations file. Operating values come from the Notion SOP, which must be `Approved`; the files under `config/` are fallbacks kept in step with it.
