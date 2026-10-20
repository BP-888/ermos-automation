"""Meeting Actions: run it now, or see how the last runs went.

    python agents/meeting-actions/run.py run      # start a run immediately (the test run) and watch it live
    python agents/meeting-actions/run.py latest   # list the last 5 runs with their Console links

Needs MEETING_ACTIONS_DEPLOYMENT_ID (the depl_... id from claude-lock.json).
"""

import os
import sys

import anthropic

DEPLOYMENT_ID = os.environ["MEETING_ACTIONS_DEPLOYMENT_ID"]
CONSOLE = "https://platform.claude.com/workspaces/default/sessions/{}"

client = anthropic.Anthropic()


def run_now() -> None:
    run = client.beta.deployments.run(DEPLOYMENT_ID)
    if not run.session_id:
        sys.exit(f"Run did not start: {run.error.type}: {run.error.message}")
    print("Watch live:", CONSOLE.format(run.session_id))

    with client.beta.sessions.events.stream(session_id=run.session_id) as stream:
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
                        session_id=run.session_id,
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


def latest() -> None:
    for i, run in enumerate(client.beta.deployment_runs.list(deployment_id=DEPLOYMENT_ID)):
        if i == 5:
            break
        trigger = run.trigger_context.type
        if run.session_id:
            print(run.created_at, trigger, CONSOLE.format(run.session_id))
        else:
            print(run.created_at, trigger, "FAILED", run.error.type, run.error.message)


if __name__ == "__main__":
    {"run": run_now, "latest": latest}[sys.argv[1] if len(sys.argv) > 1 else "latest"]()
