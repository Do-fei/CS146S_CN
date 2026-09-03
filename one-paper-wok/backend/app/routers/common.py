from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import Annotation, Book, Job, OnePaperProject, User
from ..schemas import AnnotationOut, BookDetail, BookOut, EbookOut, JobOut, PageOut, ProjectOut


def get_owned_book(db: Session, user: User, book_id: str, *, include_deleted: bool = False) -> Book:
    book = db.get(Book, book_id)
    if book is None or book.user_id != user.id or (book.deleted_at and not include_deleted):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")
    return book


def book_out(book: Book) -> BookOut:
    return BookOut(
        id=book.id,
        title=book.title,
        author=book.author,
        status=book.status,
        mode=book.mode,
        language=book.language,
        page_count=book.page_count,
        created_at=book.created_at,
        updated_at=book.updated_at,
        deleted_at=book.deleted_at,
        has_project=book.project is not None and book.project.version > 0,
        project_version=book.project.version if book.project else None,
        ebook=EbookOut(
            has_pdf=bool(book.ebook and book.ebook.pdf_path),
            has_epub=bool(book.ebook and book.ebook.epub_path),
        ),
    )


def book_detail(book: Book) -> BookDetail:
    base = book_out(book).model_dump()
    return BookDetail(
        **base,
        pages=[
            PageOut(id=p.id, index=p.index, ocr_status=p.ocr_status, has_text=bool(p.ocr_text))
            for p in book.pages
        ],
    )


def job_out(job: Job) -> JobOut:
    return JobOut(
        id=job.id,
        book_id=job.book_id,
        kind=job.kind,
        stage=job.stage,
        progress=job.progress,
        message=job.message,
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def project_out(project: OnePaperProject) -> ProjectOut:
    return ProjectOut(
        id=project.id,
        book_id=project.book_id,
        version=project.version,
        summary=project.summary,
        key_insights=[str(x) for x in project.key_insights],
        chapter_outline=[
            {
                "title": str(c.get("title", "")),
                "summary": str(c.get("summary", "")),
                "start_page": c.get("start_page"),
            }
            for c in project.chapter_outline
            if isinstance(c, dict)
        ],
        personal_insights=[
            {
                "annotation_id": i.get("annotation_id"),
                "page_index": i.get("page_index"),
                "text": str(i.get("text", "")),
            }
            for i in project.personal_insights
            if isinstance(i, dict)
        ],
        updated_at=project.updated_at,
    )


def annotation_out(ann: Annotation) -> AnnotationOut:
    return AnnotationOut(
        id=ann.id,
        book_id=ann.book_id,
        page_index=ann.page_index,
        source=ann.source,
        status=ann.status,
        handwritten_text=ann.handwritten_text,
        refined_text=ann.refined_text,
        has_image=bool(ann.image_path),
        created_at=ann.created_at,
        updated_at=ann.updated_at,
        deleted_at=ann.deleted_at,
    )
