package com.onepaper.domain.tts

import com.onepaper.domain.model.KnowledgeLayer

/** 听书：只读眼前这一页/这一章已有的文字。不代读全书。 */
data class TtsPassage(
    val text: String,
    val layer: KnowledgeLayer,
    val label: String,
)

object TtsPolicy {
    fun passage(
        kind: String,
        chapterText: String?,
        embeddedText: String?,
        recognitionDraft: String?,
    ): TtsPassage? {
        return when (kind) {
            "PDF" -> {
                val layer = embeddedText?.trim().orEmpty()
                if (layer.isNotBlank()) {
                    TtsPassage(layer, KnowledgeLayer.SOURCE, "本页文本层")
                } else {
                    val draft = recognitionDraft?.trim().orEmpty()
                    if (draft.isBlank()) null
                    else TtsPassage(draft, KnowledgeLayer.AI, "本页识别稿，不是原文")
                }
            }
            "IMAGES" -> {
                val draft = recognitionDraft?.trim().orEmpty()
                if (draft.isBlank()) null
                else TtsPassage(draft, KnowledgeLayer.AI, "本页识别稿，不是原文")
            }
            else -> {
                val body = chapterText?.trim().orEmpty()
                if (body.isBlank()) null
                else TtsPassage(body, KnowledgeLayer.SOURCE, "本章原文")
            }
        }
    }
}
