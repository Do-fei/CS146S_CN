from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth.deps import get_current_user
from ..db import get_db
from ..models import Annotation, Book, Job, OnePaperProject, User, utcnow
from ..schemas import SyncResponse
from .common import annotation_out, book_out, job_out, project_out

router = APIRouter(prefix="/sync", tags=["sync"])


@router.get("", response_model=SyncResponse)
def sync(
    since: datetime | None = Query(default=None, description="ISO-8601 UTC; omit for a full pull"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SyncResponse:
    """Incremental pull. Soft-deleted rows are included so every device converges."""
    server_time = utcnow()
    since_naive = since.replace(tzinfo=None) if since and since.tzinfo else since

    books_q = select(Book).where(Book.user_id == user.id)
    projects_q = select(OnePaperProject).where(OnePaperProject.user_id == user.id)
    annotations_q = select(Annotation).where(Annotation.user_id == user.id)
    jobs_q = select(Job).where(Job.user_id == user.id)
    if since_naive is not None:
        books_q = books_q.where(Book.updated_at > since_naive)
        projects_q = projects_q.where(OnePaperProject.updated_at > since_naive)
        annotations_q = annotations_q.where(Annotation.updated_at > since_naive)
        jobs_q = jobs_q.where(Job.updated_at > since_naive)
    else:
        books_q = books_q.where(Book.deleted_at.is_(None))
        annotations_q = annotations_q.where(Annotation.deleted_at.is_(None))

    return SyncResponse(
        server_time=server_time,
        books=[book_out(b) for b in db.scalars(books_q.order_by(Book.updated_at))],
        projects=[
            project_out(p) for p in db.scalars(projects_q.order_by(OnePaperProject.updated_at))
        ],
        annotations=[
            annotation_out(a) for a in db.scalars(annotations_q.order_by(Annotation.updated_at))
        ],
        jobs=[job_out(j) for j in db.scalars(jobs_q.order_by(Job.updated_at))],
    )
