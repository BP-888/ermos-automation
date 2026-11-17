#!/usr/bin/env python3
"""Source recency check for marketing copy (standing rule, Brad 17 Nov 2026).

AI moves fast, so every source a post quotes must be current:
  - published in the current year (or the last 12 months): PASS
  - published in the previous year: allowed only with --allow-previous-year
    (Brad's explicit yes, recorded in the run), otherwise FAIL
  - older: FAIL, never quoted, at most mentioned as background without figures

Input: a JSON list of {"title", "publisher", "date": "YYYY-MM-DD", "url"} (the run
state's "sources"), via a file or stdin.

  python3 check_sources.py sources.json [--today 2026-11-17] [--allow-previous-year]
Exit 0 = all pass, 1 = at least one fail.
"""
import argparse
import datetime as dt
import json
import sys


def judge(sources, today, allow_previous):
    results = []
    for s in sources:
        raw = str(s.get("date", ""))[:10]
        try:
            d = dt.date.fromisoformat(raw)
        except ValueError:
            results.append({**s, "verdict": "FAIL", "why": "no readable publication date"})
            continue
        age_days = (today - d).days
        if d.year == today.year or 0 <= age_days <= 365:
            verdict, why = "PASS", "current"
        elif d.year == today.year - 1:
            verdict = "PASS" if allow_previous else "FAIL"
            why = "previous year: needs Brad's yes" + (" (given)" if allow_previous else "")
        else:
            verdict, why = "FAIL", f"{d.year}: too old to quote"
        results.append({"title": s.get("title", ""), "date": raw, "verdict": verdict, "why": why})
    return results


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("file", help="JSON list of sources, or - for stdin")
    p.add_argument("--today", default=dt.date.today().isoformat())
    p.add_argument("--allow-previous-year", action="store_true")
    a = p.parse_args(argv)
    data = json.load(sys.stdin if a.file == "-" else open(a.file, encoding="utf-8"))
    res = judge(data, dt.date.fromisoformat(a.today), a.allow_previous_year)
    ok = all(r["verdict"] == "PASS" for r in res)
    print(json.dumps({"pass": ok, "sources": res}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
