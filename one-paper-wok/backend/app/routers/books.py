from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth.deps import get_current_user
from ..db import get_db
from ..models import Book, Job, Page, User, utcnow
from ..schemas import (
    BookCreate,
    BookDetail,
    BookOut,
    BookUpdate,
    JobOut,
    PageOut,
    ProjectOut,
    ProjectVersionOut,
    SearchHit,
    SearchResponse,
    TranslateRequest,
    TranslateResponse,
    UploadPagesResponse,
)
from ..services.epub_job import run_epub
from ..services.jobs import run_job
from ..services.pipeline import run_cook
from ..services.storage import save_upload
from ..services.translator import translate_page
from .common import book_detail, book_out, get_owned_book, job_out, project_out

router = APIRouter(prefix="/books", tags=["books"])


def _active_job(db: Session, book_id: str) -> Job | None:
    return db.scalars(
        select(Job)
        .where(Job.book_id == book_id, Job.stage.notin_(["done", "failed"]))
        .order_by(Job.created_at.desc())
        .limit(1)
    ).first()


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(
    payload: BookCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> BookOut:
    book = Book(
        user_id=user.id,
        title=payload.title.strip(),
        author=(payload.author or "").strip() or None,
        mode=payload.mode,
        language=payload.language,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book_out(book)


@router.get("", response_model=list[BookOut])
def list_books(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[BookOut]:
    books = db.scalars(
        select(Book)
        .where(Book.user_id == user.id, Book.deleted_at.is_(None))
        .order_by(Book.updated_at.desc())
    ).all()
    return [book_out(b) for b in books]


@router.get("/{book_id}", response_model=BookDetail)
def get_book(
    book_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> BookDetail:
    return book_detail(get_owned_book(db, user, book_id))


@router.patch("/{book_id}", response_model=BookOut)
def update_book(
    book_id: str,
    payload: BookUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> BookOut:
    book = get_owned_book(db, user, book_id)
    if payload.title is not None:
        book.title = payload.title.strip()
    if payload.author is not None:
        book.author = payload.author.strip() or None
    book.updated_at = utcnow()
    db.commit()
    return book_out(book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> None:
    book = get_owned_book(db, user, book_id)
    book.deleted_at = utcnow()  # soft delete so other devices learn about it via /sync
    book.updated_at = utcnow()
    db.commit()


@router.post("/{book_id}/pages", response_model=UploadPagesResponse)
async def upload_pages(
    book_id: str,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> UploadPagesResponse:
    book = get_owned_book(db, user, book_id)
    if book.status == "cooking":
        raise HTTPException(status.HTTP_409_CONFLICT, "慢炖中，暂时不能添加页面")
    next_index = len(book.pages)
    created: list[Page] = []
    for f in files:
        raw = await f.read()
        if not raw:
            continue
        try:
            path = save_upload(book.id, "pages", raw)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, f"无法读取图片 {f.filename}: {exc}"
            ) from exc
        page = Page(book_id=book.id, index=next_index, image_path=str(path))
        next_index += 1
        db.add(page)
        created.append(page)
    book.page_count = next_index
    book.status = "preparing" if book.status != "done" else "done"
    book.updated_at = utcnow()
    db.commit()
    db.refresh(book)
    return UploadPagesResponse(
        book_id=book.id,
        page_count=book.page_count,
        pages=[
            PageOut(id=p.id, index=p.index, ocr_status=p.ocr_status, has_text=False)
            for p in created
        ],
    )


@router.post("/{book_id}/cook", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
def cook(
    book_id: str,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> JobOut:
    book = get_owned_book(db, user, book_id)
    if not book.pages:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "请先上传扫描页")
    if (existing := _active_job(db, book.id)) is not None:
        return job_out(existing)
    job = Job(
        user_id=user.id, book_id=book.id, kind="cook", stage="queued", message="已加入慢炖队列"
    )
    db.add(job)
    db.commit()
    background.add_task(run_job, job.id, run_cook)
    return job_out(job)


@router.get("/{book_id}/search", response_model=SearchResponse)
def search(
    book_id: str,
    q: str = Query(min_length=1, max_length=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SearchResponse:
    book = get_owned_book(db, user, book_id)
    needle = q.strip().lower()
    hits: list[SearchHit] = []
    for page in book.pages:
        text = page.ocr_text or ""
        pos = text.lower().find(needle)
        while pos != -1 and len(hits) < 100:
            start, end = max(0, pos - 30), min(len(text), pos + len(needle) + 30)
            hits.append(
                SearchHit(page_index=page.index, snippet=text[start:end].replace("\n", " "))
            )
            pos = text.lower().find(needle, pos + len(needle))
    return SearchResponse(query=q, hits=hits)


@router.get("/{book_id}/ebook.pdf")
def download_pdf(
    book_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> FileResponse:
    book = get_owned_book(db, user, book_id)
    if not book.ebook or not book.ebook.pdf_path:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "电子书尚未出锅")
    return FileResponse(
        book.ebook.pdf_path, media_type="application/pdf", filename=f"{book.title}.pdf"
    )


@router.post("/{book_id}/export/epub", response_model=JobOut, status_code=status.HTTP_202_ACCEPTED)
def export_epub(
    book_id: str,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> JobOut:
    book = get_owned_book(db, user, book_id)
    if book.status != "done":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "请先完成慢炖再导出 EPUB")
    if (existing := _active_job(db, book.id)) is not None:
        return job_out(existing)
    job = Job(
        user_id=user.id, book_id=book.id, kind="epub", stage="queued", message="准备生成 EPUB"
    )
    db.add(job)
    db.commit()
    background.add_task(run_job, job.id, run_epub)
    return job_out(job)


@router.get("/{book_id}/ebook.epub")
def download_epub(
    book_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> FileResponse:
    book = get_owned_book(db, user, book_id)
    if not book.ebook or not book.ebook.epub_path:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "EPUB 尚未生成，请先导出")
    return FileResponse(
        book.ebook.epub_path, media_type="application/epub+zip", filename=f"{book.title}.epub"
    )


@router.get("/{book_id}/project", response_model=ProjectOut)
def get_project(
    book_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> ProjectOut:
    book = get_owned_book(db, user, book_id)
    if book.project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "一纸项目尚未生成")
    return project_out(book.project)


@router.get("/{book_id}/project/versions", response_model=list[ProjectVersionOut])
def project_versions(
    book_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[ProjectVersionOut]:
    book = get_owned_book(db, user, book_id)
    if book.project is None:
        return []
    return [
        ProjectVersionOut(version=v.version, created_at=v.created_at, snapshot=v.snapshot)
        for v in book.project.versions
    ]


@router.post("/{book_id}/translate", response_model=TranslateResponse)
def translate(
    book_id: str,
    payload: TranslateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TranslateResponse:
    book = get_owned_book(db, user, book_id)
    page = next((p for p in book.pages if p.index == payload.page_index), None)
    if page is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "页面不存在")
    segments = translate_page(db, book, page, payload.target_lang)
    return TranslateResponse(
        page_index=page.index, target_lang=payload.target_lang, segments=segments
    )


@router.get("/{book_id}/pages/{page_index}/text")
def page_text(
    book_id: str,
    page_index: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    book = get_owned_book(db, user, book_id)
    page = next((p for p in book.pages if p.index == page_index), None)
    if page is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "页面不存在")
    return {"page_index": page.index, "ocr_status": page.ocr_status, "text": page.ocr_text or ""}


@router.get("/{book_id}/pages/{page_index}/image")
def page_image(
    book_id: str,
    page_index: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> FileResponse:
    book = get_owned_book(db, user, book_id)
    page = next((p for p in book.pages if p.index == page_index), None)
    if page is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "页面不存在")
    return FileResponse(page.image_path, media_type="image/jpeg")
