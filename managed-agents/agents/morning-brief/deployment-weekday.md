---
name: Morning Brief - weekdays 7:15am Sydney
agent: ./agent.md
environment_id: ./environment.yaml
# Starts at 7:15 because scheduled runs can start up to 9 minutes late;
# the SOP needs the brief live by 7:35 for Brad's 7:30 handoff.
schedule:
  type: cron
  expression: "15 7 * * 1-5"
  timezone: Australia/Sydney
vault_ids: [VAULT_ID]  # replace with the vlt_... id from claude-lock.json after the vault is applied
---

Run today's morning brief for Brad, following your instructions and the hq-morning SOP.
