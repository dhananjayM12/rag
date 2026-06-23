from app import worker
from app.config import settings


def test_scheduler_registers_interval_job():
    sched = worker.build_scheduler()
    jobs = sched.get_jobs()
    assert len(jobs) == 1
    job = jobs[0]
    assert job.id == "source_ingest"
    # Interval matches the configured cadence.
    assert job.trigger.interval.total_seconds() == settings.ingest_interval_minutes * 60


def test_ingest_job_swallows_errors(monkeypatch):
    def boom():
        raise RuntimeError("ingestion blew up")

    monkeypatch.setattr(worker.ingest_sources, "run", boom)
    # Must not raise — the scheduled loop has to survive failures.
    worker.ingest_job()


def test_ingest_job_runs_ingestion(monkeypatch):
    calls = {}

    def fake_run():
        calls["ran"] = True
        return {"fetched": 0, "indexed": 0}

    monkeypatch.setattr(worker.ingest_sources, "run", fake_run)
    worker.ingest_job()
    assert calls.get("ran") is True
