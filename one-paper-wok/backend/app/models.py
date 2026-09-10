import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def new_id() -> str:
    return uuid.uuid4().hex


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow, nullable=False, index=True
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)


class EmailCode(Base):
    __tablename__ = "email_codes"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    device_id: Mapped[str] = mapped_column(String(128), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)


class Book(Base, TimestampMixin):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str | None] = mapped_column(String(255))
    # preparing | cooking | done | failed
    status: Mapped[str] = mapped_column(String(16), default="preparing", nullable=False)
    # full | excerpt
    mode: Mapped[str] = mapped_column(String(16), default="full", nullable=False)
    language: Mapped[str] = mapped_column(String(16), default="zh", nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)

    pages: Mapped[list["Page"]] = relationship(
        back_populates="book", cascade="all, delete-orphan", order_by="Page.index"
    )
    project: Mapped["OnePaperProject | None"] = relationship(
        back_populates="book", uselist=False, cascade="all, delete-orphan"
    )
    ebook: Mapped["Ebook | None"] = relationship(
        back_populates="book", uselist=False, cascade="all, delete-orphan"
    )


class Page(Base):
    __tablename__ = "pages"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id"), index=True, nullable=False)
    index: Mapped[int] = mapped_column(Integer, nullable=False)
    image_path: Mapped[str] = mapped_column(String(512), nullable=False)
    ocr_text: Mapped[str | None] = mapped_column(Text)
    # pending | done | failed
    ocr_status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)

    book: Mapped[Book] = relationship(back_populates="pages")


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id"), index=True, nullable=False)
    # cook | recook | epub
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    # queued | preprocess | ocr | structure | summary | pdf | epub | done | failed
    stage: Mapped[str] = mapped_column(String(16), default="queued", nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    message: Mapped[str | None] = mapped_column(String(512))
    error: Mapped[str | None] = mapped_column(Text)


class OnePaperProject(Base, TimestampMixin):
    __tablename__ = "one_paper_projects"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id"), unique=True, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    key_insights: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    chapter_outline: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    personal_insights: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    book: Mapped[Book] = relationship(back_populates="project")
    versions: Mapped[list["ProjectVersion"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="ProjectVersion.version"
    )


class ProjectVersion(Base):
    __tablename__ = "project_versions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("one_paper_projects.id"), index=True, nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    project: Mapped[OnePaperProject] = relationship(back_populates="versions")


class Ebook(Base, TimestampMixin):
    __tablename__ = "ebooks"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id"), unique=True, nullable=False)
    pdf_path: Mapped[str | None] = mapped_column(String(512))
    epub_path: Mapped[str | None] = mapped_column(String(512))

    book: Mapped[Book] = relationship(back_populates="ebook")


class Annotation(Base, TimestampMixin):
    __tablename__ = "annotations"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    page_index: Mapped[int | None] = mapped_column(Integer)
    image_path: Mapped[str | None] = mapped_column(String(512))
    handwritten_text: Mapped[str | None] = mapped_column(Text)
    refined_text: Mapped[str | None] = mapped_column(Text)
    # scan | typed
    source: Mapped[str] = mapped_column(String(16), default="scan", nullable=False)
    # pending | recognized | refined | failed
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    client_op_id: Mapped[str | None] = mapped_column(String(64), unique=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)


class Translation(Base):
    __tablename__ = "translations"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=new_id)
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id"), index=True, nullable=False)
    page_index: Mapped[int] = mapped_column(Integer, nullable=False)
    segment_index: Mapped[int] = mapped_column(Integer, nullable=False)
    target_lang: Mapped[str] = mapped_column(String(16), nullable=False)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
