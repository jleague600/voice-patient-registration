from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Database ---
    # Use Supabase's CONNECTION POOLER string (port 6543), not the direct
    # connection (port 5432). Vercel's serverless functions open a new
    # connection per invocation, and the direct connection limit on
    # Supabase's free tier will be exhausted almost immediately otherwise.
    # Format: postgresql+asyncpg://user:password@host:6543/postgres
    database_url: str

    # --- Voice agent / Vapi ---
    # Used to verify that incoming tool-call webhooks actually come from
    # Vapi and not an arbitrary caller of our public API.
    vapi_api_key: str = ""
    vapi_webhook_secret: str = ""

    # --- App behavior ---
    environment: str = "development"  # "development" | "production"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Single shared instance — import this, don't instantiate Settings() elsewhere.
settings = Settings()