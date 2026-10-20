# n8n workflows built from this repo

n8n holds the live workflows; this folder holds the source of each Code step and Claude prompt, with tests. When a step changes, change it here, run the tests, then paste it into n8n.

| Folder | n8n workflow | What it does |
|---|---|---|
| `revenue-reply-desk/` | revenue-reply-desk (78doWUk0vqhytWHO) | Tasks 1.7 and 1.8. One Smartlead reply in; Claude labels and drafts from the HQ pages; fixed checks pick a lane (silent expiry, Brad's tap, Brad answers, log only). |
| `hq-meeting-actions/` | hq-meeting-actions (uKIfMi5y4Ah25K9k) | Task 9.4. Wispr Flow transcripts to Notion Meeting Actions rows and Gmail drafts for Will and David. |

Each `.js` file is one Code node: the part below `// ---8<---` is what goes into n8n. `claude-system-prompt.txt` is the Claude step's system message.

Run the tests (needs Node and `npm i luxon@3.5.0` in the folder):

```sh
cd n8n/revenue-reply-desk && node test.js
cd n8n/hq-meeting-actions && node test.js
```

The Reply Desk webhook address carries a secret token. It lives only in the n8n workflow, never here.
