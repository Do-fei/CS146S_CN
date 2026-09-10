"""Per-paragraph translation with a database cache so each segment is translated once."""

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Book, Page, Translation
from .providers import get_llm_provider

_SPLIT = re.compile(r"\n\s*\n|\n")


def split_segments(text: str) -> list[str]:
    return [s.strip() for s in _SPLIT.split(text or "") if s.strip()]


def translate_page(db: Session, book: Book, page: Page, target_lang: str) -> list[dict]:
    segments = split_segments(page.ocr_text or "")
    if not segments:
        return []

    cached = {
        t.segment_index: t
        for t in db.scalars(
            select(Translation).where(
                Translation.book_id == book.id,
                Translation.page_index == page.index,
                Translation.target_lang == target_lang,
            )
        )
    }
    missing = [i for i, s in enumerate(segments) if i not in cached or cached[i].source_text != s]
    if missing:
        translated = get_llm_provider().translate(
            [segments[i] for i in missing], target_lang, book.language
        )
        for i, text in zip(missing, translated, strict=False):
            row = cached.get(i)
            if row is None:
                row = Translation(
                    book_id=book.id,
                    page_index=page.index,
                    segment_index=i,
                    target_lang=target_lang,
                    source_text=segments[i],
                    text=text,
                )
                db.add(row)
                cached[i] = row
            else:
                row.source_text = segments[i]
                row.text = text
        db.commit()

    return [
        {"segment_index": i, "source": s, "text": cached[i].text if i in cached else s}
        for i, s in enumerate(segments)
    ]
