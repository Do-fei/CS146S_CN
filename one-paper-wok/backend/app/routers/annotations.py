from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth.deps import get_current_user
from ..db import get_db
from ..models import Annotation, Job, User, utcnow
from ..schemas import AnnotationOut, AnnotationTypedCreate, AnnotationUpdate, JobOut
from ..services.jobs import run_job
from ..services.recook import run_recook
from ..services.storage import save_upload
from .common import annotation_out, get_owned_book, job_out

router = APIRouter(prefix="/books/{book_id}", tags=["annotations"])


def _get_owned_annotation(db: Session, user: User, book_id: str, annotation_id: str) -> Annotation:
    ann = db.get(Annotation, annotation_id)
    if ann is None or ann.book_id != book_id or ann.user_id != user.id or ann.deleted_at:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Annotation not found")
    return ann


@router.get("/annotations", response_model=list[AnnotationOut])
def list_annotations(
    book_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[AnnotationOut]:
    get_owned_book(db, user, book_id)
    rows = db.scalars(
        select(Annotation)
        .where(Annotation.book_id == book_id, Annotation.deleted_at.is_(None))
        .order_by(Annotation.page_index.nulls_last(), Annotation.created_at)
    ).all()
    return [annotation_out(a) for a in rows]


@router.post(
    "/annotations", response_model=list[AnnotationOut], status_code=status.HTTP_201_CREATED
)
async def upload_annotation_scans(
    book_id: str,
    files: list[UploadFile] = File(...),
    page_index: int | None = Form(default=None),
    client_op_id: str | None = Form(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[AnnotationOut]:
    """Scan mode: one photo per annotated page. Handwriting OCR happens later in /recook."""
    book = get_owned_book(db, user, book_id)
    if client_op_id:
        existing = db.scalars(
            select(Annotation).where(Annotation.client_op_id == client_op_id)
        ).all()
        if existing:
            return [annotation_out(a) for a in existing]
    created: list[Annotation] = []
    for i, f in enumerate(files):
        raw = await f.read()
        if not raw:
            continue
        path = save_upload(book.id, "annotations", raw)
        ann = Annotation(
            book_id=book.id,
            user_id=user.id,
            page_index=page_index,
            image_path=str(path),
            source="scan",
            status="pending",
            client_op_id=f"{client_op_id}:{i}" if client_op_id and len(files) > 1 else client_op_id,
        )
        db.add(ann)
        created.append(ann)
    book.updated_at = utcnow()
    db.commit()
    return [annotation_out(a) for a in created]


@router.post(
    "/annotations/typed", response_model=AnnotationOut, status_code=status.HTTP_201_CREATED
)
def create_typed_annotation(
    book_id: str,
    payload: AnnotationTypedCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AnnotationOut:
    book = get_owned_book(db, user, book_id)
    if payload.client_op_id:
        existing = db.scalars(
            select(Annotation).where(Annotation.client_op_id == payload.client_op_id)
        ).first()
        if existing:
            return annotation_out(existing)
    ann = Annotation(
        book_id=book.id,
        user_id=user.id,
        page_index=payload.page_index,
        handwritten_text=payload.text.strip(),
        source="typed",
        status="recognized",
        client_op_id=payload.client_op_id,
    )
    db.add(ann)
    book.updated_at = utcnow()
    db.commit()
    return annotation_out(ann)


@router.patch("/annotations/{annotation_id}", response_model=AnnotationOut)
def update_annotation(
    book_id: str,
    annotation_id: str,
    payload: AnnotationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AnnotationOut:
    """Manual correction of OCR output from the notebook screen."""
    get_owned_book(db, user, book_id)
    ann = _get_owned_annotation(db, user, book_id, annotation_id)
    if payload.handwritten_text is not None:
        ann.handwritten_text = payload.handwritten_text.strip()
        ann.status = "recognized"
        ann.refined_text = None
    if payload.page_index is not None:
        ann.page_index = payload.page_index
    ann.updated_at = utcnow()
    db.commit()
    return annotation_out(ann)


@router.delete("/annotations/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_annotation(
    book_id: str,
    annotation_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    get_owned_book(db, user, book_id)
    ann = _get_owned_annotation(db, user, book_id, annotation_id)
    ann.deleted_at = utcnow()
    ann.updated_at = utcnow()
    db.commit()


@router.get("/annotations/{annotation_id}/image")
def annotation_image(
    book_id: str,
    annotation_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> FileResponse:
    get_owned_book(db, user, book_id)
    ann = _get_owned_annotation(db, user, book_id, annotation_id)
    if not ann.image_path:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "该批注没有图片")
    return FileResponse(ann.image_path, media_type="image/jpeg")


@router.post("/recook", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
def recook(
    book_id: str,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> JobOut:
    book = get_owned_book(db, user, book_id)
    if book.status != "done":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "请先完成慢炖，再回锅加料")
    has_annotations = db.scalars(
        select(Annotation)
        .where(Annotation.book_id == book.id, Annotation.deleted_at.is_(None))
        .limit(1)
    ).first()
    if has_annotations is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "还没有批注，先扫描或输入一条吧")
    active = db.scalars(
        select(Job).where(Job.book_id == book.id, Job.stage.notin_(["done", "failed"])).limit(1)
    ).first()
    if active is not None:
        return job_out(active)
    job = Job(
        user_id=user.id, book_id=book.id, kind="recook", stage="queued", message="已加入回锅队列"
    )
    db.add(job)
    db.commit()
    background.add_task(run_job, job.id, run_recook)
    return job_out(job)
