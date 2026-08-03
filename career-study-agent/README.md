# 🎯 Career & Study Prioritization Agent

An AI agent that turns your tasks, goals, deadlines, and available time into a
realistic, prioritized daily plan — built with Python, SQLite, Streamlit, and
the Anthropic Claude API (tool calling).

## Quick start

```bash
git clone <your-repository-url>
cd career-study-agent

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then edit .env and add your real API key

python database.py              # creates data/tasks.db and seeds example data

streamlit run app.py
```

Open the local URL Streamlit prints (usually `http://localhost:8501`).

## What's in here

| File | Purpose |
|---|---|
| `models.py` | Task / Goal / DailyPlan data models |
| `database.py` | SQLite schema + all read/write operations |
| `tools.py` | Tool schemas + dispatcher the LLM agent can call |
| `prompts.py` | System prompt encoding prioritization logic & guardrails |
| `agent.py` | Orchestration loop against the Anthropic Messages API |
| `app.py` | Streamlit UI |
| `tests/test_agent.py` | The 6 evaluation scenarios from the project spec |

## Configuration

Set `LLM_API_KEY` in `.env` to your Anthropic API key. Optionally override
the model via `AGENT_MODEL` (defaults to `claude-sonnet-4-6`).

## Safety notes

The agent can only read/update data in the local SQLite database via the
tools in `tools.py`. It cannot send messages, modify external accounts, make
purchases, or take any action outside this app. It's instructed to never
schedule more time than you say you have, and to ask for clarification
rather than guess when key info (like available time) is missing.

## Status

MVP — see `BUILD_LOG.md` for what's been tested vs. what still needs
verification against a live API key before you rely on it.
