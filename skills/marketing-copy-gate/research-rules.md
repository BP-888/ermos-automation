# Research rules: what a search may bring back (set before searching)

Standing rules, Brad 17 Nov 2026. Every research run for ERMOS marketing reads this
file first and applies it as the search filter. Results that break a rule are not
brought back at all; they are not "found and then rejected".

## 1. Date window (decided before the search)

- Search 2026 first. Add the year to every query ("2026") and prefer results dated 2026.
- 2025 only when no 2026 primary source covers the point. Mark it "2025" in the results.
  (Brad's multi-industry brief, 17 Nov 2026, is his yes for 2025 sources in that run.)
- Nothing dated before 2025 is brought back as evidence. A 2024-or-older document may be
  named only as background, with no figures or quotes, and only if a 2025/2026 source
  cites it.
- The publication date is read on the document itself, never from a search snippet.

## 2. Source type

- Primary sources only: the regulator, court, standards board, government agency or the
  original research body (e.g. ASIC, APRA, OAIC, TPB, APESB, AHPRA, Federal Court, state
  legal regulators, AFCA, ATO, Australian Digital Health Agency, a named survey publisher).
- Not brought back: news articles, vendor blogs, law-firm or consultant summaries, SEO
  pages, LinkedIn posts, AI-generated summaries. They can point to a primary source,
  which is then read itself.
- Australian sources for Australian audiences. International material only when an
  Australian regulator cites it.

## 3. Read at source

- Every figure and quote is read on the primary page or PDF, with its exact wording,
  date, URL and the paragraph or page where it sits.
- A figure states who it applies to ("of lawyers surveyed", "of licensees reviewed").
- If the source cannot be opened, the point is not used.

## 4. What the point must be

- Informative and useful to a principal or practice manager: what the regulator expects,
  what peers are doing, what changed in 2025/2026, a practical question to take to a
  meeting.
- Non-alarmist: no fear framing, no enforcement horror stories as the lead, no "you will
  be fined". A real case may be used as context when it teaches something practical.
- No legal advice and no promise of compliance.

## 5. What ERMOS may be said to do (Claims Register, veto rank 1)

Read the live Claims Register before drafting. As at 17 Nov 2026, for ERMOS Dominion:

- Allowed (C-002, C-003, C-014, commissioning, audit log, no-training marketing fact):
  air-gapped; processes the firm's data inside its office, with no data egress from the
  appliance; only inbound health-check pings and inbound patch updates reach it;
  "Tuned for your business"; commissioned on site and maintained by ERMOS; a user audit
  log supports oversight; client data is not used to train a shared or public model.
- Never: zero risk, "zero data leakage", guaranteed compliance or privilege, "completely
  sovereign", "nothing leaves your office" (unapproved draft), "it learns how your firm
  works", productivity figures, speed claims, offline/zero-internet resilience or uptime
  promises, third-party app ingestion, tuning method or cadence, "ERMOS IQ" or "ErmosIQ"
  (retired), "appliance" in copy (use "AI unit").
- Every asset carries "Resident AI" (usually "Resident AI, secured onshore.").

## 6. What comes back from each search

For each concept: industry, concept title, hook, 5 slide texts, caption, three
first-comment options (Step 3b of SKILL.md), the ERMOS Dominion tie-in using only
section 5 wording, and a sources list:
`{"title","publisher","date":"YYYY-MM-DD","url","verified_point","where"}`.
Then run `check_sources.py` and `check_copy.py`; anything failing is fixed or dropped.
