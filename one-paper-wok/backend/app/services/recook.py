"""回锅加料流水线: handwriting OCR -> align to a page -> LLM refinement -> new project version."""

from difflib import SequenceMatcher
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Annotation, Book, Job, OnePaperProject, Page, ProjectVersion, utcnow
from .jobs import update_job
from .pipeline import snapshot_project
from .providers import get_llm_provider, get_ocr_provider

_MIN_ALIGN_RATIO = 0.18


def align_to_page(text: str, pages: list[Page]) -> int | None:
    """Pick the page whose OCR text is most similar to the annotation; None when nothing is close."""
    best_idx, best_ratio = None, 0.0
    probe = text[:200]
    for page in pages:
        body = page.ocr_text or ""
        if not body:
            continue
        ratio = SequenceMatcher(None, probe, body[:1200]).quick_ratio()
        if ratio > best_ratio:
            best_idx, best_ratio = page.index, ratio
    return best_idx if best_ratio >= _MIN_ALIGN_RATIO else None


def run_recook(db: Session, job_id: str) -> None:
    job = db.get(Job, job_id)
    if job is None:
        return
    book = db.get(Book, job.book_id)
    if book is None:
        raise RuntimeError("book not found")

    annotations = list(
        db.scalars(
            select(Annotation)
            .where(Annotation.book_id == book.id, Annotation.deleted_at.is_(None))
            .order_by(Annotation.created_at)
        )
    )
    if not annotations:
        raise RuntimeError("没有批注可回锅，请先扫描或输入批注")

    pages = list(book.pages)
    ocr = get_ocr_provider()
    pending = [a for a in annotations if a.status == "pending" and a.image_path]
    update_job(db, job_id, stage="ocr", progress=10, message=f"识别手写批注 0/{len(pending)}")
    for i, ann in enumerate(pending):
        try:
            ann.handwritten_text = ocr.recognize(
                Path(ann.image_path).read_bytes(), handwriting=True
            ).text
            ann.status = "recognized"
        except Exception as exc:  # noqa: BLE001
            ann.status = "failed"
            ann.refined_text = f"识别失败: {exc}"
        db.commit()
        update_job(
            db,
            job_id,
            stage="ocr",
            progress=10 + int(40 * (i + 1) / len(pending)),
            message=f"识别手写批注 {i + 1}/{len(pending)}",
        )

    update_job(db, job_id, stage="structure", progress=55, message="对齐批注与原文页")
    for ann in annotations:
        if ann.page_index is None and ann.handwritten_text:
            ann.page_index = align_to_page(ann.handwritten_text, pages)
    db.commit()

    project = book.project
    if project is None:
        project = OnePaperProject(book_id=book.id, user_id=book.user_id, version=0, summary="")
        db.add(project)
        db.commit()

    usable = [a for a in annotations if a.handwritten_text and a.status != "failed"]
    update_job(db, job_id, stage="summary", progress=70, message="AI 提炼个人洞见")
    insights = get_llm_provider().refine_annotations(
        book.title,
        project.summary,
        [{"id": a.id, "page_index": a.page_index, "text": a.handwritten_text} for a in usable],
    )
    by_id = {i.get("annotation_id"): i for i in insights}
    for ann in usable:
        hit = by_id.get(ann.id)
        if hit:
            ann.refined_text = str(hit.get("text", ""))
            ann.status = "refined"

    db.add(
        ProjectVersion(
            project_id=project.id, version=project.version, snapshot=snapshot_project(project)
        )
    )
    project.version += 1
    project.personal_insights = [
        {
            "annotation_id": i.get("annotation_id"),
            "page_index": i.get("page_index"),
            "text": i.get("text", ""),
        }
        for i in insights
    ]
    project.updated_at = utcnow()
    book.updated_at = utcnow()
    db.commit()
    update_job(
        db,
        job_id,
        stage="done",
        progress=100,
        message=f"回锅完成，一纸项目已更新到 v{project.version}",
    )
