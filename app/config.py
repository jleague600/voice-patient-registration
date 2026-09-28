from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database settings.
    # Use Supabase's connection pooler URL (port 6543), not the direct DB URL.
    # This helps avoid connection issues in serverless hosting.
    database_url: str

    # Vapi keys are used to check that calls are really coming from Vapi.
    vapi_api_key: str = ""
    vapi_webhook_secret: str = ""

    # App mode and log level.
    environment: str = "development"  # "development" | "production"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# This is the object we use everywhere to get env values like DB URL and keys.
settings = Settings()