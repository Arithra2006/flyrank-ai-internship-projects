from datetime import datetime
from typing import Optional, List, Any, Dict

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------- Auth ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Widget ----------

class WidgetCreate(BaseModel):
    name: str
    widget_type: str = "contact_form"
    title: str = "Get in touch"
    description: str = ""
    button_text: str = "Submit"
    primary_color: str = "#4f46e5"
    fields: List[str] = ["name", "email", "message"]
    allowed_domains: List[str] = ["*"]


class WidgetUpdate(BaseModel):
    name: Optional[str] = None
    widget_type: Optional[str] = None
    is_active: Optional[bool] = None
    title: Optional[str] = None
    description: Optional[str] = None
    button_text: Optional[str] = None
    primary_color: Optional[str] = None
    fields: Optional[List[str]] = None
    allowed_domains: Optional[List[str]] = None


class WidgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    public_key: str
    name: str
    widget_type: str
    is_active: bool
    title: str
    description: str
    button_text: str
    primary_color: str
    fields: List[str]
    allowed_domains: List[str]
    created_at: datetime
    updated_at: datetime


class WidgetConfigOut(BaseModel):
    """Public-facing config served to the embedded script. No owner/internal info."""
    public_key: str
    widget_type: str
    title: str
    description: str
    button_text: str
    primary_color: str
    fields: List[str]
    is_active: bool


# ---------- Submission ----------

class SubmissionCreate(BaseModel):
    data: Dict[str, Any]
    # Honeypot field: must stay empty. Named innocuously; bots often fill every field.
    website: Optional[str] = ""


class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    widget_id: str
    data: Dict[str, Any]
    ip_address: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    is_spam: bool
    created_at: datetime


class SubmissionPublicOut(BaseModel):
    success: bool
    message: str


# ---------- Analytics ----------

class WidgetAnalytics(BaseModel):
    widget_id: str
    widget_name: str
    total_submissions: int
    spam_count: int
    submissions_by_country: Dict[str, int]
    submissions_last_7_days: Dict[str, int]


class DashboardSummary(BaseModel):
    total_widgets: int
    total_submissions: int
    total_spam_blocked: int
    widgets: List[WidgetAnalytics]
