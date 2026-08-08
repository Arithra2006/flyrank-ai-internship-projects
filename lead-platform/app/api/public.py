from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.models import Widget, Submission
from app.schemas.schemas import WidgetConfigOut, SubmissionCreate, SubmissionPublicOut
from app.services.geo import resolve_geo
from app.core.limiter import limiter

router = APIRouter(prefix="/api/public", tags=["Public"])


def _get_client_ip(request: Request) -> str:
    # Respect X-Forwarded-For if behind a proxy/load balancer (first IP in the chain).
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""


def _domain_allowed(widget: Widget, origin_or_referrer: str) -> bool:
    allowed = widget.allowed_domains or ["*"]
    if "*" in allowed:
        return True
    if not origin_or_referrer:
        return False
    return any(domain in origin_or_referrer for domain in allowed)


@router.get("/widgets/{public_key}/config", response_model=WidgetConfigOut)
def get_widget_config(public_key: str, db: Session = Depends(get_db)):
    """
    Fetched by the embedded JS loader to render the widget dynamically.
    """
    widget = db.query(Widget).filter(Widget.public_key == public_key).first()
    if not widget or not widget.is_active:
        raise HTTPException(status_code=404, detail="Widget not found or inactive")
    return widget


@router.post(
    "/widgets/{public_key}/submit",
    response_model=SubmissionPublicOut,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(settings.submission_rate_limit)
async def submit_lead(
    public_key: str,
    submission_in: SubmissionCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    widget = db.query(Widget).filter(Widget.public_key == public_key).first()
    if not widget or not widget.is_active:
        raise HTTPException(status_code=404, detail="Widget not found or inactive")

    origin = request.headers.get("origin") or request.headers.get("referer") or ""
    if not _domain_allowed(widget, origin):
        raise HTTPException(status_code=403, detail="Submissions from this domain are not allowed")

    # --- Input validation: only accept fields the widget actually declares ---
    allowed_fields = set(widget.fields or [])
    cleaned_data = {k: v for k, v in submission_in.data.items() if k in allowed_fields}
    if not cleaned_data:
        raise HTTPException(status_code=422, detail="No valid fields submitted")

    # --- Honeypot spam check ---
    # "website" field is invisible to real users (hidden via CSS in the widget)
    # but bots that auto-fill every input will populate it.
    is_spam = bool(submission_in.website and submission_in.website.strip())

    ip = _get_client_ip(request)
    geo = await resolve_geo(ip)

    submission = Submission(
        widget_id=widget.id,
        data=cleaned_data,
        ip_address=ip,
        user_agent=request.headers.get("user-agent"),
        referrer=origin,
        country=geo["country"],
        region=geo["region"],
        city=geo["city"],
        geo_source=geo["source"],
        is_spam=is_spam,
    )
    db.add(submission)
    db.commit()

    if is_spam:
        # Still return success to the bot so it doesn't learn to adapt,
        # but the lead is flagged and hidden from default dashboard views.
        return SubmissionPublicOut(success=True, message="Submission received.")

    return SubmissionPublicOut(success=True, message="Thank you! Your submission was received.")
