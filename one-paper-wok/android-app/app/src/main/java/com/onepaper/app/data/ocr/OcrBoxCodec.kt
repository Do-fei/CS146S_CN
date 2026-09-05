package com.onepaper.app.data.ocr

import com.onepaper.domain.citation.NormPoint
import com.onepaper.domain.ocr.OcrBox
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

object OcrBoxCodec {
    private val json = Json { ignoreUnknownKeys = true }

    fun encode(boxes: List<OcrBox>): String = json.encodeToString(
        boxes.map { box ->
            val xs = box.points.map { it.x }
            val ys = box.points.map { it.y }
            StoredBox(
                text = box.text,
                left = xs.minOrNull() ?: 0.0,
                top = ys.minOrNull() ?: 0.0,
                right = xs.maxOrNull() ?: 1.0,
                bottom = ys.maxOrNull() ?: 1.0,
            )
        },
    )

    fun decode(raw: String?): List<OcrBox> {
        if (raw.isNullOrBlank()) return emptyList()
        return runCatching {
            json.decodeFromString<List<StoredBox>>(raw).map { stored ->
                OcrBox(
                    points = listOf(
                        NormPoint(stored.left, stored.top),
                        NormPoint(stored.right, stored.top),
                        NormPoint(stored.right, stored.bottom),
                        NormPoint(stored.left, stored.bottom),
                    ),
                    text = stored.text,
                    confidence = 0.8f,
                )
            }
        }.getOrDefault(emptyList())
    }

    @Serializable
    private data class StoredBox(
        val text: String,
        val left: Double,
        val top: Double,
        val right: Double,
        val bottom: Double,
    )
}
