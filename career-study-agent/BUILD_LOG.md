# Build Log

## Build 1 — Initial MVP (2026-08-01)

Built the full MVP in one pass per the project spec:

- `models.py` — dataclasses for Task, Goal, DailyPlan (no ORM dependency, kept it
  lightweight against raw sqlite3).
- `database.py` — schema + CRUD functions, `mark_overdue_tasks()` to keep status
  honest based on real dates rather than letting the LLM guess overdue state,
  `seed_example_data()` with illustrative placeholder tasks/goals matching the
  spec's examples.
- `tools.py` — 5 tools matching the spec (`get_tasks`, `get_goals`,
  `get_deadlines`, `update_task_status`, `save_daily_plan`), built against the
  documented Anthropic Messages API tool-use schema (name/description/input_schema).
- `prompts.py` — system prompt encoding the prioritization rules (deadline,
  priority, goal alignment, time budget) and the hard constraints from the
  spec's Safety & Guardrails section (never overschedule, never take
  irreversible actions, ask instead of assuming).
- `agent.py` — orchestration loop using the Anthropic Python SDK
  (`anthropic.Anthropic().messages.create`), looping on `stop_reason ==
  "tool_use"` until the model returns a final text response or a max
  iteration cap is hit.
- `app.py` — Streamlit UI: sidebar for tasks/goals + add-forms, metrics for
  progress tracking, chat interface for natural-language planning/updates.
- `tests/test_agent.py` — the 6 evaluation scenarios from the spec, as a
  runnable harness (not pre-verified against a live API key in this build
  environment — see note below).

### Known verification gaps (be aware before relying on this in production)

- I do not have network access in the sandbox that built this, so I could
  **not** run `agent.py` or `app.py` against a live Anthropic API key. The
  database layer (`database.py`) and tool dispatcher (`tools.py`) *were*
  functionally tested end-to-end (seeding, querying, status updates,
  overdue-marking, plan saving) and work correctly.
- The Anthropic SDK tool-calling loop in `agent.py` is written against the
  documented Messages API format I'm confident in (system/tools/messages
  params, `stop_reason == "tool_use"`, `tool_result` blocks keyed by
  `tool_use_id`). Verify against https://docs.claude.com if you hit any
  SDK errors, since SDK method signatures can change between versions.
- Default model is set to `claude-sonnet-4-6`, confirmed via a live doc
  search as the current recommended production default at build time
  (Aug 2026). Model naming changes over time — re-check
  https://docs.claude.com/en/docs/about-claude/models/overview periodically.
- I fixed one real bug found during testing: `update_task_status` on a
  non-existent task ID originally succeeded silently (SQLite doesn't error
  on a zero-row UPDATE). It now raises a clear error so the agent doesn't
  report a false success to the user.
- `tests/test_agent.py` scenarios are written to match the spec's 6 cases
  but have **not** been run against the live LLM — treat them as a starting
  harness, and manually review the printed output the first time you run
  them, per the checklist at the bottom of that file.

### Design decisions worth flagging

- Chose raw `sqlite3` over an ORM to keep the dependency footprint small.
- `mark_overdue_tasks()` runs automatically at the start of every agent
  turn and on Streamlit page load, so "Overdue" status is always derived
  from the real system date rather than something the LLM has to compute
  or that could drift.
- The agent is instructed to always call `get_tasks`/`get_goals` before
  reasoning, rather than trusting anything in prior conversation turns,
  so it doesn't drift from the actual database state over a long session.
