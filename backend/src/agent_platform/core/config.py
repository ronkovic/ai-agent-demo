"""アプリケーション設定."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # アプリケーション設定
    app_name: str = "Agent Platform"
    debug: bool = False

    # CORS設定
    cors_origins: list[str] = ["http://localhost:3000"]

    # データベース設定
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/agent_platform"

    # Supabase設定
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # LLM設定
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-northeast-1"

    # A2A設定
    a2a_base_url: str = "http://localhost:8000"

    # 暗号化設定（開発用Fernet暗号化キー）
    encryption_key: str = ""

    # Celery設定
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"


@lru_cache
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得."""
    return Settings()


settings = get_settings()
