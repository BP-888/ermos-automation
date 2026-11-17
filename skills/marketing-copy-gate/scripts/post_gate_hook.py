#!/usr/bin/env python3
"""Claude Code PreToolUse hook: the hard stop behind the LinkedIn pre-delivery gate.

Runs before Buffer post tools and before any file is sent or published to Brad. It
allows the call only when the post it belongs to has a checklist with status PASS and
the caption, first comment, carousel PDF and manifest are unchanged since that check.
Otherwise it denies the call and says why. Enforced by Claude Code, not by memory.

  - mcp__Buffer__create_post / edit_post with text: the text must be the caption of a
    PASS post (and any first comment must be that post's approved first comment).
  - mcp__Buffer__edit_post without text: the Buffer post id must be recorded against a
    PASS post (post_gate.py record-buffer).
  - SendUserFile, Artifact publishes: any file inside a post folder, or whose name is a
    post's public file name, needs that post to be PASS.
Everything else passes through untouched.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
POSTS = os.path.join(ROOT, "marketing", "linkedin", "posts")


def norm(s):
    return re.sub(r"\s+", " ", (s or "").replace("’", "'").replace("‘", "'")).strip()


def text_sha(s):
    return hashlib.sha256((s or "").strip().encode()).hexdigest()


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest() if path and os.path.exists(path) else ""


def posts():
    if not os.path.isdir(POSTS):
        return
    for name in sorted(os.listdir(POSTS)):
        d = os.path.join(POSTS, name)
        mp = os.path.join(d, "post.json")
        if not os.path.exists(mp):
            continue
        m = json.load(open(mp))
        cp = os.path.join(d, "build", "checklist.json")
        c = json.load(open(cp)) if os.path.exists(cp) else None
        yield d, m, c


def verdict(d, m, c):
    """(ok, reason) for one post: PASS and nothing changed since the check."""
    label = m.get("post_name") or os.path.basename(d)
    if not c:
        return False, f"{label} has never been through the pre-delivery gate (run post_gate.py run {d})"
    if c.get("status") != "PASS":
        failed = [f"{i['n']} {i['step']}: {'; '.join(i['problems']) or 'no evidence'}" for i in c["items"] if i["status"] != "PASS"]
        return False, f"{label} is BLOCKED by the pre-delivery gate. Failed: " + " | ".join(failed)
    f = c.get("fingerprints", {})
    cap_path = os.path.join(d, m.get("caption_file", "caption.txt"))
    cap = open(cap_path).read() if os.path.exists(cap_path) else ""
    pdf = os.path.join(d, m.get("carousel_pdf", "")) if m.get("carousel_pdf") else ""
    changed = [k for k, now in (("manifest", sha(os.path.join(d, "post.json"))), ("pdf", sha(pdf)),
                                ("caption", text_sha(norm(cap))),
                                ("first_comment", text_sha(norm((m.get("first_comment") or {}).get("text", "")))))
               if f.get(k) != now]
    if changed:
        return False, f"{label} changed after its checklist passed ({', '.join(changed)}); run the gate again"
    return True, f"{label} checklist PASS ({c.get('checked_at')})"


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": "Pre-delivery gate: " + reason}}))
    return 0


def file_paths(tool, ti):
    out = []
    if tool == "SendUserFile":
        out += ti.get("files") or []
    for k in ("file_path",):
        if ti.get(k):
            out.append(ti[k])
    for k in ("file_paths",):
        out += ti.get(k) or []
    fl = ti.get("files")
    if tool != "SendUserFile" and fl:
        if isinstance(fl, dict):
            out += [v if isinstance(v, str) else (v or {}).get("from", "") for v in fl.values()]
            out += list(fl.keys())
        elif isinstance(fl, list):
            out += [x.get("path", "") if isinstance(x, dict) else str(x) for x in fl]
    return [p for p in out if p]


def main():
    data = json.load(sys.stdin)
    tool, ti = data.get("tool_name", ""), data.get("tool_input") or {}
    all_posts = list(posts())

    if tool in ("mcp__Buffer__create_post", "mcp__Buffer__edit_post"):
        text = ti.get("text")
        if text is None and tool == "mcp__Buffer__edit_post":
            pid = ti.get("postId") or ti.get("id") or ""
            for d, m, c in all_posts:
                bp = os.path.join(d, "buffer.json")
                ids = json.load(open(bp)).get("buffer_post_ids", []) if os.path.exists(bp) else []
                if pid in ids:
                    ok, why = verdict(d, m, c)
                    return 0 if ok else deny(why)
            return deny(f"Buffer post {pid} is not recorded against any post that passed the gate")
        match = None
        for d, m, c in all_posts:
            cap_path = os.path.join(d, m.get("caption_file", "caption.txt"))
            if os.path.exists(cap_path) and norm(open(cap_path).read()) == norm(text):
                match = (d, m, c)
                break
        if not match:
            return deny("this caption does not match any post folder's approved caption, so it has no checklist. "
                        "Put the post in marketing/linkedin/posts/<post>/ and run post_gate.py")
        ok, why = verdict(*match)
        if not ok:
            return deny(why)
        fc = (((ti.get("metadata") or {}).get("linkedin") or {}).get("firstComment"))
        want = (match[1].get("first_comment") or {}).get("text", "")
        if fc and norm(fc) != norm(want):
            return deny("the first comment is not the approved first comment for this post")
        return 0

    if tool in ("SendUserFile", "Artifact") or tool.startswith("mcp__claude-artifacts__publish"):
        for p in file_paths(tool, ti):
            ap = os.path.abspath(p)
            base = os.path.basename(ap)
            for d, m, c in all_posts:
                inside = ap.startswith(d + os.sep)
                named = m.get("carousel_pdf") and base == os.path.basename(m["carousel_pdf"])
                if inside or named:
                    ok, why = verdict(d, m, c)
                    if not ok:
                        return deny(f"{base}: {why}")
        return 0
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # a broken gate must stop delivery, not wave it through
        deny(f"the gate hook itself failed ({e}); fix it before sending")
        sys.exit(0)
