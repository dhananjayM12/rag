from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, read from environment / .env."""

    database_url: str = "postgresql+psycopg2://upsc:upsc@localhost:5432/upsc"
    cors_origins: str = "http://localhost:3000"
    embed_dim: int = 384

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
