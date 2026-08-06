"""
FlyRank Portfolio Backend
--------------------------
Flask backend serving the portfolio frontend and powering the
AI Career Study Agent using the Groq API.

WHERE TO PUT YOUR GROQ API KEY:
Create a file named ".env" in this same folder (next to app.py) with:

    GROQ_API_KEY=your_actual_key_here

Do NOT put the key directly in this file, and do NOT commit the .env
file to GitHub (a .gitignore is included to prevent that).
"""

import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# Load variables from .env into the environment
load_dotenv()

app = Flask(__name__)
CORS(app)  # allows the frontend (even if hosted elsewhere) to call this backend

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY is not set. Create a .env file with your key.")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# NOTE: Groq periodically changes which models are available/free.
# Check https://console.groq.com/docs/models for the current list
# and swap this string if this model becomes unavailable.
GROQ_MODEL = "llama-3.3-70b-versatile"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/career-advice", methods=["POST"])
def career_advice():
    if client is None:
        return jsonify({"error": "Server is missing a GROQ_API_KEY. Check the .env file."}), 500

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    degree = data.get("degree", "").strip()
    year = data.get("year", "").strip()
    goal = data.get("goal", "").strip()
    skills = data.get("skills", "").strip()
    questions = data.get("questions", "").strip()

    if not degree or not year or not goal:
        return jsonify({"error": "Degree, year of study, and career goal are required."}), 400

    user_label = name if name else "the student"

    prompt = f"""You are a career guidance counselor for students. Based on the details below,
write a clear, well-organized, personalized career plan.

Student details:
- Name: {name or "Not provided"}
- Current degree: {degree}
- Year of study: {year}
- Career goal: {goal}
- Current skills: {skills or "Not specified"}
- Specific questions: {questions or "None"}

Please structure your response with these clear sections, using plain text headers
(not markdown symbols):

1. CAREER ROADMAP - a realistic step-by-step path from where {user_label} is now to the goal of {goal}.
2. SKILLS TO LEARN - a prioritized list of skills, ordered by importance.
3. RECOMMENDED PROJECTS - 3 to 5 concrete project ideas suited to their current level.
4. RESOURCES - specific types of resources to use (courses, books, communities). If you are not
   fully certain a specific course or book currently exists or is still available, describe the
   type of resource instead of inventing a specific title.
5. INTERVIEW PREPARATION TIPS - practical tips relevant to their target role.

If the student asked a specific question, answer it directly in a final section titled
ANSWER TO YOUR QUESTION.

Keep the tone encouraging but realistic. Keep the whole response under 500 words.
"""

    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200,
        )
        advice = completion.choices[0].message.content
        return jsonify({"advice": advice})

    except Exception as e:
        # Surface a readable error instead of a raw stack trace
        return jsonify({"error": f"AI request failed: {str(e)}"}), 500


@app.route("/contact", methods=["POST"])
def contact():
    """
    Stores contact form submissions to a local JSON file (contacts.json).
    For production, you may prefer to wire this up to an email service
    (e.g. Flask-Mail with an SMTP provider, or a form service like Formspree)
    instead of storing to a local file, since Render's free tier filesystem
    is not guaranteed to persist across restarts.
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({"error": "Name, email, and message are all required."}), 400

    entry = {"name": name, "email": email, "message": message}

    file_path = os.path.join(os.path.dirname(__file__), "contacts.json")
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                contacts = json.load(f)
        else:
            contacts = []
        contacts.append(entry)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=2)
    except Exception as e:
        return jsonify({"error": f"Could not save message: {str(e)}"}), 500

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Debug mode is fine for local development; Render will use its own
    # production server command (see Procfile).
    app.run(debug=True, port=5000)
