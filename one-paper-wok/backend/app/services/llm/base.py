from abc import ABC, abstractmethod
from typing import Any


class LlmProvider(ABC):
    """Task-oriented LLM interface shared by summarisation, annotation refinement and translation."""

    name: str = "base"

    @abstractmethod
    def outline_chapters(self, title: str, page_texts: list[str]) -> list[dict[str, Any]]:
        """Return [{"title": str, "summary": str, "start_page": int}] for the book."""

    @abstractmethod
    def one_paper_summary(
        self, title: str, author: str | None, chapters: list[dict[str, Any]], full_text: str
    ) -> dict[str, Any]:
        """Return {"summary": str, "key_insights": [str, ...]}."""

    @abstractmethod
    def refine_annotations(
        self, title: str, summary: str, annotations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Return [{"annotation_id": str, "page_index": int|None, "text": str}] personal insights."""

    @abstractmethod
    def translate(
        self, segments: list[str], target_lang: str, source_lang: str | None
    ) -> list[str]:
        """Translate each segment, preserving order and count."""
