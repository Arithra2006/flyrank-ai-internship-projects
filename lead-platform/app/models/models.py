import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    widgets = relationship("Widget", back_populates="owner", cascade="all, delete-orphan")


class Widget(Base):
    __tablename__ = "widgets"

    id = Column(String, primary_key=True, default=gen_uuid)
    public_key = Column(String, unique=True, index=True, default=gen_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    widget_type = Column(String, default="contact_form")  # contact_form, signup, popup
    is_active = Column(Boolean, default=True)

    # Widget appearance/behavior config, stored as JSON
    title = Column(String, default="Get in touch")
    description = Column(String, default="")
    button_text = Column(String, default="Submit")
    primary_color = Column(String, default="#4f46e5")
    fields = Column(JSON, default=lambda: ["name", "email", "message"])

    # Allowed domains that may embed/submit this widget. "*" allows any.
    allowed_domains = Column(JSON, default=lambda: ["*"])

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    owner = relationship("User", back_populates="widgets")
    submissions = relationship("Submission", back_populates="widget", cascade="all, delete-orphan")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=gen_uuid)
    widget_id = Column(String, ForeignKey("widgets.id"), nullable=False)

    data = Column(JSON, nullable=False)  # arbitrary form fields submitted

    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    referrer = Column(String, nullable=True)

    country = Column(String, nullable=True)
    region = Column(String, nullable=True)
    city = Column(String, nullable=True)
    geo_source = Column(String, nullable=True)  # which API/fallback resolved it

    is_spam = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    widget = relationship("Widget", back_populates="submissions")
