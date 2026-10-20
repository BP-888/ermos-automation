# ERMOS: rules for Claude

## Source of truth for agent and workflow design

Anthropic's own guidance decides every question about agent architecture, workflow design and tools. Read the relevant page before deciding; don't rely on memory or outside patterns.

1. Architecture: https://www.anthropic.com/engineering/building-effective-agents
2. Working in Claude Code: https://code.claude.com/docs/en/best-practices
3. Tool design: https://www.anthropic.com/engineering/writing-tools-for-agents
4. Choosing a pattern: https://claude.com/resources/articles/common-workflow-patterns-for-ai-agents-and-when-to-use-them

## Non-negotiable rules

- **Simplest thing that works.** Build fixed workflows first (n8n, or a chain of Claude calls). Propose a Managed Agent only when the work is open-ended, can't be scripted step by step, and is worth the extra cost. Say which named pattern you are using (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer, agent) and why nothing simpler fits.
- **Explore → Plan → Implement → Verify** for any non-trivial change. Read first, write the plan, build, then check.
- **Evidence over assertion.** Show the test output, the command and what it returned, or the diff. Never say something works without showing it.
- **Tools:** few, specific, clearly described; return only high-signal results; page or filter large outputs.

## ERMOS rules

- The framework is locked (Decisions Log, 16 Oct 2026): Function → Capability → Workflow → Tool. When operations change, change the SOP, never the framework.
- How each engine is built: `managed-agents/BLUEPRINT.md`.
- Nothing another person reads is sent without Brad's approval (hq-approval-gate, Correspondence rule). Automations draft; Brad sends.
- Credit-spending tools always sit behind a gate.
- Brad is not technical: explain outcomes in plain English and decide technical details yourself.
