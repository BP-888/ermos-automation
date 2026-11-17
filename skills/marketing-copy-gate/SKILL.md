---
name: marketing-copy-gate
description: >-
  Check and fix ERMOS marketing copy before Brad sees it: LinkedIn captions and
  carousel slides, flyers, web copy, EDMs, ads and decks. Use whenever a draft is
  ready for review, when asked to "check this copy", "run the copy gate", "is this
  ready for Brad", or as the review step of marketing-copy, marketing-linkedin-posts
  or marketing-flyers. Reviews and revises only; never publishes, schedules or sends.
---

# marketing-copy-gate

The shared review step for every ERMOS marketing asset. Pattern: **evaluator-optimizer**
(check, revise, check again), because good copy needs a judgement pass a fixed script
can't make, and one revision loop catches what a single pass misses. A script does the
mechanical checks; Claude does the judgement checks.

## Step 0: load the rules live (every run)

Fetch these from Ermos HQ in Notion. Rules are never copied into this skill; if a page
can't be read, stop and say which one.

| Page | Notion id | Use |
|---|---|---|
| marketing-copy-gate (SOP) | `3fc77626a80981c38422f0f1d6bafb8d` | order of checks, output contract |
| Output Language Standard (No AI Slop) | `3f377626a80981e587b5e000920579f5` | three tests, 18 patterns, banned and empty words |
| Claims Register | `3dd77626a80981d6ac46ead2de3e501e` | what may be said (Marketing level for marketing copy) |
| Customer Response Test | `3fb77626a809816cae4fe68f931e7171` | the buyer's three questions |
| Positioning: Resident AI | `3fe77626a80981468fd6fb6b60e8691b` | "Resident AI" term, current promise |
| The channel SOP | e.g. marketing-linkedin-posts `41577626a8098151a83cf0c8e8c100e2` | channel limits and caption standard |

Note each page's version for the report.

## Step 1: separate the copy

Put only the customer-facing words (caption, slide text, headline, body) in a temporary
file. Internal notes, source mappings and approvals stay out.

## Step 2: mechanical checks (script)

```
python3 skills/marketing-copy-gate/scripts/check_copy.py <file> \
  --banned "<Banned list from the Output Language Standard>" \
  --empty "<Usually-empty list from the Output Language Standard>" \
  --require "Resident AI|ResidentAI" \
  --max-chars <channel limit> --target-chars <channel target> --hook-chars <hook limit> \
  --fail-phrases "<channel no-go phrases>" --warn-phrases "<channel phrases to check>"
```

For a LinkedIn caption, the current marketing-linkedin-posts SOP gives: limit 3,000,
target about 500, hook inside 140; fail on zero-risk wording such as "safely",
"never worry", "risk-free", "zero risk", "eliminate the risk", and on "comment below"
prompts; warn on references to future posts ("next post", "stay tuned"). Take these
from the SOP as it stands today, not from this example.

Every FAIL must be fixed. Every warning gets a decision.

## Step 2b: sources must be current (standing rule, Brad 17 Nov 2026)

AI moves fast. Every source the copy quotes must be from the current year (or the last
12 months). The previous year is used only when no current source exists and Brad says
yes; older sources are never quoted. Search for the newest primary source first.

```
python3 skills/marketing-copy-gate/scripts/check_sources.py sources.json [--allow-previous-year]
```

`sources.json` is the run state's source list (title, publisher, date, url). Any FAIL
blocks the draft.

## Step 3: judgement checks (Claude), in the SOP's order

1. **Output Language Standard**: portability, show and voice tests; the 18 patterns.
2. **Claims Register**: every factual promise at the right level; held claims stay out;
   Edge and Dominion facts kept distinct. The register outranks everything.
3. **Customer Response Test** in the buyer's voice.
4. Any scoring mandate only if its actual criteria were loaded. Never invent a score.

## Step 3b: first comment (LinkedIn, standing rule, Brad 17 Nov 2026)

Every LinkedIn post carries a first comment, checked like the caption (run Step 2 on it
too). It passes only if it:

- opens an angle the reader hasn't considered and ends in a genuine, specific question;
- invites peers to share what works (offer one idea then ask; "if you wrote the rule from
  scratch"; speak to one role; start from what AI did well and ask about the check);
- is informative and thought-provoking, never fear-driven, never lecturing ("suck eggs");
- adds no fact beyond the post's own sources and claims nothing about other firms
  without evidence;
- has no engagement bait ("comment below", "agree?", "thoughts?").

Offer Brad two or three options; his pick is approved with the package.

## Step 4: revise and re-check (at most two loops)

Make the minimum effective edit. Keep Brad's voice, bluntness and strong human lines.
Never add a claim, number or example the source didn't have. Re-run Step 2 and Step 3
on the revised copy. If something still fails after two loops, stop and list it as a
blocker rather than writing around it.

## Step 4b: clean every file before it is published (standing rule, Brad 17 Nov 2026)

Nothing published shows how it was made. For every PDF or image that goes out:

```
python3 skills/marketing-copy-gate/scripts/clean_file.py clean <file.pdf> --title "<the public title>"
```

This writes a copy named after the public title, with the hidden Title set to it and
Author, Creator and Producer set to ERMOS, then checks it. The check fails on version
numbers (V4, V6), draft, template, final, master, REF_/MOOD_/AVOID_ prefixes and tool
names (Chrome, Skia, Canva, Ideogram) in the file name or hidden properties. Publish
only the cleaned copy. `clean_file.py check <file>` checks a file without changing it.

## Step 4c: visual check for carousels (standing rule, Brad 17 Nov 2026)

The LinkedIn look is set by Posts 1 and 2 (marketing-linkedin-posts step 5b), not by the
website palette in the general brand guide. Before Brad sees any carousel:

```
python3 skills/marketing-copy-gate/scripts/check_visual.py <file.pdf> --sheet <compare.png>
```

It compares the draft with `benchmarks/linkedin-post-2.pdf` and FAILS on the wrong size
or slide count, fonts other than Sora/Inter, slides off the paper background (#EFEEEA),
or website electric blue; it WARNS when no photo is used (Posts 1 and 2 have photo bands
on the cover, a middle slide and the close). Every FAIL is fixed; every warning goes to
Brad as a decision. Show Brad the side-by-side sheet with the draft, every time.

## Step 4d: LinkedIn pre-delivery gate (hard stop, Brad 17 Nov 2026)

"Ready for Brad" for a LinkedIn post means `post_gate.py` reports PASS on all nine items
(marketing-linkedin-posts step 5c): research rules, topic, angle, copy gate, style,
images, side by side with Posts 1 and 2, preview formats, clean file. Each item needs
evidence; none counts as a FAIL.

```
python3 skills/marketing-copy-gate/scripts/post_gate.py run marketing/linkedin/posts/<post>
```

The post folder holds `post.json` (topic, angle, sources, approvals with date and Brad's
words, images with 123RF number, listing, label and licence), `caption.txt` and the
carousel PDF. Image research uses `rf123_search.js` (search, then `--check` for each
listing's "Stock Photo" label). The gate writes `build/checklist.md` (paste it at the top
of every draft shown to Brad), `build/side-by-side.png`, `build/linkedin-preview.png`,
`build/review.pdf` and `build/team-view.pdf`. If it is BLOCKED, tell Brad what failed and
why; do not show the draft.

The hook `post_gate_hook.py` (in `.claude/settings.json`) refuses Buffer posts and edits,
and files sent or published from a post folder, unless that post is PASS and unchanged
since. After a Buffer post is made from a PASS post, record it:
`post_gate.py record-buffer <post> <buffer id>`.

## Step 5: report (the SOP's output contract)

Return, in this order:

1. **Reviewed copy**, ready for Brad.
2. **Result**: PASS, or BLOCKED with each blocker.
3. **Checks completed**: which ran (script and judgement), with the page versions used.
4. **Claim map**: each factual line and the register entry that allows it (internal only).
5. **What changed**: a short note of edits.

A pass here is not approval. Brad's yes to the exact version, and the channel SOP's
release steps, still apply. Never publish, schedule, send or spend.
