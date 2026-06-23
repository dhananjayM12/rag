import pytest

from app.rag import ingest, ingest_sources
from app.rag.sources.rss import StaticRssConnector, parse_rss, strip_html

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>PIB Test Feed</title>
    <item>
      <title>Cabinet approves National Quantum Mission</title>
      <link>https://pib.gov.in/news/quantum</link>
      <guid>pib-quantum-001</guid>
      <pubDate>Mon, 23 Jun 2026 10:00:00 +0530</pubDate>
      <description>&lt;p&gt;The Union Cabinet approved the National Quantum
      Mission to boost quantum technology research and development.&lt;/p&gt;</description>
    </item>
    <item>
      <title>India launches new monsoon forecasting system</title>
      <link>https://pib.gov.in/news/monsoon</link>
      <guid>pib-monsoon-002</guid>
      <pubDate>Mon, 23 Jun 2026 11:00:00 +0530</pubDate>
      <description>IMD unveiled an upgraded monsoon prediction model for
      more accurate seasonal rainfall forecasts.</description>
    </item>
  </channel>
</rss>"""


@pytest.fixture(scope="module", autouse=True)
def _index():
    # Seeded content (from conftest) + a static source feed.
    ingest.run()
    ingest_sources.run(connectors=[StaticRssConnector("PIB", SAMPLE_RSS)])


def test_strip_html():
    assert strip_html("<p>Hello <b>world</b></p>") == "Hello world"


def test_parse_rss():
    docs = parse_rss(SAMPLE_RSS, "PIB")
    assert len(docs) == 2
    assert docs[0].external_id == "pib-quantum-001"
    assert docs[0].url == "https://pib.gov.in/news/quantum"
    assert "Quantum Mission" in docs[0].title


def test_ingest_is_idempotent():
    first = ingest_sources.run(connectors=[StaticRssConnector("PIB", SAMPLE_RSS)])
    second = ingest_sources.run(connectors=[StaticRssConnector("PIB", SAMPLE_RSS)])
    # Same two articles, no duplicates created.
    assert first["total_articles"] == 2
    assert second["total_articles"] == 2
    # Nothing changed, so nothing re-indexed on the second pass.
    assert second["indexed"] == 0


def test_articles_endpoint(client):
    res = client.get("/api/articles")
    assert res.status_code == 200
    rows = res.json()
    assert any("Quantum Mission" in r["title"] for r in rows)
    assert all(r["source"] == "PIB" for r in rows)


def test_bad_source_is_skipped():
    class Boom(StaticRssConnector):
        def fetch(self):
            raise RuntimeError("network down")

    # A failing connector must not abort the run.
    result = ingest_sources.run(connectors=[Boom("BAD", "")])
    assert "BAD" in result["errors"][0]


def test_ask_retrieves_ingested_article(client):
    body = client.post(
        "/api/ask",
        json={"question": "What is the National Quantum Mission?"},
    ).json()
    assert body["status"] == "ok"
    # The article should surface as a citation with its source URL.
    urls = [c.get("url") for c in body["citations"]]
    assert "https://pib.gov.in/news/quantum" in urls
