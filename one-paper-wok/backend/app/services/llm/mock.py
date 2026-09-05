from typing import Any

from .base import LlmProvider


class MockLlmProvider(LlmProvider):
    """Deterministic stand-in that shapes plausible output from the OCR text itself."""

    name = "mock"

    def outline_chapters(self, title: str, page_texts: list[str]) -> list[dict[str, Any]]:
        if not page_texts:
            return []
        chunk = max(1, len(page_texts) // 3)
        chapters = []
        for i, start in enumerate(range(0, len(page_texts), chunk)):
            body = " ".join(t.strip() for t in page_texts[start : start + chunk] if t)
            chapters.append(
                {
                    "title": f"第{i + 1}部分",
                    "summary": body[:80] + ("…" if len(body) > 80 else ""),
                    "start_page": start,
                }
            )
            if len(chapters) >= 3:
                break
        return chapters

    def one_paper_summary(
        self, title: str, author: str | None, chapters: list[dict[str, Any]], full_text: str
    ) -> dict[str, Any]:
        sentences = [s.strip() for s in full_text.replace("\n", "。").split("。") if s.strip()]
        uniq: list[str] = []
        for s in sentences:
            if s not in uniq:
                uniq.append(s)
        head = "。".join(uniq[:2]) + "。" if uniq else ""
        by = f"（{author}）" if author else ""
        return {
            "summary": (
                f"《{title}》{by}一纸精华：{head}" if head else f"《{title}》{by}的一纸精华。"
            ),
            "key_insights": uniq[2:5] or uniq[:3],
        }

    def refine_annotations(
        self, title: str, summary: str, annotations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        out = []
        for a in annotations:
            raw = (a.get("text") or "").strip()
            out.append(
                {
                    "annotation_id": a.get("id"),
                    "page_index": a.get("page_index"),
                    "text": f"个人洞见：{raw}" if raw else "（空批注）",
                }
            )
        return out

    def translate(
        self, segments: list[str], target_lang: str, source_lang: str | None
    ) -> list[str]:
        return [f"[{target_lang}] {s}" for s in segments]
