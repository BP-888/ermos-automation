# Resume: Agentic Agent System (paused 20 Oct 2026, 2:30pm Sydney)

Temporary. Delete this file once we've picked up.

## Where we are
- **Agreed and recorded in Notion:** AI Operating System Architecture v1 (01 Standards), Master Brief RULE 4 "Write over, don't add", and a Decisions Log entry for 20 Oct.
- **Cleanup done:** hq-morning SOP v2, the hq-morning Workflows record, the Donna pages (marked Superseded), the approval-gate note, and the duplicate line in the Master Brief.
- **Morning Brief agent:** files written and pushed to branch `claude/loving-gates-6qflg4` (`managed-agents/agents/morning-brief/`). Not live: nothing has been created on Anthropic's side yet.
- **Three side windows,** all paused and waiting on you:
  - Reply Desk: rebuild as an n8n workflow with one Claude step.
  - Meeting Actions: rebuild as an n8n workflow with one Claude step.
  - Lead List: stays in the n8n pod; it needs n8n setup items and a few rulings from you.

## What I need from you
1. ~~The Notion page for briefs~~: done 20 Oct, Ermos Ops / Morning Briefs.
2. ~~Logins~~: all six connected in vault vlt_011CgCxQhrLNh6Y4G437tf79, 20 Oct.
3. ~~API key~~: saved as the ANTHROPIC_API_KEY environment variable, 20 Oct. **Next session starts here:** confirm the key is visible (without printing it), ask Brad before installing `ant`, show the dry-run plan, apply only on his go, then run one test brief with `python managed-agents/brief.py run`.
4. **Go or no-go** on rebuilding Reply Desk and Meeting Actions as n8n workflows.
5. **Two rulings from Reply Desk:**
   - Cold-email replies land in the Smartlead mailboxes, not your Gmail. Where should reply drafts go?
   - Task 1.8 says to send the booking link straight away, but your Hormozi Standard says to ask permission first. Which wins?

## Remember at go-live
Switch off the claude.ai scheduled task that runs today's morning brief, the same day the Morning Brief agent goes live.
