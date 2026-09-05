from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class SendCodeRequest(BaseModel):
    email: EmailStr


class SendCodeResponse(BaseModel):
    ok: bool = True
    resend_after_seconds: int
    # Only populated by the mock email provider so local dev / tests can log in without SMTP.
    debug_code: str | None = None


class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    device_id: str = Field(min_length=1, max_length=128)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: str
    email: str
    created_at: datetime


# ---------- Books ----------
class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str | None = Field(default=None, max_length=255)
    mode: str = Field(default="full", pattern="^(full|excerpt)$")
    language: str = Field(default="zh", max_length=16)


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, max_length=255)


class PageOut(BaseModel):
    id: str
    index: int
    ocr_status: str
    has_text: bool


class EbookOut(BaseModel):
    has_pdf: bool
    has_epub: bool


class BookOut(BaseModel):
    id: str
    title: str
    author: str | None
    status: str
    mode: str
    language: str
    page_count: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    has_project: bool = False
    project_version: int | None = None
    ebook: EbookOut = EbookOut(has_pdf=False, has_epub=False)


class BookDetail(BookOut):
    pages: list[PageOut] = []


class UploadPagesResponse(BaseModel):
    book_id: str
    page_count: int
    pages: list[PageOut]


# ---------- Jobs ----------
class JobOut(BaseModel):
    id: str
    book_id: str
    kind: str
    stage: str
    progress: int
    message: str | None
    error: str | None
    created_at: datetime
    updated_at: datetime


# ---------- Project ----------
class ChapterOut(BaseModel):
    title: str
    summary: str = ""
    start_page: int | None = None


class PersonalInsightOut(BaseModel):
    annotation_id: str | None = None
    page_index: int | None = None
    text: str


class ProjectOut(BaseModel):
    id: str
    book_id: str
    version: int
    summary: str
    key_insights: list[str]
    chapter_outline: list[ChapterOut]
    personal_insights: list[PersonalInsightOut]
    updated_at: datetime


class ProjectVersionOut(BaseModel):
    version: int
    created_at: datetime
    snapshot: dict[str, Any]


# ---------- Search ----------
class SearchHit(BaseModel):
    page_index: int
    snippet: str


class SearchResponse(BaseModel):
    query: str
    hits: list[SearchHit]


# ---------- Translation ----------
class TranslateRequest(BaseModel):
    page_index: int = Field(ge=0)
    target_lang: str = Field(min_length=2, max_length=16)


class TranslatedSegment(BaseModel):
    segment_index: int
    source: str
    text: str


class TranslateResponse(BaseModel):
    page_index: int
    target_lang: str
    segments: list[TranslatedSegment]


# ---------- Annotations ----------
class AnnotationTypedCreate(BaseModel):
    text: str = Field(min_length=1)
    page_index: int | None = Field(default=None, ge=0)
    client_op_id: str | None = Field(default=None, max_length=64)


class AnnotationUpdate(BaseModel):
    handwritten_text: str | None = None
    page_index: int | None = Field(default=None, ge=0)


class AnnotationOut(BaseModel):
    id: str
    book_id: str
    page_index: int | None
    source: str
    status: str
    handwritten_text: str | None
    refined_text: str | None
    has_image: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


# ---------- Sync ----------
class SyncResponse(BaseModel):
    server_time: datetime
    books: list[BookOut]
    projects: list[ProjectOut]
    annotations: list[AnnotationOut]
    jobs: list[JobOut]
