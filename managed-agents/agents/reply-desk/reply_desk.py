"""Reply Desk: test the trigger logic, start a run from a saved reply, read a run's result.

    python reply_desk.py check samples/reply-exact-positive.json   # no API call: shows what n8n would send
    python reply_desk.py run samples/reply-pricing.json            # start a real session from a saved reply and watch it
    python reply_desk.py result sesn_...                           # the result JSON n8n reads after a run
    python reply_desk.py latest                                    # the last 5 Reply Desk runs with Console links

The live trigger is the n8n workflow revenue-reply-desk-start (see trigger.md).
It makes the same session request as build_session_request() below; keep the
two in step when either changes.

run, result and latest need REPLY_DESK_AGENT_ID, REPLY_DESK_ENVIRONMENT_ID and
REPLY_DESK_VAULT_ID (the agent_, env_ and vlt_ ids from claude-lock.json).
"""

import json
import os
import re
import sys

# Ruled 14 Oct 2026 (revenue-classify-reply): replies that are exactly one of
# these are positive with no classification. Anything else goes to Claude.
POSITIVE_SET = {
    "yes",
    "yes please",
    "send",
    "send it",
    "send it over",
    "sure",
    "please do",
    "go on",
}

# Smartlead events that are a person replying. Bounces and unsubscribes never start a run.
REPLY_EVENTS = {"EMAIL_REPLY", "UNTRACKED_REPLIES"}

BUDGET_CENTS = "300"  # hard cap per run, US$3.00 at list price
CONSOLE = "https://platform.claude.com/workspaces/default/sessions/{}"


def clean_reply(payload: dict) -> str:
    """The new text only. Same steps as the Classify Reply node in smartlead-reply-router:
    every reply quotes step 1's 'Mind if I send it over?', so the quote must go first."""
    src = payload.get("preview_text") or payload.get("reply_body") or ""
    text = re.sub(r"<br\s*/?>", "\n", src, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.split(r"(?:^|\n)\s*(?:On .{0,80}wrote:|-{2,}\s*Original Message|From:\s)", text, flags=re.I)[0]
    return re.sub(r"\s+", " ", text).strip()


def is_exact_positive(reply_text: str) -> bool:
    normal = re.sub(r"[^a-z ]", "", reply_text.lower())
    return re.sub(r"\s+", " ", normal).strip() in POSITIVE_SET


def build_session_request(payload: dict) -> dict | None:
    """The POST /v1/sessions body for one Smartlead reply, or None if it should not start a run."""
    if payload.get("event_type") not in REPLY_EVENTS:
        return None
    reply_text = clean_reply(payload)
    lead_email = (payload.get("to_email") or "").lower()
    if "@" not in lead_email or not reply_text:
        return None

    run_input = {
        "lead_email": lead_email,
        "lead_name": payload.get("to_name") or "",
        "reply_text": reply_text[:4000],
        "reply_raw": (payload.get("preview_text") or payload.get("reply_body") or "")[:8000],
        "subject": payload.get("subject") or "",
        "campaign_name": payload.get("campaign_name") or "",
        "campaign_id": payload.get("campaign_id"),
        "sequence_number": payload.get("sequence_number"),
        "replied_at": payload.get("time_replied") or "",
        "from_mailbox": payload.get("from_email") or "",
        "exact_positive": is_exact_positive(reply_text),
    }
    return {
        "agent": os.environ.get("REPLY_DESK_AGENT_ID", "REPLY_DESK_AGENT_ID"),
        "environment_id": os.environ.get("REPLY_DESK_ENVIRONMENT_ID", "REPLY_DESK_ENVIRONMENT_ID"),
        "vault_ids": [os.environ.get("REPLY_DESK_VAULT_ID", "REPLY_DESK_VAULT_ID")],
        "title": f"Reply from {lead_email}",
        "metadata": {"source": "smartlead", "lead_email": lead_email[:512]},
        "budget": {"type": "limit", "max_list_cost": {"amount": BUDGET_CENTS, "currency": "USD"}},
        "initial_events": [
            {"type": "user.message", "content": [{"type": "text", "text": json.dumps(run_input, indent=2)}]}
        ],
    }


def read_result(client, session_id: str) -> dict:
    """The agent's last message, parsed. This is what n8n posts to #hq-approvals and logs."""
    last_text, stop = "", None
    for event in client.beta.sessions.events.list(session_id=session_id):
        if event.type == "agent.message":
            last_text = "".join(b.text for b in event.content if b.type == "text")
        elif event.type == "session.status_idle":
            stop = event.stop_reason.type
    match = re.search(r"```json\s*(\{.*\})\s*```", last_text, re.S)
    if stop != "end_turn" or not match:
        return {"error": f"run did not finish cleanly (stop reason: {stop})", "last_message": last_text}
    return json.loads(match.group(1))


def load_payload(path: str) -> dict:
    with open(path) as f:
        data = json.load(f)
    return data.get("body", data)  # accepts a raw Smartlead body or an n8n webhook item


def check(path: str) -> None:
    request = build_session_request(load_payload(path))
    if request is None:
        print("Would not start a run (not a reply, or no address or text).")
        return
    print(json.dumps(request, indent=2))


def run(path: str) -> None:
    import anthropic

    request = build_session_request(load_payload(path))
    if request is None:
        sys.exit("Would not start a run (not a reply, or no address or text).")
    client = anthropic.Anthropic()
    session = client.beta.sessions.create(**request)
    print("Watch live:", CONSOLE.format(session.id))

    # Created with initial_events, so it is already running. Stream until it settles.
    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        print(block.text, end="", flush=True)
            elif event.type == "agent.mcp_tool_use":
                print(f"\n[{event.mcp_server_name}] {event.name}", flush=True)
                if event.evaluated_permission == "ask":
                    # Every enabled tool is always_allow, so this should never happen.
                    # If it does, refuse: nothing unreviewed runs.
                    client.beta.sessions.events.send(
                        session_id=session.id,
                        events=[{"type": "user.tool_confirmation", "tool_use_id": event.id, "result": "deny"}],
                    )
            elif event.type == "session.error":
                print(f"\n[error] {event}", flush=True)
            elif event.type == "session.status_idle":
                if event.stop_reason.type != "requires_action":
                    print(f"\n--- finished ({event.stop_reason.type}) ---")
                    break
            elif event.type == "session.status_terminated":
                print("\n--- session terminated ---")
                break
    print(json.dumps(read_result(client, session.id), indent=2))


def result(session_id: str) -> None:
    import anthropic

    print(json.dumps(read_result(anthropic.Anthropic(), session_id), indent=2))


def latest() -> None:
    import anthropic

    agent_id = os.environ["REPLY_DESK_AGENT_ID"]
    shown = 0
    for session in anthropic.Anthropic().beta.sessions.list():
        if session.agent.id != agent_id:
            continue
        print(session.created_at, session.status, session.title, CONSOLE.format(session.id))
        shown += 1
        if shown == 5:
            break


if __name__ == "__main__":
    command, *args = sys.argv[1:] or ["latest"]
    {"check": check, "run": run, "result": result, "latest": latest}[command](*args)
