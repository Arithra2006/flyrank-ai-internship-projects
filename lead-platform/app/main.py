from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.core.config import settings
from app.core.database import Base, engine
from app.core.limiter import limiter
from app.api import auth, widgets, public, dashboard

# Create tables (for dev/SQLite; use Alembic migrations for production Postgres)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Embeddable Widget & Lead-Capture Platform",
    description="Backend API for creating embeddable lead-capture widgets.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS: public submission endpoints need to accept cross-origin requests
# from arbitrary customer websites embedding the widget.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(widgets.router)
app.include_router(public.router)
app.include_router(dashboard.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.get("/widget.js", tags=["Widget Loader"])
def serve_widget_js():
    """
    The single script customers embed. Served as static JS which then
    calls back to /api/public/widgets/{key}/config to render itself.
    """
    return FileResponse("app/static/widget.js", media_type="application/javascript")


app.mount("/dashboard", StaticFiles(directory="app/static", html=True), name="dashboard")
