"""
app.py
Streamlit interface for the Career & Study Prioritization Agent.

Run with:  streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv

import database as db
from agent import PrioritizationAgent

load_dotenv()

st.set_page_config(page_title="Career & Study Prioritization Agent", page_icon="🎯", layout="wide")

# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------

db.init_db()
db.mark_overdue_tasks()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []          # Anthropic-format message history
if "display_history" not in st.session_state:
    st.session_state.display_history = []        # simple (role, text) pairs for rendering
if "agent" not in st.session_state:
    st.session_state.agent = None
if "agent_error" not in st.session_state:
    st.session_state.agent_error = None

if st.session_state.agent is None and st.session_state.agent_error is None:
    try:
        st.session_state.agent = PrioritizationAgent()
    except Exception as e:
        st.session_state.agent_error = str(e)

# ---------------------------------------------------------------------------
# Sidebar: Tasks & Goals
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("📋 Tasks")
    tasks = db.get_tasks()
    if not tasks:
        st.caption("No tasks yet. Add one below.")
    for t in tasks:
        badge = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(t["priority"], "⚪")
        status_badge = {"Completed": "✅", "Overdue": "⚠️", "In Progress": "🔄", "Pending": ""}.get(t["status"], "")
        st.markdown(f"{badge} **{t['name']}** {status_badge}")
        st.caption(f"{t['category']} · due {t['deadline']} · {t['duration_minutes']}min · {t['status']}")

    with st.expander("➕ Add task"):
        with st.form("add_task_form", clear_on_submit=True):
            name = st.text_input("Task name")
            category = st.selectbox("Category", ["Internship", "Exam", "Technical", "Project", "Other"])
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            deadline = st.date_input("Deadline")
            duration = st.number_input("Duration (minutes)", min_value=5, max_value=600, value=60, step=5)
            description = st.text_area("Description (optional)")
            submitted = st.form_submit_button("Add task")
            if submitted and name:
                db.add_task(name, category, priority, str(deadline), int(duration), description=description)
                st.success(f"Added: {name}")
                st.rerun()

    st.divider()
    st.header("🎯 Goals")
    goals = db.get_goals()
    if not goals:
        st.caption("No goals yet. Add one below.")
    for g in goals:
        st.markdown(f"**{g['title']}**")
        st.progress(min(max(g["progress_percent"], 0), 100) / 100)
        st.caption(f"{g['progress_percent']}% · target {g['target_date'] or '—'}")

    with st.expander("➕ Add goal"):
        with st.form("add_goal_form", clear_on_submit=True):
            gtitle = st.text_input("Goal title")
            gdesc = st.text_area("Description (optional)")
            gtarget = st.date_input("Target date", key="goal_target")
            gsubmitted = st.form_submit_button("Add goal")
            if gsubmitted and gtitle:
                db.add_goal(gtitle, gdesc, str(gtarget))
                st.success(f"Added goal: {gtitle}")
                st.rerun()

# ---------------------------------------------------------------------------
# Main: Progress overview + Chat
# ---------------------------------------------------------------------------

st.title("🎯 Career & Study Prioritization Agent")
st.caption("Turn your goals and tasks into a realistic, prioritized action plan.")

col1, col2, col3, col4 = st.columns(4)
all_tasks = db.get_tasks()
completed = [t for t in all_tasks if t["status"] == "Completed"]
pending = [t for t in all_tasks if t["status"] == "Pending"]
overdue = [t for t in all_tasks if t["status"] == "Overdue"]
in_progress = [t for t in all_tasks if t["status"] == "In Progress"]

col1.metric("Completed", len(completed))
col2.metric("Pending", len(pending))
col3.metric("In Progress", len(in_progress))
col4.metric("Overdue", len(overdue))

st.divider()

if st.session_state.agent_error:
    st.error(
        f"Agent not available: {st.session_state.agent_error}\n\n"
        "Set LLM_API_KEY in your .env file (see .env.example) and reload this page."
    )
else:
    st.subheader("💬 Ask the agent")

    available_minutes = st.number_input(
        "Available time today (minutes)", min_value=0, max_value=1000, value=180, step=15
    )

    for role, text in st.session_state.display_history:
        with st.chat_message(role):
            st.markdown(text)

    user_input = st.chat_input(
        "e.g. What should I focus on today? / I finished the internship assignment."
    )

    if user_input:
        full_prompt = user_input
        if "available" not in user_input.lower() and "minute" not in user_input.lower():
            full_prompt = f"{user_input}\n\n(My available time today is {available_minutes} minutes.)"

        st.session_state.display_history.append(("user", user_input))
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = st.session_state.agent.chat(full_prompt, st.session_state.chat_history)
                    st.session_state.chat_history = result["history"]
                    st.markdown(result["reply"])
                    st.session_state.display_history.append(("assistant", result["reply"]))
                except Exception as e:
                    err = f"Something went wrong calling the agent: {e}"
                    st.error(err)
                    st.session_state.display_history.append(("assistant", err))

st.divider()
with st.expander("📊 Full task list"):
    if all_tasks:
        st.dataframe(
            [{k: t[k] for k in ("id", "name", "category", "priority", "deadline",
                                  "duration_minutes", "status")} for t in all_tasks],
            use_container_width=True,
        )
    else:
        st.caption("No tasks yet.")
