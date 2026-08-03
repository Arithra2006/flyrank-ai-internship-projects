"""
agent.py
Agent orchestration: wraps the Anthropic Messages API tool-use loop.

Built against the documented `anthropic` Python SDK (pip install anthropic).
I have not executed this against a live API key in this environment, so
please verify the SDK call signatures against current docs
(https://docs.claude.com) if you hit any errors — SDKs do change.
"""

import os
import json
from typing import List, Dict, Any

from anthropic import Anthropic

from tools import TOOLS, execute_tool
from prompts import SYSTEM_PROMPT
import database as db

MODEL_NAME = os.environ.get("AGENT_MODEL", "claude-sonnet-4-6")
MAX_TOOL_ITERATIONS = 6


class PrioritizationAgent:
    def __init__(self, api_key: str = None):
        api_key = api_key or os.environ.get("LLM_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "No API key found. Set LLM_API_KEY (or ANTHROPIC_API_KEY) in your .env file."
            )
        self.client = Anthropic(api_key=api_key)

    def chat(self, user_message: str, history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run one turn of conversation. `history` is a list of prior
        {"role": ..., "content": ...} messages (Anthropic format).
        Returns {"reply": str, "history": updated_history}.
        """
        db.mark_overdue_tasks()  # keep statuses honest before the agent reasons about them

        messages = list(history) if history else []
        messages.append({"role": "user", "content": user_message})

        final_text_parts = []

        for _ in range(MAX_TOOL_ITERATIONS):
            response = self.client.messages.create(
                model=MODEL_NAME,
                max_tokens=1500,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            # Collect any text produced this turn
            for block in response.content:
                if block.type == "text":
                    final_text_parts.append(block.text)

            if response.stop_reason != "tool_use":
                # No more tool calls requested — we're done.
                messages.append({"role": "assistant", "content": response.content})
                break

            # Model wants to use one or more tools. Append its turn, then
            # append our tool results, then loop again.
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result_json = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_json,
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            final_text_parts.append(
                "\n[Note: reached the maximum number of tool calls for this turn. "
                "Ask me to continue if you need more.]"
            )

        reply = "\n".join(p for p in final_text_parts if p.strip())
        return {"reply": reply, "history": messages}
