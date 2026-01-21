from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="env", env_file_encoding="utf-8")

    app_env: str = "dev"
    app_origin: str = "http://localhost:3000"

    # Keep defaults empty so the app can import/start without env during early dev.
    # Endpoints that require these values should fail with a clear error if missing.
    supabase_url: str = ""
    supabase_anon_key: str | None = None
    supabase_service_role_key: str = ""
    supabase_jwks_url: str = ""

    groq_api_key: str = ""
    groq_model: str = "llama-3.1-70b-versatile"

    redis_url: str = "redis://localhost:6379/0"


settings = Settings()

