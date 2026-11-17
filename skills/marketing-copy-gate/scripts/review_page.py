#!/usr/bin/env python3
"""Build Brad's review page for a LinkedIn post that passed the pre-delivery gate.

  python3 review_page.py <post_dir> [--slot "Thursday 19 November, 3:42pm"]

Writes <post_dir>/build/review-page.html: the ticked checklist first, then the post as
LinkedIn shows it (caption, cover, first comment), all slides, the side-by-side with
Posts 1 and 2, the team view, and the steps to go live. Publish it with the Artifact tool;
the pre-delivery hook allows it only while the post's checklist is PASS and unchanged.
"""
import argparse
import base64
import glob
import html
import io
import json
import os
import subprocess
import sys

from PIL import Image


def uri(p, maxw=1100, q=82):
    im = Image.open(p).convert("RGB")
    im.thumbnail((maxw, maxw * 3))
    b = io.BytesIO()
    im.save(b, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def build(d, slot):
    c = json.load(open(os.path.join(d, "build", "checklist.json")))
    if c["status"] != "PASS":
        sys.exit("checklist is not PASS: the review page is only built for a post that passed")
    m = json.load(open(os.path.join(d, "post.json")))
    b = os.path.join(d, "build")
    for f in glob.glob(os.path.join(b, "tv-*.png")):
        os.remove(f)
    subprocess.run(["pdftoppm", "-r", "48", "-png", os.path.join(b, "team-view.pdf"), os.path.join(b, "tv")], check=True)
    slides = sorted(glob.glob(os.path.join(b, "slides", "s*.png")))
    rows = "".join(
        f'<tr><td class="n">{i["n"]}</td><td>{i["step"]}</td><td><span class="pill {i["status"].lower()}">'
        f'{"✓ " if i["status"] == "PASS" else ""}{i["status"]}</span></td><td>{html.escape(i["evidence"][:260])}</td></tr>'
        for i in c["items"])
    grid = "".join(f'<figure><img src="{uri(s, 700)}" alt="Slide {k + 1}"><figcaption>Slide {k + 1}</figcaption></figure>'
                   for k, s in enumerate(slides))
    cap = html.escape(open(os.path.join(d, m.get("caption_file", "caption.txt"))).read().strip()).replace("\n", "<br>")
    fc = html.escape(m["first_comment"]["text"])
    title = html.escape(m["public_title"])
    page = f'''<title>{html.escape(m.get("review_title", "LinkedIn Post Review"))}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@600&family=Inter:wght@400;500;600&display=swap">
<style>
/* Layout: one column on ERMOS paper; checklist first, then the post as LinkedIn shows it, then slides and comparisons */
:root{{--bg:#EFEEEA;--card:#FBFAF7;--ink:#151B2B;--muted:#5A5F6B;--teal:#2F8A80;--coral:#B4534E;--rule:#D9D7D0}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#151B2B;--card:#1E2638;--ink:#EEF0F3;--muted:#A9AFBC;--teal:#5FB8AD;--coral:#E28A84;--rule:#2E3850;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#151B2B;--card:#1E2638;--ink:#EEF0F3;--muted:#A9AFBC;--teal:#5FB8AD;--coral:#E28A84;--rule:#2E3850;color-scheme:dark}}
*{{box-sizing:border-box}}body{{background:var(--bg);color:var(--ink);font:16px/1.55 Inter,system-ui,sans-serif;margin:0}}
main{{max-width:1000px;margin:0 auto;padding-block:36px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:36px}}
h1{{font:600 clamp(26px,4vw,36px)/1.15 Sora,system-ui,sans-serif;margin:8px 0;text-wrap:balance}}h2{{font:600 22px Sora,system-ui,sans-serif;margin:0 0 12px}}
.wm{{font:600 14px Sora,system-ui,sans-serif;letter-spacing:.42em}}.muted{{color:var(--muted)}}
.card{{background:var(--card);border:1px solid var(--rule);border-radius:10px;padding:18px 20px}}
.tw{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:14px;min-width:560px}}
th{{text-align:left;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--rule);padding:8px}}
td{{border-bottom:1px solid var(--rule);padding:8px;vertical-align:top}}td.n{{color:var(--muted);font-variant-numeric:tabular-nums}}
.pill{{display:inline-block;font-size:12px;font-weight:600;padding:2px 9px;border-radius:999px;border:1px solid currentColor;white-space:nowrap}}.pill.pass{{color:var(--teal)}}.pill.fail{{color:var(--coral)}}
.status{{font:600 18px Sora,system-ui,sans-serif;color:var(--teal)}}
.li{{background:#fff;color:#191919;border:1px solid #ddd;border-radius:8px;max-width:560px;padding:14px 0}}
.li .hd{{display:flex;gap:10px;align-items:center;padding:0 14px 10px}}.av{{width:44px;height:44px;border-radius:50%;background:#151B2B;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:600}}
.li .cap{{font-size:14px;padding:0 14px 10px}}.li .bar{{font-size:13px;font-weight:600;padding:8px 14px;border-top:1px solid #eee}}.li img{{width:100%;display:block}}
.li .fc{{margin:10px 14px 0;padding:10px;background:#F3F2EF;border-radius:8px;font-size:13px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}}figure{{margin:0;min-width:0}}figure img{{width:100%;display:block;border:1px solid var(--rule)}}figcaption{{font-size:13px;color:var(--muted);margin-top:4px}}
.wide img{{width:100%;display:block;border:1px solid var(--rule);border-radius:6px}}
ol{{margin:0;padding-left:22px;display:grid;gap:6px}}
</style>
<main>
<div><div class="wm">ERMOS</div><h1>{html.escape(m.get("post_name", "LinkedIn post"))}: ready for your approval</h1><p class="muted" style="margin:0;max-width:65ch">Set for {html.escape(slot)} on your profile through Buffer. Nothing has been scheduled.</p></div>
<section class="card"><h2>Pre-delivery checklist</h2><p class="status">PASS: 9 of 9 <span class="muted" style="font:400 14px Inter,system-ui,sans-serif">(checked {c["checked_at"].replace("T", " ")})</span></p><div class="tw"><table><thead><tr><th>#</th><th>Step</th><th>Result</th><th>Evidence</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section><h2>How it looks on LinkedIn</h2><div class="li"><div class="hd"><div class="av">BP</div><div><b style="font-size:14px">Brad Pickett</b><div style="font-size:12px;color:#666">Founder, ERMOS</div></div></div><div class="cap">{cap}</div><div class="bar">{title} · {len(slides)} pages</div><img src="{uri(slides[0], 900)}" alt="Slide 1"><div class="fc"><b>First comment</b><br>{fc}</div></div></section>
<section><h2>All {len(slides)} slides</h2><div class="grid">{grid}</div></section>
<section class="wide"><h2>Side by side with Posts 1 and 2</h2><img src="{uri(os.path.join(b, "side-by-side.png"), 1400)}" alt="Post 1 and Post 2 above, this post below"></section>
<section class="wide"><h2>Team view</h2><img src="{uri(sorted(glob.glob(os.path.join(b, "tv*.png")))[0], 1400)}" alt="One-page team view"></section>
<section class="card"><h2>To go live</h2><ol><li>Reply "approved" in the chat.</li><li>I update the Buffer draft with this caption and first comment.</li><li>You attach the PDF in Buffer, check the Document Title reads "{title}", and press Schedule Post.</li></ol></section>
</main>'''
    out = os.path.join(b, "review-page.html")
    open(out, "w").write(page)
    return out


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("post_dir")
    a.add_argument("--slot", default="the next Buffer slot")
    x = a.parse_args()
    print(build(x.post_dir, x.slot))
