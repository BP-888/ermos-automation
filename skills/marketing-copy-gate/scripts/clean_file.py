#!/usr/bin/env python3
"""Check and clean a file before it is published (marketing-copy-gate, step 6).

Standing rule (Brad, 17 Nov 2026): nothing published shows how it was made.
The file name and the PDF's hidden properties carry no version numbers, draft
or template words, reference prefixes or tool names.

  python3 clean_file.py check  <file.pdf>
  python3 clean_file.py clean  <file.pdf> --title "Public title" [--out DIR]

check exits 1 when anything leaks. clean writes a copy named after the title,
with Title = the public title, Author/Creator/Producer = ERMOS, nothing else,
then checks the copy.
"""
import argparse
import json
import os
import re
import sys

from pypdf import PdfReader, PdfWriter

LEAK = re.compile(r"(?i)(?<![a-z0-9])(?:(?:v\d+(?:\.\d+)?|version|draft|template|wip|final|"
                  r"master|copy of|untitled|headlesschrome|chrome|skia|canva|ideogram)(?![a-z])|(?:ref|mood|avoid)_)")


def leaks(text):
    return sorted({m.group(0) for m in LEAK.finditer(text or "")})


def check(path):
    problems = []
    name = os.path.basename(path)
    for hit in leaks(os.path.splitext(name)[0]):
        problems.append(f'file name contains "{hit}"')
    info = PdfReader(path).metadata or {}
    for key in ("/Title", "/Subject", "/Keywords", "/Author", "/Creator", "/Producer"):
        val = str(info.get(key, "") or "")
        for hit in leaks(val):
            problems.append(f'{key[1:]} property contains "{hit}" ({val[:80]})')
    if not str(info.get("/Title", "") or "").strip():
        problems.append("Title property is empty")
    return problems


def safe_name(title):
    name = re.sub(r"[:/\\?*\"<>|]", " -", title)
    return re.sub(r"\s+", " ", name).strip(" -.") + ".pdf"


def clean(path, title, out_dir):
    if leaks(title):
        raise SystemExit(f"the public title itself contains {leaks(title)}")
    r = PdfReader(path)
    w = PdfWriter()
    for page in r.pages:
        w.add_page(page)
    w.add_metadata({"/Title": title, "/Author": "ERMOS", "/Creator": "ERMOS", "/Producer": "ERMOS"})
    out = os.path.join(out_dir or os.path.dirname(os.path.abspath(path)), safe_name(title))
    with open(out, "wb") as f:
        w.write(f)
    return out, len(r.pages)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["check", "clean"])
    p.add_argument("file")
    p.add_argument("--title")
    p.add_argument("--out")
    a = p.parse_args(argv)
    if a.action == "clean":
        if not a.title:
            p.error("clean needs --title")
        out, pages = clean(a.file, a.title, a.out)
        problems = check(out)
        print(json.dumps({"file": out, "pages": pages, "pass": not problems, "problems": problems}, indent=2))
    else:
        problems = check(a.file)
        print(json.dumps({"file": a.file, "pass": not problems, "problems": problems}, indent=2))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
