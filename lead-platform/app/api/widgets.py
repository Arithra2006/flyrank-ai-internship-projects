from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, Widget
from app.schemas.schemas import WidgetCreate, WidgetUpdate, WidgetOut
from app.services.embed import generate_embed_snippet

router = APIRouter(prefix="/api/widgets", tags=["Widgets"])


def _get_owned_widget(widget_id: str, user: User, db: Session) -> Widget:
    widget = db.query(Widget).filter(Widget.id == widget_id).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    if widget.owner_id != user.id:
        # 404 instead of 403 to avoid leaking existence of other users' widgets
        raise HTTPException(status_code=404, detail="Widget not found")
    return widget


@router.post("", response_model=WidgetOut, status_code=status.HTTP_201_CREATED)
def create_widget(
    widget_in: WidgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widget = Widget(owner_id=current_user.id, **widget_in.model_dump())
    db.add(widget)
    db.commit()
    db.refresh(widget)
    return widget


@router.get("", response_model=List[WidgetOut])
def list_widgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Widget).filter(Widget.owner_id == current_user.id).all()


@router.get("/{widget_id}", response_model=WidgetOut)
def get_widget(
    widget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_owned_widget(widget_id, current_user, db)


@router.put("/{widget_id}", response_model=WidgetOut)
def update_widget(
    widget_id: str,
    widget_in: WidgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widget = _get_owned_widget(widget_id, current_user, db)
    for field, value in widget_in.model_dump(exclude_unset=True).items():
        setattr(widget, field, value)
    db.commit()
    db.refresh(widget)
    return widget


@router.delete("/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_widget(
    widget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widget = _get_owned_widget(widget_id, current_user, db)
    db.delete(widget)
    db.commit()
    return None


@router.get("/{widget_id}/embed-code")
def get_embed_code(
    widget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widget = _get_owned_widget(widget_id, current_user, db)
    return {"embed_code": generate_embed_snippet(widget.public_key)}
