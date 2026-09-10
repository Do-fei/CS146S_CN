"""慢炖流水线: preprocess -> OCR -> chapter structure -> one-paper summary -> searchable PDF."""

from pathlib import Path

from sqlalchemy.orm import Session

from ..models import Book, Ebook, Job, OnePaperProject, Page, ProjectVersion, utcnow
from .jobs import update_job
from .pdf_builder import build_searchable_pdf
from .providers import get_llm_provider, get_ocr_provider


def snapshot_project(project: OnePaperProject) -> dict:
    return {
        "version": project.version,
        "summary": project.summary,
        "key_insights": list(project.key_insights),
        "chapter_outline": list(project.chapter_outline),
        "personal_insights": list(project.personal_insights),
    }


def ocr_pages(db: Session, job_id: str, pages: list[Page], *, start: int, end: int) -> None:
    ocr = get_ocr_provider()
    total = max(1, len(pages))
    for i, page in enumerate(pages):
        if page.ocr_status == "done" and page.ocr_text:
            continue
        try:
            raw = Path(page.image_path).read_bytes()
            result = ocr.recognize(raw, handwriting=False)
            page.ocr_text = result.text
            page.ocr_status = "done"
        except Exception as exc:  # noqa: BLE001 - one bad page must not sink the book
            page.ocr_text = page.ocr_text or ""
            page.ocr_status = "failed"
            update_job(
                db, job_id, stage="ocr", progress=start, message=f"第 {i + 1} 页识别失败: {exc}"
            )
        db.commit()
        progress = start + int((end - start) * (i + 1) / total)
        update_job(
            db, job_id, stage="ocr", progress=progress, message=f"OCR 识别中 {i + 1}/{total} 页"
        )


def run_cook(db: Session, job_id: str) -> None:
    job = db.get(Job, job_id)
    if job is None:
        return
    book = db.get(Book, job.book_id)
    if book is None:
        raise RuntimeError("book not found")

    book.status = "cooking"
    db.commit()
    update_job(db, job_id, stage="preprocess", progress=5, message="备料中：整理页面")

    pages = list(book.pages)
    if not pages:
        raise RuntimeError("没有可处理的页面，请先上传扫描页")

    ocr_pages(db, job_id, pages, start=5, end=60)

    page_texts = [p.ocr_text or "" for p in pages]
    full_text = "\n\n".join(t for t in page_texts if t)
    llm = get_llm_provider()

    update_job(db, job_id, stage="structure", progress=65, message="AI 理解章节结构")
    chapters = llm.outline_chapters(book.title, page_texts)

    update_job(db, job_id, stage="summary", progress=80, message="AI 提炼一纸精华")
    summary = llm.one_paper_summary(book.title, book.author, chapters, full_text)

    project = book.project
    if project is None:
        project = OnePaperProject(book_id=book.id, user_id=book.user_id, version=1)
        db.add(project)
    else:
        db.add(
            ProjectVersion(
                project_id=project.id, version=project.version, snapshot=snapshot_project(project)
            )
        )
        project.version += 1
    project.summary = summary.get("summary", "")
    project.key_insights = list(summary.get("key_insights", []))
    project.chapter_outline = chapters
    db.commit()

    update_job(db, job_id, stage="pdf", progress=90, message="生成可搜索电子书")
    pdf_path = build_searchable_pdf(book, pages)
    ebook = book.ebook
    if ebook is None:
        ebook = Ebook(book_id=book.id)
        db.add(ebook)
    ebook.pdf_path = str(pdf_path)
    ebook.epub_path = None  # stale after re-cook; regenerated on demand

    book.status = "done"
    book.page_count = len(pages)
    book.updated_at = utcnow()
    db.commit()
    update_job(db, job_id, stage="done", progress=100, message="出锅完成")
