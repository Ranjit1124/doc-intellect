import os
from dataclasses import dataclass


@dataclass
class Settings:
    auth_db: str = os.getenv("AUTH_DB", "auth.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-please")
    supabase_url: str | None = os.getenv("SUPABASE_URL")
    supabase_key: str | None = os.getenv("SUPABASE_KEY")
    frontend_url: str | None = os.getenv("FRONTEND_URL")
    google_client_id: str | None = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: str | None = os.getenv("GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str | None = os.getenv("GOOGLE_REDIRECT_URI")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))


settings = Settings()
