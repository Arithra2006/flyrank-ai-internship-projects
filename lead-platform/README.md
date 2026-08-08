# Embeddable Widget & Lead-Capture Platform

A backend system for creating embeddable lead-capture widgets (contact forms,
signup forms, popups) that any website can embed with a single `<script>` tag.

## Stack

- FastAPI + SQLAlchemy + Pydantic
- JWT auth (python-jose) + bcrypt password hashing (passlib)
- SlowAPI for rate limiting
- SQLite for local dev, PostgreSQL for production (swap via `DATABASE_URL`)
- Vanilla JS embeddable widget loader + minimal HTML/CSS/JS dashboard

## Project Structure

```
app/
  core/         config, database session, security (JWT/bcrypt), rate limiter, auth dependency
  models/       SQLAlchemy models: User, Widget, Submission
  schemas/      Pydantic request/response schemas
  api/          route modules: auth, widgets, public, dashboard
  services/     geo enrichment (IP -> location), embed script generator
  static/       widget.js (embeddable loader) + index.html (dashboard)
  main.py       FastAPI app, CORS, router wiring
requirements.txt
Dockerfile
docker-compose.yml
.env.example
postman_collection.json
```

## Quick Start (local, SQLite)

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # defaults already use SQLite, fine for local dev

uvicorn app.main:app --reload
```

Then open:
- API docs (Swagger): http://localhost:8000/docs
- Dashboard: http://localhost:8000/dashboard/
- Health check: http://localhost:8000/health

## Quick Start (Docker, PostgreSQL)

```bash
docker-compose up --build
```

This starts the API on `:8000` and a Postgres container on `:5432`. Tables
are created automatically on startup via `Base.metadata.create_all` — this
is fine for development but for a real production rollout you'd want to
switch to Alembic migrations instead.

## Using the Platform

1. **Register / log in** via the dashboard at `/dashboard/`, or via the API
   (`POST /api/auth/register`, `POST /api/auth/login`).
2. **Create a widget** — set title, description, button text, color, and
   which fields to collect (`name`, `email`, `message`, `phone`, `company`).
3. Copy the generated **embed code**, e.g.:
   ```html
   <script src="http://localhost:8000/widget.js" data-widget-key="YOUR_KEY" async></script>
   ```
4. Paste that one line into any HTML page. The script:
   - Fetches the widget's config from `/api/public/widgets/{key}/config`
   - Renders a styled form
   - Submits to `/api/public/widgets/{key}/submit` on form submit
5. **View submissions and analytics** back in the dashboard.

## Security Notes

- **Multi-tenancy**: every widget/submission query is scoped to
  `owner_id == current_user.id`. Attempting to access another user's widget
  returns 404 (not 403), so ownership isn't leaked.
- **Spam protection**: a honeypot field (`website`) is invisible to real
  users (positioned off-screen, not `display:none`) but often auto-filled
  by bots. Submissions with it filled are flagged `is_spam=true` and hidden
  from default dashboard views, but still return a success response so bots
  don't learn to adapt.
- **Rate limiting**: the public submission endpoint is rate-limited per IP
  (`SUBMISSION_RATE_LIMIT` in `.env`, default `5/minute`) via SlowAPI.
- **Input validation**: only fields declared on the widget (`widget.fields`)
  are accepted; anything else in the payload is silently dropped, not stored.
- **Domain allowlisting**: each widget has `allowed_domains` (default `["*"]`).
  If restricted, submissions are checked against the request's Origin/Referer
  header and rejected with 403 if it doesn't match.
- **CORS**: configured broadly (`ALLOWED_ORIGINS`) because the whole point of
  an embeddable widget is that it's called from arbitrary customer domains —
  the actual security boundary is the per-widget domain allowlist above, not CORS.

## Geo Enrichment

`app/services/geo.py` resolves the submitter's IP to country/region/city using
`ip-api.com` as primary and `ipapi.co` as fallback if the primary fails or
times out. Private/local IPs (127.x, 192.168.x, 10.x, etc.) are skipped
automatically since they can't be geolocated.

> **Note:** I have not independently verified the current live JSON response
> schemas of ip-api.com and ipapi.co at the time you read this — free
> third-party API response formats and rate limits can change without notice.
> Test a real submission and check the `geo_source` field on the resulting
> record; if country/city come back null, check each provider's current docs
> (ip-api.com/docs, ipapi.co/api) and adjust the field names in `geo.py`
> accordingly.

## Environment Variables (`.env`)

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./app.db` |
| `SECRET_KEY` | JWT signing secret — **change before deploying** | dev placeholder |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiry | `60` |
| `ALLOWED_ORIGINS` | CORS origins, comma-separated or `*` | `*` |
| `PUBLIC_BASE_URL` | Used to generate the embed `<script>` tag | `http://localhost:8000` |
| `SUBMISSION_RATE_LIMIT` | SlowAPI rate limit string | `5/minute` |

## Testing with Postman

Import `postman_collection.json`. Set the `base_url` variable, run
Register → Login (copy `access_token` into the `token` variable), then
Create Widget (copy `id` into `widget_id` and `public_key` into
`widget_public_key`) to exercise the rest of the collection.

## What's Deliberately Left as a Next Step

To keep this a working, runnable deliverable rather than an over-scoped
one, a few items from the original spec are stubbed or omitted and noted
here rather than silently skipped:

- **Confirmation email/webhook on submission** — not implemented. Wiring
  this up needs a real email provider (SendGrid/SES/etc.) or webhook URL
  field on the widget, which needs a decision from you on which provider
  you want.
- **DB migrations** — tables are created via `create_all()` for simplicity.
  For a production Postgres setup, add Alembic.
- **Frontend build tooling** — the dashboard is intentionally plain
  HTML/CSS/JS (no React/build step) to match the spec's listed frontend
  stack and keep the deliverable self-contained.
