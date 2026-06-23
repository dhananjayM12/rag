"""Source connector interface for official-source ingestion."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FetchedDoc:
    source: str
    external_id: str  # stable id for de-duplication (guid or url)
    title: str
    url: str | None
    published_at: str | None
    body: str


class SourceConnector:
    """Fetches documents from one official/open source."""

    name: str = "source"

    def fetch(self) -> list[FetchedDoc]:  # pragma: no cover - interface
        raise NotImplementedError
