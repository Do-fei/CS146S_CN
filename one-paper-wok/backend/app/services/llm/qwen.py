import json
from typing import Any

from openai import OpenAI

from ...config import Settings
from .base import LlmProvider

_MAX_CHARS = 24_000


def _clip(text: str, limit: int = _MAX_CHARS) -> str:
    return text if len(text) <= limit else text[:limit] + "\n…（已截断）"


class QwenLlmProvider(LlmProvider):
    """通义千问 via DashScope's OpenAI-compatible endpoint. Also works with DeepSeek by changing base_url/model."""

    name = "qwen"

    def __init__(self, settings: Settings) -> None:
        if not settings.dashscope_api_key:
            raise ValueError("DASHSCOPE_API_KEY is required for the qwen provider")
        self._client = OpenAI(
            api_key=settings.dashscope_api_key, base_url=settings.dashscope_base_url
        )
        self._model = settings.qwen_model

    def _json(self, system: str, user: str) -> Any:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        content = resp.choices[0].message.content or "{}"
        return json.loads(content)

    def outline_chapters(self, title: str, page_texts: list[str]) -> list[dict[str, Any]]:
        numbered = "\n\n".join(f"[第{i}页]\n{t}" for i, t in enumerate(page_texts) if t)
        data = self._json(
            "你是图书结构分析助手。根据逐页 OCR 文本识别章节结构。只输出 JSON："
            '{"chapters":[{"title":"章节名","summary":"两句以内概述","start_page":起始页索引(整数)}]}。'
            "章节数量 3 到 12 个，按出现顺序排列。",
            f"书名：《{title}》\n\n{_clip(numbered)}",
        )
        chapters = data.get("chapters", []) if isinstance(data, dict) else []
        return [c for c in chapters if isinstance(c, dict) and c.get("title")]

    def one_paper_summary(
        self, title: str, author: str | None, chapters: list[dict[str, Any]], full_text: str
    ) -> dict[str, Any]:
        outline = "\n".join(f"- {c.get('title')}: {c.get('summary', '')}" for c in chapters)
        data = self._json(
            "你是「一纸读书煲」的读书助手，要把一本书炖成一页精华。只输出 JSON："
            '{"summary":"150-250字的一段话总结","key_insights":["洞见1","洞见2","洞见3"]}。'
            "洞见 3 到 5 条，每条不超过 40 字，直接、具体、可执行。",
            f"书名：《{title}》\n作者：{author or '未知'}\n\n章节大纲：\n{outline}\n\n正文（OCR）：\n{_clip(full_text)}",
        )
        return {
            "summary": str(data.get("summary", "")),
            "key_insights": [str(x) for x in data.get("key_insights", [])][:5],
        }

    def refine_annotations(
        self, title: str, summary: str, annotations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        items = "\n".join(
            f"- id={a.get('id')} page={a.get('page_index')} 原文批注：{a.get('text', '')}"
            for a in annotations
        )
        data = self._json(
            "你是读书笔记整理助手。用户在纸书上写了手写批注，OCR 结果可能有错字。"
            "请结合书的精华，把每条批注提炼成一条清晰的个人洞见（不超过 60 字），保留用户观点，不要编造。"
            '只输出 JSON：{"insights":[{"annotation_id":"...","page_index":页索引或null,"text":"..."}]}。',
            f"书名：《{title}》\n书的精华：{summary}\n\n批注：\n{items}",
        )
        insights = data.get("insights", []) if isinstance(data, dict) else []
        return [i for i in insights if isinstance(i, dict) and i.get("text")]

    def translate(
        self, segments: list[str], target_lang: str, source_lang: str | None
    ) -> list[str]:
        payload = json.dumps({"segments": segments}, ensure_ascii=False)
        data = self._json(
            f"你是专业译者。把 segments 中每一段翻译成 {target_lang}"
            + (f"（源语言 {source_lang}）" if source_lang else "")
            + '。保持段落数量和顺序不变，只输出 JSON：{"segments":["译文1","译文2",...]}。',
            payload,
        )
        out = [str(x) for x in data.get("segments", [])]
        if len(out) != len(segments):
            out = (out + segments)[: len(segments)]
        return out
