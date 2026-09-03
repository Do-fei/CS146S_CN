from sqlalchemy.orm import Session

from ..models import Book, Ebook, Job, utcnow
from .epub_builder import build_epub
from .jobs import update_job


def run_epub(db: Session, job_id: str) -> None:
    job = db.get(Job, job_id)
    if job is None:
        return
    book = db.get(Book, job.book_id)
    if book is None:
        raise RuntimeError("book not found")
    update_job(db, job_id, stage="epub", progress=20, message="整理章节与正文")
    path = build_epub(book, list(book.pages), book.project)
    ebook = book.ebook
    if ebook is None:
        ebook = Ebook(book_id=book.id)
        db.add(ebook)
    ebook.epub_path = str(path)
    book.updated_at = utcnow()
    db.commit()
    update_job(db, job_id, stage="done", progress=100, message="EPUB 已生成")
