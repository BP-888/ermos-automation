#!/usr/bin/env python3
"""Pre-delivery gate for every ERMOS LinkedIn post (Brad, 17 Nov 2026).

Nothing reaches Brad, and nothing goes into Buffer, until every item on this checklist
passes with evidence. An item with no evidence is a FAIL. The checklist follows the
marketing-linkedin-posts SOP in order:

  1 Research rules     sources current (check_sources), primary, Australian, read at source
  2 Topic              Brad's approval of the topic, with its date
  3 Angle              Brad's approval of the angle, dated no later than the copy approval
  4 Copy gate          check_copy on caption, slide text (read from the PDF) and first
                       comment; hook inside the limit; Brad's copy and first-comment approval
  5 Style (SOP 5b)     check_visual: size, slides, Sora/Inter, paper background, no website blue
  6 Images (SOP 5a)    each photo's source in the SOP order, listing number, "Stock Photo"
                       label, Brad's licence; or Brad's dated decision to run without photos
  7 Side by side       comparison sheet against every benchmark (Posts 1 and 2)
  8 Preview formats    LinkedIn-style preview, landscape review PDF, one-page team view
  9 Clean file         clean_file check; file name and hidden title match the public title

Each post lives in its own folder with a post.json manifest (see README in the posts
folder). The gate writes build/checklist.json (status and fingerprints of every file it
checked) and build/checklist.md (the ticked checklist shown at the top of every draft).
The Claude Code hook (post_gate_hook.py) reads checklist.json and refuses Buffer posts and
files sent to Brad unless the status is PASS and the files have not changed since.

  python3 post_gate.py run <post_dir>                 run every check, write the checklist
  python3 post_gate.py record-buffer <post_dir> <id>  note the Buffer post made from a PASS
Exit 0 = PASS, 1 = BLOCKED.
"""
import argparse
import datetime as dt
import glob
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import check_copy  # noqa: E402
import check_sources  # noqa: E402
import check_visual  # noqa: E402

RULES = json.load(open(os.path.join(SKILL, "linkedin_rules.json")))
BENCH_DIR = os.path.join(SKILL, "benchmarks")
STEPS = ["Research rules", "Topic", "Angle", "Copy gate", "Style (SOP 5b)",
         "Images (SOP 5a)", "Side by side with Posts 1 and 2", "Preview formats", "Clean file"]
# Benchmarks the side-by-side must include (Brad, 17 Nov 2026: Posts 1 and 2).
REQUIRED_BENCHMARKS = {"linkedin-post-1.pdf": "Post 1", "linkedin-post-2.pdf": "Post 2"}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if path and os.path.exists(path) else ""


def text_sha(s):
    return hashlib.sha256((s or "").strip().encode()).hexdigest()


def norm(s):
    return re.sub(r"\s+", " ", (s or "").replace("’", "'").replace("‘", "'")).strip()


def approval(obj, what):
    """Return (ok, evidence) for a {by, date, evidence} approval record."""
    a = (obj or {}).get("approved") if isinstance(obj, dict) and "approved" in obj else obj
    if not isinstance(a, dict):
        return False, f"no record of {RULES['approver']}'s approval of the {what}"
    missing = [k for k in ("by", "date", "evidence") if not str(a.get(k, "")).strip()]
    if missing:
        return False, f"approval of the {what} is missing {', '.join(missing)}"
    if RULES["approver"].lower() not in a["by"].lower():
        return False, f"the {what} was approved by {a['by']}, not {RULES['approver']}"
    try:
        dt.date.fromisoformat(str(a["date"])[:10])
    except ValueError:
        return False, f"approval date for the {what} is not a date: {a['date']}"
    return True, f"{a['by']}, {a['date']}: {a['evidence']}"


def run_copy(text, require=False, hook=False, max_chars=0):
    r = check_copy.check(text, check_copy.split_list(RULES["banned"]), check_copy.split_list(RULES["empty"]),
                         RULES["require_on_slides"] if require else "", max_chars, 0, 0,
                         check_copy.split_list(RULES["fail_phrases"]), check_copy.split_list(RULES["warn_phrases"]))
    fails = [f["detail"] for f in r["fails"]]
    warns = [w["detail"] for w in r["warnings"]]
    stats = dict(r["stats"])
    if hook:
        # SOP: the hook lands inside the first 140 to 210 characters, i.e. the opening
        # sentence ends before LinkedIn's "see more" fold.
        m = re.search(r"[.?!](?=\s|$)", text.strip())
        first = text.strip()[: m.end()] if m else text.strip()
        stats["hook_characters"] = len(first)
        if len(first) > RULES["hook_chars"]:
            fails.append(f"opening sentence is {len(first)} characters; the hook must land inside {RULES['hook_chars']}")
    return fails, warns, stats


def pdf_text(pdf):
    return subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout


def item(status, evidence, problems=None, notes=None):
    return {"status": status, "evidence": evidence, "problems": problems or [], "notes": notes or []}


# ---- the nine checks ------------------------------------------------------------

def step_research(m):
    srcs = (m.get("research") or {}).get("sources") or []
    if not srcs:
        return item("FAIL", "", ["no sources recorded"])
    allow = (m.get("research") or {}).get("allow_previous_year")
    allow_ok, allow_ev = approval(allow, "use of a previous-year source") if allow else (False, "")
    today = dt.date.fromisoformat(m.get("checked_on") or dt.date.today().isoformat())
    res = check_sources.judge(srcs, today, allow_ok)
    problems = [f"{r['title']} ({r['date']}): {r['why']}" for r in res if r["verdict"] != "PASS"]
    for s in srcs:
        host = (urlparse(s.get("url", "")).hostname or "").lower()
        if not host:
            problems.append(f"{s.get('title')}: no URL, so it was not read at source")
        elif any(host == d or host.endswith("." + d) for d in RULES["news_and_secondary_domains"]):
            problems.append(f"{s.get('title')}: {host} is news or secondary, not a primary source")
        elif not host.endswith(".au") and not s.get("cited_by_au_regulator"):
            problems.append(f"{s.get('title')}: {host} is not Australian")
        for k in ("verified_point", "where"):
            if not str(s.get(k, "")).strip():
                problems.append(f"{s.get('title')}: missing '{k}' (what was read, and where on the page)")
    ev = "; ".join(f"{r['title']} {r['date']} {r['verdict']}" for r in res)
    if allow_ok:
        ev += f". Previous-year source allowed: {allow_ev}"
    return item("FAIL" if problems else "PASS", "check_sources: " + ev, problems)


def step_approval(m, key, what):
    ok, ev = approval(m.get(key), what)
    text = (m.get(key) or {}).get("text", "")
    return item("PASS" if ok and text else "FAIL", f'"{text}". {ev}' if ok else "",
                [] if ok and text else [ev if not ok else f"the {what} itself is not written down"])


def step_angle(m):
    it = step_approval(m, "angle", "angle")
    if it["status"] == "PASS":
        a = str(m["angle"]["approved"]["date"])[:10]
        c = str(((m.get("copy") or {}).get("approved") or {}).get("date", ""))[:10]
        if c and a > c:
            it["status"] = "FAIL"
            it["problems"].append(f"angle approved {a}, after the copy was approved {c}; the angle comes first")
    return it


def step_copy(m, d, pdf):
    problems, notes, ev = [], [], []
    cap_path = os.path.join(d, m.get("caption_file", "caption.txt"))
    caption = open(cap_path).read() if os.path.exists(cap_path) else ""
    if not caption.strip():
        return item("FAIL", "", ["no caption file"])
    f, w, st = run_copy(caption, hook=True, max_chars=RULES["caption_max_chars"])
    problems += [f"caption: {x}" for x in f]
    notes += [f"caption: {x}" for x in w]
    ev.append(f"caption {st['characters']} chars, hook sentence {st['hook_characters']} chars: {'PASS' if not f else 'FAIL'}")
    if pdf and os.path.exists(pdf):
        f, w, _ = run_copy(pdf_text(pdf), require=True)
        problems += [f"slides: {x}" for x in f]
        notes += [f"slides: {x}" for x in w]
        ev.append(f"slide text read from the PDF: {'PASS' if not f else 'FAIL'}")
    else:
        problems.append("no carousel PDF to read the slide text from")
    fc = (m.get("first_comment") or {}).get("text", "")
    if fc:
        f, w, _ = run_copy(fc)
        problems += [f"first comment: {x}" for x in f]
        notes += [f"first comment: {x}" for x in w]
        ev.append(f"first comment: {'PASS' if not f else 'FAIL'}")
    else:
        problems.append("no first comment")
    ok, a = approval((m.get("copy") or {}).get("approved"), "copy")
    if not ok:
        problems.append(a)
    else:
        ev.append(f"copy approved: {a}")
    ok, a = approval((m.get("first_comment") or {}).get("approved"), "first comment")
    if not ok:
        problems.append(a)
    else:
        ev.append(f"first comment approved: {a}")
    return item("FAIL" if problems else "PASS", "; ".join(ev), problems, notes)


def step_style(visual):
    probs = visual["fails"]
    return item("FAIL" if probs else "PASS",
                f"check_visual: {visual['slides']} slides, " + ("PASS" if not probs else "FAIL"), probs)


def step_images(m, visual):
    imgs = m.get("images") or []
    order = RULES["image_sources_in_order"]
    problems, ev = [], []
    has_photo = any(p["photo"] for p in visual["pages"])
    if not imgs:
        ok, a = approval(m.get("images_waived"), "decision to run without photos")
        if ok and not has_photo:
            return item("PASS", f"no photos, by decision: {a}")
        if has_photo:
            return item("FAIL", "", ["the carousel shows a photo but no image source is recorded"])
        return item("FAIL", "", ["no photos and no dated decision from Brad to run without them; "
                                 "Posts 1 and 2 use photo bands (SOP 5a: own photos, then 123RF, then Unsplash or Pexels)"])
    for im in imgs:
        src = (im.get("source") or "").lower()
        tag = f"slide {im.get('slide', '?')}"
        if src not in order:
            problems.append(f"{tag}: source '{src}' is not one of {order}")
            continue
        if src == "own":
            ok, a = approval(im.get("confirmed"), f"own photo on {tag}")
            (ev.append(f"{tag}: Brad's own photo ({a})") if ok else problems.append(a))
            continue
        if not im.get("id") or not im.get("listing"):
            problems.append(f"{tag}: {src} image has no number or listing link")
        if src == "123rf":
            if im.get("type_label") != "Stock Photo":
                problems.append(f"{tag}: 123RF {im.get('id')} label is '{im.get('type_label')}', not 'Stock Photo'")
            if im.get("ai_generated"):
                problems.append(f"{tag}: 123RF {im.get('id')} is AI-generated")
            if im.get("editorial_only") is not False:
                problems.append(f"{tag}: 123RF {im.get('id')} is not confirmed free of 'For Editorial Use Only' "
                                "(editorial images cannot be used in promotional posts)")
        if src in ("unsplash", "pexels") and not im.get("why_not_123rf"):
            problems.append(f"{tag}: {src} used without noting why no 123RF image fitted (SOP order)")
        ok, a = approval(im.get("licensed"), f"licence for {tag}")
        if not ok and src == "123rf":
            problems.append(f"{tag}: 123RF {im.get('id')} not licensed by Brad yet ({a})")
        ev.append(f"{tag}: {src} {im.get('id', '')} {im.get('type_label', '')}"
                  + (f", licensed {im['licensed']['date']}" if ok else ""))
    if not has_photo:
        problems.append("images are recorded but no photo shows in the carousel")
    return item("FAIL" if problems else "PASS", "; ".join(ev), problems)


def step_side_by_side(pdf, build):
    benches = sorted(glob.glob(os.path.join(BENCH_DIR, "linkedin-post-*.pdf")))
    missing = [name for f, name in REQUIRED_BENCHMARKS.items() if not os.path.exists(os.path.join(BENCH_DIR, f))]
    sheet = os.path.join(build, "side-by-side.png")
    rows = []
    with tempfile.TemporaryDirectory() as t:
        for i, b in enumerate(benches):
            rows.append(check_visual.render(b, t, f"b{i}"))
        rows.append(check_visual.render(pdf, t, "d"))
        from PIL import Image, ImageDraw
        cw, ch, gap = 216, 270, 8
        cols = max(len(r) for r in rows)
        s = Image.new("RGB", (cols * (cw + gap) + 120, len(rows) * (ch + 16)), "white")
        dr = ImageDraw.Draw(s)
        labels = [os.path.basename(b).replace("linkedin-", "").replace(".pdf", "").replace("-", " ").title() for b in benches] + ["This draft"]
        for r, (pngs, lab) in enumerate(zip(rows, labels)):
            dr.text((6, r * (ch + 16) + ch // 2), lab, fill="black")
            for c, p in enumerate(pngs):
                s.paste(Image.open(p).convert("RGB").resize((cw, ch)), (120 + c * (cw + gap), r * (ch + 16)))
        s.save(sheet)
    probs = [f"{n} benchmark file is missing from skills/marketing-copy-gate/benchmarks/ "
             f"(add {f})" for f, n in REQUIRED_BENCHMARKS.items() if n in missing]
    return item("FAIL" if probs else "PASS",
                f"build/side-by-side.png: {', '.join(labels[:-1])} above, this draft below", probs), sheet


def step_previews(d, m, pdf, build, checklist_rows):
    """Build the three review formats from the actual PDF and caption."""
    out = {"linkedin_preview": os.path.join(build, "linkedin-preview.png"),
           "review_pdf": os.path.join(build, "review.pdf"),
           "team_view": os.path.join(build, "team-view.pdf")}
    slides_dir = os.path.join(build, "slides")
    os.makedirs(slides_dir, exist_ok=True)
    for f in glob.glob(os.path.join(slides_dir, "*.png")):
        os.remove(f)
    subprocess.run(["pdftoppm", "-r", "96", "-png", pdf, os.path.join(slides_dir, "s")], check=True)
    slides = sorted(glob.glob(os.path.join(slides_dir, "s*.png")))
    caption = open(os.path.join(d, m.get("caption_file", "caption.txt"))).read().strip()
    fc = (m.get("first_comment") or {}).get("text", "")
    title = m.get("public_title", "")
    name = m.get("post_name", "LinkedIn Page Post")
    rel = lambda p: os.path.relpath(p, build)
    esc = lambda s: html.escape(s).replace("\n", "<br>")
    css = """<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Sora:wght@600&display=swap">
<style>*{box-sizing:border-box;margin:0;padding:0}body{font-family:Inter,system-ui,sans-serif;color:#191919;background:#F3F2EF}
.card{background:#fff;border:1px solid #ddd;border-radius:8px;width:600px;margin:20px auto;padding:16px 0}
.hd{display:flex;gap:10px;align-items:center;padding:0 16px 10px}.av{width:48px;height:48px;border-radius:50%;background:#151B2B;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:600}
.nm{font-weight:600;font-size:14px}.sub{font-size:12px;color:#666}.cap{font-size:14px;line-height:1.45;padding:0 16px 12px}
.doc{border-top:1px solid #eee;border-bottom:1px solid #eee}.doc .bar{font-size:13px;font-weight:600;padding:8px 16px}.doc img{width:100%;display:block}
.fc{font-size:13px;margin:10px 16px 0;padding:10px;background:#F3F2EF;border-radius:8px}.fc b{display:block;margin-bottom:4px}
section{width:1600px;height:1000px;background:#fff;page-break-after:always;padding:40px;display:flex;gap:40px;overflow:hidden}
.big{height:920px;border:1px solid #ddd}.chk{font-size:15px;line-height:1.5;width:100%}.chk td{padding:3px 8px;border-bottom:1px solid #eee;vertical-align:top}
.pass{color:#2F8A80;font-weight:600}.fail{color:#B4534E;font-weight:600}h1{font-family:Sora;font-size:30px;margin-bottom:12px}
.strip{display:flex;gap:16px;margin-top:20px}.strip img{width:288px;border:1px solid #ddd}</style>"""
    card = (f'<div class="card"><div class="hd"><div class="av">BP</div><div><div class="nm">Brad Pickett</div>'
            f'<div class="sub">Founder, ERMOS</div></div></div><div class="cap">{esc(caption)}</div>'
            f'<div class="doc"><div class="bar">{html.escape(title)} &middot; {len(slides)} pages</div>'
            f'<img src="{rel(slides[0])}"></div>'
            + (f'<div class="fc"><b>First comment</b>{esc(fc)}</div>' if fc else "") + "</div>")
    with open(os.path.join(build, "linkedin-preview.html"), "w") as fh:
        fh.write(f"<!doctype html><meta charset=utf-8>{css}<body>{card}</body>")
    chk = "".join(f'<tr><td>{i}</td><td>{s}</td><td class="{st.lower()}">{st}</td></tr>' for i, s, st in checklist_rows)
    pages = [f'<section><div><h1>{html.escape(name)}: pre-delivery checklist</h1><table class="chk">{chk}</table></div>'
             f'<div style="flex:none;width:640px;zoom:.85">{card}</div></section>']
    pages += [f'<section style="justify-content:center"><img class="big" src="{rel(s)}"></section>' for s in slides]
    with open(os.path.join(build, "review.html"), "w") as fh:
        fh.write(f"<!doctype html><meta charset=utf-8>{css}<body style='background:#fff'>{''.join(pages)}</body>")
    team = (f'<section style="flex-direction:column;gap:0"><h1>{html.escape(name)} ERMOS Carousel</h1>'
            f'<div class="cap" style="font-size:16px;padding:0;max-width:1500px">{esc(caption)}</div>'
            f'<div class="strip">{"".join(f"<img src={chr(34)}{rel(s)}{chr(34)}>" for s in slides[:5])}</div></section>')
    with open(os.path.join(build, "team-view.html"), "w") as fh:
        fh.write(f"<!doctype html><meta charset=utf-8>{css}<body style='background:#fff'>{team}</body>")
    r = lambda a: subprocess.run(["node", os.path.join(HERE, "render_html.js")] + a, capture_output=True, text=True)
    r([os.path.join(build, "linkedin-preview.html"), out["linkedin_preview"], "640"])
    r([os.path.join(build, "review.html"), out["review_pdf"], "1600", "1000"])
    r([os.path.join(build, "team-view.html"), out["team_view"], "1600", "1000"])
    missing = [k for k, p in out.items() if not os.path.exists(p) or os.path.getsize(p) < 1000]
    return item("FAIL" if missing else "PASS",
                "build/linkedin-preview.png, build/review.pdf (checklist then slides), build/team-view.pdf",
                [f"{k} was not produced" for k in missing])


def step_clean(pdf, m):
    r = json.loads(subprocess.run([sys.executable, os.path.join(HERE, "clean_file.py"), "check", pdf],
                                  capture_output=True, text=True).stdout or "{}")
    problems = list(r.get("problems", []))
    want = re.sub(r'[\\/:*?"<>|]+', " -", m.get("public_title", "")).strip()
    stem = os.path.splitext(os.path.basename(pdf))[0]
    if norm(stem.replace(" -", ":")).lower() != norm(m.get("public_title", "")).lower() and stem != want:
        problems.append(f"file name '{stem}' does not match the public title '{m.get('public_title')}'")
    return item("FAIL" if problems else "PASS", f"clean_file check on '{os.path.basename(pdf)}': "
                + ("PASS" if not problems else "FAIL"), problems)


# ---- run ----------------------------------------------------------------------------

def run(d):
    d = os.path.abspath(d)
    m = json.load(open(os.path.join(d, "post.json")))
    build = os.path.join(d, "build")
    os.makedirs(build, exist_ok=True)
    pdf = os.path.join(d, m["carousel_pdf"]) if m.get("carousel_pdf") else ""
    items = {}
    items["Research rules"] = step_research(m)
    items["Topic"] = step_approval(m, "topic", "topic")
    items["Angle"] = step_angle(m)
    items["Copy gate"] = step_copy(m, d, pdf)
    if pdf and os.path.exists(pdf):
        visual = check_visual.check(pdf, None)
        items["Style (SOP 5b)"] = step_style(visual)
        items["Images (SOP 5a)"] = step_images(m, visual)
        items["Side by side with Posts 1 and 2"], _ = step_side_by_side(pdf, build)
        rows = [(i + 1, s, items[s]["status"] if s in items else "PENDING") for i, s in enumerate(STEPS)]
        items["Preview formats"] = step_previews(d, m, pdf, build, rows)
        items["Clean file"] = step_clean(pdf, m)
    else:
        for s in STEPS[4:]:
            items[s] = item("FAIL", "", ["no carousel PDF"])
    status = "PASS" if all(items[s]["status"] == "PASS" for s in STEPS) else "BLOCKED"
    cap = open(os.path.join(d, m.get("caption_file", "caption.txt"))).read() if os.path.exists(os.path.join(d, m.get("caption_file", "caption.txt"))) else ""
    result = {
        "post": m.get("post_name"), "public_title": m.get("public_title"), "status": status,
        "checked_at": dt.datetime.now().isoformat(timespec="seconds"),
        "items": [{"n": i + 1, "step": s, **items[s]} for i, s in enumerate(STEPS)],
        "fingerprints": {"manifest": sha(os.path.join(d, "post.json")), "pdf": sha(pdf),
                         "caption": text_sha(norm(cap)), "first_comment": text_sha(norm((m.get("first_comment") or {}).get("text", "")))},
        "pdf_name": os.path.basename(pdf) if pdf else "",
    }
    json.dump(result, open(os.path.join(build, "checklist.json"), "w"), indent=1, ensure_ascii=False)
    open(os.path.join(build, "checklist.md"), "w").write(markdown(result))
    # rebuild the review PDF so its first page carries the final checklist
    if pdf and os.path.exists(pdf):
        rows = [(it["n"], it["step"], it["status"]) for it in result["items"]]
        step_previews(d, m, pdf, build, rows)
        result["fingerprints"]["manifest"] = sha(os.path.join(d, "post.json"))
        json.dump(result, open(os.path.join(build, "checklist.json"), "w"), indent=1, ensure_ascii=False)
    return result


def markdown(r):
    tick = {"PASS": "✅", "FAIL": "❌"}
    lines = [f"**Pre-delivery checklist: {r['post']}: {r['status']}** (checked {r['checked_at']})", "",
             "| # | Step | Result | Evidence |", "|---|---|---|---|"]
    for it in r["items"]:
        ev = it["evidence"] or "none"
        if it["problems"]:
            ev += " **Failed because:** " + "; ".join(it["problems"])
        lines.append(f"| {it['n']} | {it['step']} | {tick.get(it['status'], '')} {it['status']} | {ev.replace('|', '/')} |")
    return "\n".join(lines) + "\n"


def record_buffer(d, post_id):
    c = json.load(open(os.path.join(d, "build", "checklist.json")))
    if c["status"] != "PASS":
        sys.exit("checklist is not PASS; a Buffer post cannot be recorded against it")
    p = os.path.join(d, "buffer.json")
    data = json.load(open(p)) if os.path.exists(p) else {"buffer_post_ids": []}
    if post_id not in data["buffer_post_ids"]:
        data["buffer_post_ids"].append(post_id)
    json.dump(data, open(p, "w"), indent=1)
    print(json.dumps(data))


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["run", "record-buffer"])
    p.add_argument("post_dir")
    p.add_argument("buffer_id", nargs="?")
    a = p.parse_args(argv)
    if a.action == "record-buffer":
        record_buffer(a.post_dir, a.buffer_id)
        return 0
    r = run(a.post_dir)
    print(markdown(r))
    return 0 if r["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
