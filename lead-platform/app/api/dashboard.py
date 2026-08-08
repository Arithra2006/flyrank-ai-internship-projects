from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, Widget, Submission
from app.schemas.schemas import DashboardSummary, WidgetAnalytics, SubmissionOut

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


def _build_widget_analytics(widget: Widget) -> WidgetAnalytics:
    submissions = widget.submissions
    total = len(submissions)
    spam = sum(1 for s in submissions if s.is_spam)

    by_country = defaultdict(int)
    for s in submissions:
        if s.country:
            by_country[s.country] += 1

    last_7 = defaultdict(int)
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    for s in submissions:
        created = s.created_at
        if created and created.replace(tzinfo=timezone.utc) >= cutoff:
            day_key = created.strftime("%Y-%m-%d")
            last_7[day_key] += 1

    return WidgetAnalytics(
        widget_id=widget.id,
        widget_name=widget.name,
        total_submissions=total,
        spam_count=spam,
        submissions_by_country=dict(by_country),
        submissions_last_7_days=dict(last_7),
    )


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widgets = db.query(Widget).filter(Widget.owner_id == current_user.id).all()

    analytics = [_build_widget_analytics(w) for w in widgets]
    total_submissions = sum(a.total_submissions for a in analytics)
    total_spam = sum(a.spam_count for a in analytics)

    return DashboardSummary(
        total_widgets=len(widgets),
        total_submissions=total_submissions,
        total_spam_blocked=total_spam,
        widgets=analytics,
    )


@router.get("/widgets/{widget_id}/submissions", response_model=List[SubmissionOut])
def get_widget_submissions(
    widget_id: str,
    include_spam: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widget = db.query(Widget).filter(Widget.id == widget_id).first()
    if not widget or widget.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Widget not found")

    query = db.query(Submission).filter(Submission.widget_id == widget_id)
    if not include_spam:
        query = query.filter(Submission.is_spam == False)  # noqa: E712

    return query.order_by(Submission.created_at.desc()).all()


@router.get("/widgets/{widget_id}/analytics", response_model=WidgetAnalytics)
def get_widget_analytics(
    widget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widget = db.query(Widget).filter(Widget.id == widget_id).first()
    if not widget or widget.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Widget not found")

    return _build_widget_analytics(widget)
