"""Job bookkeeping shared by the cook / recook / epub pipelines."""

import logging
import traceback
from collections.abc import Callable

from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import Job

logger = logging.getLogger("one_paper_wok.jobs")


def update_job(
    db: Session, job_id: str, *, stage: str, progress: int, message: str | None = None
) -> None:
    job = db.get(Job, job_id)
    if job is None:
        return
    job.stage = stage
    job.progress = max(0, min(100, progress))
    job.message = message
    db.commit()


def fail_job(db: Session, job_id: str, error: str) -> None:
    job = db.get(Job, job_id)
    if job is None:
        return
    job.stage = "failed"
    job.error = error
    db.commit()


def run_job(job_id: str, fn: Callable[[Session, str], None]) -> None:
    """Entry point for BackgroundTasks: opens its own session and turns exceptions into failed jobs."""
    db = SessionLocal()
    try:
        fn(db, job_id)
    except Exception as exc:  # noqa: BLE001 - job failures must be recorded, not raised
        logger.exception("job %s failed", job_id)
        db.rollback()
        fail_job(db, job_id, f"{exc}\n{traceback.format_exc()[-2000:]}")
    finally:
        db.close()
