#!/usr/bin/env python3
"""Mechanical checks for ERMOS marketing copy (marketing-copy-gate, step 2).

Only the checks a script can do reliably. Judgement checks (portability, show,
voice, claims, buyer response) stay with Claude in the skill.

Word lists are NOT kept here: the skill reads them live from the Output
Language Standard and the channel SOP each run and passes them in, so the
rules live in one place (Ermos HQ).

Usage:
  python3 check_copy.py draft.txt --banned "delve,leverage" --empty "just,simply" \
      --require "Resident AI|ResidentAI" --max-chars 3000 --target-chars 500 \
      --hook-chars 140 --fail-phrases "safely,never worry" --warn-phrases "next post"

Exit code 0 = no FAIL, 1 = at least one FAIL, 2 = bad input.
Prints JSON: {"pass": bool, "fails": [...], "warnings": [...], "stats": {...}}.
"""
import argparse
import json
import re
import sys


def split_list(value):
    return [x.strip() for x in (value or "").split(",") if x.strip()]


def find_terms(text, terms):
    """Whole-word, case-insensitive matches; returns [(term, snippet)]."""
    hits = []
    for term in terms:
        pattern = r"(?<![\w-])" + re.escape(term) + r"(?![\w-])"
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            start = max(0, m.start() - 30)
            snippet = text[start:m.end() + 30].replace("\n", " ")
            hits.append((term, snippet.strip()))
    return hits


def first_line(text):
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def check(text, banned, empty, require, max_chars, target_chars, hook_chars,
          fail_phrases, warn_phrases):
    fails, warnings = [], []
    body = text.strip()
    n = len(body)

    # Output Language Standard pattern 18: no em or en dashes in client copy.
    for ch, name in (("—", "em dash"), ("–", "en dash")):
        if ch in body:
            fails.append({"check": "dashes", "detail": f"{body.count(ch)} {name}(es) found; rewrite without them"})

    for term, snip in find_terms(body, banned):
        fails.append({"check": "banned word", "detail": f'"{term}" in: ...{snip}...'})

    for term, snip in find_terms(body, empty):
        warnings.append({"check": "empty word", "detail": f'"{term}" usually carries no meaning: ...{snip}...'})

    for phrase, snip in find_terms(body, fail_phrases):
        fails.append({"check": "channel rule", "detail": f'"{phrase}" is not allowed: ...{snip}...'})

    for phrase, snip in find_terms(body, warn_phrases):
        warnings.append({"check": "channel rule", "detail": f'"{phrase}" needs a second look: ...{snip}...'})

    if require:
        options = [r for r in require.split("|") if r]
        if not any(re.search(re.escape(o), body, flags=re.IGNORECASE) for o in options):
            fails.append({"check": "required term", "detail": f'none of {options} appears'})

    if max_chars and n > max_chars:
        fails.append({"check": "length", "detail": f"{n} characters; the limit is {max_chars}"})
    if target_chars and n > target_chars * 1.3:
        warnings.append({"check": "length", "detail": f"{n} characters; the target is about {target_chars}"})

    if hook_chars:
        hook = first_line(body)
        if len(hook) > hook_chars:
            warnings.append({"check": "hook", "detail": f"first line is {len(hook)} characters; the hook should land inside {hook_chars}"})

    # Pattern 1 (binary contrast), flagged for Claude's judgement, never failed.
    for m in re.finditer(r"\b(?:it's|it is|this is)\s+not\s+[^.?!\n]{1,60}[,;]\s*(?:it's|it is)\b|\bnot\s+just\b", body, flags=re.IGNORECASE):
        warnings.append({"check": "binary contrast", "detail": f"possible 'not X, it's Y': ...{m.group(0)}..."})

    # Pattern 17: emoji in a heading-like line.
    for line in body.splitlines():
        if line.lstrip().startswith("#") and re.search(r"[\U0001F300-\U0001FAFF]", line):
            fails.append({"check": "formatting", "detail": f"emoji in heading: {line.strip()[:60]}"})

    return {"pass": not fails, "fails": fails, "warnings": warnings,
            "stats": {"characters": n, "first_line_characters": len(first_line(body))}}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("file", help="text or markdown file holding only the customer-facing copy, or - for stdin")
    p.add_argument("--banned", default="", help="comma list from the Output Language Standard 'Banned'")
    p.add_argument("--empty", default="", help="comma list from the Output Language Standard 'Usually empty'")
    p.add_argument("--require", default="", help="'|'-separated alternatives, at least one must appear")
    p.add_argument("--max-chars", type=int, default=0)
    p.add_argument("--target-chars", type=int, default=0)
    p.add_argument("--hook-chars", type=int, default=0)
    p.add_argument("--fail-phrases", default="", help="comma list of channel phrases that fail")
    p.add_argument("--warn-phrases", default="", help="comma list of channel phrases to flag")
    a = p.parse_args(argv)
    try:
        text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    except OSError as e:
        print(json.dumps({"error": str(e)}))
        return 2
    if not text.strip():
        print(json.dumps({"error": "the copy is empty"}))
        return 2
    result = check(text, split_list(a.banned), split_list(a.empty), a.require, a.max_chars,
                   a.target_chars, a.hook_chars, split_list(a.fail_phrases), split_list(a.warn_phrases))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
