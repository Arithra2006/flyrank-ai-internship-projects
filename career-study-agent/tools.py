"""
tools.py
Tool definitions exposed to the LLM agent, and the dispatcher that executes
them against database.py.

Note on the Anthropic tool-calling format: each tool needs a `name`,
`description`, and JSON Schema `input_schema`. I built these against the
documented Anthropic Messages API tool-use format. If Anthropic has changed
this schema since my knowledge cutoff, verify against the current docs at
https://docs.claude.com before relying on it in production.
"""

import json
import database as db

# ---------------------------------------------------------------------------
# Tool schemas (Anthropic Messages API tool-use format)
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "get_tasks",
        "description": (
            "Get all tasks from the database, optionally filtered by status. "
            "Use this to see what the user has to do."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["Pending", "In Progress", "Completed", "Overdue"],
                    "description": "Optional filter. Omit to get all tasks.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_goals",
        "description": "Get all long-term goals stored for the user, including progress percent.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_deadlines",
        "description": (
            "Get non-completed tasks sorted by deadline, optionally limited to the "
            "next N days. Use this to understand urgency."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "within_days": {
                    "type": "integer",
                    "description": "Only return tasks due within this many days from today. Omit for all.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "update_task_status",
        "description": (
            "Update the status of a single task. Use this when the user reports "
            "progress (e.g. 'I finished X', 'I started Y'). Never guess a task_id — "
            "look it up via get_tasks first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "The id of the task to update."},
                "status": {
                    "type": "string",
                    "enum": ["Pending", "In Progress", "Completed", "Overdue"],
                },
            },
            "required": ["task_id", "status"],
        },
    },
    {
        "name": "save_daily_plan",
        "description": (
            "Persist a generated daily plan so it can be reviewed later. Call this "
            "only after presenting the plan to the user, not before."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "ISO date (YYYY-MM-DD) the plan is for."},
                "available_minutes": {"type": "integer"},
                "planned_task_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "IDs of tasks included in the plan, in priority order.",
                },
                "summary": {"type": "string", "description": "Short human-readable summary of the plan."},
            },
            "required": ["date", "available_minutes", "planned_task_ids"],
        },
    },
]


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def execute_tool(name: str, tool_input: dict) -> str:
    """Execute a tool call by name and return a JSON string result.

    Any exception is caught and returned as a JSON error object so the LLM
    can see what went wrong rather than the app crashing.
    """
    try:
        if name == "get_tasks":
            result = db.get_tasks(status=tool_input.get("status"))
        elif name == "get_goals":
            result = db.get_goals()
        elif name == "get_deadlines":
            result = db.get_deadlines(within_days=tool_input.get("within_days"))
        elif name == "update_task_status":
            db.update_task_status(tool_input["task_id"], tool_input["status"])
            result = {"success": True, "task_id": tool_input["task_id"], "status": tool_input["status"]}
        elif name == "save_daily_plan":
            plan_id = db.save_daily_plan(
                tool_input["date"],
                tool_input["available_minutes"],
                tool_input["planned_task_ids"],
                tool_input.get("summary", ""),
            )
            result = {"success": True, "plan_id": plan_id}
        else:
            result = {"error": f"Unknown tool: {name}"}
        return json.dumps(result, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})
