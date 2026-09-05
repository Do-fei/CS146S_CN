"""Build an EPUB from OCR text, grouped by the chapter outline of the one-paper project."""

import html
from pathlib import Path

from ebooklib import epub

from ..models import Book, OnePaperProject, Page
from .storage import output_path


def _paragraphs(text: str) -> str:
    parts = [p.strip() for p in text.replace("\r", "").split("\n") if p.strip()]
    return "".join(f"<p>{html.escape(p)}</p>" for p in parts) or "<p></p>"


def _chapter_ranges(outline: list[dict], page_count: int) -> list[tuple[str, int, int]]:
    if page_count == 0:
        return []
    starts = sorted(
        {
            int(c.get("start_page") or 0)
            for c in outline
            if 0 <= int(c.get("start_page") or 0) < page_count
        }
    )
    if not outline or not starts or starts[0] != 0:
        starts = [0] + [s for s in starts if s != 0]
    titles: dict[int, str] = {}
    for c in outline:
        sp = int(c.get("start_page") or 0)
        titles.setdefault(sp, str(c.get("title") or f"第{sp + 1}页起"))
    ranges = []
    for i, sp in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else page_count
        ranges.append((titles.get(sp, f"第{i + 1}部分"), sp, end))
    return ranges


def build_epub(book: Book, pages: list[Page], project: OnePaperProject | None) -> Path:
    out = output_path(book.id, "ebook.epub")
    ebook = epub.EpubBook()
    ebook.set_identifier(f"one-paper-wok-{book.id}")
    ebook.set_title(book.title)
    ebook.set_language(book.language or "zh")
    if book.author:
        ebook.add_author(book.author)

    items: list[epub.EpubHtml] = []

    if project is not None:
        insights = "".join(f"<li>{html.escape(str(i))}</li>" for i in project.key_insights)
        personal = "".join(
            f"<li>{html.escape(str(i.get('text', '')))}</li>" for i in project.personal_insights
        )
        front = epub.EpubHtml(title="一纸精华", file_name="one_paper.xhtml", lang=book.language)
        front.content = (
            f"<h1>一纸精华</h1><p>{html.escape(project.summary)}</p>"
            f"<h2>关键洞见</h2><ul>{insights}</ul>"
            + (f"<h2>我的批注</h2><ul>{personal}</ul>" if personal else "")
        )
        ebook.add_item(front)
        items.append(front)

    outline = project.chapter_outline if project else []
    for idx, (title, start, end) in enumerate(_chapter_ranges(outline, len(pages))):
        body = "\n".join(p.ocr_text or "" for p in pages[start:end])
        chapter = epub.EpubHtml(
            title=title, file_name=f"chapter_{idx + 1}.xhtml", lang=book.language
        )
        chapter.content = f"<h1>{html.escape(title)}</h1>{_paragraphs(body)}"
        ebook.add_item(chapter)
        items.append(chapter)

    if not items:
        empty = epub.EpubHtml(title=book.title, file_name="empty.xhtml", lang=book.language)
        empty.content = f"<h1>{html.escape(book.title)}</h1><p>（暂无内容）</p>"
        ebook.add_item(empty)
        items.append(empty)

    ebook.toc = tuple(items)
    ebook.add_item(epub.EpubNcx())
    ebook.add_item(epub.EpubNav())
    ebook.spine = ["nav", *items]
    epub.write_epub(str(out), ebook)
    return out
