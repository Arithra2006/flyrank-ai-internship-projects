# FlyRank Portfolio — AI Career Study Agent

A personal portfolio website with a working AI feature: an AI Career Study
Agent powered by Groq's free API, built with a Flask backend.

---

## 1. Project structure

```
flyrank-portfolio/
├── app.py                  ← Flask backend (this runs the server + AI calls)
├── requirements.txt        ← Python packages needed
├── Procfile                ← tells Render how to run the app
├── .env.example            ← copy this to .env and add your real API key
├── .gitignore
├── templates/
│   └── index.html          ← the webpage itself
└── static/
    ├── css/style.css
    ├── js/main.js
    ├── images/
    │   ├── favicon.ico     ← placeholder, replace with your own
    │   └── flyrank-badge.png ← placeholder, replace with your real badge
    └── resume.pdf          ← placeholder, replace with your real resume
```

---

## 2. Where to put your Groq API key

1. Get a free key at **https://console.groq.com/keys** (sign up, then create a key).
2. In the project folder, make a copy of `.env.example` and rename it to **`.env`**.
3. Open `.env` and paste your key:

```
GROQ_API_KEY=gsk_your_real_key_here
```

4. Save the file. **Never** commit `.env` to GitHub — `.gitignore` already
   excludes it, but double-check before pushing.

The backend (`app.py`) reads this automatically via `python-dotenv`. You
never need to paste the key directly into any code file.

---

## 3. How to run it locally (VS Code)

Open a terminal inside the project folder and run:

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Make sure your .env file exists with your GROQ_API_KEY (see step 2 above)

# 5. Run the server
python app.py
```

Then open your browser to **http://127.0.0.1:5000** — you should see the
full portfolio. Fill in the AI Career Study Agent form and click
"Generate Career Roadmap" to test it live.

If you get an error about a missing module, re-run
`pip install -r requirements.txt`.

If you get an error saying the AI request failed, double check:
- Your `.env` file exists and has the correct key with no extra spaces/quotes.
- Your Groq account key hasn't expired or hit its free-tier limit — check
  the current limits at Groq's docs, since these can change.

---

## 4. Customize before deploying

- Replace `static/resume.pdf` with your real resume.
- Replace `static/images/favicon.ico` with a real favicon.
- Replace `static/images/flyrank-badge.png` with the real FlyRank badge
  once you receive it, and update the verification link in
  `templates/index.html` (search for `flyrank.com/verify`).
- Edit the "Your Name", About, Skills, and Projects sections in
  `templates/index.html`.
- In `templates/index.html`, replace `G-XXXXXXXXXX` (two places) with your
  real Google Analytics Measurement ID once you set up GA4.

---

## 5. Deployment

### Backend → Render (free tier)
1. Push this project to a GitHub repository.
2. Go to **render.com** → New → Web Service → connect your GitHub repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add an environment variable in Render's dashboard:
   - Key: `GROQ_API_KEY`
   - Value: your real key
6. Deploy. Render will give you a URL like `https://your-app.onrender.com`.

### Frontend → same Flask app, or split it out
Since `app.py` already serves `templates/index.html` directly, the simplest
path is to deploy this whole project to Render as one app — you don't
strictly need a separate frontend host.

If you prefer to host the frontend separately (GitHub Pages / Vercel /
Netlify) and keep only the API on Render:
1. Move `templates/index.html` content into a standalone `index.html` at
   your frontend repo's root, and copy the `static/` folder alongside it.
2. In `static/js/main.js`, set:
   ```js
   const BACKEND_URL = "https://your-app.onrender.com";
   ```
3. Deploy the frontend folder to Vercel/Netlify/GitHub Pages.

### Custom domain (Week 9)
Follow your host's "custom domain" settings (Vercel/Netlify/Render all have
a Domains tab) and point your domain's DNS records as instructed there —
this differs by registrar, so use their current documentation rather than
guesswork.

### HTTPS
Render, Vercel, GitHub Pages, and Netlify all provision free HTTPS
certificates automatically once your domain is connected — no extra setup
needed on your end.

---

## 6. Backend data flow (for your report)

1. User fills out the Career Study form and clicks "Generate."
2. `main.js` sends a POST request with the form data (as JSON) to
   `/career-advice` on the Flask backend.
3. `app.py` builds a prompt from that data and sends it to the Groq API
   using the `groq` Python SDK.
4. Groq's AI model generates a personalized roadmap and returns it.
5. `app.py` sends that text back to the browser as JSON.
6. `main.js` displays it inside the result box on the page.

The `/contact` endpoint works similarly but simply saves submissions to
`contacts.json` on the server (see the note in `app.py` about swapping
this for real email delivery in production).

---

## 7. A note on accuracy

- Model name (`llama-3.3-70b-versatile`) and library versions in
  `requirements.txt` reflect what was current at the time this was built —
  Groq updates its available models periodically, so if you get a "model
  not found" error, check **https://console.groq.com/docs/models** for
  the current list and update the `GROQ_MODEL` variable in `app.py`.
- Google Analytics setup steps and Render/Vercel UI details can change;
  follow the current on-screen instructions on those sites if anything
  here looks different from what you see.
