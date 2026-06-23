"""Scheduled ingestion worker.

Runs in its own container. On startup it performs an initial source ingestion
(unless disabled), then schedules a recurring ingestion every
``INGEST_INTERVAL_MINUTES`` (default 6 hours). Each run fetches all configured
official feeds; individual feed failures are skipped inside
``ingest_sources.run`` so the loop keeps going.
"""

from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from app.config import settings
from app.rag import ingest_sources

log = logging.getLogger("worker")


def ingest_job() -> None:
    """One ingestion pass. Never raises — failures are logged."""
    try:
        result = ingest_sources.run()
        log.info("Source ingestion complete: %s", result)
    except Exception:  # pragma: no cover - defensive
        log.exception("Source ingestion failed; will retry on next interval")


def build_scheduler() -> BlockingScheduler:
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        ingest_job,
        trigger="interval",
        minutes=settings.ingest_interval_minutes,
        id="source_ingest",
        max_instances=1,
        coalesce=True,
    )
    return scheduler


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    if settings.ingest_on_startup:
        log.info("Running initial source ingestion on startup")
        ingest_job()

    scheduler = build_scheduler()
    log.info(
        "Scheduler started; ingesting every %s minutes from %d feed(s)",
        settings.ingest_interval_minutes,
        len(settings.source_feed_list),
    )
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):  # pragma: no cover
        log.info("Worker shutting down")


if __name__ == "__main__":
    main()
