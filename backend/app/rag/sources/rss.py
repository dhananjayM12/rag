"""RSS-based source connectors.

Parses standard RSS 2.0 feeds with the standard library (no extra deps). The
feed item's title + description is used as the document body — lightweight and
respectful of the source (no deep scraping).
"""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET

import httpx

from app.config import settings
from app.rag.sources.base import FetchedDoc, SourceConnector

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def strip_html(text: str) -> str:
    if not text:
        return ""
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return _WS_RE.sub(" ", text).strip()


def parse_rss(xml_text: str, source: str, limit: int | None = None) -> list[FetchedDoc]:
    """Parse an RSS 2.0 document into FetchedDocs."""
    docs: list[FetchedDoc] = []
    root = ET.fromstring(xml_text)
    items = root.findall(".//item")
    for item in items:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip() or None
        guid = (item.findtext("guid") or "").strip() or link or title
        pub = (item.findtext("pubDate") or "").strip() or None
        desc = strip_html(item.findtext("description") or "")
        if not title and not desc:
            continue
        body = f"{title}. {desc}".strip() if desc else title
        docs.append(
            FetchedDoc(
                source=source,
                external_id=guid,
                title=title or desc[:80],
                url=link,
                published_at=pub,
                body=body,
            )
        )
        if limit and len(docs) >= limit:
            break
    return docs


class RssConnector(SourceConnector):
    """Fetches and parses an RSS feed over HTTP."""

    def __init__(self, name: str, url: str) -> None:
        self.name = name
        self.url = url

    def fetch(self) -> list[FetchedDoc]:
        resp = httpx.get(
            self.url,
            timeout=settings.source_fetch_timeout,
            follow_redirects=True,
            headers={"User-Agent": "PrepPath/1.0 (+study-app)"},
        )
        resp.raise_for_status()
        return parse_rss(
            resp.text, self.name, limit=settings.source_max_items_per_feed
        )


class StaticRssConnector(SourceConnector):
    """Parses RSS from an in-memory string. Useful for tests / fixtures."""

    def __init__(self, name: str, xml_text: str) -> None:
        self.name = name
        self.xml_text = xml_text

    def fetch(self) -> list[FetchedDoc]:
        return parse_rss(self.xml_text, self.name)


def default_connectors() -> list[SourceConnector]:
    return [RssConnector(name, url) for name, url in settings.source_feed_list]
