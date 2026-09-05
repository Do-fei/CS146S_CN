#!/usr/bin/env python3
"""Generate bundled EPUB + image-only PDF samples (our own copy, safe to commit)."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1] / "app" / "src" / "main" / "assets" / "samples"
ROOT.mkdir(parents=True, exist_ok=True)
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for ch in paragraph:
            trial = current + ch
            if draw.textlength(trial, font=font) <= width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = ch
        if current:
            lines.append(current)
    return lines


def render_page(title: str, body: str, footer: str) -> Image.Image:
    img = Image.new("RGB", (1240, 1754), (250, 247, 241))
    draw = ImageDraw.Draw(img)
    title_font = ImageFont.truetype(FONT, 54)
    body_font = ImageFont.truetype(FONT, 40)
    foot_font = ImageFont.truetype(FONT, 28)
    draw.rectangle((48, 48, 1192, 1706), outline=(189, 89, 59), width=4)
    y = 90
    for line in wrap(draw, title, title_font, 1040):
        draw.text((100, y), line, font=title_font, fill=(48, 45, 41))
        y += 70
    y += 20
    for line in wrap(draw, body, body_font, 1040):
        draw.text((100, y), line, font=body_font, fill=(48, 45, 41))
        y += 56
    draw.text((100, 1620), footer, font=foot_font, fill=(91, 107, 78))
    return img


def write_pdf(pages: list[Image.Image], dest: Path) -> None:
    """Minimal image-only PDF so PdfRenderer can page through Chinese sample pages."""
    buffers = []
    for page in pages:
        buf = io.BytesIO()
        page.save(buf, format="JPEG", quality=88)
        buffers.append(buf.getvalue())

    objects: list[bytes] = [b""]  # 1-index
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{3 + i * 3} 0 R" for i in range(len(pages)))
    objects.append(f"<< /Type /Pages /Count {len(pages)} /Kids [{kids}] >>".encode())
    for i, jpeg in enumerate(buffers):
        page_obj = 3 + i * 3
        content_obj = page_obj + 1
        image_obj = page_obj + 2
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /XObject << /Im0 {image_obj} 0 R >> >> "
            f"/Contents {content_obj} 0 R >>".encode()
        )
        stream = b"q 595 0 0 842 0 0 cm /Im0 Do Q\n"
        objects.append(f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"endstream")
        objects.append(
            f"<< /Type /XObject /Subtype /Image /Width 1240 /Height 1754 "
            f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode "
            f"/Length {len(jpeg)} >>\nstream\n".encode()
            + jpeg
            + b"\nendstream"
        )

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for idx, obj in enumerate(objects[1:], start=1):
        offsets.append(len(out))
        out += f"{idx} 0 obj\n".encode()
        out += obj
        out += b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(objects)}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer << /Size {len(objects)} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    )
    dest.write_bytes(out)


def write_epub(dest: Path) -> None:
    chapters = [
        (
            "ch1.xhtml",
            "导入",
            """
            <p>打开书架右上角，加入一本 EPUB 或 PDF。也可以拍几页纸书。</p>
            <p>加密的文件加不进来。加进来的书只存在这台手机上。</p>
            """,
        ),
        (
            "ch2.xhtml",
            "阅读",
            """
            <p>长按选一段，可以记下，或拿去问。</p>
            <p>问的时候只发送你选的那几句。没有 Key 也能读和记。</p>
            """,
        ),
        (
            "ch3.xhtml",
            "一纸",
            """
            <p>每本书会有一张一纸。你改过的段落会留下来。</p>
            <p>回煲给出修改建议，一条一条看。换手机前，到「我的」里导出备份。</p>
            """,
        ),
    ]

    container = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
    manifest_items = "\n".join(
        f'    <item id="{name}" href="{name}" media-type="application/xhtml+xml"/>'
        for name, _, _ in chapters
    )
    spine = "\n".join(f'    <itemref idref="{name}"/>' for name, _, _ in chapters)
    opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>说明书</dc:title>
    <dc:creator>一纸书煲</dc:creator>
    <dc:language>zh-CN</dc:language>
    <dc:identifier id="bookid">urn:onepaper:guide:1</dc:identifier>
  </metadata>
  <manifest>
{manifest_items}
  </manifest>
  <spine>
{spine}
  </spine>
</package>
"""

    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml", container)
        zf.writestr("OEBPS/content.opf", opf)
        for name, title, body in chapters:
            zf.writestr(
                f"OEBPS/{name}",
                f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">
<head><title>{title}</title></head>
<body>
<h1>{title}</h1>
{body}
</body>
</html>
""",
            )


def main() -> None:
    write_epub(ROOT / "onepaper-guide.epub")
    pages = [
        render_page(
            "样页",
            "把这本书摊在桌上。先读完眼前这一页，再决定要不要往下翻。",
            "1 / 3",
        ),
        render_page(
            "样页",
            "划下一句自己还想回头看的话。别急着给整本书下结论。",
            "2 / 3",
        ),
        render_page(
            "样页",
            "读完之后，留下几句自己的话就够了。",
            "3 / 3",
        ),
    ]
    write_pdf(pages, ROOT / "onepaper-sample.pdf")
    pages[0].save(ROOT / "ocr-page.jpg", quality=90)
    print("wrote", ROOT / "onepaper-guide.epub", (ROOT / "onepaper-guide.epub").stat().st_size)
    print("wrote", ROOT / "onepaper-sample.pdf", (ROOT / "onepaper-sample.pdf").stat().st_size)
    print("wrote", ROOT / "ocr-page.jpg", (ROOT / "ocr-page.jpg").stat().st_size)


if __name__ == "__main__":
    main()
