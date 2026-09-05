from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth.deps import get_current_user
from ..db import get_db
from ..models import Job, User
from ..schemas import JobOut
from .common import job_out

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobOut])
def list_active_jobs(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[JobOut]:
    jobs = db.scalars(
        select(Job)
        .where(Job.user_id == user.id, Job.stage.notin_(["done", "failed"]))
        .order_by(Job.created_at.desc())
    ).all()
    return [job_out(j) for j in jobs]


@router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> JobOut:
    job = db.get(Job, job_id)
    if job is None or job.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return job_out(job)
