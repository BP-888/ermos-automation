---
name: Meeting Actions - weekdays 6:30am Sydney
agent: ./agent.md
environment_id: ./environment.yaml
# Runs before the Morning Brief (7:15am) so the brief sees new actions and the
# allocation drafts. Scheduled runs can start up to 9 minutes late.
schedule:
  type: cron
  expression: "30 6 * * 1-5"
  timezone: Australia/Sydney
vault_ids: [VAULT_ID]  # replace with the vlt_... id from claude-lock.json after the vault is applied
---

Process the meetings that have ended since the last run, following your instructions.
