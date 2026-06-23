from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, read from environment / .env."""

    database_url: str = "postgresql+psycopg2://upsc:upsc@localhost:5432/upsc"
    cors_origins: str = "http://localhost:3000"
    embed_dim: int = 384

    # RAG configuration (all local / open by default).
    # embedding_backend: "hashing" (zero-dependency, fully local) or
    # "sentence-transformers" (better quality; lazily imported).
    embedding_backend: str = "hashing"
    embedding_model: str = "intfloat/multilingual-e5-small"
    # llm_backend: "extractive" (no model, returns grounded source text) or
    # "ollama" (local LLM via HTTP).
    llm_backend: str = "extractive"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    rag_top_k: int = 4

    # Official-source ingestion (RSS feeds; official/open sources only).
    # Comma-separated "Name|url" pairs. Run `python -m app.rag.ingest_sources`.
    source_feeds: str = (
        "PIB|https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3,"
        "PRS|https://prsindia.org/rss.xml"
    )
    source_fetch_timeout: int = 20
    source_max_items_per_feed: int = 40

    @property
    def source_feed_list(self) -> list[tuple[str, str]]:
        pairs: list[tuple[str, str]] = []
        for entry in self.source_feeds.split(","):
            entry = entry.strip()
            if "|" in entry:
                name, url = entry.split("|", 1)
                pairs.append((name.strip(), url.strip()))
        return pairs

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
