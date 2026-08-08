import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "insecure-dev-key-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    allowed_origins: str = "*"
    public_base_url: str = "http://localhost:8000"
    submission_rate_limit: str = "5/minute"

    class Config:
        env_file = ".env"

    @property
    def allowed_origins_list(self):
        if self.allowed_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
