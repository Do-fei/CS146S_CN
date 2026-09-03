"""Build a searchable PDF: each page is the scanned image with an invisible text layer on top."""

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas

from ..models import Book, Page
from .storage import image_size, output_path

_CJK_FONT = "STSong-Light"


def _ensure_font() -> None:
    if _CJK_FONT not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(UnicodeCIDFont(_CJK_FONT))


def build_searchable_pdf(book: Book, pages: list[Page]) -> Path:
    _ensure_font()
    out = output_path(book.id, "ebook.pdf")
    pdf = canvas.Canvas(str(out))
    pdf.setTitle(book.title)
    if book.author:
        pdf.setAuthor(book.author)

    for page in pages:
        img_path = Path(page.image_path)
        if img_path.exists():
            w, h = image_size(img_path)
        else:
            w, h = A4
        pdf.setPageSize((w, h))
        if img_path.exists():
            pdf.drawImage(str(img_path), 0, 0, width=w, height=h)

        text = (page.ocr_text or "").strip()
        if text:
            lines = text.splitlines()
            font_size = max(8, min(16, h / max(len(lines) + 2, 20)))
            t = pdf.beginText()
            t.setTextRenderMode(3)  # invisible: keeps the PDF searchable/selectable
            t.setFont(_CJK_FONT, font_size)
            t.setTextOrigin(w * 0.05, h - h * 0.05 - font_size)
            t.setLeading(font_size * 1.3)
            for line in lines:
                t.textLine(line)
            pdf.drawText(t)
        pdf.showPage()

    if not pages:
        pdf.setPageSize(A4)
        pdf.showPage()
    pdf.save()
    return out
